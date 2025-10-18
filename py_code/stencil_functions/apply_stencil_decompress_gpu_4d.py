import torch,struct,math
import numpy as np
from dahuffman import HuffmanCodec
from itertools import product
import zstandard as zstd
from args import args_c
from stencil_manager import stencil_manager_c
from stencil_functions.expand_data import expand_data_gpu_4d
from stencil_functions.blockify import blockify_4d
from stencil_functions.generate_cur_block_ext import generate_cur_block_ext_gpu_4d
from stencil_functions.generate_matAB import generate_matAB_gpu_4d
from read_write_dataset import read_dataset,restore_data_range

def apply_stencil_decompress_gpu_4d(args:args_c,stencil_manager:stencil_manager_c):
    ######## Zstd ########
    dctx=zstd.ZstdDecompressor()
    hf_bs=dctx.decompress(args.zstd_bs)
    ######## Data range ########
    args.data_min=struct.unpack("<f",hf_bs[:4])[0]
    hf_bs=hf_bs[4:]
    args.data_max=struct.unpack("<f",hf_bs[:4])[0]
    hf_bs=hf_bs[4:]
    ######## Huffman pivot ########
    args.pivot_num=struct.unpack("<i",hf_bs[:4])[0]
    hf_bs=hf_bs[4:]
    args.pivot=torch.tensor(struct.unpack(f"<{args.pivot_num}f",hf_bs[:4*args.pivot_num]),dtype=torch.float32)
    hf_bs=hf_bs[4*args.pivot_num:]
    ######## Huffman parameters ########
    len_param_values=struct.unpack("<i",hf_bs[:4])[0]
    hf_bs=hf_bs[4:]
    param_data_type_flag=struct.unpack("<b",hf_bs[:1])[0]
    hf_bs=hf_bs[1:]
    if param_data_type_flag==15:
        param_values=torch.tensor(struct.unpack(f"<{len_param_values}h",hf_bs[:2*len_param_values]),dtype=torch.int32)
        hf_bs=hf_bs[2*len_param_values:]
    else:
        param_values=torch.tensor(struct.unpack(f"<{len_param_values}i",hf_bs[:4*len_param_values]),dtype=torch.int32)
        hf_bs=hf_bs[4*len_param_values:]
    param_counts=torch.tensor(struct.unpack(f"<{len_param_values}i",hf_bs[:4*len_param_values]),dtype=torch.int32)
    hf_bs=hf_bs[4*len_param_values:]
    param_freqs=dict(zip(param_values.tolist(),param_counts.tolist()))
    param_codec=HuffmanCodec.from_frequencies(param_freqs)
    len_temp_bs=struct.unpack("<i",hf_bs[:4])[0]
    hf_bs=hf_bs[4:]
    temp_bs=hf_bs[:len_temp_bs]
    hf_bs=hf_bs[len_temp_bs:]
    args.parameters=torch.tensor(param_codec.decode(temp_bs),dtype=torch.int32)
    ######## Huffman qb ########
    len_qb_values=struct.unpack("<i",hf_bs[:4])[0]
    hf_bs=hf_bs[4:]
    qb_values=torch.tensor(struct.unpack(f"<{len_qb_values}h",hf_bs[:2*len_qb_values]),dtype=torch.int32)
    hf_bs=hf_bs[2*len_qb_values:]
    qb_counts=torch.tensor(struct.unpack(f"<{len_qb_values}i",hf_bs[:4*len_qb_values]),dtype=torch.int32)
    hf_bs=hf_bs[4*len_qb_values:]
    qb_freqs=dict(zip(qb_values.tolist(),qb_counts.tolist()))
    qb_codec=HuffmanCodec.from_frequencies(qb_freqs)
    len_temp_bs=struct.unpack("<i",hf_bs[:4])[0]
    hf_bs=hf_bs[4:]
    temp_bs=hf_bs[:len_temp_bs]
    hf_bs=hf_bs[len_temp_bs:]
    args.qb=torch.tensor(qb_codec.decode(temp_bs),dtype=torch.int32)

    args.pivot=args.pivot.to(args.device)
    args.parameters=args.parameters.to(args.device)
    args.qb=args.qb.to(args.device)

    args.abs_eb=2*args.rel_eb
    args.parameter_eb=args.abs_eb*args.parameter_relative_eb
    args.cur_shape_list=[]
    args.stencil_id_list=[]
    with open(args.stencil_path,"r") as f:
        for line in f:
            args.cur_shape_list.append([int(line.split()[0]),int(line.split()[1]),int(line.split()[2]),int(line.split()[3])])
            args.stencil_id_list.append(int(line.split()[4]))
    cur_data=torch.zeros([1,1,1,1,1,1],dtype=torch.float32,device=args.device)
    cur_data[0,0,0,0,0,0]=args.pivot[0]
    mask=torch.zeros([1,2,1,1,1,1],dtype=torch.bool,device=args.device)
    mask[0,0,0,0,0,0]=True
    args.qb_begin=args.qb_end=0
    pred_gap=(2**np.ceil(np.log2(args.data_shape))).astype(np.int32)
    args.pivot_num=1
    for i in range(len(args.stencil_id_list)-1,-1,-1):
        cur_shape=args.cur_shape_list[i]
        stencil_id=args.stencil_id_list[i]
        ref_pos=stencil_manager.stencil_dict[stencil_id].ref_pos.to(args.device)
        mask_core=stencil_manager.stencil_dict[stencil_id].mask_core.to(args.device)
        cur_data,_,mask,pred_gap=expand_data_gpu_4d(cur_data,None,mask,pred_gap,args,cur_shape)
        for i0,i1,i2,i3 in product(range(0,2),repeat=4):
            mask[:,1,i0::2,i1::2,i2::2,i3::2]=ref_pos[i0,i1,i2,i3]
        if mask.sum().item()<args.data_shape[0]*args.data_shape[1]*args.data_shape[2]*args.data_shape[3]/args.pivot_ratio:
            cur_data[mask[:,1:2]]=args.pivot[args.pivot_num:args.pivot_num+mask[:,1].sum().item()]
            args.pivot_num+=mask[:,1].sum().item()
            mask[:,0]+=mask[:,1]
            mask[:,1]=False
            continue
        current_eb=args.abs_eb*(args.eb_tune_ratio**i)
        padding=1 if args.interpolation_method=="linear" else 3
        for block_id,cur_block_pad,_,mask_block_pad in blockify_4d(cur_data,None,mask,args,padding=padding):
            cur_block_ext=generate_cur_block_ext_gpu_4d(cur_block_pad,padding,args)
            cur_block=cur_block_pad[:,:,padding:-padding,padding:-padding,padding:-padding,padding:-padding]
            mask_block=mask_block_pad[:,:,padding:-padding,padding:-padding,padding:-padding,padding:-padding]
            tgt_num=mask_block[:,1].sum().item()
            param_num=mask_core.sum().item()+args.pos.shape[1]
            mat_X_baseline=torch.cat([torch.ones(param_num-args.pos.shape[1],device=args.device)/(param_num-args.pos.shape[1]),
                                      torch.zeros(args.pos.shape[1],device=args.device)],dim=0)
            mat_A,_=generate_matAB_gpu_4d(cur_block_ext,None,mask_block,mask_core,tgt_num,param_num,args)
            mat_X_bin=args.parameters[:param_num]
            args.parameters=args.parameters[param_num:]
            mat_X=mat_X_baseline+args.parameter_eb*mat_X_bin*2
            mat_H=(mat_A[:-param_num]@mat_X).clamp(-1,1)
            cur_block[mask_block[:,1:2]]=mat_H
            seq=(0,1,2,3,4,5)
            if stencil_id in [8007,4077,4079,4085,4087,4093,4095,4097,2091,2093,2095,2097,2099,2101,2103,1014]:
                seq=(0,1,2,3,4,5)
            elif stencil_id in [8011,4055,4056,4059,4060,4071,4073,4075,2078,2079,2082,2083,2086,2087,2090,1013]:
                seq=(0,1,2,3,5,4)
            elif stencil_id in [8013,4026,4027,4030,4031,4034,4035,4038,2055,2056,2057,2058,2063,2064,2065,1011]:
                seq=(0,1,2,4,5,3)
            elif stencil_id in [8014,4007,4008,4009,4010,4011,4012,4013,2021,2022,2023,2024,2025,2026,2027,1007]:
                seq=(0,1,3,4,5,2)
            quantize_block=torch.zeros_like(cur_block,dtype=torch.int32)
            args.qb_begin=args.qb_end
            args.qb_end+=tgt_num
            quantize_block.permute(seq)[mask_block[:,1:2].permute(seq)]=args.qb[args.qb_begin:args.qb_end]
            cur_block=(cur_block+quantize_block*2*current_eb).clamp(-1,1)
            cur_data[:,:,block_id[0]:block_id[0]+args.model_block_step[0],
                         block_id[1]:block_id[1]+args.model_block_step[1],
                         block_id[2]:block_id[2]+args.model_block_step[2],
                         block_id[3]:block_id[3]+args.model_block_step[3]]=cur_block
        mask[:,0:1]+=mask[:,1:2]
        print(cur_data.shape)
    args.data_decompressed=cur_data[0,0]

    if args.analysis:
        read_dataset(args)
        args.data=args.data.to(args.device)
        temp_data=restore_data_range(args.data,args)
        temp_data_decompressed=restore_data_range(args.data_decompressed,args)
        print(f"max_err= {(temp_data-temp_data_decompressed).abs().max().item():.3f}")
        print(f"max_rel_err= {((temp_data-temp_data_decompressed).abs().max().item()/(args.data_max-args.data_min)):.3f}")
        mse=((temp_data-temp_data_decompressed)**2).mean().item()
        psnr=10*math.log10((args.data_max-args.data_min)**2/mse)
        print(f"\033[31mcr= {args.data_shape[0]*args.data_shape[1]*args.data_shape[2]*args.data_shape[3]*args.unit_size/len(args.zstd_bs):.3f} \033[0m")
        print(f"\033[31mpsnr= {psnr:.3f} \033[0m")
    
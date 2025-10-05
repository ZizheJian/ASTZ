import os,torch,struct,math
import numpy as np
from dahuffman import HuffmanCodec
from itertools import product
import zstandard as zstd
from args import args_c
from stencil_manager import stencil_manager_c
from stencil_functions.expand_data import expand_data_gpu_3d
from stencil_functions.blockify import blockify_3d
from stencil_functions.generate_cur_block_ext import generate_cur_block_ext_gpu_3d
from stencil_functions.generate_matAB import generate_matAB_gpu_3d
from quantize import quantize_tensor,quantize_parameter_with_baseline
from read_write_dataset import restore_data_range

def apply_stencil_compress_gpu_3d(args:args_c,stencil_manager:stencil_manager_c):
    args.cur_shape_list=[]
    args.stencil_id_list=[]
    with open(args.stencil_path,"r") as f:
        for line in f:
            args.cur_shape_list.append([int(line.split()[0]),int(line.split()[1]),int(line.split()[2])])
            args.stencil_id_list.append(int(line.split()[3]))
    cur_data=torch.zeros([1,1,1,1,1],dtype=torch.float32,device=args.device)
    tgt_data=torch.zeros([1,1,1,1,1],dtype=torch.float32,device=args.device)
    cur_data[0,0,0,0,0]=tgt_data[0,0,0,0,0]=args.data[0,0,0]
    mask=torch.zeros([1,2,1,1,1],dtype=torch.bool,device=args.device)
    mask[0,0,0,0,0]=True
    args.qb=torch.zeros(args.data_shape[0]*args.data_shape[1]*args.data_shape[2],dtype=torch.int32,device=args.device)
    args.qb_begin=args.qb_end=0
    pred_gap=(2**np.ceil(np.log2(args.data_shape))).astype(np.int32)
    args.pivot=torch.zeros(args.data_shape[0]*args.data_shape[1]*args.data_shape[2],dtype=torch.float32,device=args.device)
    args.pivot[0]=args.data[0,0,0]
    args.pivot_num=1
    for i in range(len(args.stencil_id_list)-1,-1,-1):
        cur_shape=args.cur_shape_list[i]
        stencil_id=args.stencil_id_list[i]
        ref_pos=stencil_manager.stencil_dict[stencil_id].ref_pos.to(args.device)
        mask_core=stencil_manager.stencil_dict[stencil_id].mask_core.to(args.device)
        cur_data,tgt_data,mask,pred_gap=expand_data_gpu_3d(cur_data,tgt_data,mask,pred_gap,args,cur_shape)
        for i0,i1,i2 in product(range(0,2),repeat=3):
            mask[:,1,i0::2,i1::2,i2::2]=ref_pos[i0,i1,i2]
        if mask.sum().item()<args.data_shape[0]*args.data_shape[1]*args.data_shape[2]/args.pivot_ratio:
            cur_data[mask[:,1:2]]=tgt_data[mask[:,1:2]]
            args.pivot[args.pivot_num:args.pivot_num+mask[:,1].sum().item()]=tgt_data[mask[:,1:2]]
            args.pivot_num+=mask[:,1].sum().item()
            mask[:,0]+=mask[:,1]
            mask[:,1]=False
            continue
        current_eb=args.abs_eb*(args.eb_tune_ratio**i)
        padding=1 if args.interpolation_method=="linear" else 3
        for block_id,cur_block_pad,tgt_block,mask_block_pad in blockify_3d(cur_data,tgt_data,mask,args,padding=padding):
            mask_block=mask_block_pad[:,:,padding:-padding,padding:-padding,padding:-padding]
            max_tgt_num=mask_block[:,1].sum().item()
            break
        block_num=[(cur_data.shape[2]+args.model_block_step[0]-1)//args.model_block_step[0],
                   (cur_data.shape[3]+args.model_block_step[1]-1)//args.model_block_step[1],
                   (cur_data.shape[4]+args.model_block_step[2]-1)//args.model_block_step[2]]
        param_num=mask_core.sum().item()+args.pos.shape[1]
        mat_A=torch.zeros([*block_num,max_tgt_num+param_num,param_num],dtype=torch.float32,device=args.device)
        mat_B=torch.zeros([*block_num,max_tgt_num+param_num],dtype=torch.float32,device=args.device)
        mat_A_sampled=torch.zeros([*block_num,(max_tgt_num+args.sampling_gap-1)//args.sampling_gap+param_num,param_num],dtype=torch.float32,device=args.device)
        mat_B_sampled=torch.zeros([*block_num,(max_tgt_num+args.sampling_gap-1)//args.sampling_gap+param_num],dtype=torch.float32,device=args.device)
        blockify_records=[]
        for block_pos,cur_block_pad,tgt_block,mask_block_pad in blockify_3d(cur_data,tgt_data,mask,args,padding=padding):
            block_id=tuple(block_pos[i]//args.model_block_step[i] for i in range(3))
            cur_block_ext=generate_cur_block_ext_gpu_3d(cur_block_pad,padding,args)
            cur_block=cur_block_pad[:,:,padding:-padding,padding:-padding,padding:-padding]
            mask_block=mask_block_pad[:,:,padding:-padding,padding:-padding,padding:-padding]
            blockify_records.append((block_id,block_pos,cur_block,tgt_block,mask_block))
            if mask_block[0,1].sum().item()==0:
                raise NotImplementedError("Compression for blocks with no prediction target is not implemented.")
            mat_X_baseline=torch.cat((torch.ones(param_num-args.pos.shape[1],device=args.device)/(param_num-args.pos.shape[1]),
                                      torch.zeros(args.pos.shape[1],device=args.device)),dim=0)
            mat_A[block_id],mat_B[block_id]=generate_matAB_gpu_3d(cur_block_ext,tgt_block,mask_block,mask_core,max_tgt_num,param_num,args)
            mat_A_sampled[block_id]=torch.cat((mat_A[block_id][:-param_num][::args.sampling_gap],mat_A[block_id][-param_num:]),dim=0)
            mat_B_sampled[block_id]=torch.cat((mat_B[block_id][:-param_num][::args.sampling_gap],mat_B[block_id][-param_num:]),dim=0)
        lstsq_result=torch.linalg.lstsq(mat_A_sampled,mat_B_sampled,driver="gels")
        mat_X=lstsq_result.solution
        err=torch.matmul(mat_A_sampled[:,:,:,:-param_num],mat_X.unsqueeze(-1)).squeeze(-1)-mat_B_sampled[:,:,:,:-param_num]
        valid_equations=(err.abs()<=args.abs_eb*args.FHDE_threshold)
        mat_A_sampled[:,:,:,:-param_num][~valid_equations]=0
        mat_B_sampled[:,:,:,:-param_num][~valid_equations]=0
        lstsq_result=torch.linalg.lstsq(mat_A_sampled,mat_B_sampled,driver="gels")
        mat_X=lstsq_result.solution
        mat_X_bin,mat_X=quantize_parameter_with_baseline(mat_X,mat_X_baseline.reshape(1,1,1,-1).expand_as(mat_X),args)
        args.parameters.append(mat_X_bin)
        mat_H=torch.matmul(mat_A[:,:,:,:-param_num],mat_X.unsqueeze(-1)).squeeze(-1)
        for block_id,block_pos,cur_block,tgt_block,mask_block in blockify_records:
            tgt_num=mask_block[:,1].sum().item()
            h_block=cur_block.clone()
            h_block[mask_block[:,1:2]]=mat_H[block_id][:tgt_num]
            seq=(0,1,2,3,4)
            if stencil_id in [411,211,212,251]:
                seq=(0,1,2,3,4)
            elif stencil_id in [412,213,214,252]:
                seq=(0,1,2,4,3)
            elif stencil_id in [413,215,216,253]:
                seq=(0,1,3,4,2)
            quantize_block=quantize_tensor(tgt_block-h_block,mask_block[:,1:2],current_eb)
            cur_block[mask_block[:,1:2]]=h_block[mask_block[:,1:2]]+quantize_block[mask_block[:,1:2]]*2*current_eb
            irr_mask=(quantize_block.abs()>32767)
            args.pivot[args.pivot_num:args.pivot_num+irr_mask.sum().item()]=tgt_block[irr_mask]
            args.pivot_num+=irr_mask.sum().item()
            cur_block[irr_mask]=tgt_block[irr_mask]
            quantize_block[irr_mask]=-32768
            cur_data[:,:,block_pos[0]:block_pos[0]+args.model_block_step[0],
                         block_pos[1]:block_pos[1]+args.model_block_step[1],
                         block_pos[2]:block_pos[2]+args.model_block_step[2]]=cur_block
            args.qb_begin=args.qb_end
            args.qb_end+=tgt_num
            args.qb[args.qb_begin:args.qb_end]=quantize_block.permute(seq)[mask_block[:,1:2].permute(seq)]
        mask[:,0:1]+=mask[:,1:2]
        print(tgt_data.shape)

    ######## Data range ########
    hf_bs=struct.pack("<ff",args.data_min,args.data_max)
    ######## Huffman pivot ########
    hf_bs+=struct.pack("<i",args.pivot_num)
    hf_bs+=struct.pack(f"<{args.pivot_num}f",*(args.pivot[:args.pivot_num].tolist()))
    ######## Huffman parameters ########
    args.parameters=torch.cat([t.reshape(-1) for t in args.parameters],dim=0)
    param_values,param_counts=args.parameters.unique(return_counts=True)
    param_freqs=dict(zip(param_values.tolist(),param_counts.tolist()))
    hf_bs+=struct.pack("<i",len(param_values))
    max_param=param_values.abs().max().item()
    if max_param<=2**15-1:
        hf_bs+=struct.pack("<b",15)
        hf_bs+=struct.pack(f"<{len(param_values)}h",*param_values.tolist())
    else:
        hf_bs+=struct.pack("<b",31)
        hf_bs+=struct.pack(f"<{len(param_values)}i",*param_values.tolist())
    hf_bs+=struct.pack(f"<{len(param_values)}i",*param_counts.tolist())
    param_codec=HuffmanCodec.from_frequencies(param_freqs)
    temp_bs=param_codec.encode(args.parameters.tolist())
    hf_bs+=struct.pack("<i",len(temp_bs))
    hf_bs+=temp_bs
    ######## Huffman qb ########
    qb_values,qb_counts=args.qb[:args.qb_end].unique(return_counts=True)
    qb_freqs=dict(zip(qb_values.tolist(),qb_counts.tolist()))
    hf_bs+=struct.pack("<i",len(qb_values))
    hf_bs+=struct.pack(f"<{len(qb_values)}h",*qb_values.tolist())
    hf_bs+=struct.pack(f"<{len(qb_values)}i",*qb_counts.tolist())
    qb_codec=HuffmanCodec.from_frequencies(qb_freqs)
    temp_bs=qb_codec.encode(args.qb[:args.qb_end].tolist())
    hf_bs+=struct.pack("<i",len(temp_bs))
    hf_bs+=temp_bs
    ######## Zstd ########
    cctx=zstd.ZstdCompressor()
    args.zstd_bs=cctx.compress(hf_bs)

    if args.analysis:
        print(f"Huffman CR= {args.data_shape[0]*args.data_shape[1]*args.data_shape[2]*args.unit_size/len(hf_bs):.3f}")
        print(f"Zstd CR= {len(hf_bs)/len(args.zstd_bs):.3f}")
        print(f"\033[31mTotal CR= {args.data_shape[0]*args.data_shape[1]*args.data_shape[2]*args.unit_size/len(args.zstd_bs):.3f} \033[0m")
        temp_data=restore_data_range(args.data,args)
        temp_data_decompressed=restore_data_range(cur_data[0,0],args)
        if args.data_type_str=="ui16":
            temp_data_decompressed=temp_data_decompressed.round().clamp(0,65535)
        print(f"qb_min= {args.qb[:args.qb_end].min().item()}, qb_max= {args.qb[:args.qb_end].max().item()}")
        print(f"max_err= {(temp_data-temp_data_decompressed).abs().max().item()}")
        print(f"max_rel_err= {((temp_data-temp_data_decompressed).abs().max().item()/(args.data_max-args.data_min)):.3f}")
        mse=((temp_data-temp_data_decompressed)**2).mean().item()
        psnr=10*math.log10((args.data_max-args.data_min)**2/mse)
        print(f"\033[31mpsnr= {psnr:.3f} \033[0m")
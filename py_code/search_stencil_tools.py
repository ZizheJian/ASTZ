import torch,copy,math,os,random
import numpy as np
from typing import Tuple
from itertools import product
from torch import Tensor
from torch.nn import functional as F
from args import args_c
from stencil_manager import stencil_manager_c
from blockify import blockify
from quantize import quantize,quantize_parameter_with_baseline
from shrink_data import shrink_data
from expand_data import expand_data
from temp_code.print_pca import print_pca

def any_pred_tgt_out_of_boundary_check(stencil:Tensor,tgt_data_shape:Tuple[int])->bool:
    any_pred_tgt_out_of_boundary:bool=False
    for i0,i1,i2 in product(range(0,2),repeat=3):
        if stencil[i0,i1,i2] and (i0>=tgt_data_shape[2] or i1>=tgt_data_shape[3] or i2>=tgt_data_shape[4]):
            any_pred_tgt_out_of_boundary=True
            break
    return any_pred_tgt_out_of_boundary

def any_pred_tgt_processed_check(stencil:Tensor,mask:Tensor)->bool:
    any_pred_tgt_processed:bool=False
    for i0,i1,i2 in product(range(0,2),repeat=3):
        if stencil[i0,i1,i2] and i0<mask.shape[2] and i1<mask.shape[3] and i2<mask.shape[4] and mask[0,0,i0,i1,i2]==False:
            any_pred_tgt_processed=True
            break
    return any_pred_tgt_processed

def generate_cur_block_ext(cur_block:Tensor,mask_block:Tensor,args:args_c)->Tensor:
    cur_block_ext=torch.zeros(1,1+args.pos_ch_num,cur_block.shape[2],cur_block.shape[3],cur_block.shape[4])
    cur_block_ext[:,0:1]=cur_block
    cur_block_ext[:,1:1+args.pos_ch_num]=args.padded_pos[:,:,:cur_block.shape[2],:cur_block.shape[3],:cur_block.shape[4]]*mask_block[0,2:3]
    return cur_block_ext

def generate_mask_core(mask_block_pad:Tensor,args:args_c,padding:int)->Tensor:
    mask_core=torch.zeros(1,1,3,3,3,dtype=torch.bool)
    i0_range=range(padding,min(padding+2,mask_block_pad.shape[2]-padding))
    i1_range=range(padding,min(padding+2,mask_block_pad.shape[3]-padding))
    i2_range=range(padding,min(padding+2,mask_block_pad.shape[4]-padding))
    for i0,i1,i2 in product(i0_range,i1_range,i2_range):
        if mask_block_pad[0,1,i0,i1,i2]:
            mask_core|=mask_block_pad[:,0:1,i0-1:i0+2,i1-1:i1+2,i2-1:i2+2]
    simplified_mask_core=mask_core&torch.tensor([[[[0,0,0],[0,1,0],[0,0,0]],[[0,1,0],[1,0,1],[0,1,0]],[[0,0,0],[0,1,0],[0,0,0]]]],dtype=torch.bool)
    if simplified_mask_core.sum().item()>=args.min_reference_num:
        return simplified_mask_core
    simplified_mask_core=mask_core&torch.tensor([[[[0,1,0],[1,1,1],[0,1,0]],[[1,1,1],[1,0,1],[1,1,1]],[[0,1,0],[1,1,1],[0,1,0]]]],dtype=torch.bool)
    if simplified_mask_core.sum().item()>=args.min_reference_num:
        return simplified_mask_core
    return mask_core

def generate_mat_A_B(cur_block_ext:Tensor,tgt_block_cropped:Tensor,mask_block_cropped:Tensor,mask_core:Tensor,tgt_num:int,param_num:int,args:args_c)->Tuple[Tensor,Tensor]:
    mat_A=torch.zeros(tgt_num,param_num)
    mat_B=torch.zeros(tgt_num)
    ch_id=0
    for i0,i1,i2 in product(range(0,3),repeat=3):
        if mask_core[0,0,i0,i1,i2]:
            mat_A[:,ch_id]=cur_block_ext[:,0:1,i0:cur_block_ext.shape[2]-2+i0,i1:cur_block_ext.shape[3]-2+i1,i2:cur_block_ext.shape[4]-2+i2][mask_block_cropped[:,1:2]]
            ch_id+=1
    for j in range(1,1+args.pos_ch_num):
        mat_A[:,ch_id]=cur_block_ext[:,j:1+j,1:-1,1:-1,1:-1][mask_block_cropped[:,1:2]]
        ch_id+=1
    mat_B=tgt_block_cropped[mask_block_cropped[:,1:2]]
    mat_A=torch.cat([mat_A,args.regularization_a*torch.eye(mat_A.shape[1])],dim=0)
    mat_B=torch.cat([mat_B,args.regularization_a*torch.ones(param_num-args.pos_ch_num)/(param_num-args.pos_ch_num),torch.zeros(args.pos_ch_num)],dim=0)
    return mat_A,mat_B

def search_stencil(args:args_c,stencil_manager:stencil_manager_c):
    FHDE_threshold=args.FHDE_threshold
    stencil_path=args.stencil_path
    tgt_data=copy.deepcopy(args.data).unsqueeze(0).unsqueeze(0)
    mask=torch.zeros((1,2)+args.data.shape,dtype=torch.bool)#mask[0,0]表示已压缩数据，mask[0,1]表示正在压缩的数据。mask_block[0,2]表示未出界数据
    mask[:,0]=True
    compressed_data_num=0
    with open(stencil_path,"w") as f:   pass
    for i in range((np.sum(np.ceil(np.log2(args.data_shape)))).astype(int)):
        ########generate possible_stencil_id_list########
        if mask[:,0,0:2,0:2,0:2].sum().item()==8:
            possible_stencil_id_list=[x for x in stencil_manager.stencil_dict.keys() if 410<x<440]
        elif mask[:,0,0:2,0:2,0:2].sum().item()==4:
            possible_stencil_id_list=[x for x in stencil_manager.stencil_dict.keys() if 210<x<270]
        elif mask[:,0,0:2,0:2,0:2].sum().item()==2:
            possible_stencil_id_list=[x for x in stencil_manager.stencil_dict.keys() if 110<x<140]
        else:
            raise Exception("2*2*2区域内已压缩数据量不是2的幂")
        current_eb=args.abs_eb*(args.eb_tune_ratio**i)
        ########stencil########
        best_total_loss:float=float("inf")#使用rmsqb是因为不同的step有不同的eb，所以不能直接用rmse
        best_stencil_id:int=0
        best_mask:Tensor=torch.zeros_like(mask)
        for stencil_id in possible_stencil_id_list:
            stencil=stencil_manager.stencil_dict[stencil_id]
            if any_pred_tgt_out_of_boundary_check(stencil,tgt_data.shape):
                continue
            if any_pred_tgt_processed_check(stencil,mask):
                continue
            for i0,i1,i2 in product(range(0,2),repeat=3):
                mask[0,0,i0::2,i1::2,i2::2]&=(~stencil[i0,i1,i2])
                mask[0,1,i0::2,i1::2,i2::2]=stencil[i0,i1,i2]
            cur_data=torch.zeros_like(tgt_data)
            cur_data[mask[:,0:1]]=tgt_data[mask[:,0:1]]
            total_loss=0
            total_loss_num=0
            for block_id,cur_block_pad,tgt_block,mask_block_pad in blockify(cur_data,tgt_data,mask,args,padding=1):
                cur_block_ext=generate_cur_block_ext(cur_block_pad,mask_block_pad,args)
                mask_block=mask_block_pad[:,:,1:-1,1:-1,1:-1]
                if mask_block[0,1].sum().item()==0:
                    continue
                mask_core=generate_mask_core(mask_block_pad,args,padding=1)
                tgt_num=mask_block[:,1].sum().item()
                param_num=mask_core.sum().item()+args.pos_ch_num
                mat_X_baseline=torch.cat([torch.ones(param_num-args.pos_ch_num)/(param_num-args.pos_ch_num),torch.zeros(args.pos_ch_num)],dim=0)
                if args.method=="HDE":
                    mat_A,mat_B=generate_mat_A_B(cur_block_ext,tgt_block,mask_block,mask_core,tgt_num,param_num,args)
                    lstsq_result=torch.linalg.lstsq(mat_A,mat_B,driver="gels")
                    mat_X=lstsq_result.solution
                    _,mat_X=quantize_parameter_with_baseline(mat_X,mat_X_baseline,args)
                    err=mat_A@mat_X-mat_B
                    block_loss_num=tgt_num+param_num
                    block_loss=(err**2).sum().item()
                    total_loss_num+=block_loss_num
                    total_loss+=block_loss
                if args.method=="FHDE":
                    mat_A,mat_B=generate_mat_A_B(cur_block_ext,tgt_block,mask_block,mask_core,tgt_num,param_num,args)
                    if args.fix_coefficient:
                        mat_X=mat_X_baseline.clone()
                        err=mat_A@mat_X-mat_B
                        block_loss_num=tgt_num+param_num
                        block_loss=(err**2).sum().item()
                    else:
                        # print_pca(mat_A,args.min_reference_num)
                        lstsq_result=torch.linalg.lstsq(mat_A,mat_B,driver="gels")
                        mat_X=lstsq_result.solution
                        err=mat_A[:-param_num]@mat_X-mat_B[:-param_num]
                        valid_equations=(err.abs()<=current_eb*FHDE_threshold)
                        if valid_equations.sum().item()>0:
                            mat_A_filtered=torch.cat((mat_A[:-param_num][valid_equations],mat_A[-param_num:]),dim=0)
                            mat_B_filtered=torch.cat((mat_B[:-param_num][valid_equations],mat_B[-param_num:]),dim=0)
                            lstsq_result=torch.linalg.lstsq(mat_A_filtered,mat_B_filtered,driver="gels")
                            mat_X=lstsq_result.solution
                            _,mat_X=quantize_parameter_with_baseline(mat_X,mat_X_baseline,args)
                            err=mat_A[:-param_num]@mat_X-mat_B[:-param_num]
                            block_loss_num=valid_equations.sum().item()+param_num
                            block_loss=(err[valid_equations]**2).sum().item()
                        else:
                            mat_X=mat_X_baseline.clone()
                            err=mat_A@mat_X-mat_B
                            block_loss_num=tgt_num+param_num
                            block_loss=(err**2).sum().item()
                    total_loss_num+=block_loss_num
                    total_loss+=block_loss
            total_loss=total_loss/total_loss_num
            print(f"stencil={stencil_id}, total_loss={total_loss}, total_rmsqb={(total_loss**0.5)/(2*current_eb)}",flush=True)
            if best_total_loss>total_loss:
                best_total_loss=total_loss
                best_stencil_id=stencil_id
                best_mask[:]=mask[:]
            for i0,i1,i2 in product(range(0,2),repeat=3):
                mask[0,0,i0::2,i1::2,i2::2]|=stencil[i0,i1,i2]
                mask[0,1,i0::2,i1::2,i2::2]=False
        ########保存最佳topology########
        with open(stencil_path,"a") as f:
            f.write(f"{tgt_data.shape[2]} {tgt_data.shape[3]} {tgt_data.shape[4]} {best_stencil_id}\n")
        compressed_data_num+=best_mask[:,1].sum().item()
        tgt_data[best_mask[:,1:2]]=0
        mask[0,0]=best_mask[0,0]
        mask[0,1]=False
        tgt_data,mask=shrink_data(tgt_data,mask,args)
        print(args.data_shape,flush=True)
    compressed_data_num+=1
    print(f"compressed_data_num={compressed_data_num}",flush=True)

def apply_stencil(args:args_c,stencil_manager:stencil_manager_c,part_name:str=""):
    FHDE_threshold=args.FHDE_threshold
    stencil_path=args.stencil_path
    qb_path=os.path.join(args.project_root,"qb",f"{args.data_name}.qb")
    freq_path=os.path.join(args.project_root,"freq",f"{args.data_name}.txt")
    args.cur_shape_list=[]
    args.stencil_id_list=[]
    with open(stencil_path,"r") as f:
        for line in f:
            args.cur_shape_list.append([int(line.split()[0]),int(line.split()[1]),int(line.split()[2])])
            args.stencil_id_list.append(int(line.split()[3]))
    cur_data=torch.zeros([1,1,1,1,1],dtype=torch.float32)
    tgt_data=torch.zeros([1,1,1,1,1],dtype=torch.float32)
    cur_data[0,0,0,0,0]=tgt_data[0,0,0,0,0]=args.data[0,0,0]
    mask=torch.zeros([1,2,1,1,1],dtype=torch.bool)
    mask[0,1,0,0,0]=True
    args.qb=torch.zeros(args.data_shape[0]*args.data_shape[1]*args.data_shape[2],dtype=torch.int32)
    args.qb_begin=args.qb_end=0
    pred_gap=[2**math.ceil(np.log2(args.data_shape[i])) for i in range(3)]
    args.pivot=torch.zeros(args.data_shape[0]*args.data_shape[1]*args.data_shape[2],dtype=torch.float32)
    args.pivot[0]=args.data[0,0,0]
    args.pivot_num=1
    for i in range(len(args.stencil_id_list)-1,-1,-1):
        cur_shape=args.cur_shape_list[i]
        stencil_id=args.stencil_id_list[i]
        stencil=stencil_manager.stencil_dict[stencil_id]
        cur_data,tgt_data,mask,pred_gap=expand_data(cur_data,tgt_data,mask,pred_gap,args,cur_shape,stencil)
        if mask.sum().item()<args.data_shape[0]*args.data_shape[1]*args.data_shape[2]/args.pivot_ratio:
            cur_data[mask[:,1:2]]=tgt_data[mask[:,1:2]]
            args.pivot[args.pivot_num:args.pivot_num+mask[:,1].sum().item()]=tgt_data[mask[:,1:2]]
            args.pivot_num+=mask[:,1].sum().item()
            mask[:,0]+=mask[:,1]
            mask[:,1]=False
            continue
        current_eb=args.abs_eb*(args.eb_tune_ratio**i)
        for block_id,cur_block_pad,tgt_block,mask_block_pad in blockify(cur_data,tgt_data,mask,args,padding=1):
            # print(f"block_id={block_id}",flush=True)
            cur_block_ext=generate_cur_block_ext(cur_block_pad,mask_block_pad,args)
            cur_block=cur_block_pad[:,:,1:-1,1:-1,1:-1]
            mask_block=mask_block_pad[:,:,1:-1,1:-1,1:-1]
            if mask_block[0,1].sum().item()==0:
                continue
            mask_core=generate_mask_core(mask_block_pad,args,padding=1)
            tgt_num=mask_block[:,1].sum().item()
            param_num=mask_core.sum().item()+args.pos_ch_num
            mat_X_baseline=torch.cat([torch.ones(param_num-args.pos_ch_num)/(param_num-args.pos_ch_num),torch.zeros(args.pos_ch_num)],dim=0)
            if args.method=="HDE":
                mat_A,mat_B=generate_mat_A_B(cur_block_ext,tgt_block,mask_block,mask_core,tgt_num,param_num,args)
                lstsq_result=torch.linalg.lstsq(mat_A,mat_B,driver="gels")
                mat_X=lstsq_result.solution
                mat_X_bin,mat_X=quantize_parameter_with_baseline(mat_X,mat_X_baseline,args)
                args.parameter.append(mat_X_bin)
                h=mat_A[:-param_num]@mat_X
            if args.method=="FHDE":
                mat_A,mat_B=generate_mat_A_B(cur_block_ext,tgt_block,mask_block,mask_core,tgt_num,param_num,args)
                mat_A_small=torch.cat((mat_A[:-param_num][::args.sampling_gap],mat_A[-param_num:]),dim=0)
                mat_B_small=torch.cat((mat_B[:-param_num][::args.sampling_gap],mat_B[-param_num:]),dim=0)
                if args.fix_coefficient:
                    mat_X=mat_X_baseline.clone()
                else:
                    lstsq_result=torch.linalg.lstsq(mat_A_small,mat_B_small,driver="gels")
                    mat_X=lstsq_result.solution
                    err=mat_A_small[:-param_num]@mat_X-mat_B_small[:-param_num]
                    valid_equations=(err.abs()<=args.abs_eb*FHDE_threshold)
                    if valid_equations.sum().item()>0:
                        mat_A_filtered=torch.cat((mat_A_small[:-param_num][valid_equations],mat_A_small[-param_num:]),dim=0)
                        mat_B_filtered=torch.cat((mat_B_small[:-param_num][valid_equations],mat_B_small[-param_num:]),dim=0)
                        lstsq_result=torch.linalg.lstsq(mat_A_filtered,mat_B_filtered,driver="gels")
                        mat_X=lstsq_result.solution
                    else:
                        mat_X=mat_X_baseline.clone()
                mat_X_bin,mat_X=quantize_parameter_with_baseline(mat_X,mat_X_baseline,args)
                args.parameter.append(mat_X_bin)
                h=mat_A[:-param_num]@mat_X
            h_block=cur_block.clone()
            h_block[mask_block[:,1:2]]=h
            seq=(0,1,2,3,4)
            if stencil_id in [411,211,212,251]:
                seq=(0,1,2,3,4)
            elif stencil_id in [412,213,214,252]:
                seq=(0,1,2,4,3)
            elif stencil_id in [413,215,216,253]:
                seq=(0,1,3,4,2)
            quantize((tgt_block-h_block).permute(seq),mask_block[:,1:2].permute(seq),tgt_num,args,current_eb)
            cur_block.permute(seq)[mask_block[:,1:2].permute(seq)]=(h_block.permute(seq)[mask_block[:,1:2].permute(seq)]+args.qb[args.qb_begin:args.qb_end]*2*current_eb)
            irr_mask=(args.qb[args.qb_begin:args.qb_end].abs()>32767)
            args.pivot[args.pivot_num:args.pivot_num+irr_mask.sum().item()]=tgt_block.permute(seq)[mask_block[:,1:2].permute(seq)][irr_mask]
            args.pivot_num+=irr_mask.sum().item()
            cur_block.permute(seq)[mask_block[:,1:2].permute(seq)][irr_mask]=tgt_block.permute(seq)[mask_block[:,1:2].permute(seq)][irr_mask]
            args.qb[args.qb_begin:args.qb_end][irr_mask]=-32768
            cur_data[:,:,block_id[0]:block_id[0]+args.model_block_step[0],
                        block_id[1]:block_id[1]+args.model_block_step[1],
                        block_id[2]:block_id[2]+args.model_block_step[2]]=cur_block
        mask[:,0:1]+=mask[:,1:2]
        print(tgt_data.shape,flush=True)
    print(f"qb_num={args.qb_end}",flush=True)
    print(f"qb_min={args.qb.min().item()}, qb_max={args.qb.max().item()}",flush=True)
    args.data_decompressed=cur_data[0,0]
    max_err=(tgt_data-cur_data).abs().max().item()
    print(f"max_err={max_err}",flush=True)
    with open(qb_path,"wb") as f:
        (args.qb+32768).numpy().tofile(f)
    freq=torch.bincount(args.qb+32768,minlength=65536)
    with open(freq_path,"w") as f:
        for i in range(65536):
            f.write(str(i)+" "+str(freq[i].item())+"\n")
#尝试让param_eb和当前eb成比例
#调整min_reference_num、regularization_a、parameter_relative_eb、sampling_gap
#cubic
#cuda

import copy,torch
import numpy as np
from torch import Tensor
from itertools import product
from args import args_c
from stencil_manager import stencil_manager_c
from stencil_functions.check import num_of_reference_points_mismatch_check_3d,any_pred_tgt_out_of_boundary_check_3d,any_pred_tgt_processed_check_3d
from stencil_functions.blockify import blockify_3d
from stencil_functions.generate_cur_block_ext import generate_cur_block_ext_3d
from stencil_functions.generate_matAB import generate_matAB_3d
from quantize import quantize_parameter_with_baseline
from stencil_functions.shrink_data import shrink_data_3d

def search_stencil_3d(args:args_c,stencil_manager:stencil_manager_c):
    tgt_data=copy.deepcopy(args.data).unsqueeze(0).unsqueeze(0)
    mask=torch.zeros((1,2)+args.data.shape,dtype=torch.bool)#mask[0,0]表示已压缩数据，mask[0,1]表示正在压缩的数据。mask_block[0,2]会在blockify中被添加，表示未出界数据
    mask[:,0]=True
    compressed_data_num=0
    with open(args.stencil_path,"w") as f:
        pass
    for i in range((np.sum(np.ceil(np.log2(args.data_shape)))).astype(int)):
        current_eb=args.abs_eb*(args.eb_tune_ratio**i)
        padding=1 if args.interpolation_method=="linear" else 3
        ########stencil########
        best_total_loss:float=float("inf")#使用rmsqb是因为不同的step有不同的eb，所以不能直接用rmse
        best_stencil_id:int=0
        best_mask:Tensor=torch.zeros_like(mask)
        for stencil_id,stencil in stencil_manager.stencil_dict.items():
            ref_pos=stencil.ref_pos
            mask_core=stencil.mask_core
            if num_of_reference_points_mismatch_check_3d(ref_pos,mask):
                continue
            if any_pred_tgt_out_of_boundary_check_3d(ref_pos,tgt_data.shape):
                continue
            if any_pred_tgt_processed_check_3d(ref_pos,mask):
                continue
            for i0,i1,i2 in product(range(0,2),repeat=3):
                mask[0,0,i0::2,i1::2,i2::2]&=(~ref_pos[i0,i1,i2])
                mask[0,1,i0::2,i1::2,i2::2]=ref_pos[i0,i1,i2]
            cur_data=torch.zeros_like(tgt_data)
            cur_data[mask[:,0:1]]=tgt_data[mask[:,0:1]]
            total_loss=0
            total_loss_num=0
            for block_id,cur_block_pad,tgt_block,mask_block_pad in blockify_3d(cur_data,tgt_data,mask,args,padding):
                cur_block_ext=generate_cur_block_ext_3d(cur_block_pad,padding,args)
                mask_block=mask_block_pad[:,:,padding:-padding,padding:-padding,padding:-padding]
                if mask_block[0,1].sum().item()==0:
                    continue
                tgt_num=mask_block[:,1].sum().item()
                param_num=mask_core.sum().item()+args.pos.shape[1]
                mat_X_baseline=torch.cat([torch.ones(param_num-args.pos.shape[1])/(param_num-args.pos.shape[1]),torch.zeros(args.pos.shape[1])],dim=0)
                mat_A,mat_B=generate_matAB_3d(cur_block_ext,tgt_block,mask_block,mask_core,tgt_num,param_num,args)
                if args.method=="FIX":
                    mat_X=mat_X_baseline.clone()
                    err=mat_A@mat_X-mat_B
                    block_loss_num=tgt_num+param_num
                    block_loss=(err**2).sum().item()
                elif args.method=="HDE":
                    lstsq_result=torch.linalg.lstsq(mat_A,mat_B,driver="gels")
                    mat_X=lstsq_result.solution
                    _,mat_X=quantize_parameter_with_baseline(mat_X,mat_X_baseline,args)
                    err=mat_A@mat_X-mat_B
                    block_loss_num=tgt_num+param_num
                    block_loss=(err**2).sum().item()
                elif args.method=="FHDE":
                    # print_pca(mat_A,args.min_reference_num)
                    lstsq_result=torch.linalg.lstsq(mat_A,mat_B,driver="gels")
                    mat_X=lstsq_result.solution
                    err=mat_A[:-param_num]@mat_X-mat_B[:-param_num]
                    valid_equations=(err.abs()<=current_eb*args.FHDE_threshold)
                    if valid_equations.sum().item()>0:
                        mat_A_filtered=torch.cat((mat_A[:-param_num][valid_equations],mat_A[-param_num:]),dim=0)
                        mat_B_filtered=torch.cat((mat_B[:-param_num][valid_equations],mat_B[-param_num:]),dim=0)
                        lstsq_result=torch.linalg.lstsq(mat_A_filtered,mat_B_filtered,driver="gels")
                        mat_X=lstsq_result.solution
                        _,mat_X=quantize_parameter_with_baseline(mat_X,mat_X_baseline,args)
                        ########仅计算valid_equations的误差########
                        # err=mat_A[:-param_num][valid_equations]@mat_X-mat_B[:-param_num][valid_equations]
                        # block_loss_num=valid_equations.sum().item()
                        # block_loss=(err**2).sum().item()
                        ########计算valid_equations和正则化的误差########
                        err=mat_A_filtered@mat_X-mat_B_filtered
                        block_loss_num=valid_equations.sum().item()+param_num
                        block_loss=(err**2).sum().item()
                        ########计算所有equations的误差########
                        # err=mat_A[:-param_num]@mat_X-mat_B[:-param_num]
                        # block_loss_num=tgt_num
                        # block_loss=(err**2).sum().item()
                        ########计算所有equations和正则化的误差########
                        # err=mat_A@mat_X-mat_B
                        # block_loss_num=tgt_num+param_num
                        # block_loss=(err**2).sum().item()
                    else:
                        mat_X=mat_X_baseline.clone()
                        # err=0
                        # block_loss_num=0
                        # block_loss=0
                        err=mat_A[-param_num:]@mat_X-mat_B[-param_num:]
                        block_loss_num=param_num
                        block_loss=(err**2).sum().item()
                        # err=mat_A[:-param_num]@mat_X-mat_B[:-param_num]
                        # block_loss_num=tgt_num
                        # block_loss=(err**2).sum().item()
                        # err=mat_A@mat_X-mat_B
                        # block_loss_num=tgt_num+param_num
                        # block_loss=(err**2).sum().item()
                total_loss_num+=block_loss_num
                total_loss+=block_loss
            total_loss=total_loss/total_loss_num
            print(f"stencil={stencil_id}, total_loss={total_loss}, total_rmsqb={(total_loss**0.5)/(2*current_eb)}")
            if best_total_loss>total_loss:
                best_total_loss=total_loss
                best_stencil_id=stencil_id
                best_mask[:]=mask[:]
            for i0,i1,i2 in product(range(0,2),repeat=3):
                mask[0,0,i0::2,i1::2,i2::2]|=ref_pos[i0,i1,i2]
                mask[0,1,i0::2,i1::2,i2::2]=False
        ########保存最佳topology########
        with open(args.stencil_path,"a") as f:
            f.write(f"{tgt_data.shape[2]} {tgt_data.shape[3]} {tgt_data.shape[4]} {best_stencil_id}\n")
        compressed_data_num+=best_mask[:,1].sum().item()
        tgt_data[best_mask[:,1:2]]=0
        mask[0,0]=best_mask[0,0]
        mask[0,1]=False
        tgt_data,mask=shrink_data_3d(tgt_data,mask,args)
        print(args.data_shape)
    compressed_data_num+=1
    print(f"compressed_data_num={compressed_data_num}")
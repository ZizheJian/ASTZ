import torch
from torch import Tensor
from itertools import product
from typing import Tuple
from args import args_c

def generate_matAB_3d(cur_block_ext:Tensor,tgt_block:Tensor,mask_block:Tensor,mask_core:Tensor,tgt_num:int,param_num:int,args:args_c)->Tuple[Tensor,Tensor]:
    padding=1 if args.interpolation_method=="linear" else 3
    mat_A=torch.zeros(tgt_num+param_num,param_num)
    mat_B=torch.zeros(tgt_num+param_num)
    ch_id=0
    for i0,i1,i2 in product(range(0,3),repeat=3):
        if mask_core[0,0,i0,i1,i2]:
            mat_A[:tgt_num,ch_id]=cur_block_ext[:,0:1,i0:cur_block_ext.shape[2]-2*padding+i0,i1:cur_block_ext.shape[3]-2*padding+i1,i2:cur_block_ext.shape[4]-2*padding+i2][mask_block[:,1:2]]
            ch_id+=1
    for j in range(1,1+args.pos.shape[1]):
        mat_A[:tgt_num,ch_id]=cur_block_ext[:,j:1+j,1:-1,1:-1,1:-1][mask_block[:,1:2]]
        ch_id+=1
    mat_A[-param_num:]=args.regularization_a*torch.eye(param_num)
    if tgt_block!=None:
        mat_B[:tgt_num]=tgt_block[mask_block[:,1:2]]
        mat_B[-param_num:-args.pos.shape[1]]=args.regularization_a/(param_num-args.pos.shape[1])
        return mat_A,mat_B
    else:
        return mat_A,None
    
def generate_matAB_gpu_3d(cur_block_ext:Tensor,tgt_block:Tensor,mask_block:Tensor,mask_core:Tensor,max_tgt_num:int,param_num:int,args:args_c)->Tuple[Tensor,Tensor]:
    padding=1 if args.interpolation_method=="linear" else 3
    tgt_num=mask_block[:,1].sum().item()
    mat_A=torch.zeros(max_tgt_num+param_num,param_num,device=args.device)
    mat_B=torch.zeros(max_tgt_num+param_num,device=args.device)
    ch_id=0
    for i0,i1,i2 in product(range(0,3),repeat=3):
        if mask_core[0,0,i0,i1,i2]:
            mat_A[:tgt_num,ch_id]=cur_block_ext[:,0:1,i0:cur_block_ext.shape[2]-2*padding+i0,
                                                i1:cur_block_ext.shape[3]-2*padding+i1,
                                                i2:cur_block_ext.shape[4]-2*padding+i2][mask_block[:,1:2]]
            ch_id+=1
    for j in range(1,1+args.pos.shape[1]):
        mat_A[:tgt_num,ch_id]=cur_block_ext[:,j:1+j,1:-1,1:-1,1:-1][mask_block[:,1:2]]
        ch_id+=1
    mat_A[-param_num:]=args.regularization_a*torch.eye(param_num,device=args.device)
    if tgt_block!=None:
        mat_B[:tgt_num]=tgt_block[mask_block[:,1:2]]
        mat_B[-param_num:-args.pos.shape[1]]=args.regularization_a/(param_num-args.pos.shape[1])
        return mat_A,mat_B
    else:
        return mat_A,None
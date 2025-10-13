import torch
from torch import Tensor
from typing import Tuple
from args import args_c

def quantize(delta:Tensor,mask:Tensor,tgt_num:int,args:args_c,eb:float)->None:
    mask_positive=(delta>=0) & mask
    mask_negative=(~mask_positive) & mask
    temp_qb=torch.zeros_like(delta,dtype=torch.int)
    temp_qb[mask_positive]=torch.ceil((delta[mask_positive]-eb)/(2*eb)).int()
    temp_qb[mask_negative]=torch.floor((delta[mask_negative]+eb)/(2*eb)).int()
    args.qb_begin=args.qb_end
    args.qb_end+=tgt_num
    args.qb[args.qb_begin:args.qb_end]=temp_qb[mask].int()

def quantize_tensor(delta:Tensor,mask:Tensor,eb:float)->None:
    ret=torch.zeros_like(delta,dtype=torch.int)
    mask_positive=(delta>=0) & mask
    mask_negative=(~mask_positive) & mask
    ret[mask_positive]=torch.ceil((delta[mask_positive]-eb)/(2*eb)).int()
    ret[mask_negative]=torch.floor((delta[mask_negative]+eb)/(2*eb)).int()
    return ret

# def quantize_with_pos(block_id:Tuple[int,int,int],delta:Tensor,mask:Tensor,args:args_c)->None:
#     mask_positive=(delta>=0) & mask
#     mask_negative=(~mask_positive) & mask
#     temp_qb=torch.zeros_like(delta,dtype=torch.int)
#     temp_qb[mask_positive]=torch.ceil((delta[mask_positive]-args.abs_eb)/(2*args.abs_eb)).int()
#     temp_qb[mask_negative]=torch.floor((delta[mask_negative]+args.abs_eb)/(2*args.abs_eb)).int()
#     args.qb_tensor[:,:,block_id[0]:block_id[0]+args.model_block_step[0],
#                        block_id[1]:block_id[1]+args.model_block_step[1],
#                        block_id[2]:block_id[2]+args.model_block_step[2]][mask]=temp_qb[mask]

# def quantize_parameter(parameter:Tensor,args:args_c)->Tensor:
#     mask_positive=(parameter>=0)
#     mask_negative=(~mask_positive)
#     parameter[mask_positive]=torch.ceil((parameter[mask_positive]-args.parameter_eb)/(2*args.parameter_eb))
#     parameter[mask_negative]=torch.floor((parameter[mask_negative]+args.parameter_eb)/(2*args.parameter_eb))
#     return parameter.int()

def quantize_parameter_with_baseline(parameter:Tensor,baseline:Tensor,args:args_c)->Tensor:
    delta=parameter-baseline
    mask_positive=(delta>=0)
    mask_negative=(~mask_positive)
    parameter[mask_positive]=torch.ceil((delta[mask_positive]-args.parameter_eb)/(2*args.parameter_eb))
    parameter[mask_negative]=torch.floor((delta[mask_negative]+args.parameter_eb)/(2*args.parameter_eb))
    return parameter.int(),baseline+args.parameter_eb*parameter*2
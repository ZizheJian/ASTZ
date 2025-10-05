import torch
from torch import Tensor
from args import args_c
from typing import Tuple,List

def expand_data_3d(cur_data:Tensor,tgt_data:Tensor,mask:Tensor,pred_gap:List[int],args:args_c,cur_shape:List[int])->Tuple[Tensor,Tensor,Tensor,List[int]]:
    expand_dimension=[False,False,False]
    for i in range(3):
        if cur_shape[i]>cur_data.shape[i+2]:
            expand_dimension[i]=True
    for i in range(3):
        if expand_dimension[i]==True:
            pred_gap[i]//=2
    if tgt_data!=None:
        tgt_data=args.data[0::pred_gap[0],0::pred_gap[1],0::pred_gap[2]].unsqueeze(0).unsqueeze(0)
    expand_gap=[expand_dimension[i]+1 for i in range(3)]
    new_cur_data=torch.zeros([1,1]+cur_shape,dtype=torch.float32)
    new_cur_data[:,:,0::expand_gap[0],0::expand_gap[1],0::expand_gap[2]]=cur_data
    new_mask=torch.zeros([1,2]+cur_shape,dtype=torch.bool)
    new_mask[:,0,0::expand_gap[0],0::expand_gap[1],0::expand_gap[2]]=mask[:,0]
    return new_cur_data,tgt_data,new_mask,pred_gap

def expand_data_gpu_3d(cur_data:Tensor,tgt_data:Tensor,mask:Tensor,pred_gap:List[int],args:args_c,cur_shape:List[int])->Tuple[Tensor,Tensor,Tensor,List[int]]:
    expand_dimension=[False,False,False]
    for i in range(3):
        if cur_shape[i]>cur_data.shape[i+2]:
            expand_dimension[i]=True
    for i in range(3):
        if expand_dimension[i]==True:
            pred_gap[i]//=2
    if tgt_data!=None:
        tgt_data=args.data[0::pred_gap[0],0::pred_gap[1],0::pred_gap[2]].unsqueeze(0).unsqueeze(0)
    expand_gap=[expand_dimension[i]+1 for i in range(3)]
    new_cur_data=torch.zeros([1,1]+cur_shape,dtype=torch.float32,device=args.device)
    new_cur_data[:,:,0::expand_gap[0],0::expand_gap[1],0::expand_gap[2]]=cur_data
    new_mask=torch.zeros([1,2]+cur_shape,dtype=torch.bool,device=args.device)
    new_mask[:,0,0::expand_gap[0],0::expand_gap[1],0::expand_gap[2]]=mask[:,0]
    return new_cur_data,tgt_data,new_mask,pred_gap

import torch
from torch import Tensor
from itertools import product
from args import args_c
from typing import Tuple,List

def expand_data(cur_data:Tensor,tgt_data:Tensor,mask:Tensor,pred_gap:List[int],args:args_c,cur_shape:List[int],topology:Tensor)->Tuple[Tensor,Tensor,Tensor,List[int]]:
    expand_dimension=[False,False,False]
    for i in range(3):
        if cur_shape[i]>tgt_data.shape[i+2]:
            expand_dimension[i]=True
    for i in range(3):
        if expand_dimension[i]==True:
            pred_gap[i]//=2
    tgt_data=args.data[0::pred_gap[0],0::pred_gap[1],0::pred_gap[2]].unsqueeze(0).unsqueeze(0)
    expand_gap=[expand_dimension[i]+1 for i in range(3)]
    new_cur_data=torch.zeros_like(tgt_data)
    new_cur_data[:,:,0::expand_gap[0],0::expand_gap[1],0::expand_gap[2]]=cur_data
    new_mask=torch.zeros((1,2)+tgt_data.shape[2:5],dtype=torch.bool)
    new_mask[:,0,0::expand_gap[0],0::expand_gap[1],0::expand_gap[2]]=mask[:,0]
    for i0,i1,i2 in product(range(0,2),repeat=3):
        new_mask[:,1,i0::2,i1::2,i2::2]=topology[i0,i1,i2]
    return new_cur_data,tgt_data,new_mask,pred_gap
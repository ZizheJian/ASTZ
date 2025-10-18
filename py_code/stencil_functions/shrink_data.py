from torch import Tensor
from args import args_c
from typing import Tuple

def shrink_data_4d(tgt_data:Tensor,mask:Tensor,args:args_c)->Tuple[Tensor,Tensor]:
    if mask[0,0,1::2].sum()==0:
        tgt_data=tgt_data[:,:,0::2]
        mask=mask[:,:,0::2]
        args.data_shape[0]=(args.data_shape[0]+1)//2
    if mask[0,0,:,1::2].sum()==0:
        tgt_data=tgt_data[:,:,:,0::2]
        mask=mask[:,:,:,0::2]
        args.data_shape[1]=(args.data_shape[1]+1)//2
    if mask[0,0,:,:,1::2].sum()==0:
        tgt_data=tgt_data[:,:,:,:,0::2]
        mask=mask[:,:,:,:,0::2]
        args.data_shape[2]=(args.data_shape[2]+1)//2
    if mask[0,0,:,:,:,1::2].sum()==0:
        tgt_data=tgt_data[:,:,:,:,:,0::2]
        mask=mask[:,:,:,:,:,0::2]
        args.data_shape[3]=(args.data_shape[3]+1)//2
    return tgt_data,mask

def shrink_data_3d(tgt_data:Tensor,mask:Tensor,args:args_c)->Tuple[Tensor,Tensor]:
    if mask[0,0,1::2].sum()==0:
        tgt_data=tgt_data[:,:,0::2]
        mask=mask[:,:,0::2]
        args.data_shape[0]=(args.data_shape[0]+1)//2
    if mask[0,0,:,1::2].sum()==0:
        tgt_data=tgt_data[:,:,:,0::2]
        mask=mask[:,:,:,0::2]
        args.data_shape[1]=(args.data_shape[1]+1)//2
    if mask[0,0,:,:,1::2].sum()==0:
        tgt_data=tgt_data[:,:,:,:,0::2]
        mask=mask[:,:,:,:,0::2]
        args.data_shape[2]=(args.data_shape[2]+1)//2
    return tgt_data,mask

def shrink_data_2d(tgt_data:Tensor,mask:Tensor,args:args_c)->Tuple[Tensor,Tensor]:
    if mask[0,0,1::2].sum()==0:
        tgt_data=tgt_data[:,:,0::2]
        mask=mask[:,:,0::2]
        args.data_shape[0]=(args.data_shape[0]+1)//2
    if mask[0,0,:,1::2].sum()==0:
        tgt_data=tgt_data[:,:,:,0::2]
        mask=mask[:,:,:,0::2]
        args.data_shape[1]=(args.data_shape[1]+1)//2
    return tgt_data,mask

def shrink_data_1d(tgt_data:Tensor,mask:Tensor,args:args_c)->Tuple[Tensor,Tensor]:
    if mask[0,0,1::2].sum()==0:
        tgt_data=tgt_data[:,:,0::2]
        mask=mask[:,:,0::2]
        args.data_shape[0]=(args.data_shape[0]+1)//2
    return tgt_data,mask
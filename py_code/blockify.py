import torch
from torch import Tensor
from typing import Generator,Tuple,List
from torch.nn import functional as F
from args import args_c

def blockify(cur_data:Tensor,tgt_data:Tensor,mask:Tensor,args:args_c,padding:int=0)->Generator[Tuple[Tuple[int],Tensor,Tensor,Tensor],None,None]:
    temp_cur_data=F.pad(cur_data,(padding,)*6)
    temp_tgt_data=F.pad(tgt_data,(padding,)*6)
    temp_mask=F.pad(mask,(padding,)*6)
    temp_mask=torch.cat([temp_mask,torch.ones((1,1)+temp_mask.shape[2:],dtype=torch.bool)],dim=1)
    temp_mask[:,2,0,:,:]=False
    temp_mask[:,2,-1,:,:]=False
    temp_mask[:,2,:,0,:]=False
    temp_mask[:,2,:,-1,:]=False
    temp_mask[:,2,:,:,0]=False
    temp_mask[:,2,:,:,-1]=False
    for i0 in range(0,tgt_data.shape[2],args.model_block_step[0]):
        for i1 in range(0,tgt_data.shape[3],args.model_block_step[1]):
            for i2 in range(0,tgt_data.shape[4],args.model_block_step[2]):
                cur_block=temp_cur_data[:,:,i0:i0+args.model_block_step[0]+2*padding,i1:i1+args.model_block_step[1]+2*padding,i2:i2+args.model_block_step[2]+2*padding]
                tgt_block=temp_tgt_data[:,:,i0:i0+args.model_block_step[0]+2*padding,i1:i1+args.model_block_step[1]+2*padding,i2:i2+args.model_block_step[2]+2*padding]
                mask_block=temp_mask[:,:,i0:i0+args.model_block_step[0]+2*padding,i1:i1+args.model_block_step[1]+2*padding,i2:i2+args.model_block_step[2]+2*padding]
                yield (i0,i1,i2),cur_block,tgt_block,mask_block
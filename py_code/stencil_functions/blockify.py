import torch
from torch import Tensor
from torch.nn import functional as F
from typing import Generator,Tuple
from args import args_c

def my_pad_4d(input:Tensor,padding:Tuple[int])->Tensor:
    ret=torch.zeros((input.shape[0],input.shape[1],input.shape[2]+2*padding,input.shape[3]+2*padding,input.shape[4]+2*padding,input.shape[5]+2*padding),dtype=input.dtype,device=input.device)
    ret[0,0,padding:-padding,padding:-padding]=F.pad(input[0,0],(padding,)*4,mode="replicate")
    ret=ret.permute(0,1,4,5,2,3)
    ret[0,0]=F.pad(ret[0,0,:,:,padding:-padding,padding:-padding],(padding,)*4,mode="replicate")
    ret=ret.permute(0,1,4,5,2,3)
    return ret

def blockify_4d(cur_data:Tensor,tgt_data:Tensor,mask:Tensor,args:args_c,padding:int=0)->Generator[Tuple[Tuple[int],Tensor,Tensor,Tensor],None,None]:
    temp_cur_data=my_pad_4d(cur_data,padding)
    temp_mask=F.pad(F.pad(mask,(0,)*8+(0,1),value=True),(padding,)*8,value=False)
    for i0 in range(0,cur_data.shape[2],args.model_block_step[0]):
        for i1 in range(0,cur_data.shape[3],args.model_block_step[1]):
            for i2 in range(0,cur_data.shape[4],args.model_block_step[2]):
                for i3 in range(0,cur_data.shape[5],args.model_block_step[3]):
                    cur_block=temp_cur_data[:,:,i0:i0+args.model_block_step[0]+2*padding,i1:i1+args.model_block_step[1]+2*padding,i2:i2+args.model_block_step[2]+2*padding,i3:i3+args.model_block_step[3]+2*padding]
                    if tgt_data is not None:
                        tgt_block=tgt_data[:,:,i0:i0+args.model_block_step[0],i1:i1+args.model_block_step[1],i2:i2+args.model_block_step[2],i3:i3+args.model_block_step[3]]
                    else:
                        tgt_block=None
                    mask_block=temp_mask[:,:,i0:i0+args.model_block_step[0]+2*padding,i1:i1+args.model_block_step[1]+2*padding,i2:i2+args.model_block_step[2]+2*padding,i3:i3+args.model_block_step[3]+2*padding]
                    yield (i0,i1,i2,i3),cur_block,tgt_block,mask_block

def blockify_3d(cur_data:Tensor,tgt_data:Tensor,mask:Tensor,args:args_c,padding:int=0)->Generator[Tuple[Tuple[int],Tensor,Tensor,Tensor],None,None]:
    temp_cur_data=F.pad(cur_data,(padding,)*6,mode="replicate")
    temp_mask=F.pad(F.pad(mask,(0,)*6+(0,1),value=True),(padding,)*6,value=False)
    for i0 in range(0,cur_data.shape[2],args.model_block_step[0]):
        for i1 in range(0,cur_data.shape[3],args.model_block_step[1]):
            for i2 in range(0,cur_data.shape[4],args.model_block_step[2]):
                cur_block=temp_cur_data[:,:,i0:i0+args.model_block_step[0]+2*padding,i1:i1+args.model_block_step[1]+2*padding,i2:i2+args.model_block_step[2]+2*padding]
                if tgt_data is not None:
                    tgt_block=tgt_data[:,:,i0:i0+args.model_block_step[0],i1:i1+args.model_block_step[1],i2:i2+args.model_block_step[2]]
                else:
                    tgt_block=None
                mask_block=temp_mask[:,:,i0:i0+args.model_block_step[0]+2*padding,i1:i1+args.model_block_step[1]+2*padding,i2:i2+args.model_block_step[2]+2*padding]
                yield (i0,i1,i2),cur_block,tgt_block,mask_block

def blockify_2d(cur_data:Tensor,tgt_data:Tensor,mask:Tensor,args:args_c,padding:int=0)->Generator[Tuple[Tuple[int],Tensor,Tensor,Tensor],None,None]:
    temp_cur_data=F.pad(cur_data,(padding,)*4,mode="replicate")
    temp_mask=F.pad(F.pad(mask,(0,)*4+(0,1),value=True),(padding,)*4,value=False)
    for i0 in range(0,cur_data.shape[2],args.model_block_step[0]):
        for i1 in range(0,cur_data.shape[3],args.model_block_step[1]):
            cur_block=temp_cur_data[:,:,i0:i0+args.model_block_step[0]+2*padding,i1:i1+args.model_block_step[1]+2*padding]
            if tgt_data is not None:
                tgt_block=tgt_data[:,:,i0:i0+args.model_block_step[0],i1:i1+args.model_block_step[1]]
            else:
                tgt_block=None
            mask_block=temp_mask[:,:,i0:i0+args.model_block_step[0]+2*padding,i1:i1+args.model_block_step[1]+2*padding]
            yield (i0,i1),cur_block,tgt_block,mask_block

def blockify_1d(cur_data:Tensor,tgt_data:Tensor,mask:Tensor,args:args_c,padding:int=0)->Generator[Tuple[Tuple[int],Tensor,Tensor,Tensor],None,None]:
    temp_cur_data=F.pad(cur_data,(padding,)*2,mode="replicate")
    temp_mask=F.pad(F.pad(mask,(0,)*2+(0,1),value=True),(padding,)*2,value=False)
    for i0 in range(0,cur_data.shape[2],args.model_block_step[0]):
        cur_block=temp_cur_data[:,:,i0:i0+args.model_block_step[0]+2*padding]
        if tgt_data is not None:
            tgt_block=tgt_data[:,:,i0:i0+args.model_block_step[0]]
        else:
            tgt_block=None
        mask_block=temp_mask[:,:,i0:i0+args.model_block_step[0]+2*padding]
        yield (i0,),cur_block,tgt_block,mask_block
import torch
from torch import Tensor
from args import args_c

def generate_cur_block_ext_4d(cur_block_pad:Tensor,padding:int,args:args_c)->Tensor:
    cur_block_ext=torch.zeros(1,1+5,cur_block_pad.shape[2],cur_block_pad.shape[3],cur_block_pad.shape[4],cur_block_pad.shape[5])
    cur_block_ext[:,0:1]=cur_block_pad
    cur_block_ext[:,1:1+5,padding:-padding,padding:-padding,padding:-padding,padding:-padding]=args.pos[:,:,:cur_block_pad.shape[2]-2*padding,:cur_block_pad.shape[3]-2*padding,:cur_block_pad.shape[4]-2*padding,:cur_block_pad.shape[5]-2*padding]
    return cur_block_ext

def generate_cur_block_ext_3d(cur_block_pad:Tensor,padding:int,args:args_c)->Tensor:
    cur_block_ext=torch.zeros(1,1+4,cur_block_pad.shape[2],cur_block_pad.shape[3],cur_block_pad.shape[4])
    cur_block_ext[:,0:1]=cur_block_pad
    cur_block_ext[:,1:1+4,padding:-padding,padding:-padding,padding:-padding]=args.pos[:,:,:cur_block_pad.shape[2]-2*padding,:cur_block_pad.shape[3]-2*padding,:cur_block_pad.shape[4]-2*padding]
    return cur_block_ext

def generate_cur_block_ext_2d(cur_block_pad:Tensor,padding:int,args:args_c)->Tensor:
    cur_block_ext=torch.zeros(1,1+3,cur_block_pad.shape[2],cur_block_pad.shape[3])
    cur_block_ext[:,0:1]=cur_block_pad
    cur_block_ext[:,1:1+3,padding:-padding,padding:-padding]=args.pos[:,:,:cur_block_pad.shape[2]-2*padding,:cur_block_pad.shape[3]-2*padding]
    return cur_block_ext

def generate_cur_block_ext_1d(cur_block_pad:Tensor,padding:int,args:args_c)->Tensor:
    cur_block_ext=torch.zeros(1,1+2,cur_block_pad.shape[2])
    cur_block_ext[:,0:1]=cur_block_pad
    cur_block_ext[:,1:1+2,padding:-padding]=args.pos[:,:,:cur_block_pad.shape[2]-2*padding]
    return cur_block_ext

def generate_cur_block_ext_gpu_4d(cur_block_pad:Tensor,padding:int,args:args_c)->Tensor:
    cur_block_ext=torch.zeros(1,1+5,cur_block_pad.shape[2],cur_block_pad.shape[3],cur_block_pad.shape[4],cur_block_pad.shape[5],dtype=torch.float32,device=args.device)
    cur_block_ext[:,0:1]=cur_block_pad
    cur_block_ext[:,1:1+5,padding:-padding,padding:-padding,padding:-padding,padding:-padding]=args.pos[:,:,:cur_block_pad.shape[2]-2*padding,:cur_block_pad.shape[3]-2*padding,:cur_block_pad.shape[4]-2*padding,:cur_block_pad.shape[5]-2*padding]
    return cur_block_ext

def generate_cur_block_ext_gpu_3d(cur_block_pad:Tensor,padding:int,args:args_c)->Tensor:
    cur_block_ext=torch.zeros(1,1+4,cur_block_pad.shape[2],cur_block_pad.shape[3],cur_block_pad.shape[4],dtype=torch.float32,device=args.device)
    cur_block_ext[:,0:1]=cur_block_pad
    cur_block_ext[:,1:1+4,padding:-padding,padding:-padding,padding:-padding]=args.pos[:,:,:cur_block_pad.shape[2]-2*padding,:cur_block_pad.shape[3]-2*padding,:cur_block_pad.shape[4]-2*padding]
    return cur_block_ext

def generate_cur_block_ext_gpu_2d(cur_block_pad:Tensor,padding:int,args:args_c)->Tensor:
    cur_block_ext=torch.zeros(1,1+3,cur_block_pad.shape[2],cur_block_pad.shape[3],dtype=torch.float32,device=args.device)
    cur_block_ext[:,0:1]=cur_block_pad
    cur_block_ext[:,1:1+3,padding:-padding,padding:-padding]=args.pos[:,:,:cur_block_pad.shape[2]-2*padding,:cur_block_pad.shape[3]-2*padding]
    return cur_block_ext

def generate_cur_block_ext_gpu_1d(cur_block_pad:Tensor,padding:int,args:args_c)->Tensor:
    cur_block_ext=torch.zeros(1,1+2,cur_block_pad.shape[2],dtype=torch.float32,device=args.device)
    cur_block_ext[:,0:1]=cur_block_pad
    cur_block_ext[:,1:1+2,padding:-padding]=args.pos[:,:,:cur_block_pad.shape[2]-2*padding]
    return cur_block_ext
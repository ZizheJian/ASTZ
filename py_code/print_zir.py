import torch
from model import model_c
from torch import Tensor
from torch.nn import functional as F

def print_zir(model:model_c,baseline_core:Tensor,step_id:int)->float:
    layer=model.layer
    shape=tuple(2*(layer+baseline_core.shape[i+2]//2)+1 for i in range(3))
    center_pos=tuple(layer+baseline_core.shape[i+2]//2 for i in range(3))
    cur_data=torch.zeros((1,1)+shape)
    zir=torch.zeros((1,1)+shape)
    mask=torch.zeros((1,1)+shape,dtype=torch.bool)
    if step_id==0:
        if layer%2==0:
            mask[:,:,:,:,1::2]=True
        else:
            mask[:,:,:,:,0::2]=True
    else:
        raise NotImplementedError
    delta=1e-3
    for i0 in range(shape[0]):
        for i1 in range(shape[1]):
            for i2 in range(shape[2]):
                if mask[0,0,i0,i1,i2]:
                    zir[0,0,i0,i1,i2]=0
                    continue
                cur_data[0,0,i0,i1,i2]=delta
                interp_data=F.conv3d(cur_data,baseline_core,padding=tuple([i//2 for i in baseline_core.shape[2:]]))
                interp_data[~mask]=cur_data[~mask]
                h1=model(interp_data)[(0,0)+center_pos]
                cur_data[0,0,i0,i1,i2]=-delta
                interp_data=F.conv3d(cur_data,baseline_core,padding=tuple([i//2 for i in baseline_core.shape[2:]]))
                interp_data[~mask]=cur_data[~mask]
                h2=model(interp_data)[(0,0)+center_pos]
                zir[0,0,i0,i1,i2]=(h1-h2)/(2*delta)
                cur_data[0,0,i0,i1,i2]=0
    print("zir=",zir,sep="\n")
    print("zir_sum=",zir.sum())
    return zir.sum()

def print_zir_fast(model:model_c,baseline_core:Tensor,step_id:int)->float:
    layer=model.layer
    shape=tuple(2*(layer+baseline_core.shape[i+2]//2)+1 for i in range(3))
    center_pos=tuple(layer+baseline_core.shape[i+2]//2 for i in range(3))
    cur_data=torch.zeros((1,1)+shape)
    mask=torch.zeros((1,1)+shape,dtype=torch.bool)
    if step_id==0:
        if layer%2==0:
            mask[:,:,:,:,1::2]=True
        else:
            mask[:,:,:,:,0::2]=True
    else:
        raise NotImplementedError
    delta=1e-3
    cur_data[~mask]=delta
    interp_data=F.conv3d(cur_data,baseline_core,padding=tuple([i//2 for i in baseline_core.shape[2:]]))
    interp_data[~mask]=cur_data[~mask]
    h1=model(interp_data)[(0,0)+center_pos]
    cur_data[~mask]=-delta
    interp_data=F.conv3d(cur_data,baseline_core,padding=tuple([i//2 for i in baseline_core.shape[2:]]))
    interp_data[~mask]=cur_data[~mask]
    h2=model(interp_data)[(0,0)+center_pos]
    zir=(h1-h2)/(2*delta)
    print("zir_sum=",zir)
    return zir
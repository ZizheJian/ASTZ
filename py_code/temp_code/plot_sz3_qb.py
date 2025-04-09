import os,torch
import numpy as np
from torch import Tensor
import matplotlib.pyplot as plt

project_root=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("project_root=",project_root)
qb=torch.from_file("/home/x-zjian1/SZ3/quant_inds_tensor.bin",dtype=torch.int32,size=100*500*500)-32768
qb=qb.view(100,500,500)

def plot_qb(qb:Tensor,name:str)->None:
    qb_np=qb.numpy()
    rgb=np.zeros((qb_np.shape[0],qb_np.shape[1],3),dtype=np.float32)
    for i in range(qb_np.shape[0]):
        for j in range(qb_np.shape[1]):
            if qb_np[i,j]>=0:
                rgb[i,j,0]=1
                rgb[i,j,1]=1-np.log2(qb_np[i,j]+1)/np.log2(32768)
                rgb[i,j,2]=1-np.log2(qb_np[i,j]+1)/np.log2(32768)
            else:
                rgb[i,j,0]=1-np.log2(-qb_np[i,j]+1)/np.log2(32768)
                rgb[i,j,1]=1-np.log2(-qb_np[i,j]+1)/np.log2(32768)
                rgb[i,j,2]=1
    plt.imsave(os.path.join(project_root,"png",f"{name}.png"),rgb)

plot_qb(qb[0],"Pf01.bin_sz3_qb")
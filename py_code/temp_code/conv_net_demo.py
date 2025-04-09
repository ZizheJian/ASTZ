import torch,os
import numpy as np
from torch import Tensor
from typing import List
from torch.nn import functional as F
from matplotlib.colors import hsv_to_rgb
import matplotlib.pyplot as plt

def plot(data:Tensor,path:str)->None:
    data=data[32:96,32:96]
    data=((data.numpy()+1)/2).clip(0,1)
    h=data*5/6
    s=np.ones_like(h)
    v=np.ones_like(h)
    hsv=np.stack((h,s,v),axis=-1)
    rgb=hsv_to_rgb(hsv)
    plt.imsave(path,rgb)

torch.set_num_threads(8)
data_path:str="/anvil/projects/x-cis240192/x-zjian1/APS_Kaz/xpcs-998x128x128.bin.f32"
data_shape:List[int]=[1,128,128]

file_float_num=data_shape[0]*data_shape[1]*data_shape[2]
tgt_data=torch.from_file(data_path,dtype=torch.float32,size=file_float_num)
tgt_data=tgt_data.view([1,1]+data_shape)
tgt_data_min=tgt_data.min()
tgt_data_max=tgt_data.max()
tgt_data=2*(tgt_data-tgt_data_min)/(tgt_data_max-tgt_data_min)-1

cur_data=tgt_data.clone()
cur_data[:,:,:,1::2]=0
mask=torch.zeros([1,2]+data_shape,dtype=torch.bool)
mask[:,0,:,0::2]=1
mask[:,1,:,1::2]=1
plot(tgt_data[0,0,0],os.path.join("png",f"{os.path.basename(data_path)}_tgt.png"))
########HDE########
cur_data_pad=F.pad(cur_data,(1,1,1,1,1,1),value=0)
tgt_num=mask[:,1].sum()
param_num=2
mat_A=torch.zeros([tgt_num,param_num],dtype=torch.float32)
mat_B=torch.zeros([tgt_num],dtype=torch.float32)
mat_A[:,0]=cur_data_pad[:,:,1:cur_data_pad.shape[2]-1,0:cur_data_pad.shape[3]-2,1:cur_data_pad.shape[4]-1][mask[:,1:2]]
mat_A[:,1]=cur_data_pad[:,:,1:cur_data_pad.shape[2]-1,2:cur_data_pad.shape[3],1:cur_data_pad.shape[4]-1][mask[:,1:2]]
mat_B=tgt_data[mask[:,1:2]]
lstsq_result=torch.linalg.lstsq(mat_A,mat_B,driver="gels")
mat_X=lstsq_result.solution
conv=torch.zeros([1,1,3,3,3],dtype=torch.float32)
conv[0,0,1,0,1]=mat_X[0]
conv[0,0,1,2,1]=mat_X[1]
h=F.conv3d(cur_data,conv,padding=1)
h[mask[:,0:1]]=tgt_data[mask[:,0:1]]
plot(h[0,0,0],os.path.join("png",f"{os.path.basename(data_path)}_hde.png"))
########NET########
cur_data=h.clone()
class Net(torch.nn.Module):
    def __init__(self)->None:
        super(Net,self).__init__()
        self.layers=torch.nn.ModuleList()
        self.bns=torch.nn.ModuleList()
        self.layers.append(torch.nn.Conv3d(1,8,kernel_size=3,padding=1))
        self.bns.append(torch.nn.BatchNorm3d(8))
        for i in range(16-2):
            self.layers.append(torch.nn.Conv3d(8,8,kernel_size=3,padding=1))
            self.bns.append(torch.nn.BatchNorm3d(8))
        self.layers.append(torch.nn.Conv3d(8,1,kernel_size=3,padding=1))
        self.relu=torch.nn.ReLU()
    def forward(self,x:Tensor)->Tensor:
        x_backup=x.clone()
        x=self.layers[0](x)
        x=self.bns[0](x)
        x=self.relu(x)
        for i in range(1,len(self.layers)-1):
            x=self.layers[i](x)
            x=self.bns[i](x)
            x=self.relu(x)
        x=x_backup+self.layers[-1](x)
        return x
net=Net()
optimizer=torch.optim.Adam(net.parameters(),lr=0.001)
criterion=torch.nn.MSELoss()
scheduler=torch.optim.lr_scheduler.StepLR(optimizer,step_size=1,gamma=0.1**(1/1000))
for epoch in range(1000):
    optimizer.zero_grad()
    h=net(cur_data)
    loss=criterion(h[mask[:,1:2]],tgt_data[mask[:,1:2]])
    loss.backward()
    optimizer.step()
    scheduler.step()
    if epoch%100==0:
        print(f"epoch={epoch},loss={loss.item()}")
h=h.detach()
h[mask[:,0:1]]=tgt_data[mask[:,0:1]]
plot(h[0,0,0],os.path.join("png",f"{os.path.basename(data_path)}_net.png"))
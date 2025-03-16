import torch
import numpy as np
from args import args_c
from plot_py import plot_c

def separate_diffraction_average_residual(args:args_c,plotter:plot_c):
    X=np.linspace((1-args.data_shape[1])/2,(args.data_shape[1]-1)/2,args.data_shape[1])
    Y=np.linspace((1-args.data_shape[2])/2,(args.data_shape[2]-1)/2,args.data_shape[2])
    X,Y=np.meshgrid(X,Y)
    R=np.round(np.sqrt(X**2+Y**2)).astype(int)
    max_R=R[0,0]
    args.average_data=np.zeros((1,args.data_shape[0],max_R+1))
    args.average_data_shape=[1,args.data_shape[0],max_R+1]
    num_per_R=np.bincount(R.ravel(),minlength=max_R+1)
    for i0 in range(args.data_shape[0]):
        np.add.at(args.average_data[0,i0],R,args.data[i0])
    args.average_data[0,:,1:]/=num_per_R[1:]
    args.residual_data=torch.zeros_like(args.data)
    for i0 in range(args.data_shape[0]):
        args.residual_data[i0]=args.data[i0]-args.average_data[0,i0,R]
    plotter.plot_4_data(args.residual_data,"xpcs_fit")
    args.average_data=torch.tensor(args.average_data,dtype=torch.float32)

def get_actual_residual_data(args:args_c):
    X=np.linspace((1-args.data_shape[1])/2,(args.data_shape[1]-1)/2,args.data_shape[1])
    Y=np.linspace((1-args.data_shape[2])/2,(args.data_shape[2]-1)/2,args.data_shape[2])
    X,Y=np.meshgrid(X,Y)
    R=np.round(np.sqrt(X**2+Y**2)).astype(int)
    print(args.residual_data.shape)
    print(args.data.shape)
    print(args.decompressed_average_data.shape)
    for i0 in range(args.data_shape[0]):
        args.residual_data[i0]=args.data[i0]-args.decompressed_average_data[0,i0,R]

def add_average_and_residual_data(args:args_c):
    X=np.linspace((1-args.data_shape[1])/2,(args.data_shape[1]-1)/2,args.data_shape[1])
    Y=np.linspace((1-args.data_shape[2])/2,(args.data_shape[2]-1)/2,args.data_shape[2])
    X,Y=np.meshgrid(X,Y)
    R=np.round(np.sqrt(X**2+Y**2)).astype(int)
    decompressed_data=torch.zeros_like(args.data)
    for i0 in range(args.data_shape[0]):
        decompressed_data[i0]=args.decompressed_average_data[0,i0,R]+args.decompressed_residual_data[i0]
    return decompressed_data
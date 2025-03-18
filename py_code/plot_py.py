import subprocess,ctypes,torch,os
import numpy as np
from args import args_c
from torch import Tensor
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb

class plot_c:
    def __init__(self,args:args_c)->None:
        self.project_root=args.project_root
    def plot_data(self,data:Tensor,name:str,data_min:float=None,data_max:float=None)->None:
        if data_min is None:
            data_min=data.min().item()
        if data_max is None:
            data_max=data.max().item()
        data=((data.numpy()-data_min)/(data_max-data_min)).clip(0,1)
        h=data*5/6
        s=np.ones_like(h)
        v=np.ones_like(h)
        hsv=np.stack((h,s,v),axis=-1)
        rgb=hsv_to_rgb(hsv)
        plt.imsave(os.path.join(self.project_root,"png",f"{name}.png"),rgb)

# class plot_c:
#     def __init__(self,args:args_c)->None:
#         command=f"rm -f {args.project_root}/code/plot_gcc.so"
#         command+=f" && gcc -shared -o {args.project_root}/code/plot_gcc.so -fPIC {args.project_root}/code/plot_gcc.c"
#         print(command)
#         gcc_compile_process=subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
#         _,gcc_stderr=gcc_compile_process.communicate()
#         if gcc_compile_process.returncode==0:
#             print("plot_gcc.so compilation successful")
#         else:
#             print("plot_gcc.so compilation failed")
#             print("stderr:",gcc_stderr)
#         self.lib=ctypes.CDLL(f"{args.project_root}/code/plot_gcc.so")
#         self.lib.plot.argtypes=[ctypes.c_char_p,ctypes.POINTER(ctypes.c_float),ctypes.POINTER(ctypes.c_int),ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int]
#     def _plot(self,name:str,data:Tensor,plot_type:Tensor,h:int,w:int,hn:int,wn:int)->None:
#         fig_path=ctypes.c_char_p(f"/home/x-zjian1/jzzz/pngs/{name}.png".encode("utf-8"))
#         self.lib.plot(fig_path,data.detach().numpy().ctypes.data_as(ctypes.POINTER(ctypes.c_float)),plot_type.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),h,w,hn,wn)
#     def plot_1_data(self,data:Tensor,name:str)->None:
#         temp_data=data[0]
#         plot_type=np.array([[0]]).reshape(-1).astype(np.int32)
#         self._plot(name,temp_data,plot_type,data.shape[1],data.shape[2],1,1)
#     def plot_2_data(self,data:Tensor,name:str)->None:
#         temp_data=torch.cat((data[0],data[-1]),dim=1)
#         plot_type=np.array([[0],[0]]).reshape(-1).astype(np.int32)
#         self._plot(name,temp_data,plot_type,data.shape[1],data.shape[2],1,2)
#     def plot_4_data(self,data:Tensor,name:str)->None:
#         length=data.shape[0]
#         temp_data=torch.cat((data[0],data[(length-1)//3],data[(2*length-2)//3],data[length-1]),dim=1)
#         plot_type=np.array([[0],[0],[0],[0]]).reshape(-1).astype(np.int32)
#         self._plot(name,temp_data,plot_type,data.shape[1],data.shape[2],1,4)
#     def plot_4_qb(self,data:Tensor,name:str)->None:
#         data=data.float()
#         length=data.shape[0]
#         temp_data=torch.cat((data[0],data[(length-1)//3],data[(2*length-2)//3],data[length-1]),dim=1)
#         plot_type=np.array([[2],[2],[2],[2]]).reshape(-1).astype(np.int32)
#         self._plot(name,temp_data,plot_type,data.shape[1],data.shape[2],1,4)
#     def plot_8_qb(self,data:Tensor,name:str)->None:
#         f_data=data[0,0].float()
#         length=f_data.shape[0]
#         f_data_cat=torch.cat((torch.cat((f_data[0],f_data[(length-1)//7],f_data[(2*length-2)//7],f_data[(3*length-3)//7]),dim=1),
#                               torch.cat((f_data[(4*length-4)//7],f_data[(5*length-5)//7],f_data[(6*length-6)//7],f_data[length-1]),dim=1)),dim=0)
#         plot_type=np.array([[2,2,2,2],
#                             [2,2,2,2]]).reshape(-1).astype(np.int32)
#         self._plot(name,f_data_cat,plot_type,f_data.shape[1],f_data.shape[2],2,4)
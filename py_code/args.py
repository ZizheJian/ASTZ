import torch,argparse,os
from torch import Tensor,tensor
from typing import List

class args_c:
    def __init__(self):
        #手动设置的参数
        self.code_root:str=""
        self.project_root:str=""
        self.data_name:str=""
        self.data_path:str=""
        self.data_compressed_path:str=""
        self.data_decompressed_path:str=""
        self.data_shape:List[int]=[]
        self.rel_eb:float=0
        self.doughnut:bool=False
        self.method:str=""
        self.FHDE_threshold:float=0
        self.model_block_step=[]
        self.min_reference_num:int=0
        self.method_average:List[str]=[]
        self.method_residual:List[str]=[]
        self.parameter_relative_eb:float=0
        self.FHDE_threshold_average:float=0
        self.FHDE_threshold_residual:float=0
        self.pivot_ratio:int=0
        #仅初始化的参数
        self.data_min:float=0
        self.data_max:float=0
        self.abs_eb:float=0
        self.data:Tensor=tensor([],dtype=torch.float32)
        self.pivot:Tensor=tensor([],dtype=torch.float32)
        self.pivot_num:int=0
        self.parameter:List[Tensor]=[]
        self.data_decompressed=tensor([],dtype=torch.float32)
        self.data_average=tensor([],dtype=torch.float32)
        self.data_average_decompressed=tensor([],dtype=torch.float32)
        self.data_residual=tensor([],dtype=torch.float32)
        self.data_residual_decompressed=tensor([],dtype=torch.float32)
        self.data_shape_average:List[int]=[]
        self.qb=tensor([],dtype=torch.int32)
        self.qb_tensor=tensor([],dtype=torch.float32)
        self.qb_begin:int=0
        self.qb_end:int=0
        self.tgt_data_list:List[Tensor]=[]
        self.begin_data=tensor([],dtype=torch.float32)
        self.mask_list:List[Tensor]=[]#true表示直接继承自上一层，false表示需要插值
        self.eb_power_list:List[int]=None
        self.cur_shape_list:List[List[int]]=None
        self.topology_id_list:List[int]=None
        self.parameter_eb:float=0
        #自动生成的参数
        self.pos:Tensor=None
        self.padded_pos:Tensor=None
        self.pos_ch:int=0
        self.apply_setting()
    def apply_setting(self):
        parser=argparse.ArgumentParser()
        parser.add_argument("-f",dest="data_type_float32",action="store_true")
        parser.add_argument("-i",dest="data_path",type=str)
        parser.add_argument("-z",dest="data_compressed_path",type=str)
        parser.add_argument("-o",dest="data_decompressed_path",type=str)
        parser.add_argument("-E",dest="err",nargs="+")
        parser.add_argument("-3",dest="data_shape",nargs=3,type=int)
        parser.add_argument("-M",dest="method",nargs="+")
        parser.add_argument("-doughnut",dest="doughnut",action="store_true")
        temp_args=parser.parse_args()
        self.code_root=os.path.dirname(__file__)
        self.project_root=os.path.dirname(self.code_root)
        self.data_name=os.path.basename(temp_args.data_path)
        self.data_path=temp_args.data_path
        self.data_compressed_path=temp_args.data_compressed_path
        self.data_decompressed_path=temp_args.data_decompressed_path
        self.data_shape=[temp_args.data_shape[2],temp_args.data_shape[1],temp_args.data_shape[0]]
        self.rel_eb=float(temp_args.err[1])
        self.doughnut=temp_args.doughnut
        self.method=temp_args.method[0]
        self.FHDE_threshold=float(temp_args.method[1])
        self.model_block_step=[32,32,32]
        self.padded_pos=torch.zeros([4]+[i+2 for i in self.model_block_step]).unsqueeze(0).float()
        self.padded_pos[0,0]=(torch.arange(self.model_block_step[0]+2)-1).view(-1,1,1).expand([x+2 for x in self.model_block_step])*2/(self.model_block_step[0]-1)-1
        self.padded_pos[0,1]=(torch.arange(self.model_block_step[1]+2)-1).view(1,-1,1).expand([x+2 for x in self.model_block_step])*2/(self.model_block_step[1]-1)-1
        self.padded_pos[0,2]=(torch.arange(self.model_block_step[2]+2)-1).view(1,1,-1).expand([x+2 for x in self.model_block_step])*2/(self.model_block_step[2]-1)-1
        self.padded_pos[0,3]=torch.ones([x+2 for x in self.model_block_step])
        self.padded_pos=self.padded_pos[:,0:4]
        self.pos_ch=self.padded_pos.shape[1]
        self.min_reference_num=1
        self.separate_average_residual:bool=False
        self.method_average=["FHDE"]
        self.method_residual=["FHDE"]
        self.parameter_relative_eb=1e-2
        self.FHDE_threshold_average=5
        self.FHDE_threshold_residual=5
        self.pivot_ratio=2**13
import torch,argparse,os
from torch import Tensor,tensor
from typing import List

class args_c:
    def __init__(self):
        self.code_root=os.path.dirname(__file__)
        self.project_root=os.path.dirname(self.code_root)

        parser=argparse.ArgumentParser()
        parser.add_argument("-f",dest="data_type_float32",action="store_true")
        parser.add_argument("-uint16",dest="data_type_uint16",action="store_true")
        parser.add_argument("-i",dest="data_path",type=str)
        parser.add_argument("-z",dest="data_compressed_path",type=str)
        parser.add_argument("-o",dest="data_decompressed_path",type=str)
        parser.add_argument("-c",dest="stencil_path",type=str)
        parser.add_argument("-E",dest="err",nargs="+")
        parser.add_argument("-3",dest="data_shape",nargs=3,type=int)
        parser.add_argument("-2",dest="data_shape",nargs=2,type=int)
        parser.add_argument("-M",dest="method",nargs="+")
        temp_args=parser.parse_args()
        self.data_type_float32=temp_args.data_type_float32
        self.data_type_uint16=temp_args.data_type_uint16
        self.data_name=os.path.basename(temp_args.data_path)
        self.data_path=temp_args.data_path
        self.data_compressed_path=temp_args.data_compressed_path
        self.data_decompressed_path=temp_args.data_decompressed_path
        self.stencil_path=temp_args.stencil_path
        if len(temp_args.data_shape)==3:
            self.data_shape=[temp_args.data_shape[2],temp_args.data_shape[1],temp_args.data_shape[0]]
        else:
            self.data_shape=[temp_args.data_shape[1],temp_args.data_shape[0],1]
        self.eb_type=temp_args.err[0]
        if self.eb_type=="ABS":
            self.abs_eb=float(temp_args.err[1])
        elif self.eb_type=="REL":
            self.rel_eb=float(temp_args.err[1])
        self.method=temp_args.method[0]
        if self.method=="FHDE":
            self.FHDE_threshold=float(temp_args.method[1])
        else:
            self.FHDE_threshold=0

        self.data_min:float=0
        self.data_max:float=0
        self.data:Tensor=tensor([],dtype=torch.float32)
        self.pivot:Tensor=tensor([],dtype=torch.float32)
        self.pivot_num:int=0
        self.parameter:List[Tensor]=[]
        self.data_decompressed=tensor([],dtype=torch.float32)
        self.bs_after_zstd:bytes=b""
        self.qb=tensor([],dtype=torch.int32)
        self.qb_begin:int=0
        self.qb_end:int=0
        self.cur_shape_list:List[List[int]]=None
        self.stencil_id_list:List[int]=None
        self.parameter_eb:float=0
        
        self.model_block_step=[32,32,32]
        self.padded_pos=torch.zeros([4]+[i+2 for i in self.model_block_step]).unsqueeze(0).float()#需要pad是因为cur_block_ext有pad，方便一些，没有pad也能写
        self.padded_pos[0,0]=(torch.arange(self.model_block_step[0]+2)-1).view(-1,1,1).expand([x+2 for x in self.model_block_step])*2/(self.model_block_step[0]-1)-1
        self.padded_pos[0,1]=(torch.arange(self.model_block_step[1]+2)-1).view(1,-1,1).expand([x+2 for x in self.model_block_step])*2/(self.model_block_step[1]-1)-1
        self.padded_pos[0,2]=(torch.arange(self.model_block_step[2]+2)-1).view(1,1,-1).expand([x+2 for x in self.model_block_step])*2/(self.model_block_step[2]-1)-1
        self.padded_pos[0,3]=1
        self.padded_pos=self.padded_pos[:,0:4]
        self.pos_ch_num=self.padded_pos.shape[1]
        self.min_reference_num=1
        self.regularization_a=1e-1
        self.parameter_relative_eb=1e-2
        self.pivot_ratio=2**15
        self.eb_tune_ratio=0.95
        self.fix_coefficient:bool=False
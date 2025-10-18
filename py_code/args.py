import torch,argparse,os
from torch import Tensor,tensor
from typing import List

class args_c:
    def __init__(self,argv=None):
        self.code_root=os.path.dirname(__file__)
        self.project_root=os.path.dirname(self.code_root)

        parser=argparse.ArgumentParser()
        parser.add_argument("-f32",dest="data_type_f32",action="store_true")
        parser.add_argument("-ui16",dest="data_type_ui16",action="store_true")
        parser.add_argument("-i",dest="data_path",type=str)
        parser.add_argument("-z",dest="data_compressed_path",type=str)
        parser.add_argument("-o",dest="data_decompressed_path",type=str)
        parser.add_argument("-c",dest="stencil_path",type=str)
        parser.add_argument("-E",dest="err",nargs="+")
        parser.add_argument("-4",dest="data_shape",nargs=4,type=int)
        parser.add_argument("-3",dest="data_shape",nargs=3,type=int)
        parser.add_argument("-2",dest="data_shape",nargs=2,type=int)
        parser.add_argument("-1",dest="data_shape",nargs=1,type=int)
        parser.add_argument("-M",dest="method",nargs="+")
        parser.add_argument("-a",dest="analysis",action="store_true")
        parser_results=parser.parse_args(argv)
        if parser_results.data_type_f32:
            self.data_type_str="f32"
            self.dtype=torch.float32
            self.unit_size=4
        elif parser_results.data_type_ui16:
            self.data_type_str="ui16"
            self.dtype=torch.uint16
            self.unit_size=2
        self.data_name=os.path.basename(parser_results.data_path)
        self.data_path=parser_results.data_path
        self.data_compressed_path=parser_results.data_compressed_path
        self.data_decompressed_path=parser_results.data_decompressed_path
        self.stencil_path=parser_results.stencil_path
        if len(parser_results.data_shape)==4:
            self.dim_num=4
            self.data_shape=[parser_results.data_shape[0],parser_results.data_shape[1],parser_results.data_shape[2],parser_results.data_shape[3]]
        elif len(parser_results.data_shape)==3:
            self.dim_num=3
            self.data_shape=[parser_results.data_shape[0],parser_results.data_shape[1],parser_results.data_shape[2]]
        elif len(parser_results.data_shape)==2:
            self.dim_num=2
            self.data_shape=[parser_results.data_shape[0],parser_results.data_shape[1]]
        elif len(parser_results.data_shape)==1:
            self.dim_num=1
            self.data_shape=[parser_results.data_shape[0]]
        self.eb_type=parser_results.err[0]
        if self.eb_type=="ABS":
            self.abs_eb=float(parser_results.err[1])
        elif self.eb_type=="REL":
            self.rel_eb=float(parser_results.err[1])
        self.method=parser_results.method[0]
        if self.method in ["FIX","HDE","FHDE","FHDE_gpu"]:
            if self.method=="FHDE" or self.method=="FHDE_gpu":
                self.FHDE_threshold=float(parser_results.method[1])
            else:
                self.FHDE_threshold=0
        else:
            raise ValueError(f"Unsupported method: {self.method}")
        if "gpu" in self.method:
            if torch.cuda.is_available():
                self.device=torch.device("cuda")
            else:
                raise ValueError("No available GPU!")
        self.analysis=parser_results.analysis
        self.output_decompressed_data=False

        self.data_min:float=0
        self.data_max:float=0
        self.data:Tensor=tensor([],dtype=torch.float32)
        self.pivot:Tensor=tensor([],dtype=torch.float32)
        self.pivot_num:int=0
        self.parameters:List[Tensor]=[]
        self.data_decompressed=tensor([],dtype=torch.float32)
        self.zstd_bs:bytes=b""
        self.qb=tensor([],dtype=torch.int32)
        self.qb_begin:int=0
        self.qb_end:int=0
        self.cur_shape_list:List[List[int]]=None
        self.stencil_id_list:List[int]=None
        self.parameter_eb:float=0

        self.pivot_ratio=2**17
        self.eb_tune_ratio=0.95
        if self.dim_num==4:
            self.model_block_step=[16,16,16,16]
            self.pos=torch.zeros([1,5]+self.model_block_step).float()
            self.pos[0,0]=torch.arange(self.model_block_step[0]).view(-1,1,1,1).expand(self.model_block_step)*2/(self.model_block_step[0]-1)-1
            self.pos[0,1]=torch.arange(self.model_block_step[1]).view(1,-1,1,1).expand(self.model_block_step)*2/(self.model_block_step[1]-1)-1
            self.pos[0,2]=torch.arange(self.model_block_step[2]).view(1,1,-1,1).expand(self.model_block_step)*2/(self.model_block_step[2]-1)-1
            self.pos[0,3]=torch.arange(self.model_block_step[3]).view(1,1,1,-1).expand(self.model_block_step)*2/(self.model_block_step[3]-1)-1
            self.pos[0,4]=1
        if self.dim_num==3:
            self.model_block_step=[64,64,64]
            self.pos=torch.zeros([1,4]+self.model_block_step).float()
            self.pos[0,0]=torch.arange(self.model_block_step[0]).view(-1,1,1).expand(self.model_block_step)*2/(self.model_block_step[0]-1)-1
            self.pos[0,1]=torch.arange(self.model_block_step[1]).view(1,-1,1).expand(self.model_block_step)*2/(self.model_block_step[1]-1)-1
            self.pos[0,2]=torch.arange(self.model_block_step[2]).view(1,1,-1).expand(self.model_block_step)*2/(self.model_block_step[2]-1)-1
            self.pos[0,3]=1
        elif self.dim_num==2:
            self.model_block_step=[512,512]
            self.pos=torch.zeros([1,3]+self.model_block_step).float()
            self.pos[0,0]=torch.arange(self.model_block_step[0]).view(-1,1).expand(self.model_block_step)*2/(self.model_block_step[0]-1)-1
            self.pos[0,1]=torch.arange(self.model_block_step[1]).view(1,-1).expand(self.model_block_step)*2/(self.model_block_step[1]-1)-1
            self.pos[0,2]=1
        elif self.dim_num==1:
            self.model_block_step=[262144]
            self.pos=torch.zeros([1,2]+self.model_block_step).float()
            self.pos[0,0]=torch.arange(self.model_block_step[0]).view(-1).expand(self.model_block_step)*2/(self.model_block_step[0]-1)-1
            self.pos[0,1]=1
        self.min_reference_num=1
        # for SDRBENCH-EXAFEL min_reference_num=15
        self.regularization_a=1e-4
        self.parameter_relative_eb=1e-1
        self.sampling_gap=1
        self.interpolation_method="linear" # "linear" or "cubic"

import torch
from torch import Tensor,tensor
from typing import List

class args_c:
    def __init__(self):
        #手动设置的参数
        self.project_root=""
        self.data_name=""
        self.data_path=""
        self.data_shape=[]
        self.rel_eb=0
        self.model_block_step=[]
        self.max_epoch=0
        self.min_reference_num:int=0
        self.baseline_method:List[str]=[]
        self.average_baseline_method:List[str]=[]
        self.residual_baseline_method:List[str]=[]
        self.parameter_relative_eb:float=0
        self.FHDE_global_threshold:float=0
        self.FHDE_global_threshold_average:float=0
        self.FHDE_global_threshold_residual:float=0
        #仅初始化的参数
        self.data_min:float=0
        self.data_max:float=0
        self.abs_eb:float=0
        self.data=tensor([],dtype=torch.float32)
        self.decompressed_data=tensor([],dtype=torch.float32)
        self.average_data=tensor([],dtype=torch.float32)
        self.decompressed_average_data=tensor([],dtype=torch.float32)
        self.residual_data=tensor([],dtype=torch.float32)
        self.decompressed_residual_data=tensor([],dtype=torch.float32)
        self.average_data_shape:List[int]=[]
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
        self.apply_my_initial_setting()
    def apply_my_initial_setting(self):
        self.project_root="/home/x-zjian1/jzzz"
        # self.data_name="ISABEL_Pf01"
        # self.data_path="/anvil/projects/x-cis240192/x-zjian1/ISABEL/P/Pf01.bin"
        # self.data_shape=[100,500,500]
        # self.data_name="xpcs-998x128x128"
        # self.data_path="/anvil/projects/x-cis240192/x-zjian1/APS_Kaz/xpcs-998x128x128.bin.f32"
        # self.data_shape=[998,128,128]
        # self.data_name="EXAFEL"
        # self.data_path="/anvil/projects/x-cis240192/x-zjian1/EXAFEL/SDRBENCH-EXAFEL-data-13x1480x1552.f32"
        # self.data_shape=[13,1480,1552]
        # self.data_name="NYX_baryon_density_log10"
        # self.data_path="/anvil/projects/x-cis240192/x-zjian1/NYX/baryon_density_log10_cut.f32"
        # self.data_shape=[256,256,256]
        # self.data_name="Avg_L0470"
        # self.data_path="/anvil/projects/x-cis240192/x-zjian1/APS_DYS/9-ID_CSSI_data/benchmarkdata/Avg_L0470_Double_exp_elong_siemens_1p00sampit_0p05inplane_patch1_of1_part0_001_cut.bin"
        # self.data_shape=[150,453,390]
        self.data_name="APSU_TestData_004"
        self.data_path="/anvil/projects/x-cis240192/x-zjian1/APS_DYS/xpcs_datasets/APSU_TestData_004/APSU_TestData_004_cut.bin"
        self.data_shape=[614,312,363]
        self.rel_eb=1e-2
        self.model_block_step=[32,32,32]
        self.max_epoch=1000
        self.padded_pos=torch.zeros([4]+[i+2 for i in self.model_block_step]).unsqueeze(0).float()
        self.padded_pos[0,0]=(torch.arange(self.model_block_step[0]+2)-1).view(-1,1,1).expand([x+2 for x in self.model_block_step])*2/(self.model_block_step[0]-1)-1
        self.padded_pos[0,1]=(torch.arange(self.model_block_step[1]+2)-1).view(1,-1,1).expand([x+2 for x in self.model_block_step])*2/(self.model_block_step[1]-1)-1
        self.padded_pos[0,2]=(torch.arange(self.model_block_step[2]+2)-1).view(1,1,-1).expand([x+2 for x in self.model_block_step])*2/(self.model_block_step[2]-1)-1
        self.padded_pos[0,3]=torch.ones([x+2 for x in self.model_block_step])
        self.min_reference_num=1
        self.separate_average_residual:bool=False
        self.baseline_method=["FHDE"]
        self.average_baseline_method=["FHDE"]
        self.residual_baseline_method=["FHDE"]
        self.parameter_relative_eb=1e-2
        self.FHDE_global_threshold=2
        self.FHDE_global_threshold_average=5
        self.FHDE_global_threshold_residual=5
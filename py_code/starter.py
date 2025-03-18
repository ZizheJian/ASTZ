#整理一下python代码

import subprocess,os
from typing import List

# data_name:str="xpcs-998x128x128"
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/APS_Kaz/xpcs-998x128x128.bin.f32"
# data_shape:List[int]=[998,128,128]
# data_name:str="EXAFEL"
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/EXAFEL/SDRBENCH-EXAFEL-data-13x1480x1552.f32"
# data_shape:List[int]=[13,1480,1552]
# data_name:str="Avg_L0470"
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/APS_DYS/9-ID_CSSI_data/benchmarkdata/Avg_L0470_Double_exp_elong_siemens_1p00sampit_0p05inplane_patch1_of1_part0_001_cut.bin"
# data_shape:List[int]=[150,453,390]
data_name:str="APSU_TestData_004"
data_path:str="/anvil/projects/x-cis240192/x-zjian1/APS_DYS/xpcs_datasets/APSU_TestData_004/APSU_TestData_004_cut.bin"
data_shape:List[int]=[614,312,363]
# data_name="NYX_baryon_density_log10"
# data_path="/anvil/projects/x-cis240192/x-zjian1/NYX/baryon_density_log10_cut.f32"
# data_shape=[13,1480,1552]

rel_eb:float=1e-3
doughnut:bool=False
method:str="FHDE"
method_average:str="FHDE"
method_residual:str="FHDE"
FHDE_threshold=2
FHDE_threshold_average=FHDE_threshold
FHDE_threshold_residual=FHDE_threshold
search_threshold:bool=False

starter_file_path=os.path.abspath(__file__)
code_directory_path=os.path.dirname(starter_file_path)

if not search_threshold:
    if not doughnut:
        # command=f"python3 {os.path.join(code_directory_path,'generate_topology_list.py')} "
        # command+=f"-f -i {data_path} -E REL {rel_eb} -3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -M {method} {FHDE_threshold} "
        # print(command)
        # subprocess.run(command,shell=True,encoding="utf-8")
        command=f"python3 {os.path.join(code_directory_path,'compress.py')} "
        command+=f"-f -i {data_path} -z {os.path.join(data_path,'.fhde')} -E REL {rel_eb} -3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -M {method} {FHDE_threshold} "
        print(command)
        subprocess.run(command,shell=True,encoding="utf-8")
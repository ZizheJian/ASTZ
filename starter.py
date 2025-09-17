import subprocess,os,random,torch
from typing import List
from py_code.starter_functions.call_generate_stencil_list import call_generate_stencil_list
from py_code.starter_functions.call_py_compress import call_py_compress,call_py_decompress
from py_code.starter_functions.search_threshold import search_threshold
from py_code.code_generator import code_generator
from py_code.starter_functions.call_c_compress import call_c_compress
from py_code.starter_functions.call_sz3_compress import call_sz3_compress
from py_code.starter_functions.call_hpez_compress import call_hpez_compress
from py_code.starter_functions.call_zfp_compress import call_zfp_compress

# data_path:str="/anvil/projects/x-cis240192/x-zjian1-in-cis240192/APS_DYS/xpcs_datasets/APSU_TestData_004/block/APSU_TestData_004_float_block.bin_111"
# data_type:str="f"
# data_shape:List[int]=[256,390,454]
# rel_eb_list=[1e-1,1e-2,1e-3,1e-4]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1-in-cis240192/APS_DYS/xpcs_datasets/APSU_TestData_004/APSU_TestData_004.bin"
# data_shape:List[int]=[1024,1558,1813]
# rel_eb_list=[1e-1,1e-2,1e-3,1e-4]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1-in-cis240192/APS_DYS/xpcs_new_from_miaoqi/D0131_US-Cup2_a0010_f005000_r00001_cut.bin"
# data_shape:List[int]=[625,270,258]
# rel_eb_list=[3e-1,1e-1,3e-2,1e-2]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1-in-cis240192/EXAFEL/SDRBENCH-EXAFEL-data-130x1480x1552_cut.f32"
# data_shape:List[int]=[13,1480,1552]
# rel_eb_list=[1e-1,1e-2,1e-3,1e-4]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1-in-cis240192/EXAFEL/block/SDRBENCH-EXAFEL-data-130x1480x1552.f32_000"
# data_type:str="f"
# data_shape:List[int]=[65,740,776]
# rel_eb_list=[1e-1,1e-2,1e-3,1e-4]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1-in-cis240192/APS_Kaz/xpcs-998x128x128.bin.f32"
# data_shape:List[int]=[998,128,128]
# rel_eb_list=[3e-1,1e-1,3e-2,1e-2]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1-in-cis240192/APS_DYS/xpcs_datasets/E017_CeramicGlass_L2Mq0_060C_att00_001/E017_CeramicGlass_L2Mq0_060C_att00_001_001.bin"
# data_shape:List[int]=[1024,1813,1558]
# rel_eb_list=[1e-1,1e-2,3e-3,1e-3,3e-4,1e-4]
data_path:str="/anvil/projects/x-cis240192/x-zjian1-in-cis240192/embeddings/plm/embeds_0[(32, 256, 4096)].bin"
data_type:str="f"
data_shape:List[int]=[32,256,4096]
rel_eb_list=[1e-1,1e-2]

sz3_path:str="sz3"
hpez_path:str="hpez"
zfp_path:str="zfp"
calculateSSIM_path:str="calculateSSIM"

whether_generate_stencil_list_using_FHDE=1
whether_generate_stencil_list_using_HDE=0
#python compress using FHDE
PY_FHDE=0
#python compress using HDE
PY_HDE=0
#search threshold for FHDE
SH_TH=0
#c compress using FHDE
C_FHDE=0
#c compress using HDE
C_HDE=0
#SZ3 compress
SZ3=0
#HPEZ compress
HPEZ=0
#ZFP compress
ZFP=0

rel_eb:float=1e-4
FHDE_threshold=9
large_scale_testing:bool=False
calculate_ssim:bool=False

data_name=os.path.basename(data_path)
starter_file_path=os.path.abspath(__file__)
project_directory_path=os.path.dirname(starter_file_path)
rel_eb_str:str=f"{rel_eb:.0e}"

if not large_scale_testing:
    if whether_generate_stencil_list_using_FHDE:
        call_generate_stencil_list(project_directory_path,data_path,data_type,data_shape,rel_eb,"FHDE",FHDE_threshold)
    if PY_FHDE:
        call_py_compress(project_directory_path,data_path,data_type,data_shape,rel_eb,"FHDE",FHDE_threshold,calculate_ssim)
        call_py_decompress()
    if SH_TH:
        search_threshold(project_directory_path,data_path,data_type,data_shape,rel_eb,"FHDE",FHDE_threshold)
    # elif method=="c_FHDE":
    #     code_generator(project_directory_path,data_path,data_type,rel_eb,"FHDE")
    #     call_c_compress(project_directory_path,data_path,rel_eb,FHDE_threshold)
    # elif method=="c_HDE":
    #     code_generator(project_directory_path,data_path,data_type,rel_eb,"HDE")
    #     call_c_compress(project_directory_path,data_path,rel_eb,0)
    if SZ3:
        cr,psnr,ssim=call_sz3_compress(sz3_path,calculateSSIM_path,data_path,data_type,data_shape,rel_eb,calculate_ssim)
else:
    for rel_eb in rel_eb_list:
        if not os.path.exists(f"large_scale_record/{data_name}.txt"):
            with open(f"large_scale_record/{data_name}.txt","w") as f:  pass
        ########ASTZ########
        call_generate_stencil_list(project_directory_path,data_path,data_type,data_shape,rel_eb,"FHDE",FHDE_threshold)
        cr,psnr,ssim=call_py_compress(project_directory_path,data_path,data_type,data_shape,rel_eb,"FHDE",FHDE_threshold,calculate_ssim)
        with open(f"large_scale_record/{data_name}.txt","a") as f:
            f.write(f"{cr} {32/cr} {psnr} {ssim} ")
        ########SZ3########
        # cr,psnr,ssim=call_sz3_compress(sz3_path,calculateSSIM_path,data_path,data_type,data_shape,rel_eb,calculate_ssim)
        # with open(f"large_scale_record/{data_name}.txt","a") as f:
        #     f.write(f"{cr} {32/cr} {psnr} {ssim} ")
        ########HPEZ########
        # cr,psnr,ssim=call_hpez_compress(hpez_path,calculateSSIM_path,data_path,data_type,data_shape,rel_eb,calculate_ssim)
        # with open(f"large_scale_record/{data_name}.txt","a") as f:
        #     f.write(f"{cr} {32/cr} {psnr} {ssim} ")
        ########ZFP########
        # cr,psnr,ssim=call_zfp_compress(zfp_path,calculateSSIM_path,data_path,data_shape,rel_eb,calculate_ssim)
        # with open(f"large_scale_record/{data_name}.txt","a") as f:
        #     f.write(f"{cr} {32/cr} {psnr} {ssim}\n")
        with open(f"large_scale_record/{data_name}.txt","a") as f:
            f.write("\n")
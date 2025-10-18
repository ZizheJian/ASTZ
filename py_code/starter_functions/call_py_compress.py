import os,subprocess
from typing import List
from py_code.print_and_return_stdout import print_and_return_stdout
from py_code.starter_functions.call_calculateSSIM import call_calculateSSIM

def call_py_compress(project_directory_path:str,data_path:str,data_type:str,data_shape:List[int],rel_eb_str:str,method:str,FHDE_threshold:int=0,stencil_path:str=None):
    data_name=os.path.basename(data_path)
    if stencil_path is None:
        stencil_path=os.path.join(project_directory_path,"stencil_list",rel_eb_str,data_name+".txt")
    command=f"python3 -u {os.path.join(project_directory_path,'py_code','compress.py')} "
    command+=f"-{data_type} -i '{data_path}' -z '{data_path}_{rel_eb_str}.astz' -c '{stencil_path}' -E REL {rel_eb_str} "
    command+=f"-{len(data_shape)} "
    for dim in data_shape:
        command+=f"{dim} "
    command+=f"-M {method} {FHDE_threshold} -a "
    print(command)
    output=print_and_return_stdout(command)
    cr=float(output.split("\n")[-5].split(" ")[-2])
    psnr=float(output.split("\n")[-1].split(" ")[-2])
    return cr,psnr

def call_py_decompress(project_directory_path:str,data_path:str,data_type:str,data_shape:List[int],rel_eb_str:str,method:str,FHDE_threshold:int=0,
                       whether_calculate_ssim:bool=False):
    data_name=os.path.basename(data_path)
    stencil_path=os.path.join(project_directory_path,"stencil_list",rel_eb_str,data_name+".txt")
    command=f"python3 -u {os.path.join(project_directory_path,'py_code','decompress.py')} "
    command+=f"-{data_type} -i '{data_path}' -z '{data_path}_{rel_eb_str}.astz' -o '{data_path}_{rel_eb_str}.astz.bin' -c '{stencil_path}' -E REL {rel_eb_str} "
    command+=f"-{len(data_shape)} "
    for dim in data_shape:
        command+=f"{dim} "
    command+=f"-M {method} {FHDE_threshold} -a "
    print(command)
    output=print_and_return_stdout(command)
    cr=float(output.split("\n")[-2].split(" ")[-2])
    psnr=float(output.split("\n")[-1].split(" ")[-2])
    if whether_calculate_ssim:
        ssim=call_calculateSSIM(data_path,f"{data_path}_{rel_eb_str}.astz.bin",data_shape,data_type)
    else:
        ssim=0
    print(f"\033[31mssim= {ssim:.3f} \033[0m")
    return cr,psnr,ssim
import os,subprocess
from typing import List

def call_py_compress(project_directory_path:str,data_path:str,data_type:str,data_shape:List[int],rel_eb:float,method:str,FHDE_threshold:int,calculate_ssim:bool=False):
    data_name=os.path.basename(data_path)
    rel_eb_str=f"{rel_eb:.0e}"
    stencil_path=os.path.join(project_directory_path,"stencil_list",rel_eb_str,data_name+".txt")
    command=f"python3 {os.path.join(project_directory_path,'py_code','compress.py')} "
    command+=f"-{data_type} -i '{data_path}' -z '{data_path}_{rel_eb_str}.fhde' -o '{data_path}_{rel_eb_str}.fhde.bin' -c '{stencil_path}' "
    command+=f"-E REL {rel_eb_str} -3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -M {method} {FHDE_threshold} "
    print(command)
    process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output_lines=[]
    for line in iter(process.stdout.readline,""):
        print(line,end="",flush=True)
        output_lines.append(line)
    output=("".join(output_lines)).strip()
    cr=float(output.split("\n")[-4].split(" ")[-1])
    psnr=float(output.split("\n")[-1].split(" ")[-1])
    ssim=0
    if calculate_ssim:
        output_lines=[]
        command=f"calculateSSIM -f '{data_path}' '{data_path}_{rel_eb_str}.fhde.bin' {data_shape[2]} {data_shape[1]} {data_shape[0]}"
        process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for line in iter(process.stdout.readline,""):
            print(line,end="",flush=True)
            output_lines.append(line)
        output=("".join(output_lines)).strip()
        ssim=float(output.split("\n")[-1].split(" ")[-1])
    return cr,psnr,ssim

def call_py_decompress():
    pass
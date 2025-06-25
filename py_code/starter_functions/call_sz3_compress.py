import subprocess
from typing import List

def call_sz3_compress(sz3_path:str,calculateSSIM_path:str,data_path:str,data_type:str,data_shape:List[int],rel_eb:float,calculate_ssim:bool=False):
    rel_eb_str:str=f"{rel_eb:.0e}"
    command=f"{sz3_path} -i {data_path} -z {data_path}_{rel_eb_str}.sz3 -o {data_path}_{rel_eb_str}.sz3.bin "
    command+=f"-f -M REL -R {rel_eb} -3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -a"
    process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output_lines=[]
    for line in iter(process.stdout.readline,""):
        print(line,end="",flush=True)
        output_lines.append(line)
    output=("".join(output_lines)).strip()
    cr=float(output.split("\n")[-3].split(" ")[-1])
    psnr=float(output.split("\n")[-6].split(",")[-2].split(" ")[-1])
    ssim=0
    if calculate_ssim:
        output_lines=[]
        command=f"{calculateSSIM_path} -f {data_path} {data_path}_{rel_eb_str}.sz3.bin {data_shape[2]} {data_shape[1]} {data_shape[0]}"
        process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for line in iter(process.stdout.readline,""):
            print(line,end="",flush=True)
            output_lines.append(line)
        output=("".join(output_lines)).strip()
        ssim=float(output.split("\n")[-1].split(" ")[-1])
    return cr,psnr,ssim
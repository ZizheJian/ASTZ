import torch,subprocess
from typing import List

def call_zfp_compress(zfp_path:str,calculateSSIM_path:str,data_path:str,data_type:str,data_shape:List[int],rel_eb:float,calculate_ssim:bool=False):
    rel_eb_str=f"{rel_eb:.0e}"
    data=torch.from_file(data_path,dtype=torch.float32,size=data_shape[0]*data_shape[1]*data_shape[2])
    data_max=data.max()
    data_min=data.min()
    abs_eb=rel_eb*(data_max-data_min)
    command=f"{zfp_path} -s -i {data_path} -z {data_path}_{rel_eb_str}.zfp -o {data_path}_{rel_eb_str}.zfp.bin "
    command+=f"-f -3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -a {abs_eb}"
    process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output_lines=[]
    for line in iter(process.stdout.readline,""):
        print(line,end="",flush=True)
        output_lines.append(line)
    output=("".join(output_lines)).strip()
    cr=float(output.split(" ")[-6].split("=")[-1])
    psnr=float(output.split(" ")[-1].split("=")[-1])
    ssim=0
    if calculate_ssim:
        output_lines=[]
        command=f"{calculateSSIM_path} -f {data_path} {data_path}_{rel_eb_str}.zfp.bin {data_shape[2]} {data_shape[1]} {data_shape[0]}"
        process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for line in iter(process.stdout.readline,""):
            print(line,end="",flush=True)
            output_lines.append(line)
        output=("".join(output_lines)).strip()
        ssim=float(output.split("\n")[-1].split(" ")[-1])
    return cr,psnr,ssim
import subprocess,os
from typing import List
import numpy as np
from py_code.print_and_return_stdout import print_and_return_stdout

def call_qoz2_compress(qoz2_path:str,calculateSSIM_path:str,data_path:str,data_type:str,data_shape:List[int],rel_eb_str:str,whether_calculate_ssim:bool=False):
    if data_type not in ["f32"]:
        temp_data_path=data_path+"_temp"
        if data_type=="ui16":
            data=np.fromfile(data_path,dtype=np.uint16)
        data=data.astype(np.float32)
        data.tofile(temp_data_path)
        ret=call_qoz2_compress(qoz2_path,calculateSSIM_path,temp_data_path,"f32",data_shape,rel_eb_str,whether_calculate_ssim)
        os.remove(temp_data_path)
        if os.path.exists(f"{temp_data_path}_{rel_eb_str}.qoz2"):
            os.rename(f"{temp_data_path}_{rel_eb_str}.qoz2",f"{data_path}_{rel_eb_str}.qoz2")
        else:
            print("Warning: Cannot find the compressed file after changing the data type!")
        if os.path.exists(f"{temp_data_path}_{rel_eb_str}.qoz2.bin"):
            data=np.fromfile(f"{temp_data_path}_{rel_eb_str}.qoz2.bin",dtype=np.float32)
            if data_type=="ui16":
                data=data.astype(np.uint16)
            data.tofile(f"{data_path}_{rel_eb_str}.qoz2.bin")
            os.remove(f"{temp_data_path}_{rel_eb_str}.qoz2.bin")
        else:
            print("Warning: Cannot find the decompressed file after changing the data type!")
        cr,psnr,ssim=ret
        if data_type=="ui16":
            cr=cr/2
        return cr,psnr,ssim
    command=f"{qoz2_path} -i '{data_path}' -z '{data_path}_{rel_eb_str}.qoz2' -o '{data_path}_{rel_eb_str}.qoz2.bin' "
    command+=f"-f -M REL {rel_eb_str} -q 4 "
    command+=f"-{len(data_shape)} "
    for dim in reversed(data_shape):
        command+=f"{dim} "
    command+=f"-a "
    output=print_and_return_stdout(command)
    cr=float(output.split("\n")[-3].split(" ")[-1])
    psnr=float(output.split("\n")[-6].split(",")[0].split(" ")[-1])
    ssim=0
    if whether_calculate_ssim:
        output_lines=[]
        command=f"{calculateSSIM_path} -f '{data_path}' '{data_path}_{rel_eb_str}.qoz2.bin' "
        for dim in reversed(data_shape):
            command+=f"{dim} "
        output=print_and_return_stdout(command)
        ssim=float(output.split("\n")[-1].split(" ")[-1])
    return cr,psnr,ssim
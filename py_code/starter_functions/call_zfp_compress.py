import subprocess,os
import numpy as np
from typing import List
from py_code.print_and_return_stdout import print_and_return_stdout

def call_zfp_compress(zfp_path:str,calculateSSIM_path:str,data_path:str,data_type:str,data_shape:List[int],rel_eb_str:str,whether_calculate_ssim:bool=False):
    if data_type not in ["f32"]:
        temp_data_path=data_path+"_temp"
        if data_type=="ui16":
            data=np.fromfile(data_path,dtype=np.uint16)
        data=data.astype(np.float32)
        data.tofile(temp_data_path)
        ret=call_zfp_compress(zfp_path,calculateSSIM_path,temp_data_path,"f32",data_shape,rel_eb_str,whether_calculate_ssim)
        os.remove(temp_data_path)
        if os.path.exists(f"{temp_data_path}_{rel_eb_str}.zfp"):
            os.rename(f"{temp_data_path}_{rel_eb_str}.zfp",f"{data_path}_{rel_eb_str}.zfp")
        else:
            print("Warning: Cannot find the compressed file after changing the data type!")
        if os.path.exists(f"{temp_data_path}_{rel_eb_str}.zfp.bin"):
            data=np.fromfile(f"{temp_data_path}_{rel_eb_str}.zfp.bin",dtype=np.float32)
            if data_type=="ui16":
                data=data.astype(np.uint16)
            data.tofile(f"{data_path}_{rel_eb_str}.zfp.bin")
            os.remove(f"{temp_data_path}_{rel_eb_str}.zfp.bin")
        else:
            print("Warning: Cannot find the decompressed file after changing the data type!")
        cr,psnr,ssim=ret
        if data_type=="ui16":
            cr=cr/2
        return cr,psnr,ssim
    data=np.fromfile(data_path,dtype=np.float32)
    data_max=data.max()
    data_min=data.min()
    abs_eb=float(rel_eb_str)*(data_max-data_min)
    command=f"{zfp_path} -s -i {data_path} -z {data_path}_{rel_eb_str}.zfp -o {data_path}_{rel_eb_str}.zfp.bin "
    command+=f"-f -3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -a {abs_eb}"
    output=print_and_return_stdout(command)
    cr=float(output.split(" ")[-6].split("=")[-1])
    psnr=float(output.split(" ")[-1].split("=")[-1])
    ssim=0
    if whether_calculate_ssim:
        output_lines=[]
        command=f"{calculateSSIM_path} -f '{data_path}' '{data_path}_{rel_eb_str}.qoz2.bin' "
        for dim in reversed(data_shape):
            command+=f"{dim} "
        output=print_and_return_stdout(command)
        ssim=float(output.split("\n")[-1].split(" ")[-1])
    return cr,psnr,ssim
import subprocess,os
import numpy as np
from typing import List
from py_code.print_and_return_stdout import print_and_return_stdout

def call_cuszp_compress(cuszp_path:str,calculateSSIM_path:str,data_path:str,data_type:str,data_shape:List[int],rel_eb_str:str,whether_calculate_ssim:bool=False):
    if data_type not in ["f32"]:
        temp_data_path=data_path+"_temp"
        if data_type=="ui16":
            data=np.fromfile(data_path,dtype=np.uint16)
        data=data.astype(np.float32)
        data.tofile(temp_data_path)
        ret=call_cuszp_compress(cuszp_path,calculateSSIM_path,temp_data_path,"f32",data_shape,rel_eb_str,whether_calculate_ssim)
        os.remove(temp_data_path)
        if os.path.exists(f"{temp_data_path}_{rel_eb_str}.cuszp"):
            os.rename(f"{temp_data_path}_{rel_eb_str}.cuszp",f"{data_path}_{rel_eb_str}.cuszp")
        else:
            print("Warning: Cannot find the compressed file after changing the data type!")
        if os.path.exists(f"{temp_data_path}_{rel_eb_str}.cuszp.bin"):
            data=np.fromfile(f"{temp_data_path}_{rel_eb_str}.cuszp.bin",dtype=np.float32)
            if data_type=="ui16":
                data=data.astype(np.uint16)
            data.tofile(f"{data_path}_{rel_eb_str}.cuszp.bin")
            os.remove(f"{temp_data_path}_{rel_eb_str}.cuszp.bin")
        else:
            print("Warning: Cannot find the decompressed file after changing the data type!")
        cr,psnr,ssim=ret
        if data_type=="ui16":
            cr=cr/2
        return cr,psnr,ssim
    command=f"{cuszp_path} -i {data_path} -t {data_type} -m plain -eb rel {rel_eb_str} -x {data_path}_{rel_eb_str}.cuszp -o {data_path}_{rel_eb_str}.cuszp.bin "
    output=print_and_return_stdout(command)
    cr=float(output.split("\n")[-3].split(" ")[-1])
    data=np.fromfile(data_path,dtype=np.float32)
    decompressed_data=np.fromfile(f"{data_path}_{rel_eb_str}.cuszp.bin",dtype=np.float32)
    mse=np.mean((data-decompressed_data)**2)
    psnr=10*np.log10(((data.max()-data.min())**2)/mse)
    ssim=0
    if whether_calculate_ssim:
        output_lines=[]
        command=f"{calculateSSIM_path} -f '{data_path}' '{data_path}_{rel_eb_str}.qoz2.bin' "
        for dim in reversed(data_shape):
            command+=f"{dim} "
        output=print_and_return_stdout(command)
        ssim=float(output.split("\n")[-1].split(" ")[-1])
    return cr,psnr,ssim
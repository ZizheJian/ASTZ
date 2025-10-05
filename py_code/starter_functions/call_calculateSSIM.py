import os
import numpy as np
from typing import List
from py_code.print_and_return_stdout import print_and_return_stdout

def call_calculateSSIM(data_path:str,decompressed_path:str,data_shape:List[int],data_type:str):
    if data_type not in ["f32"]:
        temp_data_path=data_path+"_temp"
        temp_decompressed_path=decompressed_path+"_temp"
        if data_type=="ui16":
            data=np.fromfile(data_path,dtype=np.uint16)
            decompressed_data=np.fromfile(decompressed_path,dtype=np.uint16)
        data=data.astype(np.float32)
        decompressed_data=decompressed_data.astype(np.float32)
        data.tofile(temp_data_path)
        decompressed_data.tofile(temp_decompressed_path)
        ssim=call_calculateSSIM(temp_data_path,temp_decompressed_path,data_shape,"f32")
        os.remove(temp_data_path)
        os.remove(temp_decompressed_path)
        return ssim
    try:
        from device_based_starter_settings import calculateSSIM_path
        command=f"{calculateSSIM_path} -f '{data_path}' '{decompressed_path}' "
        for dim in reversed(data_shape):
            command+=f"{dim} "
        print(command)
        output=print_and_return_stdout(command)
        ssim=float(output.split("\n")[-1].split(" ")[-1])
    except:
        ssim=0
    return ssim
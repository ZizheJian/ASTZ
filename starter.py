import os,itertools,csv
import numpy as np
from py_code.starter_functions.call_generate_stencil_list import call_generate_stencil_list
from py_code.starter_functions.call_py_compress import call_py_compress,call_py_decompress
from py_code.starter_functions.search_threshold import search_threshold
from py_code.starter_functions.call_sz3_compress import call_sz3_compress
from py_code.starter_functions.call_qoz2_compress import call_qoz2_compress
from py_code.starter_functions.call_zfp_compress import call_zfp_compress
from py_code.starter_functions.call_cuszp_compress import call_cuszp_compress
from py_code.starter_functions.call_search_threshold import call_search_threshold
from py_code.starter_functions.calculate_predictability import calculate_predictability
from py_code.starter_functions.add_csv_record import add_csv_record
from py_code.starter_functions.check_csv_record import check_csv_record

from device_based_starter_settings import data_path,data_shape,data_type,rel_eb_list
try:
    from device_based_starter_settings import whether_large_scale_testing
except ImportError:
    whether_large_scale_testing=0
try:
    from device_based_starter_settings import block_num
except ImportError:
    block_num=None
from device_based_starter_settings import sz3_path,qoz2_path,zfp_path,cuszp_path,calculateSSIM_path

########Settings about single test########
whether_generate_stencil_list_using_FHDE=0
whether_compress_using_FHDE=0
whether_decompress_using_FHDE=0

whether_compress_using_FHDE_gpu=0
whether_decompress_using_FHDE_gpu=0

whether_generate_stencil_list_using_HDE=0
whether_compress_using_HDE=0
whether_decompress_using_HDE=0

whether_generate_stencil_list_using_fixed_coefficient=0
whether_compress_using_fixed_coefficient=0
whether_decompress_using_fixed_coefficient=0

whether_enumerate_threshold=0
whether_compress_using_qoz2=0
whether_compress_using_sz3=0
whether_compress_using_zfp=0
whether_compress_using_cusz=0

########Some extra settings########
whether_calculate_ssim=0

########Analysis tools########
whether_calculate_predictability=0

FHDE_threshold=9

starter_file_path=os.path.abspath(__file__)
project_directory_path=os.path.dirname(starter_file_path)

if not whether_large_scale_testing:
    data_name=os.path.basename(data_path)
    rel_eb_str:str=f"{rel_eb_list[0]:.1e}"
    if whether_generate_stencil_list_using_FHDE:
        call_generate_stencil_list(project_directory_path,data_path,data_type,data_shape,rel_eb_str,"FHDE",FHDE_threshold)
    if whether_compress_using_FHDE:
        call_py_compress(project_directory_path,data_path,data_type,data_shape,rel_eb_str,"FHDE",FHDE_threshold)
    if whether_decompress_using_FHDE:
        call_py_decompress(project_directory_path,data_path,data_type,data_shape,rel_eb_str,"FHDE",FHDE_threshold,whether_calculate_ssim)
    if whether_compress_using_FHDE_gpu:
        call_py_compress(project_directory_path,data_path,data_type,data_shape,rel_eb_str,"FHDE_gpu",FHDE_threshold)
    if whether_decompress_using_FHDE_gpu:
        call_py_decompress(project_directory_path,data_path,data_type,data_shape,rel_eb_str,"FHDE_gpu",FHDE_threshold,whether_calculate_ssim)
    if whether_generate_stencil_list_using_HDE:
        call_generate_stencil_list(project_directory_path,data_path,data_type,data_shape,rel_eb_str,"HDE")
    if whether_compress_using_HDE:
        call_py_compress(project_directory_path,data_path,data_type,data_shape,rel_eb_str,"HDE")
    if whether_decompress_using_HDE:
        call_py_decompress(project_directory_path,data_path,data_type,data_shape,rel_eb_str,"HDE",whether_calculate_ssim)
    if whether_generate_stencil_list_using_fixed_coefficient:
        call_generate_stencil_list(project_directory_path,data_path,data_type,data_shape,rel_eb_str,"FIX")
    if whether_compress_using_fixed_coefficient:
        call_py_compress(project_directory_path,data_path,data_type,data_shape,rel_eb_str,"FIX")
    if whether_decompress_using_fixed_coefficient:
        call_py_decompress(project_directory_path,data_path,data_type,data_shape,rel_eb_str,"FIX",whether_calculate_ssim)
    if whether_enumerate_threshold:
        call_search_threshold(project_directory_path,data_path,data_type,data_shape,rel_eb_list)
    # if SH_TH:
    #     search_threshold(project_directory_path,data_path,data_type,data_shape,rel_eb,"FHDE",FHDE_threshold)
    # elif method=="c_FHDE":
    #     code_generator(project_directory_path,data_path,data_type,rel_eb,"FHDE")
    #     call_c_compress(project_directory_path,data_path,rel_eb,FHDE_threshold)
    # elif method=="c_HDE":
    #     code_generator(project_directory_path,data_path,data_type,rel_eb,"HDE")
    #     call_c_compress(project_directory_path,data_path,rel_eb,0)
    if whether_compress_using_qoz2:
        cr,psnr,ssim=call_qoz2_compress(qoz2_path,calculateSSIM_path,data_path,data_type,data_shape,rel_eb_str,whether_calculate_ssim)
    if whether_compress_using_sz3:
        cr,psnr,ssim=call_sz3_compress(sz3_path,calculateSSIM_path,data_path,data_type,data_shape,rel_eb_str,whether_calculate_ssim)
    if whether_compress_using_zfp:
        cr,psnr,ssim=call_zfp_compress(zfp_path,calculateSSIM_path,data_path,data_type,data_shape,rel_eb_str,whether_calculate_ssim)
    if whether_calculate_predictability:
        calculate_predictability(data_path,data_type,data_shape)
else:
    original_file_path_list=[]
    if block_num is None:
        original_file_path_list.append(data_path)
        block_shape=data_shape.copy()
    else:
        for i in itertools.product(range(block_num),repeat=len(data_shape)):
            file_name=os.path.join(os.path.dirname(data_path),"blocks",f"{os.path.basename(data_path)}_{''.join([str(ii) for ii in i])}.bin")
            if os.path.exists(file_name):
                original_file_path_list.append(file_name)
            else:
                raise FileNotFoundError(f"{file_name} not found!")
        block_shape=[(data_shape[i]+block_num-1)//block_num for i in range(len(data_shape))]
    csv_path=os.path.join(project_directory_path,"large_scale_record",f"{os.path.basename(data_path)}.csv")
    if not os.path.exists(csv_path):
        with open(csv_path,"w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=["rel_eb","ASTZ_CR","ASTZ_PSNR","HPEZ_CR","HPEZ_PSNR","SZ3_CR","SZ3_PSNR","ZFP_CR","ZFP_PSNR","cuSZp_CR","cuSZp_PSNR"])
            writer.writeheader()
    global_data_min=float('inf')
    global_data_max=-float('inf')
    data_min_list=[]
    data_max_list=[]
    ######## Get global min and max ########
    for original_file_path in original_file_path_list:
        if data_type=="f32":
            data=np.fromfile(original_file_path,dtype=np.float32)
        elif data_type=="ui16":
            data=np.fromfile(original_file_path,dtype=np.uint16)
        data_min_list.append(data.min())
        data_max_list.append(data.max())
        global_data_max=max(data_min_list[-1],global_data_max)
        global_data_min=min(data_max_list[-1],global_data_min)
    for rel_eb in rel_eb_list:
        rel_eb_str=f"{rel_eb:.1e}"
        ######## ASTZ ########
        if check_csv_record(csv_path,rel_eb_str,"ASTZ"):
            print(f"Skip {rel_eb_str} ASTZ")
        else:
            if block_num is None:
                middle_file_path=original_file_path_list[0]
            else:
                middle_i=(block_num-1)//2
                middle_file_path=os.path.join(os.path.dirname(data_path),"blocks",f"{os.path.basename(data_path)}_{''.join([str(middle_i) for _ in range(len(data_shape))])}.bin")
            stencil_path=call_generate_stencil_list(project_directory_path,middle_file_path,data_type,block_shape,rel_eb_str,"FHDE",FHDE_threshold)
            average_mse=0
            total_compressed_file_size=0
            for original_file_id,original_file_path in enumerate(original_file_path_list):
                if len(data_shape)==3:
                    cr,psnr=call_py_compress(project_directory_path,original_file_path,data_type,block_shape,rel_eb_str,"FHDE",FHDE_threshold,stencil_path)
                else:
                    cr,psnr=call_py_compress(project_directory_path,original_file_path,data_type,block_shape,rel_eb_str,"FHDE_gpu",FHDE_threshold,stencil_path)
                data_max=data_max_list[original_file_id]
                data_min=data_min_list[original_file_id]
                mse=((data_max-data_min)**2)*(10**(-psnr/10))
                average_mse+=mse
                total_compressed_file_size+=1/cr
            average_mse/=len(original_file_path_list)
            average_psnr=10*np.log10(((global_data_max-global_data_min)**2)/average_mse)
            total_cr=len(original_file_path_list)/total_compressed_file_size
            add_csv_record(csv_path,rel_eb_str,"ASTZ",total_cr,average_psnr)
        ######## HPEZ ########
        if check_csv_record(csv_path,rel_eb_str,"HPEZ"):
            print(f"Skip {rel_eb_str} HPEZ")
        else:
            average_mse=0
            total_compressed_file_size=0
            for original_file_id,original_file_path in enumerate(original_file_path_list):
                cr,psnr,_=call_qoz2_compress(qoz2_path,calculateSSIM_path,original_file_path,data_type,block_shape,rel_eb_str,False)
                data_max=data_max_list[original_file_id]
                data_min=data_min_list[original_file_id]
                mse=((data_max-data_min)**2)*(10**(-psnr/10))
                average_mse+=mse
                total_compressed_file_size+=1/cr
                os.remove(f"{original_file_path}_{rel_eb_str}.qoz2.bin")
            average_mse/=len(original_file_path_list)
            average_psnr=10*np.log10(((global_data_max-global_data_min)**2)/average_mse)
            total_cr=len(original_file_path_list)/total_compressed_file_size
            add_csv_record(csv_path,rel_eb_str,"HPEZ",total_cr,average_psnr)
        ######## ZFP ########
        if check_csv_record(csv_path,rel_eb_str,"ZFP"):
            print(f"Skip {rel_eb_str} ZFP")
        else:
            average_mse=0
            total_compressed_file_size=0
            for original_file_id,original_file_path in enumerate(original_file_path_list):
                cr,psnr,_=call_zfp_compress(zfp_path,calculateSSIM_path,original_file_path,data_type,block_shape,rel_eb_str,False)
                data_max=data_max_list[original_file_id]
                data_min=data_min_list[original_file_id]
                mse=((data_max-data_min)**2)*(10**(-psnr/10))
                average_mse+=mse
                total_compressed_file_size+=1/cr
                os.remove(f"{original_file_path}_{rel_eb_str}.zfp.bin")
            average_mse/=len(original_file_path_list)
            average_psnr=10*np.log10(((global_data_max-global_data_min)**2)/average_mse)
            total_cr=len(original_file_path_list)/total_compressed_file_size
            add_csv_record(csv_path,rel_eb_str,"ZFP",total_cr,average_psnr)
        ######## cuSZp ########
        if check_csv_record(csv_path,rel_eb_str,"cuSZp"):
            print(f"Skip {rel_eb_str} cuSZp")
        else:
            average_mse=0
            total_compressed_file_size=0
            for original_file_id,original_file_path in enumerate(original_file_path_list):
                cr,psnr,_=call_cuszp_compress(cuszp_path,calculateSSIM_path,original_file_path,data_type,block_shape,rel_eb_str,False)
                data_max=data_max_list[original_file_id]
                data_min=data_min_list[original_file_id]
                mse=((data_max-data_min)**2)*(10**(-psnr/10))
                average_mse+=mse
                total_compressed_file_size+=1/cr
                os.remove(f"{original_file_path}_{rel_eb_str}.cuszp.bin")
            average_mse/=len(original_file_path_list)
            average_psnr=10*np.log10(((global_data_max-global_data_min)**2)/average_mse)
            total_cr=len(original_file_path_list)/total_compressed_file_size
            add_csv_record(csv_path,rel_eb_str,"cuSZp",total_cr,average_psnr)
import os
from py_code.starter_functions.call_generate_stencil_list import call_generate_stencil_list
from py_code.starter_functions.call_py_compress import call_py_compress,call_py_decompress
from py_code.starter_functions.search_threshold import search_threshold
from py_code.starter_functions.call_c_compress import call_c_compress
from py_code.starter_functions.call_sz3_compress import call_sz3_compress
from py_code.starter_functions.call_qoz2_compress import call_qoz2_compress
from py_code.starter_functions.call_zfp_compress import call_zfp_compress
from py_code.starter_functions.call_search_threshold import call_search_threshold

from device_based_starter_settings import data_path,data_shape,data_type,rel_eb_list,sz3_path,qoz_path,zfp_path,calculateSSIM_path

########Settings about large scale testing########
whether_large_scale_testing=0

########Settings about single test########
whether_generate_stencil_list_using_FHDE=0
whether_compress_using_FHDE=1
whether_decompress_using_FHDE=1

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

FHDE_threshold=9

data_name=os.path.basename(data_path)
starter_file_path=os.path.abspath(__file__)
project_directory_path=os.path.dirname(starter_file_path)
rel_eb_str:str=f"{rel_eb_list[0]:.0e}"

if not whether_large_scale_testing:
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
        cr,psnr,ssim=call_qoz2_compress(qoz_path,calculateSSIM_path,data_path,data_type,data_shape,rel_eb_str,whether_calculate_ssim)
    if whether_compress_using_sz3:
        cr,psnr,ssim=call_sz3_compress(sz3_path,calculateSSIM_path,data_path,data_type,data_shape,rel_eb_str,whether_calculate_ssim)
    if whether_compress_using_zfp:
        cr,psnr,ssim=call_zfp_compress(zfp_path,calculateSSIM_path,data_path,data_type,data_shape,rel_eb_str,whether_calculate_ssim)
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
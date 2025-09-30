from typing import List
from py_code.starter_functions.call_generate_stencil_list import call_generate_stencil_list
from py_code.starter_functions.call_py_compress import call_py_compress

def call_search_threshold(project_directory_path:str,data_path:str,data_type:str,data_shape:list[int],rel_eb_list:List[float]):
    for rel_eb in rel_eb_list:
        rel_eb_str=f"{rel_eb:.0e}"
        for threshold in range(4,5):
            call_generate_stencil_list(project_directory_path,data_path,data_type,data_shape,rel_eb_str,"FHDE",threshold)
            cr,psnr=call_py_compress(project_directory_path,data_path,data_type,data_shape,rel_eb_str,"FHDE",threshold)
            with open("search_threshold_log.txt","a") as log_file:
                log_file.write(f"{32/cr} {psnr} ")
        with open("search_threshold_log.txt","a") as log_file:
            log_file.write("\n")
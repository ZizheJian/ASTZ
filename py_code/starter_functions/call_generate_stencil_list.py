import os
from typing import List
from py_code.print_and_return_stdout import print_and_return_stdout

def call_generate_stencil_list(project_directory_path:str,data_path:str,data_type:str,data_shape:List[int],rel_eb_str:str,method:str,FHDE_threshold:int=0):
    data_name=os.path.basename(data_path)
    os.makedirs(os.path.join(project_directory_path,"stencil_list",rel_eb_str),exist_ok=True)
    stencil_path=os.path.join(project_directory_path,"stencil_list",rel_eb_str,data_name+".txt")
    command=f"python3 -u {os.path.join(project_directory_path,'py_code','generate_stencil_list.py')} "
    command+=f"-{data_type} -i '{data_path}' -c '{stencil_path}' -E REL {rel_eb_str} "
    command+=f"-{len(data_shape)} "
    for dim in data_shape:
        command+=f"{dim} "
    command+=f"-M {method} {FHDE_threshold} "
    print(f"command= {command}")
    print_and_return_stdout(command)
import os,subprocess
from typing import List

def call_generate_stencil_list(project_directory_path:str,data_path:str,data_type:str,data_shape:List[int],rel_eb:float,method:str,FHDE_threshold:int):
    data_name:str=os.path.basename(data_path)
    rel_eb_str:str=f"{rel_eb:.0e}"
    os.makedirs(os.path.join(project_directory_path,"stencil_list",rel_eb_str),exist_ok=True)
    stencil_path=os.path.join(project_directory_path,"stencil_list",rel_eb_str,data_name+".txt")
    command=f"python3 {os.path.join(project_directory_path,'py_code','generate_stencil_list.py')} "
    command+=f"-{data_type} -i {data_path} -c {stencil_path} -E REL {rel_eb_str} -3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -M {method} {FHDE_threshold} "
    print(command)
    subprocess.run(command,shell=True,encoding="utf-8")
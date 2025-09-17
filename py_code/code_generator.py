import os

def code_generator(project_directory_path:str,data_path:str,data_type:str,rel_eb:str,method:str):
    data_name:str=os.path.basename(data_path)
    rel_eb_str:str=f"{rel_eb:.0e}"
    stencil_path=os.path.join(project_directory_path,"stencil_list",rel_eb_str,data_name+".txt")
    code_path=os.path.join(project_directory_path,"c_code_v2","compress.cpp")
    with open(code_path,"w") as f:
        pass

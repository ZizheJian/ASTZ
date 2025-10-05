import re,os
from py_code.starter_functions.call_generate_stencil_list import call_generate_stencil_list
from py_code.starter_functions.call_py_compress import call_py_compress
from py_code.starter_functions.call_qoz_compress import call_qoz2_compress

embedding_dir_path="/work/hdd/bdgi/zjian1/Qwen2-VL-2B-Instruct-embeddings"
rel_eb_list=[3e-3]

starter_file_path=os.path.abspath(__file__)
project_directory_path=os.path.dirname(starter_file_path)
qoz_path="qoz"

file_name_pattern=re.compile(r"^16_11_(\d+)_1536_(\d{4})\.bin$")
file_name_dict={}
for file_name in os.listdir(embedding_dir_path):
    match=file_name_pattern.match(file_name)
    if match:
        key=int(match.group(1))
        if key not in file_name_dict:
            file_name_dict[key]=[]
        file_name_dict[key].append(file_name)
file_name_dict={key:file_name_dict[key] for key in sorted(file_name_dict.keys())}

for rel_eb in rel_eb_list:
    rel_eb_str=f"{rel_eb:.0e}"
    for key in [16]:
        file_name_dict[key].sort()
        file_num=len(file_name_dict[key])
        file_name_dict[key]=[file_name_dict[key][file_num//2]]
        for file_name in file_name_dict[key]:
            file_path=os.path.join(embedding_dir_path,file_name)
            stencil_path=f"{file_path}.stencil.txt"
            call_generate_stencil_list(project_directory_path,file_path,"f32",[16,11*key,1536],rel_eb_str,"FHDE",9,stencil_path=stencil_path)
            # cr,psnr=call_py_compress(project_directory_path,file_path,"f32",[16,11*key,1536],rel_eb_str,"FHDE",9,stencil_path=stencil_path)
            # with open("embedding_log.txt","a") as log_file:
            #     log_file.write(f"{32/cr} {psnr} ")
            # cr,psnr,_=call_qoz_compress(qoz_path,None,file_path,"f32",[16,11*key,1536],rel_eb_str)
            # with open("qoz_embedding_log.txt","a") as log_file:
            #     log_file.write(f"{32/cr} {psnr} ")
    # with open("embedding_log.txt","a") as log_file:
    #     log_file.write("\n")
            
import re,os
from py_code.starter_functions.call_generate_stencil_list import call_generate_stencil_list
from py_code.starter_functions.call_py_compress import call_py_compress
from py_code.starter_functions.call_qoz2_compress import call_qoz2_compress

# embedding_dir_path="/work/nvme/bdgi/zjian1/Qwen2-VL-2B-Instruct-embeddings"
embedding_dir_path="/work/nvme/bdgi/zjian1/Qwen2.5-VL-3B-Instruct-embeddings"
rel_eb_list=[6e-2,4.5e-2,3e-2,2.5e-2,2e-2,1.5e-2,1e-2,6e-3]

starter_file_path=os.path.abspath(__file__)
project_directory_path=os.path.dirname(starter_file_path)

# file_name_pattern=re.compile(r"^16_11_(\d+)_1536_(\d{4})\.bin$")
file_name_pattern=re.compile(r"^16_(\d+)_(\d+)_2048_(\d{4})\.bin$")
file_name_dict={}
for file_name in os.listdir(embedding_dir_path):
    match=file_name_pattern.match(file_name)
    if match:
        # key=int(match.group(1))
        key=(int(match.group(1)),int(match.group(2)))
        if key not in file_name_dict:
            file_name_dict[key]=[]
        file_name_dict[key].append(file_name)
file_name_dict={key:file_name_dict[key] for key in sorted(file_name_dict.keys())}

for rel_eb in rel_eb_list:
    rel_eb_str=f"{rel_eb:.1e}"
    for key in file_name_dict.keys():
        file_name_dict[key].sort()
        file_num=len(file_name_dict[key])
        file_name_dict[key]=[file_name_dict[key][file_num//2]]
        for file_name in file_name_dict[key]:
            file_path=os.path.join(embedding_dir_path,file_name)
            if os.path.exists(os.path.join(project_directory_path,"stencil_list",rel_eb_str,file_name+".txt")):
                print(f"Stencil list for {file_name} with rel_eb={rel_eb_str} already exists, skip generating stencil list.")
                continue
            # call_generate_stencil_list(project_directory_path,file_path,"f32",[16,11,key,1536],rel_eb_str,"FHDE",9)
            call_generate_stencil_list(project_directory_path,file_path,"f32",[16,key[0],key[1],2048],rel_eb_str,"FHDE",9)
            
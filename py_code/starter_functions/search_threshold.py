import os,random
from py_code.starter_functions.call_generate_stencil_list import call_generate_stencil_list
from py_code.starter_functions.call_py_compress import call_py_compress

def search_threshold(project_directory_path:str,data_path:str,data_type:str,data_shape:list,rel_eb:float,method:str,FHDE_threshold:int):
    rel_eb_str=f"{rel_eb:.0e}"
    data_name=os.path.basename(data_path)
    while True:
        threshold_dict={}
        try:
            with open(f"threshold/{rel_eb_str}/{data_name}.txt","r") as f:
                for line in f.readlines():
                    splited_line=line.split(" ")
                    threshold_dict[int(splited_line[0])]=float(splited_line[1])
        except FileNotFoundError:
            os.makedirs(f"threshold/{rel_eb_str}",exist_ok=True)
            with open(f"threshold/{rel_eb_str}/{data_name}.txt","w") as f:
                pass
        if len(threshold_dict)==0:
            print("threshold record is empty")
            th=FHDE_threshold
        else:
            th_found=False
            for index in range(len(threshold_dict)):
                th=list(threshold_dict.keys())[index]
                print(f"index={index},th={th}")
                possible_directions=[-1,1]
                possible_directions=[i for i in possible_directions if 0<th+i<10 and th+i not in threshold_dict.keys()]
                if len(possible_directions)==0:
                    continue
                else:
                    th+=random.choice(possible_directions)
                    th_found=True
                    break
            if not th_found:
                print("No more threshold to search")
                break
        print(f"current th={th}")
        call_generate_stencil_list(project_directory_path,data_path,data_type,data_shape,rel_eb,method,th)
        cr,psnr,ssim=call_py_compress(project_directory_path,data_path,data_type,data_shape,rel_eb,method,th)
        threshold_dict[th]=cr
        sorted_threshold_dict=sorted(threshold_dict.items(),key=lambda x:x[1],reverse=True)
        with open(f"threshold/{rel_eb_str}/{data_name}.txt","w") as f:
            for key,value in sorted_threshold_dict:
                f.write(f"{key} {value}\n")
        print(f"th={th},cr={cr}")     
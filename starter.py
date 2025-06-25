import subprocess,os,random,torch
from typing import List
from py_code.starter_functions.call_generate_stencil_list import call_generate_stencil_list
from py_code.starter_functions.call_py_compress import call_py_compress,call_py_decompress
from py_code.starter_functions.call_sz3_compress import call_sz3_compress

def call_c_compress(project_directory_path:str,data_path:str,data_shape:List[int],rel_eb:float,method:str,FHDE_threshold:int):
    os.chdir("c_code")
    os.makedirs("build",exist_ok=True)
    os.chdir("build")
    build_path=os.getcwd()
    # subprocess.run(f"cmake -DCMAKE_INSTALL_PREFIX:PATH={os.path.join(project_directory_path,'c_code','install')} ..",cwd=build_path,shell=True,encoding="utf-8")
    subprocess.run("make",cwd=build_path,shell=True,encoding="utf-8")
    print(build_path)
    os.chdir(project_directory_path)
    command=f"{build_path +'/fhde'} -f -i {data_path} -o {data_path+'.fhde'} "
    command+=f"-3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -M REL {rel_eb} -a -c {'./topology_list/Uf48.bin.dat.txt'}"
    print(command)
    process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output_lines=[]
    for line in iter(process.stdout.readline,""):
        print(line,end="",flush=True)
        output_lines.append(line)
    output=("".join(output_lines)).strip()
    return output

def call_hpez_compress(bin_path:str,calculateSSIM_path:str,data_path:str,data_shape:List[int],rel_eb:float,calculate_ssim:bool=False):
    command=f"{bin_path} -i {data_path} -z {data_path}_{rel_eb}.hpez -o {data_path}_{rel_eb}.hpez.bin -f -M REL {rel_eb} -q 4 -3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -a"
    process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output_lines=[]
    for line in iter(process.stdout.readline,""):
        print(line,end="",flush=True)
        output_lines.append(line)
    output=("".join(output_lines)).strip()
    cr=float(output.split("\n")[-3].split(" ")[-1])
    psnr=float(output.split("\n")[-6].split(",")[-2].split(" ")[-1])
    ssim=0
    if calculate_ssim:
        output_lines=[]
        command=f"{calculateSSIM_path} -f {data_path} {data_path}_{rel_eb}.hpez.bin {data_shape[2]} {data_shape[1]} {data_shape[0]}"
        process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for line in iter(process.stdout.readline,""):
            print(line,end="",flush=True)
            output_lines.append(line)
        output=("".join(output_lines)).strip()
        ssim=float(output.split("\n")[-1].split(" ")[-1])
    return cr,psnr,ssim

def call_zfp_compress(bin_path:str,calculateSSIM_path:str,data_path:str,data_shape:List[int],rel_eb:float,calculate_ssim:bool=False):
    data=torch.from_file(data_path,dtype=torch.float32,size=data_shape[0]*data_shape[1]*data_shape[2])
    data_max=data.max()
    data_min=data.min()
    abs_eb=rel_eb*(data_max-data_min)
    command=f"{bin_path} -s -i {data_path} -z {data_path}_{rel_eb}.zfp -o {data_path}_{rel_eb}.zfp.bin -f -3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -a {abs_eb}"
    process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output_lines=[]
    for line in iter(process.stdout.readline,""):
        print(line,end="",flush=True)
        output_lines.append(line)
    output=("".join(output_lines)).strip()
    cr=float(output.split(" ")[-6].split("=")[-1])
    psnr=float(output.split(" ")[-1].split("=")[-1])
    ssim=0
    if calculate_ssim:
        output_lines=[]
        command=f"{calculateSSIM_path} -f {data_path} {data_path}_{rel_eb}.zfp.bin {data_shape[2]} {data_shape[1]} {data_shape[0]}"
        process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for line in iter(process.stdout.readline,""):
            print(line,end="",flush=True)
            output_lines.append(line)
        output=("".join(output_lines)).strip()
        ssim=float(output.split("\n")[-1].split(" ")[-1])
    return cr,psnr,ssim

data_path:str="/anvil/projects/x-cis240192/x-zjian1-in-cis240192/APS_DYS/xpcs_datasets/APSU_TestData_004/block/APSU_TestData_004_float_block.bin_000"
data_type:str="uint16"
data_shape:List[int]=[256,390,454]
rel_eb_list=[1e-1,1e-2,1e-3,1e-4]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/APS_DYS/xpcs_datasets/APSU_TestData_004/APSU_TestData_004.bin"
# data_shape:List[int]=[1024,1558,1813]
# rel_eb_list=[1e-1,1e-2,1e-3,1e-4]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/APS_DYS/xpcs_new_from_miaoqi/D0131_US-Cup2_a0010_f005000_r00001_cut.bin"
# data_shape:List[int]=[625,270,258]
# rel_eb_list=[3e-1,1e-1,3e-2,1e-2]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/EXAFEL/SDRBENCH-EXAFEL-data-130x1480x1552_cut.f32"
# data_shape:List[int]=[13,1480,1552]
# rel_eb_list=[1e-1,1e-2,1e-3,1e-4]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/EXAFEL/SDRBENCH-EXAFEL-data-130x1480x1552.f32"
# data_shape:List[int]=[130,1480,1552]
# rel_eb_list=[1e-1,1e-2,1e-3,1e-4]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/APS_Kaz/xpcs-998x128x128.bin.f32"
# data_shape:List[int]=[998,128,128]
# rel_eb_list=[3e-1,1e-1,3e-2,1e-2]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/APS_DYS/xpcs_datasets/E017_CeramicGlass_L2Mq0_060C_att00_001/E017_CeramicGlass_L2Mq0_060C_att00_001_001.bin"
# data_shape:List[int]=[1024,1813,1558]
# rel_eb_list=[1e-1,1e-2,3e-3,1e-3,3e-4,1e-4]

# Here I have added the path to ~/.bashrc. If you haven't, change the path to the location of your installation.
sz3_path:str="sz3"
hpez_path:str="hpez"
zfp_path:str="zfp"
calculateSSIM_path:str="calculateSSIM"

#GSL_FHDE="generate stencil list using FHDE"
#GSL_HDE="generate stencil list using HDE"
#py_FHDE="python compress using FHDE"
#py_HDE="python compress using HDE"
#c_FHDE="c compress using FHDE"
#c_HDE="c compress using HDE"
#sz3="sz3 compress"
#hpez="HPEZ compress"
#zfp="ZFP compress"
method_list:List[str]=["GSL_FHDE","py_FHDE"]
rel_eb:float=1e-3
FHDE_threshold=4
search_threshold:bool=False
large_scale_testing:bool=False
calculate_ssim:bool=False

data_name=os.path.basename(data_path)
starter_file_path=os.path.abspath(__file__)
project_directory_path=os.path.dirname(starter_file_path)
rel_eb_float:str=f"{rel_eb:.0e}"

if not large_scale_testing:
    if not search_threshold:
        for method in method_list:
            if method=="GSL_FHDE":
                call_generate_stencil_list(project_directory_path,data_path,data_type,data_shape,rel_eb,"FHDE",FHDE_threshold)
            elif method=="py_FHDE":
                call_py_compress(project_directory_path,data_path,data_type,data_shape,rel_eb,"FHDE",FHDE_threshold,calculate_ssim)
                call_py_decompress()
                # call_c_compress(project_directory_path,data_path,data_shape,rel_eb,method,FHDE_threshold)
            elif method=="sz3":
                cr,psnr,ssim=call_sz3_compress(sz3_path,calculateSSIM_path,data_path,data_type,data_shape,rel_eb,calculate_ssim)
    else:
        th_preset=FHDE_threshold
        while True:
            threshold_dict={}
            try:
                with open(f"threshold/{rel_eb}/{data_name}.txt","r") as f:
                    for line in f.readlines():
                        splited_line=line.split(" ")
                        threshold_dict[int(splited_line[0])]=float(splited_line[1])
            except FileNotFoundError:
                os.makedirs(f"threshold/{rel_eb}",exist_ok=True)
                with open(f"threshold/{rel_eb}/{data_name}.txt","w") as f:
                    pass
            if len(threshold_dict)==0:
                print("threshold record is empty")
                th=th_preset
            else:
                for index in range(len(threshold_dict)):
                    th=list(threshold_dict.keys())[index]
                    print(f"index={index},th={th}")
                    found_unsearched=False
                    possible_directions=[-1,0,1]
                    possible_directions=[i for i in possible_directions if 0<th+i<10]
                    random.shuffle(possible_directions)
                    for d_th in possible_directions:
                        new_th=th+d_th
                        if new_th not in threshold_dict:
                            th=new_th
                            found_unsearched=True
                    if not found_unsearched:
                        continue
                    else:
                        break
            print(f"current th={th}")
            call_generate_stencil_list(project_directory_path,data_path,data_shape,rel_eb,method,th)
            cr,psnr,ssim=call_py_compress(project_directory_path,data_path,data_shape,rel_eb,method,th)
            threshold_dict[th]=cr
            sorted_threshold_dict=sorted(threshold_dict.items(),key=lambda x:x[1],reverse=True)
            with open(f"threshold/{rel_eb}/{data_name}.txt","w") as f:
                for key,value in sorted_threshold_dict:
                    f.write(f"{key} {value}\n")
            print(f"th={th},cr={cr}")     
else:
    for rel_eb in rel_eb_list:
        if not os.path.exists(f"large_scale_record/{data_name}.txt"):
            with open(f"large_scale_record/{data_name}.txt","w") as f:
                f.write("")
        ########ASTZ########
        call_generate_stencil_list(project_directory_path,data_path,data_shape,rel_eb,method,FHDE_threshold)
        cr,psnr,ssim=call_py_compress(project_directory_path,data_path,data_shape,rel_eb,method,FHDE_threshold,calculate_ssim)
        with open(f"large_scale_record/{data_name}.txt","a") as f:
            f.write(f"{cr} {32/cr} {psnr} {ssim} ")
        ########SZ3########
        cr,psnr,ssim=call_sz3_compress(sz3_path,calculateSSIM_path,data_path,data_shape,rel_eb,calculate_ssim)
        with open(f"large_scale_record/{data_name}.txt","a") as f:
            f.write(f"{cr} {32/cr} {psnr} {ssim} ")
        ########HPEZ########
        cr,psnr,ssim=call_hpez_compress(hpez_path,calculateSSIM_path,data_path,data_shape,rel_eb,calculate_ssim)
        with open(f"large_scale_record/{data_name}.txt","a") as f:
            f.write(f"{cr} {32/cr} {psnr} {ssim} ")
        ########ZFP########
        # cr,psnr,ssim=call_zfp_compress(zfp_path,calculateSSIM_path,data_path,data_shape,rel_eb,calculate_ssim)
        # with open(f"large_scale_record/{data_name}.txt","a") as f:
        #     f.write(f"{cr} {32/cr} {psnr} {ssim}\n")
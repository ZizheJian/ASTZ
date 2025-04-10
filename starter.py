import subprocess,os,random
from typing import List

def call_generate_stencil_list(project_directory_path:str,data_path:str,data_shape:List[int],rel_eb:float,method:str,FHDE_threshold:int):
    data_name=os.path.basename(data_path)
    stencil_path=os.path.join(project_directory_path,"stencil_list",data_name+".txt")
    command=f"python3 {os.path.join(project_directory_path,'py_code','generate_stencil_list.py')} "
    command+=f"-f -i {data_path} -c {stencil_path} -E REL {rel_eb} -3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -M {method} {FHDE_threshold} "
    print(command)
    subprocess.run(command,shell=True,encoding="utf-8")

def call_py_compress(project_directory_path:str,data_path:str,data_shape:List[int],rel_eb:float,method:str,FHDE_threshold:int):
    data_name=os.path.basename(data_path)
    stencil_path=os.path.join(project_directory_path,"stencil_list",data_name+".txt")
    command=f"python3 {os.path.join(project_directory_path,'py_code','compress.py')} "
    command+=f"-f -i {data_path} -z {data_path+'.fhde'} -o {data_path+'.fhde.bin'} -c {stencil_path} "
    command+=f"-E REL {rel_eb} -3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -M {method} {FHDE_threshold} "
    print(command)
    process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output_lines=[]
    for line in iter(process.stdout.readline,""):
        print(line,end="",flush=True)
        output_lines.append(line)
    output=("".join(output_lines)).strip()
    return output

def call_c_compress(project_directory_path:str,data_path:str,data_shape:List[int],rel_eb:float,method:str,FHDE_threshold:int):
    data_name=os.path.basename(data_path)
    os.chdir("c_code")
    os.makedirs("build",exist_ok=True)
    os.chdir("build")
    build_path=os.getcwd()
    subprocess.run(f"cmake -DCMAKE_INSTALL_PREFIX:PATH={os.path.join(project_directory_path,'c_code','install')} ..",cwd=build_path,shell=True,encoding="utf-8")
    subprocess.run("make",cwd=build_path,shell=True,encoding="utf-8")
    print(build_path)
    # subprocess.run("make install",cwd=build_path,shell=True,encoding="utf-8")
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

def call_sz3_compress(project_directory_path:str,data_path:str,data_shape:List[int],rel_eb:float):
    sz3_project_path="/home/x-zjian1/SZ3"
    os.chdir(os.path.join(sz3_project_path,"build"))
    # os.system(f"cmake -DCMAKE_INSTALL_PREFIX:PATH={os.path.join(sz3_project_path,'install')} ..")
    os.system("make")
    os.system("make install")
    command=f"sz3 -i {data_path} -z {data_path}.sz3 -o {data_path}.sz3.bin -f -M REL -R {rel_eb} -3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -a"
    process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output_lines=[]
    for line in iter(process.stdout.readline,""):
        print(line,end="",flush=True)
        output_lines.append(line)
    command=f"calculateSSIM -f {data_path} {data_path}.sz3.bin {data_shape[2]} {data_shape[1]} {data_shape[0]}"
    process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    for line in iter(process.stdout.readline,""):
        print(line,end="",flush=True)
        output_lines.append(line)
    output=("".join(output_lines)).strip()
    os.chdir(project_directory_path)
    return output

def call_hpez_compress(project_directory_path:str,data_path:str,data_shape:List[int],rel_eb:float):
    hpez_project_path="/home/x-zjian1/HPEZ"
    os.chdir(os.path.join(hpez_project_path,"build"))
    os.system("make")
    os.system("make install")
    command=f"hpez -i {data_path} -z {data_path}.hpez -o {data_path}.hpez.bin -f -M REL {rel_eb} -q 4 -3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -a"
    process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output_lines=[]
    for line in iter(process.stdout.readline,""):
        print(line,end="",flush=True)
        output_lines.append(line)
    command=f"calculateSSIM -f {data_path} {data_path}.hpez.bin {data_shape[2]} {data_shape[1]} {data_shape[0]}"
    process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    for line in iter(process.stdout.readline,""):
        print(line,end="",flush=True)
        output_lines.append(line)
    output=("".join(output_lines)).strip()
    os.chdir(project_directory_path)
    return output

# data_path:str="/anvil/projects/x-cis240192/x-zjian1/APS_DYS/xpcs_datasets/APSU_TestData_004/APSU_TestData_004_cut.bin"
# data_shape:List[int]=[614,312,363]
# rel_eb_list=[1e-1,3e-2,1e-2,3e-3,1e-3,3e-4,1e-4]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/APS_DYS/9-ID_CSSI_data/benchmarkdata/Avg_L0470_Double_exp_elong_siemens_1p00sampit_0p05inplane_patch1_of1_part0_001_cut.bin"
# data_shape:List[int]=[150,453,390]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/NYX/baryon_density_cut.f32"
# data_shape:List[str]=[256,256,256]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/NYX/baryon_density_log10_cut.f32"
# data_shape:List[str]=[256,256,256]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/EXAFEL/SDRBENCH-EXAFEL-data-13x1480x1552.f32"
# data_shape:List[int]=[13,1480,1552]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/APS_Kaz/xpcs-998x128x128.bin.f32"
# data_shape:List[int]=[998,128,128]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/ISABEL/P/Pf01.bin"
# data_shape:List[str]=[100,500,500]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/ISABEL/U/Uf48.bin"
# data_shape:List[str]=[100,500,500]

rel_eb:float=1e-3
doughnut:bool=False
method:str="FHDE"
method_average:str="FHDE"
method_residual:str="FHDE"
FHDE_threshold=4
FHDE_threshold_average=FHDE_threshold
FHDE_threshold_residual=FHDE_threshold
search_threshold:bool=False
large_scale_testing:bool=True

data_name=os.path.basename(data_path)
starter_file_path=os.path.abspath(__file__)
project_directory_path=os.path.dirname(starter_file_path)

if not large_scale_testing:
    if not search_threshold:
        if not doughnut:
            call_generate_stencil_list(project_directory_path,data_path,data_shape,rel_eb,method,FHDE_threshold)
            call_py_compress(project_directory_path,data_path,data_shape,rel_eb,method,FHDE_threshold)
            # call_c_compress(project_directory_path,data_path,data_shape,rel_eb,method,FHDE_threshold)
        else:
            raise NotImplementedError
    else:
        th_preset=FHDE_threshold
        while True:
            threshold_dict={}
            try:
                with open(f"threshold/{data_name}.txt","r") as f:
                    for line in f.readlines():
                        splited_line=line.split(" ")
                        threshold_dict[int(splited_line[0])]=float(splited_line[1])
            except FileNotFoundError:
                os.makedirs("threshold",exist_ok=True)
                with open(f"threshold/{data_name}.txt","w") as f:
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
                    possible_directions=[i for i in possible_directions if th+i>0]
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
            output=call_py_compress(project_directory_path,data_path,data_shape,rel_eb,method,th)
            cr=float(output.split("\n")[-5].split(" ")[-1])
            threshold_dict[th]=cr
            sorted_threshold_dict=sorted(threshold_dict.items(),key=lambda x:x[1],reverse=True)
            with open(f"threshold/{data_name}.txt","w") as f:
                for key,value in sorted_threshold_dict:
                    f.write(f"{key} {value}\n")
            print(f"th={th},cr={cr}")
else:
    for rel_eb in rel_eb_list:
        if not os.path.exists(f"large_scale_record/{data_name}.txt"):
            with open(f"large_scale_record/{data_name}.txt","w") as f:
                f.write("")
        call_generate_stencil_list(project_directory_path,data_path,data_shape,rel_eb,method,FHDE_threshold)
        output=call_py_compress(project_directory_path,data_path,data_shape,rel_eb,method,FHDE_threshold)
        cr=float(output.split("\n")[-5].split(" ")[-1])
        psnr=float(output.split("\n")[-2].split(" ")[-1])
        ssim=float(output.split("\n")[-1].split(" ")[-1])
        with open(f"large_scale_record/{data_name}.txt","a") as f:
            f.write(f"{cr} {32/cr} {psnr} {ssim} ")
        output=call_sz3_compress(project_directory_path,data_path,data_shape,rel_eb)
        cr=float(output.split("\n")[-7].split(" ")[-1])
        psnr=float(output.split("\n")[-10].split(",")[-2].split(" ")[-1])
        ssim=float(output.split("\n")[-1].split(" ")[-1])
        with open(f"large_scale_record/{data_name}.txt","a") as f:
            f.write(f"{cr} {32/cr} {psnr} {ssim} ")
        output=call_hpez_compress(project_directory_path,data_path,data_shape,rel_eb)
        cr=float(output.split("\n")[-7].split(" ")[-1])
        psnr=float(output.split("\n")[-10].split(",")[-2].split(" ")[-1])
        ssim=float(output.split("\n")[-1].split(" ")[-1])
        with open(f"large_scale_record/{data_name}.txt","a") as f:
            f.write(f"{cr} {32/cr} {psnr} {ssim}\n")
        

#APSU_TestData_004_cut
#eb=1e-2,   th=4,   fhde_cr=517.092041,     fhde_psnr=60.652073,    fhde_ssim=0.610035
#                   hpez_cr=185.404953,     hpez_psnr=56.925469,    hpez_ssim=0.561100
#                   sz3_cr=116.316650,      sz3_psnr=54.572205,     sz3_ssim=0.491469
#eb=1e-3,   th=2,   fhde_cr=81.075806,      fhde_psnr=72.019621,    fhde_ssim=0.83924
#                   hpez_cr=43.198803,      hpez_psnr=73.375284,    hpez_ssim=0.870122
#                   sz3_cr=30.231087,       sz3_psnr=70.153330,     sz3_ssim=0.793982
#eb=1e-4,   th=9,   fhde_cr=18.363937,      fhde_psnr=87.624322,    fhde_ssim=0.970660
#                   hpez_cr=17.857512,      hpez_psnr=91.002153,    hpez_ssim=0.989429
#                   sz3_cr=12.875036,       sz3_psnr=88.626429,     sz3_ssim=0.977186

#Avg_L0470_Double_exp_elong_siemens_1p00sampit_0p05inplane_patch1_of1_part0_001_cut
#eb=1e-2,   th=12,  fhde_cr=3838.148926,    fhde_psnr=65.117022,    fhde_ssim=0.030408
#                   hpez_cr=3168.116211,    hpez_psnr=65.506478,    hpez_ssim=0.059536
#                   sz3_cr=3674.118748,     sz3_psnr=63.993585,     sz3_ssim=0.019021
#eb=1e-3,   th=4,   fhde_cr=346.330261,     fhde_psnr=76.123161,    fhde_ssim=0.168114
#                   hpez_cr=315.788544,     hpez_psnr=76.335232,    hpez_ssim=0.212530
#                   sz3_cr=337.292725,      sz3_psnr=74.578649,     sz3_ssim=0.136094
#eb=1e-4,   th=,    fhde_cr=6.643421,       fhde_psnr=85.392112,    fhde_ssim=0.998004
#                   hpez_cr=38.454533,      hpez_psnr=88.775551,    hpez_ssim=0.585355
#                   sz3_cr=39.585377,       sz3_psnr=87.889948,     sz3_ssim=0.518753

#SDRBENCH-EXAFEL-data-13x1480x1552:
#eb=1e-2,   th=2,   fhde_cr=69.579140,      fhde_psnr=47.251118,    fhde_ssim=0.584669
#                   hpez_cr=48.529064,      hpez_psnr=46.992156,    hpez_ssim=0.662971   
#                   sz3_cr=47.341587,       sz3_psnr=46.356503,     sz3_ssim=0.598296
#eb=1e-3,   th=7,   fhde_cr=9.412062,       fhde_psnr=65.133070,    fhde_ssim=0.993043
#                   hpez_cr=9.160643,       hpez_psnr=64.814133,    hpez_ssim=0.992390
#                   sz3_cr=8.815522,        sz3_psnr=64.872521,     sz3_ssim=0.992496
#eb=1e-4,   th=9,   fhde_cr=4.694738,       fhde_psnr=85.122358,    fhde_ssim=0.999927
#                   hpez_cr=4.676123,       hpez_psnr=84.771873,    hpez_ssim=0.999921
#                   sz3_cr=4.617146,        sz3_psnr=84.834829,     sz3_ssim=0.999922

#xpcs-998x128x128.bin.f32
#eb=1e-2,   th=7,   fhde_cr=34.539262,      fhde_psnr=50.120942,    fhde_ssim=0.758722
#                   hpez_cr=28.890583,      hpez_psnr=49.046694,    hpez_ssim=0.698190
#                   sz3_cr=28.891068,       sz3_psnr=48.068715,     sz3_ssim=0.611233
#eb=1e-3,   th=5,   fhde_cr=13.284021,      fhde_psnr=65.764751,    fhde_ssim=0.932677
#                   hpez_cr=15.439531,      hpez_psnr=72.440304,    hpez_ssim=0.989053
#                   sz3_cr=19.258545,       sz3_psnr=76.038827,     sz3_ssim=0.996618
#eb=1e-4,   th=3,   fhde_cr=6.745661,       fhde_psnr=84.837783,    fhde_ssim=0.998096
#                   hpez_cr=12.077442,      hpez_psnr=89.213993,    hpez_ssim=0.999941
#                   sz3_cr=17.341478,       sz3_psnr=88.012202,     sz3_ssim=0.999680

#baryon_density_log10_cut.f32
#eb=1e-2,   th=2,   fhde_cr=112.175850,     fhde_psnr=48.594986,    fhde_ssim=0.960784
#                   hpez_cr=127.539017,     hpez_psnr=51.311496,    hpez_ssim=0.983513
#                   sz3_cr=92.054794,       sz3_psnr=47.666508,     sz3_ssim=0.953954

#baryon_density_cut.f32
#eb=1e-2,   th=6,   fhde_cr=59972.175781,   fhde_psnr=84.643368,    fhde_ssim=0.067792
#                   hpez_cr=38994.109375,   hpez_psnr=83.019702,    hpez_ssim=0.064159
#                   sz3_cr=47969.167969,    sz3_psnr=81.645181,     sz3_ssim=0.001000
#eb=1e-3,   th=3,   fhde_cr=10615.131836,   fhde_psnr=93.000053,    fhde_ssim=0.079688
#                   hpez_cr=7777.130859,    hpez_psnr=91.407724,    hpez_ssim=0.066296
#                   sz3_cr=9101.975586,     sz3_psnr=90.195876,     sz3_ssim=0.007802
#eb=1e-4,   th=2,   fhde_cr=1714.935669,    fhde_psnr=101.508924,    fhde_ssim=0.147669
#                   hpez_cr=1313.593506,    hpez_psnr=101.910496,    hpez_ssim=0.190152
#                   sz3_cr=1486.024414,     sz3_psnr=98.488485,     sz3_ssim=0.079761

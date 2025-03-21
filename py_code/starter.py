#测试不同model_block_step、pivot_ratio的影响

import subprocess,os,random,copy
from itertools import product
from typing import List

data_path:str="/anvil/projects/x-cis240192/x-zjian1/APS_DYS/xpcs_datasets/APSU_TestData_004/APSU_TestData_004_cut.bin"
data_shape:List[int]=[614,312,363]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/APS_DYS/9-ID_CSSI_data/benchmarkdata/Avg_L0470_Double_exp_elong_siemens_1p00sampit_0p05inplane_patch1_of1_part0_001_cut.bin"
# data_shape:List[int]=[150,453,390]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/EXAFEL/SDRBENCH-EXAFEL-data-13x1480x1552.f32"
# data_shape:List[int]=[13,1480,1552]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/APS_Kaz/xpcs-998x128x128.bin.f32"
# data_shape:List[int]=[998,128,128]
# data_path:str="/anvil/projects/x-cis240192/x-zjian1/NYX/baryon_density_log10_cut.f32"
# data_shape:List[str]=[256,256,256]

rel_eb:float=1e-4
doughnut:bool=False
method:str="FHDE"
method_average:str="FHDE"
method_residual:str="FHDE"
FHDE_threshold=9
FHDE_threshold_average=FHDE_threshold
FHDE_threshold_residual=FHDE_threshold
search_threshold:bool=False

starter_file_path=os.path.abspath(__file__)
code_directory_path=os.path.dirname(starter_file_path)

if not search_threshold:
    if not doughnut:
        command=f"python3 {os.path.join(code_directory_path,'generate_topology_list.py')} "
        command+=f"-f -i {data_path} -E REL {rel_eb} -3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -M {method} {FHDE_threshold} "
        print(command)
        subprocess.run(command,shell=True,encoding="utf-8")
        command=f"python3 {os.path.join(code_directory_path,'compress.py')} "
        command+=f"-f -i {data_path} -z {os.path.join(data_path,'.fhde')} -o {os.path.join(data_path,'.fhde.bin')} "
        command+=f"-E REL {rel_eb} -3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -M {method} {FHDE_threshold} "
        print(command)
        subprocess.run(command,shell=True,encoding="utf-8")
    else:
        raise NotImplementedError
else:
    th_preset=[[FHDE_threshold]]
    th_valid=[True]
    key_length=len(th_preset[0])
    while True:
        threshold_dict={}
        with open("threshold.txt","r") as f:
            for line in f.readlines():
                splited_line=line.split(" ")
                key=tuple([int(i) for i in splited_line[0:key_length]])
                threshold_dict[key]=float(splited_line[key_length])
        if len(threshold_dict)==0:
            print("threshold.txt is empty")
            th=copy.deepcopy(th_preset[0])
        else:
            found_th_preset_not_tested=False
            for th in th_preset:
                if tuple(th) not in threshold_dict:
                    found_th_preset_not_tested=True
                    break
            if found_th_preset_not_tested:
                pass
            else:
                for index in range(len(threshold_dict)):
                    th=[int(i) for i in list(threshold_dict.keys())[index]]
                    print(f"index={index},th={th}")
                    found_unsearched=False
                    possible_directions=list(product([-1,0,1],repeat=key_length))
                    possible_directions=[list(i) for i in possible_directions]
                    possible_directions=[i for i in possible_directions if all([th_valid[j] or i[j]==0 for j in range(key_length)])]
                    random.shuffle(possible_directions)
                    for d_th in possible_directions:
                        new_th=[th[i]+d_th[i] for i in range(key_length)]
                        if tuple(new_th) not in threshold_dict and not found_unsearched and all([new_th[i]>0 or not th_valid[i] for i in range(key_length)]):
                            th=new_th
                            found_unsearched=True
                    if not found_unsearched:
                        continue
                    else:
                        break
        print(f"current th={th[0]}")
        command=f"python3 {os.path.join(code_directory_path,'generate_topology_list.py')} "
        command+=f"-f -i {data_path} -E REL {rel_eb} -3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -M {method} {th[0]} "
        print(command)
        subprocess.run(command,shell=True,encoding="utf-8")
        command=f"python3 {os.path.join(code_directory_path,'compress.py')} "
        command+=f"-f -i {data_path} -z {os.path.join(data_path,'.fhde')} -o {os.path.join(data_path,'.fhde.bin')} "
        command+=f"-E REL {rel_eb} -3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -M {method} {th[0]} "
        print(command)
        output=subprocess.run(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE).stdout
        cr=float(output.strip().split("\n")[-1].split(" ")[-1])
        threshold_dict[tuple(th)]=cr
        sorted_threshold_dict=sorted(threshold_dict.items(),key=lambda x:x[1],reverse=True)
        with open("threshold.txt","w") as f:
            for key,value in sorted_threshold_dict:
                for i in key:
                    f.write(f"{i} ")
                f.write(f"{value}\n")
        print(f"th={th},cr={cr}")

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

#NYX/baryon
#eb=1e-2,   th=3,   fhde_cr=88.729607,      fhde_psnr=47.976594,    fhde_ssim=0.955374
#                   hpez_cr=127.539017,     hpez_psnr=51.311496,    hpez_ssim=0.983513
#                   sz3_cr=92.054794,       sz3_psnr=47.666508,     sz3_ssim=0.953954
#eb=1e-3,   th=9,   fhde_cr=13.387239,      fhde_psnr=65.295603,    fhde_ssim=0.999154
#                   hpez_cr=19.305304,      hpez_psnr=65.177432,    hpez_ssim=0.999122
#                   sz3_cr=13.180675,       sz3_psnr=64.931589,     sz3_ssim=0.999064
#eb=1e-4,   th=31,  fhde_cr=5.576238,       fhde_psnr=85.099650,    fhde_ssim=0.999991
#                   hpez_cr=6.825794,       hpez_psnr=84.772510,    hpez_ssim=0.999990
#                   sz3_cr=5.661443,        sz3_psnr=84.822851,     sz3_ssim=0.999990
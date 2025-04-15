import os,subprocess
from typing import List

def call_hpez_compress(project_directory_path:str,data_path:str,data_shape:List[int],rel_eb:float):
    command=f"hpez -i {data_path} -z {data_path}_{rel_eb}.hpez -o {data_path}_{rel_eb}.hpez.bin -f -M REL {rel_eb} -q 4 -3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -a"
    process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output_lines=[]
    for line in iter(process.stdout.readline,""):
        print(line,end="",flush=True)
        output_lines.append(line)
    output=("".join(output_lines)).strip()
    cr=float(output.split("\n")[-3].split(" ")[-1])
    psnr=float(output.split("\n")[-6].split(",")[-2].split(" ")[-1])

def call_sz3_compress(project_directory_path:str,data_path:str,data_shape:List[int],rel_eb:float):
    command=f"sz3 -i {data_path} -z {data_path}_{rel_eb}.sz3 -o {data_path}_{rel_eb}.sz3.bin -f -M REL -R {rel_eb} -3 {data_shape[2]} {data_shape[1]} {data_shape[0]}"
    process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output_lines=[]
    for line in iter(process.stdout.readline,""):
        print(line,end="",flush=True)
        output_lines.append(line)
    output=("".join(output_lines)).strip()
    cr=float(output.split("\n")[-3].split(" ")[-1])
    return cr

starter_file_path=os.path.abspath(__file__)
project_directory_path=os.path.dirname(starter_file_path)

data_path:str="/anvil/projects/x-cis240192/x-zjian1/APS_DYS/xpcs_datasets/E017_CeramicGlass_L2Mq0_060C_att00_001/E017_CeramicGlass_L2Mq0_060C_att00_001_001.bin"
data_shape:List[int]=[1024,1813,1558]
ASTZ_eb=1e-3
ASTZ_cr=122.766

left_eb=0.0011084857580706386
right_eb=0.001147202690439877
left_cr=118.163055
right_cr=122.874776
while True:
    if right_cr<ASTZ_cr or left_cr>ASTZ_cr:
        raise ValueError("ASTZ_cr is not in the range of left_cr and right_cr")
    middle_eb=(left_eb*right_eb)**0.5
    middle_cr=call_sz3_compress(project_directory_path,data_path,data_shape,middle_eb)
    print(f"left_eb:{left_eb},left_cr:{left_cr}")
    print(f"middle_eb:{middle_eb},middle_cr:{middle_cr}")
    print(f"right_eb:{right_eb},right_cr:{right_cr}")
    if middle_cr>right_cr or middle_cr<left_cr:
        raise ValueError("middle_cr is not in the range of left_cr and right_cr")
    if middle_cr>ASTZ_cr:
        right_eb=middle_eb
        right_cr=middle_cr
    elif middle_cr<ASTZ_cr:
        left_eb=middle_eb
        left_cr=middle_cr
    else:
        print(f"middle_eb:{middle_eb},middle_cr:{middle_cr}")
        break
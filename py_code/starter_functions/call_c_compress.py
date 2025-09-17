import os,subprocess

def call_c_compress(project_directory_path:str,data_path:str,rel_eb:float,FHDE_threshold:int):
    os.chdir("c_code_v2")
    os.makedirs("bin",exist_ok=True)
    bin_path=os.path.join(os.getcwd(),"bin","astz")
    if os.path.exists(bin_path):
        os.remove(bin_path)
    subprocess.run(f"g++ main.cpp -o {bin_path} -O3",cwd=os.getcwd(),shell=True,encoding="utf-8")
    if not os.path.exists(bin_path):
        return None,None,None
    rel_eb_str=f"{rel_eb:.0e}"
    command=f"{bin_path} -i {data_path} -z {data_path}.astz -E REL {rel_eb_str} -M {FHDE_threshold}"
    process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.STDOUT,errors="ignore")
    output_lines=[]
    for line in iter(process.stdout.readline,""):
        print(line,end="",flush=True)
        output_lines.append(line)


# def call_c_compress(project_directory_path:str,data_path:str,data_shape:List[int],rel_eb:float,method:str,FHDE_threshold:int):
#     os.chdir("c_code")
#     os.makedirs("build",exist_ok=True)
#     os.chdir("build")
#     build_path=os.getcwd()
#     # subprocess.run(f"cmake -DCMAKE_INSTALL_PREFIX:PATH={os.path.join(project_directory_path,'c_code','install')} ..",cwd=build_path,shell=True,encoding="utf-8")
#     subprocess.run("make",cwd=build_path,shell=True,encoding="utf-8")
#     print(build_path)
#     os.chdir(project_directory_path)
#     command=f"{build_path +'/fhde'} -f -i {data_path} -o {data_path+'.fhde'} "
#     command+=f"-3 {data_shape[2]} {data_shape[1]} {data_shape[0]} -M REL {rel_eb} -a -c {'./topology_list/Uf48.bin.dat.txt'}"
#     print(command)
#     process=subprocess.Popen(command,shell=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.PIPE)
#     output_lines=[]
#     for line in iter(process.stdout.readline,""):
#         print(line,end="",flush=True)
#         output_lines.append(line)
#     output=("".join(output_lines)).strip()
#     return output
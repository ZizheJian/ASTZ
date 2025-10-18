import torch,os,sys
import numpy as np
from transformers import AutoTokenizer,AutoModelForCausalLM
from matplotlib import pyplot as plt
from datasets import load_dataset

project_directory_path=os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_directory_path,"py_code"))

from py_code.args import args_c
from py_code.stencil_manager import stencil_manager_c
from py_code.read_write_dataset import min_max_data,restore_data_range
from py_code.stencil_functions.search_stencil_1d import search_stencil_1d
from py_code.stencil_functions.search_stencil_2d import search_stencil_2d
from py_code.stencil_functions.apply_stencil_compress_gpu_1d import apply_stencil_compress_gpu_1d
from py_code.stencil_functions.apply_stencil_compress_gpu_2d import apply_stencil_compress_gpu_2d
from py_code.stencil_functions.apply_stencil_decompress_gpu_2d import apply_stencil_decompress_gpu_2d

# mode="original"
# mode="q"
# mode="qoz2"
mode="astz"

model_name="Qwen/Qwen3-4B-Base"
q_model_name="Qwen/Qwen3-4B-AWQ"
# model_name="tencent/Hunyuan-4B-Instruct"
# q_model_name="tencent/Hunyuan-4B-Instruct-GPTQ-Int4"
block_size_limit=2**27

abs_eb_list=[6e-3]

def call_qoz2(name,param,abs_eb,force_compress=False,force_decompress=False):
    print(f"Processing {name}, shape= {param.shape}, abs_eb= {abs_eb:.0e}")
    original_size=param.numel()*param.element_size()
    compressed_size=0
    dataset_dir_path=f"/work/nvme/bdgi/zjian1/llm_weights/{model_name.split('/')[-1]}"
    input_data_path=os.path.join(dataset_dir_path,name)
    abs_eb_str=f"{abs_eb:.1e}"
    if os.path.exists(f"{input_data_path}_{abs_eb_str}.qoz2.bin") and (not force_decompress):
        ret=torch.from_numpy(np.fromfile(f"{input_data_path}_{abs_eb_str}.qoz2.bin",dtype=np.float32).reshape(param.shape)).to(param.device).to(param.dtype)
        compressed_size=os.path.getsize(f"{input_data_path}_{abs_eb_str}.qoz2")
        return ret,original_size,compressed_size
    else:
        command=f"qoz -i '{input_data_path}' -z '{input_data_path}_{abs_eb_str}.qoz2' -o '{input_data_path}_{abs_eb_str}.qoz2.bin' "
        command+=f"-f -M ABS {abs_eb_str} -q 4 "
        if param.dim()==1:
            command+=f"-2 {param.shape[0]} 1 "
        else:
            command+=f"-2 {param.shape[1]} {param.shape[0]} "
        print(command)
        os.system(command)
        ret=torch.from_numpy(np.fromfile(f"{input_data_path}_{abs_eb_str}.qoz2.bin",dtype=np.float32).reshape(param.shape)).to(param.device).to(param.dtype)
        compressed_size=os.path.getsize(f"{input_data_path}_{abs_eb_str}.qoz2")
        return ret,original_size,compressed_size

def call_ASTZ(name,param,abs_eb,device,force_search_stencil=False,force_compress=False):
    abs_eb_str=f"{abs_eb:.1e}"
    dataset_dir_path=f"/work/nvme/bdgi/zjian1/llm_weights/{model_name.split('/')[-1]}"
    stencil_path=os.path.join(dataset_dir_path,f"{name}_{abs_eb_str}.stencil")
    original_size=param.numel()*param.element_size()
    compressed_size=0
    for block_num in range(1,10):
        block_shape=tuple((x+block_num-1)//block_num for x in param.shape)
        block_size=np.prod(block_shape)*param.element_size()
        if block_size<=block_size_limit:
            break
    ######## search stencil ########
    if (not os.path.exists(stencil_path)) or force_search_stencil:
        print(f"Searching stencil for {name}, shape= {param.shape}, abs_eb= {abs_eb_str}")
        if param.dim()==1:
            fake_args_list=["-f32",
                            "-i","fake_input_path",
                            "-c",stencil_path,
                            "-E","ABS",abs_eb_str,
                            "-1",str(block_shape[0]),
                            "-M","FHDE","9"]
            i0=block_num//2
            start0=round(i0*(param.shape[0]-block_shape[0])/(block_num-1)) if block_num>1 else 0
            end0=min(start0+block_shape[0],param.shape[0])
            args=args_c(fake_args_list)
            stencil_manager=stencil_manager_c(args)
            args.data=param[start0:end0].detach().to(torch.float32).cpu()
            args.data_min=args.data.min()
            args.data_max=args.data.max()
            args.data=min_max_data(args.data,args)
            args.abs_eb=2*args.abs_eb/(args.data_max-args.data_min)
            args.parameter_eb=args.abs_eb*args.parameter_relative_eb
            search_stencil_1d(args,stencil_manager)
        else:
            fake_args_list=["-f32",
                            "-i","fake_input_path",
                            "-c",stencil_path,
                            "-E","ABS",abs_eb_str,
                            "-2",str(block_shape[0]),str(block_shape[1]),
                            "-M","FHDE","9"]
            i0=i1=block_num//2
            start0=round(i0*(param.shape[0]-block_shape[0])/(block_num-1)) if block_num>1 else 0
            start1=round(i1*(param.shape[1]-block_shape[1])/(block_num-1)) if block_num>1 else 0
            end0=min(start0+block_shape[0],param.shape[0])
            end1=min(start1+block_shape[1],param.shape[1])
            args=args_c(fake_args_list)
            stencil_manager=stencil_manager_c(args)
            args.data=param[start0:end0,start1:end1].detach().to(torch.float32).cpu()
            args.data_min=args.data.min()
            args.data_max=args.data.max()
            args.data=min_max_data(args.data,args)
            args.abs_eb=2*args.abs_eb/(args.data_max-args.data_min)
            args.parameter_eb=args.abs_eb*args.parameter_relative_eb
            search_stencil_2d(args,stencil_manager)
    ######## compress ########
    output_param=torch.zeros_like(param)
    if param.dim()==1:
        fake_args_list=["-f32",
                    "-i","fake_input_path",
                    "-z","fake_compressed_path",
                    "-c",stencil_path,
                    "-E","ABS",abs_eb_str,
                    "-1",str(block_shape[0]),
                    "-M","FHDE","9"]
        for i0 in range(block_num):
            compressed_path=os.path.join(dataset_dir_path,f"{name}_{i0}_{abs_eb_str}.astz")
            decompressed_path=os.path.join(dataset_dir_path,f"{name}_{i0}_{abs_eb_str}.astz.bin")
            print(f"Compressing block {i0}/{block_num} for {name}, shape= {block_shape}, abs_eb= {abs_eb_str}")
            start0=round(i0*(param.shape[0]-block_shape[0])/(block_num-1)) if block_num>1 else 0
            end0=min(start0+block_shape[0],param.shape[0])
            if (not os.path.exists(compressed_path)) or (not os.path.exists(decompressed_path)) or force_compress:
                args=args_c(fake_args_list)
                stencil_manager=stencil_manager_c(args)
                args.data=param[start0:end0].to(torch.float32)
                args.data_min=args.data.min()
                args.data_max=args.data.max()
                args.data=min_max_data(args.data,args)
                args.abs_eb=2*args.abs_eb/(args.data_max-args.data_min)
                args.parameter_eb=args.abs_eb*args.parameter_relative_eb
                args.device=device
                args.output_decompressed_data=True
                apply_stencil_compress_gpu_1d(args,stencil_manager)
                with open(compressed_path,"wb") as f:
                    f.write(args.zstd_bs)
                args.data_decompressed.cpu().numpy().tofile(decompressed_path)
                output_param[start0:end0].copy_(args.data_decompressed.to(param.dtype))
            else:
                data_decompressed=torch.from_numpy(np.fromfile(decompressed_path,dtype=np.float32).reshape(block_shape)).to(param.device).to(param.dtype)
                output_param[start0:end0].copy_(data_decompressed)
            compressed_size+=os.path.getsize(compressed_path)
    else:
        fake_args_list=["-f32",
                        "-i","fake_input_path",
                        "-z","fake_compressed_path",
                        "-c",stencil_path,
                        "-E","ABS",abs_eb_str,
                        "-2",str(block_shape[0]),str(block_shape[1]),
                        "-M","FHDE","9"]
        for i0 in range(block_num):
            for i1 in range(block_num):
                compressed_path=os.path.join(dataset_dir_path,f"{name}_{i0}{i1}_{abs_eb_str}.astz")
                decompressed_path=os.path.join(dataset_dir_path,f"{name}_{i0}{i1}_{abs_eb_str}.astz.bin")
                print(f"Compressing block {i0}{i1}/{block_num}{block_num} for {name}, shape= {block_shape}, abs_eb= {abs_eb_str}")
                start0=round(i0*(param.shape[0]-block_shape[0])/(block_num-1)) if block_num>1 else 0
                start1=round(i1*(param.shape[1]-block_shape[1])/(block_num-1)) if block_num>1 else 0
                end0=min(start0+block_shape[0],param.shape[0])
                end1=min(start1+block_shape[1],param.shape[1])
                if (not os.path.exists(compressed_path)) or (not os.path.exists(decompressed_path)) or force_compress:
                    args=args_c(fake_args_list)
                    stencil_manager=stencil_manager_c(args)
                    args.data=param[start0:end0,start1:end1].to(torch.float32)
                    args.data_min=args.data.min()
                    args.data_max=args.data.max()
                    args.data=min_max_data(args.data,args)
                    args.abs_eb=2*args.abs_eb/(args.data_max-args.data_min)
                    args.parameter_eb=args.abs_eb*args.parameter_relative_eb
                    args.device=device
                    args.output_decompressed_data=True
                    apply_stencil_compress_gpu_2d(args,stencil_manager)
                    with open(compressed_path,"wb") as f:
                        f.write(args.zstd_bs)
                    decompressed_path=os.path.join(dataset_dir_path,f"{name}_{i0}{i1}_{abs_eb_str}.astz.bin")
                    output_param[start0:end0,start1:end1].copy_(args.data_decompressed.to(param.dtype))
                else:
                    data_decompressed=torch.from_numpy(np.fromfile(decompressed_path,dtype=np.float32).reshape(block_shape)).to(param.device).to(param.dtype)
                    output_param[start0:end0,start1:end1].copy_(data_decompressed)
                compressed_size+=os.path.getsize(compressed_path)
    return output_param,original_size,compressed_size

available_thread_num=torch.get_num_threads()
print(f"Available threads: {available_thread_num}")
torch.set_num_threads((available_thread_num+1)//2)
print(f"Set threads to: {torch.get_num_threads()}")
cache_dir="/work/nvme/bdgi/zjian1/hf_cache"
tokenizer=AutoTokenizer.from_pretrained(model_name,cache_dir=cache_dir)
dataset=load_dataset("wikitext","wikitext-2-raw-v1",cache_dir=cache_dir,split="validation")

device=torch.device("cuda" if torch.cuda.is_available() else "cpu")

if mode=="original":
    model=AutoModelForCausalLM.from_pretrained(model_name,cache_dir=cache_dir).to(device).eval()
    loss=[]
    total_size=0
    with torch.no_grad():
        for name,param in model.named_parameters():
            weight=param.detach().to(torch.float32).cpu().numpy()
            weight.tofile(f"/work/nvme/bdgi/zjian1/llm_weights/{model_name.split('/')[-1]}/{name}")
            print(weight.shape)
    for i,sample in enumerate(dataset):
        print(f"{i}/{len(dataset)}")
        text=sample["text"]
        if len(text.strip())==0:
            continue
        inputs=tokenizer(text,return_tensors="pt",truncation=True,max_length=512).to(device)
        with torch.no_grad():
            outputs=model(**inputs,labels=inputs["input_ids"])
            loss.append(outputs.loss.item())
    print(f"Avg PPL= {torch.tensor(loss).mean():.3f}")
    with open(f"ppl_log_original.txt","a") as f:
        f.write(f"{mode} {model_name} 1 {torch.tensor(loss).mean():.3f}\n")

if mode=="q":
    model=AutoModelForCausalLM.from_pretrained(q_model_name,cache_dir=cache_dir).to(device).eval()
    loss=[]
    for i,sample in enumerate(dataset):
        print(f"{i}/{len(dataset)}")
        text=sample["text"]
        if len(text.strip())==0:
            continue
        inputs=tokenizer(text,return_tensors="pt",truncation=True,max_length=512).to(device)
        with torch.no_grad():
            outputs=model(**inputs,labels=inputs["input_ids"])
            loss.append(outputs.loss.item())
    print(f"Avg PPL= {torch.tensor(loss).mean():.3f}")
    with open(f"ppl_log_q.txt","a") as f:
        f.write(f"{mode} {model_name} {torch.tensor(loss).mean():.3f}\n")

# if mode=="quantize":
#     model=AutoModelForCausalLM.from_pretrained(model_name,cache_dir=cache_dir).to(device).eval()
#     original_state={k:v.clone() for k,v in model.state_dict().items()}
#     for abs_eb in [3e-3]:
#         total_original_size=0
#         total_compressed_size=0
#         with torch.no_grad():
#             for name,param in model.named_parameters():
#                 param.copy_(torch.round(param/(2*abs_eb))*(2*abs_eb))
#         loss=[]
#         for i,sample in enumerate(dataset):
#             text=sample["text"]
#             if len(text.strip())==0:
#                 continue
#             inputs=tokenizer(text,return_tensors="pt",truncation=True,max_length=512).to(device)
#             with torch.no_grad():
#                 outputs=model(**inputs,labels=inputs["input_ids"])
#                 loss.append(outputs.loss.item())
#         print(f"abs_eb= {abs_eb}")
#         print(f"Avg PPL= {torch.tensor(loss).mean():.3f}")
#         with open(f"ppl_log_quantize.txt","a") as f:
#             f.write(f"{torch.tensor(loss).mean():.3f} ")
#         with torch.no_grad():
#             for k,v in model.state_dict().items():
#                 v.copy_(original_state[k])

if mode=="qoz2":
    model=AutoModelForCausalLM.from_pretrained(model_name,cache_dir=cache_dir).to(device).eval()
    original_state={k:v.clone() for k,v in model.state_dict().items()}
    for abs_eb in abs_eb_list:
        total_original_size=0
        total_compressed_size=0
        with torch.no_grad():
            for name,param in model.named_parameters():
                temp_param,original_size,compressed_size=call_qoz2(name,param,abs_eb)
                param.copy_(temp_param.clone())
                total_original_size+=original_size
                total_compressed_size+=compressed_size
        loss=[]
        for i,sample in enumerate(dataset):
            print(f"{i}/{len(dataset)}")
            text=sample["text"]
            if len(text.strip())==0:
                continue
            inputs=tokenizer(text,return_tensors="pt",truncation=True,max_length=512).to(device)
            with torch.no_grad():
                outputs=model(**inputs,labels=inputs["input_ids"])
                loss.append(outputs.loss.item())
        print(f"abs_eb= {abs_eb}")
        print(f"CR= {total_original_size/total_compressed_size:.3f}")
        print(f"Avg PPL= {torch.tensor(loss).mean():.3f}")
        with open(f"ppl_log_qoz2.txt","a") as f:
            f.write(f"{mode} {model_name} {abs_eb} {total_original_size/total_compressed_size:.3f} {torch.tensor(loss).mean():.3f}\n")
        with torch.no_grad():
            for k,v in model.state_dict().items():
                v.copy_(original_state[k])

if mode=="astz":
    model=AutoModelForCausalLM.from_pretrained(model_name,cache_dir=cache_dir).to(device).eval()
    original_state={k:v.clone() for k,v in model.state_dict().items()}
    for abs_eb in abs_eb_list:
        total_original_size=0
        total_compressed_size=0
        with torch.no_grad():
            for name,param in model.named_parameters():
                temp_param,original_size,compressed_size=call_ASTZ(name,param,abs_eb,device)
                param.copy_(temp_param.clone())
                total_original_size+=original_size
                total_compressed_size+=compressed_size
        loss=[]
        for i,sample in enumerate(dataset):
            print(f"{i}/{len(dataset)}")
            text=sample["text"]
            if len(text.strip())==0:
                continue
            inputs=tokenizer(text,return_tensors="pt",truncation=True,max_length=512).to(device)
            with torch.no_grad():
                outputs=model(**inputs,labels=inputs["input_ids"])
                loss.append(outputs.loss.item())
        print(f"abs_eb= {abs_eb}")
        print(f"CR= {total_original_size/total_compressed_size:.3f}")
        print(f"Avg PPL= {torch.tensor(loss).mean():.3f}")
        with open(f"ppl_log_astz.txt","a") as f:
            f.write(f"{mode} {model_name} {abs_eb} {total_original_size/total_compressed_size:.3f} {torch.tensor(loss).mean():.3f}\n")
        with torch.no_grad():
            for k,v in model.state_dict().items():
                v.copy_(original_state[k])
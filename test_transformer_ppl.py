from transformers import AutoTokenizer,AutoModelForCausalLM
import torch
from matplotlib import pyplot as plt
from datasets import load_dataset

model_name="Qwen/Qwen3-4B-Base"
awq_model_name="Qwen/Qwen3-4B-AWQ"
cache_dir="/work/hdd/bcnl/zjian1/hf_cache"
tokenizer=AutoTokenizer.from_pretrained(model_name,cache_dir=cache_dir)
model=AutoModelForCausalLM.from_pretrained(model_name,cache_dir=cache_dir)
awq_model=AutoModelForCausalLM.from_pretrained(awq_model_name,cache_dir=cache_dir)
dataset=load_dataset("wikitext","wikitext-2-raw-v1",cache_dir=cache_dir,split="validation")

device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
model=model.to(device)
awq_model=awq_model.to(device)
model.eval()
awq_model.eval()

# loss=[]
# for i,sample in enumerate(dataset):
#     if i>=1000:
#         break
#     text=sample["text"]
#     if len(text.strip())==0:
#         continue
#     inputs=tokenizer(text,return_tensors="pt",truncation=True,max_length=512).to(device)
#     with torch.no_grad():
#         outputs=model(**inputs,labels=inputs["input_ids"])
#         loss.append(outputs.loss.item())
# print(f"Avg PPL = {torch.exp(torch.tensor(loss).mean()):.2f}")

# loss=[]
# for i,sample in enumerate(dataset):
#     if i>=1000:
#         break
#     text=sample["text"]
#     if len(text.strip())==0:
#         continue
#     inputs=tokenizer(text,return_tensors="pt",truncation=True,max_length=512).to(device)
#     with torch.no_grad():
#         outputs=awq_model(**inputs,labels=inputs["input_ids"])
#         loss.append(outputs.loss.item())
# print(f"Avg PPL = {torch.exp(torch.tensor(loss).mean()):.2f}")

original_state={k:v.clone() for k,v in model.state_dict().items()}

for power in range(-4,-20,-1):
    abs_eb=rel_eb=2**power
    ########ABS########
    with torch.no_grad():
        for name,param in model.named_parameters():
            step=2*abs_eb
            param.copy_(torch.round(param/step)*step)
    loss=[]
    for i,sample in enumerate(dataset):
        if i>=1000:
            break
        text=sample["text"]
        if len(text.strip())==0:
            continue
        inputs=tokenizer(text,return_tensors="pt",truncation=True,max_length=512).to(device)
        with torch.no_grad():
            outputs=model(**inputs,labels=inputs["input_ids"])
            loss.append(outputs.loss.item())
    print(f"Avg PPL = {torch.exp(torch.tensor(loss).mean()):.2f}")
    with open(f"quantization_log.txt","a") as f:
        f.write(f"{torch.exp(torch.tensor(loss).mean()):.2f} ")
    with torch.no_grad():
        for k,v in model.state_dict().items():
            v.copy_(original_state[k])
    ########REL########
    with torch.no_grad():
        for name,param in model.named_parameters():
            max_weight,min_weight=param.max(),param.min()
            step=2*rel_eb*(max_weight-min_weight)
            param.copy_(torch.round(param/step)*step)
    loss=[]
    for i,sample in enumerate(dataset):
        if i>=1000:
            break
        text=sample["text"]
        if len(text.strip())==0:
            continue
        inputs=tokenizer(text,return_tensors="pt",truncation=True,max_length=512).to(device)
        with torch.no_grad():
            outputs=model(**inputs,labels=inputs["input_ids"])
            loss.append(outputs.loss.item())
    print(f"Avg PPL = {torch.exp(torch.tensor(loss).mean()):.2f}")
    with open(f"quantization_log.txt","a") as f:
        f.write(f"{torch.exp(torch.tensor(loss).mean()):.2f}\n")
    with torch.no_grad():
        for k,v in model.state_dict().items():
            v.copy_(original_state[k])
import torch,os
from matplotlib import pyplot as plt
from transformers import AutoTokenizer,AutoModelForCausalLM

model_name="Qwen/Qwen3-4B-Base"
tokenizer=AutoTokenizer.from_pretrained(model_name)
model=AutoModelForCausalLM.from_pretrained(model_name)

device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
model=model.to(device) # pyright: ignore[reportArgumentType]
model.eval()

prompt="Once upon a time"
inputs=tokenizer(prompt,return_tensors="pt").to(device)

with torch.no_grad():
    outputs_generated=model.generate(**inputs,max_new_tokens=50,do_sample=True,top_k=50,top_p=0.95)
    print(tokenizer.decode(outputs_generated[0],skip_special_tokens=True))

hf_home=os.environ.get("HF_HOME")
output_path=os.path.join(os.path.dirname(hf_home),"llm_weights")
print(f"Output path: {output_path}")
for name,param in model.state_dict().items():
    print(name,param.shape)
    if param.ndim==2:
        weight=param.detach().cpu().numpy()
        # plt.figure()
        # plt.imshow(weight,aspect="auto",cmap="bwr")
        # plt.colorbar()
        # plt.tight_layout()
        # plt.savefig(f"png/{name}.png")
        # plt.close()
        weight.tofile(f"{os.path.join(output_path,name)}.bin")

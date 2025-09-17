import torch
from args import args_c
from read_dataset import read_dataset
from search_stencil_tools import search_stencil
from stencil_manager import stencil_manager_c

exit()
available_thread_num=torch.get_num_threads()
print(f"Available threads: {available_thread_num}")
torch.set_num_threads(available_thread_num//2)
print(f"Set threads to: {torch.get_num_threads()}")

args=args_c()
stencil_manager=stencil_manager_c()
read_dataset(args)
search_stencil(args,stencil_manager)

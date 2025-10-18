import torch
from args import args_c
from read_write_dataset import read_dataset
from stencil_functions.search_stencil_3d import search_stencil_3d
from stencil_functions.search_stencil_2d import search_stencil_2d
from stencil_functions.search_stencil_1d import search_stencil_1d
from stencil_functions.search_stencil_4d import search_stencil_4d
from stencil_manager import stencil_manager_c

available_thread_num=torch.get_num_threads()
print(f"Available threads: {available_thread_num}")
torch.set_num_threads((available_thread_num+1)//2)
print(f"Set threads to: {torch.get_num_threads()}")

args=args_c()
stencil_manager=stencil_manager_c(args)
read_dataset(args)
if args.dim_num==4:
    search_stencil_4d(args,stencil_manager)
elif args.dim_num==3:
    search_stencil_3d(args,stencil_manager)
elif args.dim_num==2:
    search_stencil_2d(args,stencil_manager)
elif args.dim_num==1:
    search_stencil_1d(args,stencil_manager)

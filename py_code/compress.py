import torch,math,os
from args import args_c
from plot_py import plot_c
from read_write_dataset import read_dataset,write_compressed_bitstream
from stencil_manager import stencil_manager_c
from stencil_functions.apply_stencil_compress_1d import apply_stencil_compress_1d
from stencil_functions.apply_stencil_compress_2d import apply_stencil_compress_2d
from stencil_functions.apply_stencil_compress_3d import apply_stencil_compress_3d
from stencil_functions.apply_stencil_compress_4d import apply_stencil_compress_4d
from stencil_functions.apply_stencil_compress_gpu_1d import apply_stencil_compress_gpu_1d
from stencil_functions.apply_stencil_compress_gpu_2d import apply_stencil_compress_gpu_2d
from stencil_functions.apply_stencil_compress_gpu_3d import apply_stencil_compress_gpu_3d
from stencil_functions.apply_stencil_compress_gpu_4d import apply_stencil_compress_gpu_4d
import zstandard as zstd
from bitarray import bitarray

available_thread_num=torch.get_num_threads()
print(f"Available threads: {available_thread_num}")
torch.set_num_threads((available_thread_num+1)//2)
print(f"Set threads to: {torch.get_num_threads()}")

args=args_c()
stencil_manager=stencil_manager_c(args)
read_dataset(args)

if "gpu" in args.method:
    args.data=args.data.to(args.device)
    if args.dim_num==4:
        apply_stencil_compress_gpu_4d(args,stencil_manager)
    elif args.dim_num==3:
        apply_stencil_compress_gpu_3d(args,stencil_manager)
    elif args.dim_num==2:
        apply_stencil_compress_gpu_2d(args,stencil_manager)
    elif args.dim_num==1:
        apply_stencil_compress_gpu_1d(args,stencil_manager)
else:
    if args.dim_num==4:
        apply_stencil_compress_4d(args,stencil_manager)
    elif args.dim_num==3:
        apply_stencil_compress_3d(args,stencil_manager)
    elif args.dim_num==2:
        apply_stencil_compress_2d(args,stencil_manager)
    elif args.dim_num==1:
        apply_stencil_compress_1d(args,stencil_manager)

write_compressed_bitstream(args)
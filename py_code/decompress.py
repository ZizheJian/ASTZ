import torch,math,os
from args import args_c
from plot_py import plot_c
from read_write_dataset import read_compressed_bitstream,write_dataset
from stencil_manager import stencil_manager_c
from stencil_functions.apply_stencil_decompress_1d import apply_stencil_decompress_1d
from stencil_functions.apply_stencil_decompress_2d import apply_stencil_decompress_2d
from stencil_functions.apply_stencil_decompress_3d import apply_stencil_decompress_3d
from stencil_functions.apply_stencil_decompress_gpu_1d import apply_stencil_decompress_gpu_1d
from stencil_functions.apply_stencil_decompress_gpu_2d import apply_stencil_decompress_gpu_2d
from stencil_functions.apply_stencil_decompress_gpu_3d import apply_stencil_decompress_gpu_3d
import zstandard as zstd
from bitarray import bitarray

available_thread_num=torch.get_num_threads()
print(f"Available threads: {available_thread_num}")
torch.set_num_threads((available_thread_num+1)//2)
print(f"Set threads to: {torch.get_num_threads()}")

args=args_c()
stencil_manager=stencil_manager_c(args)
read_compressed_bitstream(args)

if "gpu" in args.method:
    if args.dim_num==3:
        apply_stencil_decompress_gpu_3d(args,stencil_manager)
    elif args.dim_num==2:
        apply_stencil_decompress_gpu_2d(args,stencil_manager)
    elif args.dim_num==1:
        apply_stencil_decompress_gpu_1d(args,stencil_manager)
    args.data_decompressed=args.data_decompressed.cpu()
else:
    if args.dim_num==3:
        apply_stencil_decompress_3d(args,stencil_manager)
    elif args.dim_num==2:
        apply_stencil_decompress_2d(args,stencil_manager)
    elif args.dim_num==1:
        apply_stencil_decompress_1d(args,stencil_manager)

write_dataset(args)
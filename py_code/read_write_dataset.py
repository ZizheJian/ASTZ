import torch,math
import numpy as np
from torch import Tensor
from args import args_c

def min_max_data(data:Tensor,args:args_c):
    return 2*(data-args.data_min)/(args.data_max-args.data_min)-1

def restore_data_range(data:Tensor,args:args_c):
    return (data+1)*(args.data_max-args.data_min)/2+args.data_min

def read_dataset(args:args_c):
    data_num=math.prod(args.data_shape)
    if args.data_type_str=="f32":
        args.data=torch.from_file(args.data_path,dtype=torch.float32,size=data_num)
    elif args.data_type_str=="ui16":
        args.data=torch.from_numpy(np.fromfile(args.data_path,dtype=np.uint16,count=data_num).astype(np.float32))
    args.data=args.data.view(args.data_shape)
    args.data_min=args.data.min()
    args.data_max=args.data.max()
    print(f"data_min:{args.data_min}, data_max:{args.data_max}")
    args.data=min_max_data(args.data,args)
    if args.eb_type=="REL":
        args.abs_eb=2*args.rel_eb
    else:
        args.abs_eb=2*args.abs_eb/(args.data_max-args.data_min)
    args.parameter_eb=args.abs_eb*args.parameter_relative_eb

def write_compressed_bitstream(args:args_c):
    with open(args.data_compressed_path,"wb") as f:
        f.write(args.zstd_bs)

def read_compressed_bitstream(args:args_c):
    with open(args.data_compressed_path,"rb") as f:
        args.zstd_bs=f.read()

def write_dataset(args:args_c):
    if args.data_type_str=="ui16":
        args.data_decompressed=restore_data_range(args.data_decompressed,args).round().clamp(0,65535)
        args.data_decompressed.numpy().astype(np.uint16).tofile(args.data_decompressed_path)
    elif args.data_type_str=="f32":
        args.data_decompressed=restore_data_range(args.data_decompressed,args)
        args.data_decompressed.numpy().tofile(args.data_decompressed_path)

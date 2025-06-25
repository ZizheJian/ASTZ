import torch
import numpy as np
from args import args_c

def read_dataset(args:args_c):
    data_num=args.data_shape[0]*args.data_shape[1]*args.data_shape[2]
    if args.data_type_float32:
        args.data=torch.from_file(args.data_path,dtype=torch.float32,size=data_num)
    elif args.data_type_uint16:
        args.data=torch.from_numpy(np.fromfile(args.data_path,dtype=np.uint16,count=data_num).astype(np.float32))
    args.data=args.data.view(args.data_shape)
    args.data_min=args.data.min()
    args.data_max=args.data.max()
    print(f"data_min:{args.data_min}, data_max:{args.data_max}")
    args.data=2*(args.data-args.data_min)/(args.data_max-args.data_min)-1
    if args.eb_type=="REL":
        args.abs_eb=2*args.rel_eb
    else:
        args.abs_eb=2*args.abs_eb/(args.data_max-args.data_min)
    args.parameter_eb=2*args.rel_eb*args.parameter_relative_eb
    
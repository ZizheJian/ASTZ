import torch
from args import args_c

def read_dataset(args:args_c):
    file_float_num=args.data_shape[0]*args.data_shape[1]*args.data_shape[2]
    args.data=torch.from_file(args.data_path,dtype=torch.float32,size=file_float_num)
    args.data=args.data.view(args.data_shape)
    args.data_min=args.data.min()
    args.data_max=args.data.max()
    args.data=(args.data-args.data_min)/(args.data_max-args.data_min)*2-1
    args.abs_eb=((args.data.max()-args.data.min())*args.rel_eb).item()
    args.parameter_eb=2*args.rel_eb*args.parameter_relative_eb#假设参数的范围是[-1,1]
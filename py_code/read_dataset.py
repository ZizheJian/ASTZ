import torch
from args import args_c

def read_dataset(args:args_c):
    file_float_num=args.data_shape[0]*args.data_shape[1]*args.data_shape[2]
    args.data=torch.from_file(args.data_path,dtype=torch.float32,size=file_float_num)
    args.data=args.data.view(args.data_shape)
    # value,freq=torch.unique(args.data,return_counts=True)
    # for i in range(len(value)):
    #     print(value[i],freq[i])
    #     input()
    # exit()
    args.data_min=args.data.min()
    args.data_max=args.data.max()
    print(f"data_min:{args.data_min}, data_max:{args.data_max}")
    args.data=2*(args.data-args.data_min)/(args.data_max-args.data_min)-1
    args.abs_eb=2*args.rel_eb
    args.parameter_eb=2*args.rel_eb*args.parameter_relative_eb
    
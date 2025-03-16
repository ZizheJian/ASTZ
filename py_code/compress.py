import torch,math,copy,subprocess,os
import numpy as np
from torch import nn
from torch.nn import functional as F
from args import args_c
from plot_py import plot_c
from read_dataset import read_dataset
from topology_manager import topology_manager_c
from search_topology_tools import apply_topology1,apply_topology2
from separate_diffraction_average_residual import separate_diffraction_average_residual,get_actual_residual_data,add_average_and_residual_data

def compress(t1:float=None,t2:float=None,t3:float=None):
    torch.set_num_threads(8)
    args=args_c()
    if t1 is not None:
        args.FHDE_global_threshold=t1
        args.FHDE_global_threshold_average=t1
    if t2 is not None:
        args.FHDE_global_threshold_residual=t2
    plotter=plot_c(args)
    topology_manager=topology_manager_c()
    read_dataset(args)
    if args.separate_average_residual:
        ########压缩average_data########
        separate_diffraction_average_residual(args,plotter)
        # with open("data_generated/average.bin","wb") as f:
        #     args.average_data.numpy().tofile(f)
        # sz3_command=f"sz3 -i data_generated/average.bin -z data_generated/average.bin.sz3 -o data_generated/average.bin.sz3.bin -f -M REL -R {args.rel_eb}"
        # sz3_command+=f" -3 {args.average_data_shape[2]} {args.average_data_shape[1]} {args.average_data_shape[0]} -a"
        # subprocess.run(sz3_command,shell=True)
        # with open("data_generated/average.bin.sz3.bin","rb") as f:
        #     args.decompressed_average_data=torch.tensor(np.fromfile(f,dtype=np.float32)).reshape(args.average_data_shape)
        data_backup=copy.deepcopy(args.data)
        args.data=args.average_data
        data_shape_backup=copy.deepcopy(args.data_shape)
        args.data_shape=args.average_data_shape
        args.decompressed_average_data=apply_topology1(args,topology_manager,part_name="average")
        args.data=data_backup
        args.data_shape=data_shape_backup
        ########压缩residual_data########
        get_actual_residual_data(args)
        # with open("data_generated/residual.bin","wb") as f:
        #     args.residual_data.numpy().tofile(f)
        # sz3_command=f"sz3 -i data_generated/residual.bin -z data_generated/residual.bin.sz3 -o data_generated/residual.bin.sz3.bin -f -M REL -R {args.rel_eb}"
        # sz3_command+=f" -3 {args.data_shape[2]} {args.data_shape[1]} {args.data_shape[0]} -a"
        # subprocess.run(sz3_command,shell=True)
        # with open("data_generated/residual.bin.sz3.bin","rb") as f:
        #     args.decompressed_residual_data=np.fromfile(f,dtype=np.float32).reshape(args.data_shape)
        data_backup=copy.deepcopy(args.data)
        args.data=args.residual_data
        if args.residual_baseline_method==[]:
            args.decompressed_residual_data=apply_topology2(args,part_name="residual")
        else:
            args.decompressed_residual_data=apply_topology1(args,topology_manager,part_name="residual")
        args.data=data_backup
        args.decompressed_data=add_average_and_residual_data(args)
    else:
        args.decompressed_data=apply_topology1(args,topology_manager)
    max_err=(args.data-args.decompressed_data).abs().max().item()
    print(f"max_err={max_err}")
    mse=((args.data-args.decompressed_data)**2).mean().item()
    psnr=10*math.log10(2**2/mse)
    print(f"psnr= {psnr:.6f}")
    with open(args.data_path+".fhde.bin","wb") as f:
        ((args.data_max-args.data_min)*(args.decompressed_data+1)/2+args.data_min).numpy().tofile(f)
    calculateSSIM_command=f"calculateSSIM -f {args.data_path} {args.data_path}.fhde.bin {args.data_shape[2]} {args.data_shape[1]} {args.data_shape[0]}"
    calculateSSIM_ouput=subprocess.check_output(calculateSSIM_command,shell=True,encoding="utf-8")
    ssim=float(calculateSSIM_ouput.strip().split("\n")[-1].split()[-1])
    print(f"ssim= {ssim:.6f}")
    if args.separate_average_residual:
        # bitstream_length_average=os.path.getsize("data_generated/average.bin.sz3")
        # bitstream_length_residual=os.path.getsize("data_generated/residual.bin.sz3")
        # cr=(args.data_shape[0]*args.data_shape[1]*args.data_shape[2]*4)/(bitstream_length_average+bitstream_length_residual)
        compressQuantBins_command=f"compressQuantBins qb/{args.data_name}_average.bin"
        compressQuantBins_output=subprocess.check_output(compressQuantBins_command,shell=True,encoding="utf-8")
        bitstream_length_average=int(compressQuantBins_output.strip().split("\n")[-3].split()[-5])
        compressQuantBins_command=f"compressQuantBins qb/{args.data_name}_residual.bin"
        compressQuantBins_output=subprocess.check_output(compressQuantBins_command,shell=True,encoding="utf-8")
        bitstream_length_residual=int(compressQuantBins_output.strip().split("\n")[-3].split()[-5])
        print(f"bitstream_length_average= {bitstream_length_average}")
        print(f"bitstream_length_residual= {bitstream_length_residual}")
        cr=(args.data_shape[0]*args.data_shape[1]*args.data_shape[2]*4)/(bitstream_length_average+bitstream_length_residual)
    else:
        compressQuantBins_command=f"compressQuantBins qb/{args.data_name}.bin"
        compressQuantBins_output=subprocess.check_output(compressQuantBins_command,shell=True,encoding="utf-8")
        cr=float(compressQuantBins_output.strip().split("\n")[-3].split()[-1])
    print(f"cr= {cr:.6f}")
    return cr,psnr,ssim

if __name__=="__main__":
    compress()
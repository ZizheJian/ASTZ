import torch,math,copy,subprocess,os
from args import args_c
from plot_py import plot_c
from read_dataset import read_dataset
from topology_manager import topology_manager_c
from search_topology_tools import apply_topology,apply_topology2
from separate_diffraction_average_residual import separate_diffraction_average_residual,get_actual_residual_data,add_average_and_residual_data

torch.set_num_threads(8)
args=args_c()
plotter=plot_c(args)
topology_manager=topology_manager_c()
read_dataset(args)
if not args.doughnut:
    apply_topology(args,topology_manager)
    args.parameter=torch.cat(args.parameter)
    sorted_parameter=torch.sort(args.parameter).values
    with open(os.path.join(args.project_root,"sorted_parameter.txt"),"w") as f:
        for i in range(sorted_parameter.size(0)):
            f.write(f"{sorted_parameter[i].item()}\n")
else:
    ########压缩average_data########
    separate_diffraction_average_residual(args,plotter)
    data_backup=copy.deepcopy(args.data)
    args.data=args.data_average
    data_shape_backup=copy.deepcopy(args.data_shape)
    args.data_shape=args.data_shape_average
    args.data_average_decompressed=apply_topology(args,topology_manager,part_name="average")
    args.data=data_backup
    args.data_shape=data_shape_backup
    ########压缩residual_data########
    get_actual_residual_data(args)
    data_backup=copy.deepcopy(args.data)
    args.data=args.data_residual
    if args.method_residual==[]:
        args.data_residual_decompressed=apply_topology2(args,part_name="residual")
    else:
        args.data_residual_decompressed=apply_topology(args,topology_manager,part_name="residual")
    args.data=data_backup
    args.data_decompressed=add_average_and_residual_data(args)
args.data=args.data_min+(args.data+1)*(args.data_max-args.data_min)/2
args.data_decompressed=args.data_min+(args.data_decompressed+1)*(args.data_max-args.data_min)/2
max_err=(args.data-args.data_decompressed).abs().max().item()
print(f"max_err={max_err}",flush=True)
print(f"data_max-data_min={args.data_max-args.data_min}",flush=True)
mse=((args.data-args.data_decompressed)**2).mean().item()
psnr=10*math.log10((args.data_max-args.data_min)**2/mse)
print(f"psnr= {psnr:.6f}",flush=True)
with open(args.data_path+".fhde.bin","wb") as f:
    args.data_decompressed.numpy().tofile(f)
calculateSSIM_command=f"calculateSSIM -f {args.data_path} {args.data_path}.fhde.bin {args.data_shape[2]} {args.data_shape[1]} {args.data_shape[0]}"
calculateSSIM_ouput=subprocess.check_output(calculateSSIM_command,shell=True,encoding="utf-8")
ssim=float(calculateSSIM_ouput.strip().split("\n")[-1].split()[-1])
print(f"ssim= {ssim:.6f}",flush=True)
if not args.doughnut:
    compressQuantBins_command=f"compressQuantBins {os.path.join(args.project_root,'qb',f'{args.data_name}.qb')}"
    compressQuantBins_output=subprocess.check_output(compressQuantBins_command,shell=True,encoding="utf-8")
    cr=float(compressQuantBins_output.strip().split("\n")[-3].split()[-1])
else:
    # bitstream_length_average=os.path.getsize("data_generated/average.bin.sz3")
    # bitstream_length_residual=os.path.getsize("data_generated/residual.bin.sz3")
    # cr=(args.data_shape[0]*args.data_shape[1]*args.data_shape[2]*4)/(bitstream_length_average+bitstream_length_residual)
    compressQuantBins_command=f"compressQuantBins qb/{args.data_name}_average.bin"
    compressQuantBins_output=subprocess.check_output(compressQuantBins_command,shell=True,encoding="utf-8")
    bitstream_length_average=int(compressQuantBins_output.strip().split("\n")[-3].split()[-5])
    compressQuantBins_command=f"compressQuantBins qb/{args.data_name}_residual.bin"
    compressQuantBins_output=subprocess.check_output(compressQuantBins_command,shell=True,encoding="utf-8")
    bitstream_length_residual=int(compressQuantBins_output.strip().split("\n")[-3].split()[-5])
    print(f"bitstream_length_average= {bitstream_length_average}",flush=True)
    print(f"bitstream_length_residual= {bitstream_length_residual}",flush=True)
    cr=(args.data_shape[0]*args.data_shape[1]*args.data_shape[2]*4)/(bitstream_length_average+bitstream_length_residual)
    
print(f"cr= {cr:.6f}",flush=True)
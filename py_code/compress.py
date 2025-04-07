import torch,math,copy,subprocess,os
from args import args_c
from plot_py import plot_c
from read_dataset import read_dataset
from stencil_manager import stencil_manager_c
from search_stencil_tools import apply_stencil,apply_topology2
from separate_diffraction_average_residual import separate_diffraction_average_residual,get_actual_residual_data,add_average_and_residual_data
from huffman import huffman_encode
import zstandard as zstd
from bitarray import bitarray

torch.set_num_threads(8)
args=args_c()
plotter=plot_c(args)
stencil_manager=stencil_manager_c()
read_dataset(args)
if not args.doughnut:
    apply_stencil(args,stencil_manager)
    data_bitstream_after_huffman=huffman_encode(args.qb[:args.qb_end].numpy().tolist())
    args.parameter=torch.cat(args.parameter)
    param_bitstream_after_huffman=huffman_encode(args.parameter.numpy().tolist())
    pivot_bitstream=bitarray()
    pivot_bitstream.frombytes(args.pivot[0:args.pivot_num].numpy().tobytes())
    bitstream_after_huffman=bitarray()
    bitstream_after_huffman.extend(format(args.pivot_num&0xFFFFFFFF,'032b'))
    bitstream_after_huffman.extend(pivot_bitstream)
    bitstream_after_huffman.extend(data_bitstream_after_huffman)
    bitstream_after_huffman.extend(param_bitstream_after_huffman)
    bitstream_after_huffman=bitstream_after_huffman.tobytes()
    cctx=zstd.ZstdCompressor()
    args.bitstream_after_zstd=cctx.compress(bitstream_after_huffman)
    print("pivot space=",args.pivot_num*4+4)
    print("data space=",args.data_shape[0]*args.data_shape[1]*args.data_shape[2]*4)
    print("data after huffman space=",len(data_bitstream_after_huffman.tobytes()))
    print("data huffman CR=",args.data_shape[0]*args.data_shape[1]*args.data_shape[2]*4/len(data_bitstream_after_huffman.tobytes()))
    print("parameter space=",args.parameter.size(0)*4)
    print("parameter after huffman space=",len(param_bitstream_after_huffman.tobytes()))
    print("parameter Huffman CR=",args.parameter.size(0)*4/len(param_bitstream_after_huffman.tobytes()))
    print("all after huffman space=",len(bitstream_after_huffman))
    print("Huffman CR=",args.data_shape[0]*args.data_shape[1]*args.data_shape[2]*4/len(bitstream_after_huffman))
    print("all after zstd space=",len(args.bitstream_after_zstd))
    print("Zstd CR=",len(bitstream_after_huffman)/len(args.bitstream_after_zstd))
    print("Total CR=",args.data_shape[0]*args.data_shape[1]*args.data_shape[2]*4/len(args.bitstream_after_zstd))
    
    sorted_parameter=torch.sort(args.parameter).values
    with open(os.path.join(args.project_root,"sorted_parameter.txt"),"w") as f:
        for i in range(sorted_parameter.size(0)):
            f.write(f"{sorted_parameter[i].item()}\n")
else:
    raise NotImplementedError
    ########压缩average_data########
    # separate_diffraction_average_residual(args,plotter)
    # data_backup=copy.deepcopy(args.data)
    # args.data=args.data_average
    # data_shape_backup=copy.deepcopy(args.data_shape)
    # args.data_shape=args.data_shape_average
    # args.data_average_decompressed=apply_topology(args,stencil_manager,part_name="average")
    # args.data=data_backup
    # args.data_shape=data_shape_backup
    ########压缩residual_data########
    # get_actual_residual_data(args)
    # data_backup=copy.deepcopy(args.data)
    # args.data=args.data_residual
    # if args.method_residual==[]:
    #     args.data_residual_decompressed=apply_topology2(args,part_name="residual")
    # else:
    #     args.data_residual_decompressed=apply_topology(args,stencil_manager,part_name="residual")
    # args.data=data_backup
    # args.data_decompressed=add_average_and_residual_data(args)
args.data=args.data_min+(args.data+1)*(args.data_max-args.data_min)/2
args.data_decompressed=args.data_min+(args.data_decompressed+1)*(args.data_max-args.data_min)/2
max_err=(args.data-args.data_decompressed).abs().max().item()
print(f"max_err={max_err}",flush=True)
print(f"data_max-data_min={args.data_max-args.data_min}",flush=True)
mse=((args.data-args.data_decompressed)**2).mean().item()
psnr=10*math.log10((args.data_max-args.data_min)**2/mse)
print(f"psnr= {psnr:.6f}",flush=True)
with open(args.data_compressed_path,"wb") as f:
    f.write(args.bitstream_after_zstd)
with open(args.data_decompressed_path,"wb") as f:
    args.data_decompressed.numpy().tofile(f)
calculateSSIM_command=f"calculateSSIM -f {args.data_path} {args.data_decompressed_path} {args.data_shape[2]} {args.data_shape[1]} {args.data_shape[0]}"
calculateSSIM_ouput=subprocess.check_output(calculateSSIM_command,shell=True,encoding="utf-8")
ssim=float(calculateSSIM_ouput.strip().split("\n")[-1].split()[-1])
print(f"ssim= {ssim:.6f}",flush=True)
import torch,math,os
from args import args_c
from plot_py import plot_c
from read_write_dataset import read_compressed_bitstream,write_dataset
from stencil_manager import stencil_manager_c
from stencil_functions.apply_stencil_decompress_1d import apply_stencil_decompress_1d
from stencil_functions.apply_stencil_decompress_2d import apply_stencil_decompress_2d
from stencil_functions.apply_stencil_decompress_3d import apply_stencil_decompress_3d
import zstandard as zstd
from bitarray import bitarray

available_thread_num=torch.get_num_threads()
print(f"Available threads: {available_thread_num}")
torch.set_num_threads((available_thread_num+1)//2)
print(f"Set threads to: {torch.get_num_threads()}")

args=args_c()
stencil_manager=stencil_manager_c(args)
read_compressed_bitstream(args)

if args.dim_num==3:
    apply_stencil_decompress_3d(args,stencil_manager)
elif args.dim_num==2:
    apply_stencil_decompress_2d(args,stencil_manager)
elif args.dim_num==1:
    apply_stencil_decompress_1d(args,stencil_manager)

write_dataset(args)
exit()

bs_huffman=huffman_encode(args.qb[:args.qb_end].numpy().tolist())
args.parameters=torch.cat(args.parameters)
param_bitstream_after_huffman=huffman_encode(args.parameters.numpy().tolist())
pivot_bitstream=bitarray()
pivot_bitstream.frombytes(args.pivot[0:args.pivot_num].numpy().tobytes())
bitstream_after_huffman=bitarray()
bitstream_after_huffman.extend(format(args.pivot_num&0xFFFFFFFF,'032b'))
bitstream_after_huffman.extend(pivot_bitstream)
bitstream_after_huffman.extend(bs_huffman)
bitstream_after_huffman.extend(param_bitstream_after_huffman)
bytestream_after_huffman=bitstream_after_huffman.tobytes()
cctx=zstd.ZstdCompressor()
args.zstd_bs=cctx.compress(bytestream_after_huffman)
print("Pivoting point space=",args.pivot_num*4+4,"bytes")
print("Data space=",args.data_shape[0]*args.data_shape[1]*args.data_shape[2]*4,"bytes")
print("Data after Huffman encoding space=",len(bs_huffman.tobytes()),"bytes")
print("Data Huffman CR=",args.data_shape[0]*args.data_shape[1]*args.data_shape[2]*4/len(bs_huffman.tobytes()))
print("Parameter space=",args.parameters.size(0)*4,"bytes")
print("Parameter after Huffman encoding space=",len(param_bitstream_after_huffman.tobytes()),"bytes")
print("Parameter Huffman CR=",args.parameters.size(0)*4/len(param_bitstream_after_huffman.tobytes()))
print("All after Huffman encoding space=",len(bytestream_after_huffman),"bytes")
print("All Huffman CR=",args.data_shape[0]*args.data_shape[1]*args.data_shape[2]*4/len(bytestream_after_huffman))
print("All after Zstd space=",len(args.zstd_bs),"bytes")
print("Zstd CR=",len(bytestream_after_huffman)/len(args.zstd_bs))
print("Total CR=",args.data_shape[0]*args.data_shape[1]*args.data_shape[2]*4/len(args.zstd_bs))

sorted_parameter=torch.sort(args.parameters).values
with open(os.path.join(args.project_root,"sorted_parameter.txt"),"w") as f:
    for i in range(sorted_parameter.size(0)):
        f.write(f"{sorted_parameter[i].item()}\n")
    
args.data=args.data_min+(args.data+1)*(args.data_max-args.data_min)/2
args.data_decompressed=args.data_min+(args.data_decompressed+1)*(args.data_max-args.data_min)/2
max_err=(args.data-args.data_decompressed).abs().max().item()
print(f"max_err={max_err}",flush=True)
print(f"data_max-data_min={args.data_max-args.data_min}",flush=True)
mse=((args.data-args.data_decompressed)**2).mean().item()
psnr=10*math.log10((args.data_max-args.data_min)**2/mse)
print(f"psnr= {psnr:.6f}",flush=True)
with open(args.data_compressed_path,"wb") as f:
    f.write(args.zstd_bs)
with open(args.data_decompressed_path,"wb") as f:
    args.data_decompressed.numpy().tofile(f)
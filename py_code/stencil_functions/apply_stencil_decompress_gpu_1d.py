import os,torch,struct,math
import numpy as np
from dahuffman import HuffmanCodec
from itertools import product
import zstandard as zstd
from args import args_c
from stencil_manager import stencil_manager_c
from stencil_functions.expand_data import expand_data_3d
from stencil_functions.blockify import blockify_3d
from stencil_functions.generate_cur_block_ext import generate_cur_block_ext_3d
from stencil_functions.generate_matAB import generate_matAB_3d
from read_write_dataset import read_dataset,restore_data_range

def apply_stencil_decompress_gpu_1d(args:args_c,stencil_manager:stencil_manager_c):
    raise NotImplementedError("GPU 1D decompression is not implemented yet.")
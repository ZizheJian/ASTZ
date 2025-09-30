import os,torch,huffman,struct,math
import numpy as np
from itertools import product
from bitarray import bitarray
import zstandard as zstd
from args import args_c
from stencil_manager import stencil_manager_c
from stencil_functions.expand_data import expand_data_3d
from stencil_functions.blockify import blockify_3d
from stencil_functions.generate_cur_block_ext import generate_cur_block_ext_3d
from stencil_functions.generate_matAB import generate_matAB_3d
from quantize import quantize_tensor,quantize_parameter_with_baseline

def apply_stencil_decompress_1d(args:args_c,stencil_manager:stencil_manager_c):
    raise NotImplementedError("1D decompression is not implemented yet.")
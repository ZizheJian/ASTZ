#首先指定数据的编号列表和网络的编号列表，然后比较数据使用自己的网络最好的效果和使用其他网络最好的效果

import torch,copy,subprocess,re,ast,math,os
import numpy as np
from torch import nn,optim
from torch.nn import functional as F
from args import args_c
from read_dataset import read_dataset
from quantize import quantize
from plot_py import plot_c
from eb_cr import choose_eb_power_list
from model import create_model,model_train
from print_zir import print_zir,print_zir_fast
from search_mask_and_baseline_core import search_mask_and_baseline_core
from blockify import blockify

torch.set_num_threads(8)
data_id_list=[0,1,2]
model_id_list=[0,1,2]
args=args_c()
plotter=plot_c(args)
read_dataset(args)
criteria=nn.MSELoss()

tgt_data=copy.deepcopy(args.data).unsqueeze(1)
for mask,baseline_core in search_mask_and_baseline_core(tgt_data.shape):
    cur_data=F.conv2d(tgt_data,baseline_core,padding=tuple([i//2 for i in baseline_core.shape[2:]]))
    cur_data[~mask]=tgt_data[~mask]
    best_self_sqrtmsqb=[1e9]*len(data_id_list)
    best_self_layer=[0]*len(data_id_list)
    bear_self_range_fix=[0]*len(data_id_list)
    best_corr_sqrtmsqb=[1e9]*len(data_id_list)
    best_corr_layer=[0]*len(data_id_list)
    best_corr_range_fix=[0]*len(data_id_list)
    for data_id in data_id_list:
        cur_block=cur_data[data_id:data_id+1]
        tgt_block=tgt_data[data_id:data_id+1]
        mask_block=mask[data_id:data_id+1]
        print(f"data_id={data_id}")
        for layer_power in list(range(5)):
            layer=2**layer_power
            model=torch.load(f"data_generated/xpcs/{data_id}/layer_{layer}.pth")
            print((criteria(model(cur_block)[mask_block],tgt_block[mask_block]).item()**0.5)/(2*args.abs_eb))
            with open(f"data_generated/xpcs/{data_id}/layer_{layer}.txt","r") as f:
                line=f.readlines()[0]
                range_fix_power=float(line.split()[0])
                sqrtmsqb=float(line.split()[1])
                range_fix=0.1**range_fix_power
            if sqrtmsqb<best_self_sqrtmsqb[data_id]:
                best_self_sqrtmsqb[data_id]=sqrtmsqb
                best_self_layer[data_id]=layer
                bear_self_range_fix[data_id]=range_fix
        print(f"best_self_layer={best_self_layer[data_id]}")
        print(f"best_self_range_fix={bear_self_range_fix[data_id]}")
        print(f"best_self_sqrtmsqb={best_self_sqrtmsqb[data_id]}")
        for model_id in model_id_list:
            if model_id==data_id:
                continue
            print(f"model_id={model_id}")
            for layer_power in list(range(5)):
                layer=2**layer_power
                print(f"layer={layer}")
                model=torch.load(f"data_generated/xpcs/{model_id}/layer_{layer}.pth")
                sqrtmsqb=(criteria(model(cur_block)[mask_block],tgt_block[mask_block]).item()**0.5)/(2*args.abs_eb)
                print(f"sqrtmsqb={sqrtmsqb}")
                if sqrtmsqb<best_corr_sqrtmsqb[data_id]:
                    best_corr_sqrtmsqb[data_id]=sqrtmsqb
                    best_corr_layer[data_id]=layer
                    best_corr_range_fix[data_id]=range_fix
        print(f"best_corr_layer={best_corr_layer[data_id]}")
        print(f"best_corr_range_fix={best_corr_range_fix[data_id]}")
        print(f"best_corr_sqrtmsqb={best_corr_sqrtmsqb[data_id]}")
        input()
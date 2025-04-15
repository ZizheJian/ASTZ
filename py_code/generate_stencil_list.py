import torch
from args import args_c
from read_dataset import read_dataset
from plot_py import plot_c
from search_stencil_tools import search_stencil
from stencil_manager import stencil_manager_c

torch.set_num_threads(8)
args=args_c()
plotter=plot_c(args)
stencil_manager=stencil_manager_c()
read_dataset(args)
# plotter.plot_data(args.data[0],args.data_name)
# exit()
search_stencil(args,stencil_manager)

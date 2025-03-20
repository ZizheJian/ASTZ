import torch
from args import args_c
from read_dataset import read_dataset
from plot_py import plot_c
from search_topology_tools import search_topology
from topology_manager import topology_manager_c
from separate_diffraction_average_residual import separate_diffraction_average_residual

torch.set_num_threads(8)
args=args_c()
plotter=plot_c(args)
topology_manager=topology_manager_c()
read_dataset(args)
if not args.doughnut:
    search_topology(args,topology_manager)
else:
    pass
    # separate_diffraction_average_residual(args,plotter)
    # data_backup=copy.deepcopy(args.data)
    # args.data=args.data_average
    # data_shape_backup=copy.deepcopy(args.data_shape)
    # args.data_shape=args.data_shape_average
    # search_topology(args,topology_manager,part_name="average")
    # args.data=data_backup
    # args.data_shape=data_shape_backup
    # if args.residual_baseline_method==[]:
    #     pass
    # else:
    #     data_backup=copy.deepcopy(args.data)
    #     args.data=args.data_residual
    #     search_topology(args,topology_manager,part_name="residual")
    #     args.data=data_backup


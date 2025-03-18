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
plotter.plot_data(args.data[0],args.data_name)
if args.doughnut:
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
else:
    search_topology(args,topology_manager)

#ISABEL/P:
#eb=1e-2,   th=7,   rfnum=3,    fhde_cr=2634.698975,    fhde_psnr=55.590092,    fhde_ssim=0.893851
#                               hpez_cr=1155.241333,    hpez_psnr=60.823874,    hpez_ssim=0.979272
#                               sz3_cr=2298.163818,     sz3_psnr=53.968785,     sz3_ssim=0.930025
#eb=1e-3,   th=7,   rfnum=1,    fhde_cr=333.327789,     fhde_psnr=71.459065,    fhde_ssim=0.985095
#                               hpez_cr=312.701294,     hpez_psnr=75.108622,    hpez_ssim=0.995718
#                               sz3_cr=268.672760,      sz3_psnr=70.489531,     sz3_ssim=0.990323
#eb=1e-4,   th=18,  rfnum=7,    fhde_cr=49.339420,      fhde_psnr=87.929272,    fhde_ssim=0.999334
#                               hpez_cr=51.972595,      hpez_psnr=88.789082,    hpez_ssim=0.999499
#                               sz3_cr=40.016933,       sz3_psnr=87.068803,     sz3_ssim=0.999313

#EXAFEL:
#eb=1e-2,   th=2,               fhde_cr=69.579140,      fhde_psnr=47.251118,    fhde_ssim=0.584669
#                               hpez_cr=48.529064,      hpez_psnr=46.992156,    hpez_ssim=0.662971   
#                               sz3_cr=47.341587,       sz3_psnr=46.356503,     sz3_ssim=0.598296
#eb=1e-3,   th=7,               fhde_cr=9.412062,       fhde_psnr=65.133070,    fhde_ssim=0.993043
#                               hpez_cr=9.160643,       hpez_psnr=64.814133,    hpez_ssim=0.992390
#                               sz3_cr=8.815522,        sz3_psnr=64.872521,     sz3_ssim=0.992496
#eb=1e-4,   th=9,               fhde_cr=4.694738,       fhde_psnr=85.122358,    fhde_ssim=0.999927
#                               hpez_cr=4.676123,       hpez_psnr=84.771873,    hpez_ssim=0.999921
#                               sz3_cr=4.617146,        sz3_psnr=84.834829,     sz3_ssim=0.999922

#NYX/baryon
#eb=1e-2,   th=3,               fhde_cr=88.729607,      fhde_psnr=47.976594,    fhde_ssim=0.955374
#                               hpez_cr=127.539017,     hpez_psnr=51.311496,    hpez_ssim=0.983513
#                               sz3_cr=92.054794,       sz3_psnr=47.666508,     sz3_ssim=0.953954
#eb=1e-3,   th=9,               fhde_cr=13.387239,      fhde_psnr=65.295603,    fhde_ssim=0.999154
#                               hpez_cr=19.305304,      hpez_psnr=65.177432,    hpez_ssim=0.999122
#                               sz3_cr=13.180675,       sz3_psnr=64.931589,     sz3_ssim=0.999064
#eb=1e-4,   th=31,              fhde_cr=5.576238,       fhde_psnr=85.099650,    fhde_ssim=0.999991
#                               hpez_cr=6.825794,       hpez_psnr=84.772510,    hpez_ssim=0.999990
#                               sz3_cr=5.661443,        sz3_psnr=84.822851,     sz3_ssim=0.999990

#xpcs-998x128x128
#eb=1e-2,   th_avg=7,   th_res=5,   rfnum=1,    fhde_cr=33.972880,      fhde_psnr=50.245174,    fhde_ssim=0.765754
#           th_avg=5,   th_res=5,   rfnum=2,    fhde_cr=33.747123,      fhde_psnr=50.333876,    fhde_ssim=0.770064
#           th_avg=7,               rfnum=1,    fhde_cr=34.539262,      fhde_psnr=50.120942,    fhde_ssim=0.758722
#                                               sep_sz3_cr=26.599252,   sep_sz3_psnr=49.053660, sep_sz3_ssim=0.622610
#                                               hpez_cr=28.890583,      hpez_psnr=49.046694,    hpez_ssim=0.698190
#                                               sz3_cr=28.891068,       sz3_psnr=48.068715,     sz3_ssim=0.611233
#eb=1e-3,   th_avg=5,   th_res=5,   rfnum=4,    fhde_cr=14.379839,      fhde_psnr=67.110449,    fhde_ssim=0.961680
#           th_avg=5,   th_res=5,   rfnum=1,    fhde_cr=14.274219,      fhde_psnr=67.124398,    fhde_ssim=0.963022
#           th_avg=5,               rfnum=1,    fhde_cr=13.284021,      fhde_psnr=65.764751,    fhde_ssim=0.932677
#                                               sep_sz3_cr=13.347449,   sep_sz3_psnr=68.139568, sep_sz3_ssim=0.975952
#                                               hpez_cr=15.439531,      hpez_psnr=72.440304,    hpez_ssim=0.989053
#                                               sz3_cr=19.258545,       sz3_psnr=76.038827,     sz3_ssim=0.996618
#eb=1e-4,   th_avg=3,   th_res=8,   rfnum=5,    fhde_cr=6.094972,       fhde_psnr=85.392112,    fhde_ssim=0.998004
#           th_avg=5,   th_res=5,   rfnum=1,    fhde_cr=5.783725,       fhde_psnr=85.677309,    fhde_ssim=0.999617
#           th_avg=3,               rfnum=1,    fhde_cr=6.745661,       fhde_psnr=84.837783,    fhde_ssim=0.998096
#                                               sep_sz3_cr=6.583867,    sep_sz3_psnr=85.803919, sep_sz3_ssim=0.999771
#                                               hpez_cr=12.077442,      hpez_psnr=89.213993,    hpez_ssim=0.999941
#                                               sz3_cr=17.341478,       sz3_psnr=88.012202,     sz3_ssim=0.999680

#Avg_L0470
#eb=1e-2,   th=12,  fhde_cr=3838.148926,    fhde_psnr=65.117022,    fhde_ssim=0.030408
#                   hpez_cr=3168.116211,    hpez_psnr=65.506478,    hpez_ssim=0.059536
#                   sz3_cr=3674.118748,     sz3_psnr=63.993585,     sz3_ssim=0.019021
#eb=1e-3,   th=4,   fhde_cr=346.330261,     fhde_psnr=76.123161,    fhde_ssim=0.168114
#                   hpez_cr=315.788544,     hpez_psnr=76.335232,    hpez_ssim=0.212530
#                   sz3_cr=337.292725,      sz3_psnr=74.578649,     sz3_ssim=0.136094
#eb=1e-4,   th=,    fhde_cr=6.643421,       fhde_psnr=85.392112,    fhde_ssim=0.998004
#                   hpez_cr=38.454533,      hpez_psnr=88.775551,    hpez_ssim=0.585355
#                   sz3_cr=39.585377,       sz3_psnr=87.889948,     sz3_ssim=0.518753

#APSU_TestData_004
#eb=1e-2,   th=4,   fhde_cr=517.092041,     fhde_psnr=60.652073,    fhde_ssim=0.610035
#                   hpez_cr=185.404953,     hpez_psnr=56.925469,    hpez_ssim=0.561100
#                   sz3_cr=116.316650,      sz3_psnr=54.572205,     sz3_ssim=0.491469
#eb=1e-3,   th=2,   fhde_cr=81.075806,      fhde_psnr=72.019621,    fhde_ssim=0.83924
#                   hpez_cr=43.198803,      hpez_psnr=73.375284,    hpez_ssim=0.870122
#                   sz3_cr=30.231087,       sz3_psnr=70.153330,     sz3_ssim=0.793982
#eb=1e-4,   th=4,   fhde_cr=3.330025,       fhde_psnr=78.459892,    fhde_ssim=0.000000
#                   hpez_cr=17.857512,      hpez_psnr=91.002153,    hpez_ssim=0.989429
#                   sz3_cr=12.875036,       sz3_psnr=88.626429,     sz3_ssim=0.977186

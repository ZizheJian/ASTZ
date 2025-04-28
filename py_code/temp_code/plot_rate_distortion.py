import numpy as np
import matplotlib.pyplot as plt

compressor_name_list=["ASTZ","SZ3","HPEZ","ZFP"]

########APSU########
# file_name="APSU_TestData_004.bin.txt"
# xlim=(0,5)
# psnr_ylim=(None,95)
########D0131_cut########
# file_name="D0131_US-Cup2_a0010_f005000_r00001_cut.bin.txt"
# xlim=(0,5)
# psnr_ylim=(None,50)
# ssim_ylim=(None,1)
########E017########
file_name="E017_CeramicGlass_L2Mq0_060C_att00_001_001.bin.txt"
xlim=(0,5)
psnr_ylim=(None,90)
########EXAFEL########
# file_name="SDRBENCH-EXAFEL-data-130x1480x1552.f32.txt"
# xlim=(0,8)
# psnr_ylim=(None,90)
# ssim_ylim=(None,1)
########xpcs-998########
# file_name="xpcs-998x128x128.bin.f32.txt"
# xlim=(0,1.25)
# psnr_ylim=(None,50)
# ssim_ylim=(None,0.9)

data=np.loadtxt(file_name)

plt.figure(figsize=(4,3))
for compressor_id in range(0,data.shape[1]//4):
    plt.plot(data[:,4*compressor_id+1]*2,data[:,4*compressor_id+2],label=compressor_name_list[compressor_id],linewidth=1)
plt.xlabel("Bitrate",fontsize=12)
try:
    plt.xlim(xlim)
except:
    pass
plt.xticks(fontsize=12)
plt.ylabel("PSNR",fontsize=12)
try:
    plt.ylim(psnr_ylim)
except:
    pass
plt.yticks(fontsize=12)
plt.legend(fontsize=12)
plt.tight_layout()
plt.savefig(f"{file_name}_psnr.png",dpi=300,bbox_inches='tight')

plt.figure(figsize=(4,3))
for compressor_id in range(0,data.shape[1]//4):
    plt.plot(data[:,4*compressor_id+1],data[:,4*compressor_id+3],label=compressor_name_list[compressor_id],linewidth=1)
plt.xlabel("Bitrate")
try:
    plt.xlim(xlim)
except:
    pass
plt.ylabel("SSIM")
try:
    plt.ylim(ssim_ylim)
except:
    pass
plt.legend(fontsize=12)
plt.tight_layout()
plt.savefig(f"{file_name}_ssim.png",dpi=300,bbox_inches='tight')
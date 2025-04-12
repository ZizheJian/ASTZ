import h5py
import numpy as np
import os, sys
import time
import matplotlib.pyplot as plt
import matplotlib.colors       as mcolors
import matplotlib.patches      as mpatches
import matplotlib.transforms   as mtransforms

snapshot_number = int(sys.argv[1]) - 1

# data_path = "../illumine-data/APS_DYS/xpcs_datasets/E017_CeramicGlass_L2Mq0_060C_att00_001/E017_CeramicGlass_L2Mq0_060C_att00_001_001.h5"
# data_path = "../illumine-data/APS_DYS/xpcs_datasets/E018_CeramicGlass_L2Mq0_060C_att00_001/E018_CeramicGlass_L2Mq0_060C_att00_001_001.h5"
# data_path = "../illumine-data/APS_DYS/xpcs_datasets/APSU_TestData_004/APSU_TestData_004.h5"
# data_path = "../illumine-data/APS_DYS/xpcs_datasets/APSU_TestData_006/APSU_TestData_006.h5"
# data_path = "../illumine-data/APS_DYS/xpcs_datasets/APSU_TestData_008/APSU_TestData_008.h5"
# data_path = "../illumine-data/APS_DYS/xpcs_datasets/APSU_TestData_010/APSU_TestData_010.h5"
# data_path = "../illumine-data/APS_DYS/9-ID_CSSI_data/benchmarkdata/Avg_L0470_Double_exp_elong_siemens_1p00sampit_0p05inplane_patch1_of1_part0_001.h5"
data_path="/anvil/projects/x-cis240192/x-zjian1/APS_DYS/9-ID_CSSI_data/benchmarkdata/Avg_L0470_Double_exp_elong_siemens_1p00sampit_0p05inplane_patch1_of1_part0_001.h5"
data_path="/anvil/projects/x-cis240192/x-zjian1/APS_DYS/9-ID_CSSI_data/benchmarkdata/Avg_L0471_Double_exp_elong_siemens_1p00sampit_0p05inplane_patch1_of1_part1_001.h5"

# Analyze data.
with h5py.File(data_path, 'r') as file:
    analysis_result = {}
    def analyze(name, obj):
        if isinstance(obj, h5py.Dataset):
            # Calculate the size in bytes
            size_bytes = obj.size * obj.dtype.itemsize
            # Convert bytes to gigabytes
            size_gb = size_bytes / (1024 ** 3)
            analysis_result[name] = {'shape': obj.shape, 'dtype': obj.dtype, 'size_gb': size_gb}
    file.visititems(analyze)
print("DATASET ANALYSIS:")
print("data path:" + data_path)
for element in analysis_result:
    print(f"{element}: {analysis_result[element]}")
print()

# Configure data into numpy array.
hf = h5py.File(data_path, 'r')
# raw = np.array(hf['entry/data/data'][:])
raw = np.array(hf['exchange/data'][:])

# Calculate sparsity.
print("DATASET SPARSITY:")
num_zeros = np.count_nonzero(raw == 0)
total_elements = raw.size
percentage_zeros = (num_zeros / total_elements) * 100
print(f"Percentage of zero elements: {percentage_zeros}%\n")


# # why outlier methods cannot work, profiling
# gain_bits      = 0b1100_0000_0000_0000
# intensity_bits = 0b0011_1111_1111_1111
# gain_state = raw & gain_bits
# intensity  = raw & intensity_bits
# data = intensity[99]
# percentage = np.sum(data > 200) / data.size
# print(percentage*100)
# percentage = np.sum(data > 500) / data.size
# print(percentage*100)
# percentage = np.sum(data > 1000) / data.size
# print(percentage*100)

# # Print image.
# print("PRINT GAIN and INTENSITY:")
# # First 2 bits characterize "gain state";  Rest 14 bits characterize intensity;
# gain_bits      = 0b1100_0000_0000_0000
# intensity_bits = 0b0011_1111_1111_1111
# gain_state = raw & gain_bits
# intensity  = raw & intensity_bits
# Visualize raw intensity, gain state and calibrated image...
panel_idx_list = [snapshot_number]
ncols = 1
nrows = 1
fig   = plt.figure(figsize = (4,4))
gspec = fig.add_gridspec(nrows, ncols)
ax_list = [ fig.add_subplot(gspec[i, j], aspect = 1) for i in range(nrows) for j in range(ncols)]    # Plain list
col_ofs = 0
for panel_idx in panel_idx_list:
    ax = ax_list[col_ofs]
    # data = intensity[panel_idx]
    data = raw[panel_idx]

    # Analyzing by yafan
    # data[data > 100] = 0
    mean_value = np.mean(data)
    median_value = np.median(data)
    std_deviation = np.std(data)
    non_zero_data = data[data != 0]  # Filter out zero values
    average_non_zero = np.mean(non_zero_data)  # Calculate the mean of non-zero values
    print(f"Average of non-zero data points: {average_non_zero}")
    print(f"Mean Value: {mean_value}")
    print(f"Median Value: {median_value}")
    print(f"Standard Deviation: {std_deviation}")
    print(f"Max data point: {data.max()}")
    print(f"Max data point: {data.min()}")


    vmin = 0
    vmax = 50
    ax.imshow(data, vmin = vmin, vmax = vmax)
    # ax.set_title('Raw (Intensity), Panel:' + str(panel_idx))
    ax.set_title('Intensity, Panel:' + str(panel_idx))
    col_ofs = col_ofs + 1
    # ax = ax_list[col_ofs]
    # data = gain_state[panel_idx]
    # vmin = data.mean()
    # vmax = data.mean() + 4 * data.std()
    # ax.imshow(data, vmin = vmin, vmax = vmax)
    # ax.set_title('Raw (Gain state), Panel:' + str(panel_idx))
    # col_ofs = col_ofs + 1
    # Apply style...
    for ax in ax_list:
        ax.set_xticks([])
        ax.set_yticks([])
        # Hide the frame box
        ax.spines['top'   ].set_visible(False)
        ax.spines['right' ].set_visible(False)
        ax.spines['left'  ].set_visible(False)
        ax.spines['bottom'].set_visible(False)

    # Save the figure
    # fig.savefig("raw_figure_panel_" + str(panel_idx) + ".png", dpi=400, bbox_inches='tight')
    fig.savefig("APS-CSSI-" + str(panel_idx) + ".png", dpi=400, bbox_inches='tight')
    print("Saving pictures")
hf.close()
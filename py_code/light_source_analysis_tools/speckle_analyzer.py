"""
Author: Peco Myint
Last Edit: February 21, 2024
Description: This script profiles speckle quality
Dependencies:          python,  numpy,  matplotlib, h5py,   scipy   tqdm (optional)
corresponding versions: 3.8.18, 1.24.4, 3.7.3,      3.10.0, 1.10.1, 4.66.1
"""
import h5py
import matplotlib.pyplot as plt
import numpy as np
import time
#for plotting
from matplotlib.colors import LogNorm
from matplotlib.patches import Rectangle
from matplotlib.patches import FancyBboxPatch
from mpl_toolkits.axes_grid1 import make_axes_locatable

import crosscor
plt.rcParams.update({
    'font.size': 8,           
    'font.family': 'serif',    
    'axes.labelsize': 'small', 
    'axes.titlesize': 'medium' 
})

class Speckle_analyzer:
    def __init__(self, file_path, dataset_name):
        self.file_path    = file_path
        self.dataset_name = dataset_name
        read_time         = time.time()
        with h5py.File(self.file_path, 'r') as file:
            self.dataset  = np.rot90(file[self.dataset_name][()], k =1, axes=(2,1))#rotate to the right direction
        read_time         -= time.time()
        self.frame_index  = 4 
        profile_time      = time.time()
        self.dector_ROI   = (830,920,70,50)
        self.speckle_profile =  self.cross_corr(self.frame_index,self.frame_index,ROI =self.dector_ROI)     
        profile_time      -= time.time()
        print(
        "Contrast (Beta)                           :", self.speckle_profile[0]-1, "\n"
        "X-coordinate peak shift                   :", self.speckle_profile[1], "[pixels] \n"
        "Y-coordinate peak shift                   :", self.speckle_profile[2], "[pixels] \n"
        "FWHM of speckle along the x-axis          :", self.speckle_profile[3], "[pixels] \n"
        "FWHM of speckle along the y-axis          :", self.speckle_profile[4], "[pixels] \n"
        "HDF read time                             :", -1*read_time, "[s] \n"
        "Speckle profiling time                    :", -1*profile_time, "[s]"
        )
        
    def cross_corr(self, ref_frame_idx, compare_frame_idx, ROI):
        """_summary_

        Args:
            ref_frame_idx (int): frame number 
            compare_frame_idx (int): frame number 
            ROI (tuple): x_center (column in matplotlib), y_center(row in matplotlib), x_width, y_width. Defaults to (100,100,10,10).
        """
        self.ref_frame = self.dataset[ref_frame_idx]
        center_col, center_row, col_roi_width, row_roi_width = ROI
        col_slice = slice(max(0, center_col - col_roi_width // 2), min(self.ref_frame.shape[1], center_col + col_roi_width // 2))
        row_slice = slice(max(0, center_row - row_roi_width // 2), min(self.ref_frame.shape[0], center_row + row_roi_width // 2))
        
        # select ROIs and compute cross correlations
        ref_frame = self.ref_frame[row_slice, col_slice]
        cross_corr = crosscor.crosscor(ref_frame.shape,mask=None,normalization="symavg")
        ccr = cross_corr(ref_frame,self.dataset[compare_frame_idx][row_slice, col_slice])
        
        # self correlate (between two same frames) to get an average speckle shape
        p  = np.unravel_index(np.argmax(ccr, axis=None), ccr.shape)  # Position of max
        ax = (ccr[p[0] - 1, p[1]] + ccr[p[0] + 1, p[1]] - 2 * ccr[p[0], p[1]]) / 2. #curvature along x (row). second derivative 
        dx = (ccr[p[0] - 1, p[1]] - ccr[p[0] + 1, p[1]]) / 4. / ax # computes the displacement by taking the difference between the correlation values on either side of the peak and scales it by ax.
        ay = (ccr[p[0], p[1] - 1] + ccr[p[0], p[1] + 1] - 2 * ccr[p[0], p[1]]) / 2.
        dy = (ccr[p[0], p[1] - 1] - ccr[p[0], p[1] + 1]) / 4. / ay
        cy = ccr[p[0], p[1]] - ay * dy * dy
        cx = ccr[p[0], p[1]] - ax * dx * dx # represents the refined correlation value at the peak position

        # cropping to show speckle
        center_col, center_row, col_roi_width, row_roi_width = p[1],  p[0],  int(cy * 10) ,int(cx * 10)
        col_slice = slice(max(0, center_col - col_roi_width // 2), min(ref_frame.shape[1], center_col + col_roi_width // 2))
        row_slice = slice(max(0, center_row - row_roi_width // 2), min(ref_frame.shape[0], center_row + row_roi_width // 2))
        
        #results: 
        # 0. contrast (beta)
        # 1. the displacement along the x-axis
        # 2. the displacement along the y-axis
        # 3. FWHM width x = the standard deviation along the x-axis * 2.3548 
        # 4. FWHM width y = the standard deviation along the y-axis * 2.3548 
        # 5. speckle
        # 6. ref ROI on detector used for analysis
        # FWHM = 2.3548 * sigma
        result = [(cx+cy)/2, dx, dy, np.sqrt(-cx / 2 / ax) * 2.3548 , np.sqrt(-cy / 2 / ay) * 2.3548 , ccr[row_slice, col_slice], ref_frame]
        return result
    
    def plot_report(self):

        # Create a new figure and gridspec for the subplots
        fig = plt.figure(figsize=(10, 5))
        gs = fig.add_gridspec(4, 4, width_ratios=[0.8, 0.7, 0.8, 1.5])

        # Left Panel: Reference Frame
        ax1 = fig.add_subplot(gs[:, :2])
        ax1.imshow(self.ref_frame, cmap='viridis', aspect='auto', norm=LogNorm(vmin=0.9, vmax =100))
        ax1.set_title(f"Reference Frame No: {self.frame_index}")
        ax1.set_xlabel("X [pixels]")
        ax1.set_ylabel("Y [pixels]")
        # Add a dashed ROI box
        center_col, center_row, col_roi_width, row_roi_width = self.dector_ROI
        roi_rect = Rectangle((center_col - col_roi_width/2, center_row - row_roi_width/2), 
                            col_roi_width, row_roi_width, 
                            linestyle='-', edgecolor='red', fill=False)
        ax1.add_patch(roi_rect)
        ax1.text(center_col, center_row+row_roi_width*2, "ROI", fontsize=10, color='black', ha='center', va='center' , bbox=dict(boxstyle="round,pad=0.3", alpha=0.4, facecolor="white", edgecolor="black", linewidth=2))


        # Right Panel: Subplots
        ax4 = fig.add_subplot(gs[2:, 2])
        ax5 = fig.add_subplot(gs[:2, 2])
        ax2 = fig.add_subplot(gs[2:, 3])
        ax3 = fig.add_subplot(gs[:2, 3])


        # Subplot 2: ROI
        im =ax2.imshow(self.speckle_profile[6], cmap='viridis', aspect='auto', norm=LogNorm())
        ax2.set_title("Reference ROI")
        ax2.set_xlabel("X [pixels]")
        ax2.set_ylabel("Y [pixels]")
        cbar = plt.colorbar(im, ax=ax2)
        cbar.set_label('Intensity')

        # Subplot 3: Speckle
        toshow = self.speckle_profile[5]
        im = ax3.imshow(toshow, cmap='viridis', aspect='auto', norm=LogNorm())
        ax3.set_title("Speckle")
        ax3.set_xlabel("X [pixels]")
        ax3.set_ylabel("Y [pixels]")
        # Plot horizontal line cut at y value
        y_value = toshow.shape[0]//2
        ax3.axhline(y=y_value, color='red', alpha = 0.3, linestyle='--', label=f'Horizontal Cut')

        # Plot vertical line cut at x value
        x_value = toshow.shape[1]//2
        ax3.axvline(x=x_value, color='blue', alpha = 0.3, linestyle='--', label=f'Vertical Cut')

        
        cbar = plt.colorbar(im, ax=ax3, format = '%.1f')
        cbar.set_label('Correlation')
        ax3.legend()

        # Subplot 4: Horizontal Line Cut
        ax4.plot(toshow[toshow.shape[0]//2,:])
        ax4.set_title("Horizontal Line Cut")
        ax4.set_xlabel("Y [pixels]")
        ax4.set_ylabel("Contrast + 1 baseline")
        ax4.annotate(f"Speckle contrast={self.speckle_profile[0]-1:.2f},"+ 
                     f"\nSpeckle x shift={self.speckle_profile[1]:.2f},"+ 
                    f"\nSpeckle FWHM  = {self.speckle_profile[4]:.2f}",
                    xy=(0.05, 0.5), xycoords='axes fraction', ha='left', va='center',bbox=dict(boxstyle="round,pad=0.3", alpha=0.3, facecolor="white", edgecolor="black", linewidth=2))

        # Subplot 5: Vertical Line Cut
        ax5.plot(toshow[:, toshow.shape[1]//2])
        ax5.set_title("Vertical Line Cut")
        ax5.set_xlabel("X [pixels]")
        ax5.set_ylabel("Contrast + 1 baseline")
        # ax5.grid(True)
        ax5.annotate(f"Speckle contrast={self.speckle_profile[0]-1:.2f},"+ 
                     f"\nSpeckle y shift={self.speckle_profile[2]:.2f},"+ 
                    f"\nSpeckle FWHM  = {self.speckle_profile[3]:.2f}",
                    xy=(0.05,0.5), xycoords='axes fraction', ha='left', va='center',bbox=dict(boxstyle="round,pad=0.3", alpha=0.3, facecolor="white", edgecolor="black", linewidth=2))

        plt.tight_layout()
        plt.savefig('speckle_profile.pdf',dpi = 400)
        plt.show()
        


file_path = '/anvil/projects/x-cis240192/x-zjian1/APS_DYS/9-ID_CSSI_data/benchmarkdata/Avg_L0471_Double_exp_elong_siemens_1p00sampit_0p05inplane_patch1_of1_part1_001.h5'
dataset_name = "/exchange/data/"
speckle_analyzer = Speckle_analyzer(file_path, dataset_name)
#to use in your loss function
speckle_contrast, speckle_xshift, speckle_yshift, speckle_xwidth, speckle_ywidth = speckle_analyzer.speckle_profile[0]-1,speckle_analyzer.speckle_profile[1], speckle_analyzer.speckle_profile[2], speckle_analyzer.speckle_profile[3], speckle_analyzer.speckle_profile[4]
#to see the visual report
speckle_analyzer.plot_report()



#test below
# frame_index=2
# speckle_profile.cross_corr(frame_index,frame_index,ROI =(776,743,40,30),vset = (0.9,2), plot=True)

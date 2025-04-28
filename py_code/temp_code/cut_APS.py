import h5py,hdf5plugin
import numpy as np

with h5py.File("APSU_TestData_004.h5","r") as f:
    dataset=f["/entry/data/data"]
    for i0 in range(0,4):
        for i1 in range(0,4):
            for i2 in range(0,4):
                j0=i0*256
                j1=(i1*1168)//3
                j2=(i2*1359)//3
                block=dataset[j0:j0+256,j1:j1+390,j2:j2+454]
                block=np.array(block)
                print(i0,i1,i2,block.shape)
                block=block.astype(np.float32)
                block.tofile(f"APSU_TestData_004_cut.bin_{i0}{i1}{i2}")
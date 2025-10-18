import numpy as np

def calculate_predictability(data_path,data_type,data_shape):
    if data_type=="f32":
        data=np.fromfile(data_path,dtype=np.float32).astype(np.float32)
    elif data_type=="ui16":
        data=np.fromfile(data_path,dtype=np.uint16).astype(np.float32)
    data=data.reshape(data_shape)
    if len(data_shape)!=3:
        raise NotImplementedError("Only predictability calculation of 3D data is implemented.")
    data_max=data.max()
    data_min=data.min()
    data=2*(data-data_min)/(data_max-data_min)-1
    print((((data[:-2:2]+data[2::2])/2-data[1:-1:2])**2).mean())
    print((((data[:,:-2:2]+data[:,2::2])/2-data[:,1:-1:2])**2).mean())
    print((((data[:,:,:-2:2]+data[:,:,2::2])/2-data[:,:,1:-1:2])**2).mean())
from torch import Tensor
import numpy as np
from sklearn.decomposition import PCA

def print_pca(mat:Tensor):
    mat=mat.numpy()
    pca=PCA()
    pca.fit(mat)
    explained_var=pca.explained_variance_ratio_
    cumulative_var=np.cumsum(explained_var)
    threshold=0.95
    effective_rank=np.argmax(cumulative_var>=threshold)+1
    with open("pca.txt","a") as f:
        f.write(f"{mat.shape[1]}, {effective_rank}\n")
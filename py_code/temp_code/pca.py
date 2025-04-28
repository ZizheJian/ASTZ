import numpy as np
import matplotlib.pyplot as plt

data1=np.loadtxt("pca-1.txt", delimiter=",",dtype=int)
data6=np.loadtxt("pca-6.txt", delimiter=",",dtype=int)
data14=np.loadtxt("pca-14.txt", delimiter=",",dtype=int)
data=np.concatenate([data1,data6,data14],axis=0)
unique=np.unique(data[:,0])

param_num_list=[]
means=[]
stds=[]
for i in unique:
    mask=data[:,0]==i
    ranks=data[mask,1]
    mean=np.mean(ranks)
    std=np.std(ranks)
    if std>0:
        param_num_list.append(i)
        means.append(mean)
        stds.append(std)

plt.figure(figsize=(4,2))
plt.errorbar(param_num_list,means,yerr=stds,fmt="o-",capsize=5)
plt.xlabel("Amount of Data Available",fontsize=12)
plt.xticks(fontsize=12)
plt.ylabel("Effective Rank",fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True)
plt.tight_layout()
plt.savefig("pca.png")
plt.show()
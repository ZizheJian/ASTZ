import matplotlib.pyplot as plt
import numpy as np

def read_file(filepath):
    dict={}
    with open(filepath,'r') as file:
        for line in file:
            parts=line.strip().split()
            if len(parts)==2:
                dict[int(parts[0])]=int(parts[1])
    return dict

def plot_data(file_list):
    freq_dict_list=[read_file(file) for file in file_list]
    for i in range(len(file_list)):
        file_name=file_list[i]
        freq_dict=freq_dict_list[i]
        rmsqb=0
        num=0
        for qb,freq in freq_dict.items():
            rmsqb+=((qb-32768)**2)*freq
            num+=freq
        rmsqb=(rmsqb/num)**0.5
        print(file_name,"rmsqb=",rmsqb)
        print(file_name,"mse=",(rmsqb*0.002)**2)

    plt.figure(figsize=(8,2))
    for i in range(len(file_list)):
        file_name=file_list[i]
        freq_dict=freq_dict_list[i]
        plt.plot([i-32768 for i in freq_dict.keys()],np.array(list(freq_dict.values()))+1,label=file_name,linewidth=1)
    plt.xlim(-100,100)
    plt.xlabel("Bin",fontsize=12)
    plt.xticks(fontsize=12)
    plt.yscale('log')
    plt.ylim(1,)
    plt.ylabel("Frequency",fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(loc="upper right",fontsize=12)
    plt.grid(True,linestyle='--',alpha=0.6)
    plt.tight_layout()
    plt.savefig("EXAFEL_mse.png",dpi=300)

    sorted_freq_list_list=[sorted(freq_dict.values(),reverse=True) for freq_dict in freq_dict_list]
    for i in range(len(file_list)):
        file_name=file_list[i]
        sorted_freq_list=sorted_freq_list_list[i]
        rmsqb=0
        num=0
        for qb,freq in enumerate(sorted_freq_list):
            qb=(qb+1)//2
            rmsqb+=(qb**2)*freq
            num+=freq
        rmsqb=(rmsqb/num)**0.5
        print(file_name,"rmsqb=",rmsqb)
        print(file_name,"smse=",(rmsqb*0.002)**2)

    plt.figure(figsize=(8,2))
    for i in range(len(file_list)):
        file_name=file_list[i]
        sorted_freq_list=sorted_freq_list_list[i]
        plt.plot([i for i in range(len(sorted_freq_list))],np.array(sorted_freq_list)+1,label=file_name,linewidth=1)
    plt.xlim(0,100)
    plt.xlabel("Bin",fontsize=12)
    plt.yscale('log')
    plt.xticks(fontsize=12)
    plt.ylim(1,)
    plt.ylabel("Frequency",fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(loc="upper right",fontsize=12)
    plt.grid(True,linestyle='--',alpha=0.6)
    plt.tight_layout()
    plt.savefig("EXAFEL_smse.png",dpi=300)

file_list=["HPEZ.txt","SZ3.txt","ASZ.txt"]
plot_data(file_list)
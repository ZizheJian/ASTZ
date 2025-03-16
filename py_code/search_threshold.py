import subprocess,time,random,copy
from itertools import product
from pretrain import pretrain
from compress import compress

th_preset=[[5,0]]
th_valid=[True,False]
key_length=len(th_preset[0])
while True:
    threshold_dict={}
    with open("threshold.txt","r") as f:
        for line in f.readlines():
            splited_line=line.split(" ")
            key=tuple([int(i) for i in splited_line[0:key_length]])
            threshold_dict[key]=float(splited_line[key_length])
    if len(threshold_dict)==0:
        print("threshold.txt is empty")
        th=copy.deepcopy(th_preset[0])
    else:
        found_th_preset_not_tested=False
        for th in th_preset:
            if tuple(th) not in threshold_dict:
                found_th_preset_not_tested=True
                break
        if found_th_preset_not_tested:
            pass
        else:
            for index in range(len(threshold_dict)):
                th=[int(i) for i in list(threshold_dict.keys())[index]]
                print(f"index={index},th={th}")
                found_unsearched=False
                possible_directions=list(product([-1,0,1],repeat=key_length))
                possible_directions=[list(i) for i in possible_directions]
                possible_directions=[i for i in possible_directions if all([th_valid[j] or i[j]==0 for j in range(key_length)])]
                random.shuffle(possible_directions)
                for d_th in possible_directions:
                    new_th=[th[i]+d_th[i] for i in range(key_length)]
                    if tuple(new_th) not in threshold_dict and not found_unsearched and all([new_th[i]>0 or not th_valid[i] for i in range(key_length)]):
                        th=new_th
                        found_unsearched=True
                if not found_unsearched:
                    continue
                else:
                    break
    print(f"current th={th}")
    pretrain(*th)
    cr,psnr,ssim=compress(*th)
    threshold_dict[tuple(th)]=cr
    sorted_threshold_dict=sorted(threshold_dict.items(),key=lambda x:x[1],reverse=True)
    with open("threshold.txt","w") as f:
        for key,value in sorted_threshold_dict:
            for i in key:
                f.write(f"{i} ")
            f.write(f"{value}\n")
    print(f"th={th},cr={cr}")
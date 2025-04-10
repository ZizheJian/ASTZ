import os

threshold_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"threshold")
threshold_dict_dict={}
max_cr_dict={}
for file_name in os.listdir(threshold_path):
    file_path=os.path.join(threshold_path,file_name)
    threshold_dict_dict[file_name]={}
    with open(file_path,"r") as file:
        max_cr_dict[file_name]=float(file.readlines()[0].strip().split()[1])
        file.seek(0)
        for line in file.readlines():
            line=line.strip()
            if line:
                th,cr=line.split()
                th=int(th)
                cr=float(cr)
                threshold_dict_dict[file_name][th]=cr

best_th=0
best_score=0
for th in range(1,9):
    score=1
    for file_name in threshold_dict_dict.keys():
        if th not in threshold_dict_dict[file_name]:
            raise ValueError(f"Threshold {th} not found in file {file_name}")
        else:
            score*=(threshold_dict_dict[file_name][th]/max_cr_dict[file_name])
    if score>best_score:
        best_score=score
        best_th=th
    print(f"Threshold: {th}, Score: {score}")
print(f"Best threshold: {best_th}")
print(f"Best score: {best_score}")
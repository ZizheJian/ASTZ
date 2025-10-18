import itertools,torch

def check_stencil(stencil,ref_num):
    if stencil[0]!=0:
        return False
    if sum(stencil)!=ref_num:
        return False
    mask=torch.zeros((4,)*4,dtype=torch.bool)
    mask[1:3,1:3,1:3,1:3]=torch.tensor(stencil,dtype=torch.bool).reshape(2,2,2,2)
    mask[0]=mask[2]
    mask[3]=mask[1]
    mask[:,0]=mask[:,2]
    mask[:,3]=mask[:,1]
    mask[:,:,0]=mask[:,:,2]
    mask[:,:,3]=mask[:,:,1]
    mask[:,:,:,0]=mask[:,:,:,2]
    mask[:,:,:,3]=mask[:,:,:,1]
    # print(mask)
    mask_core=mask[0:3,0:3,0:3,0:3]
    match_num=0
    for center_pos in itertools.product([1,2],repeat=4):
        if mask[center_pos]!=0:
            continue
        if torch.equal(mask_core,mask[center_pos[0]-1:center_pos[0]+2,center_pos[1]-1:center_pos[1]+2,center_pos[2]-1:center_pos[2]+2,center_pos[3]-1:center_pos[3]+2]):
            match_num+=1
    # print(match_num==ref_num)
    # input()
    return match_num==ref_num

ret_list=[]

ref_num=8
num=0
for stencil in itertools.product([1,0],repeat=16):
    if not check_stencil(stencil,ref_num):
        continue
    ret_list.append(f"self.stencil_dict[8{num:03d}]=stencil_pattern_c(torch.tensor([[[[{stencil[0]},{stencil[1]}],[{stencil[2]},{stencil[3]}]],\
[[{stencil[4]},{stencil[5]}],[{stencil[6]},{stencil[7]}]]],[[[{stencil[8]},{stencil[9]}],[{stencil[10]},{stencil[11]}]],\
[[{stencil[12]},{stencil[13]}],[{stencil[14]},{stencil[15]}]]]],dtype=torch.bool))")
    num+=1

ref_num=4
num=0
for stencil in itertools.product([0,1],repeat=16):
    if not check_stencil(stencil,ref_num):
        continue
    ret_list.append(f"self.stencil_dict[4{num:03d}]=stencil_pattern_c(torch.tensor([[[[{stencil[0]},{stencil[1]}],[{stencil[2]},{stencil[3]}]],\
[[{stencil[4]},{stencil[5]}],[{stencil[6]},{stencil[7]}]]],[[[{stencil[8]},{stencil[9]}],[{stencil[10]},{stencil[11]}]],\
[[{stencil[12]},{stencil[13]}],[{stencil[14]},{stencil[15]}]]]],dtype=torch.bool))")
    num+=1

ref_num=2
num=0
for stencil in itertools.product([0,1],repeat=16):
    if not check_stencil(stencil,ref_num):
        continue
    ret_list.append(f"self.stencil_dict[2{num:03d}]=stencil_pattern_c(torch.tensor([[[[{stencil[0]},{stencil[1]}],[{stencil[2]},{stencil[3]}]],\
[[{stencil[4]},{stencil[5]}],[{stencil[6]},{stencil[7]}]]],[[[{stencil[8]},{stencil[9]}],[{stencil[10]},{stencil[11]}]],\
[[{stencil[12]},{stencil[13]}],[{stencil[14]},{stencil[15]}]]]],dtype=torch.bool))")
    num+=1

ref_num=1
num=0
for stencil in itertools.product([0,1],repeat=16):
    if not check_stencil(stencil,ref_num):
        continue
    ret_list.append(f"self.stencil_dict[1{num:03d}]=stencil_pattern_c(torch.tensor([[[[{stencil[0]},{stencil[1]}],[{stencil[2]},{stencil[3]}]],\
[[{stencil[4]},{stencil[5]}],[{stencil[6]},{stencil[7]}]]],[[[{stencil[8]},{stencil[9]}],[{stencil[10]},{stencil[11]}]],\
[[{stencil[12]},{stencil[13]}],[{stencil[14]},{stencil[15]}]]]],dtype=torch.bool))")
    num+=1
    
for line in ret_list:
    print(line)
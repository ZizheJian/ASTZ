import torch,copy,math,os
import numpy as np
from typing import Tuple,List
from itertools import product
from torch import Tensor
from torch.nn import functional as F
from args import args_c
from topology_manager import topology_manager_c
from blockify import blockify
from quantize import quantize,quantize_parameter
from shrink_data import shrink_data
from expand_data import expand_data

def any_pred_tgt_out_of_boundary_check(topology:Tensor,tgt_data:Tensor)->bool:
    any_pred_tgt_out_of_boundary:bool=False
    for i0,i1,i2 in product(range(0,2),repeat=3):
        if topology[i0,i1,i2] and (i0>=tgt_data.shape[2] or i1>=tgt_data.shape[3] or i2>=tgt_data.shape[4]):
            any_pred_tgt_out_of_boundary=True
            break
    return any_pred_tgt_out_of_boundary

def any_pred_tgt_processed_check(topology:Tensor,mask:Tensor)->bool:
    any_pred_tgt_processed:bool=False
    for i0,i1,i2 in product(range(0,2),repeat=3):
        if topology[i0,i1,i2] and i0<mask.shape[2] and i1<mask.shape[3] and i2<mask.shape[4] and mask[0,0,i0,i1,i2]==False:
            any_pred_tgt_processed=True
            break
    return any_pred_tgt_processed

def generate_cur_block_ext(cur_block:Tensor,mask_block:Tensor,args:args_c)->Tensor:
    cur_block_ext=torch.zeros(1,1+4,cur_block.shape[2],cur_block.shape[3],cur_block.shape[4])
    cur_block_ext[:,0:1]=cur_block
    cur_block_ext[:,1:1+4]=args.padded_pos[:,:,:cur_block.shape[2],:cur_block.shape[3],:cur_block.shape[4]]*mask_block[0,2:3]
    return cur_block_ext

def generate_mask_core(mask_block:Tensor,args:args_c,padding:int)->Tensor:
    mask_core=torch.zeros(1,1,3,3,3,dtype=torch.bool)
    i0_range=range(padding,min(padding+2,mask_block.shape[2]-padding))
    i1_range=range(padding,min(padding+2,mask_block.shape[3]-padding))
    i2_range=range(padding,min(padding+2,mask_block.shape[4]-padding))
    for i0,i1,i2 in product(i0_range,i1_range,i2_range):
        if mask_block[0,1,i0,i1,i2]:
            mask_core|=mask_block[:,0:1,i0-1:i0+2,i1-1:i1+2,i2-1:i2+2]
    simplified_mask_core=mask_core&torch.tensor([[[[0,0,0],[0,1,0],[0,0,0]],[[0,1,0],[1,0,1],[0,1,0]],[[0,0,0],[0,1,0],[0,0,0]]]],dtype=torch.bool)
    if simplified_mask_core.sum().item()>=args.min_reference_num:
        return simplified_mask_core
    simplified_mask_core=mask_core&torch.tensor([[[[0,1,0],[1,1,1],[0,1,0]],[[1,1,1],[1,0,1],[1,1,1]],[[0,1,0],[1,1,1],[0,1,0]]]],dtype=torch.bool)
    if simplified_mask_core.sum().item()>=args.min_reference_num:
        return simplified_mask_core
    return mask_core

def generate_mat_A_B(cur_block_ext:Tensor,tgt_block_cropped:Tensor,mask_block_cropped:Tensor,mask_core:Tensor,tgt_num:int,param_num:int)->Tuple[Tensor,Tensor]:
    mat_A=torch.zeros(tgt_num,param_num)
    mat_B=torch.zeros(tgt_num)
    ch_id=0
    for i0,i1,i2 in product(range(-1,2),repeat=3):
        if mask_core[0,0,i0+1,i1+1,i2+1]:
            mat_A[:,ch_id]=cur_block_ext[:,0:1,1+i0:cur_block_ext.shape[2]-1+i0,1+i1:cur_block_ext.shape[3]-1+i1,1+i2:cur_block_ext.shape[4]-1+i2][mask_block_cropped[:,1::2]]
            ch_id+=1
    for j in range(1,5):
        mat_A[:,ch_id]=cur_block_ext[:,j:1+j,1:-1,1:-1,1:-1][mask_block_cropped[:,1::2]]
        ch_id+=1
    mat_B=tgt_block_cropped[mask_block_cropped[:,1::2]]
    a=1e-10
    mat_A=torch.cat([mat_A,torch.eye(mat_A.shape[1])*(a**0.5)],dim=0)
    mat_B=torch.cat([mat_B,torch.zeros(mat_A.shape[1])],dim=0)
    return mat_A,mat_B

def decode_conv(mat_X:Tensor,mask_core:Tensor)->Tensor:
    conv=torch.zeros(1,5,3,3,3)
    ch_id=0
    for i0,i1,i2 in product(range(-1,2),repeat=3):
        if mask_core[0,0,i0+1,i1+1,i2+1]==False:
            continue
        conv[0,0,i0+1,i1+1,i2+1]=mat_X[ch_id]
        ch_id+=1
    for j in range(1,5):
        conv[0,j,1,1,1]=mat_X[ch_id]
        ch_id+=1
    return conv

def search_topology(args:args_c,topology_manager:topology_manager_c,part_name:str=""):
    if part_name=="":
        FHDE_threshold=args.FHDE_threshold
        mask_pos_file_name=os.path.join(args.project_root,"mask_pos",f"{args.data_name}.txt")
    elif part_name=="average":
        FHDE_threshold=args.FHDE_threshold_average
        mask_pos_file_name=os.path.join(args.project_root,f"mask_pos/{args.data_name}_average.txt")
    elif part_name=="residual":
        FHDE_threshold=args.FHDE_threshold_residual
        mask_pos_file_name=os.path.join(args.project_root,f"mask_pos/{args.data_name}_residual.txt")
    else:
        raise Exception("part_name参数错误")
    tgt_data=copy.deepcopy(args.data).unsqueeze(0).unsqueeze(0)
    mask=torch.zeros((1,2)+args.data.shape,dtype=torch.bool)#mask[0,0]表示在反向过程中尚未处理的数据，mask[0,1]表示正在处理的数据。mask_block[0,2]表示未出界数据
    mask[:,0]=True
    total_data_num=0
    with open(mask_pos_file_name,"w") as f:
        f.write("")
    for i in range((np.ceil(np.log2(args.data_shape[0]))+np.ceil(np.log2(args.data_shape[1]))+np.ceil(np.log2(args.data_shape[2]))).astype(int)):
        ########生成possible_topology_id_list########
        if mask[:,0,0:2,0:2,0:2].sum().item()==8:
            possible_topology_id_list=[x for x in topology_manager.topology_dict.keys() if 410<x<440]
        elif mask[:,0,0:2,0:2,0:2].sum().item()==4:
            possible_topology_id_list=[x for x in topology_manager.topology_dict.keys() if 210<x<270]
        elif mask[:,0,0:2,0:2,0:2].sum().item()==2:
            possible_topology_id_list=[x for x in topology_manager.topology_dict.keys() if 110<x<140]
        else:
            raise Exception("2*2*2区域内待处理数据量不是2的幂")
        abs_eb_backup=args.abs_eb
        args.abs_eb*=(0.95**i)
        ########搜索最佳topology########
        best_rmsqb:float=float("inf")#使用rmsqb是因为不同的step有不同的eb，所以不能直接用rmse
        best_topology_id:int=0
        best_mask:Tensor=torch.zeros_like(mask)
        for topology_id in possible_topology_id_list:
            topology=topology_manager.topology_dict[topology_id]
            if any_pred_tgt_out_of_boundary_check(topology,tgt_data):
                continue
            if any_pred_tgt_processed_check(topology,mask):
                continue
            for i0,i1,i2 in product(range(0,2),repeat=3):
                mask[0,0,i0::2,i1::2,i2::2]&=(~topology[i0,i1,i2])
                mask[0,1,i0::2,i1::2,i2::2]=topology[i0,i1,i2]
            cur_data=torch.zeros_like(tgt_data)
            cur_data[mask[:,0:1]]=tgt_data[mask[:,0:1]]
            rmsqb=0
            for block_id,cur_block,tgt_block,mask_block in blockify(cur_data,tgt_data,mask,args,padding=1):
                cur_block_ext=generate_cur_block_ext(cur_block,mask_block,args)
                tgt_block_cropped=tgt_block[:,:,1:-1,1:-1,1:-1]
                mask_block_cropped=mask_block[:,:,1:-1,1:-1,1:-1]
                if mask_block_cropped[0,1].sum().item()==0:
                    continue
                mask_core=generate_mask_core(mask_block,args,padding=1)
                tgt_num=mask_block_cropped[:,1::2].sum().item()
                param_num=mask_core.sum().item()+4
                if args.method=="HDE":
                    mat_A,mat_B=generate_mat_A_B(cur_block_ext,tgt_block_cropped,mask_block_cropped,mask_core,tgt_num,param_num)
                    lstsq_result=torch.linalg.lstsq(mat_A,mat_B,driver="gels")
                    mat_X=lstsq_result.solution
                    mat_X=quantize_parameter(mat_X,args)
                    err=mat_A@mat_X-mat_B
                    loss=((err**2).sum()/mat_B.shape[0])
                    rmsqb_block=(loss**0.5)/(2*args.abs_eb)
                    rmsqb+=(rmsqb_block**2)*tgt_num
                if args.method=="FHDE":
                    mat_A,mat_B=generate_mat_A_B(cur_block_ext,tgt_block_cropped,mask_block_cropped,mask_core,tgt_num,param_num)
                    lstsq_result=torch.linalg.lstsq(mat_A,mat_B,driver="gels")
                    mat_X=lstsq_result.solution
                    err=mat_A[:-param_num]@mat_X-mat_B[:-param_num]
                    valid_equations=(err.abs()<=args.abs_eb*FHDE_threshold)
                    if valid_equations.sum().item()>0:
                        mat_A_filtered=torch.cat((mat_A[:-param_num][valid_equations],mat_A[-param_num:]),dim=0)
                        mat_B_filtered=torch.cat((mat_B[:-param_num][valid_equations],mat_B[-param_num:]),dim=0)
                        lstsq_result=torch.linalg.lstsq(mat_A_filtered,mat_B_filtered,driver="gels")
                        mat_X=lstsq_result.solution
                    else:
                        mat_X=quantize_parameter(torch.cat((torch.ones(mask_core.sum().item())/mask_core.sum().item(),torch.zeros(4))),args)
                    mat_X=quantize_parameter(mat_X,args)
                    err=mat_A@mat_X-mat_B
                    loss=((err**2).sum()/mat_B.shape[0])
                    rmsqb_block=(loss**0.5)/(2*args.abs_eb)
                    rmsqb+=(rmsqb_block**2)*mask_block_cropped[:,1::2].sum().item()
            rmsqb=(rmsqb/(mask[:,1::2].sum().item()))**0.5
            print(f"topology={topology_id}, sqrtmsqb={rmsqb}")
            if best_rmsqb>rmsqb:
                best_rmsqb=rmsqb
                best_topology_id=topology_id
                best_mask[:]=mask[:]
            for i0,i1,i2 in product(range(0,2),repeat=3):
                mask[0,0,i0::2,i1::2,i2::2]|=topology[i0,i1,i2]
                mask[0,1,i0::2,i1::2,i2::2]=False
        ########保存最佳topology########
        topology_id=best_topology_id
        mask=best_mask
        with open(mask_pos_file_name,"a") as f:
            f.write(f"{tgt_data.shape[2]} {tgt_data.shape[3]} {tgt_data.shape[4]} {topology_id}\n")
        total_data_num+=mask[:,1::2].sum().item()
        tgt_data[mask[:,1:2]]=0
        mask[0,1]=False
        tgt_data,mask=shrink_data(tgt_data,mask,args)
        print(tgt_data[0,0,0:3,0:3,0:3])
        print(mask[0,0,0:3,0:3,0:3])
        print(tgt_data.shape,mask.shape,args.data_shape)
        args.abs_eb=abs_eb_backup
    total_data_num+=1
    print(f"total_data_num={total_data_num}")

def apply_topology1(args:args_c,topology_manager:topology_manager_c,part_name:str=""):
    if part_name=="":
        FHDE_threshold=args.FHDE_threshold
        mask_pos_file_name=os.path.join(args.project_root,f"mask_pos/{args.data_name}.txt")
        qb_file_name=os.path.join(args.project_root,"qb",f"args.data_name.qb")
        freq_file_name=os.path.join(args.project_root,f"freq/{args.data_name}.txt")
    elif part_name=="average":
        FHDE_threshold=args.FHDE_threshold_average
        mask_pos_file_name=f"/home/x-zjian1/jzzz/mask_pos/{args.data_name}_average.txt"
        qb_file_name=f"/home/x-zjian1/jzzz/qb/{args.data_name}_average.bin"
        freq_file_name=f"/home/x-zjian1/jzzz/freq/{args.data_name}_average.txt"
    elif part_name=="residual":
        FHDE_threshold=args.FHDE_threshold_residual
        mask_pos_file_name=f"/home/x-zjian1/jzzz/mask_pos/{args.data_name}_residual.txt"
        qb_file_name=f"/home/x-zjian1/jzzz/qb/{args.data_name}_residual.bin"
        freq_file_name=f"/home/x-zjian1/jzzz/freq/{args.data_name}_residual.txt"
    else:
        raise Exception("part_name参数错误")
    print(f"FHDE_threshold={FHDE_threshold}")
    args.cur_shape_list=[]
    args.topology_id_list=[]
    with open(mask_pos_file_name,"r") as f:
        for line in f:
            args.cur_shape_list.append([int(line.split()[0]),int(line.split()[1]),int(line.split()[2])])
            args.topology_id_list.append(int(line.split()[3]))
    cur_data=torch.zeros([1,1,1,1,1],dtype=torch.float32)
    tgt_data=torch.zeros([1,1,1,1,1],dtype=torch.float32)
    cur_data[0,0,0,0,0]=tgt_data[0,0,0,0,0]=args.data[0,0,0]
    mask=torch.zeros([1,2,1,1,1],dtype=torch.bool)
    mask[0,1,0,0,0]=True
    args.qb=torch.zeros(args.data_shape[0]*args.data_shape[1]*args.data_shape[2],dtype=torch.int32)
    args.qb_begin=args.qb_end=0
    pred_gap=[2**math.ceil(np.log2(args.data_shape[i])) for i in range(3)]
    pivot_num=args.data_shape[0]*args.data_shape[1]*args.data_shape[2]/pred_gap[0]/pred_gap[1]/pred_gap[2]
    for i in range(len(args.topology_id_list)-1,-1,-1):
        cur_shape=args.cur_shape_list[i]
        topology_id=args.topology_id_list[i]
        topology=topology_manager.topology_dict[topology_id]
        cur_data,tgt_data,mask,pred_gap=expand_data(cur_data,tgt_data,mask,pred_gap,args,cur_shape,topology)
        if mask.sum().item()<pivot_num:
            cur_data[mask[:,1:2]]=tgt_data[mask[:,1:2]]
            mask[:,0:1]+=mask[:,1:2]
            mask[:,1:2]=False
            continue
        abs_eb_backup=args.abs_eb
        args.abs_eb*=(0.95**i)
        for block_id,cur_block,tgt_block,mask_block in blockify(cur_data,tgt_data,mask,args,padding=1):
            cur_block_ext=generate_cur_block_ext(cur_block,mask_block,args)
            cur_block_cropped=cur_block_ext[:,0:1,1:-1,1:-1,1:-1]
            tgt_block_cropped=tgt_block[:,:,1:-1,1:-1,1:-1]
            mask_block_cropped=mask_block[:,:,1:-1,1:-1,1:-1]
            if mask_block_cropped[0,1].sum().item()==0:
                continue
            mask_core=generate_mask_core(mask_block,args,padding=1)
            tgt_num=mask_block_cropped[:,1::2].sum().item()
            param_num=mask_core.sum().item()+4
            if args.method=="HDE":
                mat_A,mat_B=generate_mat_A_B(cur_block_ext,tgt_block_cropped,mask_block_cropped,mask_core)
                lstsq_result=torch.linalg.lstsq(mat_A,mat_B,driver="gels")
                mat_X=lstsq_result.solution
                mat_X=quantize_parameter(mat_X,args)
                err=mat_A@mat_X-mat_B
                conv=decode_conv(mat_X,mask_core)
                h=F.conv3d(cur_block_ext,conv)
            if args.method=="FHDE":
                mat_A,mat_B=generate_mat_A_B(cur_block_ext,tgt_block_cropped,mask_block_cropped,mask_core,tgt_num,param_num)
                lstsq_result=torch.linalg.lstsq(mat_A,mat_B,driver="gels")
                mat_X=lstsq_result.solution
                err=mat_A[:-param_num]@mat_X-mat_B[:-param_num]
                valid_equations=(err.abs()<=args.abs_eb*FHDE_threshold)
                if valid_equations.sum().item()>0:
                    mat_A_filtered=torch.cat((mat_A[:-param_num][valid_equations],mat_A[-param_num:]),dim=0)
                    mat_B_filtered=torch.cat((mat_B[:-param_num][valid_equations],mat_B[-param_num:]),dim=0)
                    lstsq_result=torch.linalg.lstsq(mat_A_filtered,mat_B_filtered,driver="gels")
                    mat_X=lstsq_result.solution
                else:
                    mat_X=quantize_parameter(torch.cat((torch.ones(mask_core.sum().item())/mask_core.sum().item(),torch.zeros(4))),args)
                conv=decode_conv(mat_X,mask_core)
                conv=quantize_parameter(conv,args)
                h=F.conv3d(cur_block_ext,conv)
            quantize(tgt_block_cropped-h,mask_block_cropped[:,1::2],args.abs_eb,args)
            cur_block_cropped[mask_block_cropped[:,1::2]]=h[mask_block_cropped[:,1::2]]+args.qb[args.qb_begin:args.qb_end]*2*args.abs_eb
            cur_data[:,:,block_id[0]:block_id[0]+args.model_block_step[0],
                        block_id[1]:block_id[1]+args.model_block_step[1],
                        block_id[2]:block_id[2]+args.model_block_step[2]]=cur_block_cropped
        mask[:,0:1]+=mask[:,1:2]
        print(tgt_data.shape)
        args.abs_eb=abs_eb_backup
    print(f"qb_num={args.qb_end}")
    print(f"qb_min={args.qb.min().item()}, qb_max={args.qb.max().item()}")
    with open(qb_file_name,"wb") as f:
        (args.qb+32768).numpy().tofile(f)
    freq=torch.bincount(args.qb+32768,minlength=65536)
    with open(freq_file_name,"w") as f:
        for i in range(65536):
            f.write(str(i)+" "+str(freq[i].item())+"\n")
    max_err=(tgt_data-cur_data).abs().max().item()
    print(f"max_err={max_err}")
    return cur_data[0,0]

def apply_topology2(args:args_c,part_name:str):
    args.qb=torch.zeros(args.data_shape[0]*args.data_shape[1]*args.data_shape[2],dtype=torch.int32)
    args.qb_begin=args.qb_end=0
    quantize(args.data,torch.ones_like(args.data,dtype=torch.bool),args.abs_eb,args)
    cur_data=torch.zeros_like(args.data)
    cur_data+=args.qb[args.qb_begin:args.qb_end].reshape(args.data_shape)*2*args.abs_eb
    print(f"qb_num={args.qb_end}")
    print(f"qb_min={args.qb.min().item()}, qb_max={args.qb.max().item()}")
    with open(f"/home/x-zjian1/jzzz/qb/{args.data_name}_{part_name}.bin","wb") as f:
        (args.qb+32768).numpy().tofile(f)
    freq=torch.bincount(args.qb+32768,minlength=65536)
    with open(f"/home/x-zjian1/jzzz/freq/{args.data_name}_{part_name}.txt","w") as f:
        for i in range(65536):
            f.write(str(i)+" "+str(freq[i].item())+"\n")
    max_err=(args.data-cur_data).abs().max().item()
    print(f"max_err={max_err}")
    return cur_data

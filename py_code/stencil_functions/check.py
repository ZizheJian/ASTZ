from torch import Tensor
from typing import Tuple
from itertools import product

def num_of_reference_points_mismatch_check_3d(ref_pos:Tensor,mask:Tensor)->bool:
    return mask[:,:,0:2,0:2,0:2].sum().item()!=ref_pos.sum().item()*2

def num_of_reference_points_mismatch_check_2d(ref_pos:Tensor,mask:Tensor)->bool:
    return mask[:,:,0:2,0:2].sum().item()!=ref_pos.sum().item()*2

def any_pred_tgt_out_of_boundary_check_3d(stencil:Tensor,tgt_data_shape:Tuple[int])->bool:
    any_pred_tgt_out_of_boundary:bool=False
    for i0,i1,i2 in product(range(0,2),repeat=3):
        if stencil[i0,i1,i2] and (i0>=tgt_data_shape[2] or i1>=tgt_data_shape[3] or i2>=tgt_data_shape[4]):
            any_pred_tgt_out_of_boundary=True
            break
    return any_pred_tgt_out_of_boundary

def any_pred_tgt_out_of_boundary_check_2d(stencil:Tensor,tgt_data_shape:Tuple[int])->bool:
    any_pred_tgt_out_of_boundary:bool=False
    for i0,i1 in product(range(0,2),repeat=2):
        if stencil[i0,i1] and (i0>=tgt_data_shape[2] or i1>=tgt_data_shape[3]):
            any_pred_tgt_out_of_boundary=True
            break
    return any_pred_tgt_out_of_boundary

def any_pred_tgt_processed_check_3d(stencil:Tensor,mask:Tensor)->bool:
    any_pred_tgt_processed:bool=False
    for i0,i1,i2 in product(range(0,2),repeat=3):
        if stencil[i0,i1,i2] and i0<mask.shape[2] and i1<mask.shape[3] and i2<mask.shape[4] and mask[0,0,i0,i1,i2]==False:
            any_pred_tgt_processed=True
            break
    return any_pred_tgt_processed

def any_pred_tgt_processed_check_2d(stencil:Tensor,mask:Tensor)->bool:
    any_pred_tgt_processed:bool=False
    for i0,i1 in product(range(0,2),repeat=2):
        if stencil[i0,i1] and i0<mask.shape[2] and i1<mask.shape[3] and mask[0,0,i0,i1]==False:
            any_pred_tgt_processed=True
            break
    return any_pred_tgt_processed

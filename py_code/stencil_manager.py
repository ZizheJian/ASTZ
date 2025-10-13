import torch
from torch import Tensor
from args import args_c

class stencil_pattern_c():
    def __init__(self,pattern:Tensor)->None:
        self.ref_pos:Tensor=pattern # 1 indicates the positions with available values
        self.mask_core:Tensor=None # 1 indicates the positions with available values

class stencil_manager_c():
    def __init__(self,args:args_c)->None:
        if args.dim_num==3:
            if args.interpolation_method=="linear":
                self.r1_mask=torch.tensor([[[0,0,0],[0,1,0],[0,0,0]],[[0,1,0],[1,0,1],[0,1,0]],[[0,0,0],[0,1,0],[0,0,0]]],dtype=torch.bool)
                self.r2_mask=torch.tensor([[[0,1,0],[1,1,1],[0,1,0]],[[1,1,1],[1,0,1],[1,1,1]],[[0,1,0],[1,1,1],[0,1,0]]],dtype=torch.bool)
                self.r3_mask=torch.ones((3,3,3),dtype=torch.bool)
            elif args.interpolation_method=="cubic":
                raise NotImplementedError(f"Haven't implemented radius masks for cubic interpolation yet.")
            self.stencil_dict:dict[int,stencil_pattern_c]={}
            self.stencil_dict[411]=stencil_pattern_c(torch.tensor([[[0,1],[0,1]],[[0,1],[0,1]]],dtype=torch.bool))
            self.stencil_dict[412]=stencil_pattern_c(torch.tensor([[[0,0],[1,1]],[[0,0],[1,1]]],dtype=torch.bool))
            self.stencil_dict[413]=stencil_pattern_c(torch.tensor([[[0,0],[0,0]],[[1,1],[1,1]]],dtype=torch.bool))
            self.stencil_dict[421]=stencil_pattern_c(torch.tensor([[[0,1],[1,0]],[[0,1],[1,0]]],dtype=torch.bool))
            self.stencil_dict[422]=stencil_pattern_c(torch.tensor([[[0,1],[0,1]],[[1,0],[1,0]]],dtype=torch.bool))
            self.stencil_dict[423]=stencil_pattern_c(torch.tensor([[[0,0],[1,1]],[[1,1],[0,0]]],dtype=torch.bool))
            self.stencil_dict[431]=stencil_pattern_c(torch.tensor([[[0,1],[1,0]],[[1,0],[0,1]]],dtype=torch.bool))
            self.stencil_dict[211]=stencil_pattern_c(torch.tensor([[[0,1],[0,1]],[[0,0],[0,0]]],dtype=torch.bool))
            self.stencil_dict[212]=stencil_pattern_c(torch.tensor([[[0,1],[0,0]],[[0,1],[0,0]]],dtype=torch.bool))
            self.stencil_dict[213]=stencil_pattern_c(torch.tensor([[[0,0],[1,1]],[[0,0],[0,0]]],dtype=torch.bool))
            self.stencil_dict[214]=stencil_pattern_c(torch.tensor([[[0,0],[1,0]],[[0,0],[1,0]]],dtype=torch.bool))
            self.stencil_dict[215]=stencil_pattern_c(torch.tensor([[[0,0],[0,0]],[[1,1],[0,0]]],dtype=torch.bool))
            self.stencil_dict[216]=stencil_pattern_c(torch.tensor([[[0,0],[0,0]],[[1,0],[1,0]]],dtype=torch.bool))
            self.stencil_dict[221]=stencil_pattern_c(torch.tensor([[[0,0],[0,1]],[[0,0],[0,1]]],dtype=torch.bool))
            self.stencil_dict[222]=stencil_pattern_c(torch.tensor([[[0,0],[0,0]],[[0,1],[0,1]]],dtype=torch.bool))
            self.stencil_dict[223]=stencil_pattern_c(torch.tensor([[[0,0],[0,0]],[[0,0],[1,1]]],dtype=torch.bool))
            self.stencil_dict[231]=stencil_pattern_c(torch.tensor([[[0,1],[1,0]],[[0,0],[0,0]]],dtype=torch.bool))
            self.stencil_dict[232]=stencil_pattern_c(torch.tensor([[[0,1],[0,0]],[[1,0],[0,0]]],dtype=torch.bool))
            self.stencil_dict[233]=stencil_pattern_c(torch.tensor([[[0,0],[1,0]],[[1,0],[0,0]]],dtype=torch.bool))
            self.stencil_dict[241]=stencil_pattern_c(torch.tensor([[[0,0],[0,1]],[[0,1],[0,0]]],dtype=torch.bool))
            self.stencil_dict[242]=stencil_pattern_c(torch.tensor([[[0,0],[0,1]],[[0,0],[1,0]]],dtype=torch.bool))
            self.stencil_dict[243]=stencil_pattern_c(torch.tensor([[[0,0],[0,0]],[[0,1],[1,0]]],dtype=torch.bool))
            self.stencil_dict[251]=stencil_pattern_c(torch.tensor([[[0,1],[0,0]],[[0,0],[0,1]]],dtype=torch.bool))
            self.stencil_dict[252]=stencil_pattern_c(torch.tensor([[[0,0],[1,0]],[[0,0],[0,1]]],dtype=torch.bool))
            self.stencil_dict[253]=stencil_pattern_c(torch.tensor([[[0,0],[0,0]],[[1,0],[0,1]]],dtype=torch.bool))
            self.stencil_dict[261]=stencil_pattern_c(torch.tensor([[[0,1],[0,0]],[[0,0],[1,0]]],dtype=torch.bool))
            self.stencil_dict[262]=stencil_pattern_c(torch.tensor([[[0,0],[1,0]],[[0,1],[0,0]]],dtype=torch.bool))
            self.stencil_dict[263]=stencil_pattern_c(torch.tensor([[[0,0],[0,1]],[[1,0],[0,0]]],dtype=torch.bool))
            self.stencil_dict[111]=stencil_pattern_c(torch.tensor([[[0,1],[0,0]],[[0,0],[0,0]]],dtype=torch.bool))
            self.stencil_dict[112]=stencil_pattern_c(torch.tensor([[[0,0],[1,0]],[[0,0],[0,0]]],dtype=torch.bool))
            self.stencil_dict[113]=stencil_pattern_c(torch.tensor([[[0,0],[0,0]],[[1,0],[0,0]]],dtype=torch.bool))
            self.stencil_dict[121]=stencil_pattern_c(torch.tensor([[[0,0],[0,1]],[[0,0],[0,0]]],dtype=torch.bool))
            self.stencil_dict[122]=stencil_pattern_c(torch.tensor([[[0,0],[0,0]],[[0,1],[0,0]]],dtype=torch.bool))
            self.stencil_dict[123]=stencil_pattern_c(torch.tensor([[[0,0],[0,0]],[[0,0],[1,0]]],dtype=torch.bool))
            self.stencil_dict[131]=stencil_pattern_c(torch.tensor([[[0,0],[0,0]],[[0,0],[0,1]]],dtype=torch.bool))
            for stencil_id,stencil in self.stencil_dict.items():
                if args.interpolation_method=="linear":
                    stencil.mask_core=torch.zeros(1,1,3,3,3,dtype=torch.bool)
                    stencil.mask_core[0,0,1:,1:,1:]=stencil.ref_pos
                    stencil.mask_core[0,0,0,:,:]=stencil.mask_core[0,0,2,:,:]
                    stencil.mask_core[0,0,:,0,:]=stencil.mask_core[0,0,:,2,:]
                    stencil.mask_core[0,0,:,:,0]=stencil.mask_core[0,0,:,:,2]
                    if (stencil.mask_core&self.r1_mask).sum().item()>=args.min_reference_num:
                        stencil.mask_core=stencil.mask_core&self.r1_mask
                        continue
                    elif (stencil.mask_core&self.r2_mask).sum().item()>=args.min_reference_num:
                        stencil.mask_core=stencil.mask_core&self.r2_mask
                        continue
                    else:
                        continue
                else:
                    raise NotImplementedError(f"Haven't implemented mask core generation for cubic interpolation yet.")
                    #需要使用torch.flip翻转后半部分数据
        elif args.dim_num==2:
            if args.interpolation_method=="linear":
                self.r1_mask=torch.tensor([[0,1,0],[1,0,1],[0,1,0]],dtype=torch.bool)
                self.r2_mask=torch.ones((3,3),dtype=torch.bool)
            elif args.interpolation_method=="cubic":
                raise NotImplementedError(f"Haven't implemented radius masks for cubic interpolation yet.")
            self.stencil_dict:dict[int,stencil_pattern_c]={}
            self.stencil_dict[211]=stencil_pattern_c(torch.tensor([[0,1],[0,1]],dtype=torch.bool))
            self.stencil_dict[213]=stencil_pattern_c(torch.tensor([[0,0],[1,1]],dtype=torch.bool))
            self.stencil_dict[221]=stencil_pattern_c(torch.tensor([[0,1],[1,0]],dtype=torch.bool))
            self.stencil_dict[111]=stencil_pattern_c(torch.tensor([[0,1],[0,0]],dtype=torch.bool))
            self.stencil_dict[112]=stencil_pattern_c(torch.tensor([[0,0],[1,0]],dtype=torch.bool))
            self.stencil_dict[121]=stencil_pattern_c(torch.tensor([[0,0],[0,1]],dtype=torch.bool))
            for stencil_id,stencil in self.stencil_dict.items():
                if args.interpolation_method=="linear":
                    stencil.mask_core=torch.zeros(1,1,3,3,dtype=torch.bool)
                    stencil.mask_core[0,0,1:,1:]=stencil.ref_pos
                    stencil.mask_core[0,0,0,:]=stencil.mask_core[0,0,2,:]
                    stencil.mask_core[0,0,:,0]=stencil.mask_core[0,0,:,2]
                    if (stencil.mask_core&self.r1_mask).sum().item()>=args.min_reference_num:
                        stencil.mask_core=stencil.mask_core&self.r1_mask
                        continue
                    else:
                        continue
                else:
                    raise NotImplementedError(f"Haven't implemented mask core generation for cubic interpolation yet.")
                    #需要使用torch.flip翻转后半部分数据
        elif args.dim_num==1:
            self.stencil_dict[111]=stencil_pattern_c(torch.tensor([0,1],dtype=torch.bool))
            raise NotImplementedError(f"Haven't implemented mask core generation for 1D yet.")
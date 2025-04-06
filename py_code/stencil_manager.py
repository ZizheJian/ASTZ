import torch
from torch import Tensor

class stencil_manager_c():
    def __init__(self)->None:
        self.stencil_dict:dict[int,Tensor]={}
        self.stencil_dict[411]=torch.tensor([[[0,1],[0,1]],[[0,1],[0,1]]],dtype=torch.bool)
        self.stencil_dict[412]=torch.tensor([[[0,0],[1,1]],[[0,0],[1,1]]],dtype=torch.bool)
        self.stencil_dict[413]=torch.tensor([[[0,0],[0,0]],[[1,1],[1,1]]],dtype=torch.bool)
        self.stencil_dict[421]=torch.tensor([[[0,1],[1,0]],[[0,1],[1,0]]],dtype=torch.bool)
        self.stencil_dict[422]=torch.tensor([[[0,1],[0,1]],[[1,0],[1,0]]],dtype=torch.bool)
        self.stencil_dict[423]=torch.tensor([[[0,0],[1,1]],[[1,1],[0,0]]],dtype=torch.bool)
        self.stencil_dict[431]=torch.tensor([[[0,1],[1,0]],[[1,0],[0,1]]],dtype=torch.bool)

        self.stencil_dict[211]=torch.tensor([[[0,1],[0,1]],[[0,0],[0,0]]],dtype=torch.bool)
        self.stencil_dict[212]=torch.tensor([[[0,1],[0,0]],[[0,1],[0,0]]],dtype=torch.bool)
        self.stencil_dict[213]=torch.tensor([[[0,0],[1,1]],[[0,0],[0,0]]],dtype=torch.bool)
        self.stencil_dict[214]=torch.tensor([[[0,0],[1,0]],[[0,0],[1,0]]],dtype=torch.bool)
        self.stencil_dict[215]=torch.tensor([[[0,0],[0,0]],[[1,1],[0,0]]],dtype=torch.bool)
        self.stencil_dict[216]=torch.tensor([[[0,0],[0,0]],[[1,0],[1,0]]],dtype=torch.bool)
        self.stencil_dict[221]=torch.tensor([[[0,0],[0,1]],[[0,0],[0,1]]],dtype=torch.bool)
        self.stencil_dict[222]=torch.tensor([[[0,0],[0,0]],[[0,1],[0,1]]],dtype=torch.bool)
        self.stencil_dict[223]=torch.tensor([[[0,0],[0,0]],[[0,0],[1,1]]],dtype=torch.bool)
        self.stencil_dict[231]=torch.tensor([[[0,1],[1,0]],[[0,0],[0,0]]],dtype=torch.bool)
        self.stencil_dict[232]=torch.tensor([[[0,1],[0,0]],[[1,0],[0,0]]],dtype=torch.bool)
        self.stencil_dict[233]=torch.tensor([[[0,0],[1,0]],[[1,0],[0,0]]],dtype=torch.bool)
        self.stencil_dict[241]=torch.tensor([[[0,0],[0,1]],[[0,1],[0,0]]],dtype=torch.bool)
        self.stencil_dict[242]=torch.tensor([[[0,0],[0,1]],[[0,0],[1,0]]],dtype=torch.bool)
        self.stencil_dict[243]=torch.tensor([[[0,0],[0,0]],[[0,1],[1,0]]],dtype=torch.bool)
        self.stencil_dict[251]=torch.tensor([[[0,1],[0,0]],[[0,0],[0,1]]],dtype=torch.bool)
        self.stencil_dict[252]=torch.tensor([[[0,0],[1,0]],[[0,0],[0,1]]],dtype=torch.bool)
        self.stencil_dict[253]=torch.tensor([[[0,0],[0,0]],[[1,0],[0,1]]],dtype=torch.bool)
        self.stencil_dict[261]=torch.tensor([[[0,1],[0,0]],[[0,0],[1,0]]],dtype=torch.bool)
        self.stencil_dict[262]=torch.tensor([[[0,0],[1,0]],[[0,1],[0,0]]],dtype=torch.bool)
        self.stencil_dict[263]=torch.tensor([[[0,0],[0,1]],[[1,0],[0,0]]],dtype=torch.bool)
        
        self.stencil_dict[111]=torch.tensor([[[0,1],[0,0]],[[0,0],[0,0]]],dtype=torch.bool)
        self.stencil_dict[112]=torch.tensor([[[0,0],[1,0]],[[0,0],[0,0]]],dtype=torch.bool)
        self.stencil_dict[113]=torch.tensor([[[0,0],[0,0]],[[1,0],[0,0]]],dtype=torch.bool)
        self.stencil_dict[121]=torch.tensor([[[0,0],[0,1]],[[0,0],[0,0]]],dtype=torch.bool)
        self.stencil_dict[122]=torch.tensor([[[0,0],[0,0]],[[0,1],[0,0]]],dtype=torch.bool)
        self.stencil_dict[123]=torch.tensor([[[0,0],[0,0]],[[0,0],[1,0]]],dtype=torch.bool)
        self.stencil_dict[131]=torch.tensor([[[0,0],[0,0]],[[0,0],[0,1]]],dtype=torch.bool)
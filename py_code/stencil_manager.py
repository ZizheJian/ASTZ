import torch
from torch import Tensor
from args import args_c

class stencil_pattern_c():
    def __init__(self,pattern:Tensor)->None:
        self.ref_pos:Tensor=pattern # 1 indicates the positions with available values
        self.mask_core:Tensor=None # 1 indicates the positions with available values

class stencil_manager_c():
    def __init__(self,args:args_c)->None:
        if args.dim_num==4:
            if args.interpolation_method=="linear":
                self.r1_mask=torch.tensor([[[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,1,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,0]]],
                                           [[[0,0,0],[0,1,0],[0,0,0]],[[0,1,0],[1,0,1],[0,1,0]],[[0,0,0],[0,1,0],[0,0,0]]],
                                           [[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,1,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,0]]]],dtype=torch.bool)
                self.r2_mask=torch.tensor([[[[0,0,0],[0,1,0],[0,0,0]],[[0,1,0],[1,1,1],[0,1,0]],[[0,0,0],[0,1,0],[0,0,0]]],
                                           [[[0,1,0],[1,1,1],[0,1,0]],[[1,1,1],[1,0,1],[1,1,1]],[[0,1,0],[1,1,1],[0,1,0]]],
                                           [[[0,0,0],[0,1,0],[0,0,0]],[[0,1,0],[1,1,1],[0,1,0]],[[0,0,0],[0,1,0],[0,0,0]]]],dtype=torch.bool)
                self.r3_mask=torch.tensor([[[[0,1,0],[1,1,1],[0,1,0]],[[1,1,1],[1,1,1],[1,1,1]],[[0,1,0],[1,1,1],[0,1,0]]],
                                           [[[1,1,1],[1,1,1],[1,1,1]],[[1,1,1],[1,0,1],[1,1,1]],[[1,1,1],[1,1,1],[1,1,1]]],
                                           [[[0,1,0],[1,1,1],[0,1,0]],[[1,1,1],[1,1,1],[1,1,1]],[[0,1,0],[1,1,1],[0,1,0]]]],dtype=torch.bool)
                self.r4_mask=torch.ones((3,3,3,3),dtype=torch.bool)
            elif args.interpolation_method=="cubic":
                raise NotImplementedError(f"Haven't implemented radius masks for cubic interpolation yet.")
            self.stencil_dict:dict[int,stencil_pattern_c]={}
            self.stencil_dict[8000]=stencil_pattern_c(torch.tensor([[[[0,1],[1,0]],[[1,0],[0,1]]],[[[1,0],[0,1]],[[0,1],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[8001]=stencil_pattern_c(torch.tensor([[[[0,1],[1,0]],[[1,0],[0,1]]],[[[0,1],[1,0]],[[1,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[8002]=stencil_pattern_c(torch.tensor([[[[0,1],[1,0]],[[0,1],[1,0]]],[[[1,0],[0,1]],[[1,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[8003]=stencil_pattern_c(torch.tensor([[[[0,1],[1,0]],[[0,1],[1,0]]],[[[0,1],[1,0]],[[0,1],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[8004]=stencil_pattern_c(torch.tensor([[[[0,1],[0,1]],[[1,0],[1,0]]],[[[1,0],[1,0]],[[0,1],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[8005]=stencil_pattern_c(torch.tensor([[[[0,1],[0,1]],[[1,0],[1,0]]],[[[0,1],[0,1]],[[1,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[8006]=stencil_pattern_c(torch.tensor([[[[0,1],[0,1]],[[0,1],[0,1]]],[[[1,0],[1,0]],[[1,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[8007]=stencil_pattern_c(torch.tensor([[[[0,1],[0,1]],[[0,1],[0,1]]],[[[0,1],[0,1]],[[0,1],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[8008]=stencil_pattern_c(torch.tensor([[[[0,0],[1,1]],[[1,1],[0,0]]],[[[1,1],[0,0]],[[0,0],[1,1]]]],dtype=torch.bool))
            self.stencil_dict[8009]=stencil_pattern_c(torch.tensor([[[[0,0],[1,1]],[[1,1],[0,0]]],[[[0,0],[1,1]],[[1,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[8010]=stencil_pattern_c(torch.tensor([[[[0,0],[1,1]],[[0,0],[1,1]]],[[[1,1],[0,0]],[[1,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[8011]=stencil_pattern_c(torch.tensor([[[[0,0],[1,1]],[[0,0],[1,1]]],[[[0,0],[1,1]],[[0,0],[1,1]]]],dtype=torch.bool))
            self.stencil_dict[8012]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,1],[1,1]]],[[[1,1],[1,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[8013]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,1],[1,1]]],[[[0,0],[0,0]],[[1,1],[1,1]]]],dtype=torch.bool))
            self.stencil_dict[8014]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[1,1],[1,1]],[[1,1],[1,1]]]],dtype=torch.bool))
            self.stencil_dict[4000]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[1,1],[1,1]]]],dtype=torch.bool))
            self.stencil_dict[4001]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[1,1]],[[0,0],[1,1]]]],dtype=torch.bool))
            self.stencil_dict[4002]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[1,1]],[[1,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4003]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,1],[0,1]],[[0,1],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4004]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,1],[0,1]],[[1,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4005]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,1],[1,0]],[[0,1],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4006]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,1],[1,0]],[[1,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4007]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[1,0],[0,1]],[[0,1],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4008]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[1,0],[0,1]],[[1,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4009]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[1,0],[1,0]],[[0,1],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4010]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[1,0],[1,0]],[[1,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4011]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[1,1],[0,0]],[[0,0],[1,1]]]],dtype=torch.bool))
            self.stencil_dict[4012]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[1,1],[0,0]],[[1,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4013]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[1,1],[1,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4014]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[1,1]]],[[[0,0],[0,0]],[[0,0],[1,1]]]],dtype=torch.bool))
            self.stencil_dict[4015]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[1,1]]],[[[0,0],[0,0]],[[1,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4016]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[1,1]]],[[[0,0],[1,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4017]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[1,1]]],[[[1,1],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4018]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,1],[0,1]]],[[[0,0],[0,0]],[[0,1],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4019]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,1],[0,1]]],[[[0,0],[0,0]],[[1,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4020]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,1],[0,1]]],[[[0,1],[0,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4021]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,1],[0,1]]],[[[1,0],[1,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4022]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,1],[1,0]]],[[[0,0],[0,0]],[[0,1],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4023]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,1],[1,0]]],[[[0,0],[0,0]],[[1,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4024]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,1],[1,0]]],[[[0,1],[1,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4025]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,1],[1,0]]],[[[1,0],[0,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4026]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,0],[0,1]]],[[[0,0],[0,0]],[[0,1],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4027]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,0],[0,1]]],[[[0,0],[0,0]],[[1,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4028]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,0],[0,1]]],[[[0,1],[1,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4029]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,0],[0,1]]],[[[1,0],[0,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4030]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,0],[1,0]]],[[[0,0],[0,0]],[[0,1],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4031]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,0],[1,0]]],[[[0,0],[0,0]],[[1,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4032]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,0],[1,0]]],[[[0,1],[0,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4033]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,0],[1,0]]],[[[1,0],[1,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4034]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,1],[0,0]]],[[[0,0],[0,0]],[[0,0],[1,1]]]],dtype=torch.bool))
            self.stencil_dict[4035]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,1],[0,0]]],[[[0,0],[0,0]],[[1,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4036]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,1],[0,0]]],[[[0,0],[1,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4037]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,1],[0,0]]],[[[1,1],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4038]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,1],[1,1]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4039]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,0],[0,1]]],[[[0,0],[0,1]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4040]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,0],[0,1]]],[[[0,0],[1,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4041]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,0],[0,1]]],[[[0,1],[0,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4042]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,0],[0,1]]],[[[1,0],[0,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4043]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,0],[1,0]]],[[[0,0],[0,1]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4044]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,0],[1,0]]],[[[0,0],[1,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4045]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,0],[1,0]]],[[[0,1],[0,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4046]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,0],[1,0]]],[[[1,0],[0,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4047]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,1],[0,0]]],[[[0,0],[0,1]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4048]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,1],[0,0]]],[[[0,0],[1,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4049]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,1],[0,0]]],[[[0,1],[0,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4050]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,1],[0,0]]],[[[1,0],[0,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4051]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[1,0],[0,0]]],[[[0,0],[0,1]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4052]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[1,0],[0,0]]],[[[0,0],[1,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4053]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[1,0],[0,0]]],[[[0,1],[0,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4054]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[1,0],[0,0]]],[[[1,0],[0,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4055]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,0],[0,1]]],[[[0,0],[0,1]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4056]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,0],[0,1]]],[[[0,0],[1,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4057]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,0],[0,1]]],[[[0,1],[0,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4058]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,0],[0,1]]],[[[1,0],[0,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4059]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,0],[1,0]]],[[[0,0],[0,1]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4060]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,0],[1,0]]],[[[0,0],[1,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4061]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,0],[1,0]]],[[[0,1],[0,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4062]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,0],[1,0]]],[[[1,0],[0,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4063]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,1],[0,0]]],[[[0,0],[0,1]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4064]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,1],[0,0]]],[[[0,0],[1,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4065]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,1],[0,0]]],[[[0,1],[0,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4066]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,1],[0,0]]],[[[1,0],[0,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4067]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[1,0],[0,0]]],[[[0,0],[0,1]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4068]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[1,0],[0,0]]],[[[0,0],[1,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4069]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[1,0],[0,0]]],[[[0,1],[0,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4070]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[1,0],[0,0]]],[[[1,0],[0,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4071]=stencil_pattern_c(torch.tensor([[[[0,0],[1,1]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[1,1]]]],dtype=torch.bool))
            self.stencil_dict[4072]=stencil_pattern_c(torch.tensor([[[[0,0],[1,1]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[1,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4073]=stencil_pattern_c(torch.tensor([[[[0,0],[1,1]],[[0,0],[0,0]]],[[[0,0],[1,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4074]=stencil_pattern_c(torch.tensor([[[[0,0],[1,1]],[[0,0],[0,0]]],[[[1,1],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4075]=stencil_pattern_c(torch.tensor([[[[0,0],[1,1]],[[0,0],[1,1]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4076]=stencil_pattern_c(torch.tensor([[[[0,0],[1,1]],[[1,1],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4077]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,0],[0,1]]],[[[0,0],[0,1]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4078]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,0],[0,1]]],[[[0,0],[1,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4079]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,0],[0,1]]],[[[0,1],[0,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4080]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,0],[0,1]]],[[[1,0],[0,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4081]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,0],[1,0]]],[[[0,0],[0,1]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4082]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,0],[1,0]]],[[[0,0],[1,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4083]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,0],[1,0]]],[[[0,1],[0,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4084]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,0],[1,0]]],[[[1,0],[0,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4085]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,1],[0,0]]],[[[0,0],[0,1]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4086]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,1],[0,0]]],[[[0,0],[1,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4087]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,1],[0,0]]],[[[0,1],[0,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4088]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,1],[0,0]]],[[[1,0],[0,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4089]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[1,0],[0,0]]],[[[0,0],[0,1]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4090]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[1,0],[0,0]]],[[[0,0],[1,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4091]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[1,0],[0,0]]],[[[0,1],[0,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4092]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[1,0],[0,0]]],[[[1,0],[0,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4093]=stencil_pattern_c(torch.tensor([[[[0,1],[0,1]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,1],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4094]=stencil_pattern_c(torch.tensor([[[[0,1],[0,1]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[1,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4095]=stencil_pattern_c(torch.tensor([[[[0,1],[0,1]],[[0,0],[0,0]]],[[[0,1],[0,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4096]=stencil_pattern_c(torch.tensor([[[[0,1],[0,1]],[[0,0],[0,0]]],[[[1,0],[1,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4097]=stencil_pattern_c(torch.tensor([[[[0,1],[0,1]],[[0,1],[0,1]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4098]=stencil_pattern_c(torch.tensor([[[[0,1],[0,1]],[[1,0],[1,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4099]=stencil_pattern_c(torch.tensor([[[[0,1],[1,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,1],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[4100]=stencil_pattern_c(torch.tensor([[[[0,1],[1,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[1,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[4101]=stencil_pattern_c(torch.tensor([[[[0,1],[1,0]],[[0,0],[0,0]]],[[[0,1],[1,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4102]=stencil_pattern_c(torch.tensor([[[[0,1],[1,0]],[[0,0],[0,0]]],[[[1,0],[0,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4103]=stencil_pattern_c(torch.tensor([[[[0,1],[1,0]],[[0,1],[1,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[4104]=stencil_pattern_c(torch.tensor([[[[0,1],[1,0]],[[1,0],[0,1]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2000]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[1,1]]]],dtype=torch.bool))
            self.stencil_dict[2001]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,1],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[2002]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,1],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[2003]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[1,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[2004]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[1,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[2005]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[1,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2006]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,1]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[2007]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,1]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[2008]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,1]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2009]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,1]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2010]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[1,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[2011]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[1,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[2012]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[1,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2013]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[1,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2014]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[1,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2015]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,1],[0,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[2016]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,1],[0,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[2017]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,1],[0,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2018]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,1],[0,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2019]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,1],[0,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2020]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,1],[1,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2021]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[1,0],[0,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[2022]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[1,0],[0,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[2023]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[1,0],[0,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2024]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[1,0],[0,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2025]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[1,0],[0,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2026]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[1,0],[1,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2027]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[1,1],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2028]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,1]]],[[[0,0],[0,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[2029]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,1]]],[[[0,0],[0,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[2030]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,1]]],[[[0,0],[0,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2031]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,1]]],[[[0,0],[0,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2032]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,1]]],[[[0,0],[0,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2033]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,1]]],[[[0,0],[1,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2034]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,1]]],[[[0,1],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2035]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,1]]],[[[1,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2036]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[1,0]]],[[[0,0],[0,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[2037]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[1,0]]],[[[0,0],[0,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[2038]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[1,0]]],[[[0,0],[0,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2039]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[1,0]]],[[[0,0],[0,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2040]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[1,0]]],[[[0,0],[0,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2041]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[1,0]]],[[[0,0],[1,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2042]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[1,0]]],[[[0,1],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2043]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[1,0]]],[[[1,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2044]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[1,1]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2045]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,1],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[2046]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,1],[0,0]]],[[[0,0],[0,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[2047]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,1],[0,0]]],[[[0,0],[0,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2048]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,1],[0,0]]],[[[0,0],[0,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2049]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,1],[0,0]]],[[[0,0],[0,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2050]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,1],[0,0]]],[[[0,0],[1,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2051]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,1],[0,0]]],[[[0,1],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2052]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,1],[0,0]]],[[[1,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2053]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,1],[0,1]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2054]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,1],[1,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2055]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[2056]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[2057]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,0],[0,0]]],[[[0,0],[0,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2058]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,0],[0,0]]],[[[0,0],[0,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2059]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,0],[0,0]]],[[[0,0],[0,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2060]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,0],[0,0]]],[[[0,0],[1,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2061]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,0],[0,0]]],[[[0,1],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2062]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,0],[0,0]]],[[[1,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2063]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,0],[0,1]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2064]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,0],[1,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2065]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,1],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2066]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[2067]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[2068]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2069]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2070]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,0],[0,0]]],[[[0,0],[0,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2071]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,0],[0,0]]],[[[0,0],[1,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2072]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,0],[0,0]]],[[[0,1],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2073]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,0],[0,0]]],[[[1,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2074]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,0],[0,1]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2075]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,0],[1,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2076]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,1],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2077]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[1,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2078]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[2079]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[2080]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2081]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2082]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,0],[0,0]]],[[[0,0],[0,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2083]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,0],[0,0]]],[[[0,0],[1,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2084]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,0],[0,0]]],[[[0,1],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2085]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,0],[0,0]]],[[[1,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2086]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,0],[0,1]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2087]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,0],[1,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2088]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,1],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2089]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[1,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2090]=stencil_pattern_c(torch.tensor([[[[0,0],[1,1]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2091]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[2092]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[2093]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2094]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2095]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2096]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,0],[0,0]]],[[[0,0],[1,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2097]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,0],[0,0]]],[[[0,1],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2098]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,0],[0,0]]],[[[1,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2099]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,0],[0,1]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2100]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,0],[1,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2101]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,1],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2102]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[1,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2103]=stencil_pattern_c(torch.tensor([[[[0,1],[0,1]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[2104]=stencil_pattern_c(torch.tensor([[[[0,1],[1,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[1000]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,1]]]],dtype=torch.bool))
            self.stencil_dict[1001]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[1,0]]]],dtype=torch.bool))
            self.stencil_dict[1002]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,1],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[1003]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[1,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[1004]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,1]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[1005]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,0],[1,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[1006]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[0,1],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[1007]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,0]]],[[[1,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[1008]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[0,1]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[1009]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,0],[1,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[1010]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[0,1],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[1011]=stencil_pattern_c(torch.tensor([[[[0,0],[0,0]],[[1,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[1012]=stencil_pattern_c(torch.tensor([[[[0,0],[0,1]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[1013]=stencil_pattern_c(torch.tensor([[[[0,0],[1,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            self.stencil_dict[1014]=stencil_pattern_c(torch.tensor([[[[0,1],[0,0]],[[0,0],[0,0]]],[[[0,0],[0,0]],[[0,0],[0,0]]]],dtype=torch.bool))
            for stencil_id,stencil in self.stencil_dict.items():
                if args.interpolation_method=="linear":
                    stencil.mask_core=torch.zeros(1,1,3,3,3,3,dtype=torch.bool)
                    stencil.mask_core[0,0,1:,1:,1:,1:]=stencil.ref_pos
                    stencil.mask_core[0,0,0,:,:,:]=stencil.mask_core[0,0,2,:,:,:]
                    stencil.mask_core[0,0,:,0,:,:]=stencil.mask_core[0,0,:,2,:,:]
                    stencil.mask_core[0,0,:,:,0,:]=stencil.mask_core[0,0,:,:,2,:]
                    stencil.mask_core[0,0,:,:,:,0]=stencil.mask_core[0,0,:,:,:,2]
                    if (stencil.mask_core&self.r1_mask).sum().item()>=args.min_reference_num:
                        stencil.mask_core=stencil.mask_core&self.r1_mask
                        continue
                    elif (stencil.mask_core&self.r2_mask).sum().item()>=args.min_reference_num:
                        stencil.mask_core=stencil.mask_core&self.r2_mask
                        continue
                    elif (stencil.mask_core&self.r3_mask).sum().item()>=args.min_reference_num:
                        stencil.mask_core=stencil.mask_core&self.r3_mask
                    else:
                        continue
                else:
                    raise NotImplementedError(f"Haven't implemented mask core generation for cubic interpolation yet.")
                    #需要使用torch.flip翻转后半部分数据
        elif args.dim_num==3:
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
            self.stencil_dict:dict[int,stencil_pattern_c]={}
            self.stencil_dict[111]=stencil_pattern_c(torch.tensor([0,1],dtype=torch.bool))
            for stencil_id,stencil in self.stencil_dict.items():
                if args.interpolation_method=="linear":
                    stencil.mask_core=torch.zeros(1,1,3,dtype=torch.bool)
                    stencil.mask_core[0,0,1:]=stencil.ref_pos
                    stencil.mask_core[0,0,0]=stencil.mask_core[0,0,2]
                else:
                    raise NotImplementedError(f"Haven't implemented mask core generation for cubic interpolation yet.")
                    #需要使用torch.flip翻转后半部分数据
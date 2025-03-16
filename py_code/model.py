import torch,copy
from torch import nn,Tensor,optim
from typing import Tuple
from args import args_c

def create_model(layer:int=1,range_fix:float=1)->nn.Module:
    if layer==1:
        return linear_model_c()
    return model_c(layer=layer,range_fix=range_fix)

class linear_model_c(nn.Module):
    def __init__(self)->None:
        super(linear_model_c,self).__init__()
        self.layer=1
        self.range_fix=1
        self.conv=nn.Conv3d(9,1,3)
    def forward(self,x:Tensor)->Tensor:
        return self.conv(x)

class model_c(nn.Module):
    def __init__(self,layer,range_fix)->None:
        super(model_c,self).__init__()
        self.layer=layer
        self.range_fix=range_fix
        self.conv_channel=8
        self.act=nn.LeakyReLU()
        self.conv1=nn.Conv3d(1,self.conv_channel,3,padding=1)
        self.conv2=nn.ModuleList([nn.Sequential(nn.Conv3d(self.conv_channel,self.conv_channel,3,padding=1),
                                                nn.BatchNorm3d(self.conv_channel)) for _ in range(self.layer-2)])
        self.conv3=nn.Conv3d(self.conv_channel,1,3,padding=1)
    def forward(self,x:Tensor)->Tuple[Tensor,Tensor]:
        x_backup=x
        x=self.conv1(x)
        x=self.act(x)
        for conv in self.conv2:
            x=conv(x)
            x=self.act(x)
        x=self.conv3(x)
        return x_backup+x*self.range_fix

def model_train(args:args_c,cur_data:Tensor,tgt_data:Tensor,mask:Tensor,layer:int,range_fix:float,sqrtmsqb_baseline:float=float("inf"))->Tuple[nn.Module,float]:
    model=create_model(layer=layer,range_fix=range_fix)
    criteria=nn.MSELoss()
    optimizer=optim.Adam(model.parameters(),lr=1e-2)
    scheduler_increase=torch.optim.lr_scheduler.StepLR(optimizer,step_size=2,gamma=1/0.95)
    scheduler_decrease=torch.optim.lr_scheduler.StepLR(optimizer,step_size=1,gamma=0.95)
    max_lr=0.1
    last_sqrtmsqb=sqrtmsqb_baseline
    best_sqrtmsqb=sqrtmsqb_baseline
    best_model=model
    for epid in range(1,args.max_epoch+1):
        optimizer.zero_grad()
        h=model(cur_data)
        loss=criteria(h[mask],tgt_data[mask])
        with torch.no_grad():
            sqrtmsqb=(loss.item()**0.5)/(2*args.abs_eb)
            if epid%50==0 and best_sqrtmsqb>sqrtmsqb:
                best_sqrtmsqb=sqrtmsqb
                best_model=copy.deepcopy(model)
            # if layer==1:
            #     print(f"epid={epid} sqrtmsqb={sqrtmsqb:.6f} lr={optimizer.param_groups[0]['lr']:.6f}")
            # else:
            #     print(f"epid={epid} sqrtmsqb={sqrtmsqb:.6f} sqrtmsqb_rate={sqrtmsqb/sqrtmsqb_baseline:.6f} lr={optimizer.param_groups[0]['lr']:.6f}")
        loss.backward()
        optimizer.step()
        with torch.no_grad():
            if sqrtmsqb>last_sqrtmsqb:
                scheduler_decrease.step()
            else:
                if optimizer.param_groups[0]["lr"]<max_lr:
                    scheduler_increase.step()
            last_sqrtmsqb=sqrtmsqb
    # print(model.conv.weight.detach())
    # print(model.conv.bias.detach())
    print([best_model.conv.weight[0,i].sum().item() for i in range(4)])
    return best_model,best_sqrtmsqb
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision

"""
近年来，动作识别受到了广泛的关注，它通过从各种传感器数据中提取特征来对动作进行分类。然而，随着识别细粒度动作的难度越来越大，某些方法无法学习足够的运动和时间信息。
因此，需要一种有效的信息增强方法来推理视频序列中的运动线索。本文提出了一种称为运动信息增强网络（MIE-Net）的端到端视频动作识别框架，它由两个创新组件组成。
第一个组件是自适应融合模块（AFM），有选择地提取原始特征和运动增强特征之间的关系，以增强不同特征信息之间的交互。
第二个组件是双池时间注意力模块（DPTAM），它实现时间建模以增强特征提取过程中的微妙信息。
最后，通过传感器摄像头收集了包含 116 名参与者的 1000 多个视频的立定跳远数据集（SLJD），该数据集与现有数据集的不同之处在于强背景无偏性，以稳健地评估我们模型的有效性。 
SLJD、Something-Something v2 和 Diving48 数据集上的实验结果表明，所提出的 MIE-Net 优于大多数最先进的方法。
"""

class DPTAM(nn.Module):
    def __init__(self,
                 in_channels,
                 n_segment,
                 kernel_size=3,
                 stride=1,
                 padding=1):
        super(DPTAM, self).__init__()
        self.in_channels = in_channels
        self.n_segment = n_segment
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        print('DPTAM with kernel_size {}.'.format(kernel_size))

        self.conv_mask = nn.Conv2d(in_channels, 1, kernel_size=3)#context Modeling
        self.softmax = nn.Softmax(dim=2)
        self.p1_conv1= nn.Conv1d(in_channels , in_channels, 1, bias=False)


        self.dptam = nn.Sequential(
            nn.Conv1d(in_channels,
                      in_channels // 4,
                      kernel_size,
                      stride=1,
                      padding=kernel_size // 2,
                      bias=False), nn.BatchNorm1d(in_channels // 4),
            nn.ReLU(inplace=True),
            nn.Conv1d(in_channels // 4, in_channels, 1, bias=False),
            nn.Sigmoid())

    def forward(self, x):
        nt, c, h, w = x.size()

        t = self.n_segment
        n_batch = nt // t
        new_x = x.view(n_batch, t, c, h, w).permute(0, 2, 1, 3,4).contiguous()
        out = F.adaptive_avg_pool2d(new_x.view(n_batch * c, t, h, w), (1, 1))

        x_22=out.view(-1,c,t)
        x22_c_t = self.p1_conv1(x_22)
        x22 =x_22.mean(2,keepdim=True)
        x22 = self.p1_conv1(x22)
        x22 = x22_c_t * x22
        x22= x_22+x22

        local_activation = self.dptam(x22).view(n_batch, c, t, 1, 1)
        new_x = new_x * local_activation

        out = new_x.view(n_batch, c, t, h, w) #光local
        out = out.permute(0, 2, 1, 3, 4).contiguous().view(nt, c, h, w)

        return out



if __name__ == '__main__':
    n_segment = 16  

    block = DPTAM(in_channels=4, n_segment=n_segment)
    input_tensor = torch.rand(16, 4, 16, 16)
    output_tensor = block(input_tensor)
    print("Input tensor size:", input_tensor.size())
    print("Output tensor size:", output_tensor.size())


from __future__ import division
import torch
import torch.nn as nn
from collections import OrderedDict
import torch.nn.functional as F


class SACBlock(nn.Module):
    def __init__(self, inplanes, expand1x1_planes, bn_d=0.1):
        super(SACBlock, self).__init__()
        self.inplanes = inplanes
        self.bn_d = bn_d

        self.attention_x = nn.Sequential(
            nn.Conv2d(3, 9 * self.inplanes, kernel_size=7, padding=3),
            nn.BatchNorm2d(9 * self.inplanes, momentum=0.1),
        )

        self.position_mlp_2 = nn.Sequential(
            nn.Conv2d(9 * self.inplanes, self.inplanes, kernel_size=1),
            nn.BatchNorm2d(self.inplanes, momentum=0.1),
            nn.ReLU(inplace=True),
            nn.Conv2d(self.inplanes, self.inplanes, kernel_size=3, padding=1),
            nn.BatchNorm2d(self.inplanes, momentum=0.1),
            nn.ReLU(inplace=True),
        )

    def forward(self, input):
        xyz = input[0]
        new_xyz = input[1]
        feature = input[2]
        N, C, H, W = feature.size()

        new_feature = F.unfold(feature, kernel_size=3, padding=1).view(N, -1, H, W)
        attention = F.sigmoid(self.attention_x(new_xyz))
        new_feature = new_feature * attention
        new_feature = self.position_mlp_2(new_feature)
        fuse_feature = new_feature + feature

        return xyz, new_xyz, fuse_feature


if __name__ == '__main__':
    # 假设输入张量的维度，这需要根据你的SACBlock类设计来确定
    N, C, H, W = 1, 3, 224, 224  # 一个示例批次大小N=1, 通道数C=3, 高H=224, 宽W=224
    inplanes = 64  # SACBlock类的inplanes参数值
    expand1x1_planes = 64  # SACBlock类的expand1x1_planes参数值
    bn_d = 0.1  # SACBlock类的bn_d参数值

    # 初始化SACBlock
    block = SACBlock(inplanes, expand1x1_planes, bn_d)

    # 创建一个模拟的xyz, new_xyz, 和特征张量
    xyz = torch.rand(N, C, H, W)
    new_xyz = torch.rand(N, C, H, W)
    feature = torch.rand(N, C, H, W)

    # 将三个张量打包成一个输入元组
    input = (xyz, new_xyz, feature)

    # 执行前向传播
    output = block(input)

    # 打印输入和输出的尺寸
    print('Input size:', {x.size() for x in input})
    print('Output size:', {x.size() for x in output})
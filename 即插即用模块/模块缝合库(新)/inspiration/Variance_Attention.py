import sys
import os
import torch
import time
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import torch.optim as optim
import numpy as np
import torch.nn.init as init

"""
由于异常定义的模糊性以及真实视频数据中视觉场景的复杂性，视频中的异常检测仍然是一项具有挑战性的任务。
与之前利用重建或预测作为辅助任务来学习时间规律性的工作不同，在这项工作中，我们探索了一种新颖的卷积自动编码器架构，它可以分离时空表示以分别捕获空间和时间信息，因为异常事件通常不同于外观和/或运动行为的正常情况。
具体来说，空间自编码器通过学习重构第一个单独帧（FIF）的输入来对外观特征空间上的正态性进行建模，而时间部分则以前四个连续帧作为输入，RGB差值作为输出来模拟光流以有效的方式运动。
外观或运动行为不规则的异常事件会导致较大的重建误差。为了提高快速移动异常值的检测性能，我们利用基于方差的注意模块并将其插入运动自动编码器中以突出显示大的运动区域。
此外，我们提出了一种深度 K 均值聚类策略来强制空间和运动编码器提取紧凑的表示。对一些公开数据集的广泛实验证明了我们方法的有效性，实现了最先进的性能。
"""


def softmax_normalization(x, func):
    b, c, h, w = x.shape
    x_re = x.view([b, c, -1])
    x_norm = func(x_re)
    x_norm = x_norm.view([b, c, h, w])
    return x_norm


class Variance_Attention(nn.Module):
    def __init__(self, depth_in, depth_embedding, maxpool=1):
        super(Variance_Attention, self).__init__()
        self.flow = nn.Sequential()
        self.flow.add_module('proj_conv',
                             nn.Conv2d(depth_in, depth_embedding, kernel_size=1, padding=False, bias=False))
        self.maxpool = maxpool
        if not maxpool == 1:
            self.flow.add_module('pool', nn.AvgPool2d(kernel_size=maxpool, stride=maxpool))
            self.unpool = nn.Upsample(scale_factor=maxpool)
        self.norm_func = nn.Softmax(-1)

    def forward(self, x):
        # 将输入张量从 Tensor 类型转换为 torch.Tensor 类型
        x = torch.Tensor(x)

        proj_x = self.flow(x)
        mean_x = torch.mean(proj_x, dim=1, keepdim=True)
        variance_x = torch.sum(torch.pow(proj_x - mean_x, 2), dim=1, keepdim=True)
        var_norm = softmax_normalization(variance_x, self.norm_func)
        if not self.maxpool == 1:
            var_norm = self.unpool(var_norm)

        return torch.exp(var_norm) * x


if __name__ == '__main__':
    # 定义输入张量大小
    batch_size = 1
    channels = 3
    height = 64
    width = 64

    # 创建 Variance_Attention 实例，并传递深度输入和嵌入深度参数
    block = Variance_Attention(depth_in=channels, depth_embedding=64, maxpool=2)

    # 生成随机输入张量
    input_tensor = torch.rand(batch_size, channels, height, width)

    # 计算输出张量
    output_tensor = block(input_tensor)

    # 打印输入和输出张量的大小
    print("Input tensor size:", input_tensor.size())
    print("Output tensor size:", output_tensor.size())


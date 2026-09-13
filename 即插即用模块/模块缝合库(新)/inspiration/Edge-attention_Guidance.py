import torch
import torch.nn as nn
from kornia.filters import SpatialGradient
from torch import Tensor

"""
图像融合整合了从不同传感器（例如红外和可见光）获取的一系列图像 ，输出比其中任何一个传感器都包含更丰富信息的图像。传统和近期的基于深度的方法在保留突出结构和恢复实际应用中的重要纹理细节方面存在困难。在本文中，我们提出了一种用于红外和可见光图像融合的深度网络，将特征学习模块与融合学习机制级联。首先，我们应用由粗到细的深度架构来学习多模态图像的多尺度特征，这使得能够发现突出的共同结构以供以后的融合操作。所提出的特征学习模块不需要良好对齐的图像对进行训练。与现有的基于学习的方法相比，所提出的特征学习模块可以集合来自各个模态的大量示例进行训练，从而提高了特征表示能力。其次，我们在多尺度特征上设计了一个边缘引导注意机制来引导融合关注共同结构，从而在衰减噪声的同时恢复细节。此外，我们还提供了一个新的对齐红外和可见光图像融合数据集 RealStreet，该数据集是在各种实际场景中收集的，用于进行全面评估。在 TNO 和 RealStreet 两个基准上进行的大量实验证明了所提出的方法在视觉检查和六个评估指标的客观分析方面优于最先进的方法。我们还在包含雾天和弱光条件的 FLIR 和 NIR 数据集上进行了实验，以验证所提出方法的泛化和鲁棒性。
"""

class EdgeDetect(nn.Module):
    def __init__(self):
        super(EdgeDetect, self).__init__()
        self.spatial = SpatialGradient('diff')
        self.max_pool = nn.MaxPool2d(3, 1, 1)

    def forward(self, x: Tensor) -> Tensor:
        s = self.spatial(x)
        dx, dy = s[:, :, 0, :, :], s[:, :, 1, :, :]
        u = torch.sqrt(torch.pow(dx, 2) + torch.pow(dy, 2))
        y = self.max_pool(u)
        return y


class ConvConv(nn.Module):
    def __init__(self, a_channels, b_channels, c_channels):
        super(ConvConv, self).__init__()

        self.conv_1 = nn.Conv2d(a_channels, b_channels, (3, 3), padding=(1, 1))
        self.relu = nn.ReLU()
        self.conv_2 = nn.Conv2d(b_channels, c_channels, (3, 3), padding=(2, 2), dilation=(2, 2))

    def forward(self, x):
        x = self.conv_1(x)
        x = self.relu(x)
        x = self.conv_2(x)
        return x


class Attention(nn.Module):
    def __init__(self):
        super(Attention, self).__init__()

        self.conv_1 = ConvConv(3, 32, 32)
        self.conv_2 = ConvConv(32, 64, 128)
        self.conv_3 = ConvConv(128, 64, 32)
        self.conv_4 = nn.Conv2d(32, 3, (1, 1))

        self.ed = EdgeDetect()

    def forward(self, x):
        # edge detect
        e = self.ed(x)
        x = x + e

        # attention
        x = self.conv_1(x)
        x = self.conv_2(x)
        x = self.conv_3(x)
        x = self.conv_4(x)

        return x


if __name__ == '__main__':
    block = Attention()
    input_tensor = torch.rand(1, 3, 64, 64)

    # Forward pass
    output = block(input_tensor)
    print(f"Input size: {input_tensor.size()}")
    print(f"Output size: {output.size()}")
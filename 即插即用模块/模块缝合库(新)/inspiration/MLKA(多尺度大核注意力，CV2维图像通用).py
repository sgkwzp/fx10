#coding:utf-8
import torch
import torch.nn as nn

"""
ConvNets可以通过利用更大的感受野在高级任务中与Transformer竞争。为了释放ConvNet在超分辨率方面的潜力，我们提出了一种多尺度注意力网络（MAN），将经典的多尺度机制与新兴的大核注意力耦合在一起。
特别是，我们提出了多尺度大核注意力（MLKA）和门控空间注意力单元（GSAU）。通过我们的MLKA，我们用多尺度和门方案修改大核注意力，以获得各种粒度级别的丰富注意力图，从而聚合全局和局部信息，避免潜在的阻塞伪影。
在GSAU中，我们整合了门机制和空间注意力，以去除不必要的线性层并聚合信息空间上下文。为了确认我们设计的有效性，我们通过简单地堆叠不同数量的MLKA和GSAU来评估具有多种复杂性的MAN。
实验结果表明，我们的 MAN 可以在最先进的性能和计算之间实现各种权衡。
"""

# Dummy definitions for the missing utilities
class Conv2d1x1(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=1)

    def forward(self, x):
        return self.conv(x)

class LayerNorm4D(nn.Module):
    def __init__(self, num_features):
        super().__init__()
        self.layer_norm = nn.GroupNorm(1, num_features)

    def forward(self, x):
        return self.layer_norm(x)

class GSAU(nn.Module):
    r"""Gated Spatial Attention Unit.

    Args:
        n_feats: Number of input channels

    """

    def __init__(self, n_feats: int) -> None:
        super().__init__()
        i_feats = n_feats * 2

        self.Conv1 = Conv2d1x1(n_feats, i_feats)
        self.DWConv1 = nn.Conv2d(
            n_feats, n_feats, 7, 1, 7 // 2, groups=n_feats)
        self.Conv2 = Conv2d1x1(n_feats, n_feats)

        self.norm = LayerNorm4D(n_feats)
        self.scale = nn.Parameter(torch.zeros(
            (1, n_feats, 1, 1)), requires_grad=True)

    def forward(self, x) -> torch.Tensor:
        shortcut = x.clone()

        x = self.Conv1(self.norm(x))
        a, x = torch.chunk(x, 2, dim=1)
        x = x * self.DWConv1(a)
        x = self.Conv2(x)

        return x * self.scale + shortcut

class MLKA(nn.Module):
    r"""Multi-scale Large Kernel Attention.

    Args:
        n_feats: Number of input channels

    """

    def __init__(self, n_feats: int) -> None:
        super().__init__()
        i_feats = 2 * n_feats

        self.n_feats = n_feats
        self.i_feats = i_feats
        self.norm = LayerNorm4D(n_feats)
        self.scale = nn.Parameter(torch.zeros(
            (1, n_feats, 1, 1)), requires_grad=True)

        self.LKA7 = nn.Sequential(
            nn.Conv2d(n_feats // 3, n_feats // 3, 7,
                      1, 7 // 2, groups=n_feats // 3),
            nn.Conv2d(n_feats // 3, n_feats // 3, 9, 1, (9 // 2)
                      * 4, groups=n_feats // 3, dilation=4),
            nn.Conv2d(n_feats // 3, n_feats // 3, 1, 1, 0))
        self.LKA5 = nn.Sequential(
            nn.Conv2d(n_feats // 3, n_feats // 3, 5,
                      1, 5 // 2, groups=n_feats // 3),
            nn.Conv2d(n_feats // 3, n_feats // 3, 7, 1, (7 // 2)
                      * 3, groups=n_feats // 3, dilation=3),
            nn.Conv2d(n_feats // 3, n_feats // 3, 1, 1, 0))
        self.LKA3 = nn.Sequential(
            nn.Conv2d(n_feats // 3, n_feats // 3,
                      3, 1, 1, groups=n_feats // 3),
            nn.Conv2d(n_feats // 3, n_feats // 3, 5, 1, (5 // 2)
                      * 2, groups=n_feats // 3, dilation=2),
            nn.Conv2d(n_feats // 3, n_feats // 3, 1, 1, 0))

        self.X3 = nn.Conv2d(n_feats // 3, n_feats // 3,
                            3, 1, 1, groups=n_feats // 3)
        self.X5 = nn.Conv2d(n_feats // 3, n_feats // 3, 5,
                            1, 5 // 2, groups=n_feats // 3)
        self.X7 = nn.Conv2d(n_feats // 3, n_feats // 3, 7,
                            1, 7 // 2, groups=n_feats // 3)

        self.proj_first = Conv2d1x1(n_feats, i_feats)
        self.proj_last = Conv2d1x1(n_feats, n_feats)

    def forward(self, x) -> torch.Tensor:
        shortcut = x.clone()

        x = self.norm(x)
        x = self.proj_first(x)
        a, x = torch.chunk(x, 2, dim=1)
        a_1, a_2, a_3 = torch.chunk(a, 3, dim=1)
        a = torch.cat([self.LKA3(a_1) * self.X3(a_1), self.LKA5(a_2)
                      * self.X5(a_2), self.LKA7(a_3) * self.X7(a_3)], dim=1)
        x = self.proj_last(x * a)

        return x * self.scale + shortcut

if __name__ == '__main__':
    n_feats = 3
    block = MLKA(n_feats)
    input = torch.rand(1, 3, 64, 64)
    output = block(input)
    print(input.size())
    print(output.size())

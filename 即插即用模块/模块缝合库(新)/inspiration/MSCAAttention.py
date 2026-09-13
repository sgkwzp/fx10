import torch
import torch.nn as nn
from mmengine.model import BaseModule


"""
这个代码实现了一个称为"MSCAAttention"（Multi-Scale Channel Attention）的注意力模块。这种注意力模块的主要作用是增强神经网络在特定通道和空间维度上的感知能力，从而有助于提取更加丰富和有用的特征。

这个注意力模块的特点如下：

多尺度特征提取：它使用了多个卷积核大小和填充的卷积操作，以提取不同尺度的特征信息。这些卷积操作包括一个具有较大卷积核的初始卷积 (self.conv0) 和多个后续的卷积操作（self.conv0_1，self.conv0_2，self.conv1_1，self.conv1_2，self.conv2_1，self.conv2_2），每个都针对不同的核大小和填充。

通道混合：在提取多尺度特征之后，通过对这些特征进行通道混合来整合不同尺度的信息。通道混合操作由最后一个卷积层 self.conv3 完成。

卷积注意力：最后，通过将通道混合后的特征与输入特征进行逐元素乘法，实现了一种卷积注意力机制。这意味着模块通过对不同通道的特征赋予不同的权重来选择性地强调或抑制输入特征。

总的来说，MSCAAttention的主要作用是增强特征图的表示能力，它能够自动学习特定通道和空间位置的重要性，从而更好地捕捉图像或特征图中的关键信息。这有助于改善模型在各种计算机视觉任务中的性能，例如图像分类、目标检测和语义分割。
"""

class MSCAAttention(BaseModule):

    def __init__(self,
                 channels,
                 kernel_sizes=[5, [1, 7], [1, 11], [1, 21]],
                 paddings=[2, [0, 3], [0, 5], [0, 10]]):
        super().__init__()
        self.conv0 = nn.Conv2d(
            channels,
            channels,
            kernel_size=kernel_sizes[0],
            padding=paddings[0],
            groups=channels)
        for i, (kernel_size,
                padding) in enumerate(zip(kernel_sizes[1:], paddings[1:])):
            kernel_size_ = [kernel_size, kernel_size[::-1]]
            padding_ = [padding, padding[::-1]]
            conv_name = [f'conv{i}_1', f'conv{i}_2']
            for i_kernel, i_pad, i_conv in zip(kernel_size_, padding_,
                                               conv_name):
                self.add_module(
                    i_conv,
                    nn.Conv2d(
                        channels,
                        channels,
                        tuple(i_kernel),
                        padding=i_pad,
                        groups=channels))
        self.conv3 = nn.Conv2d(channels, channels, 1)

    def forward(self, x):
        """Forward function."""

        u = x.clone()

        attn = self.conv0(x)

        # Multi-Scale Feature extraction
        attn_0 = self.conv0_1(attn)
        attn_0 = self.conv0_2(attn_0)

        attn_1 = self.conv1_1(attn)
        attn_1 = self.conv1_2(attn_1)

        attn_2 = self.conv2_1(attn)
        attn_2 = self.conv2_2(attn_2)

        attn = attn + attn_0 + attn_1 + attn_2
        # Channel Mixing
        attn = self.conv3(attn)

        # Convolutional Attention
        x = attn * u

        return x

if __name__ == '__main__':
    block = MSCAAttention(channels=64)
    input = torch.rand(64, 64, 9, 9)
    output = block(input)
    print(input.size())
    print(output.size())

#
# class MSCAAttention(BaseModule):
#     """Attention Module in Multi-Scale Convolutional Attention Module (MSCA).
#
#     Args:
#         channels (int): The dimension of channels.
#         kernel_sizes (list): The size of attention
#             kernel. Defaults: [5, [1, 7], [1, 11], [1, 21]].
#         paddings (list): The number of
#             corresponding padding value in attention module.
#             Defaults: [2, [0, 3], [0, 5], [0, 10]].
#     """
#
#     def __init__(self,
#                  channels,
#                  kernel_sizes=[5, [1, 7], [1, 11], [1, 21]],
#                  paddings=[2, [0, 3], [0, 5], [0, 10]]):
#         super().__init__()
#         self.conv0 = nn.Conv2d(
#             channels,
#             channels,
#             kernel_size=kernel_sizes[0],
#             padding=paddings[0],
#             groups=channels)
#         for i, (kernel_size,
#                 padding) in enumerate(zip(kernel_sizes[1:], paddings[1:])):
#             kernel_size_ = [kernel_size, kernel_size[::-1]]
#             padding_ = [padding, padding[::-1]]
#             conv_name = [f'conv{i}_1', f'conv{i}_2']
#             for i_kernel, i_pad, i_conv in zip(kernel_size_, padding_,
#                                                conv_name):
#                 self.add_module(
#                     i_conv,
#                     nn.Conv2d(
#                         channels,
#                         channels,
#                         tuple(i_kernel),
#                         padding=i_pad,
#                         groups=channels))
#         self.conv3 = nn.Conv2d(channels, channels, 1)
#
#     def forward(self, x):
#         """Forward function."""
#
#         u = x.clone()
#
#         attn = self.conv0(x)
#
#         # Multi-Scale Feature extraction
#         attn_0 = self.conv0_1(attn)
#         attn_0 = self.conv0_2(attn_0)
#
#         attn_1 = self.conv1_1(attn)
#         attn_1 = self.conv1_2(attn_1)
#
#         attn_2 = self.conv2_1(attn)
#         attn_2 = self.conv2_2(attn_2)
#
#         attn = attn + attn_0 + attn_1 + attn_2
#         # Channel Mixing
#         attn = self.conv3(attn)
#
#         # Convolutional Attention
#         x = attn * u
#
#         return x
#
#
# class MSCASpatialAttention(BaseModule):
#     """Spatial Attention Module in Multi-Scale Convolutional Attention Module
#     (MSCA).
#
#     Args:
#         in_channels (int): The dimension of channels.
#         attention_kernel_sizes (list): The size of attention
#             kernel. Defaults: [5, [1, 7], [1, 11], [1, 21]].
#         attention_kernel_paddings (list): The number of
#             corresponding padding value in attention module.
#             Defaults: [2, [0, 3], [0, 5], [0, 10]].
#         act_cfg (dict): Config dict for activation layer in block.
#             Default: dict(type='GELU').
#     """
#
#     def __init__(self,
#                  in_channels,
#                  attention_kernel_sizes=[5, [1, 7], [1, 11], [1, 21]],
#                  attention_kernel_paddings=[2, [0, 3], [0, 5], [0, 10]],
#                  act_cfg=dict(type='GELU')):
#         super().__init__()
#         self.proj_1 = nn.Conv2d(in_channels, in_channels, 1)
#         self.activation = build_activation_layer(act_cfg)
#         self.spatial_gating_unit = MSCAAttention(in_channels,
#                                                  attention_kernel_sizes,
#                                                  attention_kernel_paddings)
#         self.proj_2 = nn.Conv2d(in_channels, in_channels, 1)
#
#     def forward(self, x):
#         """Forward function."""
#
#         shorcut = x.clone()
#         x = self.proj_1(x)
#         x = self.activation(x)
#         x = self.spatial_gating_unit(x)
#         x = self.proj_2(x)
#         x = x + shorcut
#         return x
#
#
# class MSCABlock(BaseModule):
#     """Basic Multi-Scale Convolutional Attention Block. It leverage the large-
#     kernel attention (LKA) mechanism to build both channel and spatial
#     attention. In each branch, it uses two depth-wise strip convolutions to
#     approximate standard depth-wise convolutions with large kernels. The kernel
#     size for each branch is set to 7, 11, and 21, respectively.
#
#     Args:
#         channels (int): The dimension of channels.
#         attention_kernel_sizes (list): The size of attention
#             kernel. Defaults: [5, [1, 7], [1, 11], [1, 21]].
#         attention_kernel_paddings (list): The number of
#             corresponding padding value in attention module.
#             Defaults: [2, [0, 3], [0, 5], [0, 10]].
#         mlp_ratio (float): The ratio of multiple input dimension to
#             calculate hidden feature in MLP layer. Defaults: 4.0.
#         drop (float): The number of dropout rate in MLP block.
#             Defaults: 0.0.
#         drop_path (float): The ratio of drop paths.
#             Defaults: 0.0.
#         act_cfg (dict): Config dict for activation layer in block.
#             Default: dict(type='GELU').
#         norm_cfg (dict): Config dict for normalization layer.
#             Defaults: dict(type='SyncBN', requires_grad=True).
#     """
#
#     def __init__(self,
#                  channels,
#                  attention_kernel_sizes=[5, [1, 7], [1, 11], [1, 21]],
#                  attention_kernel_paddings=[2, [0, 3], [0, 5], [0, 10]],
#                  mlp_ratio=4.,
#                  drop=0.,
#                  drop_path=0.,
#                  act_cfg=dict(type='GELU'),
#                  norm_cfg=dict(type='SyncBN', requires_grad=True)):
#         super().__init__()
#         self.norm1 = build_norm_layer(norm_cfg, channels)[1]
#         self.attn = MSCASpatialAttention(channels, attention_kernel_sizes,
#                                          attention_kernel_paddings, act_cfg)
#         self.drop_path = DropPath(
#             drop_path) if drop_path > 0. else nn.Identity()
#         self.norm2 = build_norm_layer(norm_cfg, channels)[1]
#         mlp_hidden_channels = int(channels * mlp_ratio)
#         self.mlp = Mlp(
#             in_features=channels,
#             hidden_features=mlp_hidden_channels,
#             act_cfg=act_cfg,
#             drop=drop)
#         layer_scale_init_value = 1e-2
#         self.layer_scale_1 = nn.Parameter(
#             layer_scale_init_value * torch.ones(channels), requires_grad=True)
#         self.layer_scale_2 = nn.Parameter(
#             layer_scale_init_value * torch.ones(channels), requires_grad=True)
#
#     def forward(self, x, H, W):
#         """Forward function."""
#
#         B, N, C = x.shape
#         x = x.permute(0, 2, 1).view(B, C, H, W)
#         x = x + self.drop_path(
#             self.layer_scale_1.unsqueeze(-1).unsqueeze(-1) *
#             self.attn(self.norm1(x)))
#         x = x + self.drop_path(
#             self.layer_scale_2.unsqueeze(-1).unsqueeze(-1) *
#             self.mlp(self.norm2(x)))
#         x = x.view(B, C, N).permute(0, 2, 1)
#         return x
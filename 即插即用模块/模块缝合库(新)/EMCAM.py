import torch
import torch.nn as nn
from functools import partial
import math
from timm.models.layers import trunc_normal_tf_
from timm.models.helpers import named_apply

"""《EMCAD: Efficient Multi-scale Convolutional Attention Decoding for Medical Image Segmentation》CVPR2024
高效且有效的解码机制对于医学图像分割至关重要，尤其是在计算资源有限的场景中。然而，这些解码机制通常伴随着高昂的计算成本。为了解决这一问题，我们引入了 EMCAD，一种新的高效多尺度卷积注意力解码器，旨在优化性能和计算效率。
EMCAD 利用独特的多尺度深度卷积块，通过多尺度卷积显著增强特征图。EMCAD 还采用通道空间和分组（大核）门控注意力机制，这些机制在捕捉复杂的空间关系的同时，还能高度有效地关注显著区域。
通过采用组和深度卷积，EMCAD 非常高效且可扩展性好（例如，使用标准编码器时，只需要 1.91M 个参数和 0.381G FLOP）。我们对属于六个医学图像分割任务的 12 个数据集进行了严格的评估，
结果表明，EMCAD 实现了最先进的（SOTA）性能，#Params 和 #FLOPs 分别减少了 79.4% 和 80.3%。
此外，EMCAD 对不同编码器的适应性和在分割任务中的多功能性进一步确立了 EMCAD 作为一种有前途的工具的地位，推动医学图像分析领域朝着更高效、更准确的方向发展。
我们的实现可在 https://github.com/SLDGroup/EMCAD 上找到。
"""


# GCD function
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


# Weight initialization function
def _init_weights(module, name, scheme=''):
    if isinstance(module, nn.Conv2d) or isinstance(module, nn.Conv3d):
        if scheme == 'normal':
            nn.init.normal_(module.weight, std=.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif scheme == 'trunc_normal':
            trunc_normal_tf_(module.weight, std=.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif scheme == 'xavier_normal':
            nn.init.xavier_normal_(module.weight)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif scheme == 'kaiming_normal':
            nn.init.kaiming_normal_(module.weight, mode='fan_out', nonlinearity='relu')
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        else:
            # efficientnet-like
            fan_out = module.kernel_size[0] * module.kernel_size[1] * module.out_channels
            fan_out //= module.groups
            nn.init.normal_(module.weight, 0, math.sqrt(2.0 / fan_out))
            if module.bias is not None:
                nn.init.zeros_(module.bias)
    elif isinstance(module, nn.BatchNorm2d) or isinstance(module, nn.BatchNorm3d):
        nn.init.constant_(module.weight, 1)
        nn.init.constant_(module.bias, 0)
    elif isinstance(module, nn.LayerNorm):
        nn.init.constant_(module.weight, 1)
        nn.init.constant_(module.bias, 0)


# Activation layer
def act_layer(act, inplace=False, neg_slope=0.2, n_prelu=1):
    act = act.lower()
    if act == 'relu':
        return nn.ReLU(inplace)
    elif act == 'relu6':
        return nn.ReLU6(inplace)
    elif act == 'leakyrelu':
        return nn.LeakyReLU(neg_slope, inplace)
    elif act == 'prelu':
        return nn.PReLU(num_parameters=n_prelu, init=neg_slope)
    elif act == 'gelu':
        return nn.GELU()
    elif act == 'hswish':
        return nn.Hardswish(inplace)
    else:
        raise NotImplementedError(f'activation layer [{act}] is not found')


# Channel shuffle function
def channel_shuffle(x, groups):
    batchsize, num_channels, height, width = x.size()
    channels_per_group = num_channels // groups
    x = x.view(batchsize, groups, channels_per_group, height, width)
    x = torch.transpose(x, 1, 2).contiguous()
    x = x.view(batchsize, -1, height, width)
    return x


# Channel Attention Block (CAB)
class CAB(nn.Module):
    def __init__(self, in_channels, out_channels=None, ratio=16, activation='relu'):
        super(CAB, self).__init__()

        self.in_channels = in_channels
        self.out_channels = out_channels
        if self.in_channels < ratio:
            ratio = self.in_channels
        self.reduced_channels = self.in_channels // ratio
        if self.out_channels is None:
            self.out_channels = in_channels

        self.avg_pool = nn.AdaptiveAvgPool2d(32)  # Match input spatial dimensions
        self.max_pool = nn.AdaptiveMaxPool2d(32)  # Same as above

        self.activation = act_layer(activation, inplace=True)
        self.fc1 = nn.Conv2d(self.in_channels, self.reduced_channels, 1, bias=False)
        self.fc2 = nn.Conv2d(self.reduced_channels, self.out_channels, 1, bias=False)

        self.sigmoid = nn.Sigmoid()

        self.init_weights('normal')

    def init_weights(self, scheme=''):
        named_apply(partial(_init_weights, scheme=scheme), self)

    def forward(self, x):
        avg_pool_out = self.avg_pool(x)
        avg_out = self.fc2(self.activation(self.fc1(avg_pool_out)))

        max_pool_out = self.max_pool(x)
        max_out = self.fc2(self.activation(self.fc1(max_pool_out)))

        out = avg_out + max_out
        return self.sigmoid(out)



# Spatial Attention Block (SAB)
class SAB(nn.Module):
    def __init__(self, kernel_size=7, out_channels=64):  # Add out_channels parameter
        super(SAB, self).__init__()

        assert kernel_size in (3, 7, 11), 'kernel must be 3 or 7 or 11'
        padding = kernel_size // 2

        # Adjust the output channels to match MSCB input channels
        self.conv = nn.Conv2d(2, out_channels, kernel_size, padding=padding, bias=False)

        self.sigmoid = nn.Sigmoid()

        self.init_weights('normal')

    def init_weights(self, scheme=''):
        named_apply(partial(_init_weights, scheme=scheme), self)

    def forward(self, x):
        # Ensure x has a larger spatial dimension, otherwise no space to apply attention
        if x.size(2) > 1 and x.size(3) > 1:
            avg_out = torch.mean(x, dim=1, keepdim=True)
            max_out, _ = torch.max(x, dim=1, keepdim=True)
            x = torch.cat([avg_out, max_out], dim=1)
            x = self.conv(x)
        return self.sigmoid(x)




class MSDC(nn.Module):
    def __init__(self, in_channels, kernel_sizes, stride, activation='relu6', dw_parallel=True):
        super(MSDC, self).__init__()

        self.in_channels = in_channels
        self.kernel_sizes = kernel_sizes
        self.activation = activation
        self.dw_parallel = dw_parallel

        self.dwconvs = nn.ModuleList([
            nn.Sequential(
                nn.Conv2d(self.in_channels, self.in_channels, kernel_size, stride, kernel_size // 2,
                          groups=self.in_channels, bias=False),
                nn.BatchNorm2d(self.in_channels),
                act_layer(self.activation, inplace=True)
            )
            for kernel_size in self.kernel_sizes
        ])

        self.init_weights('normal')

    def init_weights(self, scheme=''):
        named_apply(partial(_init_weights, scheme=scheme), self)

    def forward(self, x):
        outputs = []
        for dwconv in self.dwconvs:
            dw_out = dwconv(x)
            outputs.append(dw_out)
            if self.dw_parallel == False:
                x = x + dw_out
        return outputs


# Multi-Scale Convolution Block (MSCB)
class MSCB(nn.Module):
    def __init__(self, in_channels, out_channels, stride, kernel_sizes=[1, 3, 5], expansion_factor=2, dw_parallel=True,
                 add=True, activation='relu6'):
        super(MSCB, self).__init__()

        self.in_channels = in_channels
        self.out_channels = out_channels
        self.stride = stride
        self.kernel_sizes = kernel_sizes
        self.expansion_factor = expansion_factor
        self.dw_parallel = dw_parallel
        self.add = add
        self.activation = activation
        self.n_scales = len(self.kernel_sizes)
        assert self.stride in [1, 2]

        self.use_skip_connection = True if self.stride == 1 else False

        self.ex_channels = int(self.in_channels * self.expansion_factor)
        self.pconv1 = nn.Sequential(
            nn.Conv2d(self.in_channels, self.ex_channels, 1, 1, 0, bias=False),
            nn.BatchNorm2d(self.ex_channels),
            act_layer(self.activation, inplace=True)
        )
        self.msdc = MSDC(self.ex_channels, self.kernel_sizes, self.stride, self.activation,
                         dw_parallel=self.dw_parallel)
        self.combined_channels = self.ex_channels * 1 if self.add else self.ex_channels * self.n_scales
        self.pconv2 = nn.Sequential(
            nn.Conv2d(self.combined_channels, self.out_channels, 1, 1, 0, bias=False),
            nn.BatchNorm2d(self.out_channels),
        )
        if self.use_skip_connection and (self.in_channels != self.out_channels):
            self.conv1x1 = nn.Conv2d(self.in_channels, self.out_channels, 1, 1, 0, bias=False)
        self.init_weights('normal')

    def init_weights(self, scheme=''):
        named_apply(partial(_init_weights, scheme=scheme), self)

    def forward(self, x):
        pout1 = self.pconv1(x)
        msdc_outs = self.msdc(pout1)
        dout = torch.cat(msdc_outs, dim=1) if not self.add else sum(msdc_outs)
        dout = channel_shuffle(dout, gcd(self.combined_channels, self.out_channels))
        out = self.pconv2(dout)
        if self.use_skip_connection:
            if self.in_channels != self.out_channels:
                x = self.conv1x1(x)
            return x + out
        else:
            return out


# EMCAM (CAB + SAB + MSCB)
class EMCAM(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1, kernel_sizes=[1, 3, 5], expansion_factor=2,
                 dw_parallel=True, add=True, activation='relu6'):
        super(EMCAM, self).__init__()

        self.cab = CAB(in_channels, out_channels, ratio=16, activation=activation)
        self.sab = SAB(kernel_size=7, out_channels=out_channels)  # Pass out_channels to SAB
        self.mscb = MSCB(in_channels, out_channels, stride, kernel_sizes=kernel_sizes,
                         expansion_factor=expansion_factor, dw_parallel=dw_parallel, add=add, activation=activation)

    def forward(self, x):
        x = self.cab(x)
        x = self.sab(x)
        x = self.mscb(x)

        return x


if __name__ == '__main__':
    input_tensor = torch.rand(1, 64, 32, 32)  # batch_size=1, in_channels=64, height=32, width=32
    block = EMCAM(in_channels=64, out_channels=64, stride=1, kernel_sizes=[1, 3, 5], expansion_factor=2,
                  dw_parallel=True, add=True, activation='relu6')
    output = block(input_tensor)

    # Output the shape of input and output tensors
    print(f"Input size: {input_tensor.size()}")
    print(f"Output size: {output.size()}")



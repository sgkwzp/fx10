from copy import deepcopy
from torch import nn
import torch
import numpy as np
import torch.nn.functional as F

class InitWeights_He(object):
    def __init__(self, neg_slope=1e-2):
        self.neg_slope = neg_slope

    def __call__(self, module):
        if isinstance(module, nn.Conv3d) or isinstance(module, nn.Conv2d) or isinstance(module, nn.ConvTranspose2d) or isinstance(module, nn.ConvTranspose3d):
            module.weight = nn.init.kaiming_normal_(module.weight, a=self.neg_slope)
            if module.bias is not None:
                module.bias = nn.init.constant_(module.bias, 0)


class ConvNormNonlinBlock3d(nn.Module):
    '''3d卷积+归一化+非线性 模块'''
    def __init__(self, in_channels, out_channels):
        super(ConvNormNonlinBlock3d, self).__init__()

        self.conv = nn.Conv3d(in_channels, out_channels, [3, 3, 3], stride=1, padding=1)
        self.norm = nn.InstanceNorm3d(out_channels, affine=True)
        self.nonlin = nn.LeakyReLU(negative_slope=1e-2, inplace=True)

    def forward(self, x):
        # print(f'ConvNormNonlinBlock3d input shape: {x.shape}')
        return self.nonlin(self.norm(self.conv(x)))


class StackedConvBlocks3d(nn.Module):
    '''多个3d卷积模块'''
    def __init__(self, in_channels, out_channels, num_blocks=2, basic_block=ConvNormNonlinBlock3d):
        super(StackedConvBlocks3d, self).__init__()

        self.blocks = nn.Sequential(
            *([basic_block(in_channels, out_channels)] +
              [basic_block(out_channels, out_channels) for _ in range(num_blocks - 1)]))

    def forward(self, x):
        # print(f'StackedConvBlocks3d input shape: {x.shape}')
        return self.blocks(x)


def ConvTranspose3d(in_channels, out_channels):
    return nn.ConvTranspose3d(in_channels, out_channels, kernel_size=3, stride=2, padding=1, output_padding=1)


def MaxPool3d():
    return nn.MaxPool3d(kernel_size=2, stride=2, padding=0)


class SDC(nn.Module):
    def __init__(self, in_channels, guidance_channels, kernel_size=3, stride=1,
                 padding=1, dilation=1, groups=1, bias=False, theta=0.7):
        super(SDC, self).__init__()
        self.conv = nn.Conv3d(in_channels, in_channels, kernel_size=kernel_size, stride=stride, padding=padding,
                              dilation=dilation, groups=groups, bias=bias)
        self.conv1 = Conv3dbn(guidance_channels, in_channels, kernel_size=3, padding=1)
        self.theta = theta
        self.guidance_channels = guidance_channels
        self.in_channels = in_channels
        self.kernel_size = kernel_size

        # initialize
        x_initial = torch.randn(in_channels, 1, kernel_size, kernel_size, kernel_size)
        x_initial = self.kernel_initialize(x_initial)

        self.x_kernel_diff = nn.Parameter(x_initial)
        self.x_kernel_diff[:, :, 0, 0, 0].detach()
        self.x_kernel_diff[:, :, 0, 0, 2].detach()
        self.x_kernel_diff[:, :, 0, 2, 0].detach()
        self.x_kernel_diff[:, :, 2, 0, 0].detach()
        self.x_kernel_diff[:, :, 0, 2, 2].detach()
        self.x_kernel_diff[:, :, 2, 0, 2].detach()
        self.x_kernel_diff[:, :, 2, 2, 0].detach()
        self.x_kernel_diff[:, :, 2, 2, 2].detach()

        guidance_initial = torch.randn(in_channels, 1, kernel_size, kernel_size, kernel_size)
        guidance_initial = self.kernel_initialize(guidance_initial)

        self.guidance_kernel_diff = nn.Parameter(guidance_initial)
        self.guidance_kernel_diff[:, :, 0, 0, 0].detach()
        self.guidance_kernel_diff[:, :, 0, 0, 2].detach()
        self.guidance_kernel_diff[:, :, 0, 2, 0].detach()
        self.guidance_kernel_diff[:, :, 2, 0, 0].detach()
        self.guidance_kernel_diff[:, :, 0, 2, 2].detach()
        self.guidance_kernel_diff[:, :, 2, 0, 2].detach()
        self.guidance_kernel_diff[:, :, 2, 2, 0].detach()
        self.guidance_kernel_diff[:, :, 2, 2, 2].detach()

    def kernel_initialize(self, kernel):
        kernel[:, :, 0, 0, 0] = -1

        kernel[:, :, 0, 0, 2] = 1
        kernel[:, :, 0, 2, 0] = 1
        kernel[:, :, 2, 0, 0] = 1

        kernel[:, :, 0, 2, 2] = -1
        kernel[:, :, 2, 0, 2] = -1
        kernel[:, :, 2, 2, 0] = -1

        kernel[:, :, 2, 2, 2] = 1

        return kernel

    def forward(self, x, guidance):
        guidance_channels = self.guidance_channels
        in_channels = self.in_channels
        kernel_size = self.kernel_size

        guidance = self.conv1(guidance)

        x_diff = F.conv3d(input=x, weight=self.x_kernel_diff, bias=self.conv.bias, stride=self.conv.stride, padding=1,
                          groups=in_channels)

        guidance_diff = F.conv3d(input=guidance, weight=self.guidance_kernel_diff, bias=self.conv.bias,
                                 stride=self.conv.stride, padding=1, groups=in_channels)

        # Ensure x_diff and guidance_diff have the same size
        if x_diff.size() != guidance_diff.size():
            raise ValueError(
                f"Size mismatch between x_diff ({x_diff.size()}) and guidance_diff ({guidance_diff.size()})")

        out = self.conv(x_diff * guidance_diff * guidance_diff)
        return out


class SDM(nn.Module):
    def __init__(self, in_channel, guidance_channels):
        super(SDM, self).__init__()
        self.sdc1 = SDC(in_channel, guidance_channels)
        self.relu = nn.ReLU(inplace=True)
        self.bn = nn.BatchNorm3d(in_channel)

    def forward(self, feature, guidance):
        boundary_enhanced = self.sdc1(feature, guidance)
        boundary = self.relu(self.bn(boundary_enhanced))
        boundary_enhanced = boundary + feature

        return boundary_enhanced


class Conv3dReLU(nn.Sequential):
    def __init__(
            self,
            in_channels,
            out_channels,
            kernel_size,
            padding=0,
            stride=1,
            use_batchnorm=True,
    ):
        conv = nn.Conv3d(
            in_channels,
            out_channels,
            kernel_size,
            stride=stride,
            padding=padding,
            bias=not (use_batchnorm),
        )
        relu = nn.ReLU(inplace=True)

        bn = nn.BatchNorm3d(out_channels)

        super(Conv3dReLU, self).__init__(conv, bn, relu)

class Conv3dbn(nn.Sequential):
    def __init__(
            self,
            in_channels,
            out_channels,
            kernel_size,
            padding=0,
            stride=1,
            use_batchnorm=True,
    ):
        conv = nn.Conv3d(
            in_channels,
            out_channels,
            kernel_size,
            stride=stride,
            padding=padding,
            bias=not (use_batchnorm),
        )

        bn = nn.BatchNorm3d(out_channels)

        super(Conv3dbn, self).__init__(conv, bn)


def softmax_helper(x):
    # copy from: https://github.com/MIC-DKFZ/nnUNet/blob/master/nnunet/utilities/nd_softmax.py
    rpt = [1 for _ in range(len(x.size()))]
    rpt[1] = x.size(1)
    x_max = x.max(1, keepdim=True)[0].repeat(*rpt)
    e_x = torch.exp(x - x_max)
    return e_x / e_x.sum(1, keepdim=True).repeat(*rpt)


class UNetSDM(nn.Module):
    def __init__(self, in_channels, out_channels, base_filters_num=32):
        super(UNetSDM, self).__init__()
        self.weightInitializer = InitWeights_He(1e-2)

        if base_filters_num == 32:
            features = [in_channels, 32, 64, 128, 256, 320, 320]
        elif base_filters_num == 64:
            features = [in_channels, 64, 128, 256, 512, 512, 512]

        self.down_0 = StackedConvBlocks3d(in_channels, features[1])
        self.pool_0 = MaxPool3d()
        self.down_1 = StackedConvBlocks3d(features[1], features[2])
        self.pool_1 = MaxPool3d()
        self.down_2 = StackedConvBlocks3d(features[2], features[3])
        self.pool_2 = MaxPool3d()
        self.down_3 = StackedConvBlocks3d(features[3], features[4])
        self.pool_3 = MaxPool3d()
        self.down_4 = StackedConvBlocks3d(features[4], features[5])
        self.pool_4 = MaxPool3d()

        self.bottleneck = StackedConvBlocks3d(features[5], features[6])

        self.AGC_4 = SDM(features[6], features[5])
        self.trans_4 = ConvTranspose3d(features[6], features[5])
        self.up_4 = StackedConvBlocks3d(features[5] * 2, features[5])
        self.AGC_3 = SDM(features[5], features[4])
        self.trans_3 = ConvTranspose3d(features[5], features[4])
        self.up_3 = StackedConvBlocks3d(features[4] * 2, features[4])
        self.AGC_2 = SDM(features[4], features[3])
        self.trans_2 = ConvTranspose3d(features[4], features[3])
        self.up_2 = StackedConvBlocks3d(features[3] * 2, features[3])
        self.AGC_1 = SDM(features[3], features[2])
        self.trans_1 = ConvTranspose3d(features[3], features[2])
        self.up_1 = StackedConvBlocks3d(features[2] * 2, features[2])
        self.AGC_0 = SDM(features[2], features[1])
        self.trans_0 = ConvTranspose3d(features[2], features[1])
        self.up_0 = StackedConvBlocks3d(features[1] * 2, features[1])

        self.seg_output_0 = nn.Conv3d(features[1], out_channels, kernel_size=1, bias=False)
        self.apply(self.weightInitializer)

    def forward(self, x, guidance_tensor):
        down_0 = self.down_0(x)
        pool_0 = self.pool_0(down_0)

        down_1 = self.down_1(pool_0)
        pool_1 = self.pool_1(down_1)

        down_2 = self.down_2(pool_1)
        pool_2 = self.pool_2(down_2)

        down_3 = self.down_3(pool_2)
        pool_3 = self.pool_3(down_3)

        down_4 = self.down_4(pool_3)
        pool_4 = self.pool_4(down_4)

        # print(f'bottleneck input shape: {pool_4.shape}')
        bottleneck = self.bottleneck(pool_4)
        # print(f'bottleneck output shape: {bottleneck.shape}')

        trans_4 = self.trans_4(bottleneck)
        up_4 = self.up_4(torch.cat((trans_4, self.AGC_4(bottleneck, down_4)), dim=1))

        trans_3 = self.trans_3(up_4)
        up_3 = self.up_3(torch.cat((trans_3, self.AGC_3(trans_4, down_3)), dim=1))

        trans_2 = self.trans_2(up_3)
        up_2 = self.up_2(torch.cat((trans_2, self.AGC_2(trans_3, down_2)), dim=1))

        trans_1 = self.trans_1(up_2)
        up_1 = self.up_1(torch.cat((trans_1, self.AGC_1(trans_2, down_1)), dim=1))

        trans_0 = self.trans_0(up_1)
        up_0 = self.up_0(torch.cat((trans_0, self.AGC_0(trans_1, down_0)), dim=1))

        seg_output_0 = self.seg_output_0(up_0)

        return seg_output_0

if __name__ == '__main__':
    import torch

    # 定义输入张量的形状
    input_shape = (1, 3, 64, 64, 64)  # (batch_size, channels, depth, height, width)

    # 创建输入张量
    input_tensor = torch.randn(input_shape)

    # 创建引导张量
    guidance_tensor = torch.randn((1, 2, 64, 64, 64))  # 假设引导张量与输入张量大小相同

    # 创建模型
    # model = SDM(in_channel=3, guidance_channels=2)
    model = UNetSDM(in_channels=3, out_channels=3)

    # 将模型设置为评估模式
    model.eval()

    # 打印输入张量的形状
    print("输入张量的形状:", input_tensor.shape)

    # 执行前向传播
    output_tensor = model(input_tensor, guidance_tensor)

    # 打印输出张量的形状
    print("输出张量的形状:", output_tensor.shape)

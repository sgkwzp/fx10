import torch
import torch.nn as nn
import torch.nn.functional as F


class SpaBlock(nn.Module):
    """
    空间域残差特征提取模块。

    通过两层卷积提取局部空间信息，增强纹理、边缘和邻域结构，
    并利用残差连接保留原始特征，缓解深层处理中的信息退化。
    """

    def __init__(self, nc):
        """
        初始化空间域残差模块。

        参数：
            nc：输入特征与输出特征的通道数。
        """
        super(SpaBlock, self).__init__()

        self.block = nn.Sequential(
            nn.Conv2d(nc, nc, 3, 1, 1),
            nn.LeakyReLU(0.1, inplace=True),
            nn.Conv2d(nc, nc, 3, 1, 1),
            nn.LeakyReLU(0.1, inplace=True)
        )

    def forward(self, x):
        """
        对输入特征进行局部空间增强，并将增强结果与原始输入进行残差融合。
        """
        return x + self.block(x)


class ProcessBlock(nn.Module):
    """
    空间域与频率域联合处理模块。

    空间分支负责提取局部纹理和边缘信息，频率分支负责建模全局亮度
    与结构信息。两类特征经过拼接和卷积融合后，再与输入进行残差连接。
    """

    def __init__(self, in_nc, spatial=True):
        """
        初始化空间—频率联合处理模块。

        参数：
            in_nc：输入特征的通道数。
            spatial：是否启用空间域处理分支。
        """
        super(ProcessBlock, self).__init__()

        self.spatial = spatial
        self.spatial_process = SpaBlock(in_nc) if spatial else nn.Identity()
        self.frequency_process = LightTopKFreBlock(
            nc=in_nc,
            top_k=in_nc
        )

        self.cat = (
            nn.Conv2d(2 * in_nc, in_nc, 1, 1, 0)
            if spatial
            else nn.Conv2d(in_nc, in_nc, 1, 1, 0)
        )

    def forward(self, x):
        """
        分别提取输入特征的空间域信息和频率域信息，
        完成特征融合后与原始输入进行残差叠加。
        """
        xori = x

        x_out_four = self.frequency_process(x)
        x_spatial = self.spatial_process(x)

        xcat = torch.cat([x_spatial, x_out_four], dim=1)

        x_out = (
            self.cat(xcat)
            if self.spatial
            else self.cat(x_out_four)
        )

        return x_out + xori


class LightTopKFreBlock(nn.Module):
    """
    轻量级频率域特征处理模块。

    通过傅里叶变换将输入特征分解为幅度和相位，分别对亮度信息
    与结构信息进行处理。利用可靠幅度通道引导幅度恢复，并融合
    原始相位和变换后相位，最后通过逆傅里叶变换返回空间域。
    """

    def __init__(self, nc, top_k):
        """
        初始化频率域特征处理模块。

        参数：
            nc：输入特征与输出特征的通道数。
            top_k：候选幅度通道数量，当前实现实际采用Top-1筛选。
        """
        super(LightTopKFreBlock, self).__init__()

        self.nc = nc
        self.top_k = top_k

        self.conv0 = nn.Conv2d(nc, nc, 1, 1, 0)

        self.process1_mag = nn.Sequential(
            nn.Conv2d(nc, nc, 1, 1, 0),
            nn.LeakyReLU(0.1, inplace=True),
            nn.Conv2d(nc, nc, 1, 1, 0)
        )

        self.process1_pha = nn.Sequential(
            nn.Conv2d(nc, nc, 1, 1, 0),
            nn.LeakyReLU(0.1, inplace=True),
            nn.Conv2d(nc, nc, 1, 1, 0)
        )

        self.process2_pha = nn.Sequential(
            nn.Conv2d(nc * 2, nc, 1, 1, 0),
            nn.LeakyReLU(0.1, inplace=True),
            nn.Conv2d(nc, nc, 1, 1, 0)
        )

        self.magGuideFusion = MagGuidedFusion(channels=nc)
        self.conv_out = nn.Conv2d(nc * 2, nc, 1, 1, 0)

    def forward(self, x):
        """
        将输入特征转换至频率域，对幅度和相位分别进行增强，
        完成幅度先验引导和相位信息融合后重建频谱，并返回空间域特征。
        """
        B, C, H, W = x.shape

        x_conv0 = self.conv0(x)

        x_freq = torch.fft.rfft2(
            x_conv0,
            norm='backward'
        )

        mag0 = torch.abs(x_freq)
        pha0 = torch.angle(x_freq)

        mag1 = self.process1_mag(mag0)
        pha1 = self.process1_pha(pha0)

        pha_cat = torch.cat(
            (pha0, pha1),
            dim=1
        )
        pha_out = self.process2_pha(pha_cat)

        mag_out, mag0_weight = self.magGuideFusion(
            mag0,
            mag1
        )

        real = mag_out * torch.cos(pha_out)
        imag = mag_out * torch.sin(pha_out)

        x_out_freq = torch.complex(real, imag)

        x_out = torch.fft.irfft2(
            x_out_freq,
            s=(H, W),
            norm='backward'
        )

        return x_out


class MagGuidedFusion(nn.Module):
    """
    幅度先验引导融合模块。

    计算原始幅度与变换后幅度之间的跨通道相似性，从原始幅度中
    选择匹配程度最高的可靠通道，并生成自适应权重引导当前幅度恢复。
    残差式融合可以减少错误先验对当前幅度特征的干扰。
    """

    def __init__(self, channels):
        """
        初始化幅度引导融合模块。

        参数：
            channels：输入幅度特征的通道数。
        """
        super(MagGuidedFusion, self).__init__()

        self.channels = channels

        self.expand_conv = nn.Conv2d(
            1,
            channels,
            kernel_size=1,
            stride=1,
            padding=0
        )

    def forward(self, mag0, mag1):
        """
        计算两组幅度特征之间的跨通道相似度，筛选最可靠的原始幅度通道，
        将其扩展为多通道权重，并以残差方式引导变换后幅度特征。
        """
        B, C, H, W = mag0.shape

        mag0_flat = mag0.view(B, C, -1)
        mag1_flat = mag1.view(B, C, -1)

        mag0_norm = F.normalize(
            mag0_flat,
            dim=-1
        )
        mag1_norm = F.normalize(
            mag1_flat,
            dim=-1
        )

        similarity_matrix = torch.bmm(
            mag0_norm,
            mag1_norm.transpose(1, 2)
        )

        similarity_scores = similarity_matrix.mean(dim=-1)

        top1_indices = torch.argmax(
            similarity_scores,
            dim=-1
        )

        mag0_top1 = torch.stack(
            [
                mag0[b, top1_indices[b]]
                for b in range(B)
            ],
            dim=0
        ).unsqueeze(1)

        mag0_expanded = self.expand_conv(mag0_top1)
        mag0_weight = torch.sigmoid(mag0_expanded)

        fused_features = mag1 * mag0_weight + mag1

        return fused_features, mag0_weight


class RFGM(nn.Module):
    """
    由多个ProcessBlock构成的图像恢复模块。

    通过多个空间—频率联合处理块提取不同层级的图像特征，
    并利用跨层拼接加强浅层细节与深层语义之间的信息传递。
    该模块在频率域恢复亮度和整体结构，在空间域补充局部纹理，
    从而减少连续处理过程中的特征丢失。
    """

    def __init__(self, nc, n=1):
        """
        初始化RFGM图像恢复模块。

        参数：
            nc：网络中间特征的通道数。
            n：预留的模块数量参数，当前版本中未参与网络构建。
        """
        super(RFGM, self).__init__()

        self.conv0 = nn.Sequential(
            nn.Conv2d(3, nc, 1, 1, 0),
            ProcessBlock(nc)
        )

        self.conv1 = ProcessBlock(nc)
        self.conv2 = ProcessBlock(nc)
        self.conv3 = ProcessBlock(nc)

        self.conv4 = nn.Sequential(
            ProcessBlock(nc * 2),
            nn.Conv2d(nc * 2, nc, 1, 1, 0)
        )

        self.conv5 = nn.Sequential(
            ProcessBlock(nc * 2),
            nn.Conv2d(nc * 2, nc, 1, 1, 0)
        )

        self.convout = nn.Sequential(
            ProcessBlock(nc * 2),
            nn.Conv2d(nc * 2, 3, 1, 1, 0)
        )

    def forward(self, x):
        """
        依次提取多层空间—频率特征，通过跨层拼接实现浅层与深层信息融合，
        最终将融合特征映射为与输入尺寸一致的三通道恢复结果。
        """
        x = self.conv0(x)

        x1 = self.conv1(x)
        x2 = self.conv2(x1)
        x3 = self.conv3(x2)

        x4 = self.conv4(
            torch.cat(
                (x2, x3),
                dim=1
            )
        )

        x5 = self.conv5(
            torch.cat(
                (x1, x4),
                dim=1
            )
        )

        xout = self.convout(
            torch.cat(
                (x, x5),
                dim=1
            )
        )

        return xout


if __name__ == '__main__':
    nc = 32

    block = RFGM(nc=nc).to('cuda')

    input = torch.rand(1, 3, 16, 16).to('cuda')

    output = block(input)

    print("Input size :", input.size())
    print("Output size:", output.size())
# import torch
# import torch.nn as nn
# import torch.fft as fft
#
# """
# 在这篇论文中，我们揭示了扩散 U-Net 的潜力，它被视为一种“免费午餐”，可以在生成过程中大幅提高质量。
# 我们首先研究了 U-Net 架构对去噪过程的关键贡献，并确定其主要骨干主要贡献于去噪，而其跳跃连接主要将高频特征引入解码器模块，导致网络忽略了骨干语义。
# 基于这一发现，我们提出了一种简单而有效的方法——称为“FreeU”——它可以提高生成质量，而无需额外的训练或微调。我们的关键见解是，战略性地重新加权源自 U-Net 跳跃连接和骨干特征图的贡献
# 以利用 U-Net 架构的两个组成部分的优势。在图像和视频生成任务上的有希望的结果表明，我们的 FreeU 可以轻松集成到现有的扩散模型中.
# """
#
# def Fourier_filter(x, threshold, scale):
#     # FFT
#     x_freq = fft.fftn(x, dim=(-2, -1))
#     x_freq = fft.fftshift(x_freq, dim=(-2, -1))
#
#     B, C, H, W = x_freq.shape
#     mask = torch.ones((B, C, H, W), device=x.device)
#
#     crow, ccol = H // 2, W // 2
#     mask[..., crow - threshold:crow + threshold, ccol - threshold:ccol + threshold] = scale
#     x_freq = x_freq * mask
#
#     # IFFT
#     x_freq = fft.ifftshift(x_freq, dim=(-2, -1))
#     x_filtered = fft.ifftn(x_freq, dim=(-2, -1)).real
#
#     return x_filtered
#
#
# class UNetModel(nn.Module):
#     def __init__(self, model_channels, num_classes=None):
#         super().__init__()
#         self.model_channels = model_channels
#         self.num_classes = num_classes
#         self.input_block = nn.Conv2d(3, model_channels, 3, padding=1)
#         self.middle_block = nn.Conv2d(model_channels, model_channels, 3, padding=1)
#         self.output_block = nn.Conv2d(model_channels, model_channels, 3, padding=1)
#         self.final = nn.Conv2d(model_channels, 3, 3, padding=1)  # Ensure output has 3 channels
#
#
# def timestep_embedding(timesteps, dim, repeat_only=False):
#     return torch.randn((timesteps.shape[0], dim))
#
#
# class Free_UNetModel(UNetModel):
#     def __init__(
#             self,
#             b1,
#             b2,
#             s1,
#             s2,
#             *args,
#             **kwargs
#     ):
#         super().__init__(*args, **kwargs)
#         self.b1 = b1
#         self.b2 = b2
#         self.s1 = s1
#         self.s2 = s2
#         # Define the time embedding layer
#         self.time_embed = nn.Linear(self.model_channels, self.model_channels)
#
#         if self.num_classes is not None:
#             self.label_emb = nn.Embedding(self.num_classes, self.model_channels)
#
#
#     def forward(self, x, timesteps=None, context=None, y=None, **kwargs):
#         assert (y is not None) == (
#                     self.num_classes is not None), "must specify y if and only if the model is class-conditional"
#         hs = []
#         t_emb = timestep_embedding(timesteps, self.model_channels)
#         emb = self.time_embed(t_emb)
#
#         if self.num_classes is not None:
#             emb = emb + self.label_emb(y)
#
#         h = x
#         h = self.input_block(h)  # First convolution
#         hs.append(h)
#         h = self.middle_block(h)  # Middle convolution
#         for module in [self.output_block, self.final]:  # Output convolutions
#             h = module(h)
#
#         return h


import torch
from torch.fft import fftn, ifftn, fftshift, ifftshift


def Fourier_filter(x, threshold, scale):
    # FFT
    x_freq = fftn(x, dim=(-2, -1))  # 对输入进行二维快速傅里叶变换（FFT）
    x_freq = fftshift(x_freq, dim=(-2, -1))  # 平移频域结果，使低频部分位于中心

    B, C, H, W = x_freq.shape
    mask = torch.ones((B, C, H, W)).cuda()  # 创建与输入形状相同的掩码，初始化为全1

    crow, ccol = H // 2, W // 2
    mask[..., crow - threshold:crow + threshold, ccol - threshold:ccol + threshold] = scale  # 将掩码中心区域设为指定的缩放值
    x_freq = x_freq * mask  # 将掩码应用于频域结果，得到滤波后的频域结果

    # IFFT
    x_freq = ifftshift(x_freq, dim=(-2, -1))  # 逆平移操作
    x_filtered = ifftn(x_freq, dim=(-2, -1)).real  # 对滤波后的频域结果进行逆傅里叶变换（IFFT），并取实部

    return x_filtered


class Free_UNetModel(UNetModel):
    """
    :param b1: decoder第一个阶段的骨干因子。
    :param b2: decoder第二个阶段的骨干因子。
    :param s1: decoder第一个阶段的跳跃因子。
    :param s2: decoder第二个阶段的跳跃因子。
    """

    def __init__(
            self,
            b1,
            b2,
            s1,
            s2,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.b1 = b1
        self.b2 = b2
        self.s1 = s1
        self.s2 = s2

    def forward(self, x, timesteps=None, context=None, y=None, **kwargs):
        """
        Apply the model to an input batch.
        :param x: 输入的[N x C x ...]张量。
        :param timesteps: 一个包含时间步长的一维批次。
        :param context: 通过交叉注意力插入的条件。
        :param y: 一个[N]张量的标签，如果是类别条件。
        :return: 输出的[N x C x ...]张量。
        """
        assert (y is not None) == (
                self.num_classes is not None
        ), "must specify y if and only if the model is class-conditional"
        hs = []
        t_emb = timestep_embedding(timesteps, self.model_channels, repeat_only=False)
        emb = self.time_embed(t_emb)

        if self.num_classes is not None:
            assert y.shape[0] == x.shape[0]
            emb = emb + self.label_emb(y)

        h = x.type(self.dtype)
        for module in self.input_blocks:
            h = module(h, emb, context)
            hs.append(h)
        h = self.middle_block(h, emb, context)
        for module in self.output_blocks:
            hs_ = hs.pop()

            # --------------- FreeU code -----------------------
            # 只对前两个阶段进行操作
            if h.shape[1] == 1280:
                hidden_mean = h.mean(1).unsqueeze(1)
                B = hidden_mean.shape[0]
                hidden_max, _ = torch.max(hidden_mean.view(B, -1), dim=-1, keepdim=True)
                hidden_min, _ = torch.min(hidden_mean.view(B, -1), dim=-1, keepdim=True)
                hidden_mean = (hidden_mean - hidden_min.unsqueeze(2).unsqueeze(3)) / (
                            hidden_max - hidden_min).unsqueeze(2).unsqueeze(3)

                h[:, :640] = h[:, :640] * ((self.b1 - 1) * hidden_mean + 1)
                hs_ = Fourier_filter(hs_, threshold=1, scale=self.s1)
            if h.shape[1] == 640:
                hidden_mean = h.mean(1).unsqueeze(1)
                B = hidden_mean.shape[0]
                hidden_max, _ = torch.max(hidden_mean.view(B, -1), dim=-1, keepdim=True)
                hidden_min, _ = torch.min(hidden_mean.view(B, -1), dim=-1, keepdim=True)
                hidden_mean = (hidden_mean - hidden_min.unsqueeze(2).unsqueeze(3)) / (
                            hidden_max - hidden_min).unsqueeze(2).unsqueeze(3)

                h[:, :320] = h[:, :320] * ((self.b2 - 1) * hidden_mean + 1)
                hs_ = Fourier_filter(hs_, threshold=1, scale=self.s2)
            # ---------------------------------------------------------

            h = th.cat([h, hs_], dim=1)
            h = module(h, emb, context)
        h = h.type(x.dtype)
        if self.predict_codebook_ids:
            return self.id_predictor(h)
        else:
            return self.out(h)



if __name__ == '__main__':
    block = Free_UNetModel(1.5, 1.2, 0.8, 0.5, model_channels=64, num_classes=10)

    input = torch.rand(32, 3, 256, 256)
    timesteps = torch.tensor([1])
    y = torch.tensor([1])

    # 调用模型进行前向传播，并保存输出到 output 变量中
    output = block(input, timesteps=timesteps, y=y)

    print("Input size:", input.size())
    print("Output size:", output.size())



# 1.5：b1，用于指定 FreeU 中的第一个模块的参数。它控制截断位置，以调整骨干特征的权重。
# 1.2：b2，用于指定 FreeU 中的第二个模块的参数。它控制截断位置，以调整跳跃连接特征的权重。
# 0.8：s1，用于指定 FreeU 中的第一个模块的参数。它控制截断的比例因子，以调整骨干特征的缩放。
# 0.5：s2，用于指定 FreeU 中的第二个模块的参数。它控制截断的比例因子，以调整跳跃连接特征的缩放。
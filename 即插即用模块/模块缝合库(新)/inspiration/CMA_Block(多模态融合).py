import math

import torch
import torch.fft
import torch.nn as nn
import torch.nn.functional as F

"""
Deepfakes 的广泛传播需要有效的方法来检测感知上令人信服的伪造图像。在本文中，我们旨在使用转换器模型在不同尺度上捕获微妙的操纵伪影。
特别是，我们引入了多模态多尺度 TRansformer （M2TR），它可以对不同大小的斑块进行操作，以检测不同空间级别图像中的局部不一致。
M2TR进一步学习检测频域中的伪造伪影，以通过精心设计的跨模态融合块来补充RGB信息。
"""

class CMA_Block(nn.Module):
    def __init__(self, in_channel, hidden_channel, out_channel):
        super(CMA_Block, self).__init__()

        self.conv1 = nn.Conv2d(
            in_channel, hidden_channel, kernel_size=1, stride=1, padding=0
        )
        self.conv2 = nn.Conv2d(
            in_channel, hidden_channel, kernel_size=1, stride=1, padding=0
        )
        self.conv3 = nn.Conv2d(
            in_channel, hidden_channel, kernel_size=1, stride=1, padding=0
        )

        self.scale = hidden_channel ** -0.5

        self.conv4 = nn.Sequential(
            nn.Conv2d(
                hidden_channel, out_channel, kernel_size=1, stride=1, padding=0
            ),
            nn.BatchNorm2d(out_channel),
            nn.LeakyReLU(0.2, inplace=True),
        )

    def forward(self, rgb, freq):
        _, _, h, w = rgb.size()

        q = self.conv1(rgb)
        k = self.conv2(freq)
        v = self.conv3(freq)

        q = q.view(q.size(0), q.size(1), q.size(2) * q.size(3)).transpose(
            -2, -1
        )
        k = k.view(k.size(0), k.size(1), k.size(2) * k.size(3))

        attn = torch.matmul(q, k) * self.scale
        m = attn.softmax(dim=-1)

        v = v.view(v.size(0), v.size(1), v.size(2) * v.size(3)).transpose(
            -2, -1
        )
        z = torch.matmul(m, v)
        z = z.view(z.size(0), h, w, -1)
        z = z.permute(0, 3, 1, 2).contiguous()

        output = rgb + self.conv4(z)

        return output


if __name__ == '__main__':
    in_channel = 64
    hidden_channel = 32
    out_channel = 64
    h = 64
    w = 64

    block = CMA_Block(in_channel, hidden_channel, out_channel)

    rgb_input = torch.rand(1, in_channel, h, w)
    freq_input = torch.rand(1, in_channel, h, w)

    output = block(rgb_input, freq_input)

    print("RGB Input size:", rgb_input.size())
    print("Freq Input size:", freq_input.size())
    print("Output size:", output.size())

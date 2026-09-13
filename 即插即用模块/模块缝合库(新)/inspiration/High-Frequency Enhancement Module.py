import torch
import torch.nn as nn

"""
在真实场景中，拍摄的图像经常会出现模糊、噪点等形式的图像退化，并且由于传感器的限制，人们通常只能获得低动态范围的图像。
为了获得高质量的图像，研究人员尝试了对照片进行各种图像恢复和增强操作，包括去噪、去模糊和高动态范围成像。然而，仅仅执行单一类型的图像增强仍然无法产生令人满意的图像。
在本文中，为了应对上述挑战，我们提出了复合细化网络来使用多曝光图像来解决这个问题。通过充分集成信息丰富的多重曝光输入，CRNet可以进行统一的图像恢复和增强。
为了提高图像细节的质量，CRNet通过池化层明确分离和加强高频和低频信息，使用专门设计的多分支块来有效融合这些频率。
为了增加感受野并完全集成输入功能，复合细化网络采用了高频增强模块，其中包括大核卷积和倒置瓶颈 ConvFFN。我们的模型在包围式图像恢复和增强挑战赛的第一赛道上获得了第三名，在测试指标和视觉质量方面都超过了以前的SOTA模型。
"""
class ConvFFN(nn.Module):

    def __init__(self, in_channels, out_channels, expend_ratio=4):
        super().__init__()

        internal_channels = in_channels * expend_ratio
        self.pw1 = nn.Conv2d(in_channels=in_channels, out_channels=internal_channels, kernel_size=1, stride=1,
                             padding=0, groups=1,bias=False)
        self.pw2 = nn.Conv2d(in_channels=internal_channels, out_channels=out_channels, kernel_size=1, stride=1,
                             padding=0, groups=1,bias=False)
        self.nonlinear = nn.GELU()

    def forward(self, x):
        x1 = self.pw1(x)
        x2 = self.nonlinear(x1)
        x3 = self.pw2(x2)
        x4 = self.nonlinear(x3)
        return x4 + x


class invertedBlock(nn.Module):
    def __init__(self, in_channel, out_channel,ratio=2):
        super(invertedBlock, self).__init__()
        internal_channel = in_channel * ratio
        self.relu = nn.GELU()
        ## 7*7卷积，并行3*3卷积
        self.conv1 = nn.Conv2d(internal_channel, internal_channel, 7, 1, 3, groups=in_channel,bias=False)

        self.convFFN = ConvFFN(in_channels=in_channel, out_channels=in_channel)
        self.layer_norm = nn.LayerNorm(in_channel)
        self.pw1 = nn.Conv2d(in_channels=in_channel, out_channels=internal_channel, kernel_size=1, stride=1,
                             padding=0, groups=1,bias=False)
        self.pw2 = nn.Conv2d(in_channels=internal_channel, out_channels=in_channel, kernel_size=1, stride=1,
                             padding=0, groups=1,bias=False)


    def hifi(self,x):

        x1=self.pw1(x)
        x1=self.relu(x1)
        x1=self.conv1(x1)
        x1=self.relu(x1)
        x1=self.pw2(x1)
        x1=self.relu(x1)
        x3 = x1+x

        x3 = x3.permute(0, 2, 3, 1).contiguous()
        x3 = self.layer_norm(x3)
        x3 = x3.permute(0, 3, 1, 2).contiguous()
        x4 = self.convFFN(x3)

        return x4

    def forward(self, x):
        return self.hifi(x)+x



if __name__ == '__main__':
    block = invertedBlock(in_channel=32,out_channel=32,ratio=2)
    input = torch.rand(8,32,224,224)
    output = block(input)
    print(input.size())
    print(output.size())

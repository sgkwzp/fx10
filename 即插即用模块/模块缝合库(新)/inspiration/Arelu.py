# https://github.com/densechen/AReLU/blob/master/activations/arelu.py


"""
AReLU：基于注意力的整流线性单元
2020年 jun 24日 · 陈登生， 李军， 徐凯 ·  编辑社交预览

元素激活函数通过影响表达能力和学习动态，在深度神经网络中起着关键作用。基于学习的激活功能最近获得了越来越多的关注和成功。
我们提出了一种新的视角，通过元素关注机制来表述可学习激活函数。在每个网络层中，
我们设计了一个注意力模块，该模块为预激活特征图学习一个元素级的、基于符号的注意力图。注意力图根据元素的符号来缩放元素。添加带有整流线性单元 （ReLU） 的注意力模块会导致正元素的放大和负元素的抑制，
两者都具有学习的数据自适应参数。我们创造了由此产生的激活函数 Attention-based Rectified Linear Unit （AReLU）。注意力模块本质上是学习输入激活部分的元素残差，因为 ReLU 可以被视为一种身份转换。
这使得网络训练更能抵抗梯度消失。习得的专注激活导致对特征图相关区域的集中激活。通过广泛的评估，我们发现AReLU显著提升了大多数主流网络架构的性能，每层只引入了两个额外的可学习参数。
值得注意的是，AReLU有助于在较小的学习率下进行快速网络训练，这使得它特别适合迁移学习和元学习的情况。我们的源代码已经发布（见 https://github.com/densechen/AReLU）。
"""



import torch
import torch.nn as nn
import torch.nn.functional as F


class AReLU(nn.Module):
    def __init__(self, alpha=0.90, beta=2.0):
        super().__init__()
        self.alpha = nn.Parameter(torch.tensor([alpha]))
        self.beta = nn.Parameter(torch.tensor([beta]))

    def forward(self, input):
        alpha = torch.clamp(self.alpha, min=0.01, max=0.99)
        beta = 1 + torch.sigmoid(self.beta)

        return F.relu(input) * beta - F.relu(-input) * alpha
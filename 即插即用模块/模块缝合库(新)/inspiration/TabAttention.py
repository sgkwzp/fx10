import torch
from torch import nn
from torch.functional import F
import math

"""TabAttention：在表格数据上有条件地学习注意力
医学数据分析通常使用机器学习算法将成像和表格数据处理结合起来。虽然之前的研究调查了注意力机制对深度学习模型的影响，但很少有人探索整合注意力模块和表格数据。
在本文中，我们介绍了 TabAttention，这是一种新颖的模块，它通过在表格数据上进行条件训练的注意力机制来增强卷积神经网络（CNN）的性能。
具体来说，我们通过添加使用多头自注意力来学习注意力图的时间注意力模块，将卷积块注意力模块扩展到 3D。
此外，我们通过集成表格数据嵌入来增强所有注意力模块。
我们的方法在胎儿出生体重 (FBW) 估计任务中得到验证，使用 92 个胎儿腹部超声视频扫描和胎儿生物测量。
我们的结果表明 TabAttention 优于临床医生和依赖表格和/或成像数据进行 FBW 预测的现有方法。
这种新颖的方法有可能改善结合成像和表格数据的各种临床工作流程中的计算机辅助诊断。
"""


class TabAttention(nn.Module):
    def __init__(self, input_dim, tab_dim=6, tabattention=True, cam_sam=True, temporal_attention=True):
        """
        TabAttention module for integrating attention learning conditionally on tabular data within CNNs.

        @param input_dim: Input dimensions in the format C,H,W,F
        @param tab_dim: Number of tabular data features
        @param tabattention: Turn on/off tabular embeddings (plain CBAM with TAM)
        @param cam_sam: Turn on/off Channel and Spatial Attention Modules
        @param temporal_attention: Turn on/off Temporal Attention Moudule
        """
        super(TabAttention, self).__init__()

        channel_dim, h, w, frame_dim = input_dim
        hw_size = (h, w)
        self.input_dim = input_dim
        self.tabattention = tabattention
        self.temporal_attention = temporal_attention
        self.cam_sam = cam_sam
        if self.cam_sam:
            self.channel_gate = ChannelGate(channel_dim, tabattention=tabattention, tab_dim=tab_dim)
            self.spatial_gate = SpatialGate(tabattention=tabattention, tab_dim=tab_dim, input_size=hw_size)
        if temporal_attention:
            self.temporal_gate = TemporalGate(frame_dim, tabattention=tabattention, tab_dim=tab_dim)

    def forward(self, x, tab=None):
        b, c, h, w, f = x.shape
        x_in = torch.permute(x, (0, 4, 1, 2, 3))
        x_in = torch.reshape(x_in, (b * f, c, h, w))
        if self.tabattention:
            tab_rep = tab.repeat(f, 1, 1)
        else:
            tab_rep = None

        if self.cam_sam:
            x_out = self.channel_gate(x_in, tab_rep)
            x_out = self.spatial_gate(x_out, tab_rep)
        else:
            x_out = x_in

        x_out = torch.reshape(x_out, (b, f, c, h, w))

        if self.temporal_attention:
            x_out = self.temporal_gate(x_out, tab)

        x_out = torch.permute(x_out, (0, 2, 3, 4, 1))  # b,c,h,w,f

        return x_out


class BasicConv(nn.Module):
    def __init__(self, in_planes, out_planes, kernel_size, stride=1, padding=0, dilation=1, groups=1, relu=True,
                 bn=True, bias=False):
        super(BasicConv, self).__init__()
        self.out_channels = out_planes
        self.conv = nn.Conv2d(in_planes, out_planes, kernel_size=kernel_size, stride=stride, padding=padding,
                              dilation=dilation, groups=groups, bias=bias)
        self.bn = nn.BatchNorm2d(out_planes, eps=1e-5, momentum=0.01, affine=True) if bn else None
        self.relu = nn.ReLU() if relu else None

    def forward(self, x):
        x = self.conv(x)
        if self.bn is not None:
            x = self.bn(x)
        if self.relu is not None:
            x = self.relu(x)
        return x


class Flatten(nn.Module):
    def forward(self, x):
        return x.view(x.size(0), -1)


class ChannelGate(nn.Module):
    def __init__(self, gate_channels, tabattention=True, tab_dim=6, reduction_ratio=16, pool_types=['avg', 'max']):
        super(ChannelGate, self).__init__()
        self.tabattention = tabattention
        self.tab_dim = tab_dim
        self.gate_channels = gate_channels
        self.mlp = nn.Sequential(
            Flatten(),
            nn.Linear(gate_channels, gate_channels // reduction_ratio),
            nn.ReLU(),
            nn.Linear(gate_channels // reduction_ratio, gate_channels)
        )
        self.pool_types = pool_types
        if tabattention:
            self.pool_types = ['avg', 'max', 'tab']
            self.tab_embedding = nn.Sequential(
                nn.Linear(tab_dim, gate_channels // reduction_ratio),
                nn.ReLU(),
                nn.Linear(gate_channels // reduction_ratio, gate_channels)
            )

    def forward(self, x, tab=None):
        channel_att_sum = None
        for pool_type in self.pool_types:
            if pool_type == 'avg':
                avg_pool = F.avg_pool2d(x, (x.size(2), x.size(3)), stride=(x.size(2), x.size(3)))
                channel_att_raw = self.mlp(avg_pool)
            elif pool_type == 'max':
                max_pool = F.max_pool2d(x, (x.size(2), x.size(3)), stride=(x.size(2), x.size(3)))
                channel_att_raw = self.mlp(max_pool)
            elif pool_type == 'lp':
                lp_pool = F.lp_pool2d(x, 2, (x.size(2), x.size(3)), stride=(x.size(2), x.size(3)))
                channel_att_raw = self.mlp(lp_pool)
            elif pool_type == 'lse':
                # LSE pool only
                lse_pool = logsumexp_2d(x)
                channel_att_raw = self.mlp(lse_pool)
            elif pool_type == 'tab':
                embedded = self.tab_embedding(tab)
                embedded = torch.reshape(embedded, (-1, self.gate_channels))
                pool = self.mlp(embedded)
                channel_att_raw = pool

            if channel_att_sum is None:
                channel_att_sum = channel_att_raw
            else:
                channel_att_sum = channel_att_sum + channel_att_raw

        scale = torch.sigmoid(channel_att_sum).unsqueeze(2).unsqueeze(3).expand_as(x)
        return x * scale


class TemporalMHSA(nn.Module):
    def __init__(self, input_dim=2, seq_len=16, heads=2):
        super(TemporalMHSA, self).__init__()

        self.input_dim = input_dim
        self.seq_len = seq_len
        self.embedding_dim = 4
        self.head_dim = self.embedding_dim // heads
        self.heads = heads
        self.qkv = nn.Linear(self.input_dim, self.embedding_dim * 3)
        self.rel = nn.Parameter(torch.randn([1, 1, seq_len, 1]), requires_grad=True)
        self.o_proj = nn.Linear(self.embedding_dim, 1)

    def forward(self, x):
        batch_size, seq_length, _ = x.size()
        qkv = self.qkv(x)
        qkv = qkv.reshape(batch_size, seq_length, self.heads, 3 * self.head_dim)
        qkv = qkv.permute(0, 2, 1, 3)  # [Batch, Head, SeqLen, Dims]
        q, k, v = qkv.chunk(3, dim=-1)

        d_k = q.size()[-1]
        k = k + self.rel.expand_as(k)
        attn_logits = torch.matmul(q, k.transpose(-2, -1))
        attn_logits = attn_logits / math.sqrt(d_k)
        attention = F.softmax(attn_logits, dim=-1)
        values = torch.matmul(attention, v)
        values = values.permute(0, 2, 1, 3)  # [Batch, SeqLen, Head, Dims]
        values = values.reshape(batch_size, seq_length, self.embedding_dim)  # [Batch, SeqLen, EmbeddingDim]
        x_out = self.o_proj(values)

        return x_out


class TemporalGate(nn.Module):
    def __init__(self, gate_frames, pool_types=['avg', 'max'], tabattention=True, tab_dim=6):
        super(TemporalGate, self).__init__()
        self.tabattention = tabattention
        self.tab_dim = tab_dim
        self.gate_frames = gate_frames
        self.pool_types = pool_types
        if tabattention:
            self.pool_types = ['avg', 'max', 'tab']
            self.tab_embedding = nn.Sequential(
                nn.Linear(tab_dim, gate_frames // 2),
                nn.ReLU(),
                nn.Linear(gate_frames // 2, gate_frames)
            )
        if tabattention:
            self.mhsa = TemporalMHSA(input_dim=3, seq_len=self.gate_frames)
        else:
            self.mhsa = TemporalMHSA(input_dim=2, seq_len=self.gate_frames)

    def forward(self, x, tab=None):
        avg_pool = F.avg_pool3d(x, (x.size(2), x.size(3), x.size(4))).reshape(-1, self.gate_frames, 1)
        max_pool = F.max_pool3d(x, (x.size(2), x.size(3), x.size(4))).reshape(-1, self.gate_frames, 1)

        if self.tabattention:
            embedded = self.tab_embedding(tab)
            tab_embedded = torch.reshape(embedded, (-1, self.gate_frames, 1))
            concatenated = torch.cat((avg_pool, max_pool, tab_embedded), dim=2)
        else:
            concatenated = torch.cat((avg_pool, max_pool), dim=2)

        scale = torch.sigmoid(self.mhsa(concatenated)).unsqueeze(2).unsqueeze(3).expand_as(x)

        return x * scale


def logsumexp_2d(tensor):
    tensor_flatten = tensor.view(tensor.size(0), tensor.size(1), -1)
    s, _ = torch.max(tensor_flatten, dim=2, keepdim=True)
    outputs = s + (tensor_flatten - s).exp().sum(dim=2, keepdim=True).log()
    return outputs


class ChannelPool(nn.Module):
    def forward(self, x):
        return torch.cat((torch.max(x, 1)[0].unsqueeze(1), torch.mean(x, 1).unsqueeze(1)), dim=1)


class SpatialGate(nn.Module):
    def __init__(self, tabattention=True, tab_dim=6, input_size=(8, 8)):
        super(SpatialGate, self).__init__()
        self.tabattention = tabattention
        self.tab_dim = tab_dim
        self.input_size = input_size
        kernel_size = 7
        self.compress = ChannelPool()
        in_planes = 3 if tabattention else 2
        self.spatial = BasicConv(in_planes, 1, kernel_size, stride=1, padding=(kernel_size - 1) // 2, relu=False)
        if self.tabattention:
            self.tab_embedding = nn.Sequential(
                nn.Linear(tab_dim, input_size[0] * input_size[1] // 2),
                nn.ReLU(),
                nn.Linear(input_size[0] * input_size[1] // 2, input_size[0] * input_size[1])
            )

    def forward(self, x, tab=None):
        x_compress = self.compress(x)
        if self.tabattention:
            embedded = self.tab_embedding(tab)
            embedded = torch.reshape(embedded, (-1, 1, self.input_size[0], self.input_size[1]))
            x_compress = torch.cat((x_compress, embedded), dim=1)

        x_out = self.spatial(x_compress)
        scale = torch.sigmoid(x_out)  # broadcasting
        return x * scale



if __name__ == '__main__':
    x_input = torch.randn(1, 64, 16, 16, 4)  # 随机生成的输入数据：1个样本，64个通道，空间尺寸16x16，4个时间序列帧
    tab_input = torch.randn(1, 1, 6)         # 随机生成的表格数据：1个样本，1个子批次（这里的1可能用于保持维度一致性），6个特征
    input_dim = (64, 16, 16, 4)              # 定义输入数据的维度：通道数64，空间尺寸16x16，时间序列帧数4
    block = TabAttention(input_dim=input_dim, tab_dim=6)  # 初始化TabAttention模块，传入上述维度和表格特征数
    output = block(x_input, tab_input)       # 使用TabAttention模块处理输入数据和表格数据
    print(x_input.size())                    # 打印输入数据的尺寸
    print(output.size())                     # 打印输出数据的尺寸

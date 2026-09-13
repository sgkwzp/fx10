import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class XCA(nn.Module):
    """ Cross-Covariance Attention (XCA)
    Operation where the channels are updated using a weighted sum. The weights are obtained from the (softmax
    normalized) Cross-covariance matrix (Q^T \\cdot K \\in d_h \\times d_h)
    """

    def __init__(self, dim, num_heads=8, qkv_bias=False, attn_drop=0., proj_drop=0.):
        super().__init__()
        self.num_heads = num_heads
        self.temperature = nn.Parameter(torch.ones(num_heads, 1, 1))
        self.qkv = nn.Linear(dim, dim * 3, bias=qkv_bias)
        self.attn_drop = nn.Dropout(attn_drop)
        self.proj = nn.Linear(dim, dim)
        self.proj_drop = nn.Dropout(proj_drop)

    def forward(self, x):
        B, N, C = x.shape  # torch.Size([32, 784, 128])
        qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, C // self.num_heads).permute(2, 0, 3, 4,
                                                                                        1)  # torch.Size([3, 32, 8, 16, 784])
        q, k, v = qkv.unbind(0)  # q, k, v = torch.Size([32, 8, 16, 784])
        q = torch.nn.functional.normalize(q, dim=-1)  # torch.Size([32, 8, 16, 784])
        k = torch.nn.functional.normalize(k, dim=-1)  # torch.Size([32, 8, 16, 784])

        # Cross-Covariance Attention
        attn = (q @ k.transpose(-2, -1)) * self.temperature  # torch.Size([32, 8, 16, 16])
        attn = attn.softmax(dim=-1)  # torch.Size([32, 8, 16, 16])
        attn = self.attn_drop(attn)  # torch.Size([32, 8, 16, 16])
        x1 = (attn @ v).permute(0, 3, 1, 2).reshape(B, N, C)  # torch.Size([32, 784, 128])
        x1 = self.proj(x1)  # torch.Size([32, 784, 128])
        x1 = self.proj_drop(x1)  # torch.Size([32, 784, 128])

        # Linear Angular Attention
        theta = torch.acos((q * k).sum(dim=-1) / (q.norm(dim=-1) * k.norm(dim=-1)))  # 计算角度
        sim = 1 - theta / math.pi  # 相似度
        attn_angular = sim.softmax(dim=-1)  # 归一化
        x2 = (attn_angular @ v).permute(0, 3, 1, 2).reshape(B, N, C)  # 计算线性角注意力的输出
        x2 = self.proj(x2)  # 线性变换
        x2 = self.proj_drop(x2)  # 丢弃

        # Combine XCA and LAA
        x = x1 + x2  # 融合两种注意力机制的输出
        return x


if __name__ == '__main__':
    model = XCA(dim=128, num_heads=8, qkv_bias=False, attn_drop=0.1, proj_drop=0.1)
    input_tensor = torch.rand(32, 784, 128)  # 输入数据的形状 (B, N, C)
    output_tensor = model(input_tensor)
    print("Input size:", input_tensor.size())
    print("Output size:", output_tensor.size())

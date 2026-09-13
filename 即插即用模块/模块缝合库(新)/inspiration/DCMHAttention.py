import torch
import torch.nn as nn
import torch.nn.functional as F


class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-5):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        mean_square = x.pow(2).mean(-1, keepdim=True)
        norm_x = x * torch.rsqrt(mean_square + self.eps)
        return self.weight * norm_x


class DynamicWeightProjection(nn.Module):
    def __init__(self, num_heads, query_input_dim, dynamic_squeeze_ratio=16, dynamic_w_hidden_dim=128, use_sw=False):
        super().__init__()
        self.num_heads = num_heads
        self.query_input_dim = query_input_dim
        self.dynamic_squeeze_ratio = dynamic_squeeze_ratio
        self.dynamic_w_hidden_dim = dynamic_w_hidden_dim
        self.use_sw = use_sw

        self.dw1 = nn.Parameter(torch.zeros(query_input_dim, 4, dynamic_w_hidden_dim))
        self.qkw = nn.Parameter(torch.zeros(4, dynamic_w_hidden_dim, num_heads // dynamic_squeeze_ratio, num_heads))

        self.dw_activation = nn.Tanh()
        self.dw1_norm = RMSNorm(dynamic_w_hidden_dim)

        self.sw = nn.Parameter(torch.eye(num_heads).expand(2, num_heads, num_heads))

    def forward(self, query_vec):
        # B: batch size, T: sequence length, D: input dimension
        B, T, D = query_vec.size()

        # Dynamic weight hidden layer
        dw_hidden = torch.einsum('btd,dck->btck', query_vec, self.dw1)  # B, T, 4, K
        dw_hidden = self.dw_activation(dw_hidden)

        # Weight computation
        w1, w2 = torch.split(torch.einsum('btck,ckim->btkim', dw_hidden, self.qkw), self.qkw.size(2) // 2, dim=-2)

        # Normalization
        w1 = self.dw1_norm(w1)
        return w1, w2


class DCMHAttention(nn.Module):
    def __init__(self, num_heads, dim, head_dim):
        super().__init__()
        self.num_heads = num_heads
        self.head_dim = head_dim
        self.scale = head_dim ** -0.5

        self.wqkv = nn.Linear(dim, 3 * num_heads * head_dim, bias=False)
        self.wo = nn.Linear(dim, dim, bias=False)
        self.dyn_w_proj = DynamicWeightProjection(num_heads, dim)

    def forward(self, x):
        B, T, D = x.size()
        qkv = self.wqkv(x).view(B, T, self.num_heads, 3 * self.head_dim)
        q, k, v = qkv.split(self.head_dim, dim=-1)

        q = q.transpose(1, 2)  # B, num_heads, T, head_dim
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)

        q = q * self.scale
        attn_scores = torch.matmul(q, k.transpose(-2, -1))  # B, num_heads, T, T
        attn_probs = F.softmax(attn_scores, dim=-1)

        context = torch.matmul(attn_probs, v)  # B, num_heads, T, head_dim
        context = context.transpose(1, 2).contiguous().view(B, T, D)  # B, T, num_heads * head_dim

        output = self.wo(context)
        return output

if __name__ == '__main__':
    # 模型参数
    num_heads = 8
    dim = 64
    head_dim = 64 // num_heads

    # 初始化 DCMHAttention 模块
    model = DCMHAttention(num_heads, dim, head_dim)

    # 创建一个随机输入张量
    input_tensor = torch.rand(2, 10, dim)  # (批次大小, 序列长度, 嵌入维度)

    # 运行前向传递
    output = model(input_tensor)

    # 输出输入张量和输出张量的形状
    print("输入大小:", input_tensor.size())
    print("输出大小:", output.size())



import torch
import torch.nn as nn
from torch.nn import functional as F


def cluster_and_merge(x, cluster_num, subsample_factor=4):
    B, N, C = x.shape
    device = x.device
    K = cluster_num

    x_proj = x

    # 对特征进行归一化，形状为 (B, N, D)，其中 D 可以是投影维度或原始通道数 C
    x_norm = F.normalize(x_proj, dim=-1)

    # 确保采样数量 S 至少为 2K，同时不超过总 token 数 N
    S = min(N, max(2 * K, subsample_factor * K))

    samples_per_region = S // K
    sub_idx = []
    for i in range(K):
        start_idx = i * (N // K)
        end_idx = (i + 1) * (N // K) if i < K - 1 else N
        region_size = end_idx - start_idx
        n_samples = min(samples_per_region, region_size)

        if region_size > 0:
            region_perm = torch.randperm(region_size, device=device)[:n_samples]
            sub_idx.append(start_idx + region_perm)

    # 如果采样数量不足 S，则从剩余 token 中继续随机补充
    sub_idx = torch.cat(sub_idx)
    if len(sub_idx) < S:
        remaining = S - len(sub_idx)
        all_idx = torch.arange(N, device=device)
        mask = torch.ones(N, dtype=torch.bool, device=device)
        mask[sub_idx] = False
        additional = all_idx[mask][torch.randperm((~mask).sum(), device=device)[:remaining]]
        sub_idx = torch.cat([sub_idx, additional])

    # 取出子采样后的归一化 token，形状为 (B, S, D)
    x_norm_sub = x_norm[:, sub_idx]

    # 计算余弦相似度，即归一化后的点积
    sim_sub = x_norm_sub @ x_norm_sub.transpose(1, 2)  # (B, S, S)
    torch.diagonal(sim_sub, dim1=1, dim2=2).fill_(-1)

    # 计算 top-k 相似度的均值
    k = min(K, S - 1)
    sim_topk_sub, _ = torch.topk(sim_sub, k=k, dim=-1)  # (B, S, k)
    density_sub = sim_topk_sub.mean(dim=-1)  # (B, S)
    density_sub = density_sub + torch.rand_like(density_sub) * 1e-6

    # 构建高密度点掩码
    mask_higher_density = (density_sub[:, None, :] > density_sub[:, :, None]).float()  # (B, S, S)

    # 对于密度更高的点，保留相似度；否则设置为极小值
    masked_sim_sub = sim_sub * mask_higher_density - 1e9 * (1.0 - mask_higher_density)

    # 计算每个点与更高密度点之间的最大相似度
    max_sim_to_higher, _ = masked_sim_sub.max(dim=-1)  # (B, S)

    # 将相似度转换为距离：δ = 1 - similarity
    delta_sub = 1.0 - max_sim_to_higher  # (B, S)

    # 处理局部密度最大的点，即不存在更高密度邻居的点
    max_density_mask_sub = (mask_higher_density.sum(dim=-1) == 0)  # (B, S)

    # 对于密度最大的点，使用子采样集合中的最大距离
    min_sim_global = sim_sub.min(dim=-1)[0]  # (B, S)
    max_dist_global = 1.0 - min_sim_global
    delta_sub[max_density_mask_sub] = max_dist_global[max_density_mask_sub]

    # 确保 delta 非负
    delta_sub = torch.clamp(delta_sub, min=0.0)

    # 计算得分：γ = ρ × δ
    score_sub = density_sub * delta_sub  # (B, S)

    # 选择得分最高的 K 个点作为聚类中心
    _, center_idx_in_sub = torch.topk(score_sub, k=K, dim=-1)  # (B, K)

    # 将子采样索引映射回原始 token 索引
    center_idx = sub_idx[center_idx_in_sub]  # (B, K)

    # 获取聚类中心的归一化特征表示
    centers_norm = torch.gather(
        x_norm,
        1,
        center_idx[..., None].expand(B, K, x_norm.shape[-1])
    )  # (B, K, D)

    # 使用余弦相似度，与聚类中心选择过程保持一致
    sim_token_center = x_norm @ centers_norm.transpose(1, 2)  # (B, N, K)

    # 将每个 token 分配给相似度最高的聚类中心
    assign_idx = sim_token_center.argmax(dim=-1)  # (B, N)

    # 加权合并
    # 使用原始未投影的 token 进行合并，以保证输出质量
    out = x.new_zeros(B, K, C)

    # 对分配结果进行 one-hot 编码
    one_hot = F.one_hot(assign_idx, num_classes=K).type_as(x)  # (B, N, K)

    # 统计每个聚类中的 token 数量
    cluster_counts = one_hot.sum(dim=1, keepdim=True).clamp(min=1e-6)  # (B, 1, K)

    # 加权平均：先计算每个聚类内 token 的和，再进行归一化
    out = torch.einsum("bnc,bnk->bkc", x, one_hot) / cluster_counts.transpose(1, 2)

    return out


class SAA(nn.Module):
    def __init__(self, dim, num_heads=8, qkv_bias=False, qk_scale=None, attn_drop=0., proj_drop=0., c_ratio=0.5,
                 M=0.03):
        super(SAA, self).__init__()
        assert dim % num_heads == 0, f"dim {dim} should be divided by num_heads {num_heads}."
        self.dim = dim
        self.num_heads = num_heads
        self.cr = int(dim * c_ratio)
        self.scale = qk_scale or (self.cr // num_heads) ** -0.5
        self.M = M  # NF 的比例，即前景 token 或保留 token 的比例

        # QKV 线性投影层
        self.q = nn.Linear(dim, self.cr, bias=qkv_bias)
        self.k = nn.Linear(dim, self.cr, bias=qkv_bias)
        self.v = nn.Linear(dim, dim, bias=qkv_bias)
        self.attn_drop = nn.Dropout(attn_drop)
        self.proj = nn.Linear(dim, dim)
        self.proj_drop = nn.Dropout(proj_drop)

    def forward(self, x, H, W, prev_attn=None, image=None):
        B, N, C = x.shape
        T = x  # B N C

        T_unimp = x
        NF = int(self.M * N)

        # 对背景 token 进行聚类并合并，得到平均后的压缩 token
        T_avg = cluster_and_merge(T_unimp, NF)

        # 特征范数保持
        norms = torch.norm(T_unimp, dim=-1)  # B x num_unimp
        max_norm = norms.max(dim=-1, keepdim=True)[0].unsqueeze(-1)  # B x 1 x 1
        avg_norm = torch.norm(T_avg, dim=-1, keepdim=True)  # B x 1 x 1
        epsilon = 1e-6
        mask = avg_norm > epsilon  # B x 1 x 1
        scaled = (T_avg / (avg_norm + epsilon)) * max_norm
        T_avg = torch.where(mask, scaled, T_avg)

        # 构造压缩后的 Key-Value 输入
        KV_comp = T_avg
        K_size = KV_comp.shape[1]

        # 交叉注意力计算
        q = self.q(x).reshape(B, N, self.num_heads, self.cr // self.num_heads).permute(0, 2, 1, 3)
        k = self.k(KV_comp).reshape(B, K_size, self.num_heads, self.cr // self.num_heads).permute(0, 2, 1, 3)
        v = self.v(KV_comp).reshape(B, K_size, self.num_heads, C // self.num_heads).permute(0, 2, 1, 3)

        attn = (q @ k.transpose(-2, -1)) * self.scale
        attn = attn.softmax(dim=-1)
        attn = self.attn_drop(attn)

        out = (attn @ v).transpose(1, 2).reshape(B, N, C)
        out = self.proj(out)
        out = self.proj_drop(out)

        return out


if __name__ == '__main__':
    B = 2          # 批次大小
    H = 32
    W = 32
    N = H * W      # token 数量
    C = 64         # 通道数 / 嵌入维度

    block = SAA(
        dim=C,
        num_heads=8,
        qkv_bias=True,
        c_ratio=0.5,
        M=0.03
    ).to('cuda')

    x = torch.rand(B, N, C).to('cuda')

    out = block(x, H, W)

    print("input shape :", x.shape)
    print("output shape:", out.shape)
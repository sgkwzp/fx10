import torch
import torch.nn as nn

"""
Transformer 已成功应用于基于视频的 3D 人体姿态估计领域。然而，这些视频姿态转换器 （VPT） 的高计算成本使它们在资源受限的设备上不切实际。在本文中，我们提出了一个即插即用的修剪和恢复框架，称为沙漏分词器（HoT），用于从视频中进行基于Transformer的高效3D人体姿态估计。我们的 HoT 从修剪冗余帧的姿态标记开始，到恢复全长标记结束，从而在中间转换器模块中产生一些姿势标记，从而提高模型效率。为了有效地实现这一点，我们提出了一种令牌修剪集群（TPC），该集群可以动态选择一些具有高度语义多样性的代表性令牌，同时消除视频帧的冗余。此外，我们开发了一种令牌恢复注意力（TRA），以恢复基于所选令牌的详细时空信息，从而将网络输出扩展到原始的全长时间分辨率，以实现快速推理。在两个基准数据集（即Human3.6M和MPI-INF-3DHP）上的大量实验表明，与原始VPT模型相比，我们的方法可以同时实现高效率和估计精度。例如，应用于 Human3.6M 上的 MotionBERT 和 MixSTE，我们的 HoT 可以在不牺牲精度的情况下节省近 50% 的 FLOP，分别在仅降低 0.2% 的精度的情况下节省近 40% 的 FLOP。代码和模型可在 https://github.com/NationalGAILab/HoT 上获得。
"""

def index_points(points, idx):
    device = points.device
    B = points.shape[0]
    view_shape = list(idx.shape)
    view_shape[1:] = [1] * (len(view_shape) - 1)
    repeat_shape = list(idx.shape)
    repeat_shape[0] = 1
    batch_indices = torch.arange(B, dtype=torch.long).to(device).view(view_shape).repeat(repeat_shape)
    new_points = points[batch_indices, idx, :]
    return new_points


def cluster_dpc_knn(x, cluster_num, k, token_mask=None):
    with torch.no_grad():
        B, N, C = x.shape

        if cluster_num > N:
            raise ValueError(f"cluster_num should not be greater than the number of tokens (N). "
                             f"Received cluster_num={cluster_num}, N={N}.")

        dist_matrix = torch.cdist(x, x) / (C ** 0.5)

        if token_mask is not None:
            token_mask = token_mask > 0
            dist_matrix = dist_matrix * token_mask[:, None, :] + (dist_matrix.max() + 1) * (~token_mask[:, None, :])

        dist_nearest, index_nearest = torch.topk(dist_matrix, k=k, dim=-1, largest=False)

        density = (-(dist_nearest ** 2).mean(dim=-1)).exp()
        density = density + torch.rand(density.shape, device=density.device, dtype=density.dtype) * 1e-6

        if token_mask is not None:
            density = density * token_mask

        mask = density[:, None, :] > density[:, :, None]
        mask = mask.type(x.dtype)
        dist_max = dist_matrix.flatten(1).max(dim=-1)[0][:, None, None]
        dist, index_parent = (dist_matrix * mask + dist_max * (1 - mask)).min(dim=-1)

        score = dist * density

        _, index_down = torch.topk(score, k=cluster_num, dim=-1)

        dist_matrix = index_points(dist_matrix, index_down)

        idx_cluster = dist_matrix.argmin(dim=1)

        idx_batch = torch.arange(B, device=x.device)[:, None].expand(B, cluster_num)
        idx_tmp = torch.arange(cluster_num, device=x.device)[None, :].expand(B, cluster_num)
        idx_cluster[idx_batch.reshape(-1), index_down.reshape(-1)] = idx_tmp.reshape(-1)

    return index_down, idx_cluster


class TPCModule(nn.Module):
    def __init__(self, cluster_num, k):
        super().__init__()
        self.cluster_num = cluster_num
        self.k = k

    def forward(self, x, token_mask=None):
        current_cluster_num = min(self.cluster_num, x.shape[1])
        return cluster_dpc_knn(x, current_cluster_num, self.k, token_mask)


if __name__ == '__main__':
    # 初始化 TPC 模块
    cluster_num = 81
    k = 2
    tpc = TPCModule(cluster_num, k)

    input_2d = torch.rand(1, 243, 17, 2)  # (batch_size, frames, num_joints, channels)
    b, f, n, c = input_2d.shape

    # 重新排列以符合 TPC 模块的输入要求
    x = input_2d.view(b * f, n, c)

    # 使用 TPC 模块进行 token 修剪
    index_down, idx_cluster = tpc(x)

    # 输出修剪结果
    print(index_down.shape)
    print(idx_cluster.shape)

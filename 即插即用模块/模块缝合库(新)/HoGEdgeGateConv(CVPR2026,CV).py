import math
import einops
import torch
import torch.nn as nn
import torch.nn.functional as F


class EdgeConv(nn.Module):
    """
    EdgeConv: 轻量级边缘卷积模块
    对应论文中的 Edge Convolution

    作用：
    1. 使用1×k和k×1卷积提取水平与垂直方向边缘
    2. 增强结构边界和方向信息
    """

    def __init__(self,
                 in_channels,
                 mid_channels,
                 out_channels,
                 kernel_size=3,
                 bias=True):
        super().__init__()

        # 1×1卷积：降维，减少计算量
        self.in_proj = nn.Conv2d(
            in_channels=in_channels,
            out_channels=mid_channels,
            kernel_size=1,
            bias=bias)

        # 水平方向 strip convolution (1 × k)
        # 用于捕获水平边缘特征
        self.w_conv = nn.Conv2d(
            mid_channels,
            mid_channels,
            kernel_size=(1, kernel_size),
            stride=1,
            padding=(0, kernel_size // 2),
            groups=mid_channels)

        # 垂直方向 strip convolution (k × 1)
        # 用于捕获垂直边缘特征
        self.h_conv = nn.Conv2d(
            mid_channels,
            mid_channels,
            kernel_size=(kernel_size, 1),
            stride=1,
            padding=(kernel_size // 2, 0),
            groups=mid_channels
        )

        # 将两个方向特征融合
        self.out_proj = nn.Conv2d(
            in_channels=mid_channels * 2,
            out_channels=out_channels,
            kernel_size=1,
            bias=True
        )

    def forward(self, x):

        # 降维
        x = self.in_proj(x)

        # 水平边缘
        x_w = self.w_conv(x)

        # 垂直边缘
        x_h = self.h_conv(x)

        # 拼接两个方向
        x = torch.cat([x_w, x_h], dim=1)

        # 融合输出
        x = self.out_proj(x)

        return x


class HoGEdgeGateConv(nn.Module):
    """
    HoGEdgeGateConv (论文中的 DEGConv)

    核心思想：
    1. 使用HOG提取方向先验
    2. EdgeConv增强边缘
    3. gating机制动态调制特征
    4. spatial block策略增强局部结构
    """

    def __init__(self,
                 in_dim,
                 nbins,
                 cell_size=(8, 8)):
        super().__init__()

        self.nbins = nbins
        self.cell_size = cell_size

        # 方向特征编码模块
        # 将HOG特征转换成embedding
        self.hog_feat = nn.Sequential(
            nn.Conv2d(nbins, in_dim, kernel_size=1),

            # depthwise conv增强空间关系
            nn.Conv2d(in_dim, in_dim, kernel_size=3, padding=1, groups=in_dim, bias=False),

            nn.GroupNorm(in_dim // 8, in_dim),
            nn.ReLU(inplace=True),

            # 全局方向向量
            nn.AdaptiveAvgPool2d((1, 1))
        )

        # 生成 gating 权重
        self.weight = nn.Sequential(
            EdgeConv(in_channels=in_dim, mid_channels=in_dim // 2, out_channels=in_dim),
            nn.GroupNorm(in_dim // 8, in_dim)
        )

        # 主分支特征
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels=in_dim, out_channels=in_dim, kernel_size=1, stride=1),
            nn.GroupNorm(in_dim // 8, in_dim)
        )

        # 重建后的特征融合
        self.fuse_block = nn.Sequential(
            EdgeConv(in_channels=in_dim, mid_channels=in_dim // 2, out_channels=in_dim, kernel_size=3),
            nn.GroupNorm(in_dim // 8, in_dim)
        )

        self.sigmoid = nn.Sigmoid()

    def forward(self, x):

        # 保存残差
        residual = x

        # ------------------------------------------------
        # Step1: spatial block processing
        # 将feature map拆分为多个patch
        # ------------------------------------------------
        x = image2patches(x)

        # ------------------------------------------------
        # Step2: 计算HOG方向特征
        # ------------------------------------------------
        x_hog = self.get_hog_feature(x)

        # 将方向特征转为embedding
        x_hog = self.hog_feat(x_hog)

        # ------------------------------------------------
        # Step3: gating mechanism
        # ------------------------------------------------

        # 计算门控权重
        x1 = self.sigmoid(self.weight(x + x_hog))

        # 主特征分支
        x2 = self.conv(x)

        # gating调制
        x = x1 * x2

        # ------------------------------------------------
        # Step4: patch恢复
        # ------------------------------------------------
        x = patches2image(x)

        # residual连接
        x = x + residual

        # 再次进行边缘增强
        x = self.fuse_block(x)

        return x

    def get_hog_feature(self, x):
        """
        计算HOG方向特征
        对应论文 Direction Embedding Generation
        """

        # 计算灰度图
        x_mean = x.mean(dim=1, keepdim=True)

        B, _, H, W = x_mean.shape
        device = x_mean.device

        # Sobel算子
        sobel_x = torch.tensor(
            [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
            dtype=torch.float32).view(1, 1, 3, 3).to(device)

        sobel_y = torch.tensor(
            [[-1, -2, -1], [0, 0, 0], [1, 2, 1]],
            dtype=torch.float32).view(1, 1, 3, 3).to(device)

        # 梯度
        dx = F.conv2d(x_mean.float(), sobel_x, padding=1)
        dy = F.conv2d(x_mean.float(), sobel_y, padding=1)

        # ------------------------------------------------
        # 计算梯度方向
        # ------------------------------------------------

        gradient_dir = torch.atan2(dy, dx)

        # 转换到 [0,π]
        gradient_dir = torch.abs(gradient_dir)

        # ------------------------------------------------
        # cell划分
        # ------------------------------------------------

        cell_h, cell_w = self.cell_size

        H_cells = int(H / cell_h)
        W_cells = int(W / cell_w)

        # 裁剪到cell整除
        dirs_crop = gradient_dir[:, :, :H_cells * cell_h, :W_cells * cell_w]

        # reshape为cells
        dirs = dirs_crop.view(B, H_cells, W_cells, -1)

        # ------------------------------------------------
        # histogram of gradient
        # ------------------------------------------------

        bin_with = torch.pi / self.nbins

        bin_indices = (dirs / bin_with).floor().long()

        bin_indices = torch.clamp(bin_indices, 0, self.nbins - 1)

        bin_indices_flat = bin_indices.view(B * H_cells * W_cells, dirs.shape[-1])

        weight = []

        for i in range(bin_indices_flat.shape[0]):

            bins = bin_indices_flat[i]

            count = torch.bincount(bins, minlength=self.nbins)

            weight.append(count)

        weight = torch.stack(weight, dim=0).view(B, H_cells, W_cells, -1) / 64

        # ------------------------------------------------
        # 方向embedding
        # ------------------------------------------------

        start = torch.pi / (2 * self.nbins)

        hog_feature = torch.linspace(
            start,
            torch.pi - start,
            self.nbins
        ).to(device).repeat(B, H_cells, W_cells, 1) * weight

        return hog_feature.permute(0, 3, 1, 2)


def image2patches(x):
    """
    Spatial block strategy
    将feature map分块
    """
    x = einops.rearrange(
        x,
        'b c (hg h) (wg w) -> (hg wg b) c h w',
        hg=2,
        wg=2
    )
    return x


def patches2image(x):
    """
    恢复原图
    """
    x = einops.rearrange(
        x,
        '(hg wg b) c h w -> b c (hg h) (wg w)',
        hg=2,
        wg=2
    )
    return x


if __name__ == '__main__':
    B = 2
    C = 64
    H = 128
    W = 128

    block = HoGEdgeGateConv(
        in_dim=C,
        nbins=9,
        cell_size=(8, 8)
    ).to('cuda')

    x = torch.randn(B, C, H, W).to('cuda')

    y = block(x)

    print("Input shape :", x.shape)
    print("Output shape:", y.shape)
import torch
import torch.nn as nn
import torch.nn.functional as F


class GRN(nn.Module):
    """
    Global Response Normalization（全局响应归一化，ConvNeXt V2 风格）
    输入/输出张量形状均为: (B, C, H, W)

    作用：
    对每个通道在空间维度上的整体响应强度做归一化，
    再通过可学习参数进行缩放和偏移，从而增强特征稳定性。
    """
    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        # 每个通道一个可学习缩放参数，形状适配(B,C,H,W)广播
        self.gamma = nn.Parameter(torch.ones(1, dim, 1, 1))
        # 每个通道一个可学习偏置参数
        self.beta  = nn.Parameter(torch.zeros(1, dim, 1, 1))
        # 防止分母为0的小常数
        self.eps = eps

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # 在空间维度(H,W)上计算每个通道的L2范数
        # 输出形状: (B, C, 1, 1)
        gx = torch.norm(x, p=2, dim=(2, 3), keepdim=True)

        # 用通道自身的空间响应强度做归一化
        nx = x / (gx + self.eps)

        # 残差式输出：原特征 + 归一化调制 + 偏置
        return x + self.gamma * nx + self.beta


class PFGA(nn.Module):
    """
    Peripheral-Frequency Guided Aggregation（外围-频率引导聚合）
    这是一个 token mixer / spatial mixer，核心思想包括：

    1. 多个不同尺度的大核 depthwise 分支（外围感受野）
    2. 利用固定频率先验（Sobel / Laplacian / local variance）生成逐像素门控
    3. 对不同尺度分支进行像素级自适应加权融合
    4. 可选中心抑制（center suppression）
    """

    class Branch(nn.Module):
        """
        PFGA中的单个尺度分支
        每个分支负责一个卷积尺度 K，例如 9 / 15 / 31
        """
        def __init__(self, dim: int, K: int, center_suppress: bool = True):
            super().__init__()
            self.center_suppress = center_suppress

            # 用 DW(1xK) + DW(Kx1) 近似 DW(KxK)
            # 这样比直接KxK深度卷积计算量更低
            self.dw_h = nn.Conv2d(
                dim, dim,
                kernel_size=(1, K),
                padding=(0, K // 2),
                groups=dim,          # depthwise conv：每个通道单独卷积
                bias=False
            )
            self.dw_v = nn.Conv2d(
                dim, dim,
                kernel_size=(K, 1),
                padding=(K // 2, 0),
                groups=dim,
                bias=False
            )

            # 如果启用中心抑制，则增加一个3x3局部中心路径
            if self.center_suppress:
                self.dw_c = nn.Conv2d(
                    dim, dim,
                    kernel_size=3,
                    padding=1,
                    groups=dim,
                    bias=False
                )
                # 可学习中心抑制系数，按通道设置
                self.beta = nn.Parameter(torch.zeros(1, dim, 1, 1))
            else:
                # 不启用中心抑制时，不注册beta参数
                self.register_parameter('beta', None)
                self.dw_c = None

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            # 先经过分解的大核 depthwise 卷积，得到外围响应
            y = self.dw_v(self.dw_h(x))

            if self.center_suppress:
                # 中心局部响应
                center = self.dw_c(x)
                # 显式中心抑制：外围响应 - 可学习系数 * 中心响应
                # tanh将beta约束到[-1,1]
                y = y - torch.tanh(self.beta) * center

            return y

    def __init__(
        self,
        dim: int,
        K_list=(9, 15, 31),
        use_grn: bool = False,
        center_suppress: bool = True
    ):
        super().__init__()
        self.dim = dim
        self.K_list = K_list

        # 多尺度外围分支，每个K对应一个Branch
        self.branches = nn.ModuleList([
            PFGA.Branch(dim, K, center_suppress=center_suppress)
            for K in K_list
        ])

        # ---------------------------
        # 固定频率滤波器：Sobel x / Sobel y / Laplacian
        # 这些不是可学习参数，而是先验算子
        # ---------------------------
        sobel_x = torch.tensor(
            [[-1, 0, 1],
             [-2, 0, 2],
             [-1, 0, 1]],
            dtype=torch.float32
        ).view(1, 1, 3, 3)

        sobel_y = torch.tensor(
            [[-1, -2, -1],
             [ 0,  0,  0],
             [ 1,  2,  1]],
            dtype=torch.float32
        ).view(1, 1, 3, 3)

        laplace = torch.tensor(
            [[0,  1, 0],
             [1, -4, 1],
             [0,  1, 0]],
            dtype=torch.float32
        ).view(1, 1, 3, 3)

        # register_buffer：随模型一起转到GPU，但不参与训练
        self.register_buffer("sobel_x", sobel_x, persistent=False)
        self.register_buffer("sobel_y", sobel_y, persistent=False)
        self.register_buffer("laplace",  laplace,  persistent=False)

        # 1x1卷积：把3通道频率图映射成 K 个尺度的门控logits
        self.gate_head = nn.Conv2d(3, len(K_list), kernel_size=1, bias=True)

        self.use_grn = use_grn
        if use_grn:
            self.grn = GRN(dim)

    def _depthwise_filter(self, x: torch.Tensor, k: torch.Tensor) -> torch.Tensor:
        """
        对输入x的每个通道都应用同一个固定3x3卷积核k
        等价于 depthwise fixed filtering
        """
        B, C, H, W = x.shape

        # 把单个卷积核复制C份，使每个通道各自使用相同核
        w = k.repeat(C, 1, 1, 1)

        # groups=C 表示逐通道卷积
        return F.conv2d(x, w, padding=1, groups=C)

    def _freq_maps(self, x: torch.Tensor) -> torch.Tensor:
        """
        构建频率描述图（frequency maps）：
        1. 梯度幅值图
        2. Laplacian响应图
        3. 局部方差图

        输出形状: (B, 3, H, W)
        """

        # Sobel x方向响应
        gx = self._depthwise_filter(x, self.sobel_x)

        # Sobel y方向响应
        gy = self._depthwise_filter(x, self.sobel_y)

        # Laplacian响应
        lap = self._depthwise_filter(x, self.laplace)

        # 梯度幅值 = sqrt(gx^2 + gy^2)
        grad_mag = torch.sqrt(gx.pow(2) + gy.pow(2) + 1e-6)

        # 通过局部均值和平方均值计算方差
        mean  = F.avg_pool2d(x, 3, 1, 1)
        mean2 = F.avg_pool2d(x * x, 3, 1, 1)
        var   = torch.clamp(mean2 - mean * mean, min=0.)

        # 对通道求平均，得到单通道频率图
        f1 = grad_mag.mean(dim=1, keepdim=True)   # 梯度幅值图
        f2 = lap.abs().mean(dim=1, keepdim=True)  # Laplacian幅值图
        f3 = var.mean(dim=1, keepdim=True)        # 局部方差图

        # 拼接成3通道频率描述
        return torch.cat([f1, f2, f3], dim=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # -------------------------------------
        # 1) 先经过多个不同尺度的外围分支
        # peris 是一个列表，里面每个元素形状都是 (B,C,H,W)
        # -------------------------------------
        peris = [b(x) for b in self.branches]

        # -------------------------------------
        # 2) 根据输入特征提取频率图
        # -------------------------------------
        Freq = self._freq_maps(x)

        # 生成每个尺度的门控 logits，形状: (B, K, H, W)
        logits = self.gate_head(Freq)

        # 在尺度维度做softmax，得到逐像素尺度权重
        alpha = torch.softmax(logits, dim=1)

        # -------------------------------------
        # 3) 逐像素多尺度加权融合
        # -------------------------------------
        Y = 0.
        for i, y in enumerate(peris):
            # alpha[:, i:i+1, :, :] 取第i个尺度的权重图
            # 自动广播到所有通道
            Y = Y + y * alpha[:, i:i+1, :, :]

        # 可选GRN增强
        if self.use_grn:
            Y = self.grn(Y)

        return Y


class PFG(nn.Module):
    """
    主 PFG Block

    结构分成两部分：
    1. Token mixing：由 PFGA 完成空间/结构建模
    2. Channel mixing：由 GLU-like depthwise-MLP 完成通道交互

    同时包含：
    - GroupNorm
    - GRN
    - LayerScale
    - DropPath
    """

    def __init__(
        self,
        dim: int,
        groups_pw: int = 1,
        layerscale_init: float = 1e-6,
        act_layer=nn.GELU,
        drop: float = 0.0,
        drop_path: float = 0.0,
        pfga_K=(9, 15, 31),
        mlp_ratio: float = 4.0,
        dw_kernel: int = 3
    ):
        super().__init__()
        self.dim = dim

        # ---------------------------
        # 两个轻量归一化层：
        # 一个给 token mixing 前使用
        # 一个给 channel mixing 前使用
        # ---------------------------
        self.norm_dw = nn.GroupNorm(
            num_groups=min(32, dim),   # 注意：要求 dim 能被 num_groups 整除
            num_channels=dim
        )
        self.norm_pw = nn.GroupNorm(
            num_groups=min(32, dim),
            num_channels=dim
        )

        # token mixer：核心空间混合模块
        self.tm = PFGA(dim, K_list=pfga_K, use_grn=False)

        # token mixing 和 channel mixing 后都接一个GRN
        self.grn_dw = GRN(dim)
        self.grn_pw = GRN(dim)

        self.mlp_ratio = mlp_ratio
        self.dw_kernel = dw_kernel

        # 隐藏通道维度 E，通常为 dim * mlp_ratio
        E = max(dim, int(dim * self.mlp_ratio))

        # ---------------------------
        # GLU-like channel mixing
        # pw_in: 先把通道从 dim 扩展到 2E
        # 后面会一分为二，拆成 u 和 v
        # ---------------------------
        self.pw_in = nn.Conv2d(
            dim, 2 * E,
            kernel_size=1,
            bias=True,
            groups=groups_pw
        )

        # 对 v 分支做 depthwise 卷积，引入局部空间交互
        self.dw_v = nn.Conv2d(
            E, E,
            kernel_size=self.dw_kernel,
            padding=1,   # 这里默认 dw_kernel=3，如果改成5，这里最好改成 dw_kernel//2
            groups=E,
            bias=False
        )

        # 再把通道从 E 投影回 dim
        self.pw_out = nn.Conv2d(
            E, dim,
            kernel_size=1,
            bias=True,
            groups=groups_pw
        )

        # 激活函数，默认 GELU
        self.act = act_layer()

        # ---------------------------
        # LayerScale：残差分支缩放参数
        # 初值很小，训练更稳定
        # ---------------------------
        self.gamma_dw = nn.Parameter(torch.ones(dim) * layerscale_init)
        self.gamma_pw = nn.Parameter(torch.ones(dim) * layerscale_init)

        # DropPath 来自 timm
        from timm.layers import DropPath

        # 普通dropout
        self.dropout_dw = nn.Dropout(drop) if drop > 0 else nn.Identity()
        self.dropout_pw = nn.Dropout(drop) if drop > 0 else nn.Identity()

        # 随机深度
        self.drop_path = DropPath(drop_path) if drop_path > 0 else nn.Identity()

        # 初始化参数
        self._init_params()

    @torch.jit.ignore
    def no_weight_decay(self):
        # 告诉优化器：这些参数可以不做 weight decay
        return {'gamma_dw', 'gamma_pw'}

    def _init_params(self):
        """
        初始化卷积层和归一化层
        """
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                # Kaiming 初始化卷积核
                nn.init.kaiming_normal_(m.weight, mode="fan_out", nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.GroupNorm):
                # GroupNorm 缩放初始化为1，偏置为0
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # =====================================
        # (1) Token mixing / spatial mixing
        # =====================================

        # 先归一化
        y = self.norm_dw(x)

        # 再做 PFGA：多尺度外围频率引导聚合
        y = self.tm(y)

        # 激活
        y = self.act(y)

        # GRN增强
        y = self.grn_dw(y)

        # dropout
        y = self.dropout_dw(y)

        # 残差连接 + LayerScale + DropPath
        x = x + self.drop_path(
            y * self.gamma_dw.view(1, self.dim, 1, 1)
        )

        # =====================================
        # (2) Channel mixing / GLU-like mixing
        # =====================================

        # 先归一化
        z = self.norm_pw(x)

        # 1x1卷积把通道扩展到2E
        uv = self.pw_in(z)

        # 沿通道一分为二，拆成 u 和 v
        u, v = torch.chunk(uv, 2, dim=1)

        # v 分支做 depthwise 卷积
        v = self.dw_v(v)

        # GLU风格门控：silu(u) 作为门，乘以 v
        z = F.silu(u) * v

        # 再投影回原始通道数
        z = self.pw_out(z)

        # GRN增强
        z = self.grn_pw(z)

        # dropout
        z = self.dropout_pw(z)

        # 残差连接 + LayerScale + DropPath
        x = x + self.drop_path(
            z * self.gamma_pw.view(1, self.dim, 1, 1)
        )

        return x

if __name__ == '__main__':
    B = 2
    C = 4
    H = 2
    W = 2

    block = PFG(dim=C).to('cuda')
    input = torch.rand(B, C, H, W).to('cuda')
    output = block(input)

    print(input.size())
    print(output.size())
import torch
import torch.nn as nn
import torch.nn.functional as F


class APM(nn.Module):
    def __init__(self, in_channels, out_channels, time_dim=3, temperature=4, contrastive_att=True):
        super(APM, self).__init__()
        # Ensure out_channels is valid
        self.out_channels = max(out_channels, 1)

        self.time_dim = time_dim
        self.temperature = temperature
        self.contrastive_att = contrastive_att

        padding = (0, 0, 0, 0, (time_dim - 1) // 2, (time_dim - 1) // 2)
        self.padding = nn.ConstantPad3d(padding, value=0)

        self.semantic_mapping = nn.Conv3d(in_channels, self.out_channels, kernel_size=1, bias=False)
        if self.contrastive_att:
            self.x_mapping = nn.Conv3d(in_channels, self.out_channels, kernel_size=1, bias=False)
            self.n_mapping = nn.Conv3d(in_channels, self.out_channels, kernel_size=1, bias=False)
            self.contrastive_att_net = nn.Sequential(nn.Conv3d(self.out_channels, 1, kernel_size=1, bias=False), nn.Sigmoid())

    def forward(self, x):
        b, c, t, h, w = x.size()
        N = self.time_dim

        if t < N:
            N = t

        # 更改索引计算方式，确保它与期望的N值兼容
        indices = list(range(t))

        semantic = self.semantic_mapping(x)
        x_norm = F.normalize(semantic, p=2, dim=1)
        x_norm_padding = self.padding(x_norm)

        # 对于每个时间步，选择合适的邻居
        neighbor_norms = torch.zeros(b, self.out_channels, t, h, w, device=x.device)

        for i in range(t):
            start = max(i - N // 2, 0)
            end = min(i + N // 2 + 1, t)
            neighbor_slice = x_norm_padding[:, :, start:end, :, :]
            neighbor_norms[:, :, i, :, :] = neighbor_slice.mean(dim=2)

        # 假设 x_norm 和 neighbor_norms 已经正确计算了
        # 确保维度匹配，以便可以进行矩阵乘法
        x_flat = x_norm.view(b, -1, self.out_channels)  # [b, t*h*w, out_channels]
        neighbor_flat = neighbor_norms.view(b, self.out_channels, -1)  # [b, out_channels, t*h*w]

        # 计算相似度
        similarity = torch.bmm(x_flat, neighbor_flat) * self.temperature
        similarity = F.softmax(similarity, dim=-1)

        if self.contrastive_att:
            x_att = self.x_mapping(x.detach())
            n_att = self.n_mapping(neighbor_norms.detach())
            contrastive_att = self.contrastive_att_net(x_att * n_att)
            neighbor_norms *= contrastive_att

        out = x + neighbor_norms
        return out


class C2D(nn.Module):
    def __init__(self, conv2d, **kwargs):
        super(C2D, self).__init__()

        # conv3d kernel
        kernel_dim = (1, conv2d.kernel_size[0], conv2d.kernel_size[1])
        stride = (1, conv2d.stride[0], conv2d.stride[0])
        padding = (0, conv2d.padding[0], conv2d.padding[1])
        self.conv3d = nn.Conv3d(conv2d.in_channels, conv2d.out_channels,
                                kernel_size=kernel_dim, padding=padding,
                                stride=stride, bias=conv2d.bias)

        # init the parameters of conv3d
        weight_2d = conv2d.weight.data
        weight_3d = torch.zeros(*weight_2d.shape)
        weight_3d = weight_3d.unsqueeze(2)
        weight_3d[:, :, 0, :, :] = weight_2d
        self.conv3d.weight = nn.Parameter(weight_3d)
        self.conv3d.bias = conv2d.bias

    def forward(self, x):
        out = self.conv3d(x)

        return out


class I3D(nn.Module):
    def __init__(self, conv2d, time_dim=3, time_stride=1, **kwargs):
        super(I3D, self).__init__()

        # conv3d kernel
        kernel_dim = (time_dim, conv2d.kernel_size[0], conv2d.kernel_size[1])
        stride = (time_stride, conv2d.stride[0], conv2d.stride[0])
        padding = (time_dim // 2, conv2d.padding[0], conv2d.padding[1])
        self.conv3d = nn.Conv3d(conv2d.in_channels, conv2d.out_channels,
                                kernel_size=kernel_dim, padding=padding,
                                stride=stride, bias=conv2d.bias)

        # init the parameters of conv3d
        weight_2d = conv2d.weight.data
        weight_3d = torch.zeros(*weight_2d.shape)
        weight_3d = weight_3d.unsqueeze(2).repeat(1, 1, time_dim, 1, 1)
        middle_idx = time_dim // 2
        weight_3d[:, :, middle_idx, :, :] = weight_2d
        self.conv3d.weight = nn.Parameter(weight_3d)
        self.conv3d.bias = conv2d.bias

    def forward(self, x):
        out = self.conv3d(x)

        return out


class API3D(nn.Module):
    def __init__(self, conv2d, time_dim=3, time_stride=1, temperature=4, contrastive_att=True):
        super(API3D, self).__init__()

        # 保证out_channels至少为1
        out_channels = max(conv2d.in_channels // 16, 1)

        self.APM = APM(conv2d.in_channels, out_channels,
                       time_dim=time_dim, temperature=temperature, contrastive_att=contrastive_att)

        # Conv3D kernel
        kernel_dim = (time_dim, conv2d.kernel_size[0], conv2d.kernel_size[1])
        stride = (time_stride * time_dim, conv2d.stride[0], conv2d.stride[0])
        padding = (0, conv2d.padding[0], conv2d.padding[1])

        self.conv3d = nn.Conv3d(conv2d.in_channels, conv2d.out_channels,
                                kernel_size=kernel_dim, padding=padding,
                                stride=stride, bias=(conv2d.bias is not None))

        # 初始化Conv3D层权重
        weight_2d = conv2d.weight.data
        weight_3d = weight_2d.unsqueeze(2).repeat(1, 1, time_dim, 1, 1) / time_dim
        self.conv3d.weight.data = weight_3d

        if conv2d.bias is not None:
            self.conv3d.bias.data = conv2d.bias.data

    def forward(self, x):
        x_offset = self.APM(x)
        out = self.conv3d(x_offset)

        return out

if __name__ == '__main__':
    # 这里确保conv2d_example的输出通道数与APM模块中使用的in_channels一致
    in_channels = 16  # 假设这是APM模块期望的输入通道数
    out_channels = in_channels // 2  # 根据需要调整
    conv2d_example = nn.Conv2d(in_channels=3, out_channels=in_channels, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))

    block = API3D(conv2d=conv2d_example, time_dim=3, time_stride=1, temperature=4, contrastive_att=True)

    input_tensor = torch.rand(4, 3, 3, 64, 64)  # 确保这里的通道数与conv2d_example的输入通道数一致

    output = block(input_tensor)

    print("Input tensor shape:", input_tensor.size())
    print("Output tensor shape:", output.size())


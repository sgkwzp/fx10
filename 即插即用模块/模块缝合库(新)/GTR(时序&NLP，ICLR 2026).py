import torch
import torch.nn as nn
import torch.nn.functional as F


class GTR(nn.Module):
    def __init__(self, d_series, c, CI=False, period_len=24):

        super(GTR, self).__init__()
        self.agg = False
        self.period_len = period_len
        self.c = c
        self.linear = nn.Linear(d_series, d_series)
        self.CI = CI
        if self.CI:
            self.ds_convs = nn.ModuleList(
                [nn.Conv2d(in_channels=1, out_channels=1, kernel_size=(2, 1 + 2 * (self.period_len // 2)),
                           stride=1, padding=(0, self.period_len // 2), padding_mode="zeros", bias=False)
                 for _ in range(self.c)]
            )
        else:
            self.conv2d = nn.Conv2d(in_channels=1, out_channels=1, kernel_size=(2, 1 + 2 * (self.period_len // 2)),
                                    stride=1, padding=(0, self.period_len // 2), padding_mode="zeros", bias=False)
        self.dropout = nn.Dropout(p=0.1)

    def forward(self, x, q):
        _, C, S = x.shape
        # Step 1: Mapping
        global_query = self.linear(q)  # (B, C, S)

        # Step 2: GTA mode, aggregate across channels, design for capturing inter-varaible dependencies.
        if self.agg:
            weight = F.softmax(global_query, dim=1)
            global_query = torch.sum(global_query * weight, dim=1, keepdim=True)
            global_query = global_query.repeat(1, C, 1)  # (B, C, S)

        # Step 3: Fuse
        out = torch.stack([x, global_query], dim=2)  # (B, C, 2, S)

        if self.CI:
            conv_outs = [
                self.ds_convs[i](out[:, i, :, :].unsqueeze(1))  # (B, 1, 2, S)
                for i in range(self.c)
            ]
            conv_out = torch.cat(conv_outs, dim=1)  # (B, C, 1, S)
            conv_out = conv_out.squeeze(2)  # (B, C, S)

        else:
            out = out.reshape(-1, 1, 2, S)  # (B*C, 1, 2, S)
            conv_out = self.conv2d(out)  # (B*C, 1, 1, S)
            conv_out = conv_out.reshape(-1, C, S)  # (B, C, S)

        return self.dropout(conv_out)


if __name__ == '__main__':
    B = 2                                  # batch size
    C = 8                                  # 通道/变量数：多变量时间序列里有多少个变量
    S = 96                                 # 序列长度

    block = GTR(d_series=S, c=C).to('cuda')
                                           # d_series 等于序列长度
                                           # c 要等于通道数 C


    x = torch.rand(B, C, S).to('cuda')  # 构造输入 x：形状 (B, C, S)，随机数初始化，模拟一批时间序列特征
    q = torch.rand(B, C, S).to('cuda')  # 构造输入 q：形状 (B, C, S)，作为 query（会先过 linear 得到 global_query）

    output = block(x, q)

    print(x.size())
    print(output.size())
# -*- coding: utf-8 -*-
import torch
import torch.nn as nn
from thop import profile

"""
本文介绍了 SparseTSF，这是一种用于长期时间序列预测 （LTSF） 的新型、极其轻量级的模型，旨在解决以最少的计算资源在扩展范围内对复杂的时间依赖关系进行建模的挑战。
SparseTSF 的核心是跨周期稀疏预测技术，该技术通过解耦时间序列数据中的周期性和趋势来简化预测任务。该技术涉及对原始序列进行下采样以专注于跨周期趋势预测，从而有效地提取周期性特征，同时最大限度地减少模型的复杂性和参数计数。
基于这种技术，与最先进的模型相比，SparseTSF 模型使用少于 *1k* 的参数来实现具有竞争力或卓越的性能。此外，SparseTSF 还具有出色的泛化能力，非常适合计算资源有限、样本量小或数据质量低的场景。
"""

class Configs:
    def __init__(self, seq_len=100, pred_len=50, enc_in=1, period_len=10):
        self.seq_len = seq_len
        self.pred_len = pred_len
        self.enc_in = enc_in
        self.period_len = period_len

class SparseTSF(nn.Module):
    def __init__(self, configs):
        super(SparseTSF, self).__init__()
        self.seq_len = configs.seq_len
        self.pred_len = configs.pred_len
        self.enc_in = configs.enc_in
        self.period_len = configs.period_len

        self.seg_num_x = self.seq_len // self.period_len
        self.seg_num_y = self.pred_len // self.period_len

        self.conv1d = nn.Conv1d(in_channels=1, out_channels=1, kernel_size=1 + 2 * self.period_len // 2,
                                stride=1, padding=self.period_len // 2, padding_mode="zeros", bias=False)

        self.linear = nn.Linear(self.seg_num_x, self.seg_num_y, bias=False)

    def forward(self, x):
        batch_size = x.shape[0]
        seq_mean = torch.mean(x, dim=1).unsqueeze(1)
        x = (x - seq_mean).permute(0, 2, 1)

        x = self.conv1d(x.reshape(-1, 1, self.seq_len)).reshape(-1, self.enc_in, self.seq_len) + x
        x = x.reshape(-1, self.seg_num_x, self.period_len).permute(0, 2, 1)

        y = self.linear(x)
        y = y.permute(0, 2, 1).reshape(batch_size, self.enc_in, self.pred_len)
        y = y.permute(0, 2, 1) + seq_mean

        return y

if __name__ == '__main__':
    # Instantiate the configs
    configs = Configs(seq_len=100, pred_len=100, enc_in=3, period_len=10)

    # Create the model
    model = SparseTSF(configs)


    # Create a dummy input tensor
    input_tensor = torch.rand(1, configs.seq_len, configs.enc_in)  # Batch size of 1

    x = torch.randn(1, 100, 3)
    flops, params = profile(model, (x,))
    print('Params = ' + str(params / 1000 ** 2) + 'M')


    # Run the model
    output = model(input_tensor)

    # Print the sizes of input and output
    print("Input size:", input_tensor.size())
    print("Output size:", output.size())

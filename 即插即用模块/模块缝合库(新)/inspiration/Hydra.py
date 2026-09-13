import numpy as np
import torch, torch.nn as nn, torch.nn.functional as F


# 使用竞争卷积核进行时间序列分类
"""
演示了时间序列分类的字典方法（涉及时间序列中的符号模式的提取和计数）与基于使用卷积核转换输入时间序列的方法（即ROCKET及其变体）之间的简单联系。
可以证明，通过调整单个超参数，可以在类似于字典方法的模型和类似于ROCKET的模型之间逐步移动。我们提出了HYDRA，一种简单、快速且准确的字典方法，使用竞争卷积核进行时间序列分类，结合了ROCKET和传统字典方法的关键方面。
HYDRA比现有最准确的字典方法更快、更准确，其准确度与当前几种最准确的时间序列分类方法相似。HYDRA还可以与ROCKET及其变体结合使用，以显着提高这些方法的准确性。
"""


class Hydra(nn.Module):

    def __init__(self, input_length, k = 8, g = 64, seed = None):

        super().__init__()

        if seed is not None:
            torch.manual_seed(seed)

        self.k = k # num kernels per group
        self.g = g # num groups

        max_exponent = np.log2((input_length - 1) / (9 - 1)) # kernel length = 9

        self.dilations = 2 ** torch.arange(int(max_exponent) + 1)
        self.num_dilations = len(self.dilations)

        self.paddings = torch.div((9 - 1) * self.dilations, 2, rounding_mode = "floor").int()

        self.divisor = min(2, self.g)
        self.h = self.g // self.divisor

        self.W = torch.randn(self.num_dilations, self.divisor, self.k * self.h, 1, 9)
        self.W = self.W - self.W.mean(-1, keepdims = True)
        self.W = self.W / self.W.abs().sum(-1, keepdims = True)

    # transform in batches of *batch_size*
    def batch(self, X, batch_size = 256):
        num_examples = X.shape[0]
        if num_examples <= batch_size:
            return self(X)
        else:
            Z = []
            batches = torch.arange(num_examples).split(batch_size)
            for batch in batches:
                Z.append(self(X[batch]))
            return torch.cat(Z)

    def forward(self, X):

        num_examples = X.shape[0]

        if self.divisor > 1:
            diff_X = torch.diff(X)

        Z = []

        for dilation_index in range(self.num_dilations):

            d = self.dilations[dilation_index].item()
            p = self.paddings[dilation_index].item()

            for diff_index in range(self.divisor):

                _Z = F.conv1d(X if diff_index == 0 else diff_X, self.W[dilation_index, diff_index], dilation = d, padding = p) \
                      .view(num_examples, self.h, self.k, -1)

                max_values, max_indices = _Z.max(2)
                count_max = torch.zeros(num_examples, self.h, self.k)

                min_values, min_indices = _Z.min(2)
                count_min = torch.zeros(num_examples, self.h, self.k)

                count_max.scatter_add_(-1, max_indices, max_values)
                count_min.scatter_add_(-1, min_indices, torch.ones_like(min_values))

                Z.append(count_max)
                Z.append(count_min)

        Z = torch.cat(Z, 1).view(num_examples, -1)

        return Z


if __name__ == '__main__':
    # 初始化Hydra模型，输入序列长度为128
    block = Hydra(input_length=128)

    # 创建输入Tensor，大小为(batch_size, channels, length)，例如：(32, 1, 128)
    input = torch.rand(32, 1, 128)  # 随机生成输入数据

    # 使用Hydra模型进行前向传播
    output = block(input)

    # 打印输入和输出的大小
    print("Input size:", input.size())
    print("Output size:", output.size())

import torch.nn as nn
import torch

"""
毫米波雷达正越来越多地集成到商用车中，通过实现强大和高性能的物体检测、定位和识别来支持新的高级驾驶辅助系统，这是新环境感知的关键组成部分。本文提出了一种新型雷达多视角卷积神经网络（RAMP-CNN），该网络基于对距离-速度-角（RVA）热图序列的进一步处理来提取物体的位置和类别。为了绕过 4D 卷积神经网络 （NN） 的复杂性，我们建议在我们的 RAMP-CNN 模型中组合几个低维 NN 模型，这些模型仍然以较低的复杂度接近性能上限。大量的实验表明，所提出的RAMP-CNN模型在所有测试场景中都比以往工作取得了更好的平均召回率和平均精度。此外，RAMP-CNN模型经过验证，可以在夜间稳定工作，这使得低成本雷达在恶劣条件下可以替代纯光学传感。
"""

class Encode(nn.Module):
    def __init__(self, in_channels):
        super(Encode, self).__init__()

        self.conv1a = nn.Conv2d(in_channels=in_channels, out_channels=64, kernel_size=(5, 5), stride=(1, 1),
                                padding=(2, 2))
        self.conv1b = nn.Conv2d(in_channels=64, out_channels=64, kernel_size=(5, 5), stride=(2, 2), padding=(2, 2))

        self.conv2a = nn.Conv2d(in_channels=64, out_channels=128, kernel_size=(5, 5), stride=(1, 1), padding=(2, 2))
        self.conv2b = nn.Conv2d(in_channels=128, out_channels=128, kernel_size=(5, 5), stride=(2, 2), padding=(2, 2))

        self.conv3a = nn.Conv2d(in_channels=128, out_channels=256, kernel_size=(5, 5), stride=(1, 1), padding=(2, 2))
        self.conv3b = nn.Conv2d(in_channels=256, out_channels=256, kernel_size=(5, 5), stride=(2, 2), padding=(2, 2))

        self.bn1a = nn.BatchNorm2d(num_features=64)
        self.bn1b = nn.BatchNorm2d(num_features=64)
        self.bn2a = nn.BatchNorm2d(num_features=128)
        self.bn2b = nn.BatchNorm2d(num_features=128)
        self.bn3a = nn.BatchNorm2d(num_features=256)
        self.bn3b = nn.BatchNorm2d(num_features=256)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.bn1a(self.conv1a(x)))  # (B, 1, 256, 256) -> (B, 64,  256, 256)
        x = self.relu(self.bn1b(self.conv1b(x)))  # (B, 64, 256, 256) -> (B, 64, 128, 128)
        x = self.relu(self.bn2a(self.conv2a(x)))  # (B, 64, 128, 128) -> (B, 128, 128, 128)
        x = self.relu(self.bn2b(self.conv2b(x)))  # (B, 128, 128, 128) -> (B, 128, 64, 64)
        x = self.relu(self.bn3a(self.conv3a(x)))  # (B, 128, 64, 64) -> (B, 256, 64, 64 )
        x = self.relu(self.bn3b(self.conv3b(x)))  # (B, 256, 64, 64) -> (B, 256, 32, 32)

        return x


class Decode(nn.Module):
    def __init__(self, out_channel=32):
        super(Decode, self).__init__()

        self.convt1 = nn.ConvTranspose2d(in_channels=256, out_channels=128, stride=(2, 2), padding=(2, 2),
                                         kernel_size=(6, 6))
        self.convt2 = nn.ConvTranspose2d(in_channels=128, out_channels=64, stride=(2, 2), padding=(2, 2),
                                         kernel_size=(6, 6))
        self.convt3 = nn.ConvTranspose2d(in_channels=64, out_channels=out_channel, stride=(2, 2), padding=(2, 2),
                                         kernel_size=(6, 6))

        self.bn_cn = nn.BatchNorm2d(num_features=2)
        self.PRelu = nn.PReLU()

    def forward(self, x):
        x = self.PRelu(self.convt1(x))  # (B,256,32,32) -> (B,128,64,64)
        x = self.PRelu(self.convt2(x))  # (B,128,64,64) -> (B,64,128,128)
        x = self.PRelu(self.convt3(x))  # (B,64,128,128) -> (B,32,256,256)

        return x


def get_model(args):
    if args.model == 'RODNet':
        from Models.rodnet import RODNetCDC
        model = RODNetCDC(in_channels=args.frame, n_class=args.no_class)

    if args.model == 'RAMP':
        from Models.rampcnn import RAMPCNN
        model = RAMPCNN(in_channels=args.frame, n_class=args.no_class)

    if args.model == 'Crossatten':
        from Models.cross_atten import RadarCross
        model = RadarCross(in_channels=args.frame,
                           n_class=args.no_class,
                           center_offset=args.co,
                           orentation=args.oren)
    return model


class RAMPCNN(nn.Module):
    def __init__(self, in_channels=1, n_class=3):
        super(RAMPCNN, self).__init__()

        self.raencode = Encode(in_channels=in_channels)
        self.rdencode = Encode(in_channels=in_channels)
        self.adencode = Encode(in_channels=in_channels)

        self.radecode = Decode()
        self.rddecode = Decode()
        self.addecode = Decode()

        self.inception1 = nn.Conv2d(in_channels=96, out_channels=64, stride=(1, 1), padding=(1, 1), kernel_size=(3, 3))
        self.inception2 = nn.Conv2d(in_channels=64, out_channels=32, stride=(1, 1), padding=(2, 2), kernel_size=(5, 5))
        self.inception3 = nn.Conv2d(in_channels=32, out_channels=n_class, stride=(1, 1), padding=(0, 10),
                                    kernel_size=(1, 21))

        self.PRelu = nn.PReLU()

    def forward(self, ra, rd, ad):
        ra = self.raencode(ra)  # (B,1,256,256)-> (B,256,32,32)
        ra = self.radecode(ra)  # (B,256,32,32)->(B,32,256,256)

        rd = self.rdencode(rd)  # (B,1,256,64)-> (B,256,32,8)
        rd = self.rddecode(rd)  # (B,256,32,32)->(B,32,256,256)

        ad = self.adencode(ad)  # (B,1,64,256)-> (B,256,8,32)
        ad = self.addecode(ad)  # (B,256,32,32)->(B,32,256,256)

        # Fusion Module
        rd = torch.mean(rd, dim=3, keepdim=True)
        rd = torch.tile(rd, (1, 1, 1, 256))

        ad = torch.mean(ad, dim=2, keepdim=True)
        ad = torch.tile(ad, (1, 1, 256, 1))

        x = torch.cat([ra, rd, ad], dim=1)

        # Inception module
        x = self.PRelu(self.inception1(x))  # (B,96,256,256) -> (B,64,256,256)
        x = self.PRelu(self.inception2(x))  # (B,64,256,256) -> (B,64,256,256)
        x = self.PRelu(self.inception3(x))  # (B,64,256,256) -> (B,3,256,256)
        return x


if __name__ == '__main__':
    # Define input dimensions
    batch_size = 1
    channels = 1
    height = 256
    width = 256

    # Create dummy inputs
    ra_input = torch.randn(batch_size, channels, height, width)
    rd_input = torch.randn(batch_size, channels, height, width)
    ad_input = torch.randn(batch_size, channels, height, width)

    # Instantiate the model
    model = RAMPCNN()

    # Forward pass
    output = model(ra_input, rd_input, ad_input)

    # Print sizes to verify
    print("Input size (RA):", ra_input.size())
    print("Input size (RD):", rd_input.size())
    print("Input size (AD):", ad_input.size())
    print("Output size:", output.size())
# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings("ignore")
import torch
import torch.nn.functional as F

def sim(z1: torch.Tensor, z2: torch.Tensor, hidden_norm: bool = True):
    if hidden_norm:
        z1 = F.normalize(z1)
        z2 = F.normalize(z2)
    return torch.mm(z1, z2.t())


def nei_con_loss(z1: torch.Tensor, z2: torch.Tensor, tau, adj, hidden_norm: bool = True):
    '''neighbor contrastive loss'''
    adj = adj - torch.diag_embed(adj.diag())  # remove self-loop
    adj[adj > 0] = 1
    nei_count = torch.sum(adj, 1) * 2 + 1  # intra-view nei+inter-view nei+self inter-view
    nei_count = torch.squeeze(torch.tensor(nei_count))

    f = lambda x: torch.exp(x / tau)
    intra_view_sim = f(sim(z1, z1, hidden_norm))
    inter_view_sim = f(sim(z1, z2, hidden_norm))

    loss = (inter_view_sim.diag() + (intra_view_sim.mul(adj)).sum(1) + (inter_view_sim.mul(adj)).sum(1)) / (
            intra_view_sim.sum(1) + inter_view_sim.sum(1) - intra_view_sim.diag())
    loss = loss / nei_count  # divided by the number of positive pairs for each node

    return -torch.log(loss)


if __name__ == '__main__':
    # 示例数据
    batch_size = 4
    feature_dim = 5
    z1 = torch.rand(batch_size, feature_dim)
    z2 = torch.rand(batch_size, feature_dim)
    adj = torch.randint(0, 2, (batch_size, batch_size))

    print("z1:", z1.shape)
    print("z2:", z2.shape)
    print("adj:", adj.shape)

    loss = nei_con_loss(z1, z2, tau=1.0, adj=adj, hidden_norm=True)
    print("Loss:", loss)
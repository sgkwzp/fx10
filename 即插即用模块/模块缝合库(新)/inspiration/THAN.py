import logging
import random
import torch
import torch.nn as nn
import numpy as np

""" 
转移向量投影+多头注意力(TransD+TGAT)
"""


class HetMatchDecoder(torch.nn.Module):
    def __init__(self, num_etypes, dim, etype_feat=None):
        super().__init__()
        if etype_feat is None:
            etype_feat = torch.Tensor(num_etypes, dim)
            self.fc1 = torch.nn.Linear(dim * 3, dim)
        else:
            etype_feat = torch.from_numpy(etype_feat)
            self.fc1 = torch.nn.Linear(dim * 2 + etype_feat.shape[1], dim)
        self.rel_emb = nn.Parameter(etype_feat)

        self.fc2 = torch.nn.Linear(dim, 1)
        self.act = torch.nn.ReLU()
        self.reset_parameters()

    def reset_parameters(self):
        torch.nn.init.xavier_uniform_(self.rel_emb.data)
        torch.nn.init.xavier_uniform_(self.fc1.weight)
        torch.nn.init.xavier_uniform_(self.fc2.weight)

    def forward(self, x, y, edge_type_l):
        etype_l = torch.from_numpy(edge_type_l).to(x.device)
        etype_l -= 1
        e = self.rel_emb[etype_l]
        h = torch.cat([x, e, y], dim=1)
        h = self.act(self.fc1(h))
        return self.fc2(h).squeeze(dim=-1)

    def reg_loss(self):
        return self.rel_emb.pow(2).mean()


class MergeFFN(torch.nn.Module):
    def __init__(self, dim1, dim2, dim3, dim4):
        super().__init__()
        self.fc1 = torch.nn.Linear(dim1 + dim2, dim3)
        self.fc2 = torch.nn.Linear(dim3, dim4)
        self.act = torch.nn.ReLU()
        torch.nn.init.xavier_uniform_(self.fc1.weight)
        torch.nn.init.xavier_uniform_(self.fc2.weight)

    def forward(self, x1, x2):
        h = torch.cat([x1, x2], dim=1)
        h = self.act(self.fc1(h))
        return self.fc2(h)


class ScaledDotProductAttention(torch.nn.Module):
    ''' Scaled Dot-Product Attention '''

    def __init__(self, temperature, attn_dropout=0.1):
        super().__init__()
        self.temperature = temperature
        self.dropout = torch.nn.Dropout(attn_dropout)
        self.softmax = torch.nn.Softmax(dim=-1)

    def forward(self, q, k, v, r_pri=None, mask=None):
        # q, k:  (n*b) x N x dk
        # v:     (n*b) x N x dv
        # r_pri: b x N

        attn = torch.sum(q * k, dim=-1)  # [n*b, N]
        if r_pri is None:
            attn = attn / self.temperature
        else:
            attn = attn.reshape(-1, *r_pri.shape) * r_pri / self.temperature
            attn = attn.reshape(-1, r_pri.size(1))

        if mask is not None:
            attn = attn.masked_fill(mask, -1e10)

        attn = self.softmax(attn)  # [n*b, N]
        attn = self.dropout(attn)

        output = (attn.unsqueeze(-1) * v).sum(dim=1)

        return output, attn


class MultiHeadAttention(nn.Module):
    ''' Multi-Head Attention module '''

    def __init__(self, n_head, d_model, d_k, d_v, dropout=0.1, num_n_type=1, num_e_type=1):
        super().__init__()

        self.n_head = n_head
        self.d_model = d_model
        self.d_k = d_k
        self.d_v = d_v

        self.num_n_type = num_n_type
        self.num_e_type = num_e_type

        self.d_r = self.d_model
        self.w_qs = nn.ModuleList()
        self.w_ks = nn.ModuleList()
        self.w_vs = nn.ModuleList()
        for _ in range(num_e_type + 1):
            self.w_qs.append(nn.Linear(self.d_r, n_head * d_k, bias=False))
            self.w_ks.append(nn.Linear(self.d_r, n_head * d_k, bias=False))
            self.w_vs.append(nn.Linear(self.d_r, n_head * d_v, bias=False))

        self.relation_pri = nn.Parameter(torch.ones(num_n_type + 1, num_e_type + 1))

        self.attention = ScaledDotProductAttention(d_k ** 0.5, attn_dropout=dropout)

        self.fc_lins = nn.ModuleList()
        for _ in range(num_n_type + 1):
            self.fc_lins.append(nn.Linear(self.n_head * self.d_v, self.d_model))

        self.layer_norm = nn.LayerNorm(self.d_model)
        self.dropout = nn.Dropout(dropout)

        self.reset_parameter()

    def reset_parameter(self):
        for i in range(len(self.w_qs)):
            nn.init.xavier_uniform_(self.w_qs[i].weight.data)
            nn.init.xavier_uniform_(self.w_ks[i].weight.data)
            nn.init.xavier_uniform_(self.w_vs[i].weight.data)

        for fc in self.fc_lins:
            nn.init.xavier_uniform_(fc.weight.data)

    def _get_relation_pri_of_q(self, seq_utype, seq_etype):
        N = seq_etype.size(1)
        seq = seq_utype.repeat(N, 1).t()
        idx = seq * (self.num_e_type + 1) + seq_etype
        pri = self.relation_pri.flatten()
        pri = pri.index_select(0, idx.flatten())
        return pri.view(-1, N)

    def _compute_QKV_by_etype(self, q, k, v, seq_etype):
        for i, etype in enumerate(seq_etype.unique()):
            msk = (seq_etype == etype).unsqueeze(-1)
            if i == 0:
                Q = self.w_qs[etype](q * msk)
                K = self.w_ks[etype](k * msk)
                V = self.w_vs[etype](v * msk)
            else:
                Q += self.w_qs[etype](q * msk)
                K += self.w_ks[etype](k * msk)
                V += self.w_vs[etype](v * msk)
        return Q, K, V

    def forward(self, q, k, v, seq_etype=None, seq_utype=None, seq_vtype=None, mask=None):
        """
        params:
            q:    [B, N, D]  of src
            k, v: [B, N, D]  of ngh
            seq_etype: [B, N]
            seq_utype: [B]
            seq_vtype: [B, N]
            mask: [B, N]
        """
        d_k, d_v, n_head = self.d_k, self.d_v, self.n_head

        sz_b, len_e = q.size(0), k.size(1)

        # compute Q, K, V in relature feature space
        q, k, v = self._compute_QKV_by_etype(q, k, v, seq_etype)  # (b, N, n*D)

        q = q.view(sz_b, len_e, n_head, d_k)  # (b, N, n_head, D)  源节点到各个边的转移向量
        k = k.view(sz_b, len_e, n_head, d_k)
        v = v.view(sz_b, len_e, n_head, d_v)

        q = q.permute(2, 0, 1, 3).contiguous().view(-1, len_e, d_k)  # (n*b) x N x dk
        k = k.permute(2, 0, 1, 3).contiguous().view(-1, len_e, d_k)  # (n*b) x N x dk
        v = v.permute(2, 0, 1, 3).contiguous().view(-1, len_e, d_v)  # (n*b) x N x dv

        # pri = None
        pri = self._get_relation_pri_of_q(seq_utype, seq_etype)  # [B, N]
        mask = mask.repeat(n_head, 1)  # (n*b, N) x .. x ..
        output, attn = self.attention(q, k, v, pri, mask=mask)  # output (n*b) x dv

        output = output.view(n_head, sz_b, d_v)  # n x b x dv
        output = output.transpose(0, 1).contiguous().view(sz_b, -1)  # b x (n*dv) = b x d_model

        """ map out to q's feature space """
        out = torch.zeros_like(output)
        for utype in seq_utype.unique():
            mask = seq_utype == utype
            out[mask] = self.fc_lins[utype](output[mask])
        output = out

        # [b, d_model]
        output = self.layer_norm(output)
        output = self.dropout(output)

        return output, attn


class TimeEncode(torch.nn.Module):
    def __init__(self, expand_dim):
        super(TimeEncode, self).__init__()
        time_dim = expand_dim
        self.basis_freq = torch.nn.Parameter((torch.from_numpy(1 / 10 ** np.linspace(0, 9, time_dim))).float())
        self.phase = torch.nn.Parameter(torch.zeros(time_dim).float())

    def forward(self, ts):
        # ts: [N, L]
        batch_size = ts.size(0)
        seq_len = ts.size(1)

        ts = ts.view(batch_size, seq_len, 1)  # [N, L, 1]
        map_ts = ts * self.basis_freq.view(1, 1, -1)  # [N, L, time_dim]
        map_ts += self.phase.view(1, 1, -1)

        harmonic = torch.cos(map_ts)

        return harmonic  # [N, L, time_dim]


class PosEncode(torch.nn.Module):
    def __init__(self, expand_dim, seq_len):
        super().__init__()
        self.pos_embeddings = nn.Embedding(num_embeddings=seq_len, embedding_dim=expand_dim)

    def forward(self, ts):
        # ts: [N, L]
        order = ts.argsort()
        ts_emb = self.pos_embeddings(order)
        return ts_emb


class EmptyEncode(torch.nn.Module):
    def __init__(self, expand_dim):
        super().__init__()
        self.expand_dim = expand_dim

    def forward(self, ts):
        out = torch.zeros_like(ts).float()
        out = torch.unsqueeze(out, dim=-1)
        out = out.expand(out.shape[0], out.shape[1], self.expand_dim)
        return out


def resize(e, dim):
    # e:[B, N, D]
    if e.size(-1) >= dim:
        res = e[:, :, :dim]
    else:
        e_padd = torch.zeros(e.size(0), e.size(1), dim - e.size(2)).to(e.device)
        res = torch.cat([e, e_padd], dim=-1)
    return res


class Transfer(torch.nn.Module):
    """ transfer head and tail node to edge feature space """

    def __init__(self, num_n_type, num_e_type, n_dim, e_dim=32, e_type_feat=None):
        super().__init__()
        # node type and edge type vector, padding an idx
        self.node_trans = nn.Embedding(num_n_type + 1, n_dim, padding_idx=0)
        if e_type_feat is not None:
            self.edge_trans = nn.Embedding.from_pretrained(e_type_feat, padding_idx=0)
        else:
            self.edge_trans = nn.Embedding(num_e_type + 1, e_dim, padding_idx=0)
        self.e_dim = self.edge_trans.weight.size(1)

    def forward(self, src, nghs, seq_utype, seq_vtype, seq_etype):
        """
        params:
            src:  [B, D]  of src
            nghs: [B, N, D]  of ngh
            seq_utype: [B]
            seq_vtype: [B, N]
            seq_etype: [B, N]
        """
        q = src.unsqueeze(1)  # [B, 1, D]
        k = nghs
        u_trans = self.node_trans(seq_utype).unsqueeze(1)  # [B, 1, D]
        v_trans = self.node_trans(seq_vtype)  # [B, N, D]
        r_trans = self.edge_trans(seq_etype)  # [B, N, De]

        # [B, N, De]
        q = torch.sum(q * u_trans, dim=-1, keepdim=True) * r_trans + resize(q, self.e_dim)
        k = torch.sum(k * v_trans, dim=-1, keepdim=True) * r_trans + resize(k, self.e_dim)
        return q, k


class AttnModel(nn.Module):
    """Attention based temporal layers
    """

    def __init__(self, feat_dim, edge_dim, time_dim, transfer, n_head=2, dropout=0.1,
                 num_n_type=1, num_e_type=1):
        """
        args:
          feat_dim: dim for the node features
          edge_dim: dim for the temporal edge features
          time_dim: dim for the time encoding
          attn_mode: choose from 'prod' and 'map'
          n_head: number of heads in attention
          dropout: probability of dropping a neural
          num_n_type: number of node types
          num_e_type: number of edge types
        """
        super(AttnModel, self).__init__()

        self.feat_dim = feat_dim
        self.edge_dim = edge_dim
        self.time_dim = time_dim

        self.model_dim = (feat_dim + time_dim)
        assert (self.model_dim % n_head == 0)

        self.transfer = transfer

        self.norm1, self.norm2 = nn.LayerNorm(feat_dim), nn.LayerNorm(feat_dim)

        self.multi_head_target = MultiHeadAttention(n_head,
                                                    d_model=self.model_dim,
                                                    d_k=self.model_dim // n_head,
                                                    d_v=self.model_dim // n_head,
                                                    dropout=dropout,
                                                    num_n_type=num_n_type,
                                                    num_e_type=num_e_type)

        self.merger = MergeFFN(self.model_dim, feat_dim, feat_dim, feat_dim)

    def forward(self, src, src_t, seq, seq_t, seq_e, seq_etype, seq_utype, seq_vtype, mask):
        """"Attention based temporal attention forward pass
        args:
          src:   float Tensor of shape [B, D]
          src_t: float Tensor of shape [B, 1, Dt], Dt == D
          seq:   float Tensor of shape [B, N, D]
          seq_t: float Tensor of shape [B, N, Dt]
          seq_e: float Tensor of shape [B, N, De], De == D
          seq_etype: long Tensorof shape [B, N], value in (0, 1, ...), 0 is default
          seq_utype: long Tensorof shape [B, N], value in (0, 1, ...), 0 is default
          seq_vtype: long Tensorof shape [B, N], value in (0, 1, ...), 0 is default
          mask:  boolean Tensor of shape [B, N], where the true value indicate a null value in the sequence.
        returns:
          output: float Tensor of shape [B, D]
          weight: float Tensor of shape [B, N]
        """
        # type mapping
        q, k = self.transfer(src, seq, seq_utype, seq_vtype, seq_etype)  # [B, N, D]
        # q, k = src.unsqueeze(1).repeat(1, seq.size(1), 1), seq  # no transfer

        # add & norm
        q = self.norm1(q)  # source node is not associated with edge feature
        k = self.norm2(k + resize(seq_e, self.feat_dim))

        # [B, D+Dt]
        q = torch.cat([q, src_t.repeat(1, q.size(1), 1)], dim=2)
        k = torch.cat([k, seq_t], dim=2)

        # target-attention
        # output: [B, D], attn: [B, N, N]
        output, attn = self.multi_head_target(q=q, k=k, v=k, seq_etype=seq_etype, seq_utype=seq_utype,
                                              seq_vtype=seq_vtype, mask=mask)

        # residual
        # why not use q for residual: src_e is zeros vector and src_t is one vector, so they will not contribute useful information for the source node v0
        output = self.merger(output, src)

        return output, attn


class Events(object):
    def __init__(self, src_l, dst_l, ts_l, e_idx_l, e_type_l=None, u_type_l=None, v_type_l=None, label_l=None):
        self.src_l = src_l
        self.dst_l = dst_l
        self.ts_l = ts_l
        self.e_idx_l = e_idx_l
        self.e_type_l = e_type_l
        self.u_type_l = u_type_l
        self.v_type_l = v_type_l
        self.label_l = label_l
        self.node_set = set(np.unique(np.hstack([self.src_l, self.dst_l])))
        self.num_nodes = len(self.node_set)

    def sample_by_mask(self, mask):
        sam_src_l = self.src_l[mask]
        sam_dst_l = self.dst_l[mask]
        sam_ts_l = self.ts_l[mask]
        sam_e_idx_l = self.e_idx_l[mask]
        sam_e_type_l = self.e_type_l[mask] if self.e_type_l is not None else None
        sam_u_type_l = self.u_type_l[mask] if self.u_type_l is not None else None
        sam_v_type_l = self.v_type_l[mask] if self.v_type_l is not None else None
        sam_label_l = self.label_l[mask] if self.label_l is not None else None

        return Events(sam_src_l, sam_dst_l, sam_ts_l, sam_e_idx_l, sam_e_type_l, sam_u_type_l, sam_v_type_l,
                      sam_label_l)


class TemHetGraphData(Events):
    def __init__(self, g_df, n_feat, e_feat, num_n_type, num_e_type, e_type_feat=None):
        super(TemHetGraphData, self).__init__(g_df.u.values, g_df.v.values, g_df.ts.values, g_df.e_idx.values,
                                              g_df.e_type.values, g_df.u_type.values, g_df.v_type.values)
        self.g_df = g_df
        self.n_feat = n_feat
        self.e_feat = e_feat
        self.num_n_type = num_n_type
        self.num_e_type = num_e_type
        self.e_type_feat = e_type_feat
        self.max_idx = max(self.src_l.max(), self.dst_l.max())
        # self.n_dim = n_feat.shape[1]
        # self.e_dim = e_feat.shape[1]


class NeighborFinder:
    def __init__(self, adj_list, uniform=False, num_edge_type=None):
        """
        Params
        ------
          node_idx_l: List[int]
          node_ts_l: List[int]
          off_set_l: List[int], such that node_idx_l[off_set_l[i]:off_set_l[i + 1]] = adjacent_list[i]
        """
        node_idx_l, node_ts_l, e_idx_l, e_type_l, u_type_l, v_type_l, off_set_l = self.init_off_set(adj_list)
        self.node_idx_l = node_idx_l
        self.node_ts_l = node_ts_l
        self.edge_idx_l = e_idx_l
        self.edge_type_l = e_type_l
        self.u_type_l = u_type_l
        self.v_type_l = v_type_l
        self.off_set_l = off_set_l

        if num_edge_type is None:
            num_edge_type = len(np.unique(e_type_l))
        self.num_edge_type = num_edge_type + 1  # padding 0 type
        self.uniform = uniform

    def init_off_set(self, adj_list):
        """
        Params
        ------
          adj_list: List[List[int]]
        """
        n_idx_l = []
        n_ts_l = []
        e_idx_l = []
        e_type_l = []
        u_type_l = []
        v_type_l = []
        off_set_l = [0]
        for i in range(len(adj_list)):
            curr = adj_list[i]  # 节点i的邻居
            curr = sorted(curr, key=lambda x: x[2])  # 根据所属ts排序,以便快速查找之前的邻居
            n_idx_l.extend([x[0] for x in curr])
            e_idx_l.extend([x[1] for x in curr])
            n_ts_l.extend([x[2] for x in curr])
            e_type_l.extend([x[3] for x in curr])
            u_type_l.extend([x[4] for x in curr])
            v_type_l.extend([x[5] for x in curr])

            off_set_l.append(len(n_idx_l))  # 节点i邻居在n_idx的终止下标
        n_idx_l = np.array(n_idx_l)
        n_ts_l = np.array(n_ts_l)
        e_idx_l = np.array(e_idx_l)
        e_type_l = np.array(e_type_l)
        u_type_l = np.array(u_type_l)
        v_type_l = np.array(v_type_l)
        off_set_l = np.array(off_set_l)

        assert (len(n_idx_l) == len(n_ts_l))
        assert (off_set_l[-1] == len(n_ts_l))

        return n_idx_l, n_ts_l, e_idx_l, e_type_l, u_type_l, v_type_l, off_set_l

    def find_before(self, src_idx, cut_time):
        """
        Params
        ------
          src_idx: int
          cut_time: float
        """
        node_idx_l = self.node_idx_l
        node_ts_l = self.node_ts_l  # 需要按时间升序排列
        edge_idx_l = self.edge_idx_l
        edge_type_l = self.edge_type_l
        # u_type_l = self.u_type_l
        v_type_l = self.v_type_l
        off_set_l = self.off_set_l

        ngh_idx = node_idx_l[off_set_l[src_idx]:off_set_l[src_idx + 1]]
        ngh_ts = node_ts_l[off_set_l[src_idx]:off_set_l[src_idx + 1]]
        ngh_e_idx = edge_idx_l[off_set_l[src_idx]:off_set_l[src_idx + 1]]
        ngh_e_type = edge_type_l[off_set_l[src_idx]:off_set_l[src_idx + 1]]
        # ngh_u_type = u_type_l[off_set_l[src_idx]:off_set_l[src_idx + 1]]
        ngh_v_type = v_type_l[off_set_l[src_idx]:off_set_l[src_idx + 1]]

        if len(ngh_idx) == 0 or len(ngh_ts) == 0:
            return ngh_idx, ngh_e_idx, ngh_ts, ngh_e_type, ngh_v_type

        left = 0
        right = len(ngh_idx) - 1

        while left + 1 < right:  # binary search
            mid = (left + right) // 2
            curr_t = ngh_ts[mid]
            if curr_t < cut_time:
                left = mid
            else:
                right = mid

        if ngh_ts[left] >= cut_time:
            return ngh_idx[:left], ngh_e_idx[:left], ngh_ts[:left], ngh_e_type[:left], ngh_v_type[:left]
        elif ngh_ts[right] < cut_time:
            return ngh_idx[:right + 1], ngh_e_idx[:right + 1], ngh_ts[:right + 1], ngh_e_type[:right + 1], ngh_v_type[
                                                                                                           :right + 1]
        else:
            return ngh_idx[:right], ngh_e_idx[:right], ngh_ts[:right], ngh_e_type[:right], ngh_v_type[:right]

    def get_temporal_neighbor(self, src_idx_l, cut_time_l, num_neighbors=20):
        """
        Params
        ------
          src_idx_l: List[int]
          cut_time_l: List[float],
          num_neighbors: int
        """
        assert (len(src_idx_l) == len(cut_time_l))

        out_ngh_node_batch = np.zeros((len(src_idx_l), num_neighbors)).astype(np.int32)
        out_ngh_t_batch = np.zeros((len(src_idx_l), num_neighbors)).astype(np.float32)
        out_ngh_eidx_batch = np.zeros((len(src_idx_l), num_neighbors)).astype(np.int32)
        out_ngh_etype_batch = np.zeros((len(src_idx_l), num_neighbors)).astype(np.int32)
        # out_ngh_utype_batch = np.zeros((len(src_idx_l), num_neighbors)).astype(np.int32)
        out_ngh_vtype_batch = np.zeros((len(src_idx_l), num_neighbors)).astype(np.int32)

        for i, (src_idx, cut_time) in enumerate(zip(src_idx_l, cut_time_l)):
            ngh_idx, ngh_eidx, ngh_ts, ngh_etype, ngh_vtype = self.find_before(src_idx, cut_time)

            if len(ngh_idx) > 0:
                if self.uniform:
                    # samd_idx = np.random.randint(0, len(ngh_idx), num_neighbors)
                    real_num_neighbors = min(num_neighbors, len(ngh_idx))
                    nidx = np.arange(len(ngh_idx)).tolist()
                    samd_idx = random.sample(nidx, real_num_neighbors)

                    out_ngh_node_batch[i, :real_num_neighbors] = ngh_idx[samd_idx]
                    out_ngh_t_batch[i, :real_num_neighbors] = ngh_ts[samd_idx]
                    out_ngh_eidx_batch[i, :real_num_neighbors] = ngh_eidx[samd_idx]
                    out_ngh_etype_batch[i, :real_num_neighbors] = ngh_etype[samd_idx]
                    # out_ngh_utype_batch[i, :real_num_neighbors] = ngh_utype[samd_idx]
                    out_ngh_vtype_batch[i, :real_num_neighbors] = ngh_vtype[samd_idx]

                    # resort based on time
                    pos = out_ngh_t_batch[i, :].argsort()
                    out_ngh_node_batch[i, :] = out_ngh_node_batch[i, :][pos]
                    out_ngh_t_batch[i, :] = out_ngh_t_batch[i, :][pos]
                    out_ngh_eidx_batch[i, :] = out_ngh_eidx_batch[i, :][pos]
                    out_ngh_etype_batch[i, :] = out_ngh_etype_batch[i, :][pos]
                    # out_ngh_utype_batch[i, :] = out_ngh_utype_batch[i, :][pos]
                    out_ngh_vtype_batch[i, :] = out_ngh_vtype_batch[i, :][pos]
                else:
                    ngh_ts = ngh_ts[-num_neighbors:]
                    ngh_idx = ngh_idx[-num_neighbors:]
                    ngh_eidx = ngh_eidx[-num_neighbors:]
                    ngh_etype = ngh_etype[-num_neighbors:]
                    # ngh_utype = ngh_utype[-num_neighbors:]
                    ngh_vtype = ngh_vtype[-num_neighbors:]

                    assert (len(ngh_idx) <= num_neighbors)
                    assert (len(ngh_ts) <= num_neighbors)
                    assert (len(ngh_eidx) <= num_neighbors)
                    assert (len(ngh_etype) <= num_neighbors)
                    # assert(len(ngh_utype) <= num_neighbors)
                    assert (len(ngh_vtype) <= num_neighbors)

                    out_ngh_node_batch[i, num_neighbors - len(ngh_idx):] = ngh_idx
                    out_ngh_t_batch[i, num_neighbors - len(ngh_ts):] = ngh_ts
                    out_ngh_eidx_batch[i, num_neighbors - len(ngh_eidx):] = ngh_eidx
                    out_ngh_etype_batch[i, num_neighbors - len(ngh_etype):] = ngh_etype
                    # out_ngh_utype_batch[i,  num_neighbors - len(ngh_etype):] = ngh_utype
                    out_ngh_vtype_batch[i, num_neighbors - len(ngh_etype):] = ngh_vtype

        return out_ngh_node_batch, out_ngh_eidx_batch, out_ngh_t_batch, out_ngh_etype_batch, out_ngh_vtype_batch

    def get_temporal_hetneighbor(self, src_idx_l, cut_time_l, num_neighbors=10):
        """
        Params
        ------
          src_idx_l: List[int]
          cut_time_l: List[float],
          num_neighbors: int
        """
        assert (len(src_idx_l) == len(cut_time_l))
        total_num_nghs = num_neighbors * self.num_edge_type

        out_ngh_node_batch = np.zeros((len(src_idx_l), total_num_nghs)).astype(np.int32)
        out_ngh_t_batch = np.zeros((len(src_idx_l), total_num_nghs)).astype(np.float32)
        out_ngh_eidx_batch = np.zeros((len(src_idx_l), total_num_nghs)).astype(np.int32)
        out_ngh_etype_batch = np.zeros((len(src_idx_l), total_num_nghs)).astype(np.int32)
        out_ngh_vtype_batch = np.zeros((len(src_idx_l), total_num_nghs)).astype(np.int32)

        for i, (src_idx, cut_time) in enumerate(zip(src_idx_l, cut_time_l)):
            ngh_idx, ngh_eidx, ngh_ts, ngh_etype, ngh_vtype = self.find_before(src_idx, cut_time)

            if len(ngh_idx) > 0:
                etype_mask = {}
                for etype in np.unique(ngh_etype):
                    etype_mask[etype] = ngh_etype == etype

                ix_l = []
                ix = np.arange(len(ngh_idx))
                for etype, mask in etype_mask.items():
                    if self.uniform:
                        # 同一分布选择的邻居，每一类最多选num个
                        tmp_idx = ix[mask]
                        real_num_neighbors = min(num_neighbors, len(tmp_idx))
                        sam_idx = random.sample(tmp_idx.tolist(), real_num_neighbors)
                        ix_l.append(sam_idx)
                    else:
                        ix_l.append(ix[mask][-num_neighbors:])  # 选择时间最近的邻居，每一类最多选num个

                nidx = np.sort(np.concatenate(ix_l))
                real_num_nghs = len(nidx)

                out_ngh_node_batch[i, total_num_nghs - real_num_nghs:] = ngh_idx[nidx]
                out_ngh_t_batch[i, total_num_nghs - real_num_nghs:] = ngh_ts[nidx]
                out_ngh_eidx_batch[i, total_num_nghs - real_num_nghs:] = ngh_eidx[nidx]
                out_ngh_etype_batch[i, total_num_nghs - real_num_nghs:] = ngh_etype[nidx]
                out_ngh_vtype_batch[i, total_num_nghs - real_num_nghs:] = ngh_vtype[nidx]

        return out_ngh_node_batch, out_ngh_eidx_batch, out_ngh_t_batch, out_ngh_etype_batch, out_ngh_vtype_batch

    def find_k_hop(self, k, src_idx_l, cut_time_l, num_neighbors=20):
        """ Sampling the k-hop temporal sub graph
        """
        x, y, z = self.get_temporal_neighbor(src_idx_l, cut_time_l, num_neighbors)
        node_records = [x]
        eidx_records = [y]
        t_records = [z]
        for _ in range(k - 1):
            ngn_node_set, ngh_t_set = node_records[-1], t_records[-1]  # [N, *([num_neighbors] * (k - 1))]
            orig_shape = ngn_node_set.shape
            ngn_node_set = ngn_node_set.flatten()
            ngn_t_set = ngh_t_set.flatten()
            out_ngh_node_batch, out_ngh_eidx_batch, out_ngh_t_batch = self.get_temporal_neighbor(ngn_node_set,
                                                                                                 ngn_t_set,
                                                                                                 num_neighbors)
            out_ngh_node_batch = out_ngh_node_batch.reshape(*orig_shape, num_neighbors)  # [N, *([num_neighbors] * k)]
            out_ngh_eidx_batch = out_ngh_eidx_batch.reshape(*orig_shape, num_neighbors)
            out_ngh_t_batch = out_ngh_t_batch.reshape(*orig_shape, num_neighbors)

            node_records.append(out_ngh_node_batch)
            eidx_records.append(out_ngh_eidx_batch)
            t_records.append(out_ngh_t_batch)
        return node_records, eidx_records, t_records

    def find_k_hop_subgraph(self, k, src_idx_l, src_time_l, num_neighbors=20):
        """ Sampling the k-hop temporal sub graph
        """
        batch_size = len(src_idx_l)
        edge = []
        eidx = []
        t_delta = []
        for _ in range(k):
            ngh_node_batch, ngh_eidx_batch, ngh_t_batch = self.get_temporal_neighbor(src_idx_l, src_time_l,
                                                                                     num_neighbors)
            ngh_node_set = ngh_node_batch.flatten()
            e = np.stack([src_idx_l.repeat(num_neighbors), ngh_node_set])

            edge.append(e)
            eidx.append(ngh_eidx_batch.flatten())
            ngh_t_set = ngh_t_batch.flatten()
            ngh_t_delta = np.abs(src_time_l.repeat(num_neighbors) - ngh_t_set)
            t_delta.append(ngh_t_delta)

            src_idx_l = ngh_node_set
            src_time_l = ngh_t_set

        edge = np.concatenate(edge, axis=1)
        eidx = np.concatenate(eidx)
        t_delta = np.concatenate(t_delta)

        edge = edge.transpose().reshape(batch_size, -1, 2).transpose(0, 2, 1)
        eidx = eidx.reshape(batch_size, -1)
        t_delta = t_delta.reshape(batch_size, -1)

        edge_batch = []
        eidx_batch = []
        t_batch = []
        node_set_batch = []
        for i in range(batch_size):
            e = edge[i]
            # mask = (e==e)[0]
            mask = e != 0
            mask = mask[0] * mask[1]
            e = e[:, mask]

            # get node set and reindex edge_index
            node_set, e = np.unique(e, return_inverse=True)
            e = e.reshape(2, -1)
            edge_batch.append(e)
            node_set_batch.append(node_set)
            eidx_batch.append(eidx[i][mask])
            t_batch.append(t_delta[i][mask])

        return edge_batch, eidx_batch, t_batch, node_set_batch


class THAN(nn.Module):
    def __init__(self, ngh_finder: NeighborFinder, n_feat, e_feat, e_type_feat=None, num_n_type=1, num_e_type=1,
                 t_dim=128, use_time='time', num_layers=2, n_head=4, dropout=0.1, seq_len=None):
        super(THAN, self).__init__()
        self.num_layers = num_layers
        self.ngh_finder = ngh_finder
        self.logger = logging.getLogger(__name__)

        n_feat = torch.from_numpy(n_feat.astype(np.float32))
        e_feat = torch.from_numpy(e_feat.astype(np.float32))
        self.node_embed = nn.Embedding.from_pretrained(n_feat, padding_idx=0, freeze=True)
        self.edge_embed = nn.Embedding.from_pretrained(e_feat, padding_idx=0, freeze=True)

        self.n_feat_dim = n_feat.shape[1]
        self.e_feat_dim = e_feat.shape[1]
        self.t_feat_dim = t_dim
        self.out_dim = self.n_feat_dim

        self.num_n_type = num_n_type
        self.num_e_type = num_e_type

        if e_type_feat is not None:
            e_type_feat = torch.from_numpy(e_type_feat.astype(np.float32))

        # transfer layer
        self.transfer = Transfer(num_n_type, num_e_type, self.n_feat_dim, self.n_feat_dim, e_type_feat)

        # attention model
        self.logger.info('Aggregation uses attention model')
        self.attn_model_list = nn.ModuleList([AttnModel(self.n_feat_dim,
                                                        self.e_feat_dim,
                                                        self.t_feat_dim,
                                                        self.transfer,
                                                        n_head=n_head,
                                                        dropout=dropout,
                                                        num_n_type=num_n_type,
                                                        num_e_type=num_e_type) for _ in range(num_layers)])

        # time encoder
        if use_time == 'time':
            self.logger.info('Using time encoding')
            self.time_encoder = TimeEncode(expand_dim=self.t_feat_dim)
        elif use_time == 'pos':
            assert (seq_len is not None)
            self.logger.info('Using positional encoding')
            self.time_encoder = PosEncode(expand_dim=self.t_feat_dim, seq_len=seq_len)
        elif use_time == 'empty':
            self.logger.info('Using empty encoding')
            self.time_encoder = EmptyEncode(expand_dim=self.t_feat_dim)
        else:
            raise ValueError('invalid time option!')

        self.affinity_score = HetMatchDecoder(num_e_type, self.out_dim, e_type_feat)

    def forward(self, src_idx_l, tgt_idx_l, cut_time_l, src_utype_l, tgt_utype_l, etype_l, num_neighbors=20):
        src_embed = self.tem_conv(src_idx_l, cut_time_l, src_utype_l, self.num_layers, num_neighbors)
        tgt_embed = self.tem_conv(tgt_idx_l, cut_time_l, tgt_utype_l, self.num_layers, num_neighbors)

        score = self.affinity_score(src_embed, tgt_embed, etype_l).squeeze(dim=-1)

        return score.sigmoid()

    def link_contrast(self, src_idx_l, tgt_idx_l, bgd_idx_l, cut_time_l, src_utype_l, tgt_utype_l, bgd_utype_l, etype_l,
                      num_neighbors=20):
        src_embed = self.tem_conv(src_idx_l, cut_time_l, src_utype_l, self.num_layers, num_neighbors)
        tgt_embed = self.tem_conv(tgt_idx_l, cut_time_l, tgt_utype_l, self.num_layers, num_neighbors)
        # fake targets
        bgd_embed = self.tem_conv(bgd_idx_l, cut_time_l, bgd_utype_l, self.num_layers, num_neighbors)

        pos_score = self.affinity_score(src_embed, tgt_embed, etype_l).squeeze(dim=-1)
        neg_score = self.affinity_score(src_embed, bgd_embed, etype_l).squeeze(dim=-1)
        return pos_score.sigmoid(), neg_score.sigmoid()

    def tem_conv(self, src_idx_l, cut_time_l, src_utype_l, curr_layers, num_neighbors=20, uniform=None, neg=False):
        assert (curr_layers >= 0)

        device = self.node_embed.weight.device
        batch_size = len(src_idx_l)

        if curr_layers == 0:
            return self.node_embed(torch.from_numpy(src_idx_l).long().to(device))

        src_node_conv_feat = self.tem_conv(src_idx_l, cut_time_l, src_utype_l,
                                           curr_layers=curr_layers - 1,
                                           num_neighbors=num_neighbors,
                                           uniform=uniform, neg=neg)

        cut_time_l_th = torch.from_numpy(cut_time_l).float().unsqueeze(1)  # [B, 1]
        # query node always has the start time -> time span == 0
        src_node_t_embed = self.time_encoder(torch.zeros_like(cut_time_l_th).to(device))

        src_ngh_node_batch, src_ngh_eidx_batch, src_ngh_t_batch, src_ngh_etype, src_ngh_vtype \
            = self.ngh_finder.get_temporal_hetneighbor(src_idx_l, cut_time_l, num_neighbors)

        # get previous layer's node features
        src_ngh_node_batch_flat = src_ngh_node_batch.flatten()  # reshape(batch_size, -1)
        src_ngh_t_batch_flat = src_ngh_t_batch.flatten()  # reshape(batch_size, -1)
        src_ngh_vtype_flat = src_ngh_vtype.flatten()  # reshape(batch_size, -1)
        src_ngh_node_conv_feat = self.tem_conv(src_ngh_node_batch_flat,
                                               src_ngh_t_batch_flat,
                                               src_ngh_vtype_flat,
                                               curr_layers=curr_layers - 1,
                                               num_neighbors=num_neighbors,
                                               uniform=uniform,
                                               neg=neg)

        src_ngh_feat = src_ngh_node_conv_feat.view(batch_size, num_neighbors * (self.num_e_type + 1), -1)

        src_ngh_node_batch_th = torch.from_numpy(src_ngh_node_batch).long().to(device)
        src_ngh_eidx_batch = torch.from_numpy(src_ngh_eidx_batch).long().to(device)

        src_ngh_t_batch_delta = cut_time_l[:, np.newaxis] - src_ngh_t_batch
        src_ngh_t_batch_th = torch.from_numpy(src_ngh_t_batch_delta).float().to(device)

        # get edge time features and edge features
        src_ngh_t_embed = self.time_encoder(src_ngh_t_batch_th)  # △t = t0-ti
        src_ngn_edge_feat = self.edge_embed(src_ngh_eidx_batch)  # edge features

        # src/ngh node & edge label
        src_utype = torch.from_numpy(src_utype_l).long().to(device)
        src_ngh_etype = torch.from_numpy(src_ngh_etype).long().to(device)
        src_ngh_vtype = torch.from_numpy(src_ngh_vtype).long().to(device)

        # attention aggregation
        mask = src_ngh_node_batch_th == 0
        attn_m = self.attn_model_list[curr_layers - 1]

        local, _ = attn_m(src_node_conv_feat,
                          src_node_t_embed,
                          src_ngh_feat,
                          src_ngh_t_embed,
                          src_ngn_edge_feat,
                          src_ngh_etype,
                          src_utype,
                          src_ngh_vtype,
                          mask)

        return local


if __name__ == '__main__':
    block = THAN()
    input = torch.rand()
    output = block(input)
    print(input.size())
    print(output.size())
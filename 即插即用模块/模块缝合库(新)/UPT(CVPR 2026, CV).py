import torch
import torch.nn as nn
import torch.nn.functional as F
from einops import rearrange


class _Memory_Block_prompt(nn.Module):
    def __init__(self, hdim, kdim, moving_average_rate=0.999):
        super().__init__()
        self.c = hdim
        self.k = kdim

        self.moving_average_rate = moving_average_rate
        self.units = nn.Parameter(torch.randn(kdim, hdim), requires_grad=True)
        self.prompts = nn.Parameter(torch.rand(kdim, hdim), requires_grad=True)

    def update(self, x, score, m=None):
        '''
            x: (n, c)
            e: (k, c)
            score: (n, k)
        '''
        # if m is None:
        #     m = self.units.weight.data
        m = self.units
        x = x.detach()
        embed_ind = torch.max(score, dim=1)[1]  # (n, )
        embed_onehot = F.one_hot(embed_ind, self.k).type(x.dtype)  # (n, k)
        embed_onehot_sum = embed_onehot.sum(0)
        embed_sum = x.transpose(0, 1) @ embed_onehot  # (c, k)
        embed_mean = embed_sum / (embed_onehot_sum + 1e-6)
        new_data = m * self.moving_average_rate + embed_mean.t() * (1 - self.moving_average_rate)
        if self.training:
            # self.units.weight.data = new_data
            self.units = nn.Parameter(new_data)
        return new_data

    def forward(self, x, update_flag=True):
        '''
          x: (b, c, h, w)
          embed: (k, c)
        '''

        b, c, h, w = x.size()
        assert c == self.c
        k, c = self.k, self.c

        x = x.permute(0, 2, 3, 1)
        x = x.reshape(-1, c)  # (n, c)

        # m = self.units.weight.data # (k, c)
        m = self.units
        p = self.prompts

        xn = F.normalize(x, dim=1)  # (n, c)
        mn = F.normalize(m, dim=1)  # (k, c)
        score = torch.matmul(xn, mn.t())  # (n, k)

        if update_flag:
            m = self.update(x, score, m)
            mn = F.normalize(m, dim=1)  # (k, c)
            score = torch.matmul(xn, mn.t())  # (n, k)

        soft_label = F.softmax(score, dim=1)
        # print(score.shape, soft_label.shape) #
        out_m = torch.matmul(soft_label, m)  # (n, c)
        out_m = out_m.view(b, h, w, c).permute(0, 3, 1, 2)
        out = torch.matmul(soft_label, p)
        out = out.view(b, h, w, c).permute(0, 3, 1, 2)
        soft_label = soft_label.view(b, h, w, -1).permute(0, 3, 1, 2)
        # score = score.view(b, h, w, -1).permute(0, 3, 1, 2)
        return out, out_m, soft_label


class FeedForward(nn.Module):
    def __init__(self, dim, mult=4):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(dim, dim * mult, 1, 1, bias=False),
            GELU(),
            nn.Conv2d(dim * mult, dim * mult, 3, 1, 1, bias=False, groups=dim * mult),
            GELU(),
            nn.Conv2d(dim * mult, dim, 1, 1, bias=False), )

    def forward(self, x):
        out = self.net(x.permute(0, 3, 1, 2))
        return out.permute(0, 2, 3, 1)


class PreNorm(nn.Module):
    def __init__(self, dim, fn):
        super().__init__()
        self.fn = fn
        self.norm = nn.LayerNorm(dim)

    def forward(self, x, *args, **kwargs):
        x = self.norm(x)
        return self.fn(x, *args, **kwargs)


class GELU(nn.Module):
    def forward(self, x):
        return F.gelu(x)


class IG_MSA(nn.Module):
    def __init__(
            self,
            dim,
            dim_head=64,
            heads=8,
    ):
        super().__init__()
        self.num_heads = heads
        self.dim_head = dim_head
        self.to_q = nn.Linear(dim, dim_head * heads, bias=False)
        self.to_k = nn.Linear(dim, dim_head * heads, bias=False)
        self.to_v = nn.Linear(dim, dim_head * heads, bias=False)
        self.rescale = nn.Parameter(torch.ones(heads, 1, 1))
        self.proj = nn.Linear(dim_head * heads, dim, bias=True)
        self.dim = dim

    def forward(self, x, var):
        """
        x_in: [b,h,w,c]
        illu_fea: [b,h,w,c]
        return out: [b,h,w,c]
        """
        # print(x_low.shape, x_high.shape) # torch.Size([1, 256, 512, 128]) torch.Size([1, 256, 512, 128])
        b, h, w, c = x.shape
        # pos_embed = self.get_2d_sin_pos_encoding(h, w, c, x.device)
        x = x  # + pos_embed   # 위치 정보 주입

        x = x.reshape(b, h * w, c)
        var = var.reshape(b, h * w, c)
        # print("X shape ", x.shape) # torch.Size([1, 131072, 128])
        q_inp = self.to_q(x)
        k_inp = self.to_k(x)
        v_inp = self.to_v(x)
        # print(q_inp.shape, k_inp.shape, v_inp.shape) # torch.Size([1, 131072, 128]) torch.Size([1, 131072, 128]) torch.Size([1, 131072, 128])
        q, k, v = map(lambda t: rearrange(t, 'b n (h d) -> b h n d', h=self.num_heads), (q_inp, k_inp, v_inp))
        # print(q.shape, k.shape, v.shape, high_attn.shape)
        # q: b,heads,hw,c
        q = q.transpose(-2, -1)
        k = k.transpose(-2, -1)
        v = v.transpose(-2, -1)
        q = F.normalize(q, dim=-1, p=2)
        k = F.normalize(k, dim=-1, p=2)
        attn = (k @ q.transpose(-2, -1))  # A = K^T*Q
        attn = attn * self.rescale
        attn = attn.softmax(dim=-1)
        x = attn @ v  # b,heads,d,hw
        x = x.permute(0, 3, 1, 2)  # Transpose
        x = x.reshape(b, h * w, self.num_heads * self.dim_head)
        out_c = self.proj(x).view(b, h, w, c)
        out = out_c
        return out


class IG_MSA_memory(nn.Module):
    def __init__(
            self,
            dim,
            dim_head=64,
            heads=8,
            down_kernel=3,
            refine_act=nn.ReLU,  # 필요시 GELU 등으로 교체 가능
    ):
        super().__init__()
        self.num = 256
        self.momory_block = _Memory_Block_prompt(hdim=dim, kdim=self.num, moving_average_rate=0.9)

        self.num_heads = heads
        self.dim_head = dim_head
        self.dim = dim

        # QKV 프로젝션 (channels-last: [B,H,W,C] 기준으로 Linear 사용)
        self.to_q = nn.Linear(dim, dim_head * heads, bias=False)
        self.to_k = nn.Linear(dim, dim_head * heads, bias=False)
        self.to_v = nn.Linear(dim, dim_head * heads, bias=False)

        # attention 스케일 (per-head learnable)
        self.rescale = nn.Parameter(torch.ones(heads, 1, 1))

        # attention 출력 투영
        self.proj = nn.Linear(dim_head * heads, dim, bias=True)

        # Low-res 경로: 다운/업 + High-res refinement
        self.down = nn.Conv2d(dim, dim, kernel_size=down_kernel, stride=2, padding=down_kernel // 2, bias=False)
        self.up = nn.ConvTranspose2d(dim, dim, kernel_size=2, stride=2, bias=False)

        self.refine = nn.Sequential(
            nn.Conv2d(dim, dim, 3, 1, 1, bias=False),
            refine_act(inplace=True),
            nn.Conv2d(dim, dim, 3, 1, 1, bias=False),
            refine_act(inplace=True),
        )

        # 가벼운 활성/게이트가 필요하면 사용
        self.act = nn.GELU()
        self.alpha = nn.Parameter(torch.zeros((1, 1, dim, 1)), requires_grad=True)

    # ---- 내부: 저해상도에서 dual-direction prompt attention ----
    def dual_prompt_attention_lowres(self, x_lr_bhwc, z_lr_bhwc, z_m_lr_bhwc):
        """
        x_lr_bhwc, z_lr_bhwc, z_m_lr_bhwc: [B, Hlr, Wlr, C]
        """
        B, Hlr, Wlr, C = x_lr_bhwc.shape

        # ===== Horizontal =====
        q_h = self.to_q(x_lr_bhwc.reshape(B * Hlr, Wlr, C))
        k_h = self.to_k(z_lr_bhwc.reshape(B * Hlr, Wlr, C))
        v_h = self.to_v(z_m_lr_bhwc.reshape(B * Hlr, Wlr, C))

        q_h, k_h, v_h = map(lambda t: rearrange(t, 'b n (h d) -> b h n d', h=self.num_heads), (q_h, k_h, v_h))
        q_h = F.normalize(q_h, dim=-1);
        k_h = F.normalize(k_h, dim=-1)
        attn_h = torch.matmul(q_h, k_h.transpose(-2, -1)) * self.rescale  # [B*Hlr, heads, Wlr, Wlr]
        attn_h = attn_h.softmax(dim=-1)
        out_h = torch.matmul(attn_h, v_h)  # [B*Hlr, heads, Wlr, dim_head]
        out_h = rearrange(out_h, 'b h n d -> b n (h d)').reshape(B, Hlr, Wlr, C)

        # ===== Vertical =====
        q_v = self.to_q(x_lr_bhwc.permute(0, 2, 1, 3).reshape(B * Wlr, Hlr, C))
        k_v = self.to_k(z_lr_bhwc.permute(0, 2, 1, 3).reshape(B * Wlr, Hlr, C))
        v_v = self.to_v(z_m_lr_bhwc.permute(0, 2, 1, 3).reshape(B * Wlr, Hlr, C))

        q_v, k_v, v_v = map(lambda t: rearrange(t, 'b n (h d) -> b h n d', h=self.num_heads), (q_v, k_v, v_v))
        q_v = F.normalize(q_v, dim=-1);
        k_v = F.normalize(k_v, dim=-1)
        attn_v = torch.matmul(q_v, k_v.transpose(-2, -1)) * self.rescale  # [B*Wlr, heads, Hlr, Hlr]
        attn_v = attn_v.softmax(dim=-1)
        out_v = torch.matmul(attn_v, v_v)  # [B*Wlr, heads, Hlr, dim_head]
        out_v = rearrange(out_v, 'b h n d -> b n (h d)').reshape(B, Wlr, Hlr, C).permute(0, 2, 1, 3)

        # Fuse 두 방향
        out_lr = (out_h + out_v) * 0.5
        # 최종 proj (head concat → dim)
        out_lr = self.proj(out_lr)
        return out_lr  # [B, Hlr, Wlr, C]

    def forward(self, x, var):
        """
        x:   [B, H, W, C]
        var: [B, H, W, C]
        return: [B, H, W, C]
        """
        # ---- Memory block에서 prompt(z), memory(z_m) 생성 ----
        z, z_m, soft_label = self.momory_block(var.permute(0, 3, 1, 2), update_flag=self.training)  # [B,C,H,W]
        z = z.permute(0, 2, 3, 1)  # [B,H,W,C]
        z_m = z_m.permute(0, 2, 3, 1)

        B, H, W, C = x.shape

        # ---- Low-resolution로 다운샘플 ----
        x_chw = x.permute(0, 3, 1, 2)  # [B,C,H,W]
        x_lr = self.down(x_chw)  # [B,C,H/2,W/2]
        Hlr, Wlr = x_lr.shape[2], x_lr.shape[3]

        # z, z_m도 같은 해상도로 보간
        z_lr = F.interpolate(z.permute(0, 3, 1, 2), size=(Hlr, Wlr), mode='bilinear', align_corners=False)
        z_m_lr = F.interpolate(z_m.permute(0, 3, 1, 2), size=(Hlr, Wlr), mode='bilinear', align_corners=False)

        # BHWC로 변환해 dual attention 수행
        x_lr_bhwc = x_lr.permute(0, 2, 3, 1)  # [B,Hlr,Wlr,C]
        z_lr_bhwc = z_lr.permute(0, 2, 3, 1)
        z_m_lr_bhwc = z_m_lr.permute(0, 2, 3, 1)

        # out_lr_bhwc = self.dual_prompt_attention_lowres(x_lr_bhwc, z_lr_bhwc, z_m_lr_bhwc)  # [B,Hlr,Wlr,C]
        out_lr_bhwc = self.dual_prompt_attention_lowres(x_lr_bhwc, z_lr_bhwc, x_lr_bhwc)  # [B,Hlr,Wlr,C]

        # ---- 업샘플 및 High-res refinement ----
        out_lr_chw = out_lr_bhwc.permute(0, 3, 1, 2)  # [B,C,Hlr,Wlr]
        out_hr_chw = self.up(out_lr_chw)[:, :, :H, :W]  # crop to (H,W)

        # skip 연결 + conv refinement
        out_chw = self.refine(out_hr_chw + x_chw)  # [B,C,H,W]
        out = out_chw.permute(0, 2, 3, 1)  # [B,H,W,C]

        return out, soft_label


class UPT(nn.Module):
    def __init__(
            self,
            dim,
            dim_head=64,
            heads=8,
            num_blocks=2,
    ):
        super().__init__()
        self.blocks = nn.ModuleList([])
        for _ in range(num_blocks):
            self.blocks.append(nn.ModuleList([
                IG_MSA_memory(dim=dim, dim_head=dim_head, heads=heads),
                PreNorm(dim, FeedForward(dim=dim))
            ]))
            self.blocks.append(nn.ModuleList([
                IG_MSA(dim=dim, dim_head=dim_head, heads=heads),
                PreNorm(dim, FeedForward(dim=dim))
            ]))

    def forward(self, x, var):
        """
        x: [b,c,h,w]
        var: [b,c,h,w]
        return out: [b,c,h,w]
        """

        x = x.permute(0, 2, 3, 1)
        var = var.permute(0, 2, 3, 1)

        s = None

        for (attn, ff) in self.blocks:

            if isinstance(attn, IG_MSA_memory):

                x_, s = attn(x, var)
                x = x + x_

            else:

                x = x + attn(x, var)

            x = x + ff(x)

        out = x.permute(0, 3, 1, 2)

        return out, s

if __name__ == '__main__':

    B = 2
    C = 128
    H = 64
    W = 64

    block = UPT(
        dim=C,
        dim_head=16,
        heads=8,
        num_blocks=2
    ).to('cuda')

    input = torch.rand(B, C, H, W).to('cuda')

    # var 一般是另外一路特征
    var = torch.randn(B, C, H, W).to('cuda')

    output, soft_label = block(input, var)

    print("input shape      :", input.shape)
    print("output shape     :", output.shape)
    print("soft label shape :", soft_label.shape)
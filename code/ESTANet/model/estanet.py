import torch
import torch.nn as nn
import torch.nn.functional as F
from model.model_builder import META_ARCHITECTURES
import math
import random
import json
import os
import numpy as np
import copy
import time


FEATURE_SIZES = {
    'rgb_anet_resnet50': 2048,
    "vc_v_features": 256,
    "vc_v_features_10fps": 256
}




@META_ARCHITECTURES.register("RobustROAD")
class RobustROAD(nn.Module):
    
    def __init__(self, cfg, device):
        super(RobustROAD, self).__init__()
        self.input_dim = 0
        self.input_dim += FEATURE_SIZES[cfg['rgb_type']]

        self.hidden_dim = cfg['hidden_dim']
        self.num_layers = cfg['num_layers']
        self.out_dim = cfg['num_classes']

        self.relu = nn.ReLU()
        self.embedding_dim = cfg['embedding_dim']
        
        self.first_layer = nn.Sequential(
            nn.Linear(self.input_dim, self.embedding_dim),
            nn.LayerNorm(self.embedding_dim),
            nn.ReLU(),
        )

        self.s_gru = nn.GRU(self.embedding_dim, self.hidden_dim, self.num_layers, batch_first=True)
        self.l_gru = nn.GRU(self.embedding_dim, self.hidden_dim, self.num_layers, batch_first=True)

        self.s_f_classification = nn.Sequential(
            nn.Linear(self.hidden_dim, self.out_dim)
        )
        self.l_f_classification = nn.Sequential(
            nn.Linear(self.hidden_dim, self.out_dim)
        )

        self.h0 = torch.zeros(self.num_layers, 1, self.hidden_dim)
        # self.attn_h0 = torch.zeros(self.num_layers, 1, self.hidden_dim)
        # self.attention = nn.MultiheadAttention(self.embedding_dim, num_heads=8, batch_first=True)
        # self.action_features = {}

        # if "input_features" not in cfg:
        #     step_feature_dir = "vc_v_step_features"
        # else:
        #     step_feature_dir = cfg["input_features"]

        # filenames = os.listdir(os.path.join(cfg["root_path"], step_feature_dir))
        # for filename in filenames:
        #     filename = filename[:-4]
        #     if filename not in self.action_features:
        #         self.action_features[filename] = torch.from_numpy(np.load(os.path.join(cfg["root_path"], step_feature_dir, filename+".npy"))).float()

        # self.step_feature = []
        # idx = 0
        # for key, features in self.action_features.items():
        #     self.step_feature.append(features)
        #     idx += 1
        # self.step_feature = torch.stack(self.step_feature, dim=0)#.unsqueeze(0).repeat(B, 1, 1)
        # self.step_feature = self.step_feature.to(device)

    def forward(self, s_rgb_input, l_rgb_input=None, s_target=None, l_target=None):
        s_x = self.first_layer(s_rgb_input)
        l_x = self.first_layer(l_rgb_input)

        B, s_T, _ = s_x.shape
        B, l_T, _ = l_x.shape
        h0 = self.h0.expand(-1, B, -1).to(s_x.device)
        # attn_h0 = self.attn_h0.expand(-1, B, -1).to(s_x.device)

        # step_feature = self.first_layer(self.step_feature.unsqueeze(0).repeat(B, 1, 1))
        # s_attn_x, _ = self.attention(s_x, step_feature, step_feature)
        # l_attn_x, _ = self.attention(l_x, step_feature, step_feature)

        # for visualize
        # temp_s_attn_x = s_attn_x
        # temp_l_attn_x = l_attn_x

        s_ht, s_hid = self.s_gru(s_x, h0)
        l_ht, l_hid = self.l_gru(l_x, h0)
        # s_attn_ht, s_attn_hid = self.s_gru(s_attn_x, attn_h0)
        # l_attn_ht, l_attn_hid = self.l_gru(l_attn_x, attn_h0)
        
        s_ht = self.relu(s_ht)
        l_ht = self.relu(l_ht)
        # s_attn_ht = self.relu(s_attn_ht)
        # l_attn_ht = self.relu(l_attn_ht)

        s_logits = self.s_f_classification(s_ht)
        l_logits = self.l_f_classification(l_ht)
        # s_attn_logits = self.s_f_classification(s_attn_ht)
        # l_attn_logits = self.l_f_classification(l_attn_ht)

        out_dict = {}

        out_dict['s_logits'] = s_logits
        out_dict['l_logits'] = l_logits
        out_dict['l_feat'] = self.relu(l_x)

        # if self.training:
        #     out_dict['s_logits'] = s_logits
        #     out_dict['l_logits'] = l_logits
        #     out_dict['s_attn_logits'] = s_attn_logits
        #     out_dict['l_attn_logits'] = l_attn_logits
        # else:
        #     out_dict['s_logits'] = s_logits
        #     out_dict['l_logits'] = l_logits
        #     out_dict['s_attn_logits'] = s_attn_logits
        #     out_dict['l_attn_logits'] = l_attn_logits
        #     out_dict['s_x'] = self.relu(s_x)
        #     out_dict['s_attn_x'] = self.relu(temp_s_attn_x)
        return out_dict

# @META_ARCHITECTURES.register("SensitiveROAD")
# class SensitiveROAD(nn.Module):
    
#     def __init__(self, cfg, device):
#         super(SensitiveROAD, self).__init__()
#         self.input_dim = 0
#         self.input_dim += FEATURE_SIZES[cfg['rgb_type']]

#         self.hidden_dim = cfg['hidden_dim']
#         self.num_layers = cfg['num_layers']
#         self.out_dim = cfg['num_classes']

#         self.relu = nn.ReLU()
#         self.embedding_dim = cfg['embedding_dim']
        
#         self.first_layer = nn.Sequential(
#             nn.Linear(self.input_dim, self.embedding_dim),
#             nn.LayerNorm(self.embedding_dim),
#             nn.ReLU(),
#         )

#         # new design
#         self.ds_gru = nn.GRU(self.embedding_dim, self.embedding_dim * 2, self.num_layers, batch_first=True)
#         self.dl_gru = nn.GRU(self.embedding_dim, self.embedding_dim * 2, self.num_layers, batch_first=True)
#         self.s_gru = nn.GRU(self.embedding_dim, self.hidden_dim, self.num_layers, batch_first=True)
#         self.l_gru = nn.GRU(self.embedding_dim, self.hidden_dim, self.num_layers, batch_first=True)

#         self.s_f_classification = nn.Sequential(
#             nn.Linear(self.hidden_dim, self.out_dim)
#         )
#         self.l_f_classification = nn.Sequential(
#             nn.Linear(self.hidden_dim, self.out_dim)
#         )

#         self.h0 = torch.zeros(self.num_layers, 1, self.hidden_dim)
#         # self.attn_h0 = torch.zeros(self.num_layers, 1, self.hidden_dim)
#         # self.attention = nn.MultiheadAttention(self.embedding_dim, num_heads=8, batch_first=True)
#         # self.action_features = {}

#         # if "input_features" not in cfg:
#         #     step_feature_dir = "vc_v_step_features"
#         # else:
#         #     step_feature_dir = cfg["input_features"]

#         # filenames = os.listdir(os.path.join(cfg["root_path"], step_feature_dir))
#         # for filename in filenames:
#         #     filename = filename[:-4]
#         #     if filename not in self.action_features:
#         #         self.action_features[filename] = torch.from_numpy(np.load(os.path.join(cfg["root_path"], step_feature_dir, filename+".npy"))).float()

#         # self.step_feature = []
#         # idx = 0
#         # for key, features in self.action_features.items():
#         #     self.step_feature.append(features)
#         #     idx += 1
#         # self.step_feature = torch.stack(self.step_feature, dim=0)#.unsqueeze(0).repeat(B, 1, 1)
#         # self.step_feature = self.step_feature.to(device)

#     def forward(self, s_rgb_input, l_rgb_input=None, s_target=None, l_target=None):

#         s_x = self.first_layer(s_rgb_input)
#         l_x = self.first_layer(l_rgb_input)

#         B, s_T, _ = s_x.shape
#         B, l_T, _ = l_x.shape
#         h0 = self.h0.expand(-1, B, -1).to(s_x.device)
#         # attn_h0 = self.attn_h0.expand(-1, B, -1).to(s_x.device)

#         # step_feature = self.first_layer(self.step_feature.unsqueeze(0).repeat(B, 1, 1))
#         # s_attn_x, _ = self.attention(s_x, step_feature, step_feature)
#         # l_attn_x, _ = self.attention(l_x, step_feature, step_feature)

#         # # for visualize
#         # temp_s_attn_x = s_attn_x
#         # temp_l_attn_x = l_attn_x

#         # ds, _ = self.ds_gru(s_attn_x)
#         # dl, _ = self.dl_gru(l_attn_x)

#         ds, _ = self.ds_gru(s_x)
#         dl, _ = self.dl_gru(l_x)
#         ds = self.relu(ds)
#         dl = self.relu(dl)
        
#         ds_w = ds[:, :, :self.embedding_dim]
#         ds_b = ds[:, :, self.embedding_dim:]
#         # s_attn_x = ds_w * s_attn_x + ds_b
#         dynamic_s_x = ds_w * s_x + ds_b

#         dl_w = dl[:, :, :self.embedding_dim]
#         dl_b = dl[:, :, self.embedding_dim:]
#         # l_attn_x = dl_w * l_attn_x + dl_b
#         dynamic_l_x = dl_w * l_x + dl_b

#         s_ht, _ = self.s_gru(s_x, h0)
#         l_ht, _ = self.l_gru(l_x, h0)
#         dynamic_s_ht, _ = self.s_gru(dynamic_s_x, h0)
#         dynamic_l_ht, _ = self.l_gru(dynamic_l_x, h0)
#         # s_attn_ht, s_attn_hid = self.s_gru(s_attn_x, attn_h0)
#         # l_attn_ht, l_attn_hid = self.l_gru(l_attn_x, attn_h0)

#         s_ht = self.relu(s_ht)
#         l_ht = self.relu(l_ht)
#         dynamic_s_ht = self.relu(dynamic_s_ht)
#         dynamic_l_ht = self.relu(dynamic_l_ht)
        
#         s_logits = self.s_f_classification(s_ht)
#         l_logits = self.l_f_classification(l_ht)
#         dynamic_s_logits = self.s_f_classification(dynamic_s_ht)
#         dynamic_l_logits = self.l_f_classification(dynamic_l_ht)

#         out_dict = {}

#         out_dict['s_logits'] = s_logits
#         out_dict['l_logits'] = l_logits
#         out_dict['dynamic_s_logits'] = dynamic_s_logits
#         out_dict['dynamic_l_logits'] = dynamic_l_logits
#         out_dict['ds'] = ds
#         out_dict['dl'] = dl

#         # if self.training:
#         #     out_dict['s_logits'] = s_logits
#         #     out_dict['l_logits'] = l_logits
#         #     out_dict['s_attn_logits'] = s_attn_logits
#         #     out_dict['l_attn_logits'] = l_attn_logits
#         #     out_dict['ds'] = ds
#         #     out_dict['dl'] = dl
#         # else:
#         #     out_dict['s_logits'] = s_logits
#         #     out_dict['l_logits'] = l_logits
#         #     out_dict['s_attn_logits'] = s_attn_logits
#         #     out_dict['l_attn_logits'] = l_attn_logits
#         #     out_dict['ds_s_attn_x'] = self.relu(s_attn_x)
#         #     out_dict['dl_l_attn_x'] = self.relu(l_attn_x)
#         #     out_dict['s_x'] = self.relu(s_x)
#         #     out_dict['s_attn_x'] = self.relu(temp_s_attn_x)

#         return out_dict


@META_ARCHITECTURES.register("SimpleSensitiveROAD")
class SimpleSensitiveROAD(nn.Module):
    
    def __init__(self, cfg, device):
        super(SimpleSensitiveROAD, self).__init__()
        self.input_dim = 0
        self.input_dim += FEATURE_SIZES[cfg['rgb_type']]

        self.hidden_dim = cfg['hidden_dim']
        self.num_layers = cfg['num_layers']
        self.out_dim = cfg['num_classes']

        self.relu = nn.ReLU()
        self.embedding_dim = cfg['embedding_dim']
        
        self.first_layer = nn.Sequential(
            nn.Linear(self.input_dim, self.embedding_dim),
            nn.LayerNorm(self.embedding_dim),
            nn.ReLU(),
        )

        # new design
        self.ds_gru = nn.GRU(self.embedding_dim, self.embedding_dim * 2, self.num_layers, batch_first=True)
        self.dl_gru = nn.GRU(self.embedding_dim, self.embedding_dim * 2, self.num_layers, batch_first=True)
        self.s_gru = nn.GRU(self.embedding_dim, self.hidden_dim, self.num_layers, batch_first=True)
        self.l_gru = nn.GRU(self.embedding_dim, self.hidden_dim, self.num_layers, batch_first=True)

        self.s_f_classification = nn.Sequential(
            nn.Linear(self.hidden_dim, self.out_dim)
        )
        self.l_f_classification = nn.Sequential(
            nn.Linear(self.hidden_dim, self.out_dim)
        )

        self.h0 = torch.zeros(self.num_layers, 1, self.hidden_dim)

    def forward(self, s_rgb_input, l_rgb_input=None, s_target=None, l_target=None):

        s_x = self.first_layer(s_rgb_input)
        l_x = self.first_layer(l_rgb_input)

        B, s_T, _ = s_x.shape
        B, l_T, _ = l_x.shape
        h0 = self.h0.expand(-1, B, -1).to(s_x.device)


        ds, _ = self.ds_gru(s_x)
        dl, _ = self.dl_gru(l_x)
        ds = self.relu(ds)
        dl = self.relu(dl)
        
        ds_w = ds[:, :, :self.embedding_dim]
        ds_b = ds[:, :, self.embedding_dim:]
        dynamic_s_x = ds_w * s_x + ds_b

        dl_w = dl[:, :, :self.embedding_dim]
        dl_b = dl[:, :, self.embedding_dim:]
        dynamic_l_x = dl_w * l_x + dl_b

        ##### ablation for noTAD
        # dynamic_s_ht, _ = self.s_gru(s_x, h0)
        # dynamic_l_ht, _ = self.l_gru(l_x, h0)

        dynamic_s_ht, _ = self.s_gru(dynamic_s_x, h0)
        dynamic_l_ht, _ = self.l_gru(dynamic_l_x, h0)

        dynamic_s_ht = self.relu(dynamic_s_ht)
        dynamic_l_ht = self.relu(dynamic_l_ht)
        
        dynamic_s_logits = self.s_f_classification(dynamic_s_ht)
        dynamic_l_logits = self.l_f_classification(dynamic_l_ht)

        out_dict = {}

        out_dict['dynamic_s_logits'] = dynamic_s_logits
        out_dict['dynamic_l_logits'] = dynamic_l_logits
        out_dict['ds'] = ds
        out_dict['dl'] = dl
        out_dict['dl_feat'] = self.relu(dynamic_l_x)

        return out_dict
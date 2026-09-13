import torch
import torch.nn as nn
from tqdm import tqdm
import time
from utils import thumos_postprocessing
from utils import *
import json
from trainer.eval_builder import EVAL
from utils import thumos_postprocessing, perframe_average_precision
import pickle
import numpy as np
import os
from itertools import groupby
from typing import List, Dict
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from scipy.signal import medfilt
from collections import defaultdict
import torch
import torch.nn.functional as F

def channelwise_minmax(x: torch.Tensor, eps: float = 1e-6):
    """
    Scale each channel to [0, 1]
    """
    min_val = x.min(dim=0, keepdim=True).values
    max_val = x.max(dim=0, keepdim=True).values
    return (x - min_val) / (max_val - min_val + eps)

def _gaussian_1d_kernel(sigma: float, kernel_size: int, device=None, dtype=None):
    """
    Create a 1D Gaussian kernel normalized to sum to 1.
    """
    # Centered coordinates: e.g., for ks=7 -> [-3, -2, -1, 0, 1, 2, 3]
    radius = (kernel_size - 1) // 2
    x = torch.arange(-radius, radius + 1, device=device, dtype=dtype)
    kernel = torch.exp(-(x ** 2) / (2 * sigma ** 2))
    kernel = kernel / kernel.sum()
    return kernel  # shape: (ks,)

def gaussian_blur2d(x: torch.Tensor,
                    sigma: float = 1.0,
                    kernel_size: int = 15,
                    padding: str = "reflect") -> torch.Tensor:
    """
    Apply Gaussian blur to a 2D matrix or image tensor using separable convs.

    Args:
        x: Tensor of shape (H, W), (1, H, W), or (N, C, H, W).
        sigma: Standard deviation of the Gaussian.
        kernel_size: Odd integer kernel size. If None, uses 2*round(3*sigma)+1.
        padding: 'reflect', 'replicate', or 'constant' (passed to F.pad).

    Returns:
        Blurred tensor with the same shape as input.
    """
    # Ensure kernel size
    if kernel_size is None:
        kernel_size = int(2 * round(3 * sigma) + 1)
    if kernel_size % 2 == 0 or kernel_size < 1:
        raise ValueError("kernel_size must be a positive odd integer.")

    # Normalize input to 4D: (N, C, H, W)
    squeeze_c = False
    squeeze_n = False
    if x.ndim == 2:
        x = x.unsqueeze(0).unsqueeze(0)
        squeeze_n = True
        squeeze_c = True
    elif x.ndim == 3:
        # Assume (C, H, W) or (1, H, W); interpret as (N=1, C, H, W)
        x = x.unsqueeze(0)
        squeeze_n = True
    elif x.ndim != 4:
        raise ValueError("x must have shape (H, W), (C, H, W), or (N, C, H, W).")

    device, dtype = x.device, x.dtype

    # Build 1D Gaussian kernel on correct device/dtype
    g1d = _gaussian_1d_kernel(sigma, kernel_size, device=device, dtype=dtype)

    # Make depthwise (grouped) conv filters for separable convolution
    # First vertical (kh x 1), then horizontal (1 x kw)
    C = x.shape[1]
    kernel_y = g1d.view(1, 1, -1, 1).repeat(C, 1, 1, 1)  # (C,1,kh,1)
    kernel_x = g1d.view(1, 1, 1, -1).repeat(C, 1, 1, 1)  # (C,1,1,kw)

    # Padding amounts for each pass
    pad_y = (0, 0, (kernel_size - 1) // 2, (kernel_size - 1) // 2)  # (left,right,top,bottom)
    pad_x = ((kernel_size - 1) // 2, (kernel_size - 1) // 2, 0, 0)

    # Vertical blur
    y = F.pad(x, pad=pad_y, mode=padding)
    y = F.conv2d(y, kernel_y, groups=C)

    # Horizontal blur
    y = F.pad(y, pad=pad_x, mode=padding)
    y = F.conv2d(y, kernel_x, groups=C)

    # Restore original shape
    if squeeze_n and squeeze_c:
        y = y.squeeze(0).squeeze(0)   # (H, W)
    elif squeeze_n:
        y = y.squeeze(0)              # (C, H, W)

    return y


def plot_temporal_segmentation_all(framewises_s_pred, framewises_s_attn_pred, framewises_l_pred, framewises_l_attn_pred, mul_error_pred, framewise_gt, error_gt,
                                class_map: Dict[int, str] = None,
                                error_class_map: Dict[int, str] = None,
                                title: str = "Temporal Action Segmentation",
                                figsize=(15, 2), save_path=None):
    """
    Plot temporal action segmentation results.
    
    Args:
        gt_labels (List[int]): Ground truth label sequence.
        pred_labels (List[int], optional): Predicted label sequence.
        class_map (Dict[int, str], optional): Mapping from class index to class name.
        title (str): Plot title.
        figsize (tuple): Size of each timeline subplot.
        save_path (str): If provided, saves the plot to this path.
    """

    def compress(labels):
        """Compress consecutive identical labels into (label, start, end) segments."""
        segments = []
        start = 0
        for i in range(1, len(labels)):
            if labels[i] != labels[i - 1]:
                segments.append((labels[start], start, i))
                start = i
        segments.append((labels[start], start, len(labels)))
        return segments

    def plot_row(ax, labels, row_title):
        segments = compress(labels)
        for label, start, end in segments:
            color = cmap(label)
            ax.barh(0, end - start, left=start, color=color, edgecolor='black', height=1.0)
        ax.set_xlim(0, len(labels))
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_ylabel(row_title, rotation=0, labelpad=30, fontsize=12)

    num_rows = 7 # if pred_labels is not None else 1
    fig, axs = plt.subplots(num_rows, 1, figsize=(figsize[0], figsize[1] * num_rows), sharex=True)
    axs = axs if num_rows > 1 else [axs]

    global cmap
    cmap = plt.get_cmap("tab20")  # up to 20 distinct colors

    plot_row(axs[0], framewise_gt, "GT")
    plot_row(axs[1], framewises_s_pred, r'$y^{s-st}$')
    plot_row(axs[2], framewises_s_attn_pred, r'$y^{e-st}$')
    plot_row(axs[3], framewises_l_pred, r'$y^{s-lg}$')
    plot_row(axs[4], framewises_l_attn_pred, r'$y^{e-lg}$')

    # Legend
    unique_labels = set(framewise_gt) | set(framewises_s_pred) | set(framewises_l_pred)
    legend_elements = [Patch(facecolor=cmap(lbl), edgecolor='black', label=class_map.get(lbl, str(lbl)))
                        for lbl in sorted(unique_labels)]
    axs[4].legend(handles=legend_elements, bbox_to_anchor=(1.5, 1), loc='lower right')

    plot_row(axs[5], error_gt, "Err. GT")
    plot_row(axs[6], mul_error_pred, "Err. Pred")

    # Legend
    unique_labels = set(error_gt) | set(mul_error_pred) 
    legend_elements = [Patch(facecolor=cmap(lbl), edgecolor='black', label=error_class_map.get(lbl, str(lbl)))
                        for lbl in sorted(unique_labels)]
    axs[5].legend(handles=legend_elements, bbox_to_anchor=(1.15, 1), loc='lower right')

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.2)
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
        plt.close('all')

def get_labels_start_end_time(frame_wise_labels, bg_class=["background"]):
    labels = []
    starts = []
    ends = []
    last_label = frame_wise_labels[0]
    if frame_wise_labels[0] not in bg_class:
        labels.append(frame_wise_labels[0])
        starts.append(0)
    for i in range(len(frame_wise_labels)):
        if frame_wise_labels[i] != last_label:
            if frame_wise_labels[i] not in bg_class:
                labels.append(frame_wise_labels[i])
                starts.append(i)
            if last_label not in bg_class:
                ends.append(i)
            last_label = frame_wise_labels[i]
    if last_label not in bg_class:
        ends.append(i + 1)
    return labels, starts, ends

def levenstein(p, y, norm=False):
    m_row = len(p)    
    n_col = len(y)
    D = np.zeros([m_row+1, n_col+1], float)
    for i in range(m_row+1):
        D[i, 0] = i
    for i in range(n_col+1):
        D[0, i] = i

    for j in range(1, n_col+1):
        for i in range(1, m_row+1):
            if y[j-1] == p[i-1]:
                D[i, j] = D[i-1, j-1]
            else:
                D[i, j] = min(D[i-1, j] + 1,
                              D[i, j-1] + 1,
                              D[i-1, j-1] + 1)
    
    if norm:
        score = (1 - D[-1, -1]/max(m_row, n_col)) * 100
    else:
        score = D[-1, -1]

    return score


def edit_score(recognized, ground_truth, norm=True, bg_class=["background"]):
    # modified edit_score to remove consecutive duplicates after filtering out background
    recognized_no_bg = [a for a in recognized if not a in bg_class]
    ground_truth_no_bg = [a for a in ground_truth if not a in bg_class]
    P = [k for k, g in groupby(recognized_no_bg)]
    Y = [k for k, g in groupby(ground_truth_no_bg)]
    #P, _, _ = get_labels_start_end_time(recognized, bg_class)
    #Y, _, _ = get_labels_start_end_time(ground_truth, bg_class)
    return levenstein(P, Y, norm)


def f_score(recognized, ground_truth, overlap, bg_class=["background"]):
    p_label, p_start, p_end = get_labels_start_end_time(recognized, bg_class)
    y_label, y_start, y_end = get_labels_start_end_time(ground_truth, bg_class)

    tp = 0
    fp = 0

    hits = np.zeros(len(y_label))

    for j in range(len(p_label)):
        intersection = np.minimum(p_end[j], y_end) - np.maximum(p_start[j], y_start)
        union = np.maximum(p_end[j], y_end) - np.minimum(p_start[j], y_start)
        IoU = (1.0*intersection / union)*([p_label[j] == y_label[x] for x in range(len(y_label))])
        # Get the best scoring segment
        idx = np.array(IoU).argmax()

        if IoU[idx] >= overlap and not hits[idx]:
            tp += 1
            hits[idx] = 1
        else:
            fp += 1

    fn = len(y_label) - sum(hits)

    return float(tp), float(fp), float(fn)

def compute_scores(framewise_preds, framewise_gts):
    overlap = [.1, .25, .5]
    bg_class = [0]
    tp, fp, fn = np.zeros(3), np.zeros(3), np.zeros(3)

    correct = 0
    total = 0
    correct_wo_bg = 0
    total_wo_bg = 0
    edit = 0

    for framewise_pred, framewise_gt in zip(framewise_preds, framewise_gts):
        for i in range(len(framewise_gt)):
            if framewise_gt[i] not in bg_class:
                total_wo_bg += 1
                if framewise_gt[i] == framewise_pred[i]:
                    correct_wo_bg += 1
            
            if framewise_gt[i] == framewise_pred[i]:
                correct += 1
            total += 1

        edit += edit_score(framewise_pred, framewise_gt, bg_class=bg_class)

        for s in range(len(overlap)):
            tp1, fp1, fn1 = f_score(framewise_pred, framewise_gt, overlap[s], bg_class=bg_class)
            tp[s] += tp1
            fp[s] += fp1
            fn[s] += fn1

            
    acc = 100*float(correct)/total
    acc_wo_bg = 100*float(correct_wo_bg)/total_wo_bg
    edit = (1.0*edit)/len(framewise_preds)
    res_list = [acc, acc_wo_bg, edit]

    for s in range(len(overlap)):
        precision = tp[s] / float(tp[s]+fp[s])
        recall = tp[s] / float(tp[s]+fn[s])
    
        f1 = 2.0 * (precision*recall) / (precision+recall)

        f1 = np.nan_to_num(f1)*100
        #print('F1@%0.2f: %.4f' % (overlap[s], f1))
        res_list.append(f1)
    result_metrics = {'Acc': acc,  'Acc-bg': acc_wo_bg, 'Edit': edit, 
                    'F1@10': res_list[-3], 'F1@25': res_list[-2], 'F1@50': res_list[-1]}
    
    return result_metrics


def visualize_all(framewise_s_preds, framewise_s_attn_preds, framewise_l_preds, framewise_l_attn_preds, mul_error_preds, framewise_gts, framewise_error_gts, vids, output_vis_path, idx2action):

    error_idx2action = {
        0: "Normal",
        1: "Error"
    }
    for framewises_s_pred, framewises_s_attn_pred, framewises_l_pred, framewises_l_attn_pred, mul_error_pred, framewise_gt, framewise_error_gt, name in zip(framewise_s_preds, framewise_s_attn_preds, framewise_l_preds, framewise_l_attn_preds, mul_error_preds, framewise_gts, framewise_error_gts, vids):
        plot_temporal_segmentation_all(framewises_s_pred, framewises_s_attn_pred, framewises_l_pred, framewises_l_attn_pred, mul_error_pred, framewise_gt, framewise_error_gt, class_map=idx2action, error_class_map=error_idx2action, save_path=os.path.join(output_vis_path, name+".png"))

def causal_mode_filter(x, window_size=10):
    assert window_size >= 1, "Window size must be at least 1"
    assert isinstance(window_size, int), "Window size must be an integer"
    
    n = len(x)
    filtered = np.zeros_like(x, dtype=int)
    
    for i in range(n):
        start = max(0, i - window_size + 1)
        filtered[i] = np.bincount(x[start:i+1]).argmax()
    
    return filtered

def causal_mean_filter(x, window_size=10):
    """
    Causal mean filter for smoothing continuous values.
    Each output only depends on x[:i+1], so it is online-friendly.

    Args:
        x: 1D array-like of values, probabilities, or scores
        window_size: number of past/current values to average

    Returns:
        filtered: smoothed array
    """
    assert window_size >= 1, "Window size must be at least 1"
    assert isinstance(window_size, int), "Window size must be an integer"

    x = np.asarray(x, dtype=float)
    n = len(x)
    filtered = np.zeros_like(x, dtype=float)

    for i in range(n):
        start = max(0, i - window_size + 1)
        filtered[i] = x[start:i + 1].mean()

    return filtered

def f_score_per(recognized, ground_truth, overlap, bg_class=["background"]):
    p_label, p_start, p_end = get_labels_start_end_time(recognized, bg_class)
    y_label, y_start, y_end = get_labels_start_end_time(ground_truth, bg_class)

    tp = 0
    fp = 0

    hits = np.zeros(len(y_label))

    per_action_stats = defaultdict(lambda: np.array([0, 0, 0]))

    for j in range(len(p_label)):
        intersection = np.minimum(p_end[j], y_end) - np.maximum(p_start[j], y_start)
        union = np.maximum(p_end[j], y_end) - np.minimum(p_start[j], y_start)
        IoU = (1.0*intersection / union)*([p_label[j] == y_label[x] for x in range(len(y_label))])
        # Get the best scoring segment
        idx = np.array(IoU).argmax()

        if IoU[idx] >= overlap and not hits[idx]:
            tp += 1
            hits[idx] = 1
            # per_action_stats[p_label[j]][0] += 1
            per_action_stats[int(p_label[j])][0] += 1
        else:
            fp += 1
            # per_action_stats[p_label[j]][1] += 1
            per_action_stats[int(p_label[j])][1] += 1

    fn = len(y_label) - sum(hits)
    
    for j, h in enumerate(hits):
        if h == 0:
            # per_action_stats[y_label[j]][2] += 1
            per_action_stats[int(y_label[j])][2] += 1

    return float(tp), float(fp), float(fn), per_action_stats

def evaluate_ed(framewise_preds, framewise_gts):

    overlap = [.1, .25, .5]
    tp, fp, fn = np.zeros(3), np.zeros(3), np.zeros(3)

    per_action_tp = np.zeros((3, 2)) # only 0 and 1
    per_action_fp = np.zeros((3, 2)) # only 0 and 1
    per_action_fn = np.zeros((3, 2)) # only 0 and 1

    correct = 0
    total = 0

    for framewise_pred, framewise_gt in zip(framewise_preds, framewise_gts):
        for i in range(len(framewise_gt)):
            if framewise_gt[i] == framewise_pred[i]:
                correct += 1
            total += 1

        for s in range(len(overlap)):
            tp1, fp1, fn1, per_action_stats = f_score_per(framewise_pred, framewise_gt, overlap[s], bg_class=[-100])
            tp[s] += tp1
            fp[s] += fp1
            fn[s] += fn1

            for k, v in per_action_stats.items():
                per_action_tp[s][k] += v[0]
                per_action_fp[s][k] += v[1]
                per_action_fn[s][k] += v[2]
            
    acc = 100*float(correct)/total

    res_list = []

    for s in range(len(overlap)):
        precision = tp[s] / float(tp[s]+fp[s])
        recall = tp[s] / float(tp[s]+fn[s])
        f1 = 2.0 * (precision*recall) / (precision+recall)
        f1 = np.nan_to_num(f1)*100
        res_list.append(f1)

    res_list_normal = []
    res_list_error = []

    for s in range(len(overlap)):
        precision_normal = per_action_tp[s][0] / float(per_action_tp[s][0]+per_action_fp[s][0])
        recall_normal = per_action_tp[s][0] / float(per_action_tp[s][0]+per_action_fn[s][0])

        precision_error = per_action_tp[s][1] / float(per_action_tp[s][0]+per_action_fp[s][1])
        recall_error = per_action_tp[s][1] / float(per_action_tp[s][0]+per_action_fn[s][1])
        
        f1_normal = 2.0 * (precision_normal * recall_normal) / (precision_normal + recall_normal)
        f1_normal = np.nan_to_num(f1_normal)*100
        res_list_normal.append(f1_normal)

        f1_error = 2.0 * (precision_error * recall_error) / (precision_error + recall_error)
        f1_error = np.nan_to_num(f1_error)*100
        res_list_error.append(f1_error)
    
    
    
    result_metrics = {
        'All-Acc': acc, 
        'All-F1@10': res_list[-3], 
        'All-F1@25': res_list[-2], 
        'All-F1@50': res_list[-1],
        'Normal-F1@10': res_list_normal[-3], 
        'Normal-F1@25': res_list_normal[-2], 
        'Normal-F1@50': res_list_normal[-1],
        'Error-F1@10': res_list_error[-3], 
        'Error-F1@25': res_list_error[-2], 
        'Error-F1@50': res_list_error[-1],
        'Avg-F1@10': (res_list_normal[-3] + res_list_error[-3])/2, 
        'Avg-F1@25': (res_list_normal[-2] + res_list_error[-2])/2, 
        'Avg-F1@50': (res_list_normal[-1] + res_list_error[-1])/2,
    }

    return result_metrics

def evaluate_ed_ap(error_preds, preds, opposite=False):
    tp, fp, fn, tn = 0, 0, 0, 0
    count, samples = 0, 0
    for error_pred, pred in zip(error_preds, preds):

        # get matches
        matches = []
        labels, starts, ends = get_labels_start_end_time(pred)
        for label, start, end in zip(labels, starts, ends):
            out = np.array(error_pred[start:end]).sum().item()
            matches.append(False if out > 0 else True)
            # matches.append(False if out > ((end - start) / 2) else True)
        matches = np.array(matches)
        # matches = np.array([g in p for g, p in zip(gt, pred)])

        count += np.sum(matches).item()
        samples += len(matches)
        # the last one is a mistake, a mismatch is expected
        # all the actions all correct procedures except the last one
        if opposite:
            correct = matches[:-1]
            mistake = matches[-1]

            # tn: correct seen as correct
            tn += int(not mistake) #np.sum(correct).item()
            # fp: correct seen as mistake
            fp += int(mistake) #np.sum(~correct).item()
            # tp: mistake seen as mistake
            tp += np.sum(correct).item() #int(not mistake)
            # fn: mistake seen as correct
            fn += np.sum(~correct).item() #int(mistake)
        else:
            correct = matches[:-1]
            mistake = matches[-1]

            # tn: correct seen as correct
            tn += np.sum(correct).item()
            # fp: correct seen as mistake
            fp += np.sum(~correct).item()
            # tp: mistake seen as mistake
            tp += int(not mistake)
            # fn: mistake seen as correct
            fn += int(mistake)

    # * metrics
    # accuracy
    acc = (tp + tn) / (tp + tn + fp + fn)
    if (tp + fp) == 0:
        precision = 0
    else:
        precision = tp / (tp + fp)
    
    if (tp + fn) == 0:
        recall = 0
    else:
        recall = tp / (tp + fn)

    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)
    ratio = count / samples

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "accuracy": acc * 100,
        "precision": precision * 100,
        "recall": recall * 100,
        "f1": f1 * 100,
        "ratio": ratio,
        "count": count,
        "samples": samples,
    }

def plot_heatmap(feat_1, pred_1, pred_tad_1, 
                 feat_2, pred_2, pred_tad_2,
                 feat_3, pred_3, pred_tad_3,
                 feat_4, pred_4, pred_tad_4, output_path):
    # Plot heatmap
    fig, axes = plt.subplots(nrows=6, ncols=2, 
        figsize=(14, 8),
        gridspec_kw={'height_ratios': [0.5, 0.5, 2.5, 0.5, 0.5, 2.5]},  # <- make top row shorter than bottom
        constrained_layout=True
    )

    # Top heatmap

    def compress(labels):
        """Compress consecutive identical labels into (label, start, end) segments."""
        segments = []
        start = 0
        for i in range(1, len(labels)):
            if labels[i] != labels[i - 1]:
                segments.append((labels[start], start, i))
                start = i
        segments.append((labels[start], start, len(labels)))
        return segments

    def plot_row(ax, labels, row_title):
        segments = compress(labels)
        for label, start, end in segments:
            color = cmap(label)
            ax.barh(0, end - start, left=start, color=color, edgecolor='black', height=1.0)
        ax.set_xlim(0, len(labels))
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_ylabel(row_title, rotation=0, labelpad=10, fontsize=12)

    global cmap
    cmap = plt.get_cmap("tab20")  # up to 20 distinct colors
    # im1 = axes[0, 0].imshow(feat_1, cmap='hot', origin='lower', aspect='auto')
    plot_row(axes[0, 0], pred_1, r'$a^l_t$')
    plot_row(axes[1, 0], pred_tad_1, r'$\hat{a}^l_t$')
    im1 = axes[2, 0].imshow(feat_1, cmap='hot', origin='lower', aspect='auto')
    fig.colorbar(im1, ax=axes[2, 0], orientation='vertical')

    # im2 = axes[2, 0].imshow(feat_2, cmap='hot', origin='lower', aspect='auto')
    plot_row(axes[3, 0], pred_2, r'$a^l_t$')
    plot_row(axes[4, 0], pred_tad_2, r'$\hat{a}^l_t$')
    im2 = axes[5, 0].imshow(feat_2, cmap='hot', origin='lower', aspect='auto')
    fig.colorbar(im2, ax=axes[5, 0], orientation='vertical')

    # Bottom heatmap
    # im3 = axes[0, 1].imshow(feat_3, cmap='hot', origin='lower', aspect='auto')
    # axes[2].set_title('quesadilla_u1_a5_error_005')
    # axes[2].set_xlabel('Frames')
    # axes[2].set_ylabel('Semantic')
    plot_row(axes[0, 1], pred_3, r'$a^l_t$')
    plot_row(axes[1, 1], pred_tad_3, r'$\hat{a}^l_t$')
    im3 = axes[2, 1].imshow(feat_3, cmap='hot', origin='lower', aspect='auto')
    fig.colorbar(im3, ax=axes[2, 1], orientation='vertical')

    # im4 = axes[2, 1].imshow(feat_4, cmap='hot', origin='lower', aspect='auto')
    # axes[3].set_title('quesadilla_u1_a1_error_013')
    # axes[3].set_xlabel('Frames')
    # axes[3].set_ylabel('Semantic')
    plot_row(axes[3, 1], pred_4, r'$a^l_t$')
    plot_row(axes[4, 1], pred_tad_4, r'$\hat{a}^l_t$')
    im4 = axes[5, 1].imshow(feat_4, cmap='hot', origin='lower', aspect='auto')
    fig.colorbar(im4, ax=axes[5, 1], orientation='vertical')

    # plt.tight_layout()
    plt.savefig(output_path+".pdf", format="pdf")
    plt.savefig(output_path+".png")
    plt.close('all')


@EVAL.register("ESTANet")
class DUBADEvaluate(nn.Module):

    def __init__(self, cfg):
        super(DUBADEvaluate, self).__init__()
        self.cfg = cfg
        self.smooth_winsize = self.cfg["smooth_winsize"]
        self.err_smooth_winsize = self.cfg["smooth_winsize"]
        self.use_smoothing = False if "use_smoothing" not in cfg else cfg["use_smoothing"]
        self.majority_voting_threshold = self.cfg["majority_voting_threshold"]

        print(f"Using causal smoothing: {self.use_smoothing}")
        print(f"Using majority voting with threshold: {self.majority_voting_threshold}")

    def eval_error(self, vids, preds):
        error_preds = []
        error_gts = []

        ## output error
        output = {}
        s_preds, l_preds, s_attn_preds, l_attn_preds = preds

        for vid, s_pred, l_pred, s_attn_pred, l_attn_pred in zip(vids, s_preds, l_preds, s_attn_preds, l_attn_preds):
            # load error
            error_gt = []
            if "EgoPER" in self.cfg["root_path"]: # only get GT error from EgoPER
                with open(os.path.join(self.cfg["root_path"], "framewise_action_error_labels", vid+".txt"), "r") as fp:
                    lines = fp.readlines()
                
                for line in lines:
                    tokens = line.split("|")
                    action_type = tokens[1].strip("\n")
                    if action_type == "Normal":
                        error_gt.append(0)
                    else:
                        error_gt.append(1)

            error_pred = []
            for i in range(len(l_pred)):
                num_error = 0
                ## proposed pairs
                if s_attn_pred[i] != l_attn_pred[i]:
                    num_error += 1
                if s_attn_pred[i] != s_pred[i]:
                    num_error += 1
                if l_attn_pred[i] != l_pred[i]:
                    num_error += 1
                if l_pred[i] != s_pred[i]:
                    num_error += 1
                
                # marjority voting, 
                if num_error >= self.majority_voting_threshold:
                    error_pred.append(1)
                else:
                    error_pred.append(0)
                
            error_pred = causal_mode_filter(np.array(error_pred), window_size=self.err_smooth_winsize).tolist()
            error_preds.append(error_pred)
            error_gts.append(error_gt)

            output[vid] = {}
            output[vid]["pred"] = error_pred
            output[vid]["gt"] = error_gt
        
        return error_preds, error_gts, output

    def eval_tas(self, model, dataloader, logger, result_path, device):
        model.eval()
        output = {}
        with torch.no_grad():
            pred_scores, gt_targets = [], []
            vids = []
            for vid, rgb_input, target in tqdm(
                dataloader, desc="Evaluation:", leave=False
            ): 
                s_rgb_input, l_rgb_input = rgb_input
                s_target, l_target = target
                s_rgb_input, l_rgb_input = s_rgb_input.to(device), l_rgb_input.to(device)
                s_target, l_target = s_target.to(device), l_target.to(device)
                out_dict = model(s_rgb_input, l_rgb_input, vid)
                target_batch = s_target.squeeze().cpu().numpy()
                
                s_pred_logit = out_dict["s_logits"].squeeze().cpu().numpy()
                l_pred_logit = out_dict["l_logits"].squeeze().cpu().numpy()
                
                gt_targets += list(target_batch)
                video_name = vid[0]
                vids.append(video_name)
                
                s_pred = np.argmax(s_pred_logit, axis=1).astype(np.int64)
                l_pred = np.argmax(l_pred_logit, axis=1).astype(np.int64)

                gt = np.argmax(target_batch, axis=1).astype(np.int64)

                
                # causal smoothing
                if self.use_smoothing:
                    s_pred = causal_mode_filter(s_pred, window_size=self.smooth_winsize)
                    l_pred = causal_mode_filter(l_pred, window_size=self.smooth_winsize)
                        

                sample = {
                    "s_pred": s_pred, 
                    "l_pred": l_pred,
                    "gt": gt
                }
                output[video_name] = sample

            framewise_gts = []
            framewise_s_preds, framewise_l_preds = [], []
            for k, v in output.items():
                output[k] = {
                    "s_pred": v["s_pred"].tolist(), 
                    "l_pred": v["l_pred"].tolist(),
                    "gt": v["gt"].tolist()
                }
                framewise_s_preds.append(v["s_pred"].tolist())
                framewise_l_preds.append(v["l_pred"].tolist())
                framewise_gts.append(v["gt"].tolist())
                
            tas_l_results = compute_scores(framewise_l_preds, framewise_gts)
            tas_s_results = compute_scores(framewise_s_preds, framewise_gts)

        name = "smth_" if self.use_smoothing else ""
        with open(os.path.join(result_path,  name + "tas_l_results.json"), "w") as file:
            json.dump(tas_l_results, file, indent=4)
        with open(os.path.join(result_path,  name + "tas_s_results.json"), "w") as file:
            json.dump(tas_s_results, file, indent=4)
        
        return tas_s_results, tas_l_results

    def eval_tas_error(self, model, model2, dataloader, result_path, device, vis=False):
        model.eval()
        model2.eval()
        output = {}
        with torch.no_grad():
            pred_scores, gt_targets = [], []
            vids = []
            for vid, rgb_input, target in tqdm(
                dataloader, desc="Evaluation:", leave=False
            ): 
                s_rgb_input, l_rgb_input = rgb_input
                s_target, l_target = target
                s_rgb_input, l_rgb_input = s_rgb_input.to(device), l_rgb_input.to(device)
                s_target, l_target = s_target.to(device), l_target.to(device)
                out_dict = model(s_rgb_input, l_rgb_input, vid)
                out_dict2 = model2(s_rgb_input, l_rgb_input, vid)
                
                target_batch = s_target.squeeze().cpu().numpy()
                
                #### rgb, attn (proposed method)
                s_pred_logit = out_dict["s_logits"].squeeze().cpu().numpy()
                l_pred_logit = out_dict["l_logits"].squeeze().cpu().numpy()

                s_pred_logit2 = out_dict2["dynamic_s_logits"].squeeze().cpu().numpy()
                l_pred_logit2 = out_dict2["dynamic_l_logits"].squeeze().cpu().numpy()

                
                gt_targets += list(target_batch)
                video_name = vid[0]
                vids.append(video_name)
                
                s_pred = np.argmax(s_pred_logit, axis=1).astype(np.int64)
                l_pred = np.argmax(l_pred_logit, axis=1).astype(np.int64)
                s_pred2 = np.argmax(s_pred_logit2, axis=1).astype(np.int64)
                l_pred2 = np.argmax(l_pred_logit2, axis=1).astype(np.int64)

                gt = np.argmax(target_batch, axis=1).astype(np.int64)
                
                if self.use_smoothing:
                    s_pred = causal_mode_filter(s_pred, window_size=self.smooth_winsize)
                    l_pred = causal_mode_filter(l_pred, window_size=self.smooth_winsize)
                    s_pred2 = causal_mode_filter(s_pred2, window_size=self.smooth_winsize)
                    l_pred2 = causal_mode_filter(l_pred2, window_size=self.smooth_winsize)

                sample = {
                    "s_pred": s_pred, 
                    "l_pred": l_pred,
                    "s_pred2": s_pred2, 
                    "l_pred2": l_pred2,
                    "gt": gt
                }
                output[video_name] = sample

            framewise_gts = []
            framewise_s_preds, framewise_l_preds = [], []
            framewise_s_preds2, framewise_l_preds2 = [], []

            for k, v in output.items():
                framewise_s_preds.append(v["s_pred"].tolist())
                framewise_l_preds.append(v["l_pred"].tolist())
                framewise_s_preds2.append(v["s_pred2"].tolist())
                framewise_l_preds2.append(v["l_pred2"].tolist())
                framewise_gts.append(v["gt"].tolist())

                
            tas_l_results = compute_scores(framewise_l_preds, framewise_gts)
            tas_s_results = compute_scores(framewise_s_preds, framewise_gts)
            tas_l_results2 = compute_scores(framewise_l_preds2, framewise_gts)
            tas_s_results2 = compute_scores(framewise_s_preds2, framewise_gts)
            
            
            mul_error_preds, error_gts, output_error = self.eval_error(vids, (framewise_s_preds, framewise_l_preds, framewise_s_preds2, framewise_l_preds2))

            
            
            if "EPIC-TENT-O" in self.cfg["data_name"] or "ASSEMBLY101-O" in self.cfg["data_name"]:
                # use robust action detector with small number of frames as TAS results
                mul_ed_results = evaluate_ed_ap(mul_error_preds, framewise_s_preds)
                mul_ed_n_results = evaluate_ed_ap(mul_error_preds, framewise_s_preds, opposite=True)
                # print("{Correct-Mistake (Mistake-based):{", f"precision:{mul_ed_results_['precision']:.1f}, recall:{mul_ed_results_['recall']:.1f}, f1:{mul_ed_results_['f1']:.1f}", "}", "}")
                # print("{Correct-Mistake (Correct-based):{", f"precision:{mul_ed_n_results_['precision']:.1f}, recall:{mul_ed_n_results_['recall']:.1f}, f1:{mul_ed_n_results_['f1']:.1f}", "}", "}")
            else:# elif "EgoPER" in self.cfg["data_name"]:
                mul_ed_results = evaluate_ed(mul_error_preds, error_gts)

                ## also report the metrics as assembly-101
                mul_ed_results_ = evaluate_ed_ap(mul_error_preds, framewise_s_preds)
                mul_ed_n_results_ = evaluate_ed_ap(mul_error_preds, framewise_s_preds, opposite=True)


            # visualization only for EgoPER
            if vis:
                # visualization
                if not os.path.exists(os.path.join(result_path, "vis")):
                    os.mkdir(os.path.join(result_path, "vis"))
                if not os.path.exists(os.path.join(result_path, "vis", "tas_ed")):
                    os.mkdir(os.path.join(result_path, "vis", "tas_ed"))
                task = self.cfg["root_path"].split("/")[-1]
                with open("/".join(self.cfg["root_path"].split("/")[:-1])+"/action2idx.json", "r") as fp:
                    action2idx = json.load(fp)[task]
                idx2action = {}
                for k, v in action2idx.items():
                    idx2action[int(v)] = k 

                visualize_all(framewise_s_preds, framewise_s_preds2, framewise_l_preds, framewise_l_preds2, mul_error_preds, framewise_gts, error_gts, vids, os.path.join(result_path, "vis", "tas_ed"), idx2action)


            with open(os.path.join(result_path,  "tas_l_results.json"), "w") as file:
                json.dump(tas_l_results, file, indent=4)
            with open(os.path.join(result_path,  "tas_s_results.json"), "w") as file:
                json.dump(tas_s_results, file, indent=4)
            with open(os.path.join(result_path,  "tas_attn_l_results.json"), "w") as file:
                json.dump(tas_l_results2, file, indent=4)
            with open(os.path.join(result_path,  "tas_attn_s_results.json"), "w") as file:
                json.dump(tas_s_results2, file, indent=4)
            with open(os.path.join(result_path, "framewise_ed_results.json"), "w") as file:
                json.dump(output_error, file, indent=4)
            with open(os.path.join(result_path, "mul_ed_results.json"), "w") as file:
                json.dump(mul_ed_results, file, indent=4)

            if "EPIC-TENT-O" in self.cfg["data_name"] or "ASSEMBLY101-O" in self.cfg["data_name"]:
                with open(os.path.join(result_path,  "mul_ed_n_results.json"), "w") as file:
                    json.dump(mul_ed_n_results, file, indent=4)
        if "EPIC-TENT-O" in self.cfg["data_name"] or "ASSEMBLY101-O" in self.cfg["data_name"]:
            return tas_s_results, tas_l_results, tas_s_results2, tas_l_results2, (mul_ed_results, mul_ed_n_results)
        else:
            return tas_s_results, tas_l_results, tas_s_results2, tas_l_results2, mul_ed_results



    def forward(self, model, dataloader, logger, result_path, device):
        return self.eval_tas(model, dataloader, logger, result_path, device)

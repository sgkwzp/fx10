# ESTANet Online Error Detection Datasets

This repository provides processed frame-level annotations and pre-extracted visual features for online error detection in procedural videos, as used in:

**ESTANet: Efficient Online Error Detection in Procedural Videos via Prediction Inconsistency**, ECCV 2026.

Paper: https://arxiv.org/abs/2606.25317

The release covers three benchmark datasets:

- **EgoPER**
- **EPIC-Tent-O**
- **Assembly101-O**

The data is intended for online error detection and temporal action segmentation experiments, where models observe procedural videos over time and predict whether the ongoing execution is correct or erroneous.

## Dataset Details

### Dataset Description

The dataset package contains per-frame action labels, per-frame error labels where available, and pre-extracted video features. It is designed to support the ESTANet evaluation protocol, which detects procedural errors from prediction inconsistencies among action detectors with different temporal contexts and sensitivity.

### Dataset Sources

- Repository / codebase: ESTANet
- Paper: https://arxiv.org/abs/2606.25317
- arXiv DOI: https://doi.org/10.48550/arXiv.2606.25317

### Dataset Variants

| Dataset | Subsets / Tasks | Feature Type | Target Format |
|---|---:|---|---|
| EgoPER | coffee, oatmeal, pinwheels, quesadilla, tea | `vc_v_features` | `target_perframe/*.npy`, `framewise_action_error_labels/*.txt` |
| EPIC-Tent-O | tent assembly | `rgb_anet_resnet50` | `target_perframe/*.npy` |
| Assembly101-O | assembly procedures | `rgb_anet_resnet50` | `target_perframe/*.npy` |

## Repository Structure

Expected layout:

```text
EgoPER/
  action2idx.json
  idx2action.json
  coffee/
    target_perframe/
    framewise_action_error_labels/
    vc_v_features/
  oatmeal/
    target_perframe/
    framewise_action_error_labels/
    vc_v_features/
  pinwheels/
    target_perframe/
    framewise_action_error_labels/
    vc_v_features/
  quesadilla/
    target_perframe/
    framewise_action_error_labels/
    vc_v_features/
  tea/
    target_perframe/
    framewise_action_error_labels/
    vc_v_features/

PREGO/
  Epic-tent-O/
    target_perframe/
    rgb_anet_resnet50/
  Assembly101-O/
    target_perframe/
    rgb_anet_resnet50/
```

## Data Fields

### Feature Files

Feature files are NumPy arrays saved as `.npy`.

- EgoPER visual features: shape `(T, 256)`, dtype typically `float32`
- EPIC-Tent-O visual features: shape `(T, 2048)`, dtype typically `float32`
- Assembly101-O visual features: shape `(T, 2048)`, dtype typically `float32`

Here, `T` is the number of frames or sampled time steps for a video.

### Action Target Files

Action targets are NumPy arrays saved as:

```text
target_perframe/<video_id>.npy
```

Each target array has shape `(T, C)`, where `C` is the number of action classes for the corresponding dataset/task. The targets are frame-level one-hot action labels.

### Error Label Files

For EgoPER, framewise error labels are stored as text files:

```text
framewise_action_error_labels/<video_id>.txt
```

Each line corresponds to one frame or time step and follows:

```text
<action_label>|<execution_status>
```

where `<execution_status>` is `Normal` for correct execution frames and another status value for error frames.

## Splits

The official train/test splits used by ESTANet are defined in `data_info/video_list.json` in the ESTANet codebase.

| Dataset / Task | Classes | Train Videos | Test Videos |
|---|---:|---:|---:|
| EgoPER-coffee | 16 | 27 | 38 |
| EgoPER-oatmeal | 16 | 26 | 35 |
| EgoPER-pinwheels | 14 | 26 | 45 |
| EgoPER-quesadilla | 9 | 26 | 35 |
| EgoPER-tea | 11 | 26 | 35 |
| EPIC-Tent-O | 12 | 13 | 15 |
| Assembly101-O | 86 | 135 | 182 |

## Citation

If you use this dataset or the ESTANet benchmark setup, please cite:

```bibtex
@inproceedings{lee2026estanet,
  title = {ESTANet: Efficient Online Error Detection in Procedural Videos via Prediction Inconsistency},
  author = {Lee, Shih-Po and Ghoddoosian, Reza and Siddiqui, Faizan and Sachdeva, Enna and Dariush, Behzad},
  booktitle = {European Conference on Computer Vision (ECCV)},
  year = {2026},
  url = {https://arxiv.org/abs/2606.25317},
  doi = {10.48550/arXiv.2606.25317}
}
```

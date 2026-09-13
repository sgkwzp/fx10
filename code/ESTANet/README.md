# ESTANet

Official implementation of **ESTANet: Efficient Online Error Detection in Procedural Videos via Prediction Inconsistency**.

ESTANet is a lightweight framework for online error detection in procedural videos. It trains standard and error-sensitive action detectors, then detects mistakes at inference time by aggregating prediction inconsistencies across detectors and temporal windows.

Paper: [https://arxiv.org/abs/2606.25317](https://arxiv.org/abs/2606.25317)

## Overview

This repository supports experiments on:

- **EgoPER**: coffee, oatmeal, pinwheels, quesadilla, tea
- **EPIC-Tent-O**
- **Assembly101-O**

The code reports temporal action segmentation metrics and online error detection metrics.

## Installation

Create a Python environment and install the required packages:

```bash
conda create -n estanet python=3.8 -y
conda activate estanet

pip install torch torchvision tensorboard numpy scipy scikit-learn matplotlib tqdm pyyaml
```

Install the PyTorch build that matches your CUDA version if the default `pip install torch torchvision` command is not suitable for your machine.

## Data Preparation

Download the processed datasets and model weights from Hugging Face:

[https://huggingface.co/datasets/shihpolee/ESTANet_datasets](https://huggingface.co/datasets/shihpolee/ESTANet_datasets)

Put the processed datasets under `data/`:

```text
data/
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

### Important: Update `root_path`

Each YAML file in `configs/` contains a `root_path` field. For release use, `root_path` should point to the dataset location under `data/`.

For example, update `configs/egoper-tea.yaml` to:

```yaml
root_path: 'data/EgoPER/tea'
```

Other examples:

```yaml
# configs/egoper-coffee.yaml
root_path: 'data/EgoPER/coffee'

# configs/epictento.yaml
root_path: 'data/PREGO/Epic-tent-O'

# configs/assembly101o.yaml
root_path: 'data/PREGO/Assembly101-O'
```

If your datasets are stored elsewhere, update `root_path` accordingly. The paths currently in the YAML files may be local machine paths and should be changed before running training or evaluation.

## Training

Train ESTANet with a config file:

```bash
CUDA_VISIBLE_DEVICES=0 python main.py --config configs/egoper-tea.yaml
```

Available main configs:

```bash
configs/egoper-tea.yaml
configs/egoper-quesadilla.yaml
configs/egoper-pinwheels.yaml
configs/egoper-oatmeal.yaml
configs/egoper-coffee.yaml
configs/epictento.yaml
configs/assembly101o.yaml
```

The provided `train.sh` includes example commands for all supported datasets.

## Evaluation

Evaluate a trained checkpoint by passing the checkpoint directory with `--eval`:

```bash
CUDA_VISIBLE_DEVICES=0 python main.py \
  --config configs/egoper-tea.yaml \
  --eval checkpoint/EgoPER-tea/ESTANet_EgoPER-tea/
```

To save visualizations for EgoPER runs, add `--vis`:

```bash
CUDA_VISIBLE_DEVICES=0 python main.py \
  --config configs/egoper-tea.yaml \
  --eval checkpoint/EgoPER-tea/ESTANet_EgoPER-tea/ \
  --vis
```

The provided `eval.sh` includes example evaluation commands.

## Checkpoints and Outputs

Training outputs are saved under the configured `output_path`, usually:

```text
checkpoint/<dataset_name>/<task>_<dataset_name>/
```

Each run stores logs, TensorBoard files, and checkpoints. During evaluation, the code expects:

```text
ckpts/best_error.pth
ckpts/best_error2.pth
```

inside the checkpoint directory passed to `--eval`.

## Notes

- `target_perframe/*.npy` contains frame-level one-hot action targets.
- Feature files are stored as `.npy`.
- EgoPER uses `vc_v_features`.
- EPIC-Tent-O and Assembly101-O use `rgb_anet_resnet50`.
- EgoPER online error evaluation also requires framewise text error labels.
- Dataset splits and action class lists are defined in `data_info/video_list.json`.

## Citation

If you use this code or dataset setup, please cite:

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

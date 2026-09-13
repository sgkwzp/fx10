# 数据与特征来源核对

本次核对基于工作区中的原始文件、仓库文档和实现。未把本地仓库自述等同于已核验的上游版本。原始目录只读，新增文件均位于本实验目录。

| 项目 | 已核实事实 | 证据 | 尚未核实的部分 |
|---|---|---|---|
| 256 维特征 | 本地 64 个数组均为 T×256 float32；训练 26、验证 3、测试 35；文档列出 VideoClip/TimeSformer 256 维视觉特征 | `code/EgoPER/README.md:33`；`outputs/audit.json` | 对应这批数组的提取脚本、实际 checkpoint、预训练/微调数据、窗口长度及是否使用未来帧 |
| 2048 维特征 | 本地 80 个数组均为 T×2048 float16；与各自逐帧标签长度相同；文档描述 I3D 特征 | `code/EgoPER/README.md:90`；`outputs/audit.json` | 文件级提取记录和实际权重匹配 |
| I3D 提取代码 | 代码使用过去帧缓冲，roll 后写入当前帧，再以固定索引提取；shell 指向 Kinetics400 命名的 I3D 权重 | `code/EgoPER/I3D_extractor/src/feature_extract.py:232`；`code/EgoPER/I3D_extractor/features_tea.sh` | 不能据此推定 256 维特征同样因果，亦未核验现有 2048 维数组确由此版本生成 |
| 原有正常动作原型 | `Action_1` 至 `Action_10` 与文字动作清单按数字 ID 对应；本地 runner 按该清单读取 | `data/Tea/tea_normal_actions.txt`；`code/GTG2Vid/runner.py:263` | 生成流程未找到；不应称为训练视频视觉中心。本次未使用这些原型 |
| 新动作中心和特征库 | 本次从可用训练视频的 Normal 帧计算；包括 BG；11 类、每类 256 个参考特征 | `run.py`；`outputs/bank_manifest.json` | 仅覆盖 Tea 的可用训练视频，不能证明跨任务泛化 |
| 二分类口径 | 本地 GTG2Vid 将 type>0 全部转为 Error，包含 Correction；Normal/BG 为负类 | `code/GTG2Vid/runner.py:682` | 本次事件匹配指标为明确约定的诊断协议，不等同于论文全部官方指标 |
| Addition | loader 将其动作类置为 -1；oracle 没有合法正常动作类时回退到全局距离 | `code/GTG2Vid/datasets/gtg_dataset_loader.py:46` | 不可把 Addition 的标注动作直接作为可部署路由信息 |
| Omission | 本地代码通过步骤集合/任务图另行评估 | `code/GTG2Vid/runner.py:685` | 本轮逐帧错误实验不覆盖遗漏错误 |

`annotation.json` 是片段时间戳标注，`refined_label_v3` 是逐帧精修标注。本轮以精修标注为准。按片段内部时间点对照，两者有 1,942 个错误类型不一致样本：1,852 个 Slip→Correction，90 个 Addition→Normal，涉及 13 个视频。前者不改变二分类标签，后者会改变。90 个二分类差异位于 `tea_u1_a1_error_022` 的 Sprinkle cinnamon 区间。全部差异保存在 `outputs/annotation_version_audit.json`，没有覆盖或合并任何原始标签。

全部已有特征文件与逐帧标签长度精确一致，所有数值有限。JSON 标注末端与对应特征长度/10 一致。抽取的 4 个不同视频中，MP4 时长与特征时长差为 0 或约 -0.033 秒。这支持这些案例时间轴近似对齐，但不能替代每帧提取窗口核验。

训练列表缺失的 16 个 256 维特征全部带 `u2` 文件名字段。当前诊断覆盖减少，因此不称作完整官方训练配置。缺失清单与 80 个视频逐项检查结果在 `outputs/audit.json`。

# ZeProM 与单卡可行性

## 已核实

- 本机为 RTX 2060，6,144 MiB 显存；检查时空闲约 4,923 MiB。PyTorch 2.8.0+cu129 可用 CUDA；没有 transformers/vLLM 安装，也没有目标 VLM 的本地权重。尚未提供租用 4090 的访问入口。
- 本地 ZeProM 全文 `analysis_fulltext_20260809/058.txt` 第 264–267 行记载：4 fps、4×H100（论文所述每卡 96GB）、vLLM 0.19.1。第 512–517 行记载，主模型 Qwen3.5-397B-A17B-GPTQ-Int4 在该节点处理 EgoPER 用时 87.8 分钟；该时间不能直接外推到单卡 4090。
- 主表 Q-L 为 397B 量化模型，Q-M 为 Qwen3.5-35B-A3B。Q-M 的平均 EDA/F1@0.5 为 80.1/34.8，Q-L 为 84.1/41.0。用户提及 +4.4/+2.0 的主结果不能移植到任意小模型。
- 根据 Hugging Face 官方仓库 `model.safetensors.index.json`，397B GPTQ 权重实际总字节数为 235,657,499,488，约 **219.47 GiB**；35B BF16 权重为 71,903,655,008，约 **66.97 GiB**。两者均超过 4090 的 24GB 显存，尚未计入运行缓存。
- 35B 模型实际约 35.95B 参数，理想全 4-bit 权重下界约 16.74 GiB；量化元数据、未量化层、视觉编码与长视频运行缓存会额外占用显存。**35B 量化是可测试候选，不是已确认能按原设置运行。** MoE 的“激活 3B”不代表只需存储 3B 权重。
- 官方 Qwen3.5-9B 记录存在，约 9.65B 参数。可作为小模型工程候选，仍需实测视频上下文内存；它不是 ZeProM 主结果的等价替代。

机器与模型证据：`sources/local_feasibility.json`、`sources/model_metadata.json`、`sources/weight_config_metadata.json`、`sources/smaller_candidate.json`。官方 Qwen 模型卡已保存为 `sources/Qwen35B_model_card.md`。仅下载公开元数据和模型卡，没有下载数十/数百 GB 模型权重。

## 关于置信度的修正

ZeProM 基础输出为分段的二值错误标签。论文第 206–221 行明确指出直接让模型生成置信度不理想，并提出 ZeProM-MC：先做温度 0 的分割，再以温度 0.7 采样 N 次，将片段按中点对应到参考分割，汇总错误投票。因此：

- “18 帧到 6 帧口头置信度仍为 0.9”来自其他任务的研究，不能当成 ZeProM 已被证实的行为。
- 应审计 MC 错误概率、跨采样分割稳定性及证据敏感性，而不只是自报 confidence。
- 额外采样增加实际推理成本，教师伪标签没有人工标注成本，但不是免费计算。
- ZeProM 研究的是完整视频离线分割/错误检测。直接把它当在线分数流来宣称流式风险保证，会改变原评测设置；前缀推理需单列且重新计成本。

## 可立即执行的 4090 测试包

`vlm_inputs/manifest.json` 已列出跨全部 188 个测试视频按时长分位选出的 3 个完整视频及对应提示：93.0 秒、206.6 秒、366.1 秒。4 fps 分别约为 372、827、1,465 帧。实际 processor 采样帧数必须由服务器日志核实。

`benchmark_vlm.py` 使用官方 Qwen 模型卡中的原生 `video_url` + `mm_processor_kwargs.fps` 接口，保存每次原始回复、耗时、token 使用、输出截断/JSON 错误，并可在服务器本机采样整卡显存占用。它执行一次温度 0 参考及默认 5 次温度 0.7 采样。该脚本已通过参数入口与响应解析检查，**未在 VLM 服务上执行**。

运行前，4090 上需要一个已经成功加载的、明确记录版本和量化方式的兼容 vLLM 服务。原模型卡要求启动时设置 `--media-io-kwargs '{"video": {"num_frames": -1}}'`，方可通过请求配置 fps。不能用降低上下文、丢弃帧或输出截断后的成功来宣称原 ZeProM 设置可行。

客户端示例（在实验目录中；MODEL_NAME 替换为服务实际模型名）：

```text
python benchmark_vlm.py --base-url http://127.0.0.1:8000/v1 --model MODEL_NAME --video vlm_inputs/quesadilla_u1_a4_error_018.mp4 --duration-seconds 93 --prompt-file vlm_inputs/quesadilla_profile_prompt.txt --fps 4 1 --mc-samples 5 --measure-local-gpu --run-name short_clip
```

提示为显式标注的 ZeProM-style 吞吐测试版本，不是完整原论文复现。确认吞吐后，仍需对齐原方法提示、输入/输出处理、量化及 MC 汇总规则，才能用于论文比较。当前脚本改变 fps，尚未实现或验证精确 18/6 帧对照；该项未完成。

## 监督检测器缓存

找到 AMNAR 五个任务的 `eval_results.pkl`，合计覆盖 188 个测试视频。已用只允许 NumPy 类型的读取器检查，其字段是 segments、label、score；这里的 score 伴随动作检测结果，尚未核验为连续错误分数，并且没有对应正常验证输出。详见 `sources/supervised_cache_inventory.json`。因此没有把这些字段冒充校准所需错误概率。

本轮风险计算使用明确命名的正常特征最近邻诊断器。完整“一个已发表监督检测器 + 一个 VLM”的实验仍需要：导出语义明确且与训练独立的校准/测试分数，以及获得 VLM 实际运行环境。

# DeepSeek V4.1 Flash 1017 本地部署工具

围绕 DeepSeek V4.1 Flash 1017 的 Q2_K 权重，提供离线文件校验、跨目录分片管理和启动配置，面向单卡环境的部署准备。

项目固定了模型与 llama.cpp 的版本，支持十个权重分片的完整性检查，并通过软链接组织分散存放的文件，避免重复复制权重。

当前已完成配置和工具测试。目标硬件为 RTX PRO 6000 96 GB 显存、180 GB 系统内存；模型加载、推理速度及上下文测试将在后续补充。

## 功能

- 固定模型和引擎版本，整理 Q2_K 十个分片的文件名、大小及 SHA-256。
- 离线检查缺片、大小不符及重复文件歧义，支持完整 SHA-256 校验。
- 支持跨挂载目录建立软链接视图，不需要把几百 GB 权重重新复制一遍，也不会覆盖已有目录。
- 启动命令默认以 dry-run 方式输出；显式运行时限定 localhost，并设置超时与自身进程清理。
- 提供七个使用微小临时文件的单元测试，以及只包含配置的 `offline_config.ipynb`。

## 目标硬件

| 项目 | 目标配置 |
|---|---|
| GPU | RTX PRO 6000，96 GB 显存 |
| 系统内存 | 180 GB |
| 模型 | DeepSeek-V4.1-Flash-1017，Q2_K |
| 权重体积 | 264,515,416,800 字节，约 246.35 GiB |
| 当前默认配置 | CPU、2 线程、2048 tokens 上下文 |

目标硬件的可用性取决于权重放置、KV cache 和运行开销，显存与系统内存不能简单相加作为容量判断。当前默认配置为 CPU 模式，用于检查路径和启动参数；GPU 配置留待实测后补充。

## 使用

需要 Python 3.10+、完整权重，以及下方固定版本的 `llama-server` 二进制。辅助工具只用标准库，不自动下载、安装或编译。按以下顺序检查分片、创建软链接目录并查看启动命令。

```sh
python recipe.py preflight --root /mnt/models/part-1 --root /mnt/models/part-2
python recipe.py view --root /mnt/models/part-1 --root /mnt/models/part-2 --output /mnt/work/deepseek-q2-view
python recipe.py launch --binary /path/to/llama-server --view /mnt/work/deepseek-q2-view
```

最后一行默认仅打印命令。确认二进制来源与运行资源后，加 `--execute --timeout 600` 才会实际启动。需要完整 SHA-256 校验时，给 `preflight` 加 `--sha256`；这会读取全部权重，耗时取决于存储速度。

分片文件名应保持不变。软链接输出目录必须尚不存在，其父目录需要已经存在且可写。`offline_config.ipynb` 只定义配置，不会加载模型。

## 参考项目

模型、GGUF 量化和引擎支持分别来自以下项目。本仓库提供版本清单、文件校验、分片组织与启动配置。

- 原模型：[deepseek-ai/DeepSeek-V4.1-Flash-1017](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017)
- GGUF 量化：[mrfakename/DeepSeek-V4.1-Flash-1017-GGUF](https://huggingface.co/mrfakename/DeepSeek-V4.1-Flash-1017-GGUF)，revision：`2c97dba3934f27a99767a90830e7519cc7b8b2d9`
- 引擎支持：[llama.cpp PR #28696](https://github.com/ggml-org/llama.cpp/pull/28696)，`vcruz305/llama.cpp`，commit：`2076412598e99127ea2554467b2b7530856895d3`

完整分片清单在 `manifests/model.json`，来源记录与许可说明见 `docs/SOURCES.md` 和 `NOTICE.md`。本仓库提供部署工具与文档，权重和引擎二进制需另外准备。

## 测试计划

| 测试项目 | 实测结果 |
|---|---|
| 目标硬件上的加载与首个回复 | 待补充 |
| 峰值 RAM / VRAM | 待补充 |
| 预填充与生成速度 | 待补充 |
| Q2 量化质量 | 待补充 |

初始测试采用 2048 tokens 的文本服务，记录加载结果、资源占用和吞吐，再调整配置。多模态和 1M 上下文留待后续验证。详细测试范围见 [验证记录](docs/VALIDATION.md)。

运行工具测试：

```sh
python -m unittest discover -s tests -v
```

本项目的部署工具、测试与文档采用 [MIT 许可](LICENSE)。上游模型和引擎遵循各自许可。

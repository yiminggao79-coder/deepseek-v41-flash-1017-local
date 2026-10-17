# DeepSeek V4.1 Flash 1017：本地部署准备工程

**实验性工程准备版本，尚未完成真实模型推理验证。不声明已验证的速度、准确率、内存适配或硬件可行性。**

## 本项目的工程贡献

针对确切的 **DeepSeek-V4.1-Flash-1017** 版本，提供可检查、可复现的部署准备：

- 固定模型 revision，记录 Q2_K 全部十个分片的文件名、大小和 SHA-256。
- 离线检查缺片、大小不符、重名歧义，并提供可选完整哈希校验。
- 将多个已有挂载目录汇集为一个新软链接目录，不复制巨量权重，不覆盖现有目录。
- 默认仅打印命令的 CPU 本地服务配置；显式执行时设置时间上限，仅清理自身启动的进程组。
- 标准库单元测试与只包含配置的 notebook。

这些是本项目的部署工具与配置工程成果。模型、量化和推理引擎分别归下面列出的上游项目；本项目不声称原创推理引擎，不占用上游成果，也不分发其源码、二进制或权重。

## 预期硬件目标，不是已验证要求

| 项目 | 计划实验目标 | 状态 |
|---|---|---|
| GPU | 96 GB 显存的 PRO 6000 | 未测试 |
| 系统内存 | 180 GB | 未测试 |
| 权重文件 | 264,515,416,800 字节，尚不含运行开销 | 上游元数据，未下载或加载 |
| 默认配置 | 纯 CPU、2 线程、2048 tokens 上下文 | 只测试了命令构造，未测试推理 |

以上只是预期实验目标，**不是最低配置、购买建议或已跑通配置**。显存和系统内存不能简单相加来证明能装下模型；权重放置、KV cache、运行开销及上下文长度都需实测。默认配置不启用 GPU offload，GPU 部署方案尚待另行开发和验证。

## 参考项目与固定来源

- 原模型：[deepseek-ai/DeepSeek-V4.1-Flash-1017](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017)
- GGUF 量化发布者：[mrfakename/DeepSeek-V4.1-Flash-1017-GGUF](https://huggingface.co/mrfakename/DeepSeek-V4.1-Flash-1017-GGUF)
- GGUF revision：`2c97dba3934f27a99767a90830e7519cc7b8b2d9`，Q2_K 共十片。
- 引擎支持：[llama.cpp PR #28696](https://github.com/ggml-org/llama.cpp/pull/28696)，贡献者 fork 为 `vcruz305/llama.cpp`。
- 固定引擎 commit：`2076412598e99127ea2554467b2b7530856895d3`。

本项目读取了固定版本的参数定义、服务文档与许可证，没有编译或运行引擎，也没有审计完整源码树。任意最新版 llama.cpp 不等于已验证兼容。详见 `NOTICE.md`、`docs/SOURCES.md` 与 `manifests/`。

## 使用

Python 3.10+，无需安装额外包。工具不自动下载、安装或编译。先通过授权来源准备完整权重。

```sh
python recipe.py preflight --root /mnt/models/part-1 --root /mnt/models/part-2
python recipe.py view --root /mnt/models/part-1 --root /mnt/models/part-2 --output /mnt/work/deepseek-q2-view
python recipe.py launch --binary /path/to/llama-server --view /mnt/work/deepseek-q2-view
```

最后一行默认仅打印，不运行。完整 SHA-256 校验加 `--sha256`，会读取全部约 264.5 GB，可能很慢。仅大小一致不代表内容完整。输出软链接目录必须尚不存在，其父目录必须可写且已存在。

`offline_config.ipynb` 只定义配置，不请求网络、不下载、不编译、不调用子进程、不加载模型、不启用 GPU、不执行推理。

未来单独批准真实实验后，才可加 `--execute --timeout 600` 运行已经准备好的可信二进制。默认仅监听 `127.0.0.1`。本版没有请求客户端或服务就绪检查。

## 验证与已知限制

本地七个单元测试只使用微小临时文件测试辅助逻辑，不能代替真实权重或硬件测试。Q2 质量未知；初始服务范围仅文本，多模态未验证。没有测试 1M 上下文，默认仅 2048 tokens。mmap/软链接不会消除硬件限制，CPU 或磁盘换页可能很慢。Linux 内存报告可能显示超过容器限额的宿主机内存。

| 真实模型验证项 | 结果 |
|---|---|
| 目标硬件成功加载 | 待测试，未运行 |
| 峰值 RAM / VRAM | 待测试，未测量 |
| 预填充 / 生成速度 | 待测试，未测量 |
| Q2 质量 / 任务准确率 | 待测试，未评估 |

原创部署工具、测试与文档使用 MIT 许可；上游模型与引擎许可独立适用。不作“首个实现”声明。完整用法见 [English README](README.md)。

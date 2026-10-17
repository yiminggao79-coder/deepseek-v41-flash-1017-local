# DeepSeek V4.1 Flash 1017 local deployment tools

Offline file validation, cross-directory shard management and launch configuration for DeepSeek V4.1 Flash 1017 Q2_K weights, with single-GPU deployment as the target.

The project pins the model and llama.cpp revisions, checks all ten weight shards and organizes files across mounts through symlinks to avoid duplicate weight copies.

Configuration and tool tests are complete. The target hardware is an RTX PRO 6000 with 96 GB VRAM and 180 GB system RAM. Model loading, inference performance and context-length measurements are planned next.

[中文说明](README.zh-CN.md)

## Features

- Fixed model and engine revisions, with filenames, sizes and SHA-256 hashes for all ten Q2_K shards.
- An offline checker for missing shards, size mismatches and ambiguous duplicates, with optional full-file hashing.
- A cross-mount symlink view so the shards can share one directory without copying hundreds of GB or overwriting an existing directory.
- A local launch configuration that prints its command by default. Explicit execution binds to localhost, has a time limit and cleans up its own process group.
- Seven unit tests using small temporary fixtures, plus a configuration-only `offline_config.ipynb`.

## Target hardware

| Component | Target configuration |
|---|---|
| GPU | RTX PRO 6000 with 96 GB VRAM |
| System RAM | 180 GB |
| Model | DeepSeek-V4.1-Flash-1017, Q2_K |
| Weight files | 264,515,416,800 bytes, approximately 246.35 GiB |
| Current default profile | CPU, 2 threads, 2,048-token context |

Capacity depends on weight placement, KV cache and runtime overhead. VRAM and system RAM cannot simply be added to determine whether the model fits. The current default is CPU-only for checking paths and launch parameters; GPU configuration will follow hardware testing.

## Usage

Requirements: Python 3.10+, complete model weights and a separately prepared `llama-server` binary at the revision below. The helpers use only the standard library and do not download, install or compile anything. Check the shards, create a symlink view and inspect the launch command:

```sh
python recipe.py preflight --root /mnt/models/part-1 --root /mnt/models/part-2
python recipe.py view --root /mnt/models/part-1 --root /mnt/models/part-2 --output /mnt/work/deepseek-q2-view
python recipe.py launch --binary /path/to/llama-server --view /mnt/work/deepseek-q2-view
```

The last command prints only. After checking binary provenance and available resources, add `--execute --timeout 600` to start it. For complete SHA-256 verification, add `--sha256` to `preflight`; this reads every weight byte, so its duration depends on storage speed.

Keep the exact shard filenames. The symlink output directory must be new, and its parent must already exist and be writable. `offline_config.ipynb` only defines configuration and does not load the model.

## Reference projects

The model, GGUF quantization and engine support come from the projects below. This repository provides version manifests, file validation, shard organization and launch configuration.

- Original model: [deepseek-ai/DeepSeek-V4.1-Flash-1017](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017)
- GGUF quantization: [mrfakename/DeepSeek-V4.1-Flash-1017-GGUF](https://huggingface.co/mrfakename/DeepSeek-V4.1-Flash-1017-GGUF), revision `2c97dba3934f27a99767a90830e7519cc7b8b2d9`
- Engine support: [llama.cpp PR #28696](https://github.com/ggml-org/llama.cpp/pull/28696), `vcruz305/llama.cpp`, commit `2076412598e99127ea2554467b2b7530856895d3`

The full shard manifest is in `manifests/model.json`. Source records and license notes are in `docs/SOURCES.md` and `NOTICE.md`. This repository contains deployment tools and documentation; weights and engine binaries are prepared separately.

## Test plan

| Measurement | Result |
|---|---|
| Loading and first response on target hardware | Pending |
| Peak RAM / VRAM | Pending |
| Prompt processing and generation speed | Pending |
| Q2 quantization quality | Pending |

Initial tests will use text serving with a 2,048-token context to measure loading, resource use and throughput before adjusting the configuration. Multimodal support and 1M context remain later validation work. See the [validation record](docs/VALIDATION.md) for the current test scope.

Run the tool tests with:

```sh
python -m unittest discover -s tests -v
```

The deployment tools, tests and documentation use the [MIT license](LICENSE). Upstream models and engines retain their own licenses.

# DeepSeek V4.1 Flash 1017: local deployment preparation

**Experimental engineering preparation. Real-model inference has not been validated. No speed, accuracy, memory-fit or hardware-feasibility result is claimed.**

[中文说明](README.zh-CN.md)

## Engineering contributions

This repository provides reproducible local preparation for the exact **DeepSeek-V4.1-Flash-1017** release:

- A fixed model revision and SHA-256 manifest for all ten Q2_K GGUF shards.
- An offline shard checker with exact-size checks, missing-part detection, ambiguous duplicate rejection and optional complete SHA-256 verification.
- A cross-mount symlink view that assembles existing shards into one new directory without copying weight files or overwriting an existing directory.
- A CPU-only, localhost launch configuration that prints its command by default. Explicit execution of an independently prepared binary is time-bounded and cleans up its own process group.
- Standard-library unit tests for file-layout validation and command construction, plus a configuration-only notebook with no model execution.

These contributions are deployment tooling and configuration, not an original inference engine. Model authorship, quantization and engine support belong to the upstream projects credited below. No third-party engine source, binary or model weights are redistributed here.

## Intended hardware, not validated requirements

| Item | Intended experimental target | Validation status |
|---|---|---|
| GPU | PRO 6000 with 96 GB VRAM | Not tested |
| System RAM | 180 GB | Not tested |
| Weight files | 264,515,416,800 bytes (~246.35 GiB), before runtime overhead | Publisher metadata; not downloaded or loaded |
| Default launch profile | CPU-only, 2 threads, 2,048-token context | Command construction tested; inference not tested |

The hardware above is an intended target, **not a minimum specification, recommendation, or proven fit**. GPU VRAM and system RAM cannot simply be added to establish usable capacity. Weight placement, KV cache, runtime allocation, context size and other overhead need real measurement. The default profile does not enable GPU offload; a GPU deployment profile remains to be developed and tested separately.

## Pinned inputs and reference projects

| Component | Pin / credit |
|---|---|
| Original model | [deepseek-ai/DeepSeek-V4.1-Flash-1017](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017) |
| GGUF conversion/quantization | [mrfakename/DeepSeek-V4.1-Flash-1017-GGUF](https://huggingface.co/mrfakename/DeepSeek-V4.1-Flash-1017-GGUF) |
| GGUF revision | `2c97dba3934f27a99767a90830e7519cc7b8b2d9` |
| Quantization | Q2_K, ten shards, 264,515,416,800 bytes |
| Engine support | [llama.cpp PR #28696](https://github.com/ggml-org/llama.cpp/pull/28696), open when inspected on 2026-10-17 |
| Engine fork | [vcruz305/llama.cpp](https://github.com/vcruz305/llama.cpp/tree/2076412598e99127ea2554467b2b7530856895d3) |
| Engine commit | `2076412598e99127ea2554467b2b7530856895d3` |

See [model manifest](manifests/model.json), [source evidence](docs/SOURCES.md) and [upstream notices](NOTICE.md). Launcher flags were checked against pinned source; this project has not compiled the engine or validated its model loading. Do not substitute an arbitrary latest llama.cpp build and assume compatibility. Binary provenance must be checked independently.

## Offline preparation

Python 3.10+; no pip packages required. Obtain the exact model files through an authorized source before using these helpers. The tools do not download, install or build anything.

```sh
python recipe.py preflight --root /mnt/models/part-1 --root /mnt/models/part-2
# Optional: reads every weight byte, potentially very slow.
python recipe.py preflight --root /mnt/models/part-1 --root /mnt/models/part-2 --sha256
# Requires all ten size checks to pass; output must not already exist.
python recipe.py view --root /mnt/models/part-1 --root /mnt/models/part-2 --output /mnt/work/deepseek-q2-view
# Prints only. Does not execute a binary or load a model.
python recipe.py launch --binary /path/to/llama-server --view /mnt/work/deepseek-q2-view
```

`preflight` and `view` exit 2 for missing, ambiguous or mismatched shards. Size checks alone do not establish integrity. Preserve the exact shard basenames. A view creates only symlinks in a new directory under an existing writable parent; it never changes input files. Symlinks do not bypass disk or memory limits.

For a separately authorized future experiment, append `--execute --timeout 600` to launch an existing trusted binary. Defaults are `--gpu-layers 0 --cpu-moe --ctx-size 2048 --threads 2 --host 127.0.0.1 --port 8080 --jinja`. Execution blocks until exit or timeout; a second terminal can query the server during that window. Server startup does not establish readiness. This release does not include a request client or readiness check.

`offline_config.ipynb` contains only configuration. Its code cells perform no network requests, downloads, builds, subprocess calls, model loading or inference, and do not enable GPU acceleration.

## Limits and test status

- Seven local unit tests cover tiny temporary fixtures and command construction. They do not test actual model weights, engine compatibility or the intended hardware.
- Q2 quantization quality is unknown here. Initial serving scope is text only; multimodal support is unverified.
- The GGUF advertises a 1,048,576-token context. This project has not tested 1M context; the default configuration is 2,048 tokens.
- mmap does not eliminate memory pressure. Disk-backed paging or CPU execution may be unusably slow. No performance claim is made.
- `/proc/meminfo` can show host memory beyond container limits; resource output is informational, not a fit decision.
- No model was downloaded or run during preparation. The full engine source tree was not audited.

| Real-model measurement | Result |
|---|---|
| Load success on target hardware | Pending; not run |
| Peak RAM / VRAM | Pending; not measured |
| Prompt processing / generation speed | Pending; not measured |
| Q2 quality / task accuracy | Pending; not evaluated |

See [validation record](docs/VALIDATION.md). Publication does not imply inference validation.

## Tests and license

```sh
python -m unittest discover -s tests -v
```

Original deployment tooling, tests and documentation are [MIT-licensed](LICENSE). Upstream model and engine licenses apply independently. No claim of being the first implementation is made.

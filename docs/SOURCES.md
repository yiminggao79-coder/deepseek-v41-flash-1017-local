# Source records

Checked 2026-10-17 UTC.

## Model manifest

The Hugging Face model API with `?blobs=true` returned revision `2c97dba3934f27a99767a90830e7519cc7b8b2d9` and the filenames, LFS SHA-256 hashes and sizes of all ten Q2_K shards. The sizes sum to 264,515,416,800 bytes. `manifests/model.json` records this publisher metadata; local weight hashing is a separate preflight step.

## Engine revision

GitHub PR #28696 was open, with head repository `vcruz305/llama.cpp`, head SHA `2076412598e99127ea2554467b2b7530856895d3` and title “model : add DeepSeek V4.1 (DeepseekV41ForCausalLM)”. A separate commit API request reached the rate limit; the pinned raw file requests succeeded.

The inspected files were `common/arg.cpp`, `tools/server/README.md` and `LICENSE`. Their complete-file byte counts and SHA-256 fingerprints are in `manifests/upstream.json`.

The pinned `common/arg.cpp` defines the launcher's `--model`, `--ctx-size`, `--threads`, `--gpu-layers`, `--cpu-moe`, `--host`, `--port` and `--jinja` flags. Runtime model compatibility and memory use are covered by the planned deployment tests.

## Scope

These records cover metadata and selected source files. Preparation involved no model-weight download, upstream code execution, external model API request or benchmark. The full engine source tree was not cloned or reviewed.

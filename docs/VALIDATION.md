# Validation record

Updated 2026-10-17 UTC. Configuration and tool checks are complete. Model loading and performance measurements are pending.

## Completed tool checks

| Check | Result |
|---|---|
| `python -m unittest discover -s tests -v` | Seven tests passed |
| `python -m py_compile recipe.py tests/test_recipe.py` | Passed |
| Notebook JSON and Python-cell syntax | Parsed and compiled successfully |
| Notebook execution state | All execution counts null; outputs empty |
| Launch dry run | Printed a CPU-only localhost command without executing a binary |

The unit tests use small temporary files and cover missing and cross-mount shards, size/hash mismatches, ambiguous duplicates, symlink-only view creation, refusal to overwrite an existing directory, empty-view rejection, command construction and manifest totals.

The notebook syntax check compiled its cell text locally. The notebook was not run against a model. Pinned engine argument definitions, server documentation and license were read; the source evidence is recorded in `SOURCES.md`.

## Next: real-model measurements

The hardware target is an RTX PRO 6000 with 96 GB VRAM and 180 GB system RAM. The current launch configuration is CPU-only; hardware capacity and GPU settings remain part of the planned tests.

| Test | Result |
|---|---|
| Full weight hashing and loading | Pending |
| Pinned engine build and runtime compatibility | Pending |
| First response on target hardware | Pending |
| Peak RAM / VRAM | Pending |
| Prompt processing and generation speed | Pending |
| Q2 quantization quality | Pending |
| Multimodal serving | Pending |
| 1M-token context | Pending |

The completed checks used local fixtures, configuration and selected upstream source files. Model downloads, engine execution and full source-tree review are outside this completed test scope.

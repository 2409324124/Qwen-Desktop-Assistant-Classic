# Training and evaluation

Current research entry: [SFT research guide](../docs/research.md). The Python package is `latex_sft`; new commands default to reviewed v5.2. Legacy `python -m training.*` commands remain compatible and retain their historical defaults.

- [Architecture and provenance migration](../docs/architecture.md)
- [v5 grouping/review protocol](DATA_V5.md) and [historical v4 audit](DATA_V4.md)
- [Reviewed v5.2 results](../reports/v5.2-colab-sft-20261023/README.md): base 33/56, cp30/cp60 48/56; select cp30. Final test remains unused for inference.
- [All experiment reports](../reports/README.md)
- [Historical training instructions](../docs/history/training-pre-refactor.md)

No training, GPU inference, smoke run or model conversion is part of the architecture migration. Frozen exports and reviews remain at their existing paths.

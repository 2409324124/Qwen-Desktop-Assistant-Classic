# v5.2 checkpoint-30 BF16 / GGUF 发布

截至本次 Git 提交：转换与验证完成，HF 上传进行中；尚未声称远端替换成功。

- BF16：4,022,468,096 参数，两份 safetensors，总计 8,044,982,000 bytes。
- GGUF：`qwen3-4b-latex-correction-v5.2-q4_k_m.gguf`，2,497,278,784 bytes。
- 398 个 tensor 已核对：252 个 LoRA 目标匹配基座加 checkpoint-30，146 个未修改 tensor 保持一致。
- GGUF 在 llama.cpp CPU 加载、分词和单 token 生成通过；没有新增量化准确率评测，也未启动训练、Colab 或 GPU 服务。
- 两个 HF 老仓库均已保留 `v3-archive-20261023` 标签；正在替换 main。原始 adapter 私有存档保留。

## 位置与接续

- 远端产物：`home-ms03:/mnt/RC10/qwen-latex/releases/v52-20261023`。
- 发布工作记录：`/srv/storage/projects/colab/v52-release-20261023`；完成后补充 `release-receipt.json`。
- [BF16 目标仓库](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v3-bf16)
- [GGUF 目标仓库](https://huggingface.co/xu2409324124/qwen3-4b-latex-correction-v3-gguf-q4-k-m)
- [实际执行命令](commands.md)，使用远端已有缓存和 CPU 转换；不要重复启动上传。

上传工具遇到可重试网络错误后自动降低并发，已确认存在真实传输。完成标志是 HF 返回提交号并核对远端文件，而非本地转换完成。

# Resume HF release

Both models have been built and validated. HF upload is still active; do not launch duplicate uploads. No GPU is used. The old release remains recoverable at `v3-archive-20261023` in both repos.

```bash
ssh home-ms03 'ps -p 1448193,1448263 -o pid,etime,state,args; tail -c 2000 /mnt/RC10/qwen-latex/releases/v52-20261023/upload-bf16.log; tail -c 2000 /mnt/RC10/qwen-latex/releases/v52-20261023/upload-gguf.log'
```

If both upload processes complete successfully, their logs contain the new immutable commits. In `/mnt/RC10/qwen-latex/releases/v52-20261023`, with PATH prepended by `/mnt/RC10/qwen-latex/miniforge3/envs/latex-sft/bin`:

1. Confirm current HF main commits differ from `release-status.json` previous commits and files correspond to v5.2.
2. Create `v5.2-checkpoint-30` tag in each repository at its new immutable commit (check existing tags before retrying).
3. Run `python verify_release.py`; it checks archive tags, new tags, remote sizes and LFS content digests without downloading weights. It writes `release-receipt.json`.
4. Copy the receipt and successful upload logs to `/srv/storage/projects/colab/v52-release-20261023/`, update repo publication docs from pending to verified.

Xet transfer logs under `~/.cache/huggingface/xet/logs/` showed genuine network transfer and automatic retries; do not print full logs because signed URLs may appear. PID-specific logs: `*1448193.log` and `*1448263.log`.

#!/usr/bin/env bash
set -euo pipefail
cd /mnt/RC10/qwen-latex/evals/v52-math-20261023
export PATH=/mnt/PM983/vllm/.venv/bin:$PATH
export PYTHONPATH="$PWD/tasks:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
base=/home/miku/.cache/huggingface/hub/models--Qwen--Qwen3-4B-Instruct-2507/snapshots/cdbee75f17c01a7cc42f958dc650907174af0554
adapter=/mnt/RC10/qwen-latex/model-archives/v52-checkpoint30/runs/v52-20261023T073851Z-d239b61a/sft/checkpoint-30
for task in gsm8k_cot_zeroshot math500_v52 aime25; do
  for model in base checkpoint-30; do
    args="pretrained=$base,dtype=bfloat16,gpu_memory_utilization=0.85,tensor_parallel_size=1,max_model_len=8192,max_num_seqs=64,seed=42"
    if [[ $model == checkpoint-30 ]]; then args+=",lora_local_path=$adapter,max_lora_rank=64"; fi
    date -Is
    echo "START $task $model"
    lm_eval run --model vllm --model_args "$args" --tasks "$task" --include_path "$PWD/tasks" --limit 200 --num_fewshot 0 --seed 42 --apply_chat_template --batch_size auto --gen_kwargs 'temperature=0,do_sample=False,max_gen_toks=4096' --log_samples --output_path "$PWD/results/$task/$model" 2>&1 | tee "$task-$model.log"
    echo "DONE $task $model"
  done
done

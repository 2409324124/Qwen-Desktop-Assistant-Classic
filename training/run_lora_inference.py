import argparse
import json
from pathlib import Path


SYSTEM_PROMPT = "请将以下含糊、口语化或程序化描述还原为标准的 LaTeX 公式。只输出公式本身。"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run LoRA inference over the fixed eval split.")
    parser.add_argument("--model", default="Qwen/Qwen3-4B-Instruct-2507")
    parser.add_argument("--adapter", default=None, help="Optional LoRA adapter path. Omit for base-model baseline.")
    parser.add_argument("--eval-file", type=Path, default=Path("training/data/latex_formula_eval.jsonl"))
    parser.add_argument("--out", type=Path, default=Path("reports/qwen3-4b-latex-correction-predictions.jsonl"))
    parser.add_argument("--max-new-tokens", type=int, default=256)
    return parser.parse_args()


def main() -> None:
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    args = parse_args()
    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    base = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(base, args.adapter) if args.adapter else base
    model.eval()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.eval_file.open("r", encoding="utf-8") as source, args.out.open("w", encoding="utf-8") as sink:
        for line in source:
            record = json.loads(line)
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": record["input"]},
            ]
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            with torch.no_grad():
                generated = model.generate(
                    **inputs,
                    max_new_tokens=args.max_new_tokens,
                    do_sample=False,
                    temperature=None,
                    top_p=None,
                )
            new_tokens = generated[0][inputs["input_ids"].shape[-1] :]
            prediction = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
            sink.write(
                json.dumps(
                    {
                        "input": record["input"],
                        "expected": record["output"],
                        "prediction": prediction,
                        "metadata": record.get("metadata", {}),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )


if __name__ == "__main__":
    main()

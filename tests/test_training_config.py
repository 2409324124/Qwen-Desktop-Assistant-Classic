import unittest
from pathlib import Path

import yaml

from training.prompts import SYSTEM_PROMPT
from training.run_lora_inference import SYSTEM_PROMPT as INFERENCE_SYSTEM_PROMPT


REPO_ROOT = Path(__file__).resolve().parents[1]


class TrainingConfigurationTests(unittest.TestCase):
    def test_system_prompt_enforces_the_canonical_dialect(self) -> None:
        self.assertEqual(INFERENCE_SYSTEM_PROMPT, SYSTEM_PROMPT)
        self.assertIn(r"\frac{分子}{分母}", SYSTEM_PROMPT)
        self.assertIn(r"\begin{bmatrix}", SYSTEM_PROMPT)
        self.assertIn(r"x_{i}", SYSTEM_PROMPT)
        self.assertIn("只输出公式本身", SYSTEM_PROMPT)
        self.assertIn("角色：", SYSTEM_PROMPT)
        self.assertIn("范例：", SYSTEM_PROMPT)
        self.assertIn("不要使用 display math 包装", SYSTEM_PROMPT)
        self.assertIn("输入：softmax exp xi over sum exp xj", SYSTEM_PROMPT)
        self.assertIn(r"\text{Softmax}(\xi_{i})", SYSTEM_PROMPT)
        self.assertIn("输入：2 by 2 Hessian matrix", SYSTEM_PROMPT)

    def test_full_training_config_targets_the_3090_profile(self) -> None:
        config = yaml.safe_load((REPO_ROOT / "training/qwen3_4b_lora_sft.yaml").read_text(encoding="utf-8"))

        self.assertEqual(config["finetuning_type"], "lora")
        self.assertTrue(config["bf16"])
        self.assertEqual(config["flash_attn"], "fa2")
        self.assertEqual(config["lora_rank"], 64)
        self.assertEqual(config["lora_alpha"], 128)
        self.assertEqual(config["lora_target"], "all")
        self.assertEqual(config["learning_rate"], 1.5e-5)
        self.assertEqual(config["num_train_epochs"], 3.0)
        self.assertEqual(config["per_device_train_batch_size"], 4)
        self.assertEqual(config["gradient_accumulation_steps"], 4)
        self.assertEqual(config["cutoff_len"], 1024)
        self.assertTrue(config["do_eval"])
        self.assertEqual(config["eval_dataset"], "latex_formula_eval_clean")
        self.assertEqual(config["eval_strategy"], "steps")
        self.assertEqual(config["eval_steps"], 100)
        self.assertEqual(config["save_steps"], 100)

    def test_v3_training_config_preserves_v2_and_uses_targeted_output_dir(self) -> None:
        full = yaml.safe_load((REPO_ROOT / "training/qwen3_4b_lora_sft.yaml").read_text(encoding="utf-8"))
        v3 = yaml.safe_load((REPO_ROOT / "training/qwen3_4b_lora_sft_v3.yaml").read_text(encoding="utf-8"))

        self.assertEqual(v3["output_dir"], "saves/qwen3-4b-latex-correction/lora/sft-v3")
        self.assertNotEqual(v3["output_dir"], full["output_dir"])
        for key in (
            "bf16",
            "flash_attn",
            "lora_rank",
            "lora_alpha",
            "lora_target",
            "learning_rate",
            "num_train_epochs",
            "per_device_train_batch_size",
            "gradient_accumulation_steps",
            "cutoff_len",
            "eval_dataset",
        ):
            self.assertEqual(v3[key], full[key], key)

    def test_smoke_config_uses_the_same_adapter_shape(self) -> None:
        full = yaml.safe_load((REPO_ROOT / "training/qwen3_4b_lora_sft.yaml").read_text(encoding="utf-8"))
        smoke = yaml.safe_load((REPO_ROOT / "training/qwen3_4b_lora_smoke.yaml").read_text(encoding="utf-8"))

        for key in (
            "bf16",
            "flash_attn",
            "lora_rank",
            "lora_alpha",
            "lora_target",
            "learning_rate",
            "per_device_train_batch_size",
            "gradient_accumulation_steps",
            "cutoff_len",
        ):
            self.assertEqual(smoke[key], full[key], key)


if __name__ == "__main__":
    unittest.main()

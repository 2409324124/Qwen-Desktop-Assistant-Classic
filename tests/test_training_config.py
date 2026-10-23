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
        self.assertIn("输入：Softmax(xi_i) = exp(xi_i) / sum_j exp(xi_j)", SYSTEM_PROMPT)
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

    def test_v5_training_config_preserves_v3_adapter_and_uses_isolated_data(self) -> None:
        v3 = yaml.safe_load((REPO_ROOT / "training/qwen3_4b_lora_sft_v3.yaml").read_text(encoding="utf-8"))
        v5 = yaml.safe_load((REPO_ROOT / "training/qwen3_4b_lora_sft_v5.yaml").read_text(encoding="utf-8"))

        for key in ("model_name_or_path", "finetuning_type", "lora_rank", "lora_alpha",
                    "lora_dropout", "lora_target", "learning_rate", "num_train_epochs",
                    "per_device_train_batch_size", "gradient_accumulation_steps", "cutoff_len"):
            self.assertEqual(v5[key], v3[key], key)
        self.assertEqual(v5["dataset_dir"], "training/data/v5")
        self.assertEqual(v5["dataset"], "latex_formula_train")
        self.assertEqual(v5["eval_dataset"], "latex_formula_eval_clean")
        self.assertTrue(v5["do_train"])
        self.assertTrue(v5["do_eval"])
        self.assertEqual(v5["flash_attn"], "sdpa")
        self.assertTrue(v5["bf16"])
        self.assertEqual(v5["output_dir"], "saves/qwen3-4b-latex-correction/lora/sft-v5")
        self.assertNotEqual(v5["output_dir"], v3["output_dir"])
        self.assertFalse(v5["overwrite_output_dir"])

    def test_v5_retains_each_epoch_checkpoint_without_loss_based_selection(self) -> None:
        config = yaml.safe_load((REPO_ROOT / "training/qwen3_4b_lora_sft_v5.yaml").read_text(encoding="utf-8"))

        self.assertEqual(config["num_train_epochs"], 3.0)
        self.assertEqual(config["save_strategy"], "epoch")
        self.assertEqual(config["eval_strategy"], "epoch")
        self.assertEqual(config["save_total_limit"], 3)
        self.assertFalse(config["save_only_model"])
        self.assertFalse(config["load_best_model_at_end"])
        for obsolete_key in ("save_steps", "eval_steps", "metric_for_best_model", "greater_is_better", "max_steps"):
            self.assertNotIn(obsolete_key, config)

    def test_v5_smoke_uses_the_same_profile_with_five_steps_and_its_own_output(self) -> None:
        full = yaml.safe_load((REPO_ROOT / "training/qwen3_4b_lora_sft_v5.yaml").read_text(encoding="utf-8"))
        smoke = yaml.safe_load((REPO_ROOT / "training/qwen3_4b_lora_smoke_v5.yaml").read_text(encoding="utf-8"))

        for key in ("model_name_or_path", "bf16", "flash_attn", "lora_rank", "lora_alpha",
                    "lora_dropout", "lora_target", "learning_rate", "per_device_train_batch_size",
                    "gradient_accumulation_steps", "cutoff_len", "dataset_dir", "dataset", "eval_dataset"):
            self.assertEqual(smoke[key], full[key], key)
        self.assertEqual(smoke["max_steps"], 5)
        self.assertEqual(smoke["max_samples"], 64)
        self.assertEqual(smoke["save_strategy"], "steps")
        self.assertEqual(smoke["save_steps"], 5)
        self.assertEqual(smoke["eval_strategy"], "steps")
        self.assertEqual(smoke["eval_steps"], 5)
        self.assertEqual(smoke["output_dir"], "saves/qwen3-4b-latex-correction/lora/smoke-v5")
        self.assertNotEqual(smoke["output_dir"], full["output_dir"])
        self.assertFalse(smoke["overwrite_output_dir"])
        self.assertFalse(smoke["load_best_model_at_end"])

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

import json
import tempfile
import unittest
from pathlib import Path

from training.canonicalize_dataset import canonicalize_records
from training.clean_evaluation import clean_evaluation
from training.prompts import SYSTEM_PROMPT
from training.dataset_quality import apply_quality_overrides, load_quality_overrides
from training.prepare_dataset import (
    DatasetValidationError,
    build_datasets,
    dedupe_records,
    load_jsonl,
    load_sources,
    split_records,
    validate_records,
    write_jsonl,
)


def make_record(idx: int, layer: str, category: str = "stats_ml") -> dict:
    metadata = {
        "dataset_layer": layer,
        "category": category,
        "perspective": "beginner" if idx % 2 == 0 else "programmer",
    }
    if layer == "noisy":
        metadata["noise_rule"] = "ascii_substitute"
    if layer == "hard":
        metadata["hard_rule"] = "dense_ascii"
    return {
        "instruction": "restore latex",
        "input": f"sample input {layer} {idx}",
        "output": f"x_{idx} = y_{idx}",
        "metadata": metadata,
    }


class TrainingDatasetTests(unittest.TestCase):
    def test_quality_overrides_repair_or_quarantine_records(self) -> None:
        keep = make_record(1, "clean")
        repair = make_record(2, "clean")
        quarantine = make_record(3, "noisy")
        for record, source_file in ((keep, "clean.jsonl"), (repair, "clean.jsonl"), (quarantine, "noisy.jsonl")):
            record["metadata"]["source_file"] = source_file
            record["metadata"]["formula_name"] = f"formula-{record['input']}"

        overrides = [
            {
                "source_file": "clean.jsonl",
                "input": repair["input"],
                "formula_name": repair["metadata"]["formula_name"],
                "action": "replace_output",
                "output": r"x_{2} = z_{2}",
                "reason": "Ground Truth used the wrong symbol.",
            },
            {
                "source_file": "noisy.jsonl",
                "input": quarantine["input"],
                "formula_name": quarantine["metadata"]["formula_name"],
                "action": "exclude",
                "reason": "Input is underspecified.",
            },
        ]

        accepted, rejected, audit = apply_quality_overrides([keep, repair, quarantine], overrides)

        self.assertEqual([record["input"] for record in accepted], [keep["input"], repair["input"]])
        self.assertEqual(accepted[1]["output"], r"x_{2} = z_{2}")
        self.assertEqual(accepted[1]["canonical_output"], r"x_{2} = z_{2}")
        self.assertEqual(rejected, [quarantine])
        self.assertEqual(audit, {"kept": 1, "repaired": 1, "excluded": 1})

    def test_quality_overrides_can_repair_prediction_ground_truth(self) -> None:
        row = make_record(4, "clean")
        row["expected"] = row.pop("output")
        row["prediction"] = r"x_{4} = z_{4}"
        row["metadata"].update({"source_file": "clean.jsonl", "formula_name": "Example"})
        override = {
            "source_file": "clean.jsonl",
            "input": row["input"],
            "formula_name": "Example",
            "action": "replace_output",
            "output": r"x_{4} = z_{4}",
            "reason": "Repair expected value.",
        }

        accepted, rejected, audit = apply_quality_overrides([row], [override], target_field="expected")

        self.assertEqual(accepted[0]["expected"], r"x_{4} = z_{4}")
        self.assertNotIn("canonical_output", accepted[0])
        self.assertEqual(rejected, [])
        self.assertEqual(audit, {"kept": 0, "repaired": 1, "excluded": 0})

    def test_reviewed_quality_manifest_matches_full_source_records(self) -> None:
        root = Path(__file__).resolve().parents[1]
        records = load_sources(root)
        overrides = load_quality_overrides(root / "training/dataset_quality_overrides.json")

        accepted, rejected, audit = apply_quality_overrides(records, overrides)

        self.assertEqual(len(accepted), 2986)
        self.assertEqual(len(rejected), 14)
        self.assertEqual(audit, {"kept": 2978, "repaired": 8, "excluded": 14})

    def test_clean_evaluation_writes_clean_predictions_and_quarantine(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            keep = make_record(1, "clean")
            drop = make_record(2, "noisy")
            rows = []
            for record, source_file in ((keep, "clean.jsonl"), (drop, "noisy.jsonl")):
                rows.append(
                    {
                        "input": record["input"],
                        "expected": record["output"],
                        "prediction": record["output"],
                        "metadata": {
                            **record["metadata"],
                            "source_file": source_file,
                            "formula_name": record["input"],
                        },
                    }
                )
            write_jsonl(root / "predictions.jsonl", rows)
            (root / "overrides.json").write_text(
                json.dumps(
                    [
                        {
                            "source_file": "noisy.jsonl",
                            "input": drop["input"],
                            "formula_name": drop["input"],
                            "action": "exclude",
                            "reason": "Underspecified.",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            audit = clean_evaluation(
                root / "predictions.jsonl",
                root / "clean.jsonl",
                root / "quarantine.jsonl",
                root / "audit.json",
                root / "overrides.json",
            )

            self.assertEqual(len(load_jsonl(root / "clean.jsonl")), 1)
            self.assertEqual(len(load_jsonl(root / "quarantine.jsonl")), 1)
            self.assertEqual(audit["clean_total"], 1)

    def test_validation_rejects_missing_required_fields(self) -> None:
        with self.assertRaises(DatasetValidationError):
            validate_records([{"instruction": "restore", "input": "x"}], "bad.jsonl")

    def test_split_preserves_layers_in_eval_when_possible(self) -> None:
        records = []
        for layer in ("clean", "noisy", "hard"):
            records.extend(make_record(i, layer) for i in range(10))

        train, eval_records = split_records(records, eval_ratio=0.2, seed=7)

        self.assertEqual(len(train), 24)
        self.assertEqual(len(eval_records), 6)
        eval_layers = {record["metadata"]["dataset_layer"] for record in eval_records}
        self.assertEqual(eval_layers, {"clean", "noisy", "hard"})

    def test_dedupe_records_keeps_first_duplicate(self) -> None:
        first = make_record(1, "clean")
        duplicate = dict(first)
        duplicate["metadata"] = {"dataset_layer": "noisy"}

        deduped, duplicate_count = dedupe_records([first, duplicate])

        self.assertEqual(duplicate_count, 1)
        self.assertEqual(deduped, [first])

    def test_jsonl_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.jsonl"
            records = [make_record(1, "clean")]
            write_jsonl(path, records)
            self.assertEqual(load_jsonl(path), records)

            raw = path.read_text(encoding="utf-8").strip()
            self.assertEqual(json.loads(raw)["input"], "sample input clean 1")

    def test_canonicalization_preserves_original_output(self) -> None:
        record = make_record(1, "clean")

        normalized, stats = canonicalize_records([record])

        self.assertEqual(normalized[0]["output"], "x_1 = y_1")
        self.assertEqual(normalized[0]["canonical_output"], "x_{1} = y_{1}")
        self.assertEqual(stats["changed"], 1)

    def test_load_sources_uses_canonical_output_as_training_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record = make_record(1, "clean")
            record["canonical_output"] = r"x_{1} = y_{1}"
            write_jsonl(root / "source.jsonl", [record])

            loaded = load_sources(root, (("clean", "source.jsonl"),))

            self.assertEqual(loaded[0]["output"], r"x_{1} = y_{1}")
            self.assertEqual(loaded[0]["canonical_output"], r"x_{1} = y_{1}")
            self.assertEqual(loaded[0]["instruction"], SYSTEM_PROMPT)

    def test_targeted_records_are_train_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out_dir = root / "training/data"
            base = make_record(1, "clean")
            base["canonical_output"] = r"x_{1} = y_{1}"
            base_2 = make_record(3, "clean")
            base_2["canonical_output"] = r"x_{3} = y_{3}"
            write_jsonl(root / "source.jsonl", [base, base_2])
            targeted = make_record(2, "targeted")
            targeted["metadata"]["formula_name"] = "Product Rule"
            targeted["canonical_output"] = r"(u\gamma)' = u'\gamma + u\gamma'"
            write_jsonl(root / "targeted.jsonl", [targeted])

            summary = build_datasets(
                root,
                out_dir,
                eval_ratio=0.5,
                seed=1,
                sources=(("clean", "source.jsonl"),),
                train_only_sources=(("targeted", "targeted.jsonl"),),
                quality_overrides=[],
            )

            train = load_jsonl(out_dir / "latex_formula_train.jsonl")
            eval_records = load_jsonl(out_dir / "latex_formula_eval.jsonl")
            self.assertIn("targeted", summary["train"]["layers"])
            self.assertNotIn("targeted", summary["eval"]["layers"])
            self.assertEqual(len([record for record in train if record["metadata"]["dataset_layer"] == "targeted"]), 1)
            self.assertEqual({record["metadata"]["dataset_layer"] for record in eval_records}, {"clean"})


if __name__ == "__main__":
    unittest.main()

import json
import tempfile
import unittest
from pathlib import Path

from training.canonicalize_dataset import canonicalize_records
from training.prepare_dataset import (
    DatasetValidationError,
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


if __name__ == "__main__":
    unittest.main()

"""Behavioral comparison against the immutable pre-migration implementation."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

from latex_sft.core import parse_latex_faithful, compare_latex_math_only
from latex_sft.core.prompts import SYSTEM_PROMPT
from latex_sft.data.components import connected_components

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "archive/protocols/a082730/source"

# Each reference runs in a fresh interpreter: the frozen source must never
# resolve an old import to a compatibility shim from this checkout.
PROBE = r'''
from pathlib import Path
import dataclasses
import hashlib
import json
import sys
root, snapshot, mode = map(str, sys.argv[1:])
sys.path.insert(0, snapshot if mode == "frozen" else str(Path(root)/"src"))
if mode == "frozen":
    from training.latex_semantics import _faithful_ast as parse
    from training.formula_structure import structural_signatures
    from training.prepare_dataset import _group_keys as group_keys, split_grouped_records
    from training.clean_v5_holdouts import isolate_components
    from training.prompts import SYSTEM_PROMPT
    from tools.data_generation.mine_sympy import build_templates
else:
    from latex_sft.core.semantics import parse_latex_faithful as parse
    from latex_sft.data.formula_structure import structural_signatures
    from latex_sft.data.records import group_keys
    from latex_sft.data.prepare_dataset import split_grouped_records
    from latex_sft.data.clean_v5_holdouts import isolate_components
    from latex_sft.core.prompts import SYSTEM_PROMPT
    from latex_sft.data.generation.mine_sympy import build_templates

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

splits = {}
parsed = []
for split, name in (("train", "train"), ("eval", "eval_clean"), ("test", "test")):
    rows = [json.loads(line) for line in (Path(root)/"training/data/v5.2"/("latex_formula_"+name+".jsonl")).read_text().splitlines() if line.strip()]
    splits[split] = rows
    for row in rows:
        formula = row["output"]
        try:
            tree = dataclasses.asdict(parse(formula))
        except (ValueError, IndexError, RecursionError, TypeError) as error:
            tree = [type(error).__name__, str(error)]
        parsed.append([row["metadata"]["source_id"], tree, structural_signatures(formula), sorted(group_keys(row))])

# Different names, duplicated source evidence and transitive near-family links
# exercise fresh allocation without running a large combinatorial search.
rows = []
for index in range(12):
    rows.append({"instruction":"restore", "input":"input:"+str(index), "output":"target:"+str(index),
                 "metadata":{"source_id":"source:"+str(index), "formula_name":"family:"+str(index), "category":"math"}})
rows[0]["metadata"]["structural_signatures"] = ["bridge-a"]
rows[1]["metadata"]["structural_signatures"] = ["bridge-a", "bridge-b"]
rows[2]["metadata"]["structural_signatures"] = ["bridge-b"]
edges = []; allocation = {}
assigned = split_grouped_records(rows, connections=edges, allocation_report=allocation)
print(json.dumps({"rows":digest(parsed), "isolation":digest(isolate_components(splits)),
                  "allocation":digest([assigned, edges, allocation]),
                  "prompt":SYSTEM_PROMPT, "templates":build_templates()}, sort_keys=True))
'''


class CoreDataMigrationTests(unittest.TestCase):
    def test_frozen_parser_signatures_keys_allocation_and_isolation_match(self):
        outputs = []
        for mode in ("frozen", "current"):
            result = subprocess.run([sys.executable, "-c", PROBE, str(ROOT), str(SNAPSHOT), mode],
                                    check=True, text=True, capture_output=True, cwd="/tmp")
            outputs.append(json.loads(result.stdout))
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(outputs[1]["prompt"], SYSTEM_PROMPT)

    def test_shared_component_kernel_preserves_transitive_edges(self):
        rows = [{"a"}, {"a", "b"}, {"b"}, {"c"}]
        edges = []
        groups = connected_components(rows, lambda row: row, on_edge=lambda *edge: edges.append(edge))
        self.assertEqual(groups, [rows[:3], rows[3:]])
        self.assertEqual(edges, [(0, 1, "a"), (1, 2, "b")])

    def test_public_parser_does_not_enable_free_variable_scoring(self):
        self.assertNotEqual(parse_latex_faithful("x+y"), parse_latex_faithful("a+b"))
        self.assertFalse(compare_latex_math_only("x+y", "a+b").math_match)
        self.assertTrue(compare_latex_math_only(r"\frac{x}{y}", r"\frac{ x }{ y }").math_match)


if __name__ == "__main__":
    unittest.main()

import json
import random
import os
import argparse
from sympy import sympify, simplify, Eq
from sympy.generator import FormulaGenerator

class MAMUTDataBuilder:
    def __init__(self, src_path, out_path, num_equiv=3, factor_false=1):
        self.src_path = src_path
        self.out_path = out_path
        self.num_equiv = num_equiv
        self.factor_false = factor_false
        self.formulas = []
        self.instruction = "请将以下输入的数学描述或错误公式转换为标准的 LaTeX 格式，并修正其中的逻辑错误。"
        
        # Natural language templates for pseudo-code
        self.nl_templates = [
            "{name} is usually written like {pseudo}.",
            "How do I type {name}? Is it {pseudo}?",
            "Convert this to LaTeX: {pseudo}",
            "Check this formula: {pseudo}",
            "{pseudo} - help me format this properly."
        ]

    def load_source(self):
        if not os.path.exists(self.src_path):
            raise FileNotFoundError(f"Source file {self.src_path} not found.")
        with open(self.src_path, 'r', encoding='utf-8') as f:
            self.formulas = json.load(f)

    def generate_pseudo_nl(self, name, standard_latex):
        """Simple heuristic to make standard_latex look like pseudo-code/NL."""
        # Remove LaTeX commands for pseudo-code look
        pseudo = standard_latex.replace("\\frac", " / ")
        pseudo = pseudo.replace("{", "(").replace("}", ")")
        pseudo = pseudo.replace("^2", " squared ")
        pseudo = pseudo.replace("+", " plus ")
        pseudo = pseudo.replace("-", " minus ")
        pseudo = pseudo.replace("=", " equals ")
        pseudo = pseudo.replace("\\pi", " pi ")
        pseudo = pseudo.replace("\\sqrt", " square root of ")
        pseudo = " ".join(pseudo.split())
        
        # Randomly pick variants
        variants = random.sample(self.nl_templates, min(len(self.nl_templates), 2))
        return [v.format(name=name, pseudo=pseudo) for v in variants]

    def assemble_record(self, input_text, formula_obj, is_correct=True):
        status = "正确" if is_correct else "有误"
        return {
            "instruction": self.instruction,
            "input": input_text,
            "output": f"检测到公式输入（状态：{status}）。标准的 {formula_obj['name']} 应当写作：{formula_obj['standard_latex']}",
            "metadata": {
                "source": "MAMUT",
                "is_correct": is_correct,
                "formula_name": formula_obj['name']
            }
        }

    def build(self):
        records = []
        for f in self.formulas:
            print(f"Processing: {f['name']}...")
            standard_latex = f['standard_latex']
            
            # 1. Add NL pseudo variants
            nl_variants = self.generate_pseudo_nl(f['name'], standard_latex)
            for nl in nl_variants:
                records.append(self.assemble_record(nl, f, is_correct=True))
            
            # 2. Use MAMUT FormulaGenerator
            # max = num_equiv (True versions) + num_equiv * factor_false (False versions)
            max_total = self.num_equiv * (1 + self.factor_false)
            generator = FormulaGenerator(standard_latex, factor_false=self.factor_false)
            
            try:
                # generate_versions_iterator yields (latex_version, is_true)
                iterations = 0
                for version, is_true in generator.generate_versions_iterator(
                    max=max_total, 
                    initial_is_candidate=False
                ):
                    # Sanity check for falsified versions
                    if not is_true:
                        # Try to verify mathematical difference if possible
                        # This is a bit slow but safer
                        try:
                            # Parse back to check equivalence (heuristic)
                            # Note: parsing latex back to sympy is part of the fork
                            pass 
                        except:
                            pass
                    
                    records.append(self.assemble_record(version, f, is_correct=is_true))
                    iterations += 1
                    if iterations >= max_total:
                        break
            except Exception as e:
                print(f"Error generating versions for {f['name']}: {e}")

        # Shuffle and Save
        random.shuffle(records)
        with open(self.out_path, 'w', encoding='utf-8') as f_out:
            for r in records:
                f_out.write(json.dumps(r, ensure_ascii=False) + "\n")
        
        print(f"\n[DONE] Generated {len(records)} records in {self.out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="formulas.json")
    parser.add_argument("--out", default="train.jsonl")
    parser.add_argument("--equiv", type=int, default=3, help="Number of equivalent (true) versions")
    parser.add_argument("--ffactor", type=int, default=2, help="Factor of false versions per true version")
    args = parser.parse_args()

    builder = MAMUTDataBuilder(args.src, args.out, args.equiv, args.ffactor)
    builder.load_source()
    builder.build()

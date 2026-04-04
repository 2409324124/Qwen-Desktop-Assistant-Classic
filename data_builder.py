import json
import random
import os
import argparse
from sympy import sympify, latex, Eq, Add, Mul, Pow, Integer, Float, Symbol

class FormulaDatasetBuilder:
    def __init__(self, src_path, out_path, num_variants=3):
        self.src_path = src_path
        self.out_path = out_path
        self.num_variants = num_variants
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
        pseudo = standard_latex.replace("\\frac", "divided by")
        pseudo = pseudo.replace("^", " squared " if "2" in pseudo else "^")
        pseudo = pseudo.replace("+", " plus ")
        pseudo = pseudo.replace("-", " minus ")
        pseudo = pseudo.replace("=", " equals ")
        pseudo = pseudo.strip()
        # Randomly pick 3 variants
        variants = random.sample(self.nl_templates, min(len(self.nl_templates), self.num_variants))
        return [v.format(name=name, pseudo=pseudo) for v in variants]

    def mutate_formula(self, sympy_str):
        """
        Adversarial Mutation Rules:
        1. Flip + ↔ -
        2. Delete leading coefficient/number
        3. Change exponent
        """
        try:
            expr = sympify(sympy_str, evaluate=False)
            
            # Simple recursive mutation
            def _mutate_node(node):
                # Rule 1: Flip Add terms
                if isinstance(node, Add):
                    args = list(node.args)
                    idx = random.randint(0, len(args)-1)
                    # Flip sign by multiplying by -1
                    args[idx] = -1 * args[idx]
                    return Add(*args, evaluate=False)
                
                # Rule 2: Delete leading coefficient in Mul
                if isinstance(node, Mul):
                    args = [a for a in node.args if not (isinstance(a, (Integer, Float)))]
                    if args:
                        return Mul(*args, evaluate=False)
                    return node
                
                # Rule 3: Change exponent in Pow
                if isinstance(node, Pow):
                    base, exp = node.args
                    if isinstance(exp, (Integer, Float)):
                        new_exp = exp + random.choice([-1, 1])
                        return Pow(base, new_exp, evaluate=False)
                    return node
                
                # Recursive visit
                if hasattr(node, 'args') and node.args:
                    new_args = list(node.args)
                    for i in range(len(new_args)):
                        if random.random() < 0.3: # Probability of mutation
                            new_args[i] = _mutate_node(new_args[i])
                    return node.func(*new_args, evaluate=False)
                
                return node

            mutated_expr = _mutate_node(expr)
            # If nothing changed, force a string replace for sign flip
            if str(mutated_expr) == sympy_str:
                if '+' in sympy_str: return sympy_str.replace('+', '-', 1)
                if '-' in sympy_str: return sympy_str.replace('-', '+', 1)
                
            return str(mutated_expr)
        except Exception as e:
            # Fallback to simple string manipulation if sympify fails
            if '+' in sympy_str: return sympy_str.replace('+', '-', 1)
            return sympy_str + " + random_error"

    def assemble_record(self, input_text, formula_obj):
        return {
            "instruction": self.instruction,
            "input": input_text,
            "output": f"检测到公式表述不规整或存在逻辑错误。标准的 {formula_obj['name']} 应当为：{formula_obj['standard_latex']}"
        }

    def build(self):
        records = []
        for f in self.formulas:
            # 1. Add NL pseudo variants (Clean)
            nl_variants = self.generate_pseudo_nl(f['name'], f['standard_latex'])
            for nl in nl_variants:
                records.append(self.assemble_record(nl, f))
            
            # 2. Add Adversarial variants (Dirty)
            for _ in range(self.num_variants):
                mutated_sympy = self.mutate_formula(f['sympy_expr'])
                try:
                    # Convert mutated sympy back to a "wrong" latex
                    wrong_latex = latex(sympify(mutated_sympy, evaluate=False))
                except:
                    wrong_latex = mutated_sympy
                
                records.append(self.assemble_record(wrong_latex, f))

        # Shuffle and Save
        random.shuffle(records)
        with open(self.out_path, 'w', encoding='utf-8') as f_out:
            for r in records:
                f_out.write(json.dumps(r, ensure_ascii=False) + "\n")
        
        print(f"[{self.out_path}] Generated {len(records)} records.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="formulas.json")
    parser.add_argument("--out", default="train.jsonl")
    parser.add_argument("--num", type=int, default=3)
    args = parser.parse_args()

    builder = FormulaDatasetBuilder(args.src, args.out, args.num)
    builder.load_source()
    builder.build()

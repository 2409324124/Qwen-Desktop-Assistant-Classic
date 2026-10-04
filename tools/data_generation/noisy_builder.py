import argparse
import json
import random
import re
from pathlib import Path
from typing import Any


DEFAULT_RULE_WEIGHTS: dict[str, int] = {
    "ascii_substitute": 14,
    "mixed_language": 12,
    "subscript_loss": 10,
    "hat_bar_prime_loss": 10,
    "operator_confusion": 10,
    "partial_formula_reference": 12,
    "broken_brackets": 8,
    "keyword_shorthand": 8,
    "code_fragment_noise": 4,
}

TOKEN_REPLACEMENTS: list[tuple[str, str]] = [
    ("积分", "integral"),
    ("求和", "sum"),
    ("极限", "limit"),
    ("平方根", "sqrt"),
    ("平方", "^2"),
    ("立方", "^3"),
    ("乘以", "*"),
    ("乘", "*"),
    ("除以", "/"),
    ("加上", "+"),
    ("减去", "-"),
    ("无穷大", "infinity"),
    ("指数", "exp"),
    ("导数", "derivative"),
    ("偏导", "partial"),
]

FORMULA_NAME_SHORTCUTS: dict[str, str] = {
    "Mean Squared Error": "MSE loss",
    "Cross-Entropy Loss": "cross entropy loss",
    "Softmax Function": "softmax formula",
    "Bayes' Theorem": "Bayes formula",
    "Gaussian Integral": "gaussian integral",
    "Euler's Formula": "Euler formula",
    "ReLU Activation Function": "ReLU",
    "Gradient Descent Update": "GD update",
    "Hessian Matrix": "Hessian matrix",
    "Jacobian Matrix": "Jacobian matrix",
    "Kinematic Velocity Equation": "velocity update formula",
    "Kinematic Displacement Equation": "displacement formula",
    "Rotation Matrix": "rotation matrix",
    "Diagonal Matrix": "diagonal matrix",
    "Laplace Transform": "Laplace transform",
    "Ampere-Maxwell Law": "Ampere-Maxwell law",
    "Complex Conjugate Product": "complex conjugate product",
    "De Broglie Wavelength": "de Broglie wavelength",
    "Binomial Theorem": "binomial theorem",
    "Characteristic Equation": "characteristic equation",
    "Schrodinger Equation": "Schrodinger equation",
}

AMBIGUOUS_SHORTCUT_CONTEXT: dict[str, str] = {
    "Kinematic Displacement Equation": "displacement formula with v0 a delta x",
    "Kinematic Velocity Equation": "velocity formula with v0 a t",
    "Laplace Transform": "Laplace transform integral from 0 to infinity",
    "Hessian Matrix": "Hessian second partial matrix",
    "Jacobian Matrix": "Jacobian partial derivative matrix",
    "Covariance": "covariance formula for x and y",
    "Characteristic Equation": "det A minus lambda I equals 0",
    "Product Rule": "product rule derivative",
    "Softmax Function": "softmax exp over sum exp",
    "Schrodinger Equation": "Schrodinger equation i hbar d psi dt",
}

# Historical context strings are retained for auditing old data only. New
# generation derives symbols and operators solely from the complete formula.

GENERIC_SHORTCUT_MARKERS: tuple[str, ...] = (
    "我想问",
    "那个",
    "就是",
    "怎么写",
    "公式",
)

LATEX_INLINE_MAP: list[tuple[str, str]] = [
    (r"\\alpha", "alpha"),
    (r"\\beta", "beta"),
    (r"\\gamma", "gamma"),
    (r"\\theta", "theta"),
    (r"\\phi", "phi"),
    (r"\\lambda", "lambda"),
    (r"\\mu", "mu"),
    (r"\\sigma", "sigma"),
    (r"\\omega", "omega"),
    (r"\\xi", "xi"),
    (r"\\epsilon", "epsilon"),
    (r"\\varepsilon", "epsilon"),
    (r"\\Delta", "Delta"),
    (r"\\nabla", "nabla"),
    (r"\\infty", "infinity"),
    (r"\\cdots", "..."),
    (r"\\vdots", "..."),
    (r"\\ddots", "..."),
    (r"\\times", " cross "),
    (r"\\log", "log"),
    (r"\\exp", "exp"),
    (r"\\cos", "cos"),
    (r"\\sin", "sin"),
    (r"\\tanh", "tanh"),
    (r"\\max", "max"),
    (r"\\odot", " elementwise_mul "),
    (r"\\otimes", " tensor_product "),
]

FORMAT_COMMANDS: tuple[str, ...] = (
    "left",
    "right",
    "mathcal",
    "mathbf",
    "mathrm",
    "operatorname",
    "text",
    "begin",
    "end",
)

LOW_QUALITY_MARKERS: tuple[str, ...] = (
    "beginbmatrix",
    "endbmatrix",
    "mathcal",
    "operatorname",
    "varepsilon",
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def save_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def sanitize_surface_text(text: str) -> str:
    """Normalize layout only; symbols, operators and repeated operands are data."""
    return normalize_spaces(text)


def maybe_trim(text: str, rng: random.Random) -> str:
    # Kept for compatibility: trimming formula clauses destroys the target mapping.
    return sanitize_surface_text(text)


def load_formula_text(latex: str) -> str:
    """Keep the complete LaTeX surface, including matrix layout and nested groups.

    The old ASCII projection lost operator types, font semantics and grouping.
    """
    return normalize_spaces(latex)


def latex_to_ascii_fragment(latex: str) -> str:
    # Historical API name; the safe projection now preserves complete LaTeX.
    return load_formula_text(latex)


def dedupe_tail(head: str, tail: str) -> str:
    # Repeated formula operands are not redundant natural-language tokens.
    return normalize_spaces(tail)


def maybe_apply_typo_noise(text: str, rng: random.Random, strength: float = 0.08) -> str:
    # Mutating alpha/theta/etc. would mutate identifiers, not just prose.
    return text


def formula_complexity(formula: str) -> int:
    return len(re.findall(r"(integral|sum|partial|sqrt|matrix|nabla|infinity)", latex_to_ascii_fragment(formula)))


def choose_applicable_rule(text: str, formula_name: str, formula: str, rng: random.Random) -> str:
    applicable = dict(DEFAULT_RULE_WEIGHTS)
    signal = f"{text} {formula_name} {formula}"

    if not re.search(r"(hat|bar|prime|导数|_hat|_bar|')", signal, re.IGNORECASE):
        applicable.pop("hat_bar_prime_loss", None)
    if not re.search(r"[_][A-Za-z0-9{]", signal):
        applicable["subscript_loss"] = max(4, applicable.get("subscript_loss", 0) // 2)
    if len(text) < 12:
        applicable["partial_formula_reference"] = 5
        applicable["keyword_shorthand"] = max(3, applicable.get("keyword_shorthand", 0) // 2)
    if formula_complexity(formula) >= 4:
        applicable["ascii_substitute"] = max(6, applicable["ascii_substitute"] - 6)
        applicable["code_fragment_noise"] = applicable.get("code_fragment_noise", 0) + 3

    rules = list(applicable)
    weights = [applicable[rule] for rule in rules]
    return rng.choices(rules, weights=weights, k=1)[0]


def apply_ascii_substitute(text: str, formula: str, rng: random.Random) -> str:
    fragment = latex_to_ascii_fragment(formula)
    return normalize_spaces(f"{rng.choice(('note', 'calc', 'draft'))}: {fragment}")


def apply_mixed_language(text: str, formula_name: str, rng: random.Random) -> str:
    # mutate_record supplies the current formula, never stale source prose.
    shortcut = FORMULA_NAME_SHORTCUTS.get(formula_name, formula_name or "formula")
    return normalize_spaces(f"{rng.choice(('写一下', 'note', '公式'))} {shortcut}: {text}")


def apply_subscript_loss(text: str, formula: str, rng: random.Random) -> str:
    # Rule name retained; loss is now simulated by commentary/layout only.
    return normalize_spaces(f"script note: {latex_to_ascii_fragment(formula)}")


def apply_hat_bar_prime_loss(text: str, formula: str, rng: random.Random) -> str:
    return normalize_spaces(f"symbol note: {latex_to_ascii_fragment(formula)}")


def apply_operator_confusion(text: str, formula: str, rng: random.Random) -> str:
    return normalize_spaces(f"draft equation: {latex_to_ascii_fragment(formula)}")


def apply_partial_formula_reference(text: str, formula_name: str, formula: str, rng: random.Random) -> str:
    templates = [
        "那个 {shortcut}",
        "{shortcut} 那个式子",
        "就是 {shortcut}",
        "我想问 {shortcut}",
    ]
    shortcut = FORMULA_NAME_SHORTCUTS.get(formula_name, formula_name or "formula")
    return normalize_spaces(rng.choice(templates).format(shortcut=shortcut) + ': ' + latex_to_ascii_fragment(formula))


def apply_broken_brackets(text: str, formula: str, rng: random.Random) -> str:
    # Damage only an added outer wrapper, preserving every original group.
    return "[ " + latex_to_ascii_fragment(formula)


def apply_keyword_shorthand(text: str, formula_name: str, formula: str, rng: random.Random) -> str:
    shortcut = FORMULA_NAME_SHORTCUTS.get(formula_name, formula_name or 'formula')
    return normalize_spaces(shortcut + ': ' + latex_to_ascii_fragment(formula))


def apply_code_fragment_noise(text: str, formula_name: str, formula: str, rng: random.Random) -> str:
    fragment = latex_to_ascii_fragment(formula)
    label = rng.choice(("calc", "eq", "update", "note", "tmp", "draft"))
    return normalize_spaces(f"// {label}: {fragment}")


def is_low_quality_noise(text: str) -> bool:
    lower = text.lower()
    if any(marker in lower for marker in LOW_QUALITY_MARKERS):
        return True
    if len(re.findall(r"(mathcal|begin|end|varepsilon|cdots|vdots|ddots)", lower)) >= 2:
        return True
    if re.search(r"([A-Za-z]{7,})(\s+\1){1,}", text):
        return True
    if len(text) > 110 and len(re.findall(r"[A-Za-z_]+", text)) > 20 and not re.search(r"[，。,.]", text):
        return True
    return False


def repair_low_quality_noise(text: str, formula_name: str, formula: str) -> str:
    shortcut = FORMULA_NAME_SHORTCUTS.get(formula_name, formula_name or "formula")
    return sanitize_surface_text(f"{shortcut}: {latex_to_ascii_fragment(formula)}")


def mutate_record(record: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    text = record["input"]
    output = record["output"]
    metadata = dict(record.get("metadata") or {})
    formula_name = metadata.get("formula_name") or ""
    rule = choose_applicable_rule(text, formula_name, output, rng)

    mutators = {
        "ascii_substitute": lambda: apply_ascii_substitute(text, output, rng),
        "mixed_language": lambda: apply_mixed_language(output, formula_name, rng),
        "subscript_loss": lambda: apply_subscript_loss(text, output, rng),
        "hat_bar_prime_loss": lambda: apply_hat_bar_prime_loss(text, output, rng),
        "operator_confusion": lambda: apply_operator_confusion(text, output, rng),
        "partial_formula_reference": lambda: apply_partial_formula_reference(text, formula_name, output, rng),
        "broken_brackets": lambda: apply_broken_brackets(text, output, rng),
        "keyword_shorthand": lambda: apply_keyword_shorthand(text, formula_name, output, rng),
        "code_fragment_noise": lambda: apply_code_fragment_noise(text, formula_name, output, rng),
    }

    noisy_input = maybe_trim(mutators[rule](), rng)
    if noisy_input == text:
        fallback = dedupe_tail(noisy_input, latex_to_ascii_fragment(output))
        noisy_input = sanitize_surface_text(f"{noisy_input} {fallback}") if fallback else noisy_input

    if is_low_quality_noise(noisy_input):
        noisy_input = repair_low_quality_noise(noisy_input, formula_name, output)

    noisy_input = sanitize_surface_text(noisy_input)

    new_metadata = dict(metadata)
    new_metadata.update(
        {
            "noise_rule": rule,
            "noise_source_perspective": metadata.get("perspective"),
            "source_input": text,
            "generator": "RuleBasedNoisyBuilder",
            "fidelity_policy": "complete_formula_surface_v1",
            "noise_scope": "layout_and_filler",
        }
    )

    return {
        "instruction": record["instruction"],
        "input": noisy_input,
        "output": output,
        "metadata": new_metadata,
    }


def build_noisy_records(records: list[dict[str, Any]], count: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    if not records:
        return []

    chosen = rng.sample(records, k=min(count, len(records)))
    noisy_records = [mutate_record(record, rng) for record in chosen]
    rng.shuffle(noisy_records)
    return noisy_records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="archive/phase1/data/train_clean_v1_120.jsonl")
    parser.add_argument("--out", default="archive/phase1/data/train_noisy_v4_100.jsonl")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    src_path = Path(args.src)
    out_path = Path(args.out)

    records = load_jsonl(src_path)
    noisy_records = build_noisy_records(records, count=args.count, seed=args.seed)
    save_jsonl(out_path, noisy_records)
    print(f"[DONE] Generated {len(noisy_records)} noisy records -> {out_path}")


if __name__ == "__main__":
    main()

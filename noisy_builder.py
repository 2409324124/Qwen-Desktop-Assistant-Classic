import argparse
import json
import random
import re
from pathlib import Path
from typing import Any


DEFAULT_RULE_WEIGHTS: dict[str, int] = {
    "ascii_substitute": 16,
    "mixed_language": 12,
    "subscript_loss": 10,
    "hat_bar_prime_loss": 10,
    "operator_confusion": 10,
    "partial_formula_reference": 12,
    "broken_brackets": 8,
    "keyword_shorthand": 7,
    "code_fragment_noise": 4,
}

TOKEN_REPLACEMENTS: list[tuple[str, str]] = [
    ("积分", "int"),
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
    ("无穷大", "inf"),
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
}

AMBIGUOUS_SHORTCUT_CONTEXT: dict[str, str] = {
    "Kinematic Displacement Equation": "displacement formula with v0 a delta x",
    "Kinematic Velocity Equation": "velocity formula with v0 a t",
    "Laplace Transform": "Laplace transform int 0 to inf",
    "Hessian Matrix": "Hessian second partial matrix",
    "Jacobian Matrix": "Jacobian partial derivative matrix",
    "Covariance": "covariance formula for x and y",
    "Characteristic Equation": "det A minus lambda I equals 0",
    "Product Rule": "product rule derivative",
    "Softmax Function": "softmax exp over sum exp",
    "Schrodinger Equation": "Schrodinger equation i hbar d/dt psi",
}

GENERIC_SHORTCUT_MARKERS: tuple[str, ...] = (
    "我想问",
    "那个",
    "就是",
    "怎么写",
    "公式",
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


def strip_latex_wrappers(text: str) -> str:
    text = re.sub(r"\\mathbf\{([^{}]+)\}", r"\1", text)
    text = re.sub(r"\\text\{([^{}]+)\}", r"\1", text)
    text = re.sub(r"\\hat\{([^{}]+)\}", r"\1_hat", text)
    text = re.sub(r"\\bar\{([^{}]+)\}", r"\1_bar", text)
    text = re.sub(r"\\([A-Za-z]+)", r"\1", text)
    text = text.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", text).strip()


def latex_to_ascii_fragment(latex: str) -> str:
    text = latex
    text = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1)/(\2)", text)
    text = re.sub(r"\\sum_\{([^{}]+)\}\^\{([^{}]+)\}", r"sum[\1->\2]", text)
    text = re.sub(r"\\int_\{([^{}]+)\}\^\{([^{}]+)\}", r"int[\1->\2]", text)
    text = re.sub(r"\\sqrt\{([^{}]+)\}", r"sqrt(\1)", text)
    return strip_latex_wrappers(text)


def maybe_trim(text: str, rng: random.Random) -> str:
    text = re.sub(r"\s+", " ", text).strip(" ，,。.？?;；")
    if len(text) > 120 and rng.random() < 0.55:
        parts = re.split(r"[，,。.;；]", text)
        parts = [part.strip() for part in parts if part.strip()]
        if parts:
            text = parts[0]
    return text


def dedupe_tail(head: str, tail: str) -> str:
    head_tokens = set(re.findall(r"[A-Za-z0-9_]+", head.lower()))
    tail_tokens = [token for token in re.findall(r"[A-Za-z0-9_]+", tail) if token.lower() not in head_tokens]
    return " ".join(tail_tokens[:8]).strip()


def maybe_apply_typo_noise(text: str, rng: random.Random, strength: float = 0.12) -> str:
    if rng.random() >= strength:
        return text

    replacements = [
        ("alpha", "alpa"),
        ("gamma", "gama"),
        ("theta", "thta"),
        ("lambda", "lamda"),
        ("sigma", "sigm"),
    ]
    mutated = text
    for source, target in replacements:
        if source in mutated and rng.random() < 0.45:
            mutated = mutated.replace(source, target, 1)
    return mutated


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

    rules = list(applicable)
    weights = [applicable[rule] for rule in rules]
    return rng.choices(rules, weights=weights, k=1)[0]


def apply_ascii_substitute(text: str, formula: str, rng: random.Random) -> str:
    mutated = text
    for source, target in TOKEN_REPLACEMENTS:
        if source in mutated and rng.random() < 0.55:
            mutated = mutated.replace(source, target)

    concise = maybe_trim(mutated, rng)
    fragment = latex_to_ascii_fragment(formula)

    if concise != text and rng.random() < 0.7:
        return maybe_apply_typo_noise(concise, rng)

    if len(concise) > 48:
        suffix = dedupe_tail(concise, fragment)
        out = f"{concise[:48].rstrip()} {suffix}".strip() if suffix else concise[:64].rstrip()
        return maybe_apply_typo_noise(out, rng)

    prefix = concise if concise and rng.random() < 0.4 else ""
    suffix = dedupe_tail(prefix, fragment)
    if prefix and suffix:
        return maybe_apply_typo_noise(f"{prefix} {suffix}".strip(), rng)
    return maybe_apply_typo_noise(suffix or concise or fragment, rng)


def apply_mixed_language(text: str, formula_name: str, rng: random.Random) -> str:
    mutated = text
    phrases = [
        ("公式", "formula"),
        ("函数", "function"),
        ("矩阵", "matrix"),
        ("梯度", "gradient"),
        ("损失", "loss"),
        ("积分", "integral"),
        ("导数", "derivative"),
    ]
    for source, target in phrases:
        if source in mutated and rng.random() < 0.6:
            mutated = mutated.replace(source, target)

    concise = maybe_trim(mutated, rng)
    shortcut = FORMULA_NAME_SHORTCUTS.get(formula_name, formula_name)
    if formula_name and rng.random() < 0.45:
        patterns = [
            "{text} ({shortcut})",
            "{shortcut}: {text}",
            "{text} / {shortcut}",
            "{text}, aka {shortcut}",
        ]
        return rng.choice(patterns).format(text=concise, shortcut=shortcut).strip()
    return concise


def apply_subscript_loss(text: str, formula: str, rng: random.Random) -> str:
    mutated = re.sub(r"([A-Za-z])_([A-Za-z0-9])", r"\1\2", text)
    mutated = re.sub(r"([A-Za-z])_\{([^{}]+)\}", lambda m: f"{m.group(1)}{m.group(2).replace('-', ' prev ')}", mutated)
    if mutated == text:
        fragment = latex_to_ascii_fragment(formula)
        mutated = re.sub(r"([A-Za-z])_([A-Za-z0-9])", r"\1\2", fragment)
    return mutated


def apply_hat_bar_prime_loss(text: str, formula: str, rng: random.Random) -> str:
    mutated = text
    replacements = [
        (r"\by_hat\b", "yhat"),
        (r"\bx_hat\b", "xhat"),
        (r"\btheta_hat\b", "theta"),
        (r"\bf'\(([^)]+)\)", r"f \1 derivative"),
        (r"prime", ""),
    ]
    for pattern, repl in replacements:
        mutated = re.sub(pattern, repl, mutated)
    if mutated == text:
        fragment = latex_to_ascii_fragment(formula)
        mutated = fragment.replace("_hat", "").replace("_bar", "")
    return re.sub(r"\s+", " ", mutated).strip()


def apply_operator_confusion(text: str, formula: str, rng: random.Random) -> str:
    mutated = text
    if "=" in mutated and rng.random() < 0.65:
        mutated = mutated.replace("=", "==", 1)
    elif rng.random() < 0.45:
        fragment = latex_to_ascii_fragment(formula)
        if "=" in fragment:
            prefix = maybe_trim(text, rng)
            short_fragment = fragment.replace("=", "==", 1)
            if len(prefix) < 36:
                mutated = f"{prefix} {short_fragment}".strip()
            else:
                mutated = short_fragment
    if rng.random() < 0.35:
        mutated = mutated.replace(" / ", "/").replace(" * ", "*")
    return mutated


def apply_partial_formula_reference(text: str, formula_name: str, formula: str, rng: random.Random) -> str:
    templates = [
        "那个 {shortcut}",
        "{shortcut} 那个式子",
        "就是 {shortcut}",
        "我想问 {shortcut}",
    ]
    shortcut = FORMULA_NAME_SHORTCUTS.get(formula_name, formula_name or latex_to_ascii_fragment(formula)[:24])
    return rng.choice(templates).format(shortcut=shortcut)


def apply_broken_brackets(text: str, formula: str, rng: random.Random) -> str:
    candidate = text if any(ch in text for ch in "()[]{}") else latex_to_ascii_fragment(formula)
    pairs = [("(", ")"), ("[", "]"), ("{", "}")]
    options: list[str] = []

    for left, right in pairs:
        left_positions = [m.start() for m in re.finditer(re.escape(left), candidate)]
        right_positions = [m.start() for m in re.finditer(re.escape(right), candidate)]
        if left_positions and right_positions:
            if len(right_positions) > 1:
                drop_index = right_positions[len(right_positions) // 2]
            else:
                drop_index = right_positions[0]
            options.append(candidate[:drop_index] + candidate[drop_index + 1 :])

    if options:
        return maybe_trim(rng.choice(options), rng)
    return candidate[:-1] if len(candidate) > 8 else candidate


def apply_keyword_shorthand(text: str, formula_name: str, formula: str, rng: random.Random) -> str:
    shortcut = AMBIGUOUS_SHORTCUT_CONTEXT.get(formula_name) or FORMULA_NAME_SHORTCUTS.get(formula_name)
    if shortcut:
        return shortcut

    concise = maybe_trim(text, rng)
    parts = [part.strip() for part in re.split(r"[，,。.;；]", concise) if part.strip()]
    if parts:
        candidate = parts[0][:48]
        if len(candidate) >= 10 and not any(marker in candidate for marker in GENERIC_SHORTCUT_MARKERS):
            return candidate

    fragment = latex_to_ascii_fragment(formula)
    tokens = [token for token in re.split(r"[^A-Za-z0-9_+-]+", fragment) if token]
    if formula_name:
        return f"{formula_name} { ' '.join(tokens[:3])}".strip()[:56]
    return " ".join(tokens[: min(5, len(tokens))]) or fragment[:48]


def apply_code_fragment_noise(text: str, formula_name: str, formula: str, rng: random.Random) -> str:
    fragment = latex_to_ascii_fragment(formula)
    labels = ["calc", "eq", "update", "note", "tmp", "draft"]
    label = rng.choice(labels)
    shortcut = FORMULA_NAME_SHORTCUTS.get(formula_name, "formula")
    variants = [
        f"{label}: {fragment}",
        f"{shortcut}: {fragment}",
        f"{label} -> {fragment}",
        f"{fragment} // {label}",
        fragment,
    ]
    return maybe_apply_typo_noise(rng.choice(variants), rng, strength=0.08)


def mutate_record(record: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    text = record["input"]
    output = record["output"]
    metadata = dict(record.get("metadata") or {})
    formula_name = metadata.get("formula_name") or ""
    rule = choose_applicable_rule(text, formula_name, output, rng)

    mutators = {
        "ascii_substitute": lambda: apply_ascii_substitute(text, output, rng),
        "mixed_language": lambda: apply_mixed_language(text, formula_name, rng),
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
        noisy_input = f"{noisy_input} {fallback}".strip() if fallback else noisy_input

    new_metadata = dict(metadata)
    new_metadata.update(
        {
            "noise_rule": rule,
            "noise_source_perspective": metadata.get("perspective"),
            "source_input": text,
            "generator": "RuleBasedNoisyBuilder",
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
    parser.add_argument("--src", default="train_clean_v1_120.jsonl")
    parser.add_argument("--out", default="train_noisy_v3_100.jsonl")
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

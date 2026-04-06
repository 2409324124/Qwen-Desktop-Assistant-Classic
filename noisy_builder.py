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
    (r"\\times", " x "),
    (r"\\log", "log"),
    (r"\\exp", "exp"),
    (r"\\cos", "cos"),
    (r"\\sin", "sin"),
    (r"\\tanh", "tanh"),
    (r"\\max", "max"),
    (r"\\odot", " * "),
    (r"\\otimes", " * "),
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
    text = re.sub(r"\s+", " ", text)
    return text.strip(" ，,。.？?;；")


def sanitize_surface_text(text: str) -> str:
    text = re.sub(r"\bfrac\b", "over", text)
    text = re.sub(r"\bsum_", "sum ", text)
    text = re.sub(r"\bintegral_", "integral ", text)
    text = re.sub(r"([A-Za-z])_\s+([A-Za-z0-9])", r"\1_\2", text)
    text = re.sub(r"\bpartial\s+partial\b", "partial", text)
    text = text.replace(".odot", "*")
    text = re.sub(r"\bodot\b", "*", text)
    text = re.sub(r"\botimes\b", "*", text)
    text = re.sub(r"\s+ygamma\s+ygamma\b", "", text)
    text = re.sub(r"\s+h_[A-Za-z0-9_]+$", "", text)
    text = re.sub(r"\s+x_odot\b", "", text)
    text = re.sub(r"\b([A-Za-z]+)\s+\1\b", r"\1", text)
    text = re.sub(r"(\b[A-Za-z_]+\b)(?:\s+\1){1,}$", r"\1", text)
    text = re.sub(r"\b([A-Za-z])_([A-Za-z])([A-Za-z])_?\b", "", text)
    text = re.sub(r"(?:\s+[A-Za-z]+_[A-Za-z]+){1,}$", "", text)
    text = re.sub(r"(?:\s+[A-Za-z]+[A-Za-z_0-9]{2,}){2,}$", "", text)
    return normalize_spaces(text)


def maybe_trim(text: str, rng: random.Random) -> str:
    text = sanitize_surface_text(text)
    if len(text) > 120 and rng.random() < 0.55:
        parts = re.split(r"[，,。.;；]", text)
        parts = [part.strip() for part in parts if part.strip()]
        if parts:
            text = parts[0]
    return text


def load_formula_text(latex: str) -> str:
    text = latex
    text = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1)/(\2)", text)
    text = re.sub(r"\\sqrt\{([^{}]+)\}", r"sqrt(\1)", text)
    text = re.sub(r"\\sum_\{([^{}]+)\}\^\{([^{}]+)\}", r"sum[\1 to \2]", text)
    text = re.sub(r"\\int_\{([^{}]+)\}\^\{([^{}]+)\}", r"integral[\1 to \2]", text)
    text = re.sub(r"\\hat\{([^{}]+)\}", r"\1_hat", text)
    text = re.sub(r"\\bar\{([^{}]+)\}", r"\1_bar", text)

    for pattern, replacement in LATEX_INLINE_MAP:
        text = re.sub(pattern, replacement, text)

    for cmd in FORMAT_COMMANDS:
        text = re.sub(rf"\\{cmd}\s*\{{([^{{}}]+)\}}", r"\1", text)
        text = re.sub(rf"\\{cmd}\b", " ", text)

    text = text.replace("{", " ").replace("}", " ")
    text = text.replace("\\", " ")
    text = text.replace("&", " ")
    text = text.replace("^", "^")
    text = text.replace("_", "_")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def latex_to_ascii_fragment(latex: str) -> str:
    text = load_formula_text(latex)
    text = text.replace(" infinity ", " infinity ")
    text = text.replace("...", " ... ")
    text = text.replace(" x ", " * ")
    text = normalize_spaces(text)
    return text


def dedupe_tail(head: str, tail: str) -> str:
    head_tokens = set(re.findall(r"[A-Za-z0-9_]+", head.lower()))
    tail_tokens = [token for token in re.findall(r"[A-Za-z0-9_]+", tail) if token.lower() not in head_tokens]
    return " ".join(tail_tokens[:8]).strip()


def maybe_apply_typo_noise(text: str, rng: random.Random, strength: float = 0.08) -> str:
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
            break
    return mutated


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
    mutated = text
    for source, target in TOKEN_REPLACEMENTS:
        if source in mutated and rng.random() < 0.55:
            mutated = mutated.replace(source, target)

    concise = maybe_trim(mutated, rng)
    fragment = latex_to_ascii_fragment(formula)

    if concise != text and rng.random() < 0.65:
        return maybe_apply_typo_noise(concise, rng)

    if formula_complexity(formula) >= 4:
        short = " ".join(re.findall(r"[A-Za-z0-9_+\-/*^()=.]+", fragment)[:14])
        return maybe_apply_typo_noise(short or concise or fragment, rng)

    if len(concise) > 48:
        suffix = dedupe_tail(concise, fragment)
        out = f"{concise[:48].rstrip()} {suffix}".strip() if suffix else concise[:64].rstrip()
        return maybe_apply_typo_noise(out, rng)

    prefix = concise if concise and rng.random() < 0.35 else ""
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
    if formula_name and rng.random() < 0.35:
        patterns = [
            "{text} ({shortcut})",
            "{shortcut}: {text}",
            "{text} / {shortcut}",
            "{text}, aka {shortcut}",
        ]
        return normalize_spaces(rng.choice(patterns).format(text=concise, shortcut=shortcut))
    return concise


def apply_subscript_loss(text: str, formula: str, rng: random.Random) -> str:
    mutated = re.sub(r"([A-Za-z])_([A-Za-z0-9])", r"\1\2", text)
    mutated = re.sub(r"([A-Za-z])_\{([^{}]+)\}", lambda m: f"{m.group(1)}{m.group(2).replace('-', ' prev ')}", mutated)
    if mutated == text:
        fragment = latex_to_ascii_fragment(formula)
        mutated = re.sub(r"([A-Za-z])_([A-Za-z0-9])", r"\1\2", fragment)
    return normalize_spaces(mutated)


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
    return normalize_spaces(mutated)


def apply_operator_confusion(text: str, formula: str, rng: random.Random) -> str:
    mutated = text
    if "=" in mutated and rng.random() < 0.65:
        mutated = mutated.replace("=", "==", 1)
    elif rng.random() < 0.35:
        fragment = latex_to_ascii_fragment(formula)
        if "=" in fragment:
            short_fragment = fragment.replace("=", "==", 1)
            mutated = short_fragment if len(short_fragment) < 60 else " ".join(short_fragment.split()[:12])
    if rng.random() < 0.35:
        mutated = mutated.replace(" / ", "/").replace(" * ", "*")
    return normalize_spaces(mutated)


def apply_partial_formula_reference(text: str, formula_name: str, formula: str, rng: random.Random) -> str:
    templates = [
        "那个 {shortcut}",
        "{shortcut} 那个式子",
        "就是 {shortcut}",
        "我想问 {shortcut}",
    ]
    shortcut = FORMULA_NAME_SHORTCUTS.get(formula_name, formula_name or "formula")
    return normalize_spaces(rng.choice(templates).format(shortcut=shortcut))


def apply_broken_brackets(text: str, formula: str, rng: random.Random) -> str:
    candidate = text if any(ch in text for ch in "()[]{}") else latex_to_ascii_fragment(formula)
    pairs = [("(", ")"), ("[", "]"), ("{", "}")]
    options: list[str] = []

    for left, right in pairs:
        right_positions = [m.start() for m in re.finditer(re.escape(right), candidate)]
        if right_positions:
            drop_index = right_positions[len(right_positions) // 2]
            broken = candidate[:drop_index] + candidate[drop_index + 1 :]
            if any(ch in broken for ch in "(["):
                options.append(broken)

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

    if formula_name:
        return FORMULA_NAME_SHORTCUTS.get(formula_name, formula_name)
    return "formula shorthand"


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
    return maybe_apply_typo_noise(normalize_spaces(rng.choice(variants)), rng, strength=0.06)


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
    context = AMBIGUOUS_SHORTCUT_CONTEXT.get(formula_name) or FORMULA_NAME_SHORTCUTS.get(formula_name)
    fragment = latex_to_ascii_fragment(formula)
    short_fragment = " ".join(fragment.split()[:12])
    if context:
        return sanitize_surface_text(f"{context} {short_fragment}")
    return sanitize_surface_text(short_fragment)


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
    parser.add_argument("--out", default="train_noisy_v4_100.jsonl")
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

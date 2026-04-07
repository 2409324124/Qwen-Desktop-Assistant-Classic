import argparse
import random
import re
from pathlib import Path
from typing import Any

from noisy_builder import (
    FORMULA_NAME_SHORTCUTS,
    AMBIGUOUS_SHORTCUT_CONTEXT,
    dedupe_tail,
    formula_complexity,
    latex_to_ascii_fragment,
    load_jsonl,
    maybe_apply_typo_noise,
    normalize_spaces,
    sanitize_surface_text,
    save_jsonl,
)


DEFAULT_HARD_RULE_WEIGHTS: dict[str, int] = {
    "structure_collapse": 16,
    "fragment_anchor": 14,
    "operator_mix": 12,
    "symbol_dropout": 14,
    "dense_ascii": 12,
    "contextual_shorthand": 10,
    "equation_truncation": 10,
    "nested_break": 10,
    "code_commentary": 6,
}

HARD_CATEGORIES: tuple[str, ...] = ("stats_ml", "calculus", "physics", "matrix")
SHORTCUT_ONLY_NAMES: tuple[str, ...] = (
    "Softmax Function",
    "Cross-Entropy Loss",
    "Schrodinger Equation",
    "Laplace Transform",
    "Ampere-Maxwell Law",
    "Jacobian Matrix",
    "Hessian Matrix",
    "Self-Attention Score",
    "RNN Hidden State Update",
)


def is_named_formula(formula_name: str) -> bool:
    return bool(formula_name and formula_name in FORMULA_NAME_SHORTCUTS)


def extract_variable_anchor(output: str) -> str:
    fragment = latex_to_ascii_fragment(output)
    variables = re.findall(r"\b(?:[A-Za-z]+(?:_[A-Za-z0-9]+)?|[A-Za-z]\([A-Za-z0-9_, ]+\))\b", fragment)
    filtered: list[str] = []
    stopwords = {
        "integral",
        "sum",
        "sqrt",
        "infinity",
        "partial",
        "nabla",
        "exp",
        "sin",
        "cos",
        "tanh",
        "max",
        "min",
        "log",
    }
    for token in variables:
        token = token.strip()
        lower = token.lower()
        if lower in stopwords:
            continue
        if re.fullmatch(r"[A-Za-z]", token) or "_" in token or "(" in token:
            filtered.append(token)

    unique: list[str] = []
    for token in filtered:
        if token not in unique:
            unique.append(token)
    return ", ".join(unique[:3])


def score_record(record: dict[str, Any]) -> int:
    metadata = record.get("metadata") or {}
    category = metadata.get("category") or ""
    formula_name = metadata.get("formula_name") or ""
    output = record.get("output") or ""

    score = formula_complexity(output) * 3
    score += len(re.findall(r"(\\frac|\\int|\\sum|\\partial|\\nabla|\\sqrt|\\begin\{bmatrix\}|=)", output))
    if category in HARD_CATEGORIES:
        score += 3
    if formula_name in SHORTCUT_ONLY_NAMES:
        score += 2
    if len(output) > 45:
        score += 2
    return score


def choose_hard_rule(record: dict[str, Any], rng: random.Random) -> str:
    metadata = record.get("metadata") or {}
    text = record["input"]
    output = record["output"]
    formula_name = metadata.get("formula_name") or ""
    named_formula = is_named_formula(formula_name)
    applicable = dict(DEFAULT_HARD_RULE_WEIGHTS)

    if formula_complexity(output) >= 4:
        applicable["dense_ascii"] += 6
        applicable["nested_break"] += 4
        applicable["fragment_anchor"] += 3

    if not re.search(r"(=|\\frac|\\int|\\sum|\\partial|\\nabla|\(|\[)", output):
        applicable["nested_break"] = max(2, applicable["nested_break"] - 4)
        applicable["equation_truncation"] = max(4, applicable["equation_truncation"] - 2)

    if len(text) < 22:
        applicable["contextual_shorthand"] += 6
        applicable["fragment_anchor"] += 2

    if formula_name in SHORTCUT_ONLY_NAMES:
        applicable["contextual_shorthand"] += 5

    if not named_formula:
        applicable["equation_truncation"] = max(3, applicable["equation_truncation"] - 5)
        applicable["contextual_shorthand"] = max(4, applicable["contextual_shorthand"] - 4)

    rules = list(applicable)
    weights = [applicable[rule] for rule in rules]
    return rng.choices(rules, weights=weights, k=1)[0]


def apply_structure_collapse(text: str, output: str, rng: random.Random) -> str:
    fragment = latex_to_ascii_fragment(output)
    fragment = re.sub(r"\s+", " ", fragment)
    fragment = re.sub(r"\b(integral|sum)\[([^\]]+)\]", r"\1 \2", fragment)
    fragment = fragment.replace("(", " ").replace(")", " ")
    fragment = fragment.replace("[", " ").replace("]", " ")
    fragment = re.sub(r"\s*=\s*", " = ", fragment)
    tokens = fragment.split()
    if len(tokens) > 14:
        start = rng.randint(0, max(0, len(tokens) - 14))
        tokens = tokens[start : start + 14]
    prefix = rng.choice(("draft", "calc", "tmp", "derive", "推导", "先记这个"))
    return normalize_spaces(f"{prefix}: {' '.join(tokens)}")


def apply_fragment_anchor(text: str, output: str, formula_name: str, rng: random.Random) -> str:
    fragment = latex_to_ascii_fragment(output)
    short_fragment = " ".join(fragment.split()[:10])
    anchor = AMBIGUOUS_SHORTCUT_CONTEXT.get(formula_name) or FORMULA_NAME_SHORTCUTS.get(formula_name) or formula_name or "that formula"
    variable_anchor = extract_variable_anchor(output)
    patterns = [
        f"{anchor} -> {short_fragment}",
        f"{short_fragment} ... {anchor}",
        f"{anchor}, core part {short_fragment}",
        f"{short_fragment} ({anchor})",
        f"{anchor} [{variable_anchor}] -> {short_fragment}" if variable_anchor else f"{anchor} -> {short_fragment}",
        f"{anchor} for {variable_anchor}: {short_fragment}" if variable_anchor else f"{short_fragment} ({anchor})",
    ]
    return normalize_spaces(rng.choice(patterns))


def apply_operator_mix(text: str, output: str, rng: random.Random) -> str:
    fragment = latex_to_ascii_fragment(output)
    mutated = fragment.replace("=", rng.choice(("==", "~", "=>")), 1) if "=" in fragment else fragment
    mutated = mutated.replace(" * ", rng.choice((" x ", " ", "*")))
    mutated = mutated.replace(" / ", rng.choice(("/", " over ")))
    mutated = mutated.replace(" + ", rng.choice((" plus ", " + ", " ")))
    return maybe_apply_typo_noise(normalize_spaces(mutated), rng, strength=0.1)


def apply_symbol_dropout(text: str, output: str, rng: random.Random) -> str:
    fragment = latex_to_ascii_fragment(output)
    fragment = re.sub(r"_([A-Za-z0-9]+)", "", fragment)
    fragment = fragment.replace("^2", "").replace("^3", "")
    fragment = re.sub(r"\b(partial|derivative|nabla)\b", "", fragment)
    fragment = re.sub(r"\s+", " ", fragment).strip()
    return normalize_spaces(fragment)


def apply_dense_ascii(text: str, output: str, rng: random.Random) -> str:
    fragment = latex_to_ascii_fragment(output)
    tokens = re.findall(r"[A-Za-z0-9_+\-/*^=.]+", fragment)
    if len(tokens) > 16:
        tokens = tokens[:16]
    compact = " ".join(tokens)
    compact = compact.replace(" = ", "=").replace(" * ", "*").replace(" / ", "/")
    return maybe_apply_typo_noise(normalize_spaces(compact), rng, strength=0.08)


def apply_contextual_shorthand(text: str, output: str, formula_name: str, rng: random.Random) -> str:
    shortcut = AMBIGUOUS_SHORTCUT_CONTEXT.get(formula_name) or FORMULA_NAME_SHORTCUTS.get(formula_name) or formula_name or "formula"
    fragment = latex_to_ascii_fragment(output)
    variable_anchor = extract_variable_anchor(output)
    tail = dedupe_tail(shortcut, fragment)
    if tail:
        tail = " ".join(tail.split()[:6])
    zh_write = f"写个 {shortcut} [{variable_anchor}]".strip() if variable_anchor else f"写个 {shortcut}"
    zh_note = f"记一下 {shortcut} [{variable_anchor}]".strip() if variable_anchor else f"记一下 {shortcut}"
    patterns = [
        f"{shortcut} [{variable_anchor}]" if variable_anchor else f"{shortcut} core",
        f"{shortcut} main term {tail}".strip(),
        f"need {shortcut} {variable_anchor}".strip(),
        f"{shortcut} for {variable_anchor}".strip() if variable_anchor else f"{shortcut} main part",
        f"{shortcut} ({variable_anchor})".strip() if variable_anchor else f"{shortcut} main part",
        f"{shortcut} vars {variable_anchor}".strip() if variable_anchor else f"{shortcut} main part",
        zh_write,
        zh_note,
    ]
    return normalize_spaces(rng.choice(patterns))


def apply_equation_truncation(text: str, output: str, formula_name: str, rng: random.Random) -> str:
    fragment = latex_to_ascii_fragment(output)
    variable_anchor = extract_variable_anchor(output)
    named_formula = is_named_formula(formula_name)
    if "=" in fragment:
        left, right = fragment.split("=", 1)
        if named_formula:
            if rng.random() < 0.5:
                return normalize_spaces(f"{left.strip()} = {variable_anchor}".strip())
            return normalize_spaces(f"{FORMULA_NAME_SHORTCUTS.get(formula_name, formula_name)} = {right.strip()[:42]}")
        left_tokens = " ".join(left.strip().split()[:8])
        return normalize_spaces(f"{left_tokens} with {variable_anchor}".strip())
    words = fragment.split()
    if len(words) > 8:
        base = " ".join(words[:8])
        return normalize_spaces(f"{base} {variable_anchor}".strip())
    return normalize_spaces(fragment)


def apply_nested_break(text: str, output: str, rng: random.Random) -> str:
    fragment = latex_to_ascii_fragment(output)
    options: list[str] = []
    for left, right in (("(", ")"), ("[", "]")):
        right_positions = [m.start() for m in re.finditer(re.escape(right), fragment)]
        if right_positions:
            idx = right_positions[min(len(right_positions) // 2, len(right_positions) - 1)]
            options.append(fragment[:idx] + fragment[idx + 1 :])
    if options:
        broken = rng.choice(options)
    else:
        broken = fragment[:-1] if len(fragment) > 8 else fragment
    return normalize_spaces(broken)


def apply_code_commentary(text: str, output: str, formula_name: str, rng: random.Random) -> str:
    fragment = latex_to_ascii_fragment(output)
    labels = ("TODO", "check", "draft", "note", "dbg", "求导", "先算", "注")
    shortcut = FORMULA_NAME_SHORTCUTS.get(formula_name, formula_name or "formula")
    patterns = [
        f"// {shortcut}: {fragment}",
        f"{rng.choice(labels)} {shortcut} => {fragment}",
        f"{fragment} // revisit",
        f"{shortcut} ??? {fragment}",
        f"// {rng.choice(labels)}: {shortcut} {fragment}",
    ]
    return maybe_apply_typo_noise(normalize_spaces(rng.choice(patterns)), rng, strength=0.06)


def is_low_quality_hard(text: str) -> bool:
    lower = text.lower()
    if any(marker in lower for marker in ("mathcal", "beginbmatrix", "endbmatrix", "varepsilon", "operatorname")):
        return True
    if len(lower) < 6:
        return True
    if re.search(r"(?:\b[A-Za-z]{1,3}\b\s*){8,}$", text):
        return True
    if re.search(r"([A-Za-z_]{6,})(?:\s+\1){1,}", text):
        return True
    return False


def repair_low_quality_hard(output: str, formula_name: str) -> str:
    context = AMBIGUOUS_SHORTCUT_CONTEXT.get(formula_name) or FORMULA_NAME_SHORTCUTS.get(formula_name) or "formula"
    fragment = " ".join(latex_to_ascii_fragment(output).split()[:10])
    return sanitize_surface_text(f"{context} {fragment}")


def mutate_record(record: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    text = record["input"]
    output = record["output"]
    metadata = dict(record.get("metadata") or {})
    formula_name = metadata.get("formula_name") or ""
    rule = choose_hard_rule(record, rng)

    mutators = {
        "structure_collapse": lambda: apply_structure_collapse(text, output, rng),
        "fragment_anchor": lambda: apply_fragment_anchor(text, output, formula_name, rng),
        "operator_mix": lambda: apply_operator_mix(text, output, rng),
        "symbol_dropout": lambda: apply_symbol_dropout(text, output, rng),
        "dense_ascii": lambda: apply_dense_ascii(text, output, rng),
        "contextual_shorthand": lambda: apply_contextual_shorthand(text, output, formula_name, rng),
        "equation_truncation": lambda: apply_equation_truncation(text, output, formula_name, rng),
        "nested_break": lambda: apply_nested_break(text, output, rng),
        "code_commentary": lambda: apply_code_commentary(text, output, formula_name, rng),
    }

    hard_input = sanitize_surface_text(mutators[rule]())
    if is_low_quality_hard(hard_input):
        hard_input = repair_low_quality_hard(output, formula_name)

    new_metadata = dict(metadata)
    new_metadata.update(
        {
            "hard_rule": rule,
            "hard_source_perspective": metadata.get("perspective"),
            "source_input": text,
            "generator": "RuleBasedHardBuilder",
        }
    )

    return {
        "instruction": record["instruction"],
        "input": hard_input,
        "output": output,
        "metadata": new_metadata,
    }


def choose_seed_records(records: list[dict[str, Any]], count: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    if not records:
        return []

    ranked = sorted(records, key=score_record, reverse=True)
    pool_size = min(len(ranked), max(count * 3, count))
    pool = ranked[:pool_size]
    chosen = rng.sample(pool, k=min(count, len(pool)))
    return chosen


def build_hard_records(records: list[dict[str, Any]], count: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    chosen = choose_seed_records(records, count=count, seed=seed)
    hard_records = [mutate_record(record, rng) for record in chosen]
    rng.shuffle(hard_records)
    return hard_records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="train_clean_v1_300.jsonl")
    parser.add_argument("--out", default="train_hard_v1_100.jsonl")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    src_path = Path(args.src)
    out_path = Path(args.out)

    records = load_jsonl(src_path)
    hard_records = build_hard_records(records, count=args.count, seed=args.seed)
    save_jsonl(out_path, hard_records)
    print(f"[DONE] Generated {len(hard_records)} hard records -> {out_path}")


if __name__ == "__main__":
    main()

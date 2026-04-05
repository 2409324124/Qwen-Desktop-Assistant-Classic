import argparse
import json
import random
import re
import sys
from collections import Counter
from typing import Optional

from latex2sympy2 import latex2sympy
from sympy import Eq


TEXT_MACRO_RE = re.compile(r"\\text\{([^{}]*)\}")
OPERATOR_MACRO_RE = re.compile(r"\\(?:mathrm|operatorname)\{([^{}]*)\}")
STYLE_MACRO_RE = re.compile(r"\\(?:mathbf|mathcal|mathbb|mathit)\{([^{}]+)\}")
WHITESPACE_RE = re.compile(r"\s+")

# 默认领域配额。
# 这组比例来自我们当前的数据集规划：
# - stats_ml: 30%
# - calculus: 25%
# - physics: 15%
# - matrix: 15%
# - algebra_trig: 15%
DEFAULT_CATEGORY_RATIOS: dict[str, float] = {
    "stats_ml": 0.30,
    "calculus": 0.25,
    "physics": 0.15,
    "matrix": 0.15,
    "algebra_trig": 0.15,
}


def normalize_latex_for_sympy(latex_str: str) -> str:
    normalized = latex_str.strip()
    normalized = normalized.replace(r"\left", "").replace(r"\right", "")
    normalized = normalized.replace(r"\cdot", " ").replace(r"\,", " ")
    normalized = normalized.replace(r"\;", " ").replace(r"\quad", " ")
    normalized = TEXT_MACRO_RE.sub(r"\1", normalized)
    normalized = OPERATOR_MACRO_RE.sub(r"\1", normalized)
    normalized = STYLE_MACRO_RE.sub(r"\1", normalized)
    normalized = WHITESPACE_RE.sub(" ", normalized).strip()
    return normalized


def safe_latex2sympy_expr(latex_str: str) -> tuple[Optional[str], Optional[str]]:
    normalized = normalize_latex_for_sympy(latex_str)
    errors: list[str] = []

    if "=" in normalized:
        lhs, rhs = normalized.split("=", 1)
        try:
            lhs_expr = latex2sympy(lhs.strip())
            rhs_expr = latex2sympy(rhs.strip())
            return str(Eq(lhs_expr, rhs_expr, evaluate=False)), None
        except Exception as exc:
            errors.append(f"equation_sides: {type(exc).__name__}: {exc}")

    for label, candidate in (("raw", latex_str), ("normalized", normalized)):
        try:
            parsed = latex2sympy(candidate)
            if isinstance(parsed, list):
                return None, f"{label}: parser returned multiple candidate equations"
            return str(parsed), None
        except Exception as exc:
            errors.append(f"{label}: {type(exc).__name__}: {exc}")

    return None, " | ".join(errors) if errors else "unknown parse failure"


def build_templates() -> list[dict[str, str]]:
    return [
        {"name": "Softmax Function", "category": "stats_ml", "latex": r"\text{{Softmax}}({x}_{{{i}}}) = \frac{{\exp({x}_{{{i}}})}}{{\sum_j \exp({x}_j)}}"},
        {"name": "Self-Attention Mechanism", "category": "stats_ml", "latex": r"\text{{Attention}}({Q}, {K}, {V}) = \text{{softmax}}\left(\frac{{{Q} {K}^T}}{{\sqrt{{d_k}}}}\right){V}"},
        {"name": "Cross-Entropy Loss", "category": "stats_ml", "latex": r"\mathcal{{L}} = -\frac{{1}}{{{N}}} \sum_{{{i}=1}}^{{{N}}} {y}_{{{i}}} \log(\hat{{{y}}}_{{{i}}}) + (1 - {y}_{{{i}}}) \log(1 - \hat{{{y}}}_{{{i}}})"},
        {"name": "Gradient Descent Update", "category": "stats_ml", "latex": r"{theta}_{{{t}}} = {theta}_{{{t}-1}} - \eta \nabla J({theta}_{{{t}-1}})"},
        {"name": "Linear Layer with Activation", "category": "stats_ml", "latex": r"\hat{{{y}}} = \sigma({W} {x} + {b})"},
        {"name": "RMSNorm", "category": "stats_ml", "latex": r"\text{{RMSNorm}}({x}) = \frac{{{x}}}{{\sqrt{{\frac{{1}}{{d}} \sum_{{{i}=1}}^d {x}_{{{i}}}^2 + \epsilon}}}} \odot \gamma"},
        {"name": "Normal Distribution PDF", "category": "stats_ml", "latex": r"f({x}|\mu,\sigma^2) = \frac{{1}}{{\sqrt{{2\pi\sigma^2}}}} e^{{-\frac{{({x}-\mu)^2}}{{2\sigma^2}}}}"},
        {"name": "Covariance", "category": "stats_ml", "latex": r"\text{{Cov}}({x}, {y}) = \mathbb{{E}}[({x} - \mathbb{{E}}[{x}])({y} - \mathbb{{E}}[{y}])]"},
        {"name": "Bayes' Theorem", "category": "stats_ml", "latex": r"P(A|B) = \frac{{P(B|A)P(A)}}{{P(B)}}"},
        {"name": "Sample Mean", "category": "stats_ml", "latex": r"\bar{{{x}}} = \frac{{1}}{{{N}}} \sum_{{{i}=1}}^{{{N}}} {x}_{{{i}}}"},
        {"name": "Sample Variance", "category": "stats_ml", "latex": r"s^2 = \frac{{1}}{{{N}-1}} \sum_{{{i}=1}}^{{{N}}} ({x}_{{{i}}} - \bar{{{x}}})^2"},
        {"name": "Mean Squared Error", "category": "stats_ml", "latex": r"L = \frac{{1}}{{{N}}} \sum_{{{i}=1}}^{{{N}}} ({y}_{{{i}}} - \hat{{{y}}}_{{{i}}})^2"},
        {"name": "RNN Hidden State Update", "category": "stats_ml", "latex": r"\mathbf{{h}}_{{{t}}} = \tanh(\mathbf{{W}}\mathbf{{x}}_{{{t}}} + \mathbf{{U}}\mathbf{{h}}_{{{t}-1}} + \mathbf{{b}})"},
        {"name": "ReLU Activation Function", "category": "stats_ml", "latex": r"\text{{ReLU}}({x}) = \max(0, {x})"},
        {"name": "Mass-Energy Equivalence", "category": "physics", "latex": r"E = {m} c^2"},
        {"name": "Newton's Law of Universal Gravitation", "category": "physics", "latex": r"F = G \frac{{{m1} {m2}}}{{{r}^2}}"},
        {"name": "Gauss's Law for Electricity", "category": "physics", "latex": r"\nabla \cdot \mathbf{{E}} = \frac{{\rho}}{{\varepsilon_0}}"},
        {"name": "Gauss's Law (Integral Form)", "category": "physics", "latex": r"\oint \mathbf{{E}} \cdot d\mathbf{{A}} = \frac{{Q_{{\text{{enc}}}}}}{{\varepsilon_0}}"},
        {"name": "Ampere-Maxwell Law", "category": "physics", "latex": r"\nabla \times \mathbf{{B}} = \mu_0 \mathbf{{J}} + \mu_0 \varepsilon_0 \frac{{\partial \mathbf{{E}}}}{{\partial {t}}}"},
        {"name": "Schrodinger Equation", "category": "physics", "latex": r"i \hbar \frac{{\partial}}{{\partial {t}}} \Psi(\mathbf{{r}}, {t}) = \left[ -\frac{{\hbar^2}}{{2m}} \nabla^2 + V(\mathbf{{r}}, {t}) \right] \Psi(\mathbf{{r}}, {t})"},
        {"name": "Boltzmann Entropy", "category": "physics", "latex": r"S = k_B \ln \Omega"},
        {"name": "Coulomb's Law", "category": "physics", "latex": r"F = k_e \frac{{q_1 q_2}}{{{r}^2}}"},
        {"name": "De Broglie Wavelength", "category": "physics", "latex": r"\lambda = \frac{{h}}{{p}}"},
        {"name": "Second Law of Thermodynamics", "category": "physics", "latex": r"\Delta S \ge 0"},
        {"name": "Kinematic Velocity Equation", "category": "physics", "latex": r"{v} = v_0 + a {t}"},
        {"name": "Kinematic Displacement Equation", "category": "physics", "latex": r"{v}^2 = v_0^2 + 2a\Delta {x}"},
        {"name": "Gaussian Integral", "category": "calculus", "latex": r"\int_{{-\infty}}^{{\infty}} e^{{-{x}^2}} d{x} = \sqrt{{\pi}}"},
        {"name": "Fundamental Theorem of Calculus", "category": "calculus", "latex": r"\int_{{a}}^{{b}} f({x}) d{x} = F(b) - F(a)"},
        {"name": "Product Rule", "category": "calculus", "latex": r"({u}{v})' = {u}'{v} + {u}{v}'"},
        {"name": "Quotient Rule", "category": "calculus", "latex": r"\left(\frac{{{u}}}{{{v}}}\right)' = \frac{{{u}'{v} - {u}{v}'}}{{{v}^2}}"},
        {"name": "Chain Rule", "category": "calculus", "latex": r"\frac{{d}}{{d{x}}} [f(g({x}))] = f'(g({x})) g'({x})"},
        {"name": "Limit Definition of Derivative", "category": "calculus", "latex": r"f'({x}) = \lim_{{h \to 0}} \frac{{f({x} + h) - f({x})}}{{h}}"},
        {"name": "Taylor Series", "category": "calculus", "latex": r"f({x}) = \sum_{{{n}=0}}^{{\infty}} \frac{{f^{{({n})}}(a)}}{{{n}!}} ({x} - a)^{{{n}}}"},
        {"name": "Fourier Transform", "category": "calculus", "latex": r"\mathcal{{F}}\{{f({t})\}}(\omega) = \int_{{-\infty}}^{{\infty}} f({t}) e^{{-i\omega {t}}} d{t}"},
        {"name": "Laplace Transform", "category": "calculus", "latex": r"\mathcal{{L}}\{{f({t})\}}(s) = \int_{{0}}^{{\infty}} f({t}) e^{{-s{t}}} d{t}"},
        {"name": "Rotation Matrix", "category": "matrix", "latex": r"R_{{{theta}}} = \begin{{bmatrix}} \cos {theta} & -\sin {theta} \\ \sin {theta} & \cos {theta} \end{{bmatrix}}"},
        {"name": "Eigenvalue Equation", "category": "matrix", "latex": r"A \mathbf{{v}} = \lambda \mathbf{{v}}"},
        {"name": "Characteristic Equation", "category": "matrix", "latex": r"\det(A - \lambda I) = 0"},
        {"name": "Jacobian Matrix", "category": "matrix", "latex": r"J = \begin{{bmatrix}} \frac{{\partial f_1}}{{\partial {x}_1}} & \frac{{\partial f_1}}{{\partial {x}_2}} \\ \frac{{\partial f_2}}{{\partial {x}_1}} & \frac{{\partial f_2}}{{\partial {x}_2}} \end{{bmatrix}}"},
        {"name": "Hessian Matrix", "category": "matrix", "latex": r"H(f) = \begin{{bmatrix}} \frac{{\partial^2 f}}{{\partial {x}_1^2}} & \frac{{\partial^2 f}}{{\partial {x}_1 \partial {x}_2}} \\ \frac{{\partial^2 f}}{{\partial {x}_2 \partial {x}_1}} & \frac{{\partial^2 f}}{{\partial {x}_2^2}} \end{{bmatrix}}"},
        {"name": "Covariance Matrix", "category": "matrix", "latex": r"\Sigma = \begin{{bmatrix}} \sigma_{{{x}}}^2 & \rho\sigma_{{{x}}}\sigma_{{{y}}} \\ \rho\sigma_{{{x}}}\sigma_{{{y}}} & \sigma_{{{y}}}^2 \end{{bmatrix}}"},
        {"name": "Diagonal Matrix", "category": "matrix", "latex": r"\Lambda = \begin{{bmatrix}} \lambda_1 & 0 & 0 \\ 0 & \lambda_2 & 0 \\ 0 & 0 & \lambda_3 \end{{bmatrix}}"},
        {"name": "N x N Matrix with Ellipsis", "category": "matrix", "latex": r"A = \begin{{bmatrix}} a_{{11}} & a_{{12}} & \cdots & a_{{1{n}}} \\ a_{{21}} & a_{{22}} & \cdots & a_{{2{n}}} \\ \vdots & \vdots & \ddots & \vdots \\ a_{{{n}1}} & a_{{{n}2}} & \cdots & a_{{{n}{n}}} \end{{bmatrix}}"},
        {"name": "Block Matrix", "category": "matrix", "latex": r"M = \begin{{bmatrix}} A & B \\ C & D \end{{bmatrix}}"},
        {"name": "Euler's Identity", "category": "algebra_trig", "latex": r"e^{{i \pi}} + 1 = 0"},
        {"name": "Euler's Formula", "category": "algebra_trig", "latex": r"e^{{i {x}}} = \cos {x} + i \sin {x}"},
        {"name": "Pythagorean Theorem", "category": "algebra_trig", "latex": r"{u}^2 + {v}^2 = {z}^2"},
        {"name": "Law of Sines", "category": "algebra_trig", "latex": r"\frac{{\sin A}}{{a}} = \frac{{\sin B}}{{b}} = \frac{{\sin C}}{{c}}"},
        {"name": "Law of Cosines", "category": "algebra_trig", "latex": r"c^2 = a^2 + b^2 - 2ab \cos {theta}"},
        {"name": "Quadratic Formula", "category": "algebra_trig", "latex": r"{x} = \frac{{-b \pm \sqrt{{b^2 - 4ac}}}}{{2a}}"},
        {"name": "Binomial Theorem", "category": "algebra_trig", "latex": r"({x} + {y})^{{{n}}} = \sum_{{{k}=0}}^{{{n}}} \binom{{{n}}}{{{k}}} {x}^{{{n}-{k}}} {y}^{{{k}}}"},
        {"name": "Arithmetic Series Sum", "category": "algebra_trig", "latex": r"S_{{{n}}} = \frac{{{n}}}{{2}}(a_1 + a_{{{n}}})"},
        {"name": "Geometric Series Sum", "category": "algebra_trig", "latex": r"S_{{{n}}} = \frac{{a_1(1 - r^{{{n}}})}}{{1 - r}}"},
        {"name": "Pythagorean Identity", "category": "algebra_trig", "latex": r"\sin^2 {theta} + \cos^2 {theta} = 1"},
        {"name": "Double Angle Formula", "category": "algebra_trig", "latex": r"\cos(2 {theta}) = \cos^2 {theta} - \sin^2 {theta}"},
        {"name": "Sine Angle Addition", "category": "algebra_trig", "latex": r"\sin(\alpha \pm \beta) = \sin \alpha \cos \beta \pm \cos \alpha \sin \beta"},
        {"name": "Complex Conjugate Product", "category": "algebra_trig", "latex": r"(a + bi)(a - bi) = a^2 + b^2"},
        {"name": "Complex Number Polar Form", "category": "algebra_trig", "latex": r"z = r e^{{i{theta}}},\quad r = |z|"},
    ]


def allocate_category_targets(count: int, ratios: dict[str, float]) -> dict[str, int]:
    # 用 largest remainder 的思路把比例分配成整数目标数。
    # 这样 count=20 之类的小样本时，也能尽量贴近既定领域配额。
    raw_targets = {category: count * ratio for category, ratio in ratios.items()}
    base_targets = {category: int(value) for category, value in raw_targets.items()}
    remainder = count - sum(base_targets.values())

    ranked_remainders = sorted(
        ((raw_targets[category] - base_targets[category], category) for category in ratios),
        reverse=True,
    )
    for _, category in ranked_remainders[:remainder]:
        base_targets[category] += 1
    return base_targets


def parse_category_ratios(raw: Optional[str]) -> dict[str, float]:
    if not raw:
        return DEFAULT_CATEGORY_RATIOS.copy()

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid --category-ratios JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError("--category-ratios must be a JSON object")

    normalized: dict[str, float] = {}
    for category, value in payload.items():
        if category not in DEFAULT_CATEGORY_RATIOS:
            raise ValueError(f"Unknown category in --category-ratios: {category}")
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"Invalid ratio for category {category}: {value}")
        normalized[category] = float(value)

    total = sum(normalized.values())
    if total <= 0:
        raise ValueError("Sum of category ratios must be > 0")

    return {category: normalized.get(category, 0.0) / total for category in DEFAULT_CATEGORY_RATIOS}


def choose_next_category(
    category_targets: dict[str, int],
    category_counts: Counter,
    templates_by_category: dict[str, list[dict[str, str]]],
) -> str:
    # 优先选择“尚未达到配额”的领域。
    deficits: list[tuple[int, str]] = []
    for category, target in category_targets.items():
        current = category_counts[category]
        remaining = target - current
        if remaining > 0 and templates_by_category.get(category):
            deficits.append((remaining, category))

    if deficits:
        max_remaining = max(remaining for remaining, _ in deficits)
        candidates = [category for remaining, category in deficits if remaining == max_remaining]
        return random.choice(candidates)

    # 如果所有领域都满足最低配额，但总数还没够，就退回到全领域随机。
    return random.choice([category for category, items in templates_by_category.items() if items])


def generate_formulas(
    count: int = 1000,
    category_ratios: Optional[dict[str, float]] = None,
) -> list[dict[str, object]]:
    vars_x = ["x", "y", "z", "u", "v", r"\theta", r"\alpha", r"\phi", r"\xi", r"\gamma"]
    vars_n = ["n", "k", "m", "i", "j", "T", "N", "M"]
    vars_mass = ["m", "M", "m_0", "M_0", r"\mu"]
    templates = build_templates()
    category_ratios = category_ratios or DEFAULT_CATEGORY_RATIOS.copy()
    category_targets = allocate_category_targets(count, category_ratios)
    templates_by_category: dict[str, list[dict[str, str]]] = {
        category: [template for template in templates if template["category"] == category]
        for category in category_ratios
    }

    results: list[dict[str, object]] = []
    seen: set[str] = set()
    attempts = 0
    parse_failures = 0
    category_counts: Counter = Counter()

    while len(results) < count and attempts < count * 50:
        attempts += 1
        category = choose_next_category(category_targets, category_counts, templates_by_category)
        template = random.choice(templates_by_category[category])

        vx, vy, vz, vu, vv = random.sample(vars_x, 5)
        vn, vk, vi, vt = random.sample(vars_n, 4)
        m1, m2 = random.sample(vars_mass, 2)

        try:
            latex_str = template["latex"].format(
                x=vx,
                y=vy,
                z=vz,
                u=vu,
                v=vv,
                n=vn,
                k=vk,
                i=vi,
                t=vt,
                theta=random.choice([r"\theta", r"\phi", r"\alpha", r"\omega"]),
                m=random.choice(vars_mass),
                m1=m1,
                m2=m2,
                r=random.choice(["r", "d", "R"]),
                Q=random.choice(["Q", r"\mathbf{Q}"]),
                K=random.choice(["K", r"\mathbf{K}"]),
                V=random.choice(["V", r"\mathbf{V}"]),
                W=random.choice(["W", "U", "V", r"\mathbf{W}"]),
                b=random.choice(["b", "B", r"\beta"]),
                N=random.choice(["N", "M", "T"]),
            )
        except KeyError:
            continue

        if latex_str in seen:
            continue
        seen.add(latex_str)

        sympy_expr, parse_error = safe_latex2sympy_expr(latex_str)
        record: dict[str, object] = {
            "name": template["name"],
            "category": template["category"],
            "standard_latex": latex_str,
            "sympy_expr": sympy_expr,
        }
        if parse_error:
            parse_failures += 1
            record["sympy_error"] = parse_error
            print(f"[WARN] {template['name']} parse failed: {parse_error}", file=sys.stderr)

        results.append(record)
        category_counts[template["category"]] += 1

    print(f"[INFO] parse failures: {parse_failures}/{len(results)}", file=sys.stderr)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--out", default="formulas_dataset_1000.json")
    parser.add_argument(
        "--category-ratios",
        default=None,
        help='JSON object like {"stats_ml":0.3,"calculus":0.25,"physics":0.15,"matrix":0.15,"algebra_trig":0.15}',
    )
    args = parser.parse_args()

    category_ratios = parse_category_ratios(args.category_ratios)
    data = generate_formulas(args.count, category_ratios=category_ratios)
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)

    categories = Counter(item["category"] for item in data)
    print(f"[OK] Generated {len(data)} formulas -> {args.out}")
    print(f"   Distribution: {dict(categories)}")

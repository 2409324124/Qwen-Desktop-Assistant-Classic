"""Formula output form, separate from semantic correctness."""
import re
from .semantics import compare_latex_math_only


def is_output_protocol_compliant(prediction: str) -> bool:
    """Check output form independently of whether it is the correct formula.

    This checks the supported parser/dataset protocol, not arbitrary TeX syntax.
    Ordinary matrices use bmatrix; determinant/norm matrix delimiters retain
    their distinct vmatrix/Vmatrix semantics.
    """
    value = prediction.strip()
    if not value or '$' in value or '```' in value:
        return False
    if re.search(r"\\[\[\]()]|(?<!\\)(?:\\\\)*[_^](?!\{)|\\(?:over|dfrac|tfrac)\b", value) or '/' in value:
        return False
    if re.search(r"\\(?:text|operatorname|mathrm)\{[^{}]*[\s:：][^{}]*\}", value):
        return False
    if '\n' in value and r"\begin" not in value:
        return False
    environments = re.findall(r"\\begin\{([^{}]+)\}", value)
    if any(env not in {'bmatrix', 'vmatrix', 'Vmatrix'} for env in environments):
        return False
    if re.search(r"\b(?:here|formula|result|answer|because|therefore)\b", value, re.IGNORECASE):
        return False
    parsed = compare_latex_math_only(value, value)
    return parsed.parse_success and parsed.math_match


from __future__ import annotations

import re


_GREEK_COMMANDS = (
    "varepsilon",
    "vartheta",
    "varphi",
    "alpha",
    "beta",
    "gamma",
    "delta",
    "epsilon",
    "zeta",
    "eta",
    "theta",
    "iota",
    "kappa",
    "lambda",
    "mu",
    "nu",
    "xi",
    "omicron",
    "rho",
    "sigma",
    "tau",
    "upsilon",
    "phi",
    "chi",
    "psi",
    "omega",
)

_KNOWN_COMMANDS = {
    *(_GREEK_COMMANDS),
    "begin",
    "end",
    "frac",
    "sqrt",
    "sum",
    "prod",
    "int",
    "oint",
    "lim",
    "infty",
    "partial",
    "nabla",
    "Delta",
    "cdot",
    "times",
    "odot",
    "pm",
    "ge",
    "le",
    "neq",
    "approx",
    "to",
    "binom",
    "sin",
    "cos",
    "tan",
    "tanh",
    "log",
    "ln",
    "exp",
    "max",
    "min",
    "det",
    "text",
    "operatorname",
    "mathcal",
    "mathbb",
    "mathbf",
    "boldsymbol",
    "mathrm",
    "mathit",
    "textrm",
    "hat",
    "bar",
    "vec",
    "tilde",
    "dot",
    "ddot",
    "left",
    "right",
}


def _split_unknown_command(command: str) -> str | None:
    for greek in _GREEK_COMMANDS:
        if command == greek:
            return "\\" + greek
        if command.startswith(greek):
            suffix = command[len(greek) :]
            if len(suffix) == 1 and suffix.isascii() and suffix.isalpha():
                return "\\" + greek + " " + suffix
            if suffix in _GREEK_COMMANDS:
                return "\\" + greek + "\\" + suffix
    if len(command) == 1 and command.isascii() and command.isalpha():
        return command
    return None


def _split_bare_greek_words(value: str) -> str:
    greek_pattern = "|".join(sorted(_GREEK_COMMANDS, key=len, reverse=True))

    def split_word(match: re.Match[str]) -> str:
        word = match.group(0)
        parts: list[str] = []
        index = 0
        while index < len(word):
            for greek in _GREEK_COMMANDS:
                if word.startswith(greek, index):
                    parts.append("\\" + greek)
                    index += len(greek)
                    break
            else:
                return word
        return "".join(parts)

    return re.sub(rf"(?<![\\A-Za-z])(?:{greek_pattern})+(?![A-Za-z])", split_word, value)


def _find_matching_brace(value: str, start: int) -> int:
    depth = 0
    for index in range(start, len(value)):
        if value[index] == "{" and (index == 0 or value[index - 1] != "\\"):
            depth += 1
        elif value[index] == "}" and (index == 0 or value[index - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return index
    return -1


def _split_bare_greek_words_outside_text(value: str) -> str:
    parts: list[str] = []
    index = 0
    while index < len(value):
        if value.startswith(r"\text{", index) or value.startswith(r"\operatorname{", index):
            group_start = value.find("{", index)
            group_end = _find_matching_brace(value, group_start)
            if group_start != -1 and group_end != -1:
                parts.append(value[index : group_end + 1])
                index = group_end + 1
                continue
        next_text = min(
            [position for position in (value.find(r"\text{", index), value.find(r"\operatorname{", index)) if position != -1],
            default=len(value),
        )
        parts.append(_split_bare_greek_words(value[index:next_text]))
        index = next_text
    return "".join(parts)


def postprocess_latex(value: str) -> str:
    """Repair common model-only LaTeX command boundary mistakes."""

    parts: list[str] = []
    index = 0
    while index < len(value):
        if value[index] != "\\":
            parts.append(value[index])
            index += 1
            continue
        match = re.match(r"\\([A-Za-z]+)", value[index:])
        if not match:
            parts.append(value[index])
            index += 1
            continue
        command = match.group(1)
        if command in _KNOWN_COMMANDS:
            parts.append(match.group(0))
        else:
            parts.append(_split_unknown_command(command) or match.group(0))
        index += len(match.group(0))
    return _split_bare_greek_words_outside_text("".join(parts))

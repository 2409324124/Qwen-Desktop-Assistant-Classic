from __future__ import annotations

import re
from dataclasses import dataclass


_MATRIX_ENVIRONMENTS = ("matrix", "pmatrix", "Bmatrix", "vmatrix", "Vmatrix")
_SPACING_COMMANDS = (r"\,", r"\;", r"\!", r"\quad", r"\qquad")
_CANONICAL_FONT_COMMANDS = {"mathbf", "boldsymbol", "mathrm", "mathit", "textrm"}


def _find_matching_brace(value: str, start: int) -> int:
    depth = 0
    for index in range(start, len(value)):
        if value[index] == "{" and (index == 0 or value[index - 1] != "\\"):
            depth += 1
        elif value[index] == "}" and (index == 0 or value[index - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return index
    raise ValueError(f"Unbalanced LaTeX group at offset {start}: {value!r}")


def _find_top_level_over(value: str) -> int | None:
    depth = 0
    index = 0
    while index < len(value):
        char = value[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        elif depth == 0 and value.startswith(r"\over", index):
            end = index + len(r"\over")
            if end == len(value) or not value[end].isalpha():
                return index
        index += 1
    return None


def _canonicalize_groups(value: str) -> str:
    parts: list[str] = []
    index = 0
    while index < len(value):
        if value[index] != "{" or (index > 0 and value[index - 1] == "\\"):
            parts.append(value[index])
            index += 1
            continue

        end = _find_matching_brace(value, index)
        content = _canonicalize_groups(value[index + 1 : end]).strip()
        over_index = _find_top_level_over(content)
        if over_index is None:
            parts.append("{" + content + "}")
        else:
            numerator = content[:over_index].strip()
            denominator = content[over_index + len(r"\over") :].strip()
            parts.append(r"\frac{" + numerator + "}{" + denominator + "}")
        index = end + 1
    return "".join(parts)


def _brace_scripts(value: str) -> str:
    pattern = re.compile(r"([_^])(?!\{)(\\[A-Za-z]+|[A-Za-z0-9])")
    previous = None
    while value != previous:
        previous = value
        value = pattern.sub(lambda match: f"{match.group(1)}{{{match.group(2)}}}", value)
    return value


def _unwrap_commands(value: str, commands: set[str]) -> str:
    result: list[str] = []
    index = 0
    while index < len(value):
        if value[index] != "\\":
            result.append(value[index])
            index += 1
            continue
        match = re.match(r"\\([A-Za-z]+)", value[index:])
        if not match:
            result.append(value[index])
            index += 1
            continue
        command = match.group(1)
        command_end = index + len(match.group(0))
        if command in commands and command_end < len(value) and value[command_end] == "{":
            group_end = _find_matching_brace(value, command_end)
            result.append(_unwrap_commands(value[command_end + 1 : group_end], commands))
            index = group_end + 1
            continue
        result.append(match.group(0))
        index = command_end
    return "".join(result)


def canonicalize_latex(value: str, *, strip_font_styles: bool = True) -> str:
    """Return the project's deterministic LaTeX display dialect."""

    normalized = value.strip()
    if strip_font_styles:
        normalized = _unwrap_commands(normalized, _CANONICAL_FONT_COMMANDS)
    normalized = normalized.replace(r"\left", "").replace(r"\right", "")
    for command in _SPACING_COMMANDS:
        normalized = normalized.replace(command, " ")
    for environment in _MATRIX_ENVIRONMENTS:
        normalized = normalized.replace(rf"\begin{{{environment}}}", r"\begin{bmatrix}")
        normalized = normalized.replace(rf"\end{{{environment}}}", r"\end{bmatrix}")
    normalized = _canonicalize_groups(normalized)
    normalized = _brace_scripts(normalized)
    normalized = re.sub(r"[ \t\r\f\v]+", " ", normalized)
    normalized = re.sub(r"\s*\\\\\s*", lambda _: " \\\\ ", normalized)
    normalized = normalized.strip()
    return normalized


@dataclass(frozen=True)
class LatexNode:
    kind: str
    value: str = ""
    children: tuple["LatexNode", ...] = ()


@dataclass(frozen=True)
class LatexComparison:
    exact_match: bool
    canonical_match: bool
    symbol_fidelity_match: bool
    semantic_match: bool
    parse_success: bool
    match_level: str
    reason: str


@dataclass(frozen=True)
class LatexMathComparison:
    math_match: bool
    format_compliant: bool
    parse_success: bool
    match_level: str
    reason: str


_STYLE_COMMANDS = {"mathbf", "boldsymbol", "mathrm", "mathcal", "mathbb", "mathit", "textrm"}
_MODIFIER_COMMANDS = {"hat", "bar", "vec", "tilde", "dot", "ddot"}
_GREEK_VARIABLES = {
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta", "eta", "theta",
    "vartheta", "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "rho",
    "sigma", "tau", "upsilon", "phi", "varphi", "chi", "psi", "omega",
}
_FIXED_COMMANDS = {
    "sum", "prod", "int", "oint", "lim", "infty", "partial", "nabla", "Delta", "cdot",
    "times", "odot", "pm", "ge", "le", "neq", "approx", "to", "sqrt", "frac", "binom",
    "sin", "cos", "tan", "tanh", "log", "ln", "exp", "max", "min", "det",
}
_NONCOMMUTATIVE_FAMILIES = {
    "Self-Attention Mechanism",
    "Linear Layer with Activation",
    "RNN Hidden State Update",
    "Eigenvalue Equation",
    "Schrodinger Equation",
}


def _unwrap_style_commands(value: str) -> str:
    result: list[str] = []
    index = 0
    while index < len(value):
        if value[index] != "\\":
            result.append(value[index])
            index += 1
            continue
        match = re.match(r"\\([A-Za-z]+)", value[index:])
        if not match:
            result.append(value[index])
            index += 1
            continue
        command = match.group(1)
        command_end = index + len(match.group(0))
        if command in _STYLE_COMMANDS and command_end < len(value) and value[command_end] == "{":
            group_end = _find_matching_brace(value, command_end)
            result.append(_unwrap_style_commands(value[command_end + 1 : group_end]))
            index = group_end + 1
            continue
        result.append(match.group(0))
        index = command_end
    return "".join(result)


Token = tuple[str, str]


def _tokenize(value: str) -> list[Token]:
    value = _unwrap_style_commands(canonicalize_latex(value))
    tokens: list[Token] = []
    index = 0
    while index < len(value):
        if value[index].isspace():
            index += 1
            continue
        if value.startswith(r"\begin{bmatrix}", index):
            tokens.append(("BEGIN_MATRIX", "bmatrix"))
            index += len(r"\begin{bmatrix}")
            continue
        if value.startswith(r"\end{bmatrix}", index):
            tokens.append(("END_MATRIX", "bmatrix"))
            index += len(r"\end{bmatrix}")
            continue
        if value.startswith(r"\\", index):
            tokens.append(("ROW", r"\\"))
            index += 2
            continue
        char = value[index]
        if char == "\\":
            match = re.match(r"\\([A-Za-z]+)", value[index:])
            if match:
                command = match.group(1)
                index += len(match.group(0))
                if command in {"text", "operatorname"} and index < len(value) and value[index] == "{":
                    group_end = _find_matching_brace(value, index)
                    name = re.sub(r"\s+", "", value[index + 1 : group_end]).lower()
                    tokens.append(("NAME", "@" + name))
                    index = group_end + 1
                else:
                    tokens.append(("COMMAND", command))
                continue
            if index + 1 < len(value):
                tokens.append(("SYMBOL", value[index + 1]))
                index += 2
                continue
        if char.isdigit():
            end = index + 1
            while end < len(value) and (value[end].isdigit() or value[end] == "."):
                end += 1
            tokens.append(("NUMBER", value[index:end]))
            index = end
            continue
        if char.isalpha():
            tokens.append(("SYMBOL", char))
            index += 1
            continue
        tokens.append((char, char))
        index += 1
    return tokens


class _LatexParser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0

    def parse(self) -> LatexNode:
        if not self.tokens:
            raise ValueError("Empty LaTeX expression")
        node = self._parse_sequence()
        if self.index != len(self.tokens):
            remaining = " ".join(value for _, value in self.tokens[self.index :])
            raise ValueError(f"Unexpected LaTeX tokens: {remaining}")
        return node

    def _parse_sequence(self) -> LatexNode:
        expressions = [self._parse_relation()]
        while self._peek_kind() == ",":
            self._consume(",")
            expressions.append(self._parse_relation())
        return expressions[0] if len(expressions) == 1 else LatexNode("sequence", children=tuple(expressions))

    def _peek_kind(self) -> str | None:
        return self.tokens[self.index][0] if self.index < len(self.tokens) else None

    def _peek_value(self) -> str | None:
        return self.tokens[self.index][1] if self.index < len(self.tokens) else None

    def _consume(self, kind: str | None = None) -> Token:
        if self.index >= len(self.tokens):
            raise ValueError("Unexpected end of LaTeX expression")
        token = self.tokens[self.index]
        if kind is not None and token[0] != kind:
            raise ValueError(f"Expected {kind}, found {token[0]} ({token[1]!r})")
        self.index += 1
        return token

    def _parse_relation(self) -> LatexNode:
        left = self._parse_addition()
        relations: list[LatexNode] = [left]
        operators: list[str] = []
        while self._peek_kind() == "=" or (
            self._peek_kind() == "COMMAND" and self._peek_value() in {"ge", "le", "neq", "approx", "to"}
        ):
            operators.append(self._consume()[1])
            relations.append(self._parse_addition())
        if not operators:
            return left
        if len(operators) == 1:
            return LatexNode("relation", operators[0], tuple(relations))
        return LatexNode(
            "and",
            children=tuple(
                LatexNode("relation", operator, (relations[position], relations[position + 1]))
                for position, operator in enumerate(operators)
            ),
        )

    def _parse_addition(self) -> LatexNode:
        node = self._parse_multiplication()
        while self._peek_kind() in {"+", "-"}:
            operator = self._consume()[0]
            right = self._parse_multiplication()
            if operator == "-":
                right = LatexNode("neg", children=(right,))
            node = LatexNode("add", children=(node, right))
        return node

    def _parse_multiplication(self) -> LatexNode:
        node = self._parse_unary()
        while True:
            if self._peek_kind() in {"*", "/"}:
                operator = self._consume()[0]
                right = self._parse_unary()
                node = LatexNode("mul" if operator == "*" else "div", children=(node, right))
                continue
            if self._peek_kind() == "COMMAND" and self._peek_value() in {"cdot", "times", "odot"}:
                operator = self._consume()[1]
                right = self._parse_unary()
                node = LatexNode("mul", operator, (node, right))
                continue
            if self._starts_primary():
                node = LatexNode("mul", children=(node, self._parse_unary()))
                continue
            return node

    def _parse_unary(self) -> LatexNode:
        if self._peek_kind() == "+":
            self._consume("+")
            return self._parse_unary()
        if self._peek_kind() == "-":
            self._consume("-")
            return LatexNode("neg", children=(self._parse_unary(),))
        return self._parse_power()

    def _parse_power(self) -> LatexNode:
        node = self._parse_primary()
        subscript: LatexNode | None = None
        superscript: LatexNode | None = None
        while self._peek_kind() in {"_", "^"}:
            operator = self._consume()[0]
            argument = self._parse_script_argument()
            if operator == "_":
                subscript = argument
            else:
                superscript = argument
        if subscript is not None or superscript is not None:
            node = LatexNode(
                "scripts",
                children=(node, subscript or LatexNode("empty"), superscript or LatexNode("empty")),
            )
        while self._peek_kind() in {"'", "!"}:
            operator = self._consume()[0]
            node = LatexNode("prime" if operator == "'" else "factorial", children=(node,))
        return node

    def _parse_script_argument(self) -> LatexNode:
        if self._peek_kind() == "{":
            return self._parse_group()
        return self._parse_primary()

    def _parse_group(self) -> LatexNode:
        self._consume("{")
        node = self._parse_sequence()
        self._consume("}")
        return node

    def _parse_primary(self) -> LatexNode:
        kind = self._peek_kind()
        value = self._peek_value()
        if kind in {"NUMBER", "SYMBOL", "NAME"}:
            self._consume()
            return LatexNode("number" if kind == "NUMBER" else "symbol", value or "")
        if kind == "COMMAND":
            command = self._consume()[1]
            if command == "frac":
                return LatexNode("div", children=(self._parse_group(), self._parse_group()))
            if command == "sqrt":
                return LatexNode("sqrt", children=(self._parse_group(),))
            if command == "binom":
                return LatexNode("binom", children=(self._parse_group(), self._parse_group()))
            if command in _MODIFIER_COMMANDS:
                argument = self._parse_group() if self._peek_kind() == "{" else self._parse_primary()
                return LatexNode("modifier", command, (argument,))
            return LatexNode("symbol", "\\" + command)
        if kind in {"{", "(", "["}:
            opening = self._consume()[0]
            closing = {"{": "}", "(": ")", "[": "]"}[opening]
            node = self._parse_sequence()
            self._consume(closing)
            return node
        if kind == "|":
            self._consume("|")
            return LatexNode("symbol", "|")
        if kind == "BEGIN_MATRIX":
            return self._parse_matrix()
        raise ValueError(f"Expected expression, found {kind} ({value!r})")

    def _parse_matrix(self) -> LatexNode:
        self._consume("BEGIN_MATRIX")
        rows: list[LatexNode] = []
        entries: list[LatexNode] = []
        while self._peek_kind() != "END_MATRIX":
            entries.append(self._parse_relation())
            if self._peek_kind() == "&":
                self._consume("&")
                continue
            if self._peek_kind() == "ROW":
                self._consume("ROW")
                rows.append(LatexNode("row", children=tuple(entries)))
                entries = []
                continue
            if self._peek_kind() != "END_MATRIX":
                raise ValueError(f"Unexpected matrix token: {self._peek_value()!r}")
        self._consume("END_MATRIX")
        rows.append(LatexNode("row", children=tuple(entries)))
        return LatexNode("matrix", children=tuple(rows))

    def _starts_primary(self) -> bool:
        return self._peek_kind() in {"NUMBER", "SYMBOL", "NAME", "COMMAND", "{", "(", "[", "|", "BEGIN_MATRIX"}


def parse_latex(value: str) -> LatexNode:
    return _normalize_ast(_LatexParser(_tokenize(value)).parse())


def _normalize_ast(node: LatexNode) -> LatexNode:
    children = tuple(_normalize_ast(child) for child in node.children)
    if node.kind in {"add", "mul"}:
        flattened: list[LatexNode] = []
        for child in children:
            if child.kind == node.kind and child.value == node.value:
                flattened.extend(child.children)
            else:
                flattened.append(child)
        return LatexNode(node.kind, node.value, tuple(flattened))
    if node.kind == "neg" and children and children[0].kind == "neg":
        return children[0].children[0]
    return LatexNode(node.kind, node.value, children)


def _renamable_symbol(value: str) -> bool:
    if value.startswith("\\"):
        return value[1:] in _GREEK_VARIABLES
    if value.startswith("@"):
        return False
    return bool(re.fullmatch(r"[A-Za-z]", value))


def _equivalent(
    left: LatexNode,
    right: LatexNode,
    *,
    allow_rename: bool,
    commutative_multiplication: bool,
    mapping: dict[str, str],
    reverse: dict[str, str],
) -> tuple[bool, dict[str, str], dict[str, str]]:
    if left.kind != right.kind:
        return False, mapping, reverse
    if left.kind == "symbol":
        if allow_rename and _renamable_symbol(left.value) and _renamable_symbol(right.value):
            if left.value in mapping:
                return mapping[left.value] == right.value, mapping, reverse
            if right.value in reverse:
                return False, mapping, reverse
            mapping = dict(mapping)
            reverse = dict(reverse)
            mapping[left.value] = right.value
            reverse[right.value] = left.value
            return True, mapping, reverse
        return left.value == right.value, mapping, reverse
    if left.value != right.value:
        return False, mapping, reverse
    if left.kind in {"number", "empty"}:
        return left.value == right.value, mapping, reverse
    if left.kind == "relation" and left.value == "=" and len(left.children) == 2:
        direct = _equivalent_children(left.children, right.children, allow_rename, commutative_multiplication, mapping, reverse)
        if direct[0]:
            return direct
        return _equivalent_children(
            left.children,
            tuple(reversed(right.children)),
            allow_rename,
            commutative_multiplication,
            mapping,
            reverse,
        )
    if (
        left.kind == "scripts"
        and len(left.children) == 3
        and len(right.children) == 3
        and left.children[2].kind == "number"
        and right.children[2].kind == "number"
        and left.children[2].value == right.children[2].value
    ):
        try:
            even_power = int(left.children[2].value) % 2 == 0
        except ValueError:
            even_power = False
        if even_power:
            direct = _equivalent_children(
                left.children,
                right.children,
                allow_rename,
                commutative_multiplication,
                mapping,
                reverse,
            )
            if direct[0]:
                return direct
            flipped_right = (
                _negate_expression(right.children[0]),
                right.children[1],
                right.children[2],
            )
            return _equivalent_children(
                left.children,
                flipped_right,
                allow_rename,
                commutative_multiplication,
                mapping,
                reverse,
            )
    commutative = left.kind == "add" or (left.kind == "mul" and commutative_multiplication)
    if commutative:
        return _equivalent_commutative(
            left.children,
            right.children,
            allow_rename,
            commutative_multiplication,
            mapping,
            reverse,
        )
    return _equivalent_children(
        left.children,
        right.children,
        allow_rename,
        commutative_multiplication,
        mapping,
        reverse,
    )


def _negate_expression(node: LatexNode) -> LatexNode:
    if node.kind == "neg":
        return node.children[0]
    if node.kind == "add":
        return LatexNode("add", children=tuple(_negate_expression(child) for child in node.children))
    return LatexNode("neg", children=(node,))


def _equivalent_children(
    left: tuple[LatexNode, ...],
    right: tuple[LatexNode, ...],
    allow_rename: bool,
    commutative_multiplication: bool,
    mapping: dict[str, str],
    reverse: dict[str, str],
) -> tuple[bool, dict[str, str], dict[str, str]]:
    if len(left) != len(right):
        return False, mapping, reverse
    mapping = dict(mapping)
    reverse = dict(reverse)
    for left_child, right_child in zip(left, right):
        matched, mapping, reverse = _equivalent(
            left_child,
            right_child,
            allow_rename=allow_rename,
            commutative_multiplication=commutative_multiplication,
            mapping=mapping,
            reverse=reverse,
        )
        if not matched:
            return False, mapping, reverse
    return True, mapping, reverse


def _equivalent_commutative(
    left: tuple[LatexNode, ...],
    right: tuple[LatexNode, ...],
    allow_rename: bool,
    commutative_multiplication: bool,
    mapping: dict[str, str],
    reverse: dict[str, str],
) -> tuple[bool, dict[str, str], dict[str, str]]:
    if len(left) != len(right):
        return False, mapping, reverse

    def search(
        position: int,
        remaining: tuple[int, ...],
        current_mapping: dict[str, str],
        current_reverse: dict[str, str],
    ) -> tuple[bool, dict[str, str], dict[str, str]]:
        if position == len(left):
            return True, current_mapping, current_reverse
        for candidate in remaining:
            matched, next_mapping, next_reverse = _equivalent(
                left[position],
                right[candidate],
                allow_rename=allow_rename,
                commutative_multiplication=commutative_multiplication,
                mapping=dict(current_mapping),
                reverse=dict(current_reverse),
            )
            if matched:
                result = search(
                    position + 1,
                    tuple(index for index in remaining if index != candidate),
                    next_mapping,
                    next_reverse,
                )
                if result[0]:
                    return result
        return False, current_mapping, current_reverse

    return search(0, tuple(range(len(right))), dict(mapping), dict(reverse))


def _ast_equal(left: LatexNode, right: LatexNode, *, allow_rename: bool, formula_name: str | None) -> bool:
    matched, _, _ = _equivalent(
        left,
        right,
        allow_rename=allow_rename,
        commutative_multiplication=formula_name not in _NONCOMMUTATIVE_FAMILIES,
        mapping={},
        reverse={},
    )
    return matched


def _format_key(value: str, *, ignore_style: bool) -> str:
    if ignore_style:
        value = _unwrap_style_commands(value)
    return re.sub(r"\s+", "", canonicalize_latex(value, strip_font_styles=ignore_style))


def _strip_display_math(value: str) -> str:
    stripped = value.strip()
    if stripped.startswith(r"\[") and stripped.endswith(r"\]"):
        return stripped[2:-2].strip()
    if stripped.startswith("$$") and stripped.endswith("$$"):
        return stripped[2:-2].strip()
    return stripped


def _replace_exp_calls(value: str) -> str:
    previous = None
    while value != previous:
        previous = value
        value = re.sub(r"\\exp\s*\(([^()]*)\)", lambda match: f"e^{{{match.group(1).strip()}}}", value)
        value = re.sub(r"\\exp\s*\{([^{}]*)\}", lambda match: f"e^{{{match.group(1).strip()}}}", value)
    return value


def _normalize_math_latex(value: str) -> str:
    normalized = _strip_display_math(value)
    normalized = normalized.replace(r"\geq", r"\ge").replace(r"\leq", r"\le")
    normalized = normalized.replace(r"\mathrm{d}", "d").replace(r"\operatorname{d}", "d")
    normalized = normalized.replace(r"^{\prime}", "'").replace(r"^\prime", "'").replace(r"\prime", "'")
    normalized = normalized.replace(r"\operatorname", r"\text")
    normalized = re.sub(r"\\mathrm\{([A-Za-z][A-Za-z ]+)\}", r"\\text{\1}", normalized)
    normalized = _replace_exp_calls(normalized)
    return normalized


def _find_top_level_equals(value: str) -> int | None:
    depth = 0
    index = 0
    while index < len(value):
        char = value[index]
        if char in "{[(":
            depth += 1
        elif char in "}])" and depth > 0:
            depth -= 1
        elif char == "=" and depth == 0:
            return index
        index += 1
    return None


def _relation_sides(value: str) -> tuple[str, str] | None:
    index = _find_top_level_equals(value)
    if index is None:
        return None
    left = value[:index].strip()
    right = value[index + 1 :].strip()
    if not left or not right:
        return None
    return left, right


def _text_group_at_start(value: str) -> tuple[str, int] | None:
    stripped = value.lstrip()
    offset = len(value) - len(stripped)
    for command in (r"\text", r"\operatorname", r"\mathrm"):
        prefix = command + "{"
        if stripped.startswith(prefix):
            group_start = offset + len(command)
            group_end = _find_matching_brace(value, group_start)
            return value[group_start + 1 : group_end], group_end + 1
    return None


def _prediction_candidates(value: str) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []

    def add(candidate: str, reason: str) -> None:
        candidate = candidate.strip()
        if candidate and candidate not in {existing for existing, _ in candidates}:
            candidates.append((candidate, reason))

    stripped = _strip_display_math(value)
    add(stripped, "math_equivalent")
    for line in stripped.splitlines():
        add(line, "contains_correct_formula")

    text_group = _text_group_at_start(stripped)
    if text_group is not None:
        text, end = text_group
        rest = stripped[end:].strip()
        if text.rstrip().endswith(":"):
            add(rest, "contains_correct_formula")
        if rest.startswith("="):
            add(rest[1:].strip(), "contains_correct_formula")

    relation = _relation_sides(stripped)
    if relation is not None:
        left, right = relation
        if re.fullmatch(r"\\(?:text|operatorname|mathrm)\{[^{}]+\}", left.strip()):
            add(right, "contains_correct_formula")
        if left.strip().startswith(r"\text{") and ":" in left:
            add(right, "contains_correct_formula")

    return candidates


def _input_has_explicit_variables(input_text: str) -> bool:
    if re.search(r"[A-Za-z]\\?_[A-Za-z0-9]", input_text):
        return True
    if re.search(r"\b(?:alpha|beta|gamma|delta|epsilon|theta|lambda|mu|xi|rho|sigma|phi|psi|omega|hbar)\b", input_text):
        return True
    if re.search(r"\b[A-Za-z][0-9]\b", input_text):
        return True
    if re.search(r"\b[A-Za-z]\s*(?:=|\\+|-|\*|/|\^|prime|hat|bar)", input_text):
        return True
    return False


def _math_ast_match(expected: str, prediction: str, *, allow_rename: bool, formula_name: str | None) -> bool:
    expected_ast = _normalize_math_ast(parse_latex(_normalize_math_latex(expected)))
    prediction_ast = _normalize_math_ast(parse_latex(_normalize_math_latex(prediction)))
    if _ast_equal(expected_ast, prediction_ast, allow_rename=False, formula_name=formula_name):
        return True
    return allow_rename and _ast_equal(expected_ast, prediction_ast, allow_rename=True, formula_name=formula_name)


def _normalize_math_ast(node: LatexNode) -> LatexNode:
    children = tuple(_normalize_math_ast(child) for child in node.children)
    normalized = LatexNode(node.kind, node.value, children)
    if normalized.kind == "div" and len(normalized.children) == 2:
        numerator, denominator = normalized.children
        inverse = LatexNode("reciprocal", children=(denominator,))
        if numerator.kind == "mul":
            return LatexNode("mul", children=(*numerator.children, inverse))
        return LatexNode("mul", children=(numerator, inverse))
    if normalized.kind == "mul":
        flattened: list[LatexNode] = []
        for child in normalized.children:
            if child.kind == "mul":
                flattened.extend(child.children)
            else:
                flattened.append(child)
        return LatexNode("mul", children=tuple(flattened))
    return normalized


def _math_format_key(value: str) -> str:
    normalized = _normalize_math_latex(value)
    normalized = normalized.replace(r"\cdot", "").replace(r"\times", "")
    normalized = normalized.replace(r"\,", "").replace(r"\;", "").replace(r"\quad", "")
    normalized = normalized.replace(r"\left", "").replace(r"\right", "")
    normalized = normalized.replace(r"\mathrm", r"\text").replace(r"\operatorname", r"\text")
    normalized = re.sub(r"\s+", "", canonicalize_latex(normalized, strip_font_styles=True))
    return normalized


def compare_latex_math_only(
    expected: str,
    prediction: str,
    *,
    formula_name: str | None = None,
    input_text: str = "",
) -> LatexMathComparison:
    strict = compare_latex(expected, prediction, formula_name=formula_name)
    if strict.semantic_match:
        return LatexMathComparison(True, strict.symbol_fidelity_match, strict.parse_success, strict.match_level, strict.reason)

    allow_rename = not _input_has_explicit_variables(input_text)
    expected_candidates: list[tuple[str, str]] = [(expected, "math_equivalent")]
    relation = _relation_sides(expected)
    if relation is not None:
        _, expected_right = relation
        if expected_right.startswith(r"\begin{bmatrix}"):
            expected_candidates.append((expected_right, "contains_correct_formula"))

    parse_error: str | None = None
    for expected_candidate, expected_reason in expected_candidates:
        expected_normalized = _normalize_math_latex(expected_candidate)
        for prediction_candidate, prediction_reason in _prediction_candidates(prediction):
            prediction_normalized = _normalize_math_latex(prediction_candidate)
            if _math_format_key(expected_normalized) == _math_format_key(prediction_normalized):
                level = "math_equivalent" if expected_reason == prediction_reason == "math_equivalent" else "contains_correct_formula"
                return LatexMathComparison(True, False, True, level, level)
            try:
                if _math_ast_match(
                    expected_normalized,
                    prediction_normalized,
                    allow_rename=allow_rename,
                    formula_name=formula_name,
                ):
                    level = "math_equivalent" if expected_reason == prediction_reason == "math_equivalent" else "contains_correct_formula"
                    return LatexMathComparison(True, False, True, level, level)
            except ValueError as exc:
                parse_error = str(exc)

    if parse_error is not None:
        return LatexMathComparison(False, False, False, "parse_error", parse_error)
    return LatexMathComparison(False, False, True, "math_mismatch", "math_mismatch")


def compare_latex(expected: str, prediction: str, *, formula_name: str | None = None) -> LatexComparison:
    exact = prediction.strip() == expected.strip()
    canonical = _format_key(expected, ignore_style=False) == _format_key(prediction, ignore_style=False)
    style_insensitive = _format_key(expected, ignore_style=True) == _format_key(prediction, ignore_style=True)
    try:
        expected_ast = parse_latex(expected)
        prediction_ast = parse_latex(prediction)
    except ValueError as exc:
        return LatexComparison(exact, canonical, False, False, False, "parse_error", str(exc))

    symbol_fidelity = _ast_equal(expected_ast, prediction_ast, allow_rename=False, formula_name=formula_name)
    semantic = symbol_fidelity or _ast_equal(expected_ast, prediction_ast, allow_rename=True, formula_name=formula_name)
    if exact:
        level = "exact"
    elif canonical:
        level = "canonical"
    elif style_insensitive:
        level = "style_only"
    elif symbol_fidelity:
        level = "commutative_reorder"
    elif semantic:
        level = "alpha_rename"
    else:
        level = "true_mismatch"
    return LatexComparison(exact, canonical, symbol_fidelity, semantic, True, level, level)

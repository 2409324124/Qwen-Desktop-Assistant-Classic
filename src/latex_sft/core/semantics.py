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


def canonicalize_latex_faithful(value: str) -> str:
    """Normalize the output dialect without erasing symbol/type/operator meaning.

    Font commands, determinant/norm environments, explicit products and all
    operand groups survive. The legacy canonicalizer remains historical only.
    """
    normalized = value.strip()
    normalized = re.sub(r"\\(?:left|right)\b", '', normalized)
    for command in _SPACING_COMMANDS:
        if command[-1].isalpha():
            normalized = re.sub(re.escape(command) + r"\b", ' ', normalized)
        else:
            normalized = normalized.replace(command, ' ')
    for environment in ('matrix', 'pmatrix', 'Bmatrix'):
        normalized = normalized.replace(rf"\begin{{{environment}}}", r"\begin{bmatrix}")
        normalized = normalized.replace(rf"\end{{{environment}}}", r"\end{bmatrix}")
    normalized = _brace_scripts(_canonicalize_groups(normalized))
    normalized = re.sub(r"[ \t\r\f\v]+", ' ', normalized)
    normalized = re.sub(r"\s*\\\\\s*", lambda _: " \\\\ ", normalized)
    return normalized.strip()


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
    verification_status: str = "verified"


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


def _tokenize(value: str, *, faithful: bool = False) -> list[Token]:
    value = canonicalize_latex_faithful(value) if faithful else canonicalize_latex(value)
    if not faithful:
        value = _unwrap_style_commands(value)
    tokens: list[Token] = []
    index = 0
    while index < len(value):
        if value[index].isspace():
            index += 1
            continue
        matrix = re.match(r"\\(begin|end)\{(bmatrix|vmatrix|Vmatrix)\}", value[index:])
        if matrix:
            tokens.append(("BEGIN_MATRIX" if matrix[1] == "begin" else "END_MATRIX", matrix[2]))
            index += len(matrix[0])
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
                    name = re.sub(r"\s+", "", value[index + 1 : group_end])
                    if not faithful:
                        name = name.lower()
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
    def __init__(self, tokens: list[Token], *, faithful: bool = False):
        self.tokens = tokens
        self.index = 0
        self.faithful = faithful

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
            if self.faithful and ((operator == "_" and subscript is not None) or (operator == "^" and superscript is not None)):
                raise ValueError("Repeated script changes or invalidates the expression")
            if operator == "_":
                subscript = argument
            else:
                superscript = argument
        if subscript is not None or superscript is not None:
            node = LatexNode(
                "scripts",
                children=(node, subscript or LatexNode("empty"), superscript or LatexNode("empty")),
            )
        if self.faithful and node.kind == "scripts" and node.children[0].value in {r"\sum", r"\prod", r"\lim"}:
            lower = node.children[1]
            if node.children[0].value == r"\lim" and (lower.kind != "relation" or lower.value != "to" or len(lower.children) != 2):
                raise ValueError("Unsupported limit-variable declaration")
            variable = lower.children[0] if lower.kind == "relation" else lower
            if variable.kind != "symbol" or not _renamable_symbol(variable.value):
                raise ValueError("Unsupported bound-variable declaration")
            body = self._parse_multiplication()
            return LatexNode("binder", variable.value, (node.children[0], lower, node.children[2], body))
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
            if self.faithful and command in _STYLE_COMMANDS:
                return LatexNode("style", command, (self._parse_group(),))
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
        environment = self._consume("BEGIN_MATRIX")[1]
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
        if self._consume("END_MATRIX")[1] != environment:
            raise ValueError("Mismatched matrix environment")
        rows.append(LatexNode("row", children=tuple(entries)))
        if self.faithful and len({len(row.children) for row in rows}) != 1:
            raise ValueError("Matrix rows must have equal widths")
        return LatexNode("matrix", environment, tuple(rows))

    def _starts_primary(self) -> bool:
        if self.faithful and self._peek_kind() == "COMMAND" and self._peek_value() in {"ge", "le", "neq", "approx", "to"}:
            return False
        return self._peek_kind() in {"NUMBER", "SYMBOL", "NAME", "COMMAND", "{", "(", "[", "|", "BEGIN_MATRIX"}


def parse_latex(value: str) -> LatexNode:
    return _normalize_ast(_LatexParser(_tokenize(value)).parse())


def _normalize_ast(node: LatexNode, *, faithful: bool = False) -> LatexNode:
    children = tuple(_normalize_ast(child, faithful=faithful) for child in node.children)
    if node.kind == "add" or (node.kind == "mul" and not (faithful and node.value)):
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
    commutative = left.kind == "add" or (left.kind == "mul" and commutative_multiplication and left.value not in {"times", "odot"})
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


def _faithful_ast(value: str) -> LatexNode:
    # Parsing binds only a declared index within its operator's operand. Free
    # symbols, including e/i, never participate in the historical rename map.
    tree = _normalize_ast(_LatexParser(_tokenize(_normalize_math_latex(value), faithful=True), faithful=True).parse(), faithful=True)

    def bind(node: LatexNode, scope: tuple[str, ...] = ()) -> LatexNode:
        if node.kind == "symbol" and node.value in scope:
            return LatexNode("symbol", "@bound:" + str(scope[::-1].index(node.value)))
        if node.kind == "binder":
            operator, lower, upper, body = node.children
            local = (*scope, node.value)
            # Initialization/bound expressions stay in the enclosing scope.
            if lower.kind == "relation":
                lower = LatexNode("relation", lower.value, (bind(lower.children[0], local), bind(lower.children[1], scope)))
            else:
                lower = bind(lower, local)
            return LatexNode("binder", children=(operator, lower, bind(upper, scope), bind(body, local)))
        children = tuple(bind(child, scope) for child in node.children)
        result = LatexNode(node.kind, node.value, children)
        if node.kind == "style" and node.value in {"mathrm", "mathit", "textrm"}:
            return children[0]
        if node.kind == "div" and children[1].kind == "number":
            result = LatexNode("mul", children=(children[0], LatexNode("reciprocal", children=(children[1],))))
        if result.kind == "mul" and not result.value:
            flattened = []
            for child in result.children:
                if child.kind == "mul" and not child.value:
                    flattened.extend(child.children)
                else:
                    flattened.append(child)
            scalars = [child for child in flattened if child.kind == "number" or (child.kind == "reciprocal" and child.children[0].kind == "number")]
            others = [child for child in flattened if child not in scalars]
            result = LatexNode("mul", children=tuple(sorted(scalars, key=repr) + others))
        return result

    return bind(tree)


# These two task families declare scalar force magnitudes, masses/charges and
# distances. Do not infer scalar types from bare letters in arbitrary formulas.
_SCALAR_FRACTION_FORMULAS = {"Coulomb's Law", "Newton's Law of Universal Gravitation"}


def _regroup_scalar_fraction(node: LatexNode) -> LatexNode:
    """Move factors into one numerator without cancellation or domain changes.

    Called only in the explicit scalar-family context above. Unsupported types,
    binders, explicit product operators and nested quotients are left untouched.
    This normalization is evaluation-only; grouping signatures remain frozen.
    """
    def scalar_polynomial(part: LatexNode) -> bool:
        if part.kind in {"number", "symbol", "empty"}:
            return True
        if part.kind not in {"scripts", "neg", "add", "mul"}:
            return False
        if part.kind == "mul" and part.value:
            return False
        return all(scalar_polynomial(child) for child in part.children)

    children = tuple(_regroup_scalar_fraction(child) for child in node.children)
    result = LatexNode(node.kind, node.value, children)
    if node.kind != "mul" or node.value:
        return result
    fractions = [child for child in children if child.kind == "div"]
    if len(fractions) != 1:
        return result
    fraction = fractions[0]
    if not all(scalar_polynomial(part) for part in fraction.children):
        return result
    if not all(child is fraction or scalar_polynomial(child) for child in children):
        return result
    numerator = LatexNode("mul", children=tuple(
        fraction.children[0] if child is fraction else child for child in children
    ))
    # Retain the exact denominator: x/x must not become 1, and d^2 must not
    # become another power or lose its nonzero-domain restriction.
    return LatexNode("div", children=(
        _normalize_ast(numerator, faithful=True), fraction.children[1],
    ))


_SCALAR_FORMULAS = {"Product Rule", "Mean Squared Error", "Coulomb's Law", "Normal Distribution PDF", "Softmax Function"}


def compare_latex_math_only(
    expected: str,
    prediction: str,
    *,
    formula_name: str | None = None,
    input_text: str = "",
) -> LatexMathComparison:
    """Verify the complete expression, preserving free symbols and scope.

    Unsupported or unmatched expressions are unverified, not proven incorrect.
    input_text remains accepted for API compatibility; it cannot authorize renaming.
    """
    candidate = _strip_display_math(prediction)
    prefixed = False
    try:
        text_group = _text_group_at_start(candidate)
        if text_group is not None and text_group[0].rstrip().endswith(":"):
            candidate = candidate[text_group[1]:].strip()
            prefixed = True
        left, right = _faithful_ast(expected), _faithful_ast(candidate)
        if formula_name in _SCALAR_FRACTION_FORMULAS:
            left, right = _regroup_scalar_fraction(left), _regroup_scalar_fraction(right)
    except (ValueError, IndexError, RecursionError) as exc:
        return LatexMathComparison(False, False, False, "parse_error", str(exc), "unverified")
    matched, _, _ = _equivalent(
        left, right, allow_rename=False,
        commutative_multiplication=formula_name in _SCALAR_FORMULAS,
        mapping={}, reverse={},
    )
    if not matched:
        return LatexMathComparison(False, False, True, "math_mismatch", "Equivalence was not established under symbol/type/scope-preserving rules", "unverified")
    strict = compare_latex(expected, prediction, formula_name=formula_name)
    format_compliant = strict.symbol_fidelity_match and not prefixed
    level = "contains_correct_formula" if prefixed else (strict.match_level if format_compliant else "math_equivalent")
    return LatexMathComparison(True, format_compliant, True, level, level)


def compare_latex(expected: str, prediction: str, *, formula_name: str | None = None) -> LatexComparison:
    exact = prediction.strip() == expected.strip()
    try:
        canonical = _format_key(expected, ignore_style=False) == _format_key(prediction, ignore_style=False)
        style_insensitive = _format_key(expected, ignore_style=True) == _format_key(prediction, ignore_style=True)
        expected_ast = parse_latex(expected)
        prediction_ast = parse_latex(prediction)
    except ValueError as exc:
        return LatexComparison(exact, False, False, False, False, "parse_error", str(exc))

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


# Public parser vocabulary and structural-analysis hooks. These do not permit
# free-variable renaming in the faithful scoring API.
FIXED_COMMANDS = frozenset(_FIXED_COMMANDS)
GREEK_VARIABLES = frozenset(_GREEK_VARIABLES)


def parse_latex_faithful(value: str) -> LatexNode:
    """Parse a complete formula preserving symbols, operators and binder scope."""
    return _faithful_ast(value)


def is_renamable_symbol(value: str) -> bool:
    """Whether a symbol may be abstracted for grouping (never scoring)."""
    return _renamable_symbol(value)

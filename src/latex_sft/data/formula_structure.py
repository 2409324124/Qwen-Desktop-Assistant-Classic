"""Conservative structural identities for dataset grouping, never model scoring.

Free-variable renaming is a consistent bijection by first occurrence. Declared
bound variables use the faithful parser's local de Bruijn identities. Explicit
operators, operand order, variable repetition and all complete-expression nodes
remain in both hashes. Failure produces no usable grouping signature.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
from typing import Any

from latex_sft.core.semantics import (LatexNode, parse_latex_faithful, is_renamable_symbol,
                                      FIXED_COMMANDS, GREEK_VARIABLES, canonicalize_latex_faithful)

SIGNATURE_VERSION = 'faithful_structure_v2'
_CONSTANTS = {'e', 'i', r'\pi', r'\infty', r'\hbar'}
_FIXED_FUNCTIONS = {'sin', 'cos', 'tan', 'tanh', 'log', 'ln', 'exp', 'max', 'min', 'det',
                    'softmax', 'Softmax', 'Attention', 'ReLU', 'RMSNorm', 'Cov', 'Var', 'Tr'}
_UNSUPPORTED_BINDERS = {r'\int', r'\oint', r'\iint', r'\iiint', r'\forall', r'\exists'}
_DECLARED_BINDERS = {r'\sum', r'\prod', r'\lim'}
_ALLOWED_SYMBOL_COMMANDS = FIXED_COMMANDS | GREEK_VARIABLES | {
    'pi', 'hbar', 'ell', 'Gamma', 'Sigma', 'Theta', 'Lambda', 'Xi', 'Pi',
    'Upsilon', 'Phi', 'Psi', 'Omega', 'cdots', 'vdots', 'ddots', 'otimes',
}


def _function_symbols(latex: str) -> set[str]:
    """Recognize explicit single-symbol/named function application notation.

    Function symbols have their own alpha namespace. Fixed operator/function
    names retain their literal identity. This does not infer roles from prose.
    """
    latex = canonicalize_latex_faithful(latex)
    functions = set(re.findall(r'(?<![A-Za-z\\])([A-Za-z])\s*\(', latex))
    functions.update('\\'+name for name in re.findall(r'\\([A-Za-z]+)\s*\(', latex))
    for command, name in re.findall(r'\\(text|operatorname|mathrm|mathit|mathbf|boldsymbol|mathcal|mathbb)\{([^{}]+)\}\s*\(', latex):
        name = re.sub(r'\s+', '', name)
        functions.add(name if command not in {'text', 'operatorname'} and len(name) == 1 else '@'+name)
    return functions


def _validate_scope(node: LatexNode, *, binder_operator: bool = False) -> None:
    if node.kind == 'symbol':
        if node.value.startswith('\\') and node.value[1:] not in _ALLOWED_SYMBOL_COMMANDS:
            raise ValueError('Unknown or unsupported command: '+node.value)
        if node.value in _UNSUPPORTED_BINDERS:
            raise ValueError('Unsupported binding operator: '+node.value)
        if node.value in _DECLARED_BINDERS and not binder_operator:
            raise ValueError('Binding operator has no supported explicit declaration')
    for index, child in enumerate(node.children):
        _validate_scope(child, binder_operator=node.kind == 'binder' and index == 0)


def _number(value: str) -> tuple[str, Decimal]:
    try:
        number = Decimal(value)
        if not number.is_finite(): raise ValueError('Non-finite number')
    except InvalidOperation as error:
        raise ValueError('Invalid number: '+value) from error
    canonical = format(number.normalize(), 'f')
    return canonical, number


def _payload(tree: LatexNode, functions: set[str], *, template: bool) -> list[Any]:
    variables: dict[str, str] = {}
    function_names: dict[str, str] = {}

    def scalar_literal(node: LatexNode) -> bool:
        return node.kind == 'number' or (node.kind == 'neg' and node.children[0].kind == 'number')

    def visit(node: LatexNode, *, role: str = 'literal', protect_numbers: bool = False,
              index_context: bool = False) -> list[Any]:
        value = node.value
        if node.kind == 'symbol':
            if value.startswith('@bound:'):
                pass
            elif value in _CONSTANTS and not (index_context and value in {'i', 'e'}):
                pass
            elif index_context and is_renamable_symbol(value):
                value = variables.setdefault(value, '@free:'+str(len(variables)))
            elif value in functions and value.lstrip('\\@') not in _FIXED_FUNCTIONS:
                value = function_names.setdefault(value, '@function:'+str(len(function_names)))
            elif is_renamable_symbol(value):
                value = variables.setdefault(value, '@free:'+str(len(variables)))
        if node.kind == 'number':
            value, number = _number(value)
            ordinary = number not in {Decimal(-1), Decimal(0), Decimal(1)}
            integer_power = role == 'power' and number == number.to_integral_value()
            if template and not protect_numbers and ordinary and (role == 'coefficient' or integer_power):
                value = '@parameter:'+('integer_power' if integer_power else 'coefficient')
        children = []
        for index, child in enumerate(node.children):
            # A number's default is a literal. Only a direct scalar factor of
            # multiplication or a complete literal integer exponent can opt in.
            child_role = 'literal'
            child_protected, child_index = protect_numbers, index_context
            if node.kind == 'mul' and scalar_literal(child):
                child_role = 'coefficient'
            elif node.kind == 'neg' and scalar_literal(node):
                child_role = role
            elif node.kind == 'binder':
                child_protected = protect_numbers or index in {1, 2}
            elif node.kind == 'div' and index == 1:
                child_protected = True
            elif node.kind == 'reciprocal':
                # The faithful AST represents a numerical denominator as a
                # reciprocal factor: its number is still a denominator literal.
                child_protected = True
            elif node.kind == 'scripts':
                if index == 1:
                    child_index, child_protected = True, True
                elif index == 2:
                    child_role = 'power' if scalar_literal(child) else 'literal'
                    child_protected = protect_numbers or not scalar_literal(child)
            children.append(visit(child, role=child_role, protect_numbers=child_protected,
                                  index_context=child_index))
        return [node.kind, value, children]

    return visit(tree)


def _hash(payload: list[Any]) -> str:
    serialized = json.dumps([SIGNATURE_VERSION, payload], ensure_ascii=False,
                            separators=(',', ':'), sort_keys=True)
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()


def structural_signatures(latex: str) -> dict[str, Any]:
    """Return deterministic structural/template hashes or fail closed.

    template_signature abstracts only direct multiplicative scalar coefficients
    and complete non-special integer exponents. Additive literals, denominators,
    bounds, numeric indices, complex exponents and 0/1/-1 remain literal. Index
    symbols i/e participate in consistent variable alpha renaming; elsewhere
    they retain their constant identity. This grants no scoring equivalence.
    """
    result: dict[str, Any] = {
        'signature_version': SIGNATURE_VERSION, 'parse_success': False,
        'structural_signature': None, 'template_signature': None,
        'structural_payload': None, 'template_payload': None,
    }
    try:
        tree = parse_latex_faithful(latex)
        _validate_scope(tree)
        functions = _function_symbols(latex)
        structure = _payload(tree, functions, template=False)
        template = _payload(tree, functions, template=True)
    except (ValueError, IndexError, RecursionError, TypeError) as error:
        result['reason'] = str(error)
        return result
    result.update(parse_success=True, structural_signature=_hash(structure),
                  template_signature=_hash(template), structural_payload=structure,
                  template_payload=template, reason='complete faithful AST')
    return result

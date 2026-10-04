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

from training.latex_semantics import (LatexNode, _faithful_ast, _renamable_symbol,
                                      _FIXED_COMMANDS, _GREEK_VARIABLES, canonicalize_latex_faithful)

SIGNATURE_VERSION = 'faithful_structure_v1'
_CONSTANTS = {'e', 'i', r'\pi', r'\infty', r'\hbar'}
_FIXED_FUNCTIONS = {'sin', 'cos', 'tan', 'tanh', 'log', 'ln', 'exp', 'max', 'min', 'det',
                    'softmax', 'Softmax', 'Attention', 'ReLU', 'RMSNorm', 'Cov', 'Var', 'Tr'}
_UNSUPPORTED_BINDERS = {r'\int', r'\oint', r'\iint', r'\iiint', r'\forall', r'\exists'}
_DECLARED_BINDERS = {r'\sum', r'\prod', r'\lim'}
_ALLOWED_SYMBOL_COMMANDS = _FIXED_COMMANDS | _GREEK_VARIABLES | {
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

    def visit(node: LatexNode, *, role: str = 'coefficient', in_bound: bool = False) -> list[Any]:
        value = node.value
        if node.kind == 'symbol':
            if value.startswith('@bound:') or value in _CONSTANTS:
                pass
            elif value in functions and value.lstrip('\\@') not in _FIXED_FUNCTIONS:
                value = function_names.setdefault(value, '@function:'+str(len(function_names)))
            elif _renamable_symbol(value):
                value = variables.setdefault(value, '@free:'+str(len(variables)))
        if node.kind == 'number':
            value, number = _number(value)
            ordinary = number not in {Decimal(-1), Decimal(0), Decimal(1)}
            integer_power = role == 'power' and number == number.to_integral_value()
            if template and not in_bound and ordinary and (role == 'coefficient' or integer_power):
                value = '@parameter:'+('integer_power' if integer_power else 'coefficient')
        children = []
        for index, child in enumerate(node.children):
            child_role, child_bound = role, in_bound
            if node.kind == 'binder':
                child_bound = in_bound or index in {1, 2}
                child_role = 'coefficient'
            elif node.kind == 'scripts':
                literal_power = child.kind == 'number' or (child.kind == 'neg' and child.children[0].kind == 'number')
                child_role = ('index' if index == 1 else
                              ('power' if literal_power else 'protected') if index == 2 else 'coefficient')
            children.append(visit(child, role=child_role, in_bound=child_bound))
        return [node.kind, value, children]

    return visit(tree)


def _hash(payload: list[Any]) -> str:
    serialized = json.dumps([SIGNATURE_VERSION, payload], ensure_ascii=False,
                            separators=(',', ':'), sort_keys=True)
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()


def structural_signatures(latex: str) -> dict[str, Any]:
    """Return deterministic structural/template hashes or fail closed.

    template_signature abstracts ordinary coefficients and non-special integer
    powers. Numeric 0/1/-1, bound declarations/endpoints, indices, e/i/pi and
    fixed functions remain literal. This interface grants no scoring equivalence.
    """
    result: dict[str, Any] = {
        'signature_version': SIGNATURE_VERSION, 'parse_success': False,
        'structural_signature': None, 'template_signature': None,
        'structural_payload': None, 'template_payload': None,
    }
    try:
        tree = _faithful_ast(latex)
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

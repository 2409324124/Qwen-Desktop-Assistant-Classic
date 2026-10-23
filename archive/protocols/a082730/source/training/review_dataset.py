"""Versioned, conservative review of frozen records; never mutates sources.

A rule-checked record is not a proof of arbitrary natural-language equivalence.
Information-destroying historical perturbations are held for manual review.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import re
from typing import Any

from training.latex_postprocess import postprocess_latex
from training.latex_semantics import _faithful_ast, compare_latex_math_only, canonicalize_latex_faithful
from tools.data_generation.noisy_builder import FORMULA_NAME_SHORTCUTS, AMBIGUOUS_SHORTCUT_CONTEXT

DATA_VERSION = 'v4'
LOSSY_RULES = {'subscript_loss', 'hat_bar_prime_loss', 'code_fragment_noise',
              'symbol_dropout', 'equation_truncation', 'fragment_anchor',
              'contextual_shorthand', 'structure_collapse', 'nested_break', 'broken_brackets',
              'ascii_substitute', 'operator_confusion', 'operator_mix', 'dense_ascii'}
GREEK = {'alpha','beta','gamma','theta','phi','xi','mu','sigma','omega','lambda',
         'epsilon','varepsilon','tau','psi','rho','eta','Delta','Sigma','Gamma','Phi','Omega'}
WORDS = {'sum','prod','log','ln','exp','sin','cos','tan','tanh','sqrt','frac','int','lim',
         'infinity','inf','range','for','in','to','from','of','all','indices','matrix',
         'bar','hat','prime','partial','nabla','dt','dx','dy','dz','d','text','operatorname',
         'mathrm','mathbb','mathcal','mathbf','boldsymbol','begin','end','bmatrix','pmatrix',
         'vmatrix','Vmatrix','left','right','cdot','times','odot','otimes','cdots','vdots',
         'ddots','det','Cov','Softmax','RMSNorm','ReLU','max','min','pi','infty'}

def normalized_text(value: str) -> str:
    return re.sub(r'\s+', ' ', value.strip())

def _name_only(text: str, family: str) -> bool:
    aliases = {family.lower(), FORMULA_NAME_SHORTCUTS.get(family, '').lower(),
               'softmax' if family == 'Softmax Function' else '',
               'jacobian' if family == 'Jacobian Matrix' else ''}
    value = text.strip().lower()
    value = re.sub(r'^(?:我想问|记一下|那个|就是)\s*', '', value)
    value = re.sub(r'\s*(?:那个式子|怎么写|公式)[？?。.!]*$', '', value).strip()
    return value in (aliases - {''}) or value in {'那个','就是','我想问','product',''}

def symbol_tokens(value: str, *, latex: bool = False) -> set[str]:
    """Conservative symbol-presence screen, not a semantic verifier."""
    if latex:
        value = re.sub(r'\\(?:text|operatorname)\{[^{}]*\}', '', value)
        value = re.sub(r'\\(?:begin|end)\{[^{}]*\}', '', value)
    result: set[str] = set()
    if not latex:
        if re.search(r'\bexp\b', value): result.add('e')
        if re.search(r'\b(?:dt|dx|dy|dz)\b', value):
            result.add('d'); result.update(re.findall(r'\bd([txyz])\b',value))
        if 'epsilon' in value or 'eps' in value: result.update({'epsilon','varepsilon'})
        if 'delta ' in value or 'delta_' in value or 'd_' in value: result.add('Delta')
    for word in re.findall(r'[A-Za-z]+', value):
        if word in GREEK:
            result.add(word)
        elif word in WORDS:
            continue
        elif len(word) == 1:
            result.add(word)
        elif len(word) <= 3 and (latex or word in {'fg','xy','zu','uv','ij','Wx','Uh','Ax','AB','BA'}):
            result.update(word)
    return result

def _bce_repair(text: str, output: str) -> str | None:
    # Only repair explicit sum(... two terms ... for ...), never a formula-name shortcut.
    binder = re.search(r'\\sum_\{([^{}=]+)=1\}\^\{([^{}]+)\}', output)
    if not binder: return None
    has_scope = False
    if 'sum' in text:
        tail = text[text.index('sum')+3:]
        prefix = re.match(r'(?:_[A-Za-z](?:\^[A-Za-z])?|_over_[A-Za-z]_from_1_to_[A-Za-z])?(?:=1_to_[A-Za-z])?\s*',tail)
        position = prefix.end() if prefix else 0
        # Only groups directly attached to the sum call are evidence. A
        # subsequent note, equation, or unrelated parenthesis cannot set scope.
        for _ in range(2):
            tail=tail[position:].lstrip()
            if not tail or tail[0] not in '([': break
            opening=tail[0]; closing=')' if opening=='(' else ']'; depth=0; end=None
            for i,c in enumerate(tail):
                if c==opening: depth+=1
                elif c==closing: depth-=1
                if depth==0: end=i; break
            if end is None: break
            chunk=tail[1:end]
            if '+' in chunk and re.search(r'\(1(?:\.0)?\s*-',chunk) and chunk.count('log')>=2:
                has_scope=True; break
            # A separate body after a bound declaration is legal: sum(i=1 to N) [body].
            if not re.fullmatch(r'\s*[A-Za-z]\s*=\s*1\s*to\s*[A-Za-z]\s*',chunk): break
            position=end+1
    # These two manually checked descriptions explicitly specify all operand
    # names and both terms inside the sum. Other name/description-only BCE rows
    # remain quarantined rather than receiving arbitrary random symbols.
    if ('求和里面' in text and 'alpha' in text and '负号' in text
            and ('两项相加' in text or '再加上' in text) and '1减' in text):
        has_scope=True
    if not has_scope: return None
    if not re.search(r'[\u4e00-\u9fff]',text) and symbol_tokens(output,latex=True)-symbol_tokens(text):
        return None
    start=binder.end()
    return output[:start]+r' \left['+output[start:].strip()+r'\right]'

def review_records(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    rows = deepcopy(records)
    for row in rows:
        meta = row.setdefault('metadata', {})
        original = str(meta.get('original_output', row['output']))
        meta.setdefault('original_output', original)
        meta.setdefault('source_id', 'content:' + hashlib.sha256((row['input']+'\0'+original).encode()).hexdigest())
        meta['data_version'] = DATA_VERSION
        # Rebuild from original, avoiding a cached canonicalizer's loss of matrix types.
        row['output'] = canonicalize_latex_faithful(postprocess_latex(original))
        row['canonical_output'] = row['output']
    conflicts: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        conflicts[normalized_text(row['input'])].add(normalized_text(row['output']))
    accepted, quarantined, decisions = [], [], []
    for row in rows:
        meta = row['metadata']; text = row['input']; output = row['output']
        family = str(meta.get('formula_name', ''))
        reasons: list[str] = []
        repairs: list[str] = []
        if len(conflicts[normalized_text(text)]) > 1:
            reasons.append('identical_input_conflicting_targets')
        if _name_only(text, family):
            reasons.append('insufficient_formula_information')
        if any(ord(c) < 32 and c not in '\n\r\t' for c in text+output):
            reasons.append('control_character_corruption')
        if any(text.lower().startswith(v.lower()) for v in AMBIGUOUS_SHORTCUT_CONTEXT.values()):
            reasons.append('historical_shortcut_missing_or_conflicting_symbols')
        rule = meta.get('hard_rule') or meta.get('noise_rule')
        if rule in LOSSY_RULES and meta.get('fidelity_policy') != 'complete_formula_surface_v1':
            reasons.append('information_destroying_perturbation_requires_manual_review')
        # Bind only an explicit declaration, never the first operand of sum(...).
        declarations = [r'for\s+([A-Za-z])\s+in\s+range\(1,\s*([A-Za-z])\s*\+\s*1\)',
                        r'(?:for\s+|sum\(\s*)([A-Za-z])\s*(?:=\s*1\s*to|from\s+1\s+to)\s+([A-Za-z])\b',
                        r'sum_over_([A-Za-z])_from_1_to_([A-Za-z])\b']
        declaration = next((m for pat in declarations if (m:=re.search(pat,text))), None)
        target_index = re.search(r'\\sum_\{([^{}=]+)=1\}\^\{([^{}]+)\}', output)
        if (family in {'Cross-Entropy Loss','Mean Squared Error','Sample Mean'}
                and declaration and target_index and declaration[2]==target_index[2]
                and declaration[1]!=target_index[1] and declaration[1]!=declaration[2] and not reasons):
            old,new=target_index[1],declaration[1]
            def nodes(node):
                yield node
                for child in node.children: yield from nodes(child)
            try:
                tree=_faithful_ast(output)
                parsed=list(nodes(tree))
                unsafe = any(n.kind=='symbol' and n.value==new for n in parsed)
                unsafe |= any(n.kind=='scripts' and len(n.children)>1 and
                              any(c.kind=='symbol' and c.value==old for c in nodes(n.children[1])) for n in parsed)
            except (ValueError,IndexError,RecursionError):
                unsafe=True
            if unsafe:
                reasons.append('index_restoration_scope_requires_manual_review')
            else:
                output=output.replace('{'+old+'=', '{'+new+'=',1)
                output=re.sub(r'(_\{)'+re.escape(old)+r'(\})',lambda m:m[1]+new+m[2],output)
                repairs.append('restore_explicit_sum_index')
        if re.search(r'\\(?:sum|prod)_\{([^{}=]+)=([^{}]+)\}\^\{\1\}', output):
            reasons.append('bound_index_collision')
        if meta.get('reviewed_explicit_replacement') and not reasons:
            output=postprocess_latex(meta['reviewed_explicit_replacement'])
            repairs.append('restore_explicit_product_rule_symbols')
        if family == 'Softmax Function':
            indices=re.findall(r'\\sum_\{([^{}]+)\}',output)
            lhs=output.split('=',1)[0]
            if any('_{'+i+'}' in lhs for i in indices):
                reasons.append('softmax_free_index_captured')
        if family == 'RMSNorm' and re.search(r'RMSNorm\}\(\\gamma\)', output):
            reasons.append('input_scale_parameter_collision')
        if family in {'Fourier Transform','Schrodinger Equation'} and (re.search(r'\\partial i\b|\\psi\(i\)|f\(i\)|\bdi\b', output)):
            reasons.append('imaginary_constant_variable_collision')
        grouped_bce = re.search(r'\\sum_\{[^{}]+\}\^\{[^{}]+\}\s*(?:\\left)?\[',output)
        if family == 'Cross-Entropy Loss' and not grouped_bce:
            repaired = _bce_repair(text, output)
            if repaired and not reasons:
                output = repaired; repairs.append('restore_explicit_bce_sum_scope')
            else:
                reasons.append('bce_scope_not_uniquely_recoverable')
        # ASCII/code inputs allow a strict presence screen. Chinese descriptions require
        # separate manual/linguistic verification; do not fill symbols from source_input.
        if '=' in text or ' for ' in text or re.search(r'[\u4e00-\u9fff]',text):
            missing = symbol_tokens(output, latex=True) - symbol_tokens(text)
            for bound in re.findall(r'\\(?:sum|prod)_\{([^{}=]+)(?:=[^{}]+)?\}',output):
                # These symbols are locally bound, not user-specified free variables.
                missing.discard(bound)
            if 'hbar' in text: missing.discard('h')
            if missing:
                reasons.append('target_symbols_absent_from_input:' + ','.join(sorted(missing)))
        if '=' in text and not reasons:
            # The local parser can prove elementary explicit transcriptions.
            # Unsupported program loops/matrix descriptions stay under other
            # conservative screens; this path does not infer a standard formula.
            expression=text.split(':')[-1].strip()
            if (re.fullmatch(r'[A-Za-z0-9_\\{}^+*/=()., \-]+',expression)
                    and not re.search(r'\b(?:sum|int|integral|limit|range|for|matrix)\b',expression)
                    and 'sum_' not in expression):
                expression=expression.replace('**','^').replace('==','=')
                expression=re.sub(r'\b([A-Za-z])(\d+)\b',r'\1_{\2}',expression)
                for name in ('sin','cos','tan','tanh','log','ln','exp','sqrt'):
                    expression=re.sub(r'(?<![A-Za-z\\])'+name+r'(?=\s*\()',lambda m:'\\'+name,expression)
                result=compare_latex_math_only(output,postprocess_latex(expression),formula_name=family)
                if not result.math_match:
                    reasons.append('explicit_expression_not_verified_against_target')
        if meta.get('quality_override_action') == 'exclude':
            reasons.append('reviewed_exclusion:' + str(meta.get('quality_override_reason','')))
        if family == 'Cross-Entropy Loss' and re.search(r'\bL\s*=',text) and output.startswith(r'\mathcal{L}') and not reasons:
            output='L'+output[len(r'\mathcal{L}'):]
            repairs.append('restore_explicit_loss_symbol')
        output=canonicalize_latex_faithful(output)
        row['output'] = row['canonical_output'] = output
        reasons = sorted(set(reasons))
        action = 'quarantine' if reasons else ('replace_output' if repairs or output != meta['original_output'] else 'keep')
        meta['review_status'] = 'quarantined' if reasons else 'rule_checked_not_semantic_proof'
        normalized_only = output != meta['original_output'] and not repairs
        meta['review_reasons'] = reasons or repairs or (['surface_normalization'] if normalized_only else ['passed_conservative_screens'])
        meta['sympy_expr_validated'] = False
        if repairs:
            meta['original_sympy_expr'] = meta.get('sympy_expr')
            meta['sympy_expr'] = None
        decision = {'source_id': meta['source_id'], 'source_file': meta.get('source_file',''),
                    'source_path': meta.get('source_path',''), 'source_line': meta.get('source_line'),
                    'formula_name': family, 'input': text, 'original_output': meta['original_output'],
                    'revised_output': output, 'action': action, 'reasons': meta['review_reasons'],
                    'reason': '; '.join(meta['review_reasons']), 'data_version': DATA_VERSION}
        decisions.append(decision)
        (quarantined if reasons else accepted).append(row)
    final_targets = defaultdict(set)
    for row in accepted: final_targets[normalized_text(row['input'])].add(normalized_text(row['output']))
    conflicted = {text for text,targets in final_targets.items() if len(targets)>1}
    if conflicted:
        moved = [row for row in accepted if normalized_text(row['input']) in conflicted]
        ids = {row['metadata']['source_id'] for row in moved}
        for row in moved:
            row['metadata']['review_status']='quarantined'
            row['metadata']['review_reasons'].append('conflicting_targets_after_repair')
        for decision in decisions:
            if decision['source_id'] in ids:
                decision['action']='quarantine'
                decision['reasons'].append('conflicting_targets_after_repair')
                decision['reason']='; '.join(decision['reasons'])
        quarantined.extend(moved)
        accepted=[row for row in accepted if row['metadata']['source_id'] not in ids]
    return accepted, quarantined, decisions

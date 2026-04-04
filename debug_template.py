import json
import ast

with open('d:/1/mine_sympy.py', 'r', encoding='utf-8') as f:
    text = f.read()

try:
    module = ast.parse(text)
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == 'generate_formulas':
            for stmt in node.body:
                if isinstance(stmt, ast.Assign) and isinstance(stmt.targets[0], ast.Name) and stmt.targets[0].id == 'templates':
                    for elt in stmt.value.elts:
                        latex_idx = -1
                        for i, k in enumerate(elt.keys):
                            if getattr(k, 'value', getattr(k, 'id', '')) == 'latex':
                                latex_idx = i
                                break
                        val = elt.values[latex_idx].value
                        try:
                            val.format(x='x', y='y', z='z', u='u', v='v', n='n', k='k', i='i', t='t', theta='theta', m='m', m1='m1', m2='m2', r='r', Q='Q', K='K', V='V', W='W', b='b', N='N')
                        except ValueError as e:
                            print(f"Error in '{val}': {e}")
except Exception as e:
    print('Ast error', e)

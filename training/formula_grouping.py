"""Grouping-only identities; never used to relax the evaluation metric."""
from copy import deepcopy
import json
from pathlib import Path

from training.formula_structure import structural_signatures

GROUPING_VERSION = 'v5-structure-near-1'
REGISTRY_PATH = Path(__file__).with_name('formula_families.json')


def load_family_registry(path=REGISTRY_PATH):
    payload=json.loads(path.read_text(encoding='utf-8'))
    registry={}
    ids=set()
    for group in payload['groups']:
        if group['id'] in ids:
            raise ValueError(f'Duplicate near-family ID: {group["id"]}')
        ids.add(group['id'])
        for family in group['members']:
            if family in registry:
                raise ValueError(f'Family assigned more than once: {family}')
            registry[family]={'near_family_id':group['id'],'near_family_basis':group['basis'],
                              'family_registry_version':payload['version']}
    return registry


def prepare_grouping_records(records):
    registry=load_family_registry()
    accepted,held,diagnostic=[],[],[]
    for source in records:
        row=deepcopy(source); meta=row.setdefault('metadata',{})
        meta.update(data_version='v5', grouping_rule_version=GROUPING_VERSION)
        family=meta.get('formula_name')
        if family=='Symbol Boundary':
            meta.update(evaluation_role='diagnostic',grouping_status='diagnostic',
                        grouping_reasons=['symbol_transcription_not_formula_generalization'])
            diagnostic.append(row)
            continue
        meta['evaluation_role']='main'
        reasons=[]
        if family not in registry:
            reasons.append('unknown_formula_family')
        else:
            meta.update(registry[family])
        signatures=[]
        for label,formula in (('revised',row['output']),('original',meta.get('original_output',row['output']))):
            try:
                result=structural_signatures(formula)
                if not result.get('parse_success') or not result.get('structural_signature') or not result.get('template_signature'):
                    raise ValueError(result.get('reason','No complete structural signature'))
                signatures.append({'label':label, **result})
            except (ValueError,IndexError,RecursionError) as exc:
                reasons.append(f'{label}_structure_unverified:{exc}')
        if reasons:
            meta.update(grouping_status='quarantined',grouping_reasons=reasons)
            held.append(row)
        else:
            meta.update(grouping_status='ready',grouping_reasons=['registered_family_and_complete_structure'],
                        structural_signature=signatures[0]['structural_signature'],
                        template_signature=signatures[0]['template_signature'],
                        structural_signatures=sorted({s['structural_signature'] for s in signatures}),
                        template_signatures=sorted({s['template_signature'] for s in signatures}),
                        signature_evidence=signatures)
            accepted.append(row)
    return accepted,held,diagnostic

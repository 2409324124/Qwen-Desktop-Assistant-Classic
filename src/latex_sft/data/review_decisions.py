"""Source-bound human decisions and frozen-split leakage checks."""
from collections import defaultdict
from copy import deepcopy
from .formula_grouping import prepare_grouping_records
from .records import group_keys, dedupe_records
from .text import normalized_text
from .io import sha_text

VERSION = 'v5.1-reviewed-training'

def review_decisions(rows, decisions, heldout):
    """Require exactly one bound decision per row; failed checks quarantine, never accept."""
    if len(rows) != len(decisions):
        raise ValueError('Review must cover every training record exactly once')
    by_id = {}
    for d in decisions:
        if d['source_id'] in by_id:
            raise ValueError('Duplicate review source_id')
        by_id[d['source_id']] = d
    if set(by_id) != {r['metadata']['source_id'] for r in rows}:
        raise ValueError('Review source IDs do not match the training set')
    accepted, quarantine, audit = [], [], []
    for number, original in enumerate(rows, 1):
        sid = original['metadata']['source_id']; d = by_id[sid]
        if d['row'] != number or any(d[k+'_sha256'] != sha_text(original[k]) for k in ('input', 'output')):
            raise ValueError(f'Stale or misaligned review: {sid}')
        if d['decision'] not in {'keep', 'repair', 'quarantine'} or not str(d.get('reason', '')).strip():
            raise ValueError(f'Missing review decision/evidence: {sid}')
        if d['decision'] == 'repair' and (not d.get('output') or d['output'] == original['output']):
            raise ValueError(f'Repair must provide a different complete target: {sid}')
        if d['decision'] != 'repair' and d.get('output') not in (None, original['output']):
            raise ValueError(f'Only a repair may change the target: {sid}')
        row = deepcopy(original); meta = row['metadata']
        entry = deepcopy(d); entry['final_action'] = d['decision']; entry['validation_reasons'] = []
        meta.update(data_version=VERSION, parent_data_version='v5',
                    reviewed_v5_output=original['output'], review_status=d['decision'],
                    review_reason=d['reason'], review_rule_version=VERSION)
        if d['decision'] == 'repair':
            row['output'] = d['output']; row['canonical_output'] = d['output']
        if d['decision'] != 'quarantine':
            # Recompute repaired identities while retaining every historical edge.
            ready, held, diagnostic = prepare_grouping_records([row])
            if held or diagnostic:
                entry['final_action'] = 'quarantine'
                entry['validation_reasons'].append('revised_structure_unverified')
                entry['structure_diagnostics'] = held[0]['metadata'].get('grouping_reasons', []) if held else ['diagnostic_only']
            else:
                fresh = ready[0]['metadata']
                for key in ('structural_signatures', 'template_signatures'):
                    meta[key] = sorted(set(meta.get(key, [])) | set(fresh[key]))
                for key in ('structural_signature', 'template_signature', 'signature_evidence'):
                    meta[key] = fresh[key]
        meta['review_status'] = entry['final_action']
        meta['review_validation_reasons'] = entry['validation_reasons']
        if entry['final_action'] == 'quarantine':
            meta['evaluation_role'] = 'quarantine'; quarantine.append(row)
        else:
            accepted.append(row)
        audit.append(entry)

    audit_by_id = {d['source_id']: d for d in audit}
    targets = defaultdict(set)
    for row in accepted:
        targets[normalized_text(row['input'])].add(normalized_text(row['output']))
    conflicts = {x for x, outputs in targets.items() if len(outputs) > 1}
    heldout_keys = {k for split in heldout for row in split for k in group_keys(row)}
    unsafe_groups = {r['metadata']['formula_group_id'] for r in accepted if group_keys(r) & heldout_keys}
    # Conservatively remove a whole original training component if a repair
    # adds a relationship to a frozen development/test component.
    kept = []
    for row in accepted:
        reasons = []
        if normalized_text(row['input']) in conflicts: reasons.append('conflicting_targets_after_review')
        if row['metadata']['formula_group_id'] in unsafe_groups: reasons.append('component_connects_to_frozen_holdout')
        if reasons:
            entry = audit_by_id[row['metadata']['source_id']]
            entry['final_action'] = 'quarantine'; entry['validation_reasons'].extend(reasons)
            row['metadata'].update(review_status='quarantine', evaluation_role='quarantine', review_validation_reasons=reasons)
            quarantine.append(row)
        else:
            kept.append(row)
    kept, duplicates = dedupe_records(kept)
    for row in kept:
        for sid in row['metadata'].get('duplicate_source_ids', []):
            if sid in audit_by_id and sid != row['metadata']['source_id']:
                audit_by_id[sid]['exported_as_duplicate_of'] = row['metadata']['source_id']
    return kept, sorted(quarantine, key=lambda r:r['metadata']['source_id']), audit, duplicates


def leakage_report(splits):
    keys = [{k for row in split for k in group_keys(row)} |
            {('group', row['metadata']['formula_group_id']) for row in split} for split in splits]
    labels = ('input', 'equation', 'source', 'family', 'lineage', 'structure', 'template', 'near_family', 'group')
    result = {label+'_overlap': sum(len({v for k,v in keys[a] & keys[b] if k == label})
              for a,b in ((0,1),(0,2),(1,2))) for label in labels}
    if any(result.values()): raise ValueError(f'Cross-split leakage: {result}')
    return result



# Historical API name retained for callers.
review_training = review_decisions

"""Exact, deterministic allocation of indivisible formula components.

Optimize sample L1 error first, then missing category slots, group L1 error,
then category L1 error. Seed only resolves equally good assignments. Exhaustive
subset search is bounded by a feasible incumbent, never by formula identities.
"""
from collections import Counter
from fractions import Fraction
import hashlib
import math
import random

ALLOCATION_VERSION = 'component-allocation-v1'
SPLITS = ('train', 'eval', 'test')


def allocate_components(groups, *, eval_ratio=.1, test_ratio=.1, seed=42):
    groups = sorted(groups, key=lambda g: g[0]['metadata']['formula_group_id'])
    n = len(groups)
    ratios = [1-Fraction(str(eval_ratio))-Fraction(str(test_ratio)),
              Fraction(str(eval_ratio)), Fraction(str(test_ratio))]
    if ratios[0] <= 0 or ratios[1] <= 0 or ratios[2] < 0:
        raise ValueError('Invalid component allocation ratios')
    scale = math.lcm(*(r.denominator for r in ratios))
    weights = [int(r*scale) for r in ratios]
    sizes = [len(g) for g in groups]
    total = sum(sizes)
    categories = [Counter(str(r['metadata'].get('category') or 'unknown') for r in g) for g in groups]
    category_total = sum(categories, Counter())
    # Reserve training first, then evaluation; too few components are disclosed.
    active = [s for s in (1, 2) if weights[s]]
    minimum = [int(n > 0), 0, 0]
    if n > len(active):
        for s in active: minimum[s] = min(3, (n-1)//len(active)) if len(active) == 2 else 1
    else:
        for s in active[:max(0, n-1)]: minimum[s] = 1
    enabled = [s for s in active if minimum[s]]
    target = [total*w for w in weights]
    group_target = [n*w for w in weights]

    def sample_error(counts):
        return sum(abs(c*scale-t) for c, t in zip(counts, target))

    def assess(assignment):
        counts = [0, 0, 0]; group_counts = [0, 0, 0]
        domains = [Counter(), Counter(), Counter()]
        for i, split in enumerate(assignment):
            counts[split] += sizes[i]; group_counts[split] += 1
            domains[split].update(categories[i])
        missing = sum(category not in domains[s] for s in (0, *enabled) for category in category_total)
        group_error = sum(abs(c*scale-t) for c,t in zip(group_counts, group_target))
        domain_error = sum(abs(domains[s][c]*scale-category_total[c]*weights[s])
                           for s in range(3) for c in category_total)
        return (sample_error(counts), missing, group_error, domain_error)

    assignment = [0]*n
    shuffled = list(range(n)); random.Random(seed).shuffle(shuffled)
    cursor = 0
    for s in enabled:
        for i in shuffled[cursor:cursor+minimum[s]]: assignment[i] = s
        cursor += minimum[s]
    # Tighten the exhaustive-search bound with legal local moves and swaps.
    while True:
        current = assess(assignment)[0]
        improved = None
        for i in range(n):
            for s in (0, *enabled):
                if s == assignment[i] or assignment.count(assignment[i]) <= minimum[assignment[i]]: continue
                candidate = assignment.copy(); candidate[i] = s
                error = assess(candidate)[0]
                if error < current: current, improved = error, candidate
            for j in range(i):
                if assignment[i] == assignment[j]: continue
                candidate = assignment.copy(); candidate[i], candidate[j] = candidate[j], candidate[i]
                error = assess(candidate)[0]
                if error < current: current, improved = error, candidate
        if improved is None: break
        assignment = improved
    best_score = assess(assignment)

    def tie_key(candidate):
        return hashlib.sha256(f'{seed}:'.encode()+bytes(candidate)).digest()

    best_tie = tie_key(assignment)
    suffix = [0]*(n+1)
    for i in range(n-1, -1, -1): suffix[i] = suffix[i+1]+sizes[i]

    def candidates(split):
        if split not in enabled: return [(0, 0, 0, abs(target[split]))]
        # Since split deviations sum to zero, any one deviation is at most
        # half the incumbent L1 error. This is an exact pruning bound.
        bound = best_score[0]
        lower = max(0, math.ceil(Fraction(2*target[split]-bound, 2*scale)))
        upper = math.floor(Fraction(2*target[split]+bound, 2*scale))
        max_groups = n-sum(minimum[s] for s in range(3) if s != split)
        result = []
        def visit(i, mask, count, size):
            if size > upper or size+suffix[i] < lower or count > max_groups or count+n-i < minimum[split]: return
            if i == n:
                if size >= lower and count >= minimum[split]:
                    result.append((mask, count, size, abs(size*scale-target[split])))
                return
            visit(i+1, mask, count, size)
            visit(i+1, mask | (1 << i), count+1, size+sizes[i])
        visit(0, 0, 0, 0)
        return sorted(result, key=lambda c: (c[3], c[0]))

    dev_candidates, test_candidates = candidates(1), candidates(2)
    feasible_pairs = 0
    for dev_mask, dev_groups, dev_size, dev_error in dev_candidates:
        if dev_error > best_score[0]: break
        for test_mask, test_groups, test_size, test_error in test_candidates:
            if dev_error+test_error > best_score[0]: break
            if dev_mask & test_mask or n-dev_groups-test_groups < minimum[0]: continue
            counts = [total-dev_size-test_size, dev_size, test_size]
            if sample_error(counts) > best_score[0]: continue
            feasible_pairs += 1
            candidate = [1 if dev_mask & (1 << i) else 2 if test_mask & (1 << i) else 0 for i in range(n)]
            score = assess(candidate)
            tie = tie_key(candidate)
            if (score, tie) < (best_score, best_tie):
                assignment, best_score, best_tie = candidate, score, tie
    result = {g[0]['metadata']['formula_group_id']: SPLITS[s] for g,s in zip(groups, assignment)}
    counts = Counter(result.values())
    report = {
        'version': ALLOCATION_VERSION, 'search': 'exact bounded subset enumeration',
        'objective_order': ['sample_l1', 'missing_category_slots', 'group_l1', 'category_l1'],
        'objective': {'sample_l1_records': best_score[0]/scale, 'missing_category_slots': best_score[1],
                      'group_l1': best_score[2]/scale, 'category_l1_records': best_score[3]/scale},
        'requested_sample_ratios': dict(zip(SPLITS, map(float, ratios))),
        'requested_group_ratios': dict(zip(SPLITS, map(float, ratios))),
        'minimum_groups': dict(zip(SPLITS, minimum)),
        'missing_splits': [SPLITS[s] for s in range(3) if weights[s] and not counts[SPLITS[s]]],
        'seed_tie_break': 'sha256(seed, assignment in sorted group ID order)',
        'candidate_counts': {'eval': len(dev_candidates), 'test': len(test_candidates)},
        'feasible_pairs_scored': feasible_pairs,
    }
    return result, report

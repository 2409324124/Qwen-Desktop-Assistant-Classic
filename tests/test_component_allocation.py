import itertools
import random
import unittest
from collections import Counter

from training.component_allocation import allocate_components


def groups(sizes, domains=None):
    return [[{'metadata': {'formula_group_id': f'group-{i:02d}',
                           'category': (domains or ['a']*len(sizes))[i]}} for _ in range(size)]
            for i,size in enumerate(sizes)]


class ComponentAllocationTests(unittest.TestCase):
    def test_unequal_components_balance_samples_and_broaden_holdouts(self):
        sizes = [90,10,14,2,26,3,24,5,2,5,7,31,170,20,147,33,1,9,44]
        items = groups(sizes, ['a','s','s','a','p','p','s','p','p','s','p','s','c','a','s','m','s','m','a'])
        assignment, report = allocate_components(items)
        counts = Counter()
        for group in items: counts[assignment[group[0]['metadata']['formula_group_id']]] += len(group)
        self.assertEqual(dict(counts), {'train':515, 'eval':64, 'test':64})
        self.assertGreaterEqual(Counter(assignment.values())['eval'],3)
        self.assertGreaterEqual(Counter(assignment.values())['test'],3)
        self.assertEqual(report['objective']['sample_l1_records'],1.2)
        self.assertEqual(assignment, allocate_components(list(reversed(items)))[0])
        self.assertEqual((assignment,report), allocate_components(items))

    def test_exact_objective_matches_independent_exhaustive_oracle(self):
        rng = random.Random(8)
        for n in (3,5,7):
            sizes = [rng.randrange(1,12) for _ in range(n)]
            domains = [rng.choice('abc') for _ in range(n)]
            items = groups(sizes, domains)
            assignment, report = allocate_components(items)
            minimum = report['minimum_groups']
            total = sum(sizes); weights = (8,1,1)
            all_categories = set(domains)
            totals = Counter()
            for size,domain in zip(sizes,domains): totals[domain] += size
            def objective(candidate):
                counts = [0]*3; category_counts = [Counter() for _ in range(3)]
                for split,size,category in zip(candidate,sizes,domains):
                    counts[split] += size; category_counts[split][category] += size
                return (sum(abs(count*10-total*w) for count,w in zip(counts,weights)),
                        sum(c not in counts for counts in category_counts for c in all_categories),
                        sum(abs(candidate.count(s)*10-n*weights[s]) for s in range(3)),
                        sum(abs(category_counts[s][c]*10-totals[c]*weights[s]) for s in range(3) for c in all_categories))
            feasible = [candidate for candidate in itertools.product(range(3), repeat=n)
                        if all(candidate.count(s) >= minimum[name] for s,name in enumerate(('train','eval','test')))]
            actual = tuple(('train','eval','test').index(assignment[g[0]['metadata']['formula_group_id']]) for g in items)
            self.assertEqual(objective(actual), min(map(objective, feasible)))

    def test_zero_test_ratio_and_insufficient_components_are_explicit(self):
        assignment, report = allocate_components(groups([3]*10), eval_ratio=.2, test_ratio=0)
        self.assertEqual(Counter(assignment.values()), {'train':8, 'eval':2})
        self.assertFalse(report['missing_splits'])
        for sizes, expected in (([], {}), ([100], {'train':1}), ([100,1], {'train':1,'eval':1})):
            assignment, report = allocate_components(groups(sizes))
            self.assertEqual(Counter(assignment.values()), expected)
            self.assertIn('test', report['missing_splits'])

    def test_large_group_is_never_split_to_reach_ratio(self):
        assignment, report = allocate_components(groups([1000]+[1]*6))
        self.assertEqual(assignment['group-00'], 'train')
        self.assertEqual(Counter(assignment.values()), {'train':1,'eval':3,'test':3})
        self.assertGreater(report['objective']['sample_l1_records'], 100)


if __name__ == '__main__': unittest.main()

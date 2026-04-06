# Noisy v4_900 Review Sync

This document is for external reviewers or other LLMs to quickly align on the current `noisy_v4_900` validation set.

The point is not to redesign the project, but to evaluate whether the current noisy layer is already stable enough to serve as a scaled validation split.

---

## 1. Review Target

Primary file to review:

- [train_noisy_v4_900.jsonl](D:\1\train_noisy_v4_900.jsonl)

Current generator:

- [noisy_builder.py](D:\1\noisy_builder.py)

Supporting upstream clean set:

- [train_clean_v1_300.jsonl](D:\1\train_clean_v1_300.jsonl)

Supporting formula base:

- [formulas_clean_300.json](D:\1\formulas_clean_300.json)

---

## 2. Project Context

The project builds an SFT dataset for LaTeX formula correction.

Current dataset plan:

- `clean`: high-quality inputs
- `noisy`: realistic but recoverable messy inputs
- `hard`: not implemented yet

Primary audience:

- Simplified Chinese users

Important design principle:

- canonical LaTeX is always controlled locally as `output`
- models only generate or help transform `input`-side data

---

## 3. What Happened Before v4

### `noisy_v1`

- too much script smell
- unnatural text + ASCII Frankenstein outputs

### `noisy_v2`

- fixed the worst Frankenstein issues
- judged as "small fixes before scaling"

### `noisy_v3`

- improved ambiguity control and typo realism
- still exposed over-corruption
- important correction: many ugly samples were not implementation bugs, but rule-level over-corruption

### `noisy_v4`

Current version of the generator was redesigned to:

- use better semantic token mapping
- clean surface residue
- post-filter low-quality outputs
- reduce corruption strength on complex formulas

This removed the worst machine-like LaTeX residue patterns.

---

## 4. Current Dataset Snapshot

### Record count

- total records: `900`

### Structure

Every record contains:

- `instruction`
- `input`
- `output`
- `metadata`

### Category distribution

- `stats_ml`: `270`
- `calculus`: `225`
- `physics`: `135`
- `matrix`: `135`
- `algebra_trig`: `135`

### Perspective distribution

- `beginner`: `300`
- `programmer`: `300`
- `researcher`: `300`

### Noise rule distribution

- `ascii_substitute`: `150`
- `partial_formula_reference`: `140`
- `mixed_language`: `119`
- `operator_confusion`: `117`
- `subscript_loss`: `111`
- `broken_brackets`: `93`
- `keyword_shorthand`: `83`
- `code_fragment_noise`: `49`
- `hat_bar_prime_loss`: `38`

---

## 5. What Is Already Considered Fixed

Compared with earlier versions, the following are no longer the main issue:

1. `mathcal / frac / beginbmatrix / endbmatrix` residue piles
2. obvious Frankenstein concatenations
3. the worst high-ambiguity shorthand failures

These problems were the main blockers in earlier noisy versions.
They are not the primary review focus anymore.

---

## 6. What Reviewers Should Focus On Now

At this stage, the main question is no longer "is the noisy pipeline broken?"

The real question is:

> Has `noisy_v4_900` already crossed the quality threshold strongly enough to be treated as a stable scaled validation set?

Please focus on:

1. realism
- do inputs still look like plausible human input?

2. recoverability
- are the formulas still recoverable with enough consistency for SFT?

3. scaling stability
- does the quality hold at 900 samples, not just at 100 or 300?

4. remaining polish issues
- are the remaining issues only small polish items, or are there still hidden blockers?

---

## 7. Suggested Output Shape For External Review

The external reviewer should ideally answer:

1. Overall conclusion
- is `noisy_v4_900` already mature?

2. What is working well
- which rules now look stable?

3. Remaining issues
- sort by severity
- clearly separate blockers from polish items

4. Final scaling judgment
- choose one:
  - do not scale yet
  - scale after small fixes
  - ready to use as a larger noisy validation set

---

## 8. Bottom Line

Current best internal judgment is:

> `noisy_v4_900` is already a strong noisy validation set candidate, and the main remaining task is no longer rebuilding the noisy pipeline, but confirming that the current scaled version is stable enough to freeze as a phase-1 noisy validation split.


# Project Handoff - 2026-04-07 Phase 1 Frozen State

## 1. Executive Summary

The phase-1 validation stack is now materially complete.

Current frozen validation datasets:

- [train_clean_v1_500.jsonl](D:\1\train_clean_v1_500.jsonl): `1500`
- [train_noisy_v4_900.jsonl](D:\1\train_noisy_v4_900.jsonl): `900`
- [train_hard_v5_600.jsonl](D:\1\train_hard_v5_600.jsonl): `600`

Important status judgment:

- `noisy_v4_900` has passed repeated external review and is stable enough to freeze
- `hard_v5_600` has passed external review and is stable enough to freeze
- `clean_v1_300` is good enough for current generation work, but it is still **undersized** relative to the original phase-1 target

Original phase-1 target:

- `clean`: `1500`
- `noisy`: `900`
- `hard`: `600`

Current status:

- `clean` target met
- `noisy` target met
- `hard` target met

So the project has now fully met the originally planned phase-1 validation sample counts.

---

## 2. Stable Architecture

Current architecture is stable and should not be re-opened casually.

1. [mine_sympy.py](D:\1\mine_sympy.py)
- generates canonical formula records
- includes `standard_latex`
- includes `sympy_expr`
- uses defensive parsing and stores parse failures instead of crashing

2. [data_builder.py](D:\1\data_builder.py)
- builds `clean` training data
- uses Gemini for input-style generation
- preserves canonical LaTeX as `output`
- does not delegate ground-truth formula generation to Gemini

3. [noisy_builder.py](D:\1\noisy_builder.py)
- derives rule-based `noisy` from `clean`
- includes cleaned surface mapping, corruption controls, and post-filtering

4. [hard_builder.py](D:\1\hard_builder.py)
- derives rule-based `hard` from `clean`
- emphasizes structure collapse, nested damage, shorthand anchors, and harder recovery paths

5. local Ollama
- reserved for post-SFT local evaluation
- not the main dataset-generation backend

6. [tavily_client.py](D:\1\tavily_client.py)
- used for real-web reference collection
- supported prompt and rule refinement for `clean` and `noisy`

---

## 3. Formula Base Status

Current large formula base:

- [formulas_clean_300.json](D:\1\formulas_clean_300.json)
- total formulas: `300`

Category distribution:

- `stats_ml`: `90`
- `calculus`: `75`
- `physics`: `45`
- `matrix`: `45`
- `algebra_trig`: `45`

This still matches the intended domain ratio:

- `stats_ml`: `30%`
- `calculus`: `25%`
- `physics`: `15%`
- `matrix`: `15%`
- `algebra_trig`: `15%`

---

## 4. Frozen Dataset State

### Clean

Current main file:

- [train_clean_v1_500.jsonl](D:\1\train_clean_v1_500.jsonl)

Current size:

- `1500`

Distribution:

- `stats_ml`: `450`
- `calculus`: `375`
- `physics`: `225`
- `matrix`: `225`
- `algebra_trig`: `225`

Perspective split:

- `beginner`: `500`
- `programmer`: `500`
- `researcher`: `500`

Current judgment:

- frozen as the current formal phase-1 `clean` validation set
- stable enough to serve as the upstream base for later expansion work
- both quality and quantity now meet the original phase-1 target

### Noisy

Frozen main file:

- [train_noisy_v4_900.jsonl](D:\1\train_noisy_v4_900.jsonl)

Current size:

- `900`

Current judgment:

- frozen as the current formal phase-1 `noisy` validation set
- repeated external review concluded it can be used directly

### Hard

Frozen main file:

- [train_hard_v5_600.jsonl](D:\1\train_hard_v5_600.jsonl)

Current size:

- `600`

Category distribution:

- `stats_ml`: `192`
- `calculus`: `141`
- `physics`: `97`
- `matrix`: `89`
- `algebra_trig`: `81`

Perspective distribution:

- `beginner`: `212`
- `researcher`: `196`
- `programmer`: `192`

Current judgment:

- frozen as the current formal phase-1 `hard` validation set
- external review concluded it can be used directly

---

## 5. What Is Frozen vs What Is Still Open

### Frozen

- [train_noisy_v4_900.jsonl](D:\1\train_noisy_v4_900.jsonl)
- [train_hard_v5_600.jsonl](D:\1\train_hard_v5_600.jsonl)

These two are ready to be treated as phase-1 formal validation datasets.

### Not Fully Closed Yet

None at the phase-1 validation-count level.

All three planned dataset layers have now reached their intended phase-1 counts.

---

## 6. Review Consensus Snapshot

### Clean

Consensus:

- `clean` is now both usable and sufficiently expanded for the original phase-1 plan
- the count gap has been closed

### Noisy

Consensus:

- `noisy_v4_900` crossed the quality gate
- earlier over-corruption issues have been resolved
- remaining issues are polish only

### Hard

Consensus:

- `hard_v5_600` crossed the quality gate
- structure-collapse logic is working
- variable-anchor bugs and shorthand dead-ends have been resolved
- current version is suitable to freeze

---

## 7. Most Important Current Project Truth

The most important current truth is:

**The three-layer design is now real, working, and quantitatively aligned with the original phase-1 plan.**

Current state:

- `clean = 1500`
- `noisy = 900`
- `hard = 600`

Original desired phase-1 state:

- `clean = 1500`
- `noisy = 900`
- `hard = 600`

Therefore:

- the architecture is no longer the bottleneck
- `noisy` is no longer the bottleneck
- `hard` is no longer the bottleneck
- `clean` is no longer the quantity-side bottleneck either

---

## 8. Recommended Next Step

The most natural next step is:

1. treat phase-1 validation datasets as frozen
- `clean = 1500`
- `noisy = 900`
- `hard = 600`

2. decide what phase 2 should prioritize
- larger-scale expansion
- bilingual extension
- training and local evaluation

3. avoid reopening `noisy` or `hard` unless a new training/evaluation signal justifies it

---

## 9. Important Operating Constraints

- when modifying or running project code, use the `latex` conda environment
- do not operate in `base`
- user prefers a short plan before substantial execution
- if something risky, expensive, or blocked appears, notify quickly

---

## 10. Repository / Handoff Context

At the time of this document:

- [train_clean_v1_500.jsonl](D:\1\train_clean_v1_500.jsonl) exists
- [train_noisy_v4_900.jsonl](D:\1\train_noisy_v4_900.jsonl) exists
- [train_hard_v5_600.jsonl](D:\1\train_hard_v5_600.jsonl) exists

If another agent resumes work, the most efficient continuation path is:

1. treat `clean_v1_500` as frozen
2. treat `noisy_v4_900` as frozen
3. treat `hard_v5_600` as frozen
4. decide whether phase 2 should focus on:
- larger-scale expansion
- bilingual extension
- training / evaluation execution

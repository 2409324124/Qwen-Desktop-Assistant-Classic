# Project Handoff - 2026-04-06

## 1. Project Goal

This project builds an SFT dataset for a neuro-symbolic LaTeX formula correction system.

Target setup:

- local base model / future SFT model served through Ollama for post-training evaluation
- formula base generated locally
- user-style input variants generated and curated as training data

Current user focus:

- primary audience is Simplified Chinese users
- bilingual support is postponed, not the main target for now

---

## 2. Current Architecture

The pipeline has been upgraded from a naive local-Ollama-only flow into a split architecture:

1. [mine_sympy.py](D:\1\mine_sympy.py)
- generates canonical formula records
- includes `standard_latex`
- includes `sympy_expr`
- uses defensive parsing and failure fallback

2. [data_builder.py](D:\1\data_builder.py)
- builds `clean`-style training data
- uses Gemini REST generation
- reads `.env`
- keeps the canonical LaTeX as `output`
- only uses the model for input-side variant generation

3. [tavily_client.py](D:\1\tavily_client.py)
- asynchronous Tavily client
- used for real-web expression/noise reference collection

4. local Ollama
- not the current data generator
- reserved for future post-SFT local evaluation

---

## 3. Dataset Layer Status

### `clean`

Current baseline:

- [train_clean_v1_120.jsonl](D:\1\train_clean_v1_120.jsonl)

Status:

- usable as current `clean` baseline
- already prompt-tuned using Tavily expression references
- still not perfect, but strong enough as the main clean seed set

Supporting source:

- [formulas_clean_120.json](D:\1\formulas_clean_120.json)

### `noisy`

Version history:

- [train_noisy_v1_100.jsonl](D:\1\train_noisy_v1_100.jsonl)
  - first prototype
  - useful as review baseline
  - too much script smell

- [train_noisy_v2_100.jsonl](D:\1\train_noisy_v2_100.jsonl)
  - fixed major Frankenstein-style issues
  - significantly improved realism
  - judged by Gemini as “small fixes before scaling”

- [train_noisy_v3_100.jsonl](D:\1\train_noisy_v3_100.jsonl)
  - latest prototype
  - adds lighter typo noise
  - reduces rigid prefix/template usage further
  - tightens shorthand ambiguity handling

Generator:

- [noisy_builder.py](D:\1\noisy_builder.py)

Rule design:

- [noisy_rules_v1.md](D:\1\noisy_rules_v1.md)

### `hard`

Status:

- not implemented yet
- only planned conceptually

---

## 4. Reference Collection Assets

### Real expression style references

- [expression_reference_sampler.py](D:\1\expression_reference_sampler.py)
- [expression_reference_sample.json](D:\1\expression_reference_sample.json)
- [expression_reference_sample.md](D:\1\expression_reference_sample.md)

Purpose:

- used to tune `clean` prompt style
- especially for beginner / programmer / researcher style separation

### Real noisy reference collection

- [noise_reference_sampler.py](D:\1\noise_reference_sampler.py)
- [noise_reference_sample.json](D:\1\noise_reference_sample.json)
- [noise_reference_sample.md](D:\1\noise_reference_sample.md)

Purpose:

- used to derive real-world noise patterns
- supports noisy rule design

---

## 5. Review Artifacts

### Cross-review of Gemini audit

- [gemini_audit_cross_review.md](D:\1\gemini_audit_cross_review.md)

Purpose:

- records what Gemini got right
- records what Gemini overstated
- records what needed re-alignment

### Gemini v2 review prompt

- [gemini_noisy_v2_review_prompt.md](D:\1\gemini_noisy_v2_review_prompt.md)

Purpose:

- compare `noisy_v1` vs `noisy_v2`
- request targeted external audit instead of full redesign

---

## 6. Current Best Read Of Project State

### Clean state

- `clean` is stable enough to serve as baseline
- no immediate need to redesign `clean`

### Noisy state

- `noisy` direction is now validated
- `noisy_v1` should not be scaled
- `noisy_v2` was judged “small fixes before scaling”
- `noisy_v3` is now the newest prototype and should be the next review target

### Overall

The project is no longer blocked on architecture.
It is now in the stage of dataset quality iteration.

---

## 7. Suggested Next Steps

Recommended order:

1. External review of [train_noisy_v3_100.jsonl](D:\1\train_noisy_v3_100.jsonl)
- check realism
- check recoverability
- check whether typo noise is appropriately light

2. If review is positive, generate a larger noisy validation split
- suggested first expansion: `300` to `900` noisy examples

3. Start `hard` layer design
- focus on integrals
- sums
- PDE / gradient / Hessian
- matrix-heavy expressions
- long physics formulas
- deep-learning formulas with structure corruption

4. Prepare a formal combined validation set
- `clean`
- `noisy`
- later `hard`

---

## 8. Important Constraints / Preferences

- when modifying or running project code, use the `latex` conda environment
- do not operate in `base`
- user prefers being informed quickly when something looks wrong or expensive
- user wants short planning before substantial execution

---

## 9. Current Repository State At Handoff

This handoff file was created after:

- generating `noisy_v3`
- updating [noisy_builder.py](D:\1\noisy_builder.py)

At the time of writing, the intended next action is:

- save the latest work
- push to remote
- let the next reviewer or agent continue from `noisy_v3`


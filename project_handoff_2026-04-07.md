# Project Handoff - 2026-04-07

## 1. Project Goal

This project builds an SFT dataset for a neuro-symbolic LaTeX formula correction system.

Target audience and current assumptions:

- primary target users are Simplified Chinese users
- bilingual support is a later extension, not the current focus
- the goal is robust recovery from messy human input to standard LaTeX

Dataset structure:

- `clean`: high-quality, natural, clear user inputs
- `noisy`: realistic but recoverable messy inputs
- `hard`: longer-tail, more difficult and structurally damaged inputs

---

## 2. Stable Architecture

The project is no longer in exploratory architecture mode.

Current architecture is:

1. [mine_sympy.py](D:\1\mine_sympy.py)
- generates canonical formula records
- includes `standard_latex`
- includes `sympy_expr`
- uses defensive parsing and stores parse failures instead of crashing

2. [data_builder.py](D:\1\data_builder.py)
- builds `clean` training data
- calls Gemini
- preserves canonical LaTeX as `output`
- uses the model only for input-side style generation

3. [noisy_builder.py](D:\1\noisy_builder.py)
- derives rule-based `noisy` samples from `clean` baselines
- now includes surface cleaning and post-filtering

4. local Ollama
- not used for the current dataset generation loop
- reserved for future post-SFT local evaluation

5. [tavily_client.py](D:\1\tavily_client.py)
- used for real-web expression and noise reference collection

---

## 3. Formula Base Status

The formula base pipeline is fixed and usable.

Important files:

- [mine_sympy.py](D:\1\mine_sympy.py)
- [formulas_clean_120.json](D:\1\formulas_clean_120.json)
- [formulas_clean_300.json](D:\1\formulas_clean_300.json)

Current large formula base:

- [formulas_clean_300.json](D:\1\formulas_clean_300.json)
- total formulas: `300`

Current category distribution:

- `stats_ml`: `90`
- `calculus`: `75`
- `physics`: `45`
- `matrix`: `45`
- `algebra_trig`: `45`

This matches the intended domain ratios:

- `stats_ml`: `30%`
- `calculus`: `25%`
- `physics`: `15%`
- `matrix`: `15%`
- `algebra_trig`: `15%`

---

## 4. Clean Layer Status

### First clean baseline

- [train_clean_v1_120.jsonl](D:\1\train_clean_v1_120.jsonl)
- total records: `360`

### Expanded clean set

- [train_clean_v1_300.jsonl](D:\1\train_clean_v1_300.jsonl)
- total records: `900`

Current `train_clean_v1_300.jsonl` distribution:

- `stats_ml`: `270`
- `calculus`: `225`
- `physics`: `135`
- `matrix`: `135`
- `algebra_trig`: `135`

Perspective distribution:

- `beginner`: `300`
- `programmer`: `300`
- `researcher`: `300`

Current judgment:

- `clean` is stable enough for downstream noisy generation
- no urgent need to redesign `clean`

---

## 5. Noisy Layer Status

### Version history

#### `noisy_v1`

- [train_noisy_v1_100.jsonl](D:\1\train_noisy_v1_100.jsonl)

Status:

- useful as review baseline
- too much script smell
- not suitable for direct scaling

#### `noisy_v2`

- [train_noisy_v2_100.jsonl](D:\1\train_noisy_v2_100.jsonl)

Status:

- fixed major Frankenstein-style issues
- judged as "small fixes before scaling"

#### `noisy_v3`

- [train_noisy_v3_100.jsonl](D:\1\train_noisy_v3_100.jsonl)

Status:

- improved shorthand ambiguity and typo realism
- exposed over-corruption issues
- key correction: many ugly samples were not implementation bugs, but rule-level over-corruption

#### `noisy_v4`

Current generator:

- [noisy_builder.py](D:\1\noisy_builder.py)

Key upgrades introduced in `v4`:

- rewritten formula down-mapping logic
- surface cleaning
- post-filter and repair step
- lower corruption strength on complex formulas

Intermediate review asset:

- [train_noisy_v4_300.jsonl](D:\1\train_noisy_v4_300.jsonl)
- [noisy_v4_300_review_sync.md](D:\1\noisy_v4_300_review_sync.md)

Current large noisy set:

- [train_noisy_v4_900.jsonl](D:\1\train_noisy_v4_900.jsonl)
- total records: `900`

Current `train_noisy_v4_900.jsonl` category distribution:

- `stats_ml`: `270`
- `calculus`: `225`
- `physics`: `135`
- `matrix`: `135`
- `algebra_trig`: `135`

Perspective distribution:

- `beginner`: `300`
- `programmer`: `300`
- `researcher`: `300`

Current `noise_rule` distribution:

- `ascii_substitute`: `150`
- `partial_formula_reference`: `140`
- `mixed_language`: `119`
- `operator_confusion`: `117`
- `subscript_loss`: `111`
- `broken_brackets`: `93`
- `keyword_shorthand`: `83`
- `code_fragment_noise`: `49`
- `hat_bar_prime_loss`: `38`

Current judgment:

- `noisy_v4` has crossed the quality gate
- remaining issues are polish, not blockers
- scaling from 100 -> 300 -> 900 has already succeeded

---

## 6. Reference Assets

### Expression-style references

- [expression_reference_sampler.py](D:\1\expression_reference_sampler.py)
- [expression_reference_sample.json](D:\1\expression_reference_sample.json)
- [expression_reference_sample.md](D:\1\expression_reference_sample.md)

Purpose:

- used to tune `clean` prompt style

### Real-noise references

- [noise_reference_sampler.py](D:\1\noise_reference_sampler.py)
- [noise_reference_sample.json](D:\1\noise_reference_sample.json)
- [noise_reference_sample.md](D:\1\noise_reference_sample.md)

Purpose:

- used to derive realistic noisy rule patterns

---

## 7. Review / Alignment Artifacts

- [gemini_audit_cross_review.md](D:\1\gemini_audit_cross_review.md)
- [gemini_noisy_v2_review_prompt.md](D:\1\gemini_noisy_v2_review_prompt.md)
- [noisy_v4_300_review_sync.md](D:\1\noisy_v4_300_review_sync.md)

These files capture:

- where earlier external reviews were correct
- where they overstated bugs vs over-corruption
- how the project re-aligned and improved noisy generation

---

## 8. Current Best Read Of Project State

### Clean

- stable
- sufficiently expanded for current phase

### Noisy

- `v4` is now the mainline
- quality gate has been crossed
- current large validation set exists at `900` records

### Hard

- not implemented yet
- now the most obvious remaining missing dataset layer

### Overall

The project is no longer blocked on architecture or on noisy quality viability.
It has entered the stage of:

- consolidation
- external review alignment
- preparation for larger-scale dataset assembly

---

## 9. Recommended Next Steps

Recommended order from this point:

1. External review of [train_noisy_v4_900.jsonl](D:\1\train_noisy_v4_900.jsonl)
- verify it still looks stable at 900-scale
- identify any remaining polish items

2. Consolidate current dataset state
- decide whether to freeze `clean_v1_300`
- decide whether to freeze `noisy_v4_900`

3. Start `hard` layer design
- integrals
- sums
- PDE / gradient / Hessian
- matrix-heavy expressions
- long physics formulas
- deep-learning formulas with structural corruption

4. Prepare a combined phase-1 validation bundle
- `clean`
- `noisy`
- later `hard`

---

## 10. Important Constraints / Preferences

- when modifying or running project code, use the `latex` conda environment
- do not operate in `base`
- user prefers fast notification if something looks risky, expensive, or blocked
- user wants a short plan before substantial execution

---

## 11. Repository State At Handoff

At the time of this handoff:

- `formulas_clean_300.json` exists
- `train_clean_v1_300.jsonl` exists
- `train_noisy_v4_900.jsonl` exists

Current likely next action:

- save and push the expanded clean/noisy artifacts
- continue with external review alignment or start `hard`


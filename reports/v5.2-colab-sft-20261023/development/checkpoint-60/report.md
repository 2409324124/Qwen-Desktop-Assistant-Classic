# Qwen3-4B LaTeX Correction Evaluation

- total: 56
- input_total: 56 (includes diagnostics)
- diagnostic_total: 0 (excluded from all primary metrics)
- math_accuracy: 0.8571 (faithful mathematical equivalence primary)
- macro_math_accuracy: 0.9212 (each labelled formula group has equal weight)
- grouped_samples: 56; group_count: 4; grouped_coverage: 1.0000
- macro_output_protocol_compliance_accuracy: 0.9881
- macro_math_parse_coverage: 0.9881
- unverified: 8 (equivalence not established; not scored correct)
- raw_math_accuracy: 0.8571
- raw_macro_math_accuracy: 0.9212
- raw_grouped_samples: 56; raw_group_count: 4; raw_grouped_coverage: 1.0000
- raw_exact_accuracy: 0.6071
- raw_format_compliance_accuracy: 0.7857
- raw_output_protocol_compliance_accuracy: 0.9821
- raw_coverage: 1.0000
- postprocessed_math_accuracy: 0.8571
- postprocessed_format_compliance_accuracy: 0.7857
- postprocessed_output_protocol_compliance_accuracy: 0.9821
- postprocessed_exact_accuracy: 0.6071
- format_compliance_accuracy: 0.7857 (correct formula + historical structural format match; not independent protocol compliance)
- output_protocol_compliance_accuracy: 0.9821 (supported single bare formula; independent of correctness)
- semantic_accuracy: 0.8036 (legacy historical diagnostic only)
- symbol_fidelity_accuracy: 0.8036 (legacy historical diagnostic only)
- canonical_accuracy: 0.7857
- exact_accuracy: 0.6071
- normalized_accuracy: 0.7857
- parse_coverage: 0.9821
- math_parse_coverage: 0.9821

## Math Match Levels

| level | count |
| --- | ---: |
| canonical | 10 |
| exact | 34 |
| math_equivalent | 4 |
| math_mismatch | 7 |
| parse_error | 1 |

## Legacy Match Levels

| level | count |
| --- | ---: |
| canonical | 10 |
| commutative_reorder | 1 |
| exact | 34 |
| parse_error | 1 |
| true_mismatch | 10 |

## By Layer

| layer | total | exact | symbol fidelity | semantic | math | format compliance | math accuracy | parse coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| clean | 52 | 32 | 42 | 42 | 45 | 41 | 0.8654 | 1.0000 |
| hard | 3 | 1 | 2 | 2 | 2 | 2 | 0.6667 | 0.6667 |
| noisy | 1 | 1 | 1 | 1 | 1 | 1 | 1.0000 | 1.0000 |

## Postprocessed Formula Groups

| formula_group_id | n | math accuracy | output protocol compliance | parse coverage | math parse coverage |
| --- | ---: | ---: | ---: | ---: | ---: |
| formula:2f1888ebf675fe2145d0 | 2 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| formula:42e053ec5daf6d1ff2d1 | 21 | 0.8571 | 0.9524 | 0.9524 | 0.9524 |
| formula:4341dec926fb2db7ffe1 | 4 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| formula:daa427f99e12e830fc5f | 29 | 0.8276 | 1.0000 | 1.0000 | 1.0000 |

## Raw Formula Groups

| formula_group_id | n | math accuracy | output protocol compliance | parse coverage | math parse coverage |
| --- | ---: | ---: | ---: | ---: | ---: |
| formula:2f1888ebf675fe2145d0 | 2 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| formula:42e053ec5daf6d1ff2d1 | 21 | 0.8571 | 0.9524 | 0.9524 | 0.9524 |
| formula:4341dec926fb2db7ffe1 | 4 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| formula:daa427f99e12e830fc5f | 29 | 0.8276 | 1.0000 | 1.0000 | 1.0000 |

## Math Failure Samples

### 1

- input: A = (a_ij) M x M matrix. showing first two rows and last row, with horiz & vert ellipsis. i.e., [a_11 ... a_1M; a_21 ... a_2M; ...; a_M1 ... a_MM].
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1M} \\ a_{21} & a_{22} & \cdots & a_{2M} \\ \vdots & \vdots & \ddots & \vdots \\ a_{M1} & a_{M2} & \cdots & a_{MM} \end{bmatrix}`
- prediction: `A = \begin{bmatrix} a_{11} & \cdots & a_{1M} \\ a_{21} & \cdots & a_{2M} \\ \vdots & \ddots & \vdots \\ a_{M1} & \cdots & a_{MM} \end{bmatrix}`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 2

- input: def relu(x): return max(0, x)
- expected: `\operatorname{relu}(x) = \max(0, x)`
- prediction: `\text{ReLU}(x) = \max(0, x)`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 3

- input: N x N matrix A. Entries a_ij. Full general form, with all dots. Like a_11 ... a_1N, then vert dots, then a_N1 ... a_NN.
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1N} \\ a_{21} & a_{22} & \cdots & a_{2N} \\ \vdots & \vdots & \ddots & \vdots \\ a_{N1} & a_{N2} & \cdots & a_{NN} \end{bmatrix}`
- prediction: `A = \begin{bmatrix} a_{11} & \cdots & a_{1N} \\ \vdots & \ddots & \vdots \\ a_{N1} & \cdots & a_{NN} \end{bmatrix}`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 4

- input: RNN h_k update: tanh(W*x_k + U*h_prev + b)
- expected: `h_{k} = \tanh(W x_{k} + U h_{\mathrm{prev}} + b)`
- prediction: `h_{k} = \tanh(Wx_{k} + Uh_{k-1} + b)`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 5

- input: A = M-dim square matrix, elements a_ij. Need full matrix display with all ellipses:
	a_11 ... a_1M
	...
	a_M1 ... a_MM. Incl. vertical & diag dots.
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1M} \\ a_{21} & a_{22} & \cdots & a_{2M} \\ \vdots & \vdots & \ddots & \vdots \\ a_{M1} & a_{M2} & \cdots & a_{MM} \end{bmatrix}`
- prediction: `A = \begin{bmatrix} a_{11} & \cdots & a_{1M} \\ \vdots & \ddots & \vdots \\ a_{M1} & \cdots & a_{MM} \end{bmatrix}`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 6

- input: A = [a_jk] for j,k=1...i. Full i x i matrix with ellipsis. Eg. a_11 ... a_1i, a_21 ... a_2i, then vdots & ddots, then a_i1 ... a_ii. 方阵，带点。
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1i} \\ a_{21} & a_{22} & \cdots & a_{2i} \\ \vdots & \vdots & \ddots & \vdots \\ a_{i1} & a_{i2} & \cdots & a_{ii} \end{bmatrix}`
- prediction: `A = \begin{bmatrix} a_{11} & \cdots & a_{1i} \\ a_{21} & \cdots & a_{2i} \\ \vdots & \ddots & \vdots \\ a_{i1} & \cdots & a_{ii} \end{bmatrix}`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 7

- input: N x N matrix A, elements a_ij. 方阵形式，带省略号。Show leading rows/cols, then dots. e.g. A = [a_11 ... a_1n; a_21 ... a_2n; ... ; a_n1 ... a_nn]
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1n} \\ a_{21} & a_{22} & \cdots & a_{2n} \\ \vdots & \vdots & \ddots & \vdots \\ a_{n1} & a_{n2} & \cdots & a_{nn} \end{bmatrix}`
- prediction: `A = \begin{bmatrix} a_{11} & \cdots & a_{1n} \\ a_{21} & \cdots & a_{2n} \\ \vdots & \ddots & \vdots \\ a_{n1} & \cdots & a_{nn} \end{bmatrix}`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 8

- input: dbg Linear Layer with Activation => gamma_hat = sigma(W z + B)
- expected: `\hat{\gamma} = \sigma(W z + B)`
- prediction: `\gamma_{\hat{}} = \sigma(Wz + B)`
- match_level: parse_error
- reason: Expected expression, found } ('}')


## Legacy Semantic Failure Samples

### 1

- input: A = (a_ij) M x M matrix. showing first two rows and last row, with horiz & vert ellipsis. i.e., [a_11 ... a_1M; a_21 ... a_2M; ...; a_M1 ... a_MM].
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1M} \\ a_{21} & a_{22} & \cdots & a_{2M} \\ \vdots & \vdots & \ddots & \vdots \\ a_{M1} & a_{M2} & \cdots & a_{MM} \end{bmatrix}`
- prediction: `A = \begin{bmatrix} a_{11} & \cdots & a_{1M} \\ a_{21} & \cdots & a_{2M} \\ \vdots & \ddots & \vdots \\ a_{M1} & \cdots & a_{MM} \end{bmatrix}`
- match_level: true_mismatch
- reason: true_mismatch

### 2

- input: Coulomb force F: k_e * q1 q2 / r^2
- expected: `F = k_{e} \frac{q_{1} q_{2}}{r^{2}}`
- prediction: `F = \frac{k_{e} q_{1} q_{2}}{r^{2}}`
- match_level: true_mismatch
- reason: true_mismatch

### 3

- input: Coulomb force F, k_e * q1q2 / R^2. Inv sq law. 电荷间作用力.
- expected: `F = k_{e} \frac{q_{1} q_{2}}{R^{2}}`
- prediction: `F = \frac{k_{e} q_{1} q_{2}}{R^{2}}`
- match_level: true_mismatch
- reason: true_mismatch

### 4

- input: N x N matrix A. Entries a_ij. Full general form, with all dots. Like a_11 ... a_1N, then vert dots, then a_N1 ... a_NN.
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1N} \\ a_{21} & a_{22} & \cdots & a_{2N} \\ \vdots & \vdots & \ddots & \vdots \\ a_{N1} & a_{N2} & \cdots & a_{NN} \end{bmatrix}`
- prediction: `A = \begin{bmatrix} a_{11} & \cdots & a_{1N} \\ \vdots & \ddots & \vdots \\ a_{N1} & \cdots & a_{NN} \end{bmatrix}`
- match_level: true_mismatch
- reason: true_mismatch

### 5

- input: RNN h_k update: tanh(W*x_k + U*h_prev + b)
- expected: `h_{k} = \tanh(W x_{k} + U h_{\mathrm{prev}} + b)`
- prediction: `h_{k} = \tanh(Wx_{k} + Uh_{k-1} + b)`
- match_level: true_mismatch
- reason: true_mismatch

### 6

- input: A = M-dim square matrix, elements a_ij. Need full matrix display with all ellipses:
	a_11 ... a_1M
	...
	a_M1 ... a_MM. Incl. vertical & diag dots.
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1M} \\ a_{21} & a_{22} & \cdots & a_{2M} \\ \vdots & \vdots & \ddots & \vdots \\ a_{M1} & a_{M2} & \cdots & a_{MM} \end{bmatrix}`
- prediction: `A = \begin{bmatrix} a_{11} & \cdots & a_{1M} \\ \vdots & \ddots & \vdots \\ a_{M1} & \cdots & a_{MM} \end{bmatrix}`
- match_level: true_mismatch
- reason: true_mismatch

### 7

- input: A = [a_jk] for j,k=1...i. Full i x i matrix with ellipsis. Eg. a_11 ... a_1i, a_21 ... a_2i, then vdots & ddots, then a_i1 ... a_ii. 方阵，带点。
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1i} \\ a_{21} & a_{22} & \cdots & a_{2i} \\ \vdots & \vdots & \ddots & \vdots \\ a_{i1} & a_{i2} & \cdots & a_{ii} \end{bmatrix}`
- prediction: `A = \begin{bmatrix} a_{11} & \cdots & a_{1i} \\ a_{21} & \cdots & a_{2i} \\ \vdots & \ddots & \vdots \\ a_{i1} & \cdots & a_{ii} \end{bmatrix}`
- match_level: true_mismatch
- reason: true_mismatch

### 8

- input: N x N matrix A, elements a_ij. 方阵形式，带省略号。Show leading rows/cols, then dots. e.g. A = [a_11 ... a_1n; a_21 ... a_2n; ... ; a_n1 ... a_nn]
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1n} \\ a_{21} & a_{22} & \cdots & a_{2n} \\ \vdots & \vdots & \ddots & \vdots \\ a_{n1} & a_{n2} & \cdots & a_{nn} \end{bmatrix}`
- prediction: `A = \begin{bmatrix} a_{11} & \cdots & a_{1n} \\ a_{21} & \cdots & a_{2n} \\ \vdots & \ddots & \vdots \\ a_{n1} & \cdots & a_{nn} \end{bmatrix}`
- match_level: true_mismatch
- reason: true_mismatch

### 9

- input: Newton's universal grav. F = G M mu / d^2. G is const, M, mu masses, d dist. Inverse square law.
- expected: `F = G \frac{M \mu}{d^{2}}`
- prediction: `F = \frac{G M \mu}{d^{2}}`
- match_level: true_mismatch
- reason: true_mismatch

### 10

- input: Gravitational F: G * m0*m / R^2. Universal gravity law.
- expected: `F = G \frac{m_{0} m}{R^{2}}`
- prediction: `F = \frac{G m_{0} m}{R^{2}}`
- match_level: true_mismatch
- reason: true_mismatch

### 11

- input: dbg Linear Layer with Activation => gamma_hat = sigma(W z + B)
- expected: `\hat{\gamma} = \sigma(W z + B)`
- prediction: `\gamma_{\hat{}} = \sigma(Wz + B)`
- match_level: parse_error
- reason: Expected expression, found } ('}')

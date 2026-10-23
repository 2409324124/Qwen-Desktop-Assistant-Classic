# Qwen3-4B LaTeX Correction Evaluation

- total: 56
- input_total: 56 (includes diagnostics)
- diagnostic_total: 0 (excluded from all primary metrics)
- math_accuracy: 0.5893 (faithful mathematical equivalence primary)
- macro_math_accuracy: 0.7722 (each labelled formula group has equal weight)
- grouped_samples: 56; group_count: 4; grouped_coverage: 1.0000
- macro_output_protocol_compliance_accuracy: 0.9762
- macro_math_parse_coverage: 0.9762
- unverified: 23 (equivalence not established; not scored correct)
- raw_math_accuracy: 0.5893
- raw_macro_math_accuracy: 0.7722
- raw_grouped_samples: 56; raw_group_count: 4; raw_grouped_coverage: 1.0000
- raw_exact_accuracy: 0.4464
- raw_format_compliance_accuracy: 0.5000
- raw_output_protocol_compliance_accuracy: 0.9643
- raw_coverage: 1.0000
- postprocessed_math_accuracy: 0.5893
- postprocessed_format_compliance_accuracy: 0.5000
- postprocessed_output_protocol_compliance_accuracy: 0.9643
- postprocessed_exact_accuracy: 0.4464
- format_compliance_accuracy: 0.5000 (correct formula + historical structural format match; not independent protocol compliance)
- output_protocol_compliance_accuracy: 0.9643 (supported single bare formula; independent of correctness)
- semantic_accuracy: 0.6071 (legacy historical diagnostic only)
- symbol_fidelity_accuracy: 0.5714 (legacy historical diagnostic only)
- canonical_accuracy: 0.4821
- exact_accuracy: 0.4464
- normalized_accuracy: 0.4821
- parse_coverage: 0.9643
- math_parse_coverage: 0.9643

## Math Match Levels

| level | count |
| --- | ---: |
| canonical | 2 |
| commutative_reorder | 1 |
| exact | 25 |
| math_equivalent | 5 |
| math_mismatch | 21 |
| parse_error | 2 |

## Legacy Match Levels

| level | count |
| --- | ---: |
| alpha_rename | 2 |
| canonical | 2 |
| commutative_reorder | 2 |
| exact | 25 |
| parse_error | 2 |
| style_only | 3 |
| true_mismatch | 20 |

## By Layer

| layer | total | exact | symbol fidelity | semantic | math | format compliance | math accuracy | parse coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| clean | 52 | 23 | 29 | 31 | 31 | 26 | 0.5962 | 0.9808 |
| hard | 3 | 1 | 2 | 2 | 1 | 1 | 0.3333 | 0.6667 |
| noisy | 1 | 1 | 1 | 1 | 1 | 1 | 1.0000 | 1.0000 |

## Postprocessed Formula Groups

| formula_group_id | n | math accuracy | output protocol compliance | parse coverage | math parse coverage |
| --- | ---: | ---: | ---: | ---: | ---: |
| formula:2f1888ebf675fe2145d0 | 2 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| formula:42e053ec5daf6d1ff2d1 | 21 | 0.5714 | 0.9048 | 0.9048 | 0.9048 |
| formula:4341dec926fb2db7ffe1 | 4 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| formula:daa427f99e12e830fc5f | 29 | 0.5172 | 1.0000 | 1.0000 | 1.0000 |

## Raw Formula Groups

| formula_group_id | n | math accuracy | output protocol compliance | parse coverage | math parse coverage |
| --- | ---: | ---: | ---: | ---: | ---: |
| formula:2f1888ebf675fe2145d0 | 2 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| formula:42e053ec5daf6d1ff2d1 | 21 | 0.5714 | 0.9048 | 0.9048 | 0.9048 |
| formula:4341dec926fb2db7ffe1 | 4 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| formula:daa427f99e12e830fc5f | 29 | 0.5172 | 1.0000 | 1.0000 | 1.0000 |

## Math Failure Samples

### 1

- input: A = (a_ij) M x M matrix. showing first two rows and last row, with horiz & vert ellipsis. i.e., [a_11 ... a_1M; a_21 ... a_2M; ...; a_M1 ... a_MM].
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1M} \\ a_{21} & a_{22} & \cdots & a_{2M} \\ \vdots & \vdots & \ddots & \vdots \\ a_{M1} & a_{M2} & \cdots & a_{MM} \end{bmatrix}`
- prediction: `A = \begin{bmatrix} a_{11} & \cdots & a_{1M} \\ a_{21} & \cdots & a_{2M} \\ \vdots & \cdots & \vdots \\ a_{M1} & \cdots & a_{MM} \end{bmatrix}`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 2

- input: M = [[A, B], [C, D]]
- expected: `M = \begin{bmatrix} A & B \\ C & D \end{bmatrix}`
- prediction: `\begin{bmatrix} A & B \\ C & D \end{bmatrix}`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 3

- input: h[N] = tanh(W * x[N] + U * h[N-1] + b)
- expected: `h_{N} = \tanh(W x_{N} + U h_{N-1} + b)`
- prediction: `h[N] = \tanh(W \cdot x[N] + U \cdot h[N-1] + b)`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 4

- input: Block matrix M = [A B; C D]
- expected: `M = \begin{bmatrix} A & B \\ C & D \end{bmatrix}`
- prediction: `\begin{bmatrix} A & B \\ C & D \end{bmatrix}`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 5

- input: N-by-N matrix A. Elements a_ij. Full form with horizontal, vertical, and diagonal ellipses. Shows leading rows/cols and trailing rows/cols. e.g., a_11 to a_nn.
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1n} \\ a_{21} & a_{22} & \cdots & a_{2n} \\ \vdots & \vdots & \ddots & \vdots \\ a_{n1} & a_{n2} & \cdots & a_{nn} \end{bmatrix}`
- prediction: `\begin{bmatrix}
a_{11} & a_{12} & \cdots & a_{1n} \\
a_{21} & a_{22} & \cdots & a_{2n} \\
\vdots & \vdots & \ddots & \vdots \\
a_{n1} & a_{n2} & \cdots & a_{nn}
\end{bmatrix}`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 6

- input: 我想写一个大矩阵M，它里面分成四块，左上角放A，右上角放B，左下角放C，右下角放D，就像一个2乘2的方块组合起来的大矩阵。
- expected: `M = \begin{bmatrix} A & B \\ C & D \end{bmatrix}`
- prediction: `\begin{bmatrix} A & B \\ C & D \end{bmatrix}`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 7

- input: matrix A = [[a_11, a_12, ..., a_1T], [a_21, a_22, ..., a_2T], [..., ..., ..., ...], [a_T1, a_T2, ..., a_TT]]
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1T} \\ a_{21} & a_{22} & \cdots & a_{2T} \\ \vdots & \vdots & \ddots & \vdots \\ a_{T1} & a_{T2} & \cdots & a_{TT} \end{bmatrix}`
- prediction: `\mathbf{A} = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1T} \\ a_{21} & a_{22} & \cdots & a_{2T} \\ \vdots & \vdots & \ddots & \vdots \\ a_{T1} & a_{T2} & \cdots & a_{TT} \end{bmatrix}`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 8

- input: def relu(x): return max(0, x)
- expected: `\operatorname{relu}(x) = \max(0, x)`
- prediction: `\text{ReLU}(x) = \max(0, x)`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 9

- input: N x N matrix A. Entries a_ij. Full general form, with all dots. Like a_11 ... a_1N, then vert dots, then a_N1 ... a_NN.
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1N} \\ a_{21} & a_{22} & \cdots & a_{2N} \\ \vdots & \vdots & \ddots & \vdots \\ a_{N1} & a_{N2} & \cdots & a_{NN} \end{bmatrix}`
- prediction: `\begin{bmatrix}
a_{11} & \cdots & a_{1N} \\
\vdots & \ddots & \vdots \\
a_{N1} & \cdots & a_{NN}
\end{bmatrix}`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 10

- input: h[k] = tanh(W @ x[k] + U @ h[k-1] + b)
- expected: `h_{k} = \tanh(W x_{k} + U h_{k-1} + b)`
- prediction: `h_{k} = \tanh(\mathbf{W} @ \mathbf{x}_{k} + \mathbf{U} @ \mathbf{h}_{k-1} + \mathbf{b})`
- match_level: parse_error
- reason: Expected ), found @ ('@')

### 11

- input: A = M-dim square matrix, elements a_ij. Need full matrix display with all ellipses:
	a_11 ... a_1M
	...
	a_M1 ... a_MM. Incl. vertical & diag dots.
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1M} \\ a_{21} & a_{22} & \cdots & a_{2M} \\ \vdots & \vdots & \ddots & \vdots \\ a_{M1} & a_{M2} & \cdots & a_{MM} \end{bmatrix}`
- prediction: `\begin{bmatrix}
a_{11} & \cdots & a_{1M} \\
\vdots & \ddots & \vdots \\
a_{M1} & \cdots & a_{MM}
\end{bmatrix}`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 12

- input: 我想打一个矩阵，它叫A，方括号那种。里面是a开头带下标的元素。第一行是a11, a12，然后有省略号，到a1j。第二行是a21, a22，也是省略号到a2j。然后中间几行就用省略号代替了，最后一行是aj1, aj2，同样省略号到ajj。就是那种中间带点点的方阵。
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1j} \\ a_{21} & a_{22} & \cdots & a_{2j} \\ \vdots & \vdots & \ddots & \vdots \\ a_{j1} & a_{j2} & \cdots & a_{jj} \end{bmatrix}`
- prediction: `\begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1j} \\ a_{21} & a_{22} & \cdots & a_{2j} \\ \vdots & \vdots & \ddots & \vdots \\ a_{j1} & a_{j2} & \cdots & a_{jj} \end{bmatrix}`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 13

- input: ReLU(v) def: max(0,v). If v<0, output 0. Else, output v.
- expected: `\text{ReLU}(v) = \max(0, v)`
- prediction: `\text{ReLU}(\nu) = \max(0, \nu)`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 14

- input: A = [a_jk] for j,k=1...i. Full i x i matrix with ellipsis. Eg. a_11 ... a_1i, a_21 ... a_2i, then vdots & ddots, then a_i1 ... a_ii. 方阵，带点。
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1i} \\ a_{21} & a_{22} & \cdots & a_{2i} \\ \vdots & \vdots & \ddots & \vdots \\ a_{i1} & a_{i2} & \cdots & a_{ii} \end{bmatrix}`
- prediction: `A = \begin{bmatrix} a_{11} & \cdots & a_{1i} \\ a_{21} & \cdots & a_{2i} \\ \vdots & \ddots & \vdots \\ a_{i1} & \cdots & a_{ii} \end{bmatrix}`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 15

- input: N x N matrix A, elements a_ij. 方阵形式，带省略号。Show leading rows/cols, then dots. e.g. A = [a_11 ... a_1n; a_21 ... a_2n; ... ; a_n1 ... a_nn]
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1n} \\ a_{21} & a_{22} & \cdots & a_{2n} \\ \vdots & \vdots & \ddots & \vdots \\ a_{n1} & a_{n2} & \cdots & a_{nn} \end{bmatrix}`
- prediction: `A = \begin{bmatrix} a_{11} & \cdots & a_{1n} \\ a_{21} & \cdots & a_{2n} \\ \vdots & \ddots & \vdots \\ a_{n1} & \cdots & a_{nn} \end{bmatrix}`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 16

- input: matrix A of size i by i. elements A[r][c] = a_rc. structure: [[a_11, a_12, ..., a_1i], [a_21, a_22, ..., a_2i], ..., [a_i1, a_i2, ..., a_ii]]. use '...' for omitted elements and rows/cols, including diagonal.
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1i} \\ a_{21} & a_{22} & \cdots & a_{2i} \\ \vdots & \vdots & \ddots & \vdots \\ a_{i1} & a_{i2} & \cdots & a_{ii} \end{bmatrix}`
- prediction: `\begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1i} \\ a_{21} & a_{22} & \cdots & a_{2i} \\ \vdots & \vdots & \ddots & \vdots \\ a_{i1} & a_{i2} & \cdots & a_{ii} \end{bmatrix}`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 17

- input: 我想问下那个机器学习的公式，就是输入xi先乘上权重V，然后再加上偏置beta，最后整个结果再套个激活函数sigma，得到输出phi hat的那个公式是怎么表示的？
- expected: `\hat{\phi} = \sigma(V \xi + \beta)`
- prediction: `\hat{\phi} = \sigma(\mathbf{V} \xi + \beta)`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 18

- input: h[j] = tanh(W * x[j] + U * h[j-1] + b)
- expected: `h_{j} = \tanh(W x_{j} + U h_{j-1} + b)`
- prediction: `h_{j} = \tanh\left(W \cdot x_{j} + U \cdot h_{j-1} + b\right)`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 19

- input: 我想打一个N乘N的方阵A，它里面的元素都是a带下标的。第一行是a11, a12，然后省略号，一直到a1n。第二行类似，a21, a22，省略号到a2n。然后中间好几行都用一个垂直的省略号表示。最后一行是an1, an2，省略号到ann。中间的对角线上也有省略号。
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1n} \\ a_{21} & a_{22} & \cdots & a_{2n} \\ \vdots & \vdots & \ddots & \vdots \\ a_{n1} & a_{n2} & \cdots & a_{nn} \end{bmatrix}`
- prediction: `\begin{bmatrix}
a_{11} & a_{12} & \cdots & a_{1n} \\
a_{21} & a_{22} & \cdots & a_{2n} \\
\vdots & \vdots & \ddots & \vdots \\
a_{n1} & a_{n2} & \cdots & a_{nn}
\end{bmatrix}`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules

### 20

- input: ReLU(y) = max(0, y) for activation.
- expected: `\text{ReLU}(y) = \max(0, y)`
- prediction: `\text{ReLU}(\xi) = \max(0, \xi)`
- match_level: math_mismatch
- reason: Equivalence was not established under symbol/type/scope-preserving rules


## Legacy Semantic Failure Samples

### 1

- input: A = (a_ij) M x M matrix. showing first two rows and last row, with horiz & vert ellipsis. i.e., [a_11 ... a_1M; a_21 ... a_2M; ...; a_M1 ... a_MM].
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1M} \\ a_{21} & a_{22} & \cdots & a_{2M} \\ \vdots & \vdots & \ddots & \vdots \\ a_{M1} & a_{M2} & \cdots & a_{MM} \end{bmatrix}`
- prediction: `A = \begin{bmatrix} a_{11} & \cdots & a_{1M} \\ a_{21} & \cdots & a_{2M} \\ \vdots & \cdots & \vdots \\ a_{M1} & \cdots & a_{MM} \end{bmatrix}`
- match_level: true_mismatch
- reason: true_mismatch

### 2

- input: M = [[A, B], [C, D]]
- expected: `M = \begin{bmatrix} A & B \\ C & D \end{bmatrix}`
- prediction: `\begin{bmatrix} A & B \\ C & D \end{bmatrix}`
- match_level: true_mismatch
- reason: true_mismatch

### 3

- input: Coulomb force F: k_e * q1 q2 / r^2
- expected: `F = k_{e} \frac{q_{1} q_{2}}{r^{2}}`
- prediction: `F = \frac{k_{e} q_{1} q_{2}}{r^{2}}`
- match_level: true_mismatch
- reason: true_mismatch

### 4

- input: h[N] = tanh(W * x[N] + U * h[N-1] + b)
- expected: `h_{N} = \tanh(W x_{N} + U h_{N-1} + b)`
- prediction: `h[N] = \tanh(W \cdot x[N] + U \cdot h[N-1] + b)`
- match_level: true_mismatch
- reason: true_mismatch

### 5

- input: Block matrix M = [A B; C D]
- expected: `M = \begin{bmatrix} A & B \\ C & D \end{bmatrix}`
- prediction: `\begin{bmatrix} A & B \\ C & D \end{bmatrix}`
- match_level: true_mismatch
- reason: true_mismatch

### 6

- input: N-by-N matrix A. Elements a_ij. Full form with horizontal, vertical, and diagonal ellipses. Shows leading rows/cols and trailing rows/cols. e.g., a_11 to a_nn.
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1n} \\ a_{21} & a_{22} & \cdots & a_{2n} \\ \vdots & \vdots & \ddots & \vdots \\ a_{n1} & a_{n2} & \cdots & a_{nn} \end{bmatrix}`
- prediction: `\begin{bmatrix}
a_{11} & a_{12} & \cdots & a_{1n} \\
a_{21} & a_{22} & \cdots & a_{2n} \\
\vdots & \vdots & \ddots & \vdots \\
a_{n1} & a_{n2} & \cdots & a_{nn}
\end{bmatrix}`
- match_level: true_mismatch
- reason: true_mismatch

### 7

- input: 我想写一个大矩阵M，它里面分成四块，左上角放A，右上角放B，左下角放C，右下角放D，就像一个2乘2的方块组合起来的大矩阵。
- expected: `M = \begin{bmatrix} A & B \\ C & D \end{bmatrix}`
- prediction: `\begin{bmatrix} A & B \\ C & D \end{bmatrix}`
- match_level: true_mismatch
- reason: true_mismatch

### 8

- input: Coulomb force F, k_e * q1q2 / R^2. Inv sq law. 电荷间作用力.
- expected: `F = k_{e} \frac{q_{1} q_{2}}{R^{2}}`
- prediction: `F = \frac{k_{e} q_{1} q_{2}}{R^{2}}`
- match_level: true_mismatch
- reason: true_mismatch

### 9

- input: N x N matrix A. Entries a_ij. Full general form, with all dots. Like a_11 ... a_1N, then vert dots, then a_N1 ... a_NN.
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1N} \\ a_{21} & a_{22} & \cdots & a_{2N} \\ \vdots & \vdots & \ddots & \vdots \\ a_{N1} & a_{N2} & \cdots & a_{NN} \end{bmatrix}`
- prediction: `\begin{bmatrix}
a_{11} & \cdots & a_{1N} \\
\vdots & \ddots & \vdots \\
a_{N1} & \cdots & a_{NN}
\end{bmatrix}`
- match_level: true_mismatch
- reason: true_mismatch

### 10

- input: RNN h_k update: tanh(W*x_k + U*h_prev + b)
- expected: `h_{k} = \tanh(W x_{k} + U h_{\mathrm{prev}} + b)`
- prediction: `h_{k} = \tanh(W x_{k} + U h_{\text{prev}} + b)`
- match_level: true_mismatch
- reason: true_mismatch

### 11

- input: h[k] = tanh(W @ x[k] + U @ h[k-1] + b)
- expected: `h_{k} = \tanh(W x_{k} + U h_{k-1} + b)`
- prediction: `h_{k} = \tanh(\mathbf{W} @ \mathbf{x}_{k} + \mathbf{U} @ \mathbf{h}_{k-1} + \mathbf{b})`
- match_level: parse_error
- reason: Expected ), found @ ('@')

### 12

- input: A = M-dim square matrix, elements a_ij. Need full matrix display with all ellipses:
	a_11 ... a_1M
	...
	a_M1 ... a_MM. Incl. vertical & diag dots.
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1M} \\ a_{21} & a_{22} & \cdots & a_{2M} \\ \vdots & \vdots & \ddots & \vdots \\ a_{M1} & a_{M2} & \cdots & a_{MM} \end{bmatrix}`
- prediction: `\begin{bmatrix}
a_{11} & \cdots & a_{1M} \\
\vdots & \ddots & \vdots \\
a_{M1} & \cdots & a_{MM}
\end{bmatrix}`
- match_level: true_mismatch
- reason: true_mismatch

### 13

- input: 我想打一个矩阵，它叫A，方括号那种。里面是a开头带下标的元素。第一行是a11, a12，然后有省略号，到a1j。第二行是a21, a22，也是省略号到a2j。然后中间几行就用省略号代替了，最后一行是aj1, aj2，同样省略号到ajj。就是那种中间带点点的方阵。
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1j} \\ a_{21} & a_{22} & \cdots & a_{2j} \\ \vdots & \vdots & \ddots & \vdots \\ a_{j1} & a_{j2} & \cdots & a_{jj} \end{bmatrix}`
- prediction: `\begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1j} \\ a_{21} & a_{22} & \cdots & a_{2j} \\ \vdots & \vdots & \ddots & \vdots \\ a_{j1} & a_{j2} & \cdots & a_{jj} \end{bmatrix}`
- match_level: true_mismatch
- reason: true_mismatch

### 14

- input: A = [a_jk] for j,k=1...i. Full i x i matrix with ellipsis. Eg. a_11 ... a_1i, a_21 ... a_2i, then vdots & ddots, then a_i1 ... a_ii. 方阵，带点。
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1i} \\ a_{21} & a_{22} & \cdots & a_{2i} \\ \vdots & \vdots & \ddots & \vdots \\ a_{i1} & a_{i2} & \cdots & a_{ii} \end{bmatrix}`
- prediction: `A = \begin{bmatrix} a_{11} & \cdots & a_{1i} \\ a_{21} & \cdots & a_{2i} \\ \vdots & \ddots & \vdots \\ a_{i1} & \cdots & a_{ii} \end{bmatrix}`
- match_level: true_mismatch
- reason: true_mismatch

### 15

- input: N x N matrix A, elements a_ij. 方阵形式，带省略号。Show leading rows/cols, then dots. e.g. A = [a_11 ... a_1n; a_21 ... a_2n; ... ; a_n1 ... a_nn]
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1n} \\ a_{21} & a_{22} & \cdots & a_{2n} \\ \vdots & \vdots & \ddots & \vdots \\ a_{n1} & a_{n2} & \cdots & a_{nn} \end{bmatrix}`
- prediction: `A = \begin{bmatrix} a_{11} & \cdots & a_{1n} \\ a_{21} & \cdots & a_{2n} \\ \vdots & \ddots & \vdots \\ a_{n1} & \cdots & a_{nn} \end{bmatrix}`
- match_level: true_mismatch
- reason: true_mismatch

### 16

- input: matrix A of size i by i. elements A[r][c] = a_rc. structure: [[a_11, a_12, ..., a_1i], [a_21, a_22, ..., a_2i], ..., [a_i1, a_i2, ..., a_ii]]. use '...' for omitted elements and rows/cols, including diagonal.
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1i} \\ a_{21} & a_{22} & \cdots & a_{2i} \\ \vdots & \vdots & \ddots & \vdots \\ a_{i1} & a_{i2} & \cdots & a_{ii} \end{bmatrix}`
- prediction: `\begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1i} \\ a_{21} & a_{22} & \cdots & a_{2i} \\ \vdots & \vdots & \ddots & \vdots \\ a_{i1} & a_{i2} & \cdots & a_{ii} \end{bmatrix}`
- match_level: true_mismatch
- reason: true_mismatch

### 17

- input: Newton's universal grav. F = G M mu / d^2. G is const, M, mu masses, d dist. Inverse square law.
- expected: `F = G \frac{M \mu}{d^{2}}`
- prediction: `F = \frac{G M \mu}{d^{2}}`
- match_level: true_mismatch
- reason: true_mismatch

### 18

- input: h[j] = tanh(W * x[j] + U * h[j-1] + b)
- expected: `h_{j} = \tanh(W x_{j} + U h_{j-1} + b)`
- prediction: `h_{j} = \tanh\left(W \cdot x_{j} + U \cdot h_{j-1} + b\right)`
- match_level: true_mismatch
- reason: true_mismatch

### 19

- input: Gravitational F: G * m0*m / R^2. Universal gravity law.
- expected: `F = G \frac{m_{0} m}{R^{2}}`
- prediction: `F = \frac{G m_{0} m}{R^{2}}`
- match_level: true_mismatch
- reason: true_mismatch

### 20

- input: 我想打一个N乘N的方阵A，它里面的元素都是a带下标的。第一行是a11, a12，然后省略号，一直到a1n。第二行类似，a21, a22，省略号到a2n。然后中间好几行都用一个垂直的省略号表示。最后一行是an1, an2，省略号到ann。中间的对角线上也有省略号。
- expected: `A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1n} \\ a_{21} & a_{22} & \cdots & a_{2n} \\ \vdots & \vdots & \ddots & \vdots \\ a_{n1} & a_{n2} & \cdots & a_{nn} \end{bmatrix}`
- prediction: `\begin{bmatrix}
a_{11} & a_{12} & \cdots & a_{1n} \\
a_{21} & a_{22} & \cdots & a_{2n} \\
\vdots & \vdots & \ddots & \vdots \\
a_{n1} & a_{n2} & \cdots & a_{nn}
\end{bmatrix}`
- match_level: true_mismatch
- reason: true_mismatch

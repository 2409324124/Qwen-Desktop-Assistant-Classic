# 真实噪声表达采样摘要

这份文档用于提炼 noisy 层规则，不直接作为训练数据。

## 覆盖分布

- `algebra_trig`: 1
- `calculus`: 2
- `matrix`: 2
- `physics`: 1
- `stats_ml`: 4

## Softmax Function

- Category: `stats_ml`
- Formula: `\text{Softmax}(\gamma_{k}) = \frac{\exp(\gamma_{k})}{\sum_j \exp(\gamma_j)}`

### messy_nl | Softmax Function formula how do I type this

- Answer Summary: The softmax of a vector \(x=(x_1,\dots ,x_K)\) is defined by \(s_i=\frac{\exp(x_i)}{\sum_{j=1}^{K}\exp(x_j)}\) (often written with a temperature \(\beta\) as \(s_i=\frac{\exp(\beta x_i)}{\sum_{j=1}^{K}\exp(\beta x_j)}\)), which you can type in LaTeX as `s_i = \frac{\exp(x_i)}{\sum_{j=1}^{K}\exp(x_j)}` (or with \(\beta\) as `s_i = \frac{\exp(\beta x_i)}{\sum_{j=1}^{K}\exp(\beta x_j)}`), in plain text as `s_i = exp(x_i) / sum_j exp(x_j)`, and in Python/Numpy as `def softmax(x): e = np.exp(x); return e / e.sum()`.
- [A Simple Explanation of the Softmax Function - victorzhou.com](https://victorzhou.com/blog/softmax/)
  Snippet: Victor Zhou  #### Victor Zhou  # A Simple Explanation of the Softmax Function  ## What Softmax is, how it's used, and how to implement it in Python.  | UPDATED  Softmax turns arbitrary real values into probabilities, which are often useful in Machine Learning. The math behind ...
- [The Softmax function and its derivative - Eli Bendersky's website](https://eli.thegreenplace.net/2016/the-softmax-function-and-its-derivative/)
  Snippet: Where D is also an arbitrary constant. This formula is equivalent to the original for any D, so we're free to choose a D that will make our computation better numerically. A good choice is the maximum between all inputs, negated:  This will shift the inputs to a range close to...
- [Softmax function - Wikipedia](https://en.wikipedia.org/wiki/Softmax_function)
  Snippet: ``` >>> import  numpy  as  np>>> z = np. array([1.0,2.0,3.0,4.0,1.0,2.0,3.0])>>> beta =1.0>>> np. exp(beta z)/ np. sum(np. exp(beta z))array([0.02364054, 0.06426166, 0.1746813, 0.474833, 0.02364054, 0.06426166, 0.1746813]) ```  ## Alternatives  [edit]  The softmax function gen...

### messy_nl | Softmax Function 这个公式怎么打

- Answer Summary: 在 LaTeX 中常用的 Softmax 公式写法是：\displaystyle \text{softmax}(x)_i \;=\; \frac{e^{x_i}}{\sum_{j=1}^{n} e^{x_j}}，其中 \(x_i\) 是第 i 个输入值，\(n\) 为输入向量的维度，分子使用指数函数 \(e^{x_i}\)，分母是所有输入指数值的求和，以确保输出为概率分布。要在文档中插入该公式，可直接使用 `\[\text{softmax}(x)_i = \frac{e^{x_i}}{\sum_{j=1}^{n} e^{x_j}}\]` 或在行内使用 `$\text{softmax}(x)_i = \frac{e^{x_i}}{\sum_{j=1}^{n} e^{x_j}}$`。
- [A Simple Explanation of the Softmax Function - victorzhou.com](https://victorzhou.com/blog/softmax/)
  Snippet: Victor Zhou  #### Victor Zhou  # A Simple Explanation of the Softmax Function  ## What Softmax is, how it's used, and how to implement it in Python.  | UPDATED  Softmax turns arbitrary real values into probabilities, which are often useful in Machine Learning. The math behind ...
- [Softmax function - Wikipedia](https://en.wikipedia.org/wiki/Softmax_function)
  Snippet: ``` >>> import  numpy  as  np>>> z = np. array([1.0,2.0,3.0,4.0,1.0,2.0,3.0])>>> beta =1.0>>> np. exp(beta z)/ np. sum(np. exp(beta z))array([0.02364054, 0.06426166, 0.1746813, 0.474833, 0.02364054, 0.06426166, 0.1746813]) ```  ## Alternatives  [edit]  The softmax function gen...
- [Understanding the Softmax Activation Function - SingleStore](https://www.singlestore.com/blog/a-guide-to-softmax-activation-function/)
  Snippet: .png?width=1024&disable=upscale&auto=webp)  The softmax function, often used in the final layer of a neural network model for classification tasks, converts raw output scores — also known as logits — into probabilities by taking the exponential of each output and normalizing t...

### plain_text | Softmax Function plain text formula notation

- Answer Summary: The softmax function maps a vector z = (z₁,…,z_K) to a probability distribution whose i‑th component is given by σ(z_i) = exp(z_i) / ∑_{j=1}^{K} exp(z_j).
- [Softmax function - Wikipedia](https://en.wikipedia.org/wiki/Softmax_function)
  Snippet: In words, the softmax applies the standard exponential function to each element  of the input tuple  (consisting of  real numbers), and normalizes these values by dividing by the sum of all these exponentials. The normalization ensures that the sum of the components of the out...
- [Softmax Activation Function in Neural Networks - GeeksforGeeks](https://www.geeksforgeeks.org/deep-learning/the-role-of-softmax-in-neural-networks-detailed-explanation-and-applications/)
  Snippet: ## Softmax Function  For a given vector, z = [z\_1, z\_2, \dots, z\_n]the Softmax function is defined as:  > \sigma(z\_i) = \frac{e^{z\_i}}{\sum\_{j=1}^{n} e^{z\_j}}  where:   e^{z\_j}: Exponentiation of the input value.  \sum\_{j=1}^{n} e^{z\_j}: Sum of all exponentiated valu...
- [[PDF] The softmax function: Properties, motivation, and interpretation*](https://alpslab.stanford.edu/papers/FrankeDegen_submitted.pdf)
  Snippet: 2 The deﬁnition of the softmax function is:2 SM(s; α) = p, with: pi = exp (α si) P j exp (α sj) Authors often use a simpler notation, omitting the normalizing constant Z = P j exp (α sj), to just write: pi ∝exp (α si) The softmax function has a softmax parameter α ∈R, which is...

### plain_text | Softmax Function keyboard formula input

- Answer Summary: The softmax function maps a vector z = (z₁,…,z_K) to a probability distribution σ(z) whose i‑th component is given by σ(z)_i = exp(z_i) / ∑_{j=1}^{K} exp(z_j), and a numerically stable variant is σ(z)_i = exp(z_i − max(z)) / ∑_{j=1}^{K} exp(z_j − max(z)).
- [Softmax function - Wikipedia](https://en.wikipedia.org/wiki/Softmax_function)
  Snippet: ## Example  [edit]  With an input of (1, 2, 3, 4, 1, 2, 3), the softmax is approximately (0.024, 0.064, 0.175, 0.475, 0.024, 0.064, 0.175). The output has most of its weight where the "4" was in the original input. This is what the function is normally used for: to highlight t...
- [Accurately Computing the Softmax Function - Nick Higham](https://nhigham.com/2020/02/03/accurately-computing-the-softmax-function/)
  Snippet: Nick Higham  Applied mathematics, numerical linear algebra and software.  # Accurately Computing the Softmax Function  The softmax function takes as input an n-vector x and returns a vector g(x) with elements  n x g(x)  g_j(x) = \displaystyle\frac{\mathrm{e}^{x_j}}{\sum_{i=1}^...
- [Softmax Function Definition - DeepAI](https://deepai.org/machine-learning-glossary-and-terms/softmax-layer)
  Snippet: DeepAI  avatar  # Softmax Function  ## What is the Softmax Function?  The softmax function is a function that turns a vector of K real values into a vector of K real values that sum to 1. The input values can be positive, negative, zero, or greater than one, but the softmax tr...

### latex_help | Softmax Function latex help input notation

- Answer Summary: Use the standard notation \(\mathbf{z}=(z_{1},\dots ,z_{K})\) for the input vector and define the soft‑max as the component‑wise function  
\[
\operatorname{softmax}(\mathbf{z})_{i}= \frac{\exp(z_{i})}{\sum_{j=1}^{K}\exp(z_{j})},
\qquad i=1,\dots ,K,
\]  
or, in compact vector form,  
\[
\operatorname{softmax}(\mathbf{z})=\frac{\exp(\mathbf{z})}{\mathbf{1}^{\!\top}\exp(\mathbf{z})},
\]  
where \(\exp(\mathbf{z})\) is applied element‑wise and \(\mathbf{1}\) is a column vector of ones. If a temperature \(T>0\) is desired, replace \(z_{i}\) by \(z_{i}/T\) (or equivalently multiply the exponentials by \(1/T\)):  
\[
\operatorname{softmax}_{T}(\mathbf{z})_{i}= \frac{\exp\!\bigl(z_{i}/T\bigr)}{\sum_{j=1}^{K}\exp\!\bigl(z_{j}/T\bigr)}.
\]  
In LaTeX you can write these formulas inside an equation environment, e.g.  

\[
\begin{equation}
\sigma(\mathbf{z})_{i}= \frac{e^{z_{i}}}{\sum_{j=1}^{K} e^{z_{j}}}
\end{equation}
\]  

and use \verb|\operatorname{softmax}| or simply \verb|\sigma| as the function name.
- [Softmax activation function - TeX - LaTeX Stack Exchange](https://tex.stackexchange.com/questions/612601/softmax-activation-function)
  Snippet: enter image description here  enter image description here  Please help me check if the plot looks alright since I hardly know anything about the softmax function.  Some immature words:  It is `pgfplots` commit `d2fbb2a` that led to the error  `pgfplots` `d2fbb2a`  ! Package P...
- [Softmax function - Wikipedia](https://en.wikipedia.org/wiki/Softmax_function)
  Snippet: ## Example  [edit]  With an input of (1, 2, 3, 4, 1, 2, 3), the softmax is approximately (0.024, 0.064, 0.175, 0.475, 0.024, 0.064, 0.175). The output has most of its weight where the "4" was in the original input. This is what the function is normally used for: to highlight t...
- [Softmax Activation Function: Everything You Need to Know - Pinecone](https://www.pinecone.io/learn/softmax-activation/)
  Snippet: In fact, you can think of the softmax function as a vector generalization of the sigmoid activation. We’ll revisit this later to confirm that for binary classification—when N = 2—the softmax and sigmoid activations are equivalent.  ### Limitations of the Argmax Function  The a...

### latex_help | Softmax Function latex 写法 求助

- Answer Summary: 在 LaTeX 中可以使用如下写法表示 Softmax 函数的公式，例如对向量 \(\mathbf{z}=(z_1,\dots ,z_N)\) 的第 \(i\) 个分量取值为  
\[
\operatorname{softmax}(\mathbf{z})_i \;=\; \frac{\exp(z_i)}{\displaystyle\sum_{j=1}^{N}\exp(z_j)}\,,\qquad i=1,\dots ,N,
\]  
其中 \(\exp(z_i)\) 也可以写成 \(e^{z_i}\)。若只需要行内形式，可写成 \(\mathrm{softmax}(z)_i = \frac{e^{z_i}}{\sum_{j} e^{z_j}}\)。
- [tikz pgf - Softmax activation function](https://tex.stackexchange.com/questions/612601/softmax-activation-function)
  Snippet: `/pgf/fpu=true` `/pgf/fpu/output format=fixed` `\pgfplotsforeachungrouped` `\pgfmathsubtract@` `\pgfplotsforeachungroupeduniform@`  Here I employed the possibly easiest change: restrict the scope of `/pgf/fpu/output format=fixed`. In a bigger picture, perhaps the `\pgfplotsfor...
- [三分钟读懂Softmax函数 - 腾讯云](https://cloud.tencent.com/developer/article/1676286)
  Snippet: 比如，仍然用刚才那个NumPy实现的简单的Softmax：  `b = np.array([20, 300, 5000]) softmax(b)`  会报错：  `RuntimeWarning: overflow encountered in exp return np.exp(x) / np.sum(np.exp(x), axis=0)`  一个简单的办法是，先求得输入向量的最大值，然后所有向量都减去这个最大值：  参考资料  本文分享自 皮皮鲁的AI星球 微信公众号，前往查看  如有侵权，请联系 cloudcommunity@tencent.c...
- [A Simple Explanation of the Softmax Function - victorzhou.com](https://victorzhou.com/blog/softmax/)
  Snippet: Victor Zhou  #### Victor Zhou  # A Simple Explanation of the Softmax Function  ## What Softmax is, how it's used, and how to implement it in Python.  | UPDATED  Softmax turns arbitrary real values into probabilities, which are often useful in Machine Learning. The math behind ...

### mixed_language | Softmax Function 中文 英文 混合 公式 写法

- Answer Summary: Softmax函数将一个未归一化的向量 \(\mathbf{o} = (o_1, o_2, \dots, o_K)\) 映射为概率分布 \(\hat{\mathbf{y}} = (\hat{y}_1, \hat{y}_2, \dots, \hat{y}_K)\)，其混合中英文写法为：\[\hat{y}_j = \frac{\exp(o_j)}{\sum_{k=1}^{K}\exp(o_k)}\quad (j=1,\dots,K),\]其中 \(\exp(\cdot)\) 表示指数函数，分子保证非负，分母对所有指数值求和实现归一化，使得 \(0\le \hat{y}_j\le1\) 且 \(\sum_{j=1}^{K}\hat{y}_j = 1\)，可直接解释为每个类别的预测概率。
- [什么是Softmax？函数、公式与AI应用 - Ultralytics](https://www.ultralytics.com/zh/glossary/softmax)
  Snippet: Softmax 通过执行两个主要操作来解决这个问题：  1. 指数运算：它计算每个输入数字的指数。这一步确保所有值都是非负的（因为 $e^x$ 始终为正），并惩罚远低于最大值的值，同时突出最大的分数。 2. 归一化：它将这些指数化值求和，然后将每个单独的指数值除以这个总和。这个归一化过程对数值进行缩放，使其代表整体的一部分，从而使开发人员能够将其解释为百分比置信度分数。  ## 实际应用  输出清晰概率的能力使Softmax在各个行业和 机器学习 (ML)任务中不可或缺。   图像分类：在计算机视觉中，模型使用 Softmax 对图像进行分类。例如...
- [一分钟理解softmax函数（超简单） - CSDN博客](https://blog.csdn.net/lz_peter/article/details/84574716)
  Snippet: # 一分钟理解softmax函数（超简单）  做过多分类任务的同学一定都知道softmax函数。softmax函数，又称归一化指数函数。它是二分类函数sigmoid在多分类上的推广，目的是将多分类的结果以概率的形式展现出来。下图展示了softmax的计算方法：  下面为大家解释一下为什么softmax是这种形式。  首先，我们知道概率有两个性质：1）预测的概率为非负数；2）各种预测结果概率之和等于1。  softmax就是将在负无穷到正无穷上的预测结果按照这两步转换为概率的。  1）将预测结果转化为非负数  下图为y=exp(x）的图像，我们可以知...
- [3.4. softmax回归 - 动手学深度学习](https://zh.d2l.ai/chapter_linear-networks/softmax-regression.html)
  Snippet: 然而我们能否将未规范化的预测\(o\)直接视作我们感兴趣的输出呢？ 答案是否定的。 因为将线性层的输出直接视为概率时存在一些问题： 一方面，我们没有限制这些输出数字的总和为1。 另一方面，根据输入的不同，它们可以为负值。 这些违反了 2.6节中所说的概率基本公理。  要将输出视为概率，我们必须保证在任何数据上的输出都是非负的且总和为1。 此外，我们需要一个训练的目标函数，来激励模型精准地估计概率。 例如， 在分类器输出0.5的所有样本中，我们希望这些样本是刚好有一半实际上属于预测的类别。 这个属性叫做校准（calibration）。  社会科学家邓...

### mixed_language | Softmax Function formula notes shorthand mixed language

- Answer Summary: The soft‑max transform maps a vector \(z=(z_{1},…,z_{K})\) of arbitrary real scores to a probability distribution \(\sigma(z)=(\sigma_{1},…,σ_{K})\) by the compact formula \(\displaystyle \sigma_{i}(z)=\frac{\exp(\beta\,z_{i})}{\sum_{j=1}^{K}\exp(\beta\,z_{j})}\), where the scalar \(\beta\) (often written as \(1/\tau\) with \(\tau\) the temperature) controls the “sharpness’’ of the output – \(\beta>0\) (or low \(\tau\)) yields the usual maximum‑convention in machine‑learning, while \(\beta<0\) (high \(\tau\)) corresponds to the minimum‑convention used in statistical‑mechanics; setting \(\beta=0\) (or \(\tau\to\infty\)) gives the uniform distribution. In practice the most common shorthand omits \(\beta\) and writes \(\sigma_{i}(z)=\frac{e^{z_{i}}}{\sum_{j}e^{z_{j}}}\). The log‑softmax variant is \(\log\sigma_{i}(z)=z_{i}-\log\!\sum_{j}e^{z_{j}}\), and its gradient has the simple closed form \(\partial\sigma_{i}/\partial z_{j}=σ_{i}(\delta_{ij}-σ_{j})\).
- [Deriving the Softmax from First Principles - will wolf](https://willwolf.io/2017/04/19/deriving-the-softmax-from-first-principles/)
  Snippet: To ensure that all unnormalized probabilities are positive, we must first pass them through a function that takes as input a real number and produces as output a strictly positive real number. This is simply an exponent; let's choose Euler's number (\(e\))) for now. The ration...
- [Softmax function - Wikipedia](https://en.wikipedia.org/wiki/Softmax_function)
  Snippet: ## Notes  [edit]  1. ^ Positive β corresponds to the maximum convention, and is usual in machine learning, corresponding to the highest score having highest probability. The negative −β corresponds to the minimum convention, and is conventional in thermodynamics, corresponding...
- [A Simple Explanation of the Softmax Function - victorzhou.com](https://victorzhou.com/blog/softmax/)
  Snippet: Victor Zhou  #### Victor Zhou  # A Simple Explanation of the Softmax Function  ## What Softmax is, how it's used, and how to implement it in Python.  | UPDATED  Softmax turns arbitrary real values into probabilities, which are often useful in Machine Learning. The math behind ...

## ReLU Activation Function

- Category: `stats_ml`
- Formula: `\text{ReLU}(\theta) = \max(0, \theta)`

### messy_nl | ReLU Activation Function formula how do I type this

- Answer Summary: The ReLU activation function is defined as \(f(x)=\max(0,x)\), which can be typed in LaTeX as `f(x)=\max(0,x)` or expressed piece‑wise as \(f(x)=\begin{cases}x & \text{if } x>0\\0 & \text{if } x\le 0\end{cases}\) (plain‑text form: “if input > 0 return input else return 0”).
- [ReLU Activation Function in Deep Learning - GeeksforGeeks](https://www.geeksforgeeks.org/deep-learning/relu-activation-function-in-deep-learning/)
  Snippet: The formula for Exponential Linear Unit (ELU) is:  \text{ELU}(x) = \begin{cases} x & \text{if } x \geq 0 \\ \alpha (\exp(x) - 1) & \text{if } x < 0 \end{cases}  Where:   x is the input.  \alpha is a positive constant that defines the value for negative inputs (often set to 1)....
- [ReLU Activation Function Explained - Built In](https://builtin.com/machine-learning/relu-activation-function)
  Snippet: The ReLU activation function is differentiable at all points except at zero. For values greater than zero, we just consider the max of the function. This can be written as:  ``` f(x) = max{0, z} ```  In simple terms, this can also be written as follows:  ``` if input > 0:    r...
- [A Gentle Introduction to the Rectified Linear Unit (ReLU)](https://www.machinelearningmastery.com/rectified-linear-activation-function-for-deep-learning-neural-networks/)
  Snippet: indeed, you can also write it as relu = lambda x: max(x,0)  ELU still faces potential saturation for negative inputs. But is it more preferable to sigmoid because only one side may saturate?   PReLU doesn’t seem to have such an issue. Is it probably more preferred than ELU?  H...

### messy_nl | ReLU Activation Function 这个公式怎么打

- Answer Summary: ReLU（Rectified Linear Unit）的公式可以写成 LaTeX 形式的两种常见写法：  

$$f(x)=\max(0,\,x)$$  

或等价的分段写法  

$$f(x)=\begin{cases}x & \text{if } x>0\\[4pt]0 & \text{if } x\le 0\end{cases}$$
- [ReLU Activation Function in Deep Learning - GeeksforGeeks](https://www.geeksforgeeks.org/deep-learning/relu-activation-function-in-deep-learning/)
  Snippet: The formula for Exponential Linear Unit (ELU) is:  \text{ELU}(x) = \begin{cases} x & \text{if } x \geq 0 \\ \alpha (\exp(x) - 1) & \text{if } x < 0 \end{cases}  Where:   x is the input.  \alpha is a positive constant that defines the value for negative inputs (often set to 1)....
- [ReLU Activation Function Explained - Built In](https://builtin.com/machine-learning/relu-activation-function)
  Snippet: The ReLU activation function is differentiable at all points except at zero. For values greater than zero, we just consider the max of the function. This can be written as:  ``` f(x) = max{0, z} ```  In simple terms, this can also be written as follows:  ``` if input > 0:    r...
- [An Introduction to Rectified Linear Unit (ReLU) | Great Learning](https://www.mygreatlearning.com/blog/relu-activation-function/)
  Snippet: ## What is ReLU Activation Function?  ReLU stands for rectified linear activation unit and is considered one of the few milestones in the deep learning revolution. It is simple yet really better than its predecessor activation functions such as sigmoid or tanh.  #### ReLU acti...

### plain_text | ReLU Activation Function plain text formula notation

- Answer Summary: The ReLU (Rectified Linear Unit) activation function is defined as f(x)=max(0, x), which can also be written in piecewise form as f(x)= x if x > 0, otherwise f(x)= 0.
- [ReLU Activation Function in Deep Learning - GeeksforGeeks](https://www.geeksforgeeks.org/deep-learning/relu-activation-function-in-deep-learning/)
  Snippet: In simpler terms, ReLU allows positive values to pass through unchanged while setting all negative values to zero. This helps the neural network maintain the necessary complexity to learn patterns while avoiding some of the pitfalls associated with other activation functions, ...
- [ReLU Activation Function Explained - Built In](https://builtin.com/machine-learning/relu-activation-function)
  Snippet: The ReLU activation function is differentiable at all points except at zero. For values greater than zero, we just consider the max of the function. This can be written as:  ``` f(x) = max{0, z} ```  In simple terms, this can also be written as follows:  ``` if input > 0:    r...
- [An Introduction to Rectified Linear Unit (ReLU) | Great Learning](https://www.mygreatlearning.com/blog/relu-activation-function/)
  Snippet: ## What is ReLU Activation Function?  ReLU stands for rectified linear activation unit and is considered one of the few milestones in the deep learning revolution. It is simple yet really better than its predecessor activation functions such as sigmoid or tanh.  #### ReLU acti...

### plain_text | ReLU Activation Function keyboard formula input

- Answer Summary: The ReLU (Rectified Linear Unit) activation function is defined by the simple piece‑wise expression f(x)=max(0, x), meaning the output equals the input x when x is positive and zero otherwise; its derivative is 0 for x < 0 and 1 for x > 0 (undefined at exactly 0). Common keyboard‑friendly forms of this rule are written as f(x)=max(0,x) or as an if‑else statement: if x>0 return x else return 0. Variants modify the negative slope: Leaky ReLU uses f(x)=max(0.01 x, x) (typically α=0.01), while Parametric ReLU replaces the fixed coefficient with a learnable parameter α, giving f(x)=max(α x, x) with derivative α for x < 0 and 1 for x ≥ 0.
- [ReLU Activation Function in Deep Learning - GeeksforGeeks](https://www.geeksforgeeks.org/deep-learning/relu-activation-function-in-deep-learning/)
  Snippet: The formula for Exponential Linear Unit (ELU) is:  \text{ELU}(x) = \begin{cases} x & \text{if } x \geq 0 \\ \alpha (\exp(x) - 1) & \text{if } x < 0 \end{cases}  Where:   x is the input.  \alpha is a positive constant that defines the value for negative inputs (often set to 1)....
- [ReLU Activation Function Explained - Built In](https://builtin.com/machine-learning/relu-activation-function)
  Snippet: The ReLU activation function is differentiable at all points except at zero. For values greater than zero, we just consider the max of the function. This can be written as:  ``` f(x) = max{0, z} ```  In simple terms, this can also be written as follows:  ``` if input > 0:    r...
- [ReLU Activation Function and Its Variants | Python Kitchen](https://www.pythonkitchen.com/relu-activation-function-and-its-variants/)
  Snippet: # ReLU Activation Function  The full form of the term ReLU is the rectified linear unit. ReLU is the activation function that is most widely used in neural network architectures.  The equation for the ReLU activation function is:  > F(x) = max(0,x)  which tells that if the inp...

### latex_help | ReLU Activation Function latex help input notation

- Answer Summary: The ReLU activation is usually written in LaTeX as $\operatorname{ReLU}(x)=\max\{0,\,x\}$ or equivalently $\sigma(x)=\max(0,x)$, and for a vector input $\mathbf{x}\in\mathbb{R}^d$ one writes $\mathbf{h}= \operatorname{ReLU}(\mathbf{W}\mathbf{x}+\mathbf{b})$, where $\mathbf{W}$ and $\mathbf{b}$ are the weight matrix and bias vector of the layer and the max operator is applied element‑wise.
- [[PDF] Suggested Notation for Machine Learning](https://ctan.math.utah.edu/ctan/tex-archive/macros/latex/contrib/mlmath/mlmath.pdf)
  Snippet: 4 11 Notation table symbol meaning L A T EX simplied x input \bm{x} \vx y output, label \bm{y} \vy d input dimension d do output dimension d_{\rm o} n number of samples n X instances domain (a set) \mathcal{X} \fX Y labels domain (a set) \mathcal{Y} \fY Z = X × Y example domai...
- [Exploring Activation Functions in Deep Learning - DevOps.dev](https://blog.devops.dev/exploring-activation-functions-in-deep-learning-properties-derivatives-and-impact-on-model-7585aad8a757)
  Snippet: # Create a range of input values 10 10 400 # Apply the binary step function to the input # Plot the function 8 6 'Binary Step Function' 'blue' 0 'black''--''Threshold (x=0)' 1 'gray''--' 0 'gray''--' 'Binary Step Activation Function''Input (x)''Output (f(x))' True ``` [...] Ou...
- [ReLU Activation Function Explained - Built In](https://builtin.com/machine-learning/relu-activation-function)
  Snippet: The ReLU activation function is differentiable at all points except at zero. For values greater than zero, we just consider the max of the function. This can be written as:  ``` f(x) = max{0, z} ```  In simple terms, this can also be written as follows:  ``` if input > 0:    r...

### latex_help | ReLU Activation Function latex 写法 求助

- Answer Summary: 在 LaTeX 中常用的 ReLU 表达式可以写成 $f(x)=\max(0,x)$，若需要分段写法则写作 $f(x)=\begin{cases}x & \text{if } x>0\\[4pt]0 & \text{if } x\le 0\end{cases}$，也可以用 \verb|\operatorname{ReLU}(x)| 或 \verb|\text{ReLU}(x)| 来标记函数名，例如 \verb|$\operatorname{ReLU}(x)=\max(0,x)$|。
- [ReLU Activation Function Explained - Built In](https://builtin.com/machine-learning/relu-activation-function)
  Snippet: The ReLU activation function is differentiable at all points except at zero. For values greater than zero, we just consider the max of the function. This can be written as:  ``` f(x) = max{0, z} ```  In simple terms, this can also be written as follows:  ``` if input > 0:    r...
- [ReLU Activation Function in Deep Learning - GeeksforGeeks](https://www.geeksforgeeks.org/deep-learning/relu-activation-function-in-deep-learning/)
  Snippet: In simpler terms, ReLU allows positive values to pass through unchanged while setting all negative values to zero. This helps the neural network maintain the necessary complexity to learn patterns while avoiding some of the pitfalls associated with other activation functions, ...
- [An Introduction to Rectified Linear Unit (ReLU) | Great Learning](https://www.mygreatlearning.com/blog/relu-activation-function/)
  Snippet: ## What is ReLU Activation Function?  ReLU stands for rectified linear activation unit and is considered one of the few milestones in the deep learning revolution. It is simple yet really better than its predecessor activation functions such as sigmoid or tanh.  #### ReLU acti...

### mixed_language | ReLU Activation Function 中文 英文 混合 公式 写法

- Answer Summary: ReLU（Rectified Linear Unit）激活函数的数学表达式通常写作 f(x)=\max(0, x) ，即 f(x)=\begin{cases}x, & x>0\\0, & x\le 0\end{cases}，其中 x 为神经元的线性加权和；当 x 为正时输出本身 x （线性），为零或负时输出 0 （截断），这种“修正线性”形式在中文文献中常以 “ReLU函数 f(x)=\max(0,x) 或分段写法” 说明。
- [深度学习笔记V – 激活函数ReLU - ReLU Activation Function - Steemit](https://steemit.com/cn/@victory622/v-relu-relu-activation-function)
  Snippet: The rectifier activation function allows a network to easily obtain sparse representations. For example, after uniform initialization of the weights, around 50% of hidden units continuous output values are real zeros, and this fraction can easily increase with sparsity-inducin...
- [ReLU激活函数 - ApX Machine Learning](https://apxml.com/zh/courses/introduction-to-deep-learning/chapter-2-activation-functions-architecture/relu-activation)
  Snippet: ApX 标志 ApX 标志  趋近智  所有课程  # 修正线性单元 (ReLU)  修正线性单元，通常称为ReLU，为Sigmoid和Tanh等其他非线性激活函数 (activation function)提供了一种更简单但效果很好的替代方案。虽然Sigmoid和Tanh等函数引入了非线性，但它们可能存在饱和和梯度消失等潜在弊端。由于其计算效率高以及能够缓解一些梯度问题，ReLU已成为深度学习 (deep learning)中，特别是隐藏层中的常用方法。  ReLU函数在数学上的定义为：  简单来说，如果输入xxx为正，函数输出xxx本身。如果输...
- [线性整流函数 - 机器之心](https://www.jiqizhixin.com/graph/technologies/65877f4d-0482-4a66-9bbb-f8b7f19a17ab)
  Snippet: # 线性整流函数  线性整流函数（Rectified Linear Unit, ReLU）,又称修正线性单元, 是一种人工神经网络中常用的激活函数（activation function），通常指代以斜坡函数及其变种为代表的非线性函数。比较常用的线性整流函数有斜坡函数f(x)=max(0, x)，以及带泄露整流函数 (Leaky ReLU)，其中x为神经元(Neuron)的输入。  来源：维基百科  线性整流函数（Rectified Linear Unit, ReLU）,又称修正线性单元,是一种人工神经网络中常用的激活函数（activation f...

### mixed_language | ReLU Activation Function formula notes shorthand mixed language

- Answer Summary: The Rectified Linear Unit (ReLU) activation is defined by the concise formula f(x)=max(0,x), which can also be written in piece‑wise form as f(x)= { x if x>0, 0 if x≤0 }; its derivative is f′(x)=1 for x>0 and 0 otherwise, giving an output range of [0,∞) and making it computationally cheap and effective at mitigating the vanishing‑gradient problem, though it can suffer from the “dying ReLU” issue where neurons output zero permanently; a common remedy is the Leaky ReLU variant f(x)=x if x>0 else αx (typically α≈0.01), which retains a small gradient for negative inputs—Nota: ReLU se escribe como f(x)=max(0,x) y es ampliamente usada en capas ocultas de redes neuronales profundas.
- [ReLU Activation Function in Deep Learning - GeeksforGeeks](https://www.geeksforgeeks.org/deep-learning/relu-activation-function-in-deep-learning/)
  Snippet: | Activation Function | Formula | Output Range | Advantages | Disadvantages | Use Case |  ---  ---  --- | | ReLU | f(x) = \max(0, x) | 0, ∞) | - Simple and computationally efficient | - Dying ReLU problem (neurons stop learning) | Hidden layers of deep networks | | - Helps mit...
- [ReLU Activation Function Explained - Built In](https://builtin.com/machine-learning/relu-activation-function)
  Snippet: The ReLU activation function is differentiable at all points except at zero. For values greater than zero, we just consider the max of the function. This can be written as:  ``` f(x) = max{0, z} ```  In simple terms, this can also be written as follows:  ``` if input > 0:    r...
- [The ReLU Activation Function: Powering Modern Neural Networks](https://codesignal.com/learn/courses/the-mlp-architecture-activations-initialization/lessons/the-relu-activation-function-powering-modern-neural-networks-1)
  Snippet: The ReLU Activation Function  The Rectified Linear Unit (ReLU) is perhaps the simplest non-linear activation function, yet it has revolutionized deep learning. Its mathematical definition is elegantly straightforward:  f(x)=max(0,x)  In plain English: `ReLU` outputs the input ...

## Limit Definition of Derivative

- Category: `calculus`
- Formula: `f'(\xi) = \lim_{h \to 0} \frac{f(\xi + h) - f(\xi)}{h}`

### messy_nl | Limit Definition of Derivative formula how do I type this

- Answer Summary: The limit definition of the derivative is written as f′(x)=lim₍ₕ→0₎ [f(x+h)−f(x)]/h, which in plain‑text can be typed as f'(x) = lim_{h->0} (f(x+h)-f(x))/h, and in LaTeX or markdown math mode as \[
f'(x)=\lim_{h\to 0}\frac{f(x+h)-f(x)}{h}
\] (an equivalent form using the point a is f'(a)=\lim_{h\to0}[f(a+h)-f(a)]/h or \lim_{x\to a}[f(x)-f(a)]/(x-a)).
- [Definition of the Derivative - YouTube](https://www.youtube.com/watch?v=-aTLjoDT1GQ)
  Snippet: In this video, we're going to talk about how to find the derivative using the definition of the derivative formula. So basically, we need to find the derivative of a function using the limit process. And frime of x represents the derivative of f ofx. And it's equal to the limi...
- [Derivative - Wikipedia](https://en.wikipedia.org/wiki/Derivative)
  Snippet: A function of a real variable {\displaystyle f(x)} is differentiable at a point {\displaystyle a} of its domain, if its domain contains an open interval containing ⁠{\displaystyle a}⁠, and the limit "Limit (mathematics)") {\displaystyle L=\lim _{h\to 0}{\frac {f(a+h)-f(a)}{h}}...
- [Calculus I - The Definition of the Derivative - Pauls Online Math Notes](https://tutorial.math.lamar.edu/classes/calci/defnofderivative.aspx)
  Snippet: \[f'\left( x \right) = y' = \frac{{df}}{{dx}} = \frac{{dy}}{{dx}} = \frac{d}{{dx}}\left( {f\left( x \right)} \right) = \frac{d}{{dx}}\left( y \right)\]  Because we also need to evaluate derivatives on occasion we also need a notation for evaluating derivatives when using the f...

### messy_nl | Limit Definition of Derivative 这个公式怎么打

- Answer Summary: 要在常用的排版或计算软件中输入导数的极限定义公式，可以使用 LaTeX 语法：  
```latex
f'(x)=\lim_{h\to 0}\frac{f(x+h)-f(x)}{h}
```  
如果想写成微分形式，则为  
```latex
\frac{df}{dx}=\lim_{h\to 0}\frac{f(x+h)-f(x)}{h}
```  
在 Word、Google Docs 或其他支持公式编辑的环境里，只需插入公式框并粘贴上述 LaTeX 代码，或在相应的公式编辑器中手动输入 “lim_{h→0} (f(x+h)-f(x))/h”。这样即可完整地呈现导数的极限定义。
- [Definition of the Derivative - YouTube](https://www.youtube.com/watch?v=-aTLjoDT1GQ)
  Snippet: everything into this formula. So it's going to be the limit as h approaches zero and then it's going to be 5 x + h - 4 and then minus f ofx which fx is 5x - 4. And so we're going to divide all of this by h. Now let's simplify. So first we need to distribute five to x + h. And ...
- [Derivative - Wikipedia](https://en.wikipedia.org/wiki/Derivative)
  Snippet: A function of a real variable {\displaystyle f(x)} is differentiable at a point {\displaystyle a} of its domain, if its domain contains an open interval containing ⁠{\displaystyle a}⁠, and the limit "Limit (mathematics)") {\displaystyle L=\lim _{h\to 0}{\frac {f(a+h)-f(a)}{h}}...
- [Derivatives - Calculus, Meaning, Interpretation](https://www.cuemath.com/calculus/derivatives/)
  Snippet: ## Derivative of a Function Using the First Principle  The derivative of a function can be obtained by the limit definition of derivative which is f'(x) = limh→0 [f(x + h) - f(x) / h. This process is known as the differentiation by the first principle. Let f(x) = x2 and we wil...

### plain_text | Limit Definition of Derivative plain text formula notation

- Answer Summary: The derivative of a function f at a point x (or at a) is defined by the limit f′(x)=limₕ→0 [ f(x + h) − f(x) ] / h, which can also be written as f′(a)=lim_{x→a} [ f(x) − f(a) ] / (x − a).
- [Definition of the Derivative - YouTube](https://www.youtube.com/watch?v=-aTLjoDT1GQ)
  Snippet: In this video, we're going to talk about how to find the derivative using the definition of the derivative formula. So basically, we need to find the derivative of a function using the limit process. And frime of x represents the derivative of f ofx. And it's equal to the limi...
- [Derivative - Wikipedia](https://en.wikipedia.org/wiki/Derivative)
  Snippet: A function of a real variable {\displaystyle f(x)} is differentiable at a point {\displaystyle a} of its domain, if its domain contains an open interval containing ⁠{\displaystyle a}⁠, and the limit "Limit (mathematics)") {\displaystyle L=\lim _{h\to 0}{\frac {f(a+h)-f(a)}{h}}...
- [Calculus I - The Definition of the Derivative - Pauls Online Math Notes](https://tutorial.math.lamar.edu/classes/calci/defnofderivative.aspx)
  Snippet: \[\mathop {\lim }\limits\_{x \to 0} f\left( x \right) = \mathop {\lim }\limits\_{x \to 0} \left| x \right| = 0 = f\left( 0 \right)\]  So, \(f\left( x \right) = \left| x \right|\) is continuous at \(x = 0\) but we’ve just shown above in Example 4 that \(f\left( x \right) = \lef...

### plain_text | Limit Definition of Derivative keyboard formula input

- Answer Summary: The derivative of a function f at a point x (or at a) is defined by the limit f′(x)=lim₍ₕ→0₎[f(x+ₕ)−f(x)]/ₕ, which is equivalently written as f′(a)=lim₍ₓ→a₎[f(x)−f(a)]/(x−a).
- [Calculus I - The Definition of the Derivative - Pauls Online Math Notes](https://tutorial.math.lamar.edu/classes/calci/defnofderivative.aspx)
  Snippet: \[\mathop {\lim }\limits\_{x \to a} \frac{{f\left( x \right) - f\left( a \right)}}{{x - a}}\]  We also saw that with a small change of notation this limit could also be written as,  \[\begin{equation}\mathop {\lim }\limits\_{h \to 0} \frac{{f\left( {a + h} \right) - f\left( a ...
- [3.2 Using derivatives to evaluate limits - Active Calculus](https://activecalculus.org/single/sec-3-2-LHR.html)
  Snippet: 🔗    🔗  🔗  ### Subsection 3.2.1 Introduction  Because differential calculus is based on the definition of the derivative, and the definition of the derivative involves a limit, there is a sense in which all of calculus rests on limits. In addition, the limit involved in the de...
- [Calculating Derivatives](https://www2.math.uconn.edu/~stein/virtual/Notes/differentiation.html)
  Snippet: The first group of formulas, which is used almost without thought, may be expressed as:  1. The derivative of a constant times a function equals the contant times the derivative of the function. 2. The derivative of a sum equals the sum of the derivatives. 3. The derivative of...

### latex_help | Limit Definition of Derivative latex help input notation

- Answer Summary: To write the limit definition of the derivative in LaTeX you can use either form \[\displaystyle f'(a)=\lim_{h\to 0}\frac{f(a+h)-f(a)}{h}\] or the equivalent \[\displaystyle f'(a)=\lim_{x\to a}\frac{f(x)-f(a)}{x-a}\]; the command \verb|\lim_{h\to 0}| produces the limit, \verb|\frac{...}{...}| creates the fraction, and you can display the result inline with \verb|$f'(a)=\lim_{h\to 0}\frac{f(a+h)-f(a)}{h}$| or use the fractional notation \verb|\frac{df}{dx}\big|_{x=a}| for evaluation at \(x=a\).
- [Derivative - Wikipedia](https://en.wikipedia.org/wiki/Derivative)
  Snippet: If the function {\displaystyle f} is differentiable at ⁠{\displaystyle a}⁠, that is if the limit {\displaystyle L} exists, then this limit is called the derivative of {\displaystyle f} at ⁠{\displaystyle a}⁠. Multiple notations for the derivative exist. The derivative of {\dis...
- [Calculus I - The Definition of the Derivative - Pauls Online Math Notes](https://tutorial.math.lamar.edu/classes/calci/defnofderivative.aspx)
  Snippet: \[\mathop {\lim }\limits\_{x \to 0} f\left( x \right) = \mathop {\lim }\limits\_{x \to 0} \left| x \right| = 0 = f\left( 0 \right)\]  So, \(f\left( x \right) = \left| x \right|\) is continuous at \(x = 0\) but we’ve just shown above in Example 4 that \(f\left( x \right) = \lef...
- [LateX Derivatives, Limits, Sums, Products and Integrals](https://www.math-linux.com/latex/faq/latex-faq/article/latex-derivatives-limits-sums-products-and-integrals)
  Snippet: ## Latex derivative  How to write LateX Derivatives ?  | Definition | Latex code | Result |  ---  | First order derivative | f’(x) | \(f'(x)\) | | Second order derivative | f’‘(x) | \(f''(x)\) | | K-th order derivative | f^{(k)}(x) | \(f^{(k)}(x)\) | | Partial firt order deriv...

### latex_help | Limit Definition of Derivative latex 写法 求助

- Answer Summary: 在 LaTeX 中，导数的极限定义常写作  
\[
f'(x)=\lim_{h\to 0}\frac{f(x+h)-f(x)}{h},
\]  
对应的代码为 `\displaystyle f'(x)=\lim_{h\to 0}\frac{f(x+h)-f(x)}{h}`；若写成在点 \(a\) 处的导数，则为  
\[
f'(a)=\lim_{x\to a}\frac{f(x)-f(a)}{x-a},
\]  
代码为 `\displaystyle f'(a)=\lim_{x\to a}\frac{f(x)-f(a)}{x-a}`，其中 `\lim_{...}` 用来表示极限，`\frac{...}{...}` 表示分数，`\to` 表示趋向，`\displaystyle` 可放在行间公式或在 `$$...$$` 环境中使用，使符号以显示样式呈现。
- [LateX Derivatives, Limits, Sums, Products and Integrals](https://www.math-linux.com/latex/faq/latex-faq/article/latex-derivatives-limits-sums-products-and-integrals)
  Snippet: ## Latex limit  How to write LateX Limits?  | Definition | Latex code | Result |  ---  | Limit at plus infinity | \lim\_{x \to +\infty} f(x) | \(\displaystyle\lim\_{x \to +\infty} f(x)\) | | Limit at minus infinity | \lim\_{x \to -\infty} f(x) | \(\displaystyle\lim\_{x \to -\i...
- [[PDF] The derivative package](https://ctan.math.illinois.edu/macros/latex/contrib/derivative/derivative.pdf)
  Snippet: 6 [⟨keyval list⟩]{⟨function⟩}/{⟨variables⟩}_{⟨point1⟩}^{⟨point2⟩} \odv Updated: v1.1 In this package, the ordinary derivative is defined with an upright lowercase d if the package option upright=true is used. Otherwise, it is defined with an italic lowercase d. This choice was...
- [[PDF] 一份(不太)简短的LATEX2ε 介绍](https://ftp.math.utah.edu/pub/texlive/Contents/live/texmf-dist/doc/latex/lshort-chinese/lshort-zh-cn.pdf)
  Snippet: 界限。 4 第一章 L A T EX 须知 • 反斜线和后面的单个非字母符号，如\$。 要注意L AT EX 命令是对大小写敏感的，比如输入\LaTeX 命令可以生成错落有致的L AT EX 字母组合，但输入\Latex 或者\LaTex 什么都得不到，还会报错。 字母形式的L AT EX 命令忽略其后的所有空格。如果要人为引入空格，需要在命令后面加一 对括号阻止其忽略空格2： Shall we call ourselves \TeX users or \TeX{} users?

### mixed_language | Limit Definition of Derivative 中文 英文 混合 公式 写法

- Answer Summary: 导数的极限定义可以用中英文混合的方式写成  
$$f'(a)=\lim_{h\to0}\frac{f(a+h)-f(a)}{h} \;=\;\lim_{\Delta x\to0}\frac{f(x+\Delta x)-f(x)}{\Delta x},$$  
其中 \(h\)（或 \(\Delta x\)）表示自变量的增量，趋近于零时的商即函数在点 \(a\)（或 \(x\)）的瞬时变化率；常用符号还有 \(f'(a)\)、\(\displaystyle \left.\frac{dy}{dx}\right|_{x=a}\) 或 \(\displaystyle Df(a)\)，它们都代表同一概念——在该点的导数。
- [[PDF] 導數函數](https://www.math.ntu.edu.tw/~mathcal/download/precal/PPT/Chapter%2002_08.pdf)
  Snippet: 範例五 17 17 同樣，對於x < 0 ，|x| = – x ，此時我們也同樣取h 足夠小 使得x + h < 0 ，此時由極限之定義有： 因此對任意x < 0 ，f 亦可微。 範例五/ 解 cont’d 18 18 剩下最後一個點x = 0 ，我們計算導數的極限： 由於取絕對值在h > 0 與h < 0 結果不同，分左右極限： 範例五/ 解 cont’d 19 19 由於左右極限值並不相同，因此f’(0) 並不存在，是故f 只在 所有不為0 的點可微。 我們可以寫下這樣的導函數表示式： 注意到定義域只在{x: x≠0} ，其函數圖形 如右圖所示...
- [DERIVATIVE in Simplified Chinese - Cambridge Dictionary](https://dictionary.cambridge.org/dictionary/english-chinese-simplified/derivative)
  Snippet: Cambridge Dictionary AI icon Cambridge Dictionary Online  # Translation of derivative – English–Mandarin Chinese dictionary  Your browser doesn't support HTML5 audio  Your browser doesn't support HTML5 audio  Your browser doesn't support HTML5 audio  Your browser doesn't suppo...
- [[PDF] index English to Chinese](https://lsa.umich.edu/content/dam/math-assets/math-document/english-to-chinese/index%20English%20to%20Chinese-Cal1&2.pdf)
  Snippet: function theorem 减函数定理 definite integral 定积分 degree of a polynomial 多项式次数 degree-days 日度差 Delta 德尔塔 demand curve 需求曲线 density 密度 density function 密度函数 dependent function 关联函数 dependent variable 相关变量 depreciation 贬值 derivative 导数 chain rule 连锁法则 critical points 驻点 differentiabi...

### mixed_language | Limit Definition of Derivative formula notes shorthand mixed language

- Answer Summary: The derivative of a function f at a point x is defined as the limit of the difference quotient, written in shorthand as \(f'(x)=\displaystyle\lim_{\Delta x\to0}\frac{f(x+\Delta x)-f(x)}{\Delta x}\), which is equivalently expressed with the variable h as \(f'(a)=\displaystyle\lim_{h\to0}\frac{f(a+h)-f(a)}{h}\); this limit, when it exists, gives the instantaneous rate of change of f with respect to x and is also denoted by \(\frac{df}{dx}\).
- [Limit Definition of the Derivative – Calculus Tutorials](https://math.hmc.edu/calculus/hmc-mathematics-calculus-online-tutorials/single-variable-calculus/limit-definition-of-the-derivative/)
  Snippet: #### Notes  The limit definition of the derivative is used to prove many well-known results, including the following:   If $f$ is differentiable at $x\_0$, then $f$ is continuous at $x\_0$.  Differentiation of polynomials: $\displaystyle \frac{d}{dx}\left[x^n\right]=nx^{n-1}$....
- [Calculus I - The Definition of the Derivative - Pauls Online Math Notes](https://tutorial.math.lamar.edu/classes/calci/defnofderivative.aspx)
  Snippet: \[\begin{align\}f'\left( x \right) & = \mathop {\lim }\limits\_{h \to 0} \frac{{2{x^2} + 4xh + 2{h^2} - 16x - 16h + 35 - 2{x^2} + 16x - 35}}{h}\\ & = \mathop {\lim }\limits\_{h \to 0} \frac{{4xh + 2{h^2} - 16h}}{h}\end{align\}\]  Notice that every term in the numerator that di...
- [3.3: Differentiation Rules - Mathematics LibreTexts](https://math.libretexts.org/Bookshelves/Calculus/Calculus_(OpenStax)/03%3A_Derivatives/3.03%3A_Differentiation_Rules)
  Snippet: That is,  \[\text{if }p(x)=f(x)g(x),\quad \text{then }p′(x)=f′(x)g(x)+g′(x)f(x).\nonumber \]  This means that the derivative of a product of two functions is the derivative of the first function times the second function plus the derivative of the second function times the fir...

## Fundamental Theorem of Calculus

- Category: `calculus`
- Formula: `\int_{a}^{b} f(z) dz = F(b) - F(a)`

### messy_nl | Fundamental Theorem of Calculus formula how do I type this

- Answer Summary: The Fundamental Theorem of Calculus is expressed in two parts: Part 1 states that if \(F(x)=\int_{a}^{x}f(t)\,dt\) for a continuous function \(f\) on \([a,b]\), then the derivative of \(F\) is the original integrand, \(F'(x)=f(x)\) for all \(x\) in \([a,b]\); in LaTeX this is typed as `F(x)=\int_{a}^{x} f(t)\,dt` and `F'(x)=f(x)`. Part 2 (the evaluation theorem) says that if \(F\) is any antiderivative of \(f\) (i.e., \(F'(x)=f(x)\)), then the definite integral from \(a\) to \(b\) can be computed by the difference of the antiderivative at the endpoints: \(\int_{a}^{b} f(x)\,dx = F(b)-F(a)\), which in LaTeX is written as `\int_{a}^{b} f(x)\,dx = F(b)-F(a)`.
- [The Fundamental Theorem of Calculus](https://www2.math.uconn.edu/ClassHomePages/Math1071/Textbook/sec_Ch5Sec3.html)
  Snippet: then \(F'(x)=f(x)\) over \([a,b].\)  Before we delve into the proof, a couple of subtleties are worth mentioning here. First, a comment on the notation. Note that we have defined a function, \(F(x),\) as the definite integral of another function, \(f(t),\) from the point \(a\)...
- [5.3: The Fundamental Theorem of Calculus - Mathematics LibreTexts](https://math.libretexts.org/Bookshelves/Calculus/Calculus_(OpenStax)/05%3A_Integration/5.03%3A_The_Fundamental_Theorem_of_Calculus)
  Snippet: then \(F′(x)=f(x)\) over \([a,b]\).  Before we delve into the proof, a couple of subtleties are worth mentioning here. First, a comment on the notation. Note that we have defined a function, \(F(x)\), as the definite integral of another function, \(f(t)\), from the point \(a\)...
- [Fundamental Theorem of Calculus - First(Part 1), Second(Part 2)](https://www.cuemath.com/calculus/fundamental-theorem-of-calculus/)
  Snippet: ### Fundamental Theorem of Calculus Formula  The fundamental theorem of calculus has two formulas:  Let us learn in detail about each of these theorems along with their proofs.  ## First Fundamental Theorem of Calculus (Part 1)  The first fundamental theorem of calculus(FTC Pa...

### messy_nl | Fundamental Theorem of Calculus 这个公式怎么打

- Answer Summary: 在 LaTeX 中可以用下面的代码输入基本形式的微积分基本定理：  
\[
\int_{a}^{b} f(x)\,dx = F(b)-F(a)
\]  
以及它的等价写法  
\[
F(x)=\int_{a}^{x} f(t)\,dt,\qquad F'(x)=f(x)
\]  
其中 `\int_{a}^{b}` 表示上下限的定积分，`\,,` 在 `dx` 前加一个小空格，`F(b)-F(a)` 表示在上、下限处求原函数的差值。只需在文档的数学环境（如 `\( … \)`、`\[ … \]` 或 `equation` 环境）中插入上述代码即可。
- [5.3: The Fundamental Theorem of Calculus Basics](https://math.libretexts.org/Courses/Monroe_Community_College/MTH_210_Calculus_I_(Professor_Dean)/Chapter_5%3A_Integration/5.3%3A__The_Fundamental_Theorem_of_Calculus_Basics)
  Snippet: then \(F′(x)=f(x)\) over \([a,b]\).  A couple of subtleties are worth mentioning here. First, a comment on the notation. Note that we have defined a function, \(F(x)\), as the definite integral of another function, \(f(t)\), from the point a to the point x. At first glance, th...
- [5.3: The Fundamental Theorem of Calculus](https://math.libretexts.org/Bookshelves/Calculus/Calculus_(OpenStax)/05%3A_Integration/5.03%3A_The_Fundamental_Theorem_of_Calculus)
  Snippet: \[ ∫^b\_af(x)\,dx=F(b)−F(a). \label{FTC2} \]  We often see the notation \(\displaystyle F(x)|^b\_a\) to denote the expression \(F(b)−F(a)\). We use this vertical bar and associated limits \(a\) and \(b\) to indicate that we should evaluate the function \(F(x)\) at the upper li...
- [The Fundamental Theorem of Calculus](https://www2.math.uconn.edu/ClassHomePages/Math1071/Textbook/sec_Ch5Sec3.html)
  Snippet: then \(F'(x)=f(x)\) over \([a,b].\)  Before we delve into the proof, a couple of subtleties are worth mentioning here. First, a comment on the notation. Note that we have defined a function, \(F(x),\) as the definite integral of another function, \(f(t),\) from the point \(a\)...

### plain_text | Fundamental Theorem of Calculus plain text formula notation

- Answer Summary: The Fundamental Theorem of Calculus states that if F is an antiderivative of f (i.e., F′(x)=f(x) for all x in [a,b]), then the definite integral of f over [a,b] can be evaluated by the plain‑text formula ∫ₐᵇ f(x) dx = F(b) − F(a), which is often written as F(x)|ₐᵇ to indicate “evaluate F at the upper limit b and subtract its value at the lower limit a.”
- [AC The Fundamental Theorem of Calculus](https://activecalculus.org/single/sec-4-4-FTC.html)
  Snippet: 🔗  🔗")  A common alternate notation for \(F(b) - F(a)\) is  \begin{equation\} F(b) - F(a) = \Bigl. F(x) \Bigr|\_a^b\text{,} \end{equation\}  where we read the righthand side as “the function \(F\) evaluated from \(a\) to \(b\text{.}\)” In this notation, the FTC says that  \beg...
- [5.3: The Fundamental Theorem of Calculus - Mathematics LibreTexts](https://math.libretexts.org/Bookshelves/Calculus/Calculus_(OpenStax)/05%3A_Integration/5.03%3A_The_Fundamental_Theorem_of_Calculus)
  Snippet: \[ ∫^b\_af(x)\,dx=F(b)−F(a). \label{FTC2} \]  We often see the notation \(\displaystyle F(x)|^b\_a\) to denote the expression \(F(b)−F(a)\). We use this vertical bar and associated limits \(a\) and \(b\) to indicate that we should evaluate the function \(F(x)\) at the upper li...
- [5.3 The Fundamental Theorem of Calculus – Calculus Volume 1](https://opentextbooks.clemson.edu/math1060scruggs/chapter/the-fundamental-theorem-of-calculus/)
  Snippet: g(x)={\int }_{a}^{x}f(t)dt,  then {g}^{\prime }(x)=f(x) over ![\left[a,b\right].]( "Rendered by QuickLaTeX.com")  Before we delve into the proof, a couple of subtleties are worth mentioning here. First, a comment on the notation. Note that we have defined a function, g(x), as ...

### plain_text | Fundamental Theorem of Calculus keyboard formula input

- Answer Summary: The Fundamental Theorem of Calculus is commonly entered on a keyboard in LaTeX as \displaystyle\int_{a}^{b}f(x)\,dx = F(b)-F(a) (or equivalently \left. F(x)\right|_{a}^{b}), where F′(x)=f(x) if F(x)=\int_{a}^{x}f(t)\,dt.
- [The Fundamental Theorem of Calculus](https://www2.math.uconn.edu/ClassHomePages/Math1071/Textbook/sec_Ch5Sec3.html)
  Snippet: \begin{equation\} f(c)=\frac{1}{b-a} \displaystyle{ \int\_{a}^{b} f(x)dx}. \end{equation\}  This formula can also be stated as  \begin{equation\} \displaystyle{ \int\_{a}^{b} f(x)dx}=f(c)(b-a). \end{equation\}  #### Example 5.57. Finding the Average Value of a Function.  Find ...
- [5.3: The Fundamental Theorem of Calculus - Mathematics LibreTexts](https://math.libretexts.org/Bookshelves/Calculus/Calculus_(OpenStax)/05%3A_Integration/5.03%3A_The_Fundamental_Theorem_of_Calculus)
  Snippet: \[ ∫^b\_af(x)\,dx=F(b)−F(a). \label{FTC2} \]  We often see the notation \(\displaystyle F(x)|^b\_a\) to denote the expression \(F(b)−F(a)\). We use this vertical bar and associated limits \(a\) and \(b\) to indicate that we should evaluate the function \(F(x)\) at the upper li...
- [5.3: The Fundamental Theorem of Calculus Basics](https://math.libretexts.org/Courses/Monroe_Community_College/MTH_210_Calculus_I_(Professor_Dean)/Chapter_5%3A_Integration/5.3%3A__The_Fundamental_Theorem_of_Calculus_Basics)
  Snippet: The Fundamental Theorem of Calculus is an extremely powerful theorem that establishes the relationship between differentiation and integration, and gives us a way to evaluate definite integrals without using Riemann sums or calculating areas. The theorem is comprised of two pa...

### latex_help | Fundamental Theorem of Calculus latex help input notation

- Answer Summary: Use the standard notation \(\displaystyle\int_{a}^{b}f(x)\,dx = F(b)-F(a)\), where \(F\) is any antiderivative of \(f\) (\(F' = f\)). In LaTeX you can write this compactly with an evaluation bar by defining a differential operator and a convenient macro, for example  

```latex
\usepackage{amsmath}
\DeclareMathOperator{\di}{\mathrm{d}\!}
\newcommand{\Eval}[3]{\left.#1\right|_{#2}^{#3}}
```  

Then the fundamental theorem can be typeset as  

```latex
\[
\int_{a}^{b} f(x)\,\di x = \Eval{F(x)}{a}{b}
\] 
```  

which expands to \(\displaystyle\int_{a}^{b} f(x)\,dx = \bigl.F(x)\bigr|_{a}^{b}=F(b)-F(a)\). For a concrete example, the antiderivative of \(x\) is \(\tfrac12 x^{2}\), so  

```latex
\[
\int_{a}^{b} x\,\di x = \Eval{\tfrac12 x^{2}}{a}{b}
\] 
```  

produces \(\displaystyle\int_{a}^{b} x\,dx = \left.\frac12 x^{2}\right|_{a}^{b}= \frac{b^{2}}{2}-\frac{a^{2}}{2}\). The `\left.\dots\right|_{a}^{b}` construction automatically sizes the vertical bar to match the surrounding expression, and you can replace `\big|` or `\Big|` with `\left.|` for a fully scalable evaluation symbol.
- [Evaluation of Differentiation and Integration - LaTeX Stack Exchange](https://tex.stackexchange.com/questions/15894/evaluation-of-differentiation-and-integration)
  Snippet: `\left` `\right` `\documentclass{article} \usepackage{amsmath} \DeclareMathOperator{\di}{\mathrm{d}\!} \def\at{ \left. \vphantom{\int} \right| } \begin{document} \begin{eqnarray} \int_a^b x^2 \di x &=& \frac{x^3}{3}\at_a^b \\ \int\limits_a^b x^2 \di x &=& \frac{x^3}{3}\at_a^b ...
- [The Fundamental Theorem of Calculus - eMathHelp](https://www.emathhelp.net/notes/calculus-2/definite-integral/the-fundamental-theorem-of-calculus/)
  Snippet: 1. If $$${P}{\left({x}\right)}={\int\_{{a}}^{{x}}}{f{{\left({t}\right)}}}{d}{t}$$$, then $$${P}'{\left({x}\right)}={f{{\left({x}\right)}}}$$$. 2. $$${\int\_{{a}}^{{b}}}{f{{\left({x}\right)}}}{d}{x}={F}{\left({b}\right)}-{F}{\left({a}\right)}$$$, where F is any antiderivative o...
- [5.3 The Fundamental Theorem of Calculus - OpenStax](https://openstax.org/books/calculus-volume-1/pages/5-3-the-fundamental-theorem-of-calculus)
  Snippet: (5.16)  then over  Before we delve into the proof, a couple of subtleties are worth mentioning here. First, a comment on the notation. Note that we have defined a function, as the definite integral of another function, from the point a to the point x. At first glance, this is ...

### latex_help | Fundamental Theorem of Calculus latex 写法 求助

- Answer Summary: 在 LaTeX 中写出基本积分定理常用的形式是  
\[
\int_{a}^{b}f(x)\,dx = F(b)-F(a)=\left. F(x)\right|_{a}^{b},
\]  
其中 \(F'(x)=f(x)\)。如果希望竖线的高度与前面的表达式匹配，可以使用 \verb|\big|、\big| 或 \verb|\Big| 等，例如 \verb|\big|_{a}^{b}|，或更通用的自定义宏：  
\verb|\newcommand{\Eval}[3]{\left.#1\right|_{#2}^{#3}}|，随后写成 \verb|\Eval{F(x)}{a}{b}|，效果同上。记得在积分符号后加上 \verb|\;| 或 \verb|\,| 以得到适当的间距，例如 \verb|\int_{a}^{b} f(x)\,dx|。
- [5.4: The Fundamental Theorem of Calculus - Mathematics LibreTexts](https://math.libretexts.org/Bookshelves/Calculus/Calculus_3e_(Apex)/05%3A_Integration/5.04%3A_The_Fundamental_Theorem_of_Calculus)
  Snippet: Notation: A special notation is often used in the process of evaluating definite integrals using the Fundamental Theorem of Calculus. Instead of explicitly writing \(F(b)-F(a)\), the notation \(F(x)\Big|\_a^b\) is used. Thus the solution to Example \(\PageIndex{2}\) would be w...
- [The Fundamental Theorem of Calculus](https://www2.math.uconn.edu/ClassHomePages/Math1071/Textbook/sec_Ch5Sec3.html)
  Snippet: \begin{equation\} f(c)=\frac{1}{b-a} \displaystyle{ \int\_{a}^{b} f(x)dx}. \end{equation\}  This formula can also be stated as  \begin{equation\} \displaystyle{ \int\_{a}^{b} f(x)dx}=f(c)(b-a). \end{equation\}  #### Example 5.57. Finding the Average Value of a Function.  Find ...
- [Evaluation of Differentiation and Integration - LaTeX Stack Exchange](https://tex.stackexchange.com/questions/15894/evaluation-of-differentiation-and-integration)
  Snippet: `\left` `\right` `\documentclass{article} \usepackage{amsmath} \DeclareMathOperator{\di}{\mathrm{d}\!} \def\at{ \left. \vphantom{\int} \right| } \begin{document} \begin{eqnarray} \int_a^b x^2 \di x &=& \frac{x^3}{3}\at_a^b \\ \int\limits_a^b x^2 \di x &=& \frac{x^3}{3}\at_a^b ...

### mixed_language | Fundamental Theorem of Calculus 中文 英文 混合 公式 写法

- Answer Summary: 微積分基本定理（Fundamental Theorem of Calculus）分為兩部分：第一部分說，若 \(F\) 是 \(f\) 的原函數（即 \(F'(x)=f(x)\)），則定積分可寫成 \(\displaystyle \int_{a}^{b} f(x)\,dx = F(b)-F(a)\)；第二部分則指出，對於變上限的定積分，導數滿足 \(\displaystyle \frac{d}{dx}\Bigl(\int_{a}^{x} f(t)\,dt\Bigr)=f(x)\)。這兩式同時說明了積分是微分的逆運算，且積分與導數在上下限的處理上保持一致。
- [Fundamental theorem of calculus - Cambridge OCR AS Level](https://www.thinka.ai/zh/Cambridge-OCR-AS-Level/Mathematics-A---H230/Fundamental-theorem-of-calculus)
  Snippet: ### 2. 不定積分與定積分  釐清這兩類積分之間的區別非常重要，因為它們雖然看起來相似，但功能各不相同。  不定積分 (Indefinite Integrals)：    這是通用公式。它們總是包含一個 + c（積分常數）。    例子： \(\int 2x dx = x^2 + c\)。    你可以將其視為尋找一「族」具有相同斜率的曲線。  定積分 (Definite Integrals)：    這些在積分符號的上下方有數字（稱為積分上下限）。它們會給出一個具體的數值答案，通常代表曲線下方的面積。    例子： \(\int\_{1}^{...
- [微積分常見數學專有名詞中英文對照表(二三類組) A](https://www.nups.ntnu.edu.tw/upfiles/course/math/Syllabus/%E5%BE%AE%E7%A9%8D%E5%88%86%E5%B8%B8%E8%A6%8B%E6%95%B8%E5%AD%B8%E5%B0%88%E6%9C%89%E5%90%8D%E8%A9%9E%E4%B8%AD%E8%8B%B1%E6%96%87%E5%B0%8D%E7%85%A7%E8%A1%A8(%E4%BA%8C%E4%B8%89%E9%A1%9E%E7%B5%84)20250107.pdf)
  Snippet: 230 極值 F finite sum, 318 有限和 first derivative test for local extreme values, 248 一階導數檢驗局部極值 functions, 19 函數 Fundamental Theorem of Calculus, 340-342 微積分基本定理 Fundamental Theorem of Calculus, part 1, 340 微積分第一基本定理 Fundamental Theorem of Calculus, part 2, 342 微積分第二基本定理 G general...
- [數學科常用英漢辭彙2020年7月8日版](https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/res/Glossary20200708.pdf)
  Snippet: line 分線 fractional index 分數指數 fractional inequality 分式不等式 free vector 自由向量，自由矢量 frequency 頻數，頻率 frequency curve 頻數曲線，頻率曲線 frequency distribution 頻數分佈，頻率分佈 frequency polygon 頻數多邊形，頻率多邊形 frequency table 頻數表，頻率表 frustum 平截頭體，平截頭台，錐臺 function 函數 function of function 函數的函數，複合函數，疊函數...

### mixed_language | Fundamental Theorem of Calculus formula notes shorthand mixed language

- Answer Summary: The Fundamental Theorem of Calculus consists of two complementary statements: Part 1 (the derivative of an integral) says that if f is continuous on an interval and we define F(x)=∫ₐˣ f(t) dt, then F′(x)=f(x) (equivalently d/dx ∫ₐˣ f(t) dt = f(x)); Part 2 (the evaluation theorem) states that for any antiderivative F of f, the definite integral ∫ₐᵇ f(x) dx equals F(b)−F(a), a shorthand often written as [F(x)]ₐᵇ or F|ₐᵇ, which expresses the net change of a quantity whose rate of change is f.
- [[PDF] 1.3 | The Fundamental Theorem of Calculus](https://www.math.stonybrook.edu/~ndang/mat126-fall20/sec_1.3.pdf)
  Snippet: 146. To get on a certain toll road a driver has to take a card that lists the mile entrance point. The card also has a timestamp. When going to pay the toll at the exit, the driver is surprised to receive a speeding ticket along with the toll. Explain how this can happen. 147....
- [[PDF] Lecture 23 Fundamental Theorem of Calculus - KSU Math](https://www.math.ksu.edu/~gerald/math220d/hand23.pdf)
  Snippet: Calculus I - Lecture 23 Fundamental Theorem of Calculus Lecture Notes:  Course Syllabus:  Gerald Hoehn (based on notes by T. Cochran) April 16, 2014 Section 5.3 - Fundamental Theorem of Calculus I We have seen two types of integrals: 1. Indeﬁnite: Z f (x) dx = F(x) + C where F...
- [4.4: The Fundamental Theorem of Calculus - Mathematics LibreTexts](https://math.libretexts.org/Bookshelves/Calculus/Book%3A_Active_Calculus_(Boelkins_et_al.)/04%3A_The_Definite_Integral/4.04%3A_The_Fundamental_Theorem_of_Calculus)
  Snippet: ##### Fundamental Theorem of Calculus  If \(f\) is a continuous function on \([a,b]\text{,}\) and \(F\) is any antiderivative of \(f\text{,}\) then \(\int\_a^b f(x) \, dx = F(b) - F(a)\text{.}\)  A common alternate notation for \(F(b) - F(a)\) is  where we read the righthand s...

## Coulomb's Law

- Category: `physics`
- Formula: `F = k_e \frac{q_1 q_2}{R^2}`

### messy_nl | Coulomb's Law formula how do I type this

- Answer Summary: Coulomb’s law can be typed as F = k \frac{|q₁ q₂|}{r²} for the scalar magnitude (or \vec F_{12}=k \frac{q₁ q₂}{r²}\,\hat r_{12} for the vector form), where F is the force in newtons, k ≈ 8.99 × 10⁹ N·m²/C² (also written kₑ = 1⁄(4π ε₀)), q₁ and q₂ are the charges in coulombs, and r is the separation in metres; in plain‑text you can write F = k*abs(q1*q2)/r^2 or F = k*q1*q2/r^2 for signed charges.
- [Coulomb's Law | Physics - Lumen Learning](https://courses.lumenlearning.com/suny-physics/chapter/18-3-coulombs-law/)
  Snippet: Through the work of scientists in the late 18th century, the main features of the electrostatic force—the existence of two types of charge, the observation that like charges repel, unlike charges attract, and the decrease of force with distance—were eventually refined, and exp...
- [18.3: Coulomb's Law - Physics LibreTexts](https://phys.libretexts.org/Bookshelves/College_Physics/College_Physics_1e_(OpenStax)/18%3A_Electric_Charge_and_Electric_Field/18.03%3A_Coulomb's_Law)
  Snippet: \( \newcommand{\vectorA}{\vec{#1}}      % arrow\)  \( \newcommand{\vectorAt}{\vec{\text{#1}}}      % arrow\)  \( \newcommand{\vectorB}{\overset { \scriptstyle \rightharpoonup} {\mathbf{#1}} } \)  \( \newcommand{\vectorC}{\textbf{#1}} \)  \( \newcommand{\vectorD}{\overrightarro...
- [Coulomb's Law - Definition, Formula, and Applications - Science Notes](https://sciencenotes.org/coulombs-law-definition-formula-and-applications/)
  Snippet: If the charges have the same sign, the force is repulsive. If they have opposite signs, the force is attractive.  ### Coulomb’s Law Formula  Coulomb’s law can be expressed in both scalar and vector forms, depending on whether you are interested only in the magnitude of the for...

### messy_nl | Coulomb's Law 这个公式怎么打

- Answer Summary: 在普通文本或聊天里可以直接敲 `F = k * |q1 * q2| / r^2`（其中 k≈8.99×10⁹ N·m²/C²，r 为两点电荷间距离），如果需要更正式的排版可使用 LaTeX 语法写成 `F = k \frac{|q_1 q_2|}{r^{2}}`，向量形式则写成 `\mathbf{F}_{12}= k \frac{q_1 q_2}{r^{2}} \hat{r}_{12}`，在 Word 的公式编辑器中则输入 `F = k\frac{|q_1 q_2|}{r^2}`，或在 MathType 中同样使用分数模板即可完成 Coulomb 定律的公式输入。
- [What is Coulomb's Law? An Introductory Guide - School of PE](https://schoolofpe.com/blogs/news/what-is-coulombs-law-an-introductory-guide-html?srsltid=AfmBOooTIVmEIrA3KHoGEfRdeJj6i5bdF3IKP8zFZjxKjNJ309mYyMF7)
  Snippet: Torsion Balance  Figure 1  Coulomb's law describes the force of attraction or repulsion between two charged particles. The force is directly proportional to the product of the charges and inversely proportional to the square of the distance between them. The Coulomb's law can ...
- [18.3: Coulomb's Law - Physics LibreTexts](https://phys.libretexts.org/Bookshelves/College_Physics/College_Physics_1e_(OpenStax)/18%3A_Electric_Charge_and_Electric_Field/18.03%3A_Coulomb's_Law)
  Snippet: Definition: Coulomb’s Law  Coulomb’s law calculates the magnitude of the force \(F\) between two point charges, \(q\_1\) and \(q\_2\), separated by a distance \(r\).  \[F=k\dfrac{|q\_{1}q\_{2}|}{r^{2}}.\]  In SI units, the constant\(k\) is equal to  \[k=8.988\times 10^{9}\dfra...
- [Coulomb's law - Wikipedia](https://en.wikipedia.org/wiki/Coulomb%27s_law)
  Snippet: Coulomb's inverse-square law, or simply Coulomb's law, is an experimental law of physics that calculates the amount of force "Force (physics)") between two electrically charged particles at rest. This electric force is conventionally called the electrostatic force or Coulomb f...

### plain_text | Coulomb's Law plain text formula notation

- Answer Summary: Coulomb’s law in plain‑text notation is F = k · q₁ q₂ / r², where F is the magnitude of the electrostatic force (in newtons), q₁ and q₂ are the point‑charge values (in coulombs), r is the separation distance (in metres), and k = 8.987551 × 10⁹ N·m²·C⁻² (equivalently k = 1 / (4π ε₀)). The vector form is \(\mathbf{F} = \frac{k\,q₁q₂}{r^{2}}\,\hat{\mathbf{r}}\), with \(\hat{\mathbf{r}}\) a unit vector pointing from one charge to the other.
- [17.3: Coulomb's Law - Physics LibreTexts](https://phys.libretexts.org/Bookshelves/University_Physics/Physics_(Boundless)/17%3A_Electric_Charge_and_Field/17.3%3A_Coulombs_Law)
  Snippet: \[\mathbf { F } \_ { \mathbf { E } } = \dfrac { \operatorname { kq } Q \left( \mathrm { r } \_ { \mathrm { q } } - \mathrm { r } \_ { Q } \right) } { \left| \mathrm { r } \_ { \mathrm { q } } - \mathrm { r } \_ { Q } \right| ^ { 3 } }\] [...] \[\mathbf { F } \_ { \mathbf { E }...
- [18.3: Coulomb's Law - Physics LibreTexts](https://phys.libretexts.org/Bookshelves/College_Physics/College_Physics_1e_(OpenStax)/18%3A_Electric_Charge_and_Electric_Field/18.03%3A_Coulomb's_Law)
  Snippet: Definition: Coulomb’s Law  Coulomb’s law calculates the magnitude of the force \(F\) between two point charges, \(q\_1\) and \(q\_2\), separated by a distance \(r\).  \[F=k\dfrac{|q\_{1}q\_{2}|}{r^{2}}.\]  In SI units, the constant\(k\) is equal to  \[k=8.988\times 10^{9}\dfra...
- [9.2 Coulomb's law | Electrostatics - Siyavula](https://www.siyavula.com/read/za/physical-sciences/grade-11/electrostatics/09-electrostatics-02)
  Snippet: Therefore,\begin{align\} F\_R & = \text{4,5} \times \text{10}^{-\text{5}}\text{ N} + \text{1,69} \times \text{10}^{-\text{5}}\text{ N} \\ & = \text{6,19} \times \text{10}^{-\text{5}}\text{ N} \end{align\}  The resultant force acting on \(Q\_2\) is \(\text{6,19} \times \text{10...

### plain_text | Coulomb's Law keyboard formula input

- Answer Summary: F = k · |q₁ q₂| / r²  (where k ≈ 8.99 × 10⁹ N·m²/C², q₁ and q₂ are the point‑charge magnitudes in coulombs, r is the separation distance in metres, and the absolute‑value bars give the force magnitude; the direction is along the line joining the charges, attractive for opposite signs and repulsive for like signs).
- [17.3: Coulomb's Law - Physics LibreTexts](https://phys.libretexts.org/Bookshelves/University_Physics/Physics_(Boundless)/17%3A_Electric_Charge_and_Field/17.3%3A_Coulombs_Law)
  Snippet: \[\mathbf { F } \_ { \mathbf { E } } = \dfrac { \operatorname { kq } Q \left( \mathrm { r } \_ { \mathrm { q } } - \mathrm { r } \_ { Q } \right) } { \left| \mathrm { r } \_ { \mathrm { q } } - \mathrm { r } \_ { Q } \right| ^ { 3 } }\] [...] \[\mathbf { F } \_ { \mathbf { E }...
- [18.3: Coulomb's Law - Physics LibreTexts](https://phys.libretexts.org/Bookshelves/College_Physics/College_Physics_1e_(OpenStax)/18%3A_Electric_Charge_and_Electric_Field/18.03%3A_Coulomb's_Law)
  Snippet: \( \newcommand{\vectorA}{\vec{#1}}      % arrow\)  \( \newcommand{\vectorAt}{\vec{\text{#1}}}      % arrow\)  \( \newcommand{\vectorB}{\overset { \scriptstyle \rightharpoonup} {\mathbf{#1}} } \)  \( \newcommand{\vectorC}{\textbf{#1}} \)  \( \newcommand{\vectorD}{\overrightarro...
- [Coulomb's Law | Physics - Lumen Learning](https://courses.lumenlearning.com/suny-physics/chapter/18-3-coulombs-law/)
  Snippet: Through the work of scientists in the late 18th century, the main features of the electrostatic force—the existence of two types of charge, the observation that like charges repel, unlike charges attract, and the decrease of force with distance—were eventually refined, and exp...

### latex_help | Coulomb's Law latex help input notation

- Answer Summary: In LaTeX the scalar Coulomb‑law expression is written as \[F = k\,\frac{|q_{1}\,q_{2}|}{r^{2}}\] where \(k = 8.99\times10^{9}\;\mathrm{N\,m^{2}/C^{2}}\) or equivalently \(k = \frac{1}{4\pi\varepsilon_{0}}\); the vector form can be expressed with bold or arrow notation as \[\mathbf{F}_{12}= \frac{1}{4\pi\varepsilon_{0}}\;\frac{q_{1}q_{2}}{|\mathbf{r}_{1}-\mathbf{r}_{2}|^{3}}\;(\mathbf{r}_{1}-\mathbf{r}_{2}) = \frac{1}{4\pi\varepsilon_{0}}\;\frac{q_{1}q_{2}}{r^{2}}\;\hat{\mathbf r}_{12},\] using \verb|\mathbf{F}_{12}|, \verb|\mathbf{r}_{1}|, \verb|\mathbf{r}_{2}| for vectors, \verb|\hat{\mathbf r}_{12}| for the unit‑vector, and \verb|\frac{…}{…}| for fractions; subscripts are added with an underscore (e.g., \(q_{i},\;r_{\text{init}},\;F_{\text{final}}\)), absolute values with \verb|\left|…\right|, and parentheses or brackets for grouping as needed.
- [17.3: Coulomb's Law - Physics LibreTexts](https://phys.libretexts.org/Bookshelves/University_Physics/Physics_(Boundless)/17%3A_Electric_Charge_and_Field/17.3%3A_Coulombs_Law)
  Snippet: In this equation, k is equal to \(\frac { 1 } { 4 \pi \varepsilon \_ { 0 } \varepsilon }\) ,where \(\varepsilon \_ { 0 }\) is the permittivity of free space and εε is the relative permittivity of the material in which the charges are immersed. The variables \(\mathbf { F} \_ {...
- [18.3: Coulomb's Law - Physics LibreTexts](https://phys.libretexts.org/Bookshelves/College_Physics/College_Physics_1e_(OpenStax)/18%3A_Electric_Charge_and_Electric_Field/18.03%3A_Coulomb's_Law)
  Snippet: \[ \begin{align\} F &=k\dfrac{|q\_{1}q\_{2}|}{r^2} \\[5pt] &=(8.99\times 10^{9} N\cdot m^{2}/C^{2})\times \dfrac{(1.60\times 10^{-19}C)(1.60\times 10^{-19}C)}{(0.530\times 10^{-10}m)^{2}} \end{align\}\]  Thus the Coulomb force is  \[F=8.19\times 10^{-8}N. \nonumber\]  The char...
- [18.2 Coulomb's law - Physics | OpenStax](https://openstax.org/books/physics/pages/18-2-coulombs-law)
  Snippet: Use the following notation: When the charges are 5.0 cm apart, the force is and , where the subscript i means initial. Once the charges are brought closer together, we know , where the subscript f means final.  Solution  Coulomb’s law applied to the spheres in their initial po...

### latex_help | Coulomb's Law latex 写法 求助

- Answer Summary: Coulomb’s law can be written in LaTeX as \(F = k\,\frac{|q_{1}q_{2}|}{r^{2}}\) or, using the electrostatic constant \(k = \frac{1}{4\pi\varepsilon_{0}}\) and indicating the direction of the force, as \(\displaystyle \vec{F}= \frac{1}{4\pi\varepsilon_{0}}\frac{q_{1}q_{2}}{r^{2}}\;\hat{r}\), where \(q_{1}\) and \(q_{2}\) are the point charges, \(r\) is the separation distance, \(\hat{r}\) is the unit vector from one charge to the other, and \(\varepsilon_{0}\) is the vacuum permittivity.
- [Coulomb's Law | Physics - Lumen Learning](https://courses.lumenlearning.com/suny-physics/chapter/18-3-coulombs-law/)
  Snippet: 4. The separation decreased by a factor of 5.  8. [latex]\begin{array}{lll}F&=&k\frac{\mid{q}\_{1}{q}\_{2}\mid}{{r}^{2}}=ma\Rightarrow{a}=\frac{k{q}^{2}}{mr^{2}}\\\text{ }&=&\frac{\left(9.00\times{10}^{9}\text{ N}\cdot\text{m}^{2}/{\text{C}}^{2}\right){\left(1.60\times {10}^{-...
- [18.3: Coulomb's Law - Physics LibreTexts](https://phys.libretexts.org/Bookshelves/College_Physics/College_Physics_1e_(OpenStax)/18%3A_Electric_Charge_and_Electric_Field/18.03%3A_Coulomb's_Law)
  Snippet: \( \newcommand{\RealPart}{\mathrm{Re}}\) \( \newcommand{\ImaginaryPart}{\mathrm{Im}}\)  \( \newcommand{\Argument}{\mathrm{Arg}}\) \( \newcommand{\norm}{\| #1 \|}\)  \( \newcommand{\inner}{\langle #1, #2 \rangle}\)  \( \newcommand{\Span}{\mathrm{span}}\)  \( \newcommand{\id}{\m...
- [Coulomb's law - Wikipedia](https://en.wikipedia.org/wiki/Coulomb%27s_law)
  Snippet: Coulomb's inverse-square law, or simply Coulomb's law, is an experimental law of physics that calculates the amount of force "Force (physics)") between two electrically charged particles at rest. This electric force is conventionally called the electrostatic force or Coulomb f...

### mixed_language | Coulomb's Law 中文 英文 混合 公式 写法

- Answer Summary: 库仑定律可写成中英文混合的形式为： \(F = k_e \dfrac{q_1 q_2}{r^{2}}\)，其中 \(F\) 表示库仑力（单位 N），\(k_e\) 为库仑常数（约等于 \(9.0\times10^{9}\,\text{N·m}^2\text{/C}^2\)），\(q_1\) 与 \(q_2\) 为两点电荷的电量（单位 C），\(r\) 为两电荷之间的距离（单位 m），而 \(\dfrac{q_1 q_2}{r^{2}}\) 可标注为“电荷乘积除以距离平方”。
- [[PDF] 國立秀水高工電機與電子群行業英文術語題庫表](https://www.ssivs.chc.edu.tw/resources/WID_0_1_3c58649dcb0de4024ba889fdd1407b0c7865e65c/CLS_0_1_7ad4c7e3705c7dd6a3624700661721e466d419ec/02e7bda276d7b211e097e21832dd4178.pdf)
  Snippet: band 導電帶 常用 E0144 conductor 導體 常用 E0145 construction 結構 常用 E0146 Contact resistance 接觸電阻 常用 E0147 continuity equation 連續方程式 常用 E0148 continuous 連續的 常用 E0149 contrary 相反的 常用 E0150 contrast 反襯 常用 E0151 contrast 對比 常用 E0152 Control 控制 常用 E0153 control circuit 控制電路 常用 E0154 Contro...
- [1996 年版物理学名词修订英中对照初稿本](https://wulixb.iphy.ac.cn/fileWLXB/cms/news/info/upload/0b531a2f-aaaa-465e-9eac-3e33edbdb2c6.pdf)
  Snippet: barrier 库仑势垒 Coulomb blockade 库仑阻塞 Coulomb collision 库仑碰撞 Coulomb correction factor 库仑修正因子 又称“费米函数(Fermi function)” 。 Coulomb energy 库仑能 Coulomb excitation 库仑激发 Coulomb explosion 库仑爆炸 Coulomb field 库仑场 Coulomb force 库仑力 Coulomb gap 库仑隙 Coulomb gas 库仑气 Coulomb gauge 库仑规范 Coulom...
- [[PDF] IChO General instructions](https://www.icho2021.org/pdf/TWN/exams-docs_TWN-2_print_exam-4.pdf)
  Snippet: kg 標準壓力 𝑝= 1 bar = 105 Pa 大氣壓力 𝑝atm = 1.01325 × 105 Pa 攝氏零度 0 ∘C = 273.15 K 埃 1 Å = 10−10 m 皮米 1 pm = 10−12 m 電子伏特 1 eV = 1.602176634 × 10−19 J 百萬分點 1 ppm = 10−6 十億分點 1 ppb = 10−9 兆分點 1 ppt = 10−12 pi, π 𝜋= 3.141592653589793 自然對數底(Euler's number) 𝑒= 2.718281828459045 TWN-2 C-0...

### mixed_language | Coulomb's Law formula notes shorthand mixed language

- Answer Summary: Coulomb’s law states that the electric force between two point charges is proportional to the product of the charges and inversely proportional to the square of the distance separating them, expressed in shorthand as F ∝ q₁q₂⁄r²; the full equation is F = k·q₁q₂⁄r² with k = 1⁄(4π ε₀) where ε₀ is the permittivity of free space, and in vector form \(\vec F_{12}= \frac{1}{4\pi\varepsilon_{0}}\frac{q_{1}q_{2}}{r_{12}^{2}}\hat r_{12}\) (the force on q₂ due to q₁ points along the unit vector \(\hat r_{12}\) from q₁ to q₂, with sign indicating attraction or repulsion).
- [Coulomb's Law | OCR A Level Physics Revision Notes 2015](https://www.savemyexams.com/a-level/physics/ocr/17/revision-notes/6-particles-and-medical-physics/6-3-electric-fields/6-3-4-coulombs-law/)
  Snippet: F equals fraction numerator Q q over denominator 4 straight pi epsilon subscript italic 0 r squared end [...] F equals fraction numerator Q q over denominator 4 straight pi epsilon subscript italic 0 r squared end [...] F equals fraction numerator Q q over denominator 4 straig...
- [Coulomb's Law Between Electric Charges - BYJU'S](https://byjus.com/jee/coulombs-law/)
  Snippet: ### Table of Content   Coulomb’s Law Formula  Coulomb’s Law in Vector Form  What Is One Coulomb of Charge  Key Points  Limitations  Relative Permittivity  Applications  Problems  ## Coulomb’s Law Formula  In short, F ∝ q1q2/d2   ε is absolute permittivity,  K or εr is the rela...
- [5.4: Coulomb's Law - Physics LibreTexts](https://phys.libretexts.org/Bookshelves/University_Physics/University_Physics_(OpenStax)/University_Physics_II_-_Thermodynamics_Electricity_and_Magnetism_(OpenStax)/05%3A_Electric_Charges_and_Fields/5.04%3A_Coulomb's_Law)
  Snippet: In this expression, \(Q\) represents the charge of the particle that is experiencing the electric force \(\vec{F}\), and is located at \(\vec{r}\) from the origin; the \(q\_i\)'s are the \(N\) source charges, and the vectors \(\vec{r}\_i = r\_i \hat{r}\_i\) are the displacemen...

## Rotation Matrix

- Category: `matrix`
- Formula: `R_{\theta} = \begin{bmatrix} \cos \theta & -\sin \theta \\ \sin \theta & \cos \theta \end{bmatrix}`

### messy_nl | Rotation Matrix formula how do I type this

- Answer Summary: The standard 2‑D rotation matrix that rotates a column vector \((x,\;y)^{\mathsf T}\) counter‑clockwise by an angle \(\theta\) is  

\[
\begin{bmatrix}
\cos\theta & -\sin\theta\\[2pt]
\sin\theta & \;\cos\theta
\end{bmatrix},
\]  

so the transformed coordinates are \(x' = x\cos\theta - y\sin\theta\) and \(y' = x\sin\theta + y\cos\theta\); in plain‑text you can type it as `[[cos(theta), -sin(theta)], [sin(theta), cos(theta)]]` or in LaTeX as `\begin{bmatrix}\cos\theta & -\sin\theta \\ \sin\theta & \cos\theta\end{bmatrix}`. For 3‑D rotations about the principal axes the matrices are  

\[
R_x(\alpha)=\begin{bmatrix}1&0&0\\0&\cos\alpha&-\sin\alpha\\0&\sin\alpha&\cos\alpha\end{bmatrix},\qquad
R_y(\beta)=\begin{bmatrix}\cos\beta&0&\sin\beta\\0&1&0\\-\sin\beta&0&\cos\beta\end{bmatrix},\qquad
R_z(\gamma)=\begin{bmatrix}\cos\gamma&-\sin\gamma&0\\\sin\gamma&\cos\gamma&0\\0&0&1\end{bmatrix},
\]  

which can be typed similarly in LaTeX or as nested lists of numbers.
- [[PDF] Rotation Matrices](https://www.math.utah.edu/~wortman/1060text-rm.pdf)
  Snippet: We can write this vector in polar coordinates as a(1, 0), or equivalently, as a( cos(0), sin(0) ). Now we can rotate the vector (a, 0) by an angle α. That’s the vector Rα(a, 0), which by the formula from the beginning of this chapter is Rα(a, 0) = Rα  a( cos(0), sin(0) )  = a...
- [Rotation matrix - Wikipedia](https://en.wikipedia.org/wiki/Rotation_matrix)
  Snippet: This can be written more concisely as   where [u]× is the cross product matrix of u; the expression u ⊗ u is the outer product, and I is the identity matrix. Alternatively, the matrix entries are:  where εjkl is the Levi-Civita symbol with ε123 = 1. This is a matrix form of Ro...
- [Rotation Matrix - Definition, Formula, Derivation, Examples - Cuemath](https://www.cuemath.com/algebra/rotation-matrix/)
  Snippet: Thus, \(\begin{bmatrix} cos\theta & -sin\theta \\ \\sin\theta& cos\theta \end{bmatrix}\) will be the rotation matrix.  ## Rotation Matrix in 3D  In 3D space, rotation can occur about the x, y, or z-axis. Such a type of rotation that occurs about any one of the axis is known as...

### messy_nl | Rotation Matrix 这个公式怎么打

- Answer Summary: 在 LaTeX 中，二维逆时针旋转 θ 的矩阵可以写成  
\[
\begin{bmatrix}
\cos\theta & -\sin\theta\\
\sin\theta & \;\cos\theta
\end{bmatrix},
\]  
对应的代码为 `\begin{bmatrix}\cos\theta & -\sin\theta\\ \sin\theta & \cos\theta\end{bmatrix}`；若需要表示三维的 yaw（绕 z 轴）、pitch（绕 y 轴）和 roll（绕 x 轴），可以分别使用  
\[
\text{yaw}:\ \begin{bmatrix}\cos\alpha & -\sin\alpha & 0\\ \sin\alpha & \cos\alpha & 0\\ 0 & 0 & 1\end{bmatrix},\qquad
\text{pitch}:\ \begin{bmatrix}\cos\beta & 0 & \sin\beta\\ 0 & 1 & 0\\ -\sin\beta & 0 & \cos\beta\end{bmatrix},\qquad
\text{roll}:\ \begin{bmatrix}1 & 0 & 0\\ 0 & \cos\gamma & -\sin\gamma\\ 0 & \sin\gamma & \cos\gamma\end{bmatrix},
\]  
其代码分别为 `\begin{bmatrix}\cos\alpha & -\sin\alpha & 0\\ \sin\alpha & \cos\alpha & 0\\ 0 & 0 & 1\end{bmatrix}`、`\begin{bmatrix}\cos\beta & 0 & \sin\beta\\ 0 & 1 & 0\\ -\sin\beta & 0 & \cos\beta\end{bmatrix}`、`\begin{bmatrix}1 & 0 & 0\\ 0 & \cos\gamma & -\sin\gamma\\ 0 & \sin\gamma & \cos\gamma\end{bmatrix}`。
- [Rotation Matrix - Definition, Formula, Derivation, Examples - Cuemath](https://www.cuemath.com/algebra/rotation-matrix/)
  Snippet: PT = \(\begin{bmatrix} cos\theta & -sin\theta\\ \\sin\theta & cos\theta \end{bmatrix}\)  P-1 = \(\begin{bmatrix} cos\theta & -sin\theta\\ \\sin\theta & cos\theta \end{bmatrix}\)  Hence, PT = P-1  Now, |P| = (cos2θ + sin2θ) = 1.  Thus, P is a rotation matrix. We can say that P ...
- [Rotation matrix 旋转矩阵 - GitBook](https://windmising.gitbook.io/mathematics-basic-for-ml/src/geometry/rotationmatrix)
  Snippet: ✍️  `⌘Ctrl``k`  # Rotation matrix 旋转矩阵  在线性代数中，旋转矩阵是用于在欧几里得空间中执行旋转的变换矩阵。  旋转矩阵是行列式 1 的正交矩阵。旋转矩阵描述了围绕原点的旋转。 旋转矩阵的逆是它的转置，也是一个旋转矩阵。 两个旋转矩阵的乘积是一个旋转矩阵。 对于 n > 2，n × n 旋转矩阵的乘法通常是不可交换的。  ## 二维旋转矩阵  二维旋转矩阵具有以下形式：  R=[cosθsinθ​−sinθcosθ​]  通过以下矩阵乘法旋转列向量，  [x′y′​]=[cosθsinθ​−sinθcosθ​][...
- [矩阵旋转和变换- MATLAB & Simulink Example - MathWorks](https://ww2.mathworks.cn/help/symbolic/rotation-matrix-and-transformation-matrix.html)
  Snippet: ``` xyzScaled = ```  ``` 'Scaling by 3 along z' equal ```  Rotate the scaled surface about the `x`-, `y`-, and `z`-axis by 45 degrees clockwise, in order `z`, then `y`, then `x`. The rotation matrix for this transformation is as follows.  ``` R = RxRyRz ```  ``` R = ```  Use t...

### plain_text | Rotation Matrix plain text formula notation

- Answer Summary: A rotation matrix can be written in plain‑text form as follows: for a 2‑D rotation by angle θ, R(θ) = [[cosθ, ‑sinθ],[sinθ, cosθ]]; for a 3‑D rotation about the x‑axis by α, Rx(α) = [[1, 0, 0],[0, cosα, ‑sinα],[0, sinα, cosα]], about the y‑axis by β, Ry(β) = [[cosβ, 0, sinβ],[0, 1, 0],[‑sinβ, 0, cosβ]], and about the z‑axis by γ, Rz(γ) = [[cosγ, ‑sinγ, 0],[sinγ, cosγ, 0],[0, 0, 1]]; a general rotation about a unit axis u = (ux,uy,uz) by angle θ can be expressed as R = cosθ I + (1‑cosθ) *u* *u*ᵀ + sinθ [u]×, where I is the 3×3 identity, *u* *u*ᵀ = [[ux*ux, ux*uy, ux*uz],[uy*ux, uy*uy, uy*uz],[uz*ux, uz*uy, uz*uz]], and the cross‑product matrix [u]× = [[0, ‑uz, uy],[uz, 0, ‑ux],[‑uy, ux, 0]].
- [Rotation Matrix - Definition, Formula, Derivation, Examples - Cuemath](https://www.cuemath.com/algebra/rotation-matrix/)
  Snippet: P (y, \(\beta\)) = \(\begin{bmatrix} cos\beta & 0 & sin\beta\\ 0 &1 & 0 \\ -sin\beta & 0 & cos\beta \end{bmatrix}\). Such a matrix is known as a pitch. Here, it represents the counterclockwise rotation of \(\beta\) about the y axis.  P (z, \(\alpha\)) = \(\begin{bmatrix} cos\a...
- [Rotation matrix - Wikipedia](https://en.wikipedia.org/wiki/Rotation_matrix)
  Snippet: This can be written more concisely as   where [u]× is the cross product matrix of u; the expression u ⊗ u is the outer product, and I is the identity matrix. Alternatively, the matrix entries are:  where εjkl is the Levi-Civita symbol with ε123 = 1. This is a matrix form of Ro...
- [Rotation Matrix -- from Wolfram MathWorld](https://mathworld.wolfram.com/RotationMatrix.html)
  Snippet: ![ R_theta=[costheta -sintheta; sintheta costheta], ](/images/equations/RotationMatrix/NumberedEquation1.svg)  so  |  |  |  --- | | v^'=R_thetav_0. | (2) |   v^'=R_thetav_0.   This is the convention used by the Wolfram Language command RotationMatrix[theta].  RotationMatrixAxe...

### plain_text | Rotation Matrix keyboard formula input

- Answer Summary: A rotation matrix can be entered directly with standard keyboard symbols by using the trigonometric functions of the rotation angle θ: in two dimensions the matrix is [[cos(θ),‑sin(θ)],[sin(θ),cos(θ)]], while in three dimensions rotations about the principal axes are given by the “roll‑pitch‑yaw’’ forms Rx(γ)=[[1,0,0],[0,cos(γ),‑sin(γ)],[0,sin(γ),cos(γ)]], Ry(β)=[[cos(β),0,sin(β)],[0,1,0],[‑sin(β),0,cos(β)]], and Rz(α)=[[cos(α),‑sin(α),0],[sin(α),cos(α),0],[0,0,1]]; a general axis‑angle rotation about a unit vector u=(ux,uy,uz) uses Rodrigues’ formula R=cos θ·I+(1‑cos θ)·u uᵀ+sin θ·[u]× where [u]×=[[0,‑uz,uy],[uz,0,‑ux],[‑uy,ux,0]], and in many computer‑algebra systems the same matrices can be typed as, for example, RotationMatrix[θ] for 2‑D or RotationMatrix[θ,{ux,uy,uz}] for 3‑D.
- [RotationMatrix - Wolfram Language Documentation](https://reference.wolfram.com/language/ref/RotationMatrix.html)
  Snippet: RotationMatrix gives matrices for rotations of vectors around the origin.  Two different conventions for rotation matrices are in common use.  RotationMatrix is set up to use the vector-oriented convention and to give a matrix m so that m.r yields the rotated version of a vect...
- [Rotation Matrix - GeeksforGeeks](https://www.geeksforgeeks.org/maths/rotation-matrix/)
  Snippet: A(x, \gamma) = \begin{bmatrix}1 & 0 & 0 \\0 & cos(\gamma) & -sin(\gamma) \\0 & sin(\gamma) & cos(\gamma)\end{bmatrix}. This is also known as a roll and it's defined as the counterclockwise rotation of γ about the x axis.  A(y, \beta)=\begin{bmatrix}cos(\beta) & 0 & sin(\beta) ...
- [Rotation matrix - Wikipedia](https://en.wikipedia.org/wiki/Rotation_matrix)
  Snippet: This can be written more concisely as   where [u]× is the cross product matrix of u; the expression u ⊗ u is the outer product, and I is the identity matrix. Alternatively, the matrix entries are:  where εjkl is the Levi-Civita symbol with ε123 = 1. This is a matrix form of Ro...

### latex_help | Rotation Matrix latex help input notation

- Answer Summary: In LaTeX you can write a rotation matrix as a regular matrix surrounded by \(\left(\) and \(\right)\) and, if you need it inline, use the smallmatrix environment; for example the 2‑D rotation about the \(x\)–\(y\) plane by an angle \(\theta\) is typed as `$R_{xy}^2(\theta)=\left(\begin{smallmatrix}\cos\theta & -\sin\theta\\ \sin\theta & \cos\theta\end{smallmatrix}\right)$`, which produces \(R_{xy}^2(\theta)=\left(\begin{smallmatrix}\cos\theta & -\sin\theta\\ \sin\theta & \cos\theta\end{smallmatrix}\right)\); for a displayed equation you can replace smallmatrix with pmatrix or bmatrix inside `\begin{pmatrix} … \end{pmatrix}` or `\begin{bmatrix} … \end{bmatrix}` after loading `\usepackage{amsmath}`.
- [Rotation Matrices - Logos con carne](https://logosconcarne.com/stuff/rotation-matrices/)
  Snippet: The name, {R}_{xy}^{2}(\theta) identifies it as a Rotation matrix. As with the identity matrix, the superscript indicates a rotation in two dimensions, and the subscript that the rotation involves the X and Y coordinates (exactly as we’d expect in two dimensions). Also, note t...
- [LaTeX Matrix Tutorial - Complete Guide with Examples](https://resources.latex-cloud-studio.com/learn/latex/mathematics/matrices)
  Snippet: \documentclass{article} \documentclass{article}\usepackage{amsmath} \usepackage{amsmath}\begin{document} \begin{document} % Inline matrix in text % Inline matrix in textThe rotation matrix $\left(\begin{smallmatrix} The rotation matrix $\left(\begin{smallmatrix}\cos\theta & -\...
- [Rotation Matrices — skinematics 0.10.4 documentation - Haslwanter](https://work.thaslwanter.at/skinematics/html/rotmat.html)
  Snippet: Note: For displaying the Greek symbols for LaTeX expressions, such as ‘psi’, you may have to add the following lines to your Jupyter terminal:  ``` >>> from  sympy.interactive  import printing>>> printing. init_printing(use_latex = True) ```  ## Spatial Transformation Matrices...

### latex_help | Rotation Matrix latex 写法 求助

- Answer Summary: 在 LaTeX 中，二维旋转矩阵可写成 \[R(\theta)=\begin{pmatrix}\cos\theta & -\sin\theta \\ \sin\theta & \cos\theta\end{pmatrix}\]，三维绕 x、y、z 轴的矩阵分别为 \[R_x(\theta)=\begin{pmatrix}1&0&0\\0&\cos\theta&-\sin\theta\\0&\sin\theta&\cos\theta\end{pmatrix},\;R_y(\theta)=\begin{pmatrix}\cos\theta&0&\sin\theta\\0&1&0\\-\sin\theta&0&\cos\theta\end{pmatrix},\;R_z(\theta)=\begin{pmatrix}\cos\theta&-\sin\theta&0\\\sin\theta&\cos\theta&0\\0&0&1\end{pmatrix}\]，若要表示任意单位轴 \(\mathbf u=(u_x,u_y,u_z)\) 按角 \(\theta\) 的旋转，可使用罗德里格斯公式 \[R(\mathbf u,\theta)=\cos\theta\,I+(1-\cos\theta)\,\mathbf u\mathbf u^{\top}+\sin\theta\,[\mathbf u]_\times\]，其中 \([\mathbf u]_\times=\begin{pmatrix}0&-u_z&u_y\\u_z&0&-u_x\\-u_y&u_x&0\end{pmatrix}\) 为叉乘矩阵，全部代码可直接嵌入 LaTeX 文档中使用。
- [Rotation matrix - Wikipedia](https://en.wikipedia.org/wiki/Rotation_matrix)
  Snippet: This can be written more concisely as   where [u]× is the cross product matrix of u; the expression u ⊗ u is the outer product, and I is the identity matrix. Alternatively, the matrix entries are:  where εjkl is the Levi-Civita symbol with ε123 = 1. This is a matrix form of Ro...
- [Rotation Matrices — skinematics 0.10.4 documentation - Haslwanter](https://work.thaslwanter.at/skinematics/html/rotmat.html)
  Snippet: Note: For displaying the Greek symbols for LaTeX expressions, such as ‘psi’, you may have to add the following lines to your Jupyter terminal:  ``` >>> from  sympy.interactive  import printing>>> printing. init_printing(use_latex = True) ```  ## Spatial Transformation Matrices...
- [Rotation Matrices - Logos con carne](https://logosconcarne.com/stuff/rotation-matrices/)
  Snippet: The name, {R}_{xy}^{2}(\theta) identifies it as a Rotation matrix. As with the identity matrix, the superscript indicates a rotation in two dimensions, and the subscript that the rotation involves the X and Y coordinates (exactly as we’d expect in two dimensions). Also, note t...

### mixed_language | Rotation Matrix 中文 英文 混合 公式 写法

- Answer Summary: 在二维平面中，顺时针（或逆时针）旋转 θ 弧度的矩阵常写成 R(θ)=\(\begin{bmatrix}\cos\theta&-\sin\theta\\[2pt]\sin\theta&\cos\theta\end{bmatrix}\)，其中 “cosθ” 与 “sinθ” 为余弦、正弦函数，θ 为旋转角（使用弧度制），中文可描述为“绕原点逆时针旋转 θ”。在三维空间，若以 X、Y、Z 三轴分别为旋转轴，则常用的基于右手坐标系的旋转矩阵分别写作：\(\displaystyle R_x(\alpha)=\begin{bmatrix}1&0&0\\0&\cos\alpha&-\sin\alpha\\0&\sin\alpha&\cos\alpha\end{bmatrix}\)（绕 X 轴旋转 α），\(\displaystyle R_y(\beta)=\begin{bmatrix}\cos\beta&0&\sin\beta\\0&1&0\\-\sin\beta&0&\cos\beta\end{bmatrix}\)（绕 Y 轴旋转 β），以及 \(\displaystyle R_z(\gamma)=\begin{bmatrix}\cos\gamma&-\sin\gamma&0\\\sin\gamma&\cos\gamma&0\\0&0&1\end{bmatrix}\)（绕 Z 轴旋转 γ），其中 α、β、γ 同样使用弧度制，中文可写为“绕 X（Y、Z）轴旋转 α（β、γ）”。如果需要将多个旋转组合，只需按乘法顺序相乘，例如 “R=R_z(γ)·R_y(β)·R_x(α)”，中文可表述为“先绕 X 轴旋转 α，再绕 Y 轴旋转 β，最后绕 Z 轴旋转 γ”。这些公式在代码实现时常配合函数如 `cos(theta)`、`sin(theta)`，并注意在某些引擎（如 Godot）使用 `TAU` 或 `PI/2` 表示四分之一圈的弧度。
- [矩阵与变换— Godot Engine (4.3) 简体中文文档](https://docs.godotengine.org/zh-cn/4.3/tutorials/math/matrices_and_transforms.html)
  Snippet: 要从已存在的变换矩阵中计算对象的缩放尺度，可以对该矩阵的每个列向量使用 `length()` 方法。  `length()`  备注  在实际项目中，你可以使用 `scaled()` 方法去执行缩放变换操作。  `scaled()`  ### 旋转变换矩阵  我们将以与前面相同的方式开始本节内容，先在单位矩阵下方叠加一个 Godot logo 吧：  ../../_images/identity-godot.png  举个例子，假设我们想让 Godot logo 顺时针旋转 90 度，而现在 X 轴正方形向右，Y 轴正方向向下。如果我们在脑海中模...
- [[PDF] 數學式和數學用語的英文讀法](https://mcube.lab.nycu.edu.tw/wiki/core/uploads/Course/PS2014/MathSymbols.pdf)
  Snippet: orthocenter(AmE) 反正割 arc secant 重心 barycentre(BrE), barycenter(AmE) 反餘割 arc cosecant 體積 volume 投影 projection 表面積 surface area 旋轉 rotation 12 (10-10) Geometry (III): Lines and Coordinates 幾何 (三)： 線與座標 軌跡 locus, loci(pl.) 向量 vector 座標系 coordinate 象限 quadrant 直角座標系 Cartesian coor...
- [[PDF] 數學科常用英漢辭彙2020年7月8日版](https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/res/Glossary20200708.pdf)
  Snippet: remainder term 餘項 remainder theorem 餘式定理 repeated trials 重複試驗 repeating decimal 循環小數 repetend （小數的）循環節 resolution of vector 向量分解，矢量分解 resultant vector 合（成）向量，合（成）矢量 rhombus 菱形 Riemann sum 黎曼和 right angle 直角 right circular cone 直（立）圓錐（體） right circular cylinder 直（立）圓柱（體） right ...

### mixed_language | Rotation Matrix formula notes shorthand mixed language

- Answer Summary: A rotation matrix is the linear operator that rotates vectors while preserving lengths and angles; in two dimensions the compact form is \(\displaystyle R_{2D}(\theta)=\begin{bmatrix}\cos\theta&-\sin\theta\\[2pt]\sin\theta&\cos\theta\end{bmatrix}\), which maps \((x,y)^T\) to \((x\cos\theta-y\sin\theta,\;x\sin\theta+y\cos\theta)^T\); in three‑dimensional space the elementary yaw‑pitch‑roll (Z‑Y‑X) rotations are respectively \(\displaystyle R_{z}(\alpha)=\begin{bmatrix}\cos\alpha&-\sin\alpha&0\\[2pt]\sin\alpha&\cos\alpha&0\\[2pt]0&0&1\end{bmatrix},\;R_{y}(\beta)=\begin{bmatrix}\cos\beta&0&\sin\beta\\[2pt]0&1&0\\[2pt]-\sin\beta&0&\cos\beta\end{bmatrix},\;R_{x}(\gamma)=\begin{bmatrix}1&0&0\\[2pt]0&\cos\gamma&-\sin\gamma\\[2pt]0&\sin\gamma&\cos\gamma\end{bmatrix}\); a general rotation about a unit axis \(\mathbf u=(u_x,u_y,u_z)^T\) by angle \(\theta\) can be written succinctly with Rodrigues’ formula as \(\displaystyle R(\mathbf u,\theta)=I\cos\theta+(1-\cos\theta)\,\mathbf u\mathbf u^{\!T}+[\mathbf u]_{\times}\sin\theta\), where \(I\) is the \(3\times3\) identity, \(\mathbf u\mathbf u^{\!T}\) is the outer product, and \([\mathbf u]_{\times}=\begin{bmatrix}0&-u_z&u_y\\[2pt]u_z&0&-u_x\\[2pt]-u_y&u_x&0\end{bmatrix}\) is the cross‑product matrix; this compact notation unifies the axis‑angle representation and yields the same component formulas as the explicit Euler‑Rodrigues matrices.
- [Rotation matrix - Wikipedia](https://en.wikipedia.org/wiki/Rotation_matrix)
  Snippet: This can be written more concisely as   where [u]× is the cross product matrix of u; the expression u ⊗ u is the outer product, and I is the identity matrix. Alternatively, the matrix entries are:  where εjkl is the Levi-Civita symbol with ε123 = 1. This is a matrix form of Ro...
- [Rotation Matrix - Definition, Formula, Derivation, Examples - Cuemath](https://www.cuemath.com/algebra/rotation-matrix/)
  Snippet: P (y, \(\beta\)) = \(\begin{bmatrix} cos\beta & 0 & sin\beta\\ 0 &1 & 0 \\ -sin\beta & 0 & cos\beta \end{bmatrix}\). Such a matrix is known as a pitch. Here, it represents the counterclockwise rotation of \(\beta\) about the y axis.  P (z, \(\alpha\)) = \(\begin{bmatrix} cos\a...
- [Rotation Matrix in 2D & 3D: Derivation, Properties & Solved Examples](https://testbook.com/maths/rotation-matrix)
  Snippet: ## What is a Rotation Matrix?  A rotation matrix can be defined as a transformation matrix that operates on a vector and produces a rotated vector such that the coordinate axes always remain fixed. A rotation matrix is a transformation matrix that is used to perform a rotation...

## Jacobian Matrix

- Category: `matrix`
- Formula: `J = \begin{bmatrix} \frac{\partial f_1}{\partial \gamma_1} & \frac{\partial f_1}{\partial \gamma_2} \\ \frac{\partial f_2}{\partial \gamma_1} & \frac{\partial f_2}{\partial \gamma_2} \end{bmatrix}`

### messy_nl | Jacobian Matrix formula how do I type this

- Answer Summary: In LaTeX you can write the Jacobian matrix of a vector‑valued function \(\mathbf f=(f_{1},\dots ,f_{m})\) with respect to variables \(\mathbf x=(x_{1},\dots ,x_{n})\) as  

\[
J_{\mathbf f}(\mathbf x)=\frac{\partial (f_{1},\ldots ,f_{m})}{\partial (x_{1},\ldots ,x_{n})}
=\begin{pmatrix}
\frac{\partial f_{1}}{\partial x_{1}}&\dots &\frac{\partial f_{1}}{\partial x_{n}}\\
\vdots&\ddots &\vdots\\
\frac{\partial f_{m}}{\partial x_{1}}&\dots &\frac{\partial f_{m}}{\partial x_{n}}
\end{pmatrix},
\]  

where `\frac{\partial ...}{\partial ...}` produces a partial derivative and the matrix is created with `\begin{pmatrix} ... \end{pmatrix}` (or `\begin{bmatrix} ... \end{bmatrix}` for brackets). For the square case \(m=n\) the Jacobian determinant is written as  

\[
\det J=\left|\frac{\partial (f_{1},\ldots ,f_{n})}{\partial (x_{1},\ldots ,x_{n})}\right|.
\]
- [Jacobian matrix and determinant - Wikipedia](https://en.wikipedia.org/wiki/Jacobian_matrix_and_determinant)
  Snippet: The Jacobian matrix, whose entries are functions of x, is denoted in various ways; other common notations include Df, {\displaystyle \nabla \mathbf {f} }, and {\textstyle {\frac {\partial (f_{1},\ldots ,f_{m})}{\partial (x_{1},\ldots ,x_{n})}}}. Some authors define the Jacobia...
- [Jacobians](https://web.ma.utexas.edu/users/m408s/m408d/CurrentWeb/LM15-10-4.php)
  Snippet: the $2 \times 2$ matrix mean ''determinant'', not absolute value. The Jacobian $\frac{\partial(x,y)}{\partial(u,v)}$ may be positive or negative. |     |  |  | Change-of-variable formula: If a 1-1 mapping $\Phi$ sends a region $D^\$ in $uv$-space to a region $D$ in $xy$-space,...
- [Jacobian matrix of symbolic function - MATLAB - MathWorks](https://www.mathworks.com/help/symbolic/sym.jacobian.html)
  Snippet: Skip to content  Main Content  # jacobian  Jacobian matrix of symbolic function  collapse all in page;)  ## Syntax  `jacobian(f,v)`  ## Description  `jacobian(f,v)` computes the Jacobian matrix of symbolic function `f` with respect to `v`. The (i,j) element of the result is . ...

### messy_nl | Jacobian Matrix 这个公式怎么打

- Answer Summary: 在 LaTeX 中可以用 \verb|\[ ... \]|（或行间 \verb|$$ ... $$|）写出雅可比矩阵的完整公式，例如  
\[
J = \frac{\partial \mathbf{f}}{\partial \mathbf{x}}
   = \begin{bmatrix}
       \frac{\partial f_{1}}{\partial x_{1}} & \cdots & \frac{\partial f_{1}}{\partial x_{n}}\\
       \vdots                                 & \ddots & \vdots\\
       \frac{\partial f_{m}}{\partial x_{1}} & \cdots & \frac{\partial f_{m}}{\partial x_{n}}
     \end{bmatrix},
\]  
其中 \verb|\mathbf{f}| 表示向量函数 \((f_{1},\dots,f_{m})^{T}\)，\(\mathbf{x}=(x_{1},\dots,x_{n})^{T}\)，而矩阵的每个元素可用行内形式 \verb|$J_{ij} = \frac{\partial f_{i}}{\partial x_{j}}$| 表示。  
- [【漫话机器学习系列】266.雅可比矩阵（Jacobian Matrix） - 稀土掘金](https://juejin.cn/post/7505006357356593215)
  Snippet: 那么它的雅可比矩阵 J∈Rm×nJ \in \mathbb{R}^{m \times n} 为：  J=∂f∂x=[∂f1∂x1⋯∂f1∂xn∂f2∂x1⋯∂f2∂xn⋮⋱⋮∂fm∂x1⋯∂fm∂xn]J = \frac{\partial \mathbf{f}}{\partial \mathbf{x}} = \begin{bmatrix} \frac{\partial f\_1}{\partial x\_1} & \cdots & \frac{\partial f\_1}{\partial x\_n} \\ \frac{\partial f\_2}...
- [雅可比矩阵Jacobian & 海塞矩阵Hessian - 知乎专栏](https://zhuanlan.zhihu.com/p/655776763)
  Snippet: Part.I Jacobian Matrix在向量微积分中， 雅可比矩阵(Jacobian matrix)是一阶偏导数以一定方式排列成的矩阵，描述了函数在某点处的局部梯度，
- [史上最简SLAM零基础解读(7) - Jacobian matrix(雅可比矩阵) → 理论 ...](https://www.guyuehome.com/wap/detail?id=1825500237582364674)
  Snippet: 雅可比行列式是坐标变换理论的基础之一，在数学分析隐函数理论中发挥着重要作用。雅克比矩阵定义如下所示： 那么这个矩阵是如何来的，又有什么作用呢？不要着急，下面就来一

### plain_text | Jacobian Matrix plain text formula notation

- Answer Summary: The Jacobian of a vector‑valued function f : ℝⁿ→ℝᵐ is the m×n matrix whose (i,j) entry is the partial derivative of the i‑th component of f with respect to the j‑th variable, i.e. J_f = [∂f_i/∂x_j]_{i=1..m,\;j=1..n}, which can be written in plain‑text as “J = (∂f_i/∂x_j)”, “J = ∂(f₁,…,f_m)/∂(x₁,…,x_n)”, or displayed as [[∂f₁/∂x₁, …, ∂f₁/∂x_n]; … ; [∂f_m/∂x₁, …, ∂f_m/∂x_n]]; common alternative symbols are Df, ∇f, or J_F(U) when emphasizing that the Jacobian of F is taken with respect to the vector U.
- [Jacobian matrix and determinant - Wikipedia](https://en.wikipedia.org/wiki/Jacobian_matrix_and_determinant)
  Snippet: The Jacobian matrix, whose entries are functions of x, is denoted in various ways; other common notations include Df, {\displaystyle \nabla \mathbf {f} }, and {\textstyle {\frac {\partial (f_{1},\ldots ,f_{m})}{\partial (x_{1},\ldots ,x_{n})}}}. Some authors define the Jacobia...
- [notation - Correct way to write a symbol for the Jacobian matrix](https://math.stackexchange.com/questions/4029231/correct-way-to-write-a-symbol-for-the-jacobian-matrix)
  Snippet: \begin{equation} J =\frac{\partial F}{\partial U} = \begin{vmatrix}\frac{\partial F\_1}{\partial U\_1} && \frac{\partial F\_1}{\partial U\_2} \\ \frac{\partial F\_2}{\partial U\_1} && \frac{\partial F\_2 }{\partial U\_2}\end{vmatrix} \end{equation}  Which is the correct notati...
- [Geometric Meaning of Jacobian Matrix](https://angeloyeo.github.io/2020/07/24/Jacobian_en.html)
  Snippet: When we calculate the Jacobian matrix using this formula, we get:  \[J = \begin{bmatrix} \frac{\partial x}{\partial r} & \frac{\partial x}{\partial \theta} \\ \frac{\partial y}{\partial r} & \frac{\partial y}{\partial \theta} \end{bmatrix}\] \[= \begin{bmatrix}\cos(\theta) & -...

### plain_text | Jacobian Matrix keyboard formula input

- Answer Summary: To enter a Jacobian matrix with a keyboard, write the vector of functions \(f\) and the vector of variables \(x\) in plain text and use the appropriate function call for your software: in MATLAB the command is `J = jacobian(f, x)` where `f` and `x` are symbolic arrays (e.g., `f = [xyz; y^2; x+z]; x = [x; y; z];`), in Python with SymPy you type `J = Matrix(f).jacobian(Matrix(x))` after defining `x, y, z = symbols('x y z')` and `f = [x*y*z, y**2, x+z]`, and in LaTeX you can type `\begin{bmatrix}\frac{\partial f_1}{\partial x_1}&\dots&\frac{\partial f_1}{\partial x_n}\\\vdots&\ddots&\vdots\\\frac{\partial f_m}{\partial x_1}&\dots&\frac{\partial f_m}{\partial x_n}\end{bmatrix}` which renders the Jacobian matrix of a mapping \(f:\mathbb{R}^n\to\mathbb{R}^m\).
- [What is Jacobian Matrix? - Analytics Vidhya](https://www.analyticsvidhya.com/blog/2025/05/jacobian-matrix/)
  Snippet: Write the function for numerical approximation with NumPy.  `def numerical_jacobian(func, x, epsilon=1e-6): n = len(x) # Number of input variables m = len(func(x)) # Number of output variables jacobian = np.zeros((m, n)) for i in range(n): x_plus = x.copy() x_plus[i] += epsilo...
- [Jacobian matrix of symbolic function - MATLAB - MathWorks](https://www.mathworks.com/help/symbolic/sym.jacobian.html)
  Snippet: Skip to content  Main Content  # jacobian  Jacobian matrix of symbolic function  collapse all in page;)  ## Syntax  `jacobian(f,v)`  ## Description  `jacobian(f,v)` computes the Jacobian matrix of symbolic function `f` with respect to `v`. The (i,j) element of the result is . ...
- [A Recipe To Cook Jacobian - shahin rabbani](https://www.shahinrabbani.ca/jacobian/a-recipe-to-cook-jacobian)
  Snippet: ^{b}J(\theta) =   \begin{bmatrix} ^{b}\zeta\_1 && ^{b}\zeta{^\prime\_2} && \cdots && ^{b}\zeta{^\prime\_n}  \end{bmatrix}.  \end{equation}  Here, the \(j\)th column of \(J\) is the derivative of the mapping function \(g(\theta)\) with respect to the corresponding joint angle \...

### latex_help | Jacobian Matrix latex help input notation

- Answer Summary: To write a Jacobian matrix in LaTeX you place the array of partial derivatives inside a math‑mode matrix environment (e.g., `bmatrix` from amsmath) and use `\frac{\partial ...}{\partial ...}` (or the convenient `\pdv{...}{...}` macro from the physics package); for a function \(\mathbf{f}=(f_1,\dots,f_m)\) of variables \(\mathbf{x}=(x_1,\dots,x_n)\) the matrix can be coded as 
```latex
\[
\mathbf{J}_{\mathbf{f}}=
\begin{bmatrix}
\frac{\partial f_1}{\partial x_1}&\cdots&\frac{\partial f_1}{\partial x_n}\\[1ex]
\vdots&\ddots&\vdots\\[1ex]
\frac{\partial f_m}{\partial x_1}&\cdots&\frac{\partial f_m}{\partial x_n}
\end{bmatrix}
\] 
``` 
or, with the physics package, 
```latex
\[
\mathbf{J}_{\mathbf{f}}=
\begin{bmatrix}
\pdv{f_1}{x_1}&\cdots&\pdv{f_1}{x_n}\\[1ex]
\vdots&\ddots&\vdots\\[1ex]
\pdv{f_m}{x_1}&\cdots&\pdv{f_m}{x_n}
\end{bmatrix}
\] 
``` 
If you prefer a compact notation you can also write 
```latex
\[
J_{ij}=\frac{\partial f_i}{\partial x_j}
\] 
``` 
and then use `\begin{bmatrix} ... \end{bmatrix}` (or `array` with `\begin{array}{ccc}`) to display the full matrix.
- [Jacobian matrix and determinant - Wikipedia](https://en.wikipedia.org/wiki/Jacobian_matrix_and_determinant)
  Snippet: The Jacobian matrix, whose entries are functions of x, is denoted in various ways; other common notations include Df, {\displaystyle \nabla \mathbf {f} }, and {\textstyle {\frac {\partial (f_{1},\ldots ,f_{m})}{\partial (x_{1},\ldots ,x_{n})}}}. Some authors define the Jacobia...
- [How to write a Jacobian matrix in LaTeX - TeX](https://tex.stackexchange.com/questions/442103/how-to-write-a-jacobian-matrix-in-latex)
  Snippet: I am using LaTeX to write this Jacobian matrix:  `\mathbf{u_{i,j}}=\left[\begin{array}{ccc} \frac{\partial u_1}{\partial x_1} & \frac{\partial u_1}{\partial x_2} & \frac{\partial u_1}{\partial x_3} \\ \frac{\partial u_2}{\partial x_1} & \frac{\partial u_2}{\partial x_2} & \fra...
- [Latex jacobian symbol - Math-Linux.com](https://www.math-linux.com/latex/faq/latex-faq/article/latex-jacobian-symbol)
  Snippet: `$$ \begin{aligned} \mathbf{f}(\mathbf{x})&=\mathbf{f}(x_1,x_2,\dots,x_n)\\ &=(f_1(x_1,x_2,\dots,x_n),,\dots,f_m(x_1,x_2,\dots,x_n))\\ &=(f_1(\mathbf{x}),,\dots,f_m(\mathbf{x})) \end{aligned} $$` `$$ \mathbb{J}=\left[\begin{array}{ccc} \dfrac{\partial \mathbf{f}(\mathbf{x})}{\...

### latex_help | Jacobian Matrix latex 写法 求助

- Answer Summary: 在 LaTeX 中写 Jacobian 矩阵最简洁的办法是加载 amsmath 宏包并使用 bmatrix 环境，例如完整的 3×3 Jacobian 可以写成  

\[
J(\mathbf x)=\begin{bmatrix}
\displaystyle\frac{\partial f_{1}}{\partial x_{1}} & \displaystyle\frac{\partial f_{1}}{\partial x_{2}} & \displaystyle\frac{\partial f_{1}}{\partial x_{3}}\\[1ex]
\displaystyle\frac{\partial f_{2}}{\partial x_{1}} & \displaystyle\frac{\partial f_{2}}{\partial x_{2}} & \displaystyle\frac{\partial f_{2}}{\partial x_{3}}\\[1ex]
\displaystyle\frac{\partial f_{3}}{\partial x_{1}} & \displaystyle\frac{\partial f_{3}}{\partial x_{2}} & \displaystyle\frac{\partial f_{3}}{\partial x_{3}}
\end{bmatrix},
\]  

其中 \(\mathbf x=(x_{1},x_{2},x_{3})\) 且 \(\mathbf f=(f_{1},f_{2},f_{3})\)。若行列式的维数不同，只需相应改动行数 \(m\) 和列数 \(n\)，通用形式为  

\[
J(\mathbf x)=\begin{bmatrix}
\displaystyle\frac{\partial f_{1}}{\partial x_{1}} & \dots & \displaystyle\frac{\partial f_{1}}{\partial x_{n}}\\
\vdots & \ddots & \vdots\\
\displaystyle\frac{\partial f_{m}}{\partial x_{1}} & \dots & \displaystyle\frac{\partial f_{m}}{\partial x_{n}}
\end{bmatrix},
\]  

只要在文档导言区加入 `\usepackage{amsmath}`，上述代码即可正常编译并得到整洁的 Jacobian 矩阵。
- [How to write a Jacobian matrix in LaTeX - TeX](https://tex.stackexchange.com/questions/442103/how-to-write-a-jacobian-matrix-in-latex)
  Snippet: ## 3 Answers 3  @Sebastiano's answer shows what you need to do to get the code to compile without error or warning messages. In order to make the matrix easier to read and more visually appealing, you may additionally want to (a) increase the amount of whitespace between rows ...
- [Jacobian matrix and determinant - Wikipedia](https://en.wikipedia.org/wiki/Jacobian_matrix_and_determinant)
  Snippet: The Jacobian matrix, whose entries are functions of x, is denoted in various ways; other common notations include Df, {\displaystyle \nabla \mathbf {f} }, and {\textstyle {\frac {\partial (f_{1},\ldots ,f_{m})}{\partial (x_{1},\ldots ,x_{n})}}}. Some authors define the Jacobia...
- [Latex jacobian symbol - Math-Linux.com](https://www.math-linux.com/latex/faq/latex-faq/article/latex-jacobian-symbol)
  Snippet: \[\mathbb{J}=\left[\begin{array}{ccc} \dfrac{\partial \mathbf{f}(\mathbf{x})}{\partial x\_{1}} & \cdots & \dfrac{\partial \mathbf{f}(\mathbf{x})}{\partial x\_{n}} \end{array}\right]=\left[\begin{array}{c} \nabla^{T} f\_{1}(\mathbf{x}) \\ \vdots \\ \nabla^{T} f\_{m}(\mathbf{x})...

### mixed_language | Jacobian Matrix 中文 英文 混合 公式 写法

- Answer Summary: 雅可比矩阵（Jacobian matrix）常用的混合中英文写法是先用中文标出函数和自变量的意义，再在数学符号中使用英文或拉丁字母，例如  

\[
\mathbf{J}_{\mathbf{f}}(\mathbf{x})=
\begin{bmatrix}
\displaystyle\frac{\partial f_{1}}{\partial x_{1}} &
\displaystyle\frac{\partial f_{1}}{\partial x_{2}} &
\cdots &
\displaystyle\frac{\partial f_{1}}{\partial x_{n}}\\[6pt]
\displaystyle\frac{\partial f_{2}}{\partial x_{1}} &
\displaystyle\frac{\partial f_{2}}{\partial x_{2}} &
\cdots &
\displaystyle\frac{\partial f_{2}}{\partial x_{n}}\\
\vdots & \vdots & \ddots & \vdots\\
\displaystyle\frac{\partial f_{m}}{\partial x_{1}} &
\displaystyle\frac{\partial f_{m}}{\partial x_{2}} &
\cdots &
\displaystyle\frac{\partial f_{m}}{\partial x_{n}}
\end{bmatrix},
\qquad 
J_{ij}= \frac{\partial f_i}{\partial x_j},
\;i=1,\dots,m,\;j=1,\dots,n,
\]  

其中 \(f_i\) 为第 \(i\) 个分量函数（英文常写作 \(f_i\)），\(x_j\) 为第 \(j\) 个自变量（英文常写作 \(x_j\)），而整体矩阵可称为 **雅可比矩阵** 或 **Jacobian matrix**。在 LaTeX 中若需在公式里出现中文，可用 \text{...} 包裹，例如 \(\frac{\partial \text{函数}}{\partial \text{变量}}\)。这样既保持了数学符号的标准英文形式，又在文字说明中提供中文解释，适合中英文混排的学术文稿。
- [https://www.naer.edu.tw/opdata/188933257.csv](https://www.naer.edu.tw/opdata/188933257.csv)
  Snippet: isotopy,合痕；同痕,同痕 isotopy invariant,合痕不變式,同痕不?量 isotropic line,迷向[直]線,迷向直? isotropic subspace,迷向子空間,迷向子空? isotropic vector,迷向向量,迷向向量 isotropy subgroup,穩定子群,?定子群 iterated clique graph,迭代團圖,迭代?? iterated interpolation method,迭代插值法,迭代插值法 iterated kernel,疊核,?核 iteration sampling te...
- [[PDF] 学位论文 - 求解一类 矩阵范数逼近 问题的数值算法 - PolyU](https://www.polyu.edu.hk/ama/profile/dfsun//files/Thesis_Caihua.pdf)
  Snippet: Let ˜ Y = U TY V and ˜ X = U TXV . Let y(·, ·, ·), s(·, ·, ·) and H(·, ·, ·) be deﬁned by (2.22). Denote by h′ and g′ the partial Jacobian of s(·, ·, ·) and y(·, ·, ·) with respect to the last two variables at the point (ε, t, σ), respectively. For σi ̸= σj, we write g− ij = y...
- [[PDF] 博士学位论文](https://engineering.purdue.edu/~byao/Thesis/%E5%8D%9A%E5%A3%AB%E8%AE%BA%E6%96%87-%E5%BB%96%E5%BB%BA%E5%B3%B0_ZJU18.pdf)
  Snippet: In Chapter 2, a complete description of the chassis motion and the wheel motion is derived by means of theoretical modeling. With the study of wheel/ground interactions, a coupled dynamic of the over-actuated mobile robot is established. For the mobile manipulator, the complet...

### mixed_language | Jacobian Matrix formula notes shorthand mixed language

- Answer Summary: The Jacobian matrix of a vector‑valued function f : ℝⁿ→ℝᵐ is the m × n array of its first‑order partial derivatives, commonly written J_f(x)=\[\frac{\partial (f_1,\dots,f_m)}{\partial (x_1,\dots,x_n)}\] or simply Df, ∇f, and its entries are (J_f)_{ij}=∂f_i/∂x_j; many authors use the transpose of this form, but the standard convention is to list the derivatives of each component function in rows; when m=n the Jacobian is square and its determinant, denoted det J_f or ∂(x_1,…,x_n)/∂(u_1,…,u_n), gives the local volume scaling factor, appearing in the change‑of‑variables formula ∫_D g(x)dx = ∫_{D'} g(Φ(u)) |∂(x)/∂(u)| du, where the absolute value is taken because area or volume is always positive even if the oriented Jacobian is negative.
- [Jacobian matrix and determinant - Wikipedia](https://en.wikipedia.org/wiki/Jacobian_matrix_and_determinant)
  Snippet: The Jacobian matrix, whose entries are functions of x, is denoted in various ways; other common notations include Df, {\displaystyle \nabla \mathbf {f} }, and {\textstyle {\frac {\partial (f_{1},\ldots ,f_{m})}{\partial (x_{1},\ldots ,x_{n})}}}. Some authors define the Jacobia...
- [Jacobians](https://web.ma.utexas.edu/users/m408s/m408d/CurrentWeb/LM15-10-4.php)
  Snippet: the $2 \times 2$ matrix mean ''determinant'', not absolute value. The Jacobian $\frac{\partial(x,y)}{\partial(u,v)}$ may be positive or negative. |     |  |  | Change-of-variable formula: If a 1-1 mapping $\Phi$ sends a region $D^\$ in $uv$-space to a region $D$ in $xy$-space,...
- [Understanding the Jacobian Matrix and Determinant in Machine ...](https://medium.com/@dbhatt245/understanding-the-jacobian-matrix-and-determinant-in-machine-learning-298355ab0cb8)
  Snippet: ## Understanding the Jacobian Matrix  The Jacobian matrix provides valuable insights into the relationships between the input and output variables in a machine learning model. By examining the values in the Jacobian matrix, we can understand how changes in the input variables ...

## Law of Sines

- Category: `algebra_trig`
- Formula: `\frac{\sin A}{a} = \frac{\sin B}{b} = \frac{\sin C}{c}`

### messy_nl | Law of Sines formula how do I type this

- Answer Summary: The Law of Sines is written as \(\displaystyle \frac{a}{\sin A}=\frac{b}{\sin B}=\frac{c}{\sin C}\) or equivalently \(\displaystyle \frac{\sin A}{a}=\frac{\sin B}{b}=\frac{\sin C}{c}\); in plain‑text you can type it as “a/sin A = b/sin B = c/sin C”, and in LaTeX or most equation editors use the syntax “\frac{a}{\sin A} = \frac{b}{\sin B} = \frac{c}{\sin C}”.
- [Law of sines - Wikipedia](https://en.wikipedia.org/wiki/Law_of_sines)
  Snippet: sin ⁡ a sin ⁡ b sin ⁡ c . {\displaystyle {\begin{aligned}\sin ^{2}\!A&=1-\left({\frac {\cos a-\cos b\,\cos c}{\sin b\,\sin c}}\right)^{2}\\&={\frac {\left(1-\cos ^{2}\!b\right)\left(1-\cos ^{2}\!c\right)-\left(\cos a-\cos b\,\cos c\right)^{2}}{\sin ^{2}\!b\,\sin ^{2}\!c}}\\[8p...
- [2.1: The Law of Sines - Mathematics LibreTexts](https://math.libretexts.org/Bookshelves/Precalculus/Elementary_Trigonometry_(Corral)/02%3A_General_Triangles/2.01%3A_The_Law_of_Sines)
  Snippet: ## Theorem \(\PageIndex{1}\): Law of Sines  If a triangle has sides of lengths \(a \), \(b \), and \(c \) opposite the angles \(A \), \(B \), and \(C \), respectively, then  \[\label{2.1} \dfrac{a}{\sin\;A} ~=~ \dfrac{b}{\sin\;B} ~=~ \dfrac{c}{\sin\;C} ~. \]  Note that by taki...
- [Law of Sines - Formula, Cases & Examples | ChiliMath](https://www.chilimath.com/lessons/trigonometry/law-of-sines/)
  Snippet: Skip to content  ChiliMath Logo  ChiliMath Logo  # Sine Rule  # Law of Sines  To solve the unknown sides and angles of oblique triangles, we will need the Law of Sines or Sine Rule. By the way, an oblique triangle is a type of triangle which does not contain a right angle or a...

### messy_nl | Law of Sines 这个公式怎么打

- Answer Summary: 在 LaTeX 中可以这样输入正弦定理的公式，例如常用的两种等价写法：  

\[
\frac{a}{\sin\alpha}\;=\;\frac{b}{\sin\beta}\;=\;\frac{c}{\sin\gamma}
\]

或  

\[
\frac{\sin\alpha}{a}\;=\;\frac{\sin\beta}{b}\;=\;\frac{\sin\gamma}{c}
\]

对应的源码分别是 `\frac{a}{\sin\alpha} = \frac{b}{\sin\beta} = \frac{c}{\sin\gamma}` 和 `\frac{\sin\alpha}{a} = \frac{\sin\beta}{b} = \frac{\sin\gamma}{c}`，记得把公式放在 `\( … \)`（行内）或 `\[ … \]`（行间）之间即可。
- [Law of Sines | Proof, What Is?, History, How To Use?](https://helpingwithmath.com/law-of-sines/)
  Snippet: Mathematically, it can be defined as:  $\frac{sinsin \alpha}{a} = \frac{sinsin\beta}{b} = \frac{sinsin\gamma}{c}$  a, b and c are the lengths of a triangle; and   $\alpha, \beta, \gamma$ andare the opposite angles.  By taking the reciprocals, the Law of Sines can also be writt...
- [Law of sines - Wikipedia](https://en.wikipedia.org/wiki/Law_of_sines)
  Snippet: ![{\displaystyle {\begin{aligned}{\frac {abc}{2T}}&={\frac {abc}{2{\sqrt {s(s-a)(s-b)(s-c)}}}}\\[6pt]&={\frac {2abc}{\sqrt {{(a^{2}+b^{2}+c^{2})}^{2}-2(a^{4}+b^{4}+c^{4})}}},\end{aligned}}}]( {\textstyle s={\frac {1}{2}}\left(a+b+c\right).}  The second equality above readily s...
- [Law of Sines & Law of Cosines - American Board](https://americanboard.org/Subjects/mathematics/law-of-sines-law-of-cosines/)
  Snippet: Let A, B, and Crepresent the three interior angles of any triangle. Let adenote the length of the side that is opposite the angle A, bdenote the length of the side that is opposite the angle B, and cdenote the length of the side that is opposite the angle C.  The Law of Sines ...

### plain_text | Law of Sines plain text formula notation

- Answer Summary: The law of sines states that in any triangle the ratio of each side length to the sine of its opposite angle is constant, so \(a/\sin A = b/\sin B = c/\sin C\); equivalently, the reciprocal form is \(\sin A/a = \sin B/b = \sin C/c\).
- [Law of Sines - Formula, Cases & Examples | ChiliMath](https://www.chilimath.com/lessons/trigonometry/law-of-sines/)
  Snippet: In other words, the ratio of the sine of an angle in a triangle to its opposite side is the same as the ratios of the sines of the other two angles to their opposite sides. That is, the ratio of the sine of an angle to its opposite side is the same in every triangle.  That is ...
- [Law of Sines Formula & Examples - Lesson - Study.com](https://study.com/academy/lesson/law-of-sines-definition-and-application.html)
  Snippet: $$B = \sin^{-1} \left( \frac{ b\sin A}{a} \right) $$  To unlock this lesson you must be a Study.com member  Create an account  ## Law of Sines Examples  Solve the triangles illustrated below.  ### Example 1  An angle-angle-side problem: solve for angle C, and sides b and c.  |...
- [2.1: The Law of Sines - Mathematics LibreTexts](https://math.libretexts.org/Bookshelves/Precalculus/Elementary_Trigonometry_(Corral)/02%3A_General_Triangles/2.01%3A_The_Law_of_Sines)
  Snippet: ## Theorem \(\PageIndex{1}\): Law of Sines  If a triangle has sides of lengths \(a \), \(b \), and \(c \) opposite the angles \(A \), \(B \), and \(C \), respectively, then  \[\label{2.1} \dfrac{a}{\sin\;A} ~=~ \dfrac{b}{\sin\;B} ~=~ \dfrac{c}{\sin\;C} ~. \]  Note that by taki...

### plain_text | Law of Sines keyboard formula input

- Answer Summary: The Law of Sines can be entered on a standard keyboard as a/sin(A)=b/sin(B)=c/sin(C) or equivalently sin(A)/a = sin(B)/b = sin(C)/c, where a, b, c are the side lengths and A, B, C are the opposite angles; you may also write the common value as 2R, giving a/sin(A)=b/sin(B)=c/sin(C)=2R.
- [Law of Sines - Formula, Proof, Examples | Sine Rule](https://www.cuemath.com/trigonometry/sine-law/)
  Snippet: Solution:  For the given data, we can use the following formula of sine law: a/sinA = b/sinB = c/sinC   ⇒ 20/sin A = 25/sin 42º   ⇒ sin A/20 = sin 42º/25   ⇒ sin A = (sin 42º/25) × 20   ⇒ sin A = (sin 42º/25) × 20   ⇒ sin A = (0.6691/5) × 4   ⇒ sin A = 0.5353   ⇒ A = sin-1(0.5...
- [The Law of Sines](https://www.mathsisfun.com/algebra/trig-sine-law.html)
  Snippet: # The Law of Sines  The Law of Sines (or Sine Rule) is very useful for solving triangles:  a sin A  =  b sin B  =  c sin C  It works for any triangle:  |  |  | a, b and c are sides.  A, B and C are angles.  (Side a faces angle A,  side b faces angle B and  side c faces angle C...
- [Law of Sines Calculator](https://www.omnicalculator.com/math/law-of-sines)
  Snippet: The law of sines states that the proportion between the length of a side of a triangle to the sine of the opposite angle is equal for each side:  `a / sin(α) = b / sin(β) = c / sin(γ)`  `a / sin(α) = b / sin(β) = c / sin(γ)`  This ratio is also equal to the diameter of the tri...

### latex_help | Law of Sines latex help input notation

- Answer Summary: The standard LaTeX for the Law of Sines is written as a series of equal ratios, for example  

\[
\frac{\sin A}{a}\;=\;\frac{\sin B}{b}\;=\;\frac{\sin C}{c},
\]  

or, equivalently, using the reciprocal form  

\[
\frac{a}{\sin A}\;=\;\frac{b}{\sin B}\;=\;\frac{c}{\sin C},
\]  

and the pairwise version can be entered as  

\[
\frac{a}{b}\;=\;\frac{\sin A}{\sin B},\qquad 
\frac{a}{c}\;=\;\frac{\sin A}{\sin C},\qquad 
\frac{b}{c}\;=\;\frac{\sin B}{\sin C}.
\]  

In LaTeX code these appear as `\frac{\sin A}{a} = \frac{\sin B}{b} = \frac{\sin C}{c}`, `\frac{a}{\sin A} = \frac{b}{\sin B} = \frac{c}{\sin C}`, and `\frac{a}{b} = \frac{\sin A}{\sin B}` (etc.), all placed within a displayed‑math environment such as `\[` … `\]` or `$$` … `$$`.
- [Law of Sines: Videos & Practice Problems - Pearson](https://www.pearson.com/channels/trigonometry/learn/patrick/7-non-right-triangles/law-of-sines)
  Snippet: However, when dealing with non-right triangles, the approach changes significantly. In such cases, the Law of Sines becomes the primary tool for finding missing sides or angles. The Law of Sines states that the ratio of the sine of an angle to the length of the opposite side i...
- [2.1: The Law of Sines - Mathematics LibreTexts](https://math.libretexts.org/Bookshelves/Precalculus/Elementary_Trigonometry_(Corral)/02%3A_General_Triangles/2.01%3A_The_Law_of_Sines)
  Snippet: Using the \(\fbox{\(\sin^{-1}\)}\) button on a calculator gives \(B = 44.8^\circ \). However, recall from Section 1.5 that \(\sin\;(180^\circ - B) = \sin\;B \). So there is a second possible solution for \(B \), namely \(180^\circ - 44.8^\circ = 135.2^\circ \). Thus, we have t...
- [Making sense of the law of sines - Medium](https://medium.com/plus-minus/making-sense-of-the-law-of-sines-84ab0ad7c80b)
  Snippet: Up until now, I’ve used the notation ∠A with a single variable A to indicate an angle. This notation is short, but can be ambiguous if there are multiple angles that may be indicated by the single variable. For added clarity, I’ll sometimes use the notation ∠xzy to refer to th...

### latex_help | Law of Sines latex 写法 求助

- Answer Summary: 在 LaTeX 中写正弦定理常用两种等价形式，例如使用行间公式可以写成  
\[
\frac{\sin A}{a}=\frac{\sin B}{b}=\frac{\sin C}{c}
\]  
或等价的  
\[
\frac{a}{\sin A}=\frac{b}{\sin B}=\frac{c}{\sin C}=2R,
\]  
其中 \(A,B,C\) 为角，\(a,b,c\) 为对应的对边长度，\(R\) 为外接圆半径；在正文中若要内联显示，只需在两侧加上美元符号，如 \(\frac{\sin A}{a}=\frac{\sin B}{b}=\frac{\sin C}{c}\)。
- [Law of Sines - EquPlus.net - Science equations](https://equplus.net/eqninfo/Equation-285.html)
  Snippet: |  |  | Law of Sines | |  | | LaTeX Code:  \frac{{\sin A}}{a} = \frac{{\sin B}}{b} = \frac{{\sin C}}{c} | | MathType 5.0 Code: % MathType!MTEF!2!1!+-  % feaafaart1ev1aaatCvAUfeBSjuyZL2yd9gzLbvyNv2CaerbuLwBLn  % hiov2DGi1BTfMBaeXatLxBI9gBaerbd9wDYLwzYbItLDharqqr1ngB  % PrgifHhD...
- [Law of Sines - AoPS Wiki](https://artofproblemsolving.com/wiki/index.php/Law_of_Sines?srsltid=AfmBOordyx65AL9XD_6PrF73EzIs1H9AngljKufS9y0Iuva-VPaahWAY)
  Snippet: Since it doesn't matter which sides are chosen as $a$, $b$, and $c$, the following equality holds:  ![\[\frac{1}{2}bc\sin A = \frac{1}{2}ac\sin B = \frac{1}{2}ab\sin C\]](//latex.artofproblemsolving.com/b/3/c/b3c723d9efc56c7f0d769b4aa916faa52c0b7045.png)  Assuming the triangle...
- [2.1: The Law of Sines - Mathematics LibreTexts](https://math.libretexts.org/Bookshelves/Precalculus/Elementary_Trigonometry_(Corral)/02%3A_General_Triangles/2.01%3A_The_Law_of_Sines)
  Snippet: Library homepage  ## Search  x  #### Text Color  #### Text Size  #### Margin Size  #### Font Type  ##   selected template will load here  ## Error  This action is not available.  Library homepage Mathematics LibreTexts  # 2.1: The Law of Sines     \( \newcommand{\vecs}{\overse...

### mixed_language | Law of Sines 中文 英文 混合 公式 写法

- Answer Summary: 在任意三角形 \(ABC\) 中，邊長 \(a, b, c\) 分別對應於角 \(A, B, C\)，滿足正弦定理（Law of Sines）公式：\( \displaystyle \frac{a}{\sin A} = \frac{b}{\sin B} = \frac{c}{\sin C}\)，亦可寫成等價形式 \( \displaystyle \frac{\sin A}{a} = \frac{\sin B}{b} = \frac{\sin C}{c}\)。
- [正弦與餘弦 - 單維彰](https://shann.idv.tw/matheng/sine.html)
  Snippet: ### 數學英文  # 正弦與餘弦  Right Triangle  三角比    Trigonometric Ratios  只要指定任一銳角（就說是 \(\angle A\)，say \(\angle A\)）， 則所有這樣的直角 \(\triangle ABC\) 皆彼此相似 (similar)， 因此 \(a:b:c\) 是一個固定的比。 如果我們定義 \[a:b:c = \sin A:\sin B:1\] 再規定 \(\sin90^\circ:=1\)， 則所謂「正弦定理」(Law of Sines) 在直角三角形上僅為正弦 (sine)...
- [[PDF] AlterMundus - LaTeX 工作室](https://www.latexstudio.net/uploads/20250729/5bc4a786b2558c871205154a742600d7.pdf)
  Snippet: ”Le Monde” version 《世界报》版本. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 273 46.10. Triangle altitudes 三角形的高. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 274 46.11. Altitudes - other construction 高：其他构造方法. . . . . . . . . . . . . . ...
- [https://www.naer.edu.tw/opdata/188933257.csv](https://www.naer.edu.tw/opdata/188933257.csv)
  Snippet: interpolation formula,Lagrange插值公式,拉格朗日插值公式 Lagrange multiplier,Lagrange乘數；Lagrange乘子,拉格朗日乘? Laplace expansion,Laplace展開式,拉普拉斯展?式 Laplace transform,Laplace變換,拉普拉斯?? last term,末項,末? lateral area,側面積,?面? Latin square,拉丁方格；拉丁方陣,拉丁方 lattice,格子；絡,格 lattice group,格子群,格群 Laurent seri...

### mixed_language | Law of Sines formula notes shorthand mixed language

- Answer Summary: In any triangle ABC with side a opposite angle A, side b opposite B, and side c opposite C, the Law of Sines states that \(\frac{\sin A}{a}=\frac{\sin B}{b}=\frac{\sin C}{c}\), which can also be written as \(a/\sin A = b/\sin B = c/\sin C\); in shorthand this is often expressed as \(\sin A:\sin B:\sin C = a:b:c\) or equivalently \(a:b:c = \sin A:\sin B:\sin C\), a relation used for ASA, AAS, or SSA cases (en español: “la razón del seno de un ángulo a su lado opuesto es constante”).
- [Law of Sines - Formula, Cases & Examples | ChiliMath](https://www.chilimath.com/lessons/trigonometry/law-of-sines/)
  Snippet: Skip to content  ChiliMath Logo  ChiliMath Logo  # Sine Rule  # Law of Sines  To solve the unknown sides and angles of oblique triangles, we will need the Law of Sines or Sine Rule. By the way, an oblique triangle is a type of triangle which does not contain a right angle or a...
- [6-01 Law of Sines](https://www.andrews.edu/~rwright/Precalculus-RLW/Text/06-01.html)
  Snippet: $$Area = \frac{1}{2} bh$$  The height of the triangle is found using the left triangle.  $$\sin A = \frac{h}{c}$$  $$h = c \sin A$$  Substitute this into the area formula.  $$Area = \frac{1}{2} bc \sin A$$  ###### Area of ∆ABC Given 2 sides and the Included Angle  $$Area = \fr...
- [4.2: The Law of Sines - The Ambiguous Case](https://math.libretexts.org/Bookshelves/Precalculus/Elementary_Trigonometry_(Beveridge)/04%3A_The_Law_of_Sines_and_The_Law_of_Cosines/4.02%3A_The_Law_of_Sines_-_the_ambiguous_case)
  Snippet: \( \newcommand{\vectorA}{\vec{#1}}      % arrow\)  \( \newcommand{\vectorAt}{\vec{\text{#1}}}      % arrow\)  \( \newcommand{\vectorB}{\overset { \scriptstyle \rightharpoonup} {\mathbf{#1}} } \)  \( \newcommand{\vectorC}{\textbf{#1}} \)  \( \newcommand{\vectorD}{\overrightarro...

## Mean Squared Error

- Category: `stats_ml`
- Formula: `L = \frac{1}{M} \sum_{n=1}^{M} (\alpha_{n} - \hat{\alpha}_{n})^2`

### messy_nl | Mean Squared Error formula how do I type this

- Answer Summary: The mean‑squared‑error (MSE) of an estimator \(\hat{x}=g(y)\) is defined as the expected value of the squared deviation between the true value \(X\) and the estimate, often written as \( \text{MSE}=E\!\big[(X-\hat{x})^{2}\mid Y=y\big]=E\!\big[(X-g(y))^{2}\mid Y=y\big]\); for a sample of \(n\) paired actual and predicted values \(\{y_i,\hat{y}_i\}_{i=1}^{n}\) the practical formula is \(\displaystyle \text{MSE}=\frac{1}{n}\sum_{i=1}^{n}\big(\hat{y}_{i}-y_{i}\big)^{2}\), which in plain‑text can be typed as `MSE = (1/n) * Σ_{i=1}^{n} (y_hat_i - y_i)^2` or in LaTeX as `\text{MSE} = \frac{1}{n}\sum_{i=1}^{n}(\hat{y}_i - y_i)^2`.
- [Mean Squared Error (MSE) Loss Function - CodingNomads](https://codingnomads.com/mean-squared-error-loss-function)
  Snippet: ``` # actual values ys = [y1, y2, ..., yn] # predicted values yhats = [yhat1, yhat2, ..., yhatn] # calculate the mean squared error in one line mse = ((ys - yhat)2).mean()  ```  In this line, `(ys - yhat)2` calculates the squared differences between the actual and predicted va...
- [What is Mean Square Error (MSE)? Formula & Role - Deepchecks](https://deepchecks.com/glossary/mean-square-error-mse/)
  Snippet: Mean Squared Error Formula:  Where:   Yi is the i value seen.  correspond to the expected value  n = the number of occurrences  Mean squared error estimates are quite close to variance computations.  The mean squared error calculator is done by taking the observed value, subtr...
- [Mean Squared Error: Definition and Example - Statistics How To](https://www.statisticshowto.com/probability-and-statistics/statistics-definitions/mean-squared-error/)
  Snippet: MSE formula = (1/n) \ Σ(actual – forecast)2    Where:   n = number of items,  Σ = summation notation,  Actual = original or observed y-value,  Forecast = y-value from regression.  General steps to calculate the MSE from a set of X and Y values:  1. Find the regression line. 2....

### messy_nl | Mean Squared Error 这个公式怎么打

- Answer Summary: Mean Squared Error的常用写法是 MSE = \frac{1}{n}\sum_{i=1}^{n}(y_i - \hat{y}_i)^2，若只用普通字符可写成 MSE = (1/n) * Σ_{i=1}^{n}(y_i - ŷ_i)^2；在LaTeX中直接输入\text{MSE} = \frac{1}{n}\sum_{i=1}^{n}(y_i - \hat{y}_i)^2即可得到公式；在Word或Google Docs的公式编辑器里，选择“插入→公式”，然后键入 \frac{1}{n}\sum_{i=1}^{n}(y_i - \hat{y}_i)^2（或直接输入 MSE = (1/n)∑(y_i‑ŷ_i)^2）即可呈现该公式。
- [Mean Squared Error (MSE) - Statistics By Jim](https://statisticsbyjim.com/regression/mean-squared-error-mse/)
  Snippet: As the data points fall closer to the regression line, the model has less error, decreasing the MSE. A model with less error produces more precise predictions.  ## MSE Formula  The formula for MSE is the following.  formula for MSE.formula for MSE.  formula for MSE. formula fo...
- [Mean Squared Error - BYJU'S](https://byjus.com/maths/mean-squared-error/)
  Snippet: Mean Squared Error Formula  Mean Squared Error Formula  In more general language, if θ be some unknown parameter and θobs, i be the corresponding estimator, then the formula for mean square error of the given estimator is:  |  |  | MSE(θobs, i) = E[(θobs, i – θ)2] |  MSE(θobs,...
- [Mean Squared Error: Definition and Example - Statistics How To](https://www.statisticshowto.com/probability-and-statistics/statistics-definitions/mean-squared-error/)
  Snippet: MSE formula = (1/n) \ Σ(actual – forecast)2    Where:   n = number of items,  Σ = summation notation,  Actual = original or observed y-value,  Forecast = y-value from regression.  General steps to calculate the MSE from a set of X and Y values:  1. Find the regression line. 2....

### plain_text | Mean Squared Error plain text formula notation

- Answer Summary: The mean squared error (MSE) is calculated as the average of the squared differences between the observed values \(y_i\) and the predicted values \(\hat{y}_i\); mathematically it is expressed as \( \text{MSE} = \frac{1}{n}\sum_{i=1}^{n}(y_i - \hat{y}_i)^2 \), where \(n\) is the number of observations.
- [Mean Squared Error - GeeksforGeeks](https://www.geeksforgeeks.org/maths/mean-squared-error/)
  Snippet: graph  Model Error  ## Mean Squared Error Formula  The formula for the mean squared error is:  > Mean Squared Error =  \frac{1}{n}\sum\_{i = 1}^{n}(Y\_i - \hat Y\_i)^2  Where:   n is the number of observations in the dataset.  yiis the actual value of the observation.  \hat Y\...
- [Mean squared error](https://en.wikipedia.org/wiki/Mean_squared_error)
  Snippet: ![{\displaystyle {\begin{aligned}\operatorname {MSE} (S_{a}^{2})&=\operatorname {E} \left[\left({\frac {n-1}{a}}S_{n-1}^{2}-\sigma ^{2}\right)^{2}\right]\\&=\operatorname {E} \left[{\frac {(n-1)^{2}}{a^{2}}}S_{n-1}^{4}-2\left({\frac {n-1}{a}}S_{n-1}^{2}\right)\sigma ^{2}+\sigm...
- [A Deeper look at Mean Squared Error - Count Bayesie](https://www.countbayesie.com/blog/2019/1/30/a-deeper-look-at-mean-squared-error)
  Snippet: With MSE unpacked we can see that Mean Squared Error is quite literally:  $$\text{Mean Squared Error}=\text{Model Variance} + \text{Model Bias}^2 + \text{Irreducible Uncertainty}$$  ## Simulating Bias and Variance  It turns out that we actually need MSE is able to capture the ...

### plain_text | Mean Squared Error keyboard formula input

- Answer Summary: Mean Squared Error (MSE) can be written with plain keyboard characters as MSE = (1/n) * Σ_{i=1}^{n} (y_i – ŷ_i)², where n is the number of observations, y_i are the actual values, and ŷ_i are the predicted values (often typed as y_hat_i).
- [Mean Squared Error - GeeksforGeeks](https://www.geeksforgeeks.org/maths/mean-squared-error/)
  Snippet: graph  Model Error  ## Mean Squared Error Formula  The formula for the mean squared error is:  > Mean Squared Error =  \frac{1}{n}\sum\_{i = 1}^{n}(Y\_i - \hat Y\_i)^2  Where:   n is the number of observations in the dataset.  yiis the actual value of the observation.  \hat Y\...
- [Mean Squared Error: Definition and Example - Statistics How To](https://www.statisticshowto.com/probability-and-statistics/statistics-definitions/mean-squared-error/)
  Snippet: MSE formula = (1/n) \ Σ(actual – forecast)2    Where:   n = number of items,  Σ = summation notation,  Actual = original or observed y-value,  Forecast = y-value from regression.  General steps to calculate the MSE from a set of X and Y values:  1. Find the regression line. 2....
- [Mean squared error - Wikipedia](https://en.wikipedia.org/wiki/Mean_squared_error)
  Snippet: ![{\displaystyle {\begin{aligned}\operatorname {MSE} ({\hat {\theta }})&=\operatorname {E} _{\theta }\left[({\hat {\theta }}-\theta )^{2}\right]\\&=\operatorname {E} _{\theta }\left[\left({\hat {\theta }}-\operatorname {E} _{\theta }[{\hat {\theta }}]+\operatorname {E} _{\thet...

### latex_help | Mean Squared Error latex help input notation

- Answer Summary: The mean‑squared error for a set of predictions \(\hat{y}_i\) against true values \(y_i\) is written in LaTeX as 

\[
\text{MSE}= \frac{1}{n}\sum_{i=1}^{n}\bigl(y_{i}-\hat{y}_{i}\bigr)^{2},
\]

where `n` is the number of samples, `\sum_{i=1}^{n}` produces the summation sign, and the parentheses are escaped with `\bigl(` and `\bigr)` (or simply `(` and `)`) while the exponent is given by `^{2}`; the same expression can also be shown as the bias‑variance decomposition 

\[
\text{MSE}= \operatorname{Var}(\hat{\theta})+\bigl(\operatorname{Bias}(\hat{\theta})\bigr)^{2},
\] 

typed with `\operatorname{Var}` and `\operatorname{Bias}` for the variance and bias terms.
- [Mean squared error - Wikipedia](https://en.wikipedia.org/wiki/Mean_squared_error)
  Snippet: {\theta }}-\operatorname {E} _{\theta }[{\hat {\theta }}]\right)^{2}\right]+\operatorname {E} _{\theta }\left[2\left({\hat {\theta }}-\operatorname {E} _{\theta }[{\hat {\theta }}]\right)\left(\operatorname {E} _{\theta }[{\hat {\theta }}]-\theta \right)\right]+\operatorname {...
- [Classical ML Equations in LaTeX](https://blmoistawinde.github.io/ml_equations_latex/)
  Snippet: ## Loss  ### Regression  Below xxx and yyy are DDD dimensional vectors, and xix\_ixi​ denotes the value on the $i$th dimension of xxx.  #### Mean Absolute Error(MAE)  ∑i=1D∣xi−yi∣\sum\_{i=1}^{D}|x\_i-y\_i| i=1∑D​∣xi​−yi​∣  `\sum_{i=1}^{D}|x_i-y_i|` `\sum_{i=1}^{D}|x_i-y_i|`  #...
- [Mean Squared Error (MSE) Loss Function - CodingNomads](https://codingnomads.com/mean-squared-error-loss-function)
  Snippet: Here's the break down the components of this formula:   $`n`$ is the total number of items or instances in your dataset.  $`\sum\_{i=1}^{n}`$ is a mathematical notation that means "sum up everything from the first item (i=1) to the nth item".  $`\hat{y\_i}`$ represents the "$`...

### latex_help | Mean Squared Error latex 写法 求助

- Answer Summary: 在 LaTeX 中常用的均方误差（Mean Squared Error）写法如下：  

\[
\operatorname{MSE}= \frac{1}{n}\sum_{i=1}^{n}\bigl(y_{i}-\hat{y}_{i}\bigr)^{2}
\]

如果需要矩阵形式则可写成  

\[
\operatorname{MSE}= \frac{1}{n}\,\mathbf{e}^{\mathsf{T}}\mathbf{e},
\qquad \text{其中 } \mathbf{e}= \mathbf{y}-\hat{\mathbf{y}} .
\]
- [Mean squared error - Wikipedia](https://en.wikipedia.org/wiki/Mean_squared_error)
  Snippet: {\theta }})+\operatorname {Bias} _{\theta }({\hat {\theta }},\theta )^{2}\end{aligned}}}]( [...] This definition depends on the unknown parameter, therefore the MSE is a priori property of an estimator. The MSE could be a function of unknown parameters, in which case any estim...
- [immse - Mean-squared error - MATLAB - MathWorks](https://www.mathworks.com/help/images/ref/immse.html)
  Snippet: Skip to content  Main Content  # immse  Mean-squared error  collapse all in page;)  ## Syntax  `err = immse(X,Y)`  ## Description  `err = immse(X,Y)` calculates the mean-squared error (MSE) between the arrays `X` and `Y`. A lower MSE value indicates greater similarity between ...
- [Classical ML Equations in LaTeX](https://blmoistawinde.github.io/ml_equations_latex/)
  Snippet: ## Loss  ### Regression  Below xxx and yyy are DDD dimensional vectors, and xix\_ixi​ denotes the value on the $i$th dimension of xxx.  #### Mean Absolute Error(MAE)  ∑i=1D∣xi−yi∣\sum\_{i=1}^{D}|x\_i-y\_i| i=1∑D​∣xi​−yi​∣  `\sum_{i=1}^{D}|x_i-y_i|` `\sum_{i=1}^{D}|x_i-y_i|`  #...

### mixed_language | Mean Squared Error 中文 英文 混合 公式 写法

- Answer Summary: Mean Squared Error（均方误差，MSE）的常用写法是  
\[
\text{MSE}= \frac{1}{n}\sum_{i=1}^{n}\bigl(y_i-\hat{y}_i\bigr)^{2},
\]  
其中 \(y_i\) 表示第 \(i\) 个观测的真实值（actual value），\(\hat{y}_i\) 表示对应的预测值（predicted value），\(n\) 为样本总数；等价的统计学定义为 \(\operatorname{MSE}(T)=\operatorname{E}\bigl[(T-\theta)^{2}\bigr]=\operatorname{Var}(T)+\bigl(\operatorname{Bias}(T)\bigr)^{2}\)，其中 \(\theta\) 为不可观测的真参数，\(T\) 为其估计量，\(\operatorname{Bias}(T)=\operatorname{E}(T)-\theta\)。
- [均方誤差- 維基百科，自由的百科全書](https://zh.wikipedia.org/wiki/%E5%9D%87%E6%96%B9%E8%AF%AF%E5%B7%AE)
  Snippet: 维基百科 自由的百科全书  ## 目录  # 均方误差  本页使用了标题或全文手工转换  在统计学中，平均平方誤差（mean-square error，MSE）或均方误差，又称均方偏差（mean-square deviation，MSD）、均方差，是预测值或估计值与真实值的差异平方的均值。均方误差越小说明模型的预测或者参数的估计精度越准确。  ## 計算公式  对于无法观察的参数  θ {\displaystyle \theta } {\displaystyle \theta }的一个估计函数T；其定义为：  {\displaystyle \the...
- [[PDF] 數學科常用英漢辭彙2020年7月8日版](https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/ma/res/Glossary20200708.pdf)
  Snippet: remainder term 餘項 remainder theorem 餘式定理 repeated trials 重複試驗 repeating decimal 循環小數 repetend （小數的）循環節 resolution of vector 向量分解，矢量分解 resultant vector 合（成）向量，合（成）矢量 rhombus 菱形 Riemann sum 黎曼和 right angle 直角 right circular cone 直（立）圓錐（體） right circular cylinder 直（立）圓柱（體） right ...
- [表達式管理器 - LimeSurvey](https://www.limesurvey.org/manual/index.php?title=Expression_Manager/zh&variant=zh-hant)
  Snippet: | 顏色 | 實例 | 含義 | 工具提示 | 注釋 |  ---  ---  | 棕褐色背景 | Sample | 整個方程式 | none | 花括號中被識別為方程式的任何東西（例如，沒有前導或尾隨空白）將用棕褐色背景進行顏色編碼，以幫助將其與周圍文本區分開來 | | 粗體紅色文本 | Sample | 錯誤 | 關於錯誤的一些解釋 | 可以是一個未知變量或函數中的錯誤，……調查可以被完全破壞，所以不要向公眾用戶展示。 | | 藍色文本 | Sample | 函數名稱 | 含義和允許語法 | 函數名稱，或者應該是函數的東西，因為它們後跟一個左括...

### mixed_language | Mean Squared Error formula notes shorthand mixed language

- Answer Summary: The mean squared error (MSE) of a predictor \(\hat{Y}\) for observed values \(Y\) over a sample of size \(n\) is defined as \(\displaystyle \operatorname{MSE}= \frac{1}{n}\sum_{i=1}^{n}\bigl(Y_{i}-\hat{Y}_{i}\bigr)^{2}\), i.e. the average of the squared deviations between each true value \(Y_i\) and its corresponding prediction \(\hat{Y}_i\); in estimator notation, for an estimator \(\hat\theta\) of a parameter \(\theta\) the MSE can be decomposed as \(\displaystyle \operatorname{MSE}(\hat\theta)=\mathbb{E}\bigl[(\hat\theta-\theta)^{2}\bigr]=\operatorname{Var}(\hat\theta)+\bigl(\operatorname{Bias}(\hat\theta,\theta)\bigr)^{2}\), showing that total error consists of variance plus the squared bias (plus any irreducible error in a modelling context); the quantity is always non‑negative, reaches zero only for a perfect predictor, and larger errors are penalised more heavily because of the squaring operation.
- [Mean squared error - Wikipedia](https://en.wikipedia.org/wiki/Mean_squared_error)
  Snippet: An even shorter proof can be achieved using the well-known formula that for a random variable {\textstyle X}, {\textstyle \mathbb {E} (X^{2})=\operatorname {Var} (X)+(\mathbb {E} (X))^{2}}.[citation needed] By substituting {\textstyle X} with, {\textstyle {\hat {\theta }}-\the...
- [Mean Squared Error (MSE) - Statistics By Jim](https://statisticsbyjim.com/regression/mean-squared-error-mse/)
  Snippet: As the data points fall closer to the regression line, the model has less error, decreasing the MSE. A model with less error produces more precise predictions.  ## MSE Formula  The formula for MSE is the following.  formula for MSE.formula for MSE.  formula for MSE. formula fo...
- [Mean Squared Error (MSE) Loss Function - CodingNomads](https://codingnomads.com/mean-squared-error-loss-function)
  Snippet: Here's the break down the components of this formula:   $`n`$ is the total number of items or instances in your dataset.  $`\sum\_{i=1}^{n}`$ is a mathematical notation that means "sum up everything from the first item (i=1) to the nth item".  $`\hat{y\_i}`$ represents the "$`...

## Gradient Descent Update

- Category: `stats_ml`
- Formula: `\phi_{n} = \phi_{n-1} - \eta \nabla J(\phi_{n-1})`

### messy_nl | Gradient Descent Update formula how do I type this

- Answer Summary: The standard gradient‑descent update can be written as θₜ₊₁ = θₜ − α ∇J(θₜ) (where θₜ is the parameter vector at iteration t, α is the learning‑rate hyperparameter, and ∇J(θₜ) is the gradient of the loss function J evaluated at θₜ); equivalently, for a variable x and objective f(x) the update is xₙ₊₁ = xₙ − α ∇f(xₙ).
- [The Art of Optimization: Understanding Gradient Descent](https://community.ibm.com/community/user/ai-datascience/blogs/danish-hasarat/2024/03/26/optimization-understanding-gradient-des)
  Snippet: ## Basic Formulation:  Let’s delve into the basic mathematical formulation of Gradient Descent. Suppose we have a parameter vector θ and a loss functionJ(θ) that we aim to minimize. The update rule for Gradient Descent can be expressed as follows:  Here, θt​ denotes the parame...
- [12.3. Gradient Descent - Dive into Deep Learning](http://d2l.ai/chapter_optimization/gd.html)
  Snippet: Recall that we have the update \(x^{(k+1)} = x^{(k)} - f'(x^{(k)}) / f''(x^{(k)})\). Plugging in this update equation and taking the absolute value of both sides, we have  (12.3.12)¶\[\left|e^{(k+1)}\right| = \frac{1}{2}(e^{(k)})^2 \frac{\left|f'''(\xi^{(k)})\right|}{f''(x^{(k...
- [Gradient descent (article) | Khan Academy](https://www.khanacademy.org/math/multivariable-calculus/applications-of-multivariable-derivatives/optimizing-multivariable-functions/a/what-is-gradient-descent)
  Snippet: x 1=x 0−α∇f(x 0)‍  More generally, we can write a formula for turning x n‍ into x n+1‍:  x n+1=x n−α∇f(x n)‍  Starting from an initial guess x 0‍, we keep improving little by little until we find a local minimum. This process may take thousands of iterations, so we typically i...

### messy_nl | Gradient Descent Update 这个公式怎么打

- Answer Summary: 在 LaTeX 中常用的梯度下降更新式可以写成  

\[
x^{k}=x^{k-1}-\eta\,\nabla f\!\left(x^{k-1}\right),
\] 

其中 \(\eta\) 为学习率（步长），\(\nabla f(x^{k-1})\) 为在第 \(k-1\) 次迭代点的函数梯度。如果要在行内显示，只需使用 `$x^{k}=x^{k-1}-\eta\,\nabla f(x^{k-1})$`；若在独立公式环境中，则使用 `\[\]` 包裹，如上所示。若需要写成向量形式，可把 \(x\) 与 \(\nabla f\) 都记成向量符号，例如 `\mathbf{x}^{k}=\mathbf{x}^{k-1}-\eta\,\nabla f(\mathbf{x}^{k-1})`。
- [机器学习中的那些优化算法 - Just Me](https://huangzichun.github.io/2021/06/20/Optimization_1-2021/)
  Snippet: # 0x01 First-order Methods  ## 0x01\_1 Gradient Descent  梯度下降，无约束优化中的常用方法，假设函数$f(x)$是可微的光滑凸函数，满足$domain(f)=R^{n}$，下式的优化目标形式成为无约束优化  \[\min f(x)\]  为了求解出这个 $ x^{\} $，我们可以直接求解$\bigtriangledown f(x^{\} )=0$，但是不容易直接求解出来的。然后我们可以采用迭代的方式，找出一组$x$的序列$x^{0}, x^{1},$满足当$k \rightarrow \in...
- [梯度下降算法总结 - 卢明冬的博客](https://lumingdong.cn/summary-of-gradient-descent-algorithm.html)
  Snippet: Adagrad 修改了 t 时刻对于每个参数 $\theta\_{i}$的学习率 $\eta$：  $$\theta\_{t+1,i}=\theta\_{t,i}-\frac{\eta}{\sqrt{G\_{t,ii}+\epsilon}} \cdot g\_{t,i}$$  其中，   $G\_{t}\in R^{d \times d}$是对角矩阵，AdaGrad 算法维护了一个累积梯度平方和的对角矩阵 $G\_t$来实现二阶动量，每一个对角元素 $G\_t^{(i，i)}$ 是 $\theta\_{i}$在时刻 t 之前累积的梯度平方和，用公式...
- [An overview of gradient descent optimization algorithms - ruder.io](https://www.ruder.io/optimizing-gradient-descent/)
  Snippet: \( \Delta \theta\_t = - \dfrac{\eta}{RMS[g]\_{t}} g\_t\).  The authors note that the units in this update (as well as in SGD, Momentum, or Adagrad) do not match, i.e. the update should have the same hypothetical units as the parameter. To realize this, they first define anothe...

### plain_text | Gradient Descent Update plain text formula notation

- Answer Summary: The basic gradient‑descent update is written in plain‑text notation as θ ← θ ‑ η ∇_θ J(θ), where θ represents the parameters (often a weight vector w), η is a positive learning‑rate scalar, and ∇_θ J(θ) is the gradient of the loss (or objective) function J with respect to θ.
- [12.3. Gradient Descent - Dive into Deep Learning](http://d2l.ai/chapter_optimization/gd.html)
  Snippet: Recall that we have the update \(x^{(k+1)} = x^{(k)} - f'(x^{(k)}) / f''(x^{(k)})\). Plugging in this update equation and taking the absolute value of both sides, we have  (12.3.12)¶\[\left|e^{(k+1)}\right| = \frac{1}{2}(e^{(k)})^2 \frac{\left|f'''(\xi^{(k)})\right|}{f''(x^{(k...
- [Understanding Gradient Descent Algorithm and the Maths Behind It](https://www.analyticsvidhya.com/blog/2021/08/understanding-gradient-descent-algorithm-and-the-maths-behind-it/)
  Snippet: ## The Core of Gradient Descent Optimisation Algorithm  Gradient Descent is an Iterative Solver. The Iterative solver does not give the exact solution. Not in all cases, the objective function is solvable.  In such cases, the iterative solvers are used to get the approximate s...
- [A worked example on updating weights by gradient descent - Medium](https://medium.com/mitb-for-all/a-worked-example-on-updating-weights-by-gradient-descent-9a12181ed2b9)
  Snippet: Applying the equation, you can compute the loss to be 1.12 when w=0.5. Note that this is the absolute loss, NOT the gradient.  Finally, let’s go all the way back to the very first equation you see in this post:  Gradient descent algorithm to update weights w based on the gradi...

### plain_text | Gradient Descent Update keyboard formula input

- Answer Summary: The standard gradient‑descent update is written as θ←θ−α∇J(θ), meaning that at each iteration the parameter vector θ is replaced by the current θ minus the learning‑rate α times the gradient of the loss J with respect to θ; equivalently for a variable x one writes x_{k+1}=x_k−η∇f(x_k), where η is the step size and ∇f(x_k) is the vector of partial derivatives [∂f/∂x₁,…,∂f/∂x_d]ᵀ evaluated at x_k.
- [12.3. Gradient Descent - Dive into Deep Learning](http://d2l.ai/chapter_optimization/gd.html)
  Snippet: Recall that we have the update \(x^{(k+1)} = x^{(k)} - f'(x^{(k)}) / f''(x^{(k)})\). Plugging in this update equation and taking the absolute value of both sides, we have  (12.3.12)¶\[\left|e^{(k+1)}\right| = \frac{1}{2}(e^{(k)})^2 \frac{\left|f'''(\xi^{(k)})\right|}{f''(x^{(k...
- [The Art of Optimization: Understanding Gradient Descent](https://community.ibm.com/community/user/ai-datascience/blogs/danish-hasarat/2024/03/26/optimization-understanding-gradient-des)
  Snippet: ## Basic Formulation:  Let’s delve into the basic mathematical formulation of Gradient Descent. Suppose we have a parameter vector θ and a loss functionJ(θ) that we aim to minimize. The update rule for Gradient Descent can be expressed as follows:  Here, θt​ denotes the parame...
- [ML - Stochastic Gradient Descent (SGD) - GeeksforGeeks](https://www.geeksforgeeks.org/machine-learning/ml-stochastic-gradient-descent-sgd/)
  Snippet: In traditional gradient descent, the gradients are computed based on the entire dataset which can be computationally expensive for large datasets.  In Stochastic Gradient Descent, the gradient is calculated for each training example (or a small subset of training examples) rat...

### latex_help | Gradient Descent Update latex help input notation

- Answer Summary: Use a vector‑or‑parameter notation such as  
\[
\theta_{t+1}= \theta_{t}-\eta\,\nabla_{\theta}\,L(\theta_{t})\!,
\]  
where \(\theta_{t}\) is the parameter (or input) vector at iteration \(t\), \(\eta\) is the learning‑rate scalar, and \(\nabla_{\theta}L(\theta_{t})\) is the gradient of the loss (or objective) \(L\) with respect to \(\theta\) evaluated at \(\theta_{t}\); in a two‑dimensional case you can write \(\langle x_{t+1},y_{t+1}\rangle =\langle x_{t},y_{t}\rangle-\eta\,\nabla f(x_{t},y_{t})\).
- [Understanding gradient descent - Eli Bendersky's website](https://eli.thegreenplace.net/2016/understanding-gradient-descent)
  Snippet: So \theta=0 gives us the largest positive change in f(x,y). To get \theta=0, \vec{v} has to point in the same direction as the gradient. Similarly, for \theta=180^{\circ} we get cos(\theta)=-1 and therefore the largest negative change in f(x,y). So if we want to decrease f(x,y...
- [Gradient notation spacing - TeX - LaTeX Stack Exchange](https://tex.stackexchange.com/questions/470154/gradient-notation-spacing)
  Snippet: enter image description here  enter image description here  Here's the picture of what you get from the previous input by just changing `\!#1` into `\mspace{-4mu}#1` (`\!` is the same as `\mspace{-3mu}`).  `\!#1` `\mspace{-4mu}#1` `\!` `\mspace{-3mu}`  enter image description ...
- [[PDF] Suggested Notation for Machine Learning](https://ctan.math.utah.edu/ctan/tex-archive/macros/latex/contrib/mlmath/mlmath.pdf)
  Snippet: The Rademacher complexity of a hypothesis space H on a sample set S is denoted by Rad(H◦S) or RadS(H). The complexity RadS(H) is random because of the randomness of S. The expectation of the empirical Rademacher complexity over all samples of size n is denoted by Radn(H) = ESR...

### latex_help | Gradient Descent Update latex 写法 求助

- Answer Summary: 在 LaTeX 中，梯度下降的基本更新式常写为 \[ x_{k+1}=x_{k}-\alpha\,\nabla f(x_{k}) \]，其中 \(x_{k}\) 为第 \(k\) 次迭代的参数向量，\(\alpha>0\) 为学习率（步长），\(\nabla f(x_{k})\) 为目标函数 \(f\) 在 \(x_{k}\) 处的梯度；若使用随机梯度下降，则可写成 \[ \theta_{t+1}= \theta_{t}-\alpha\,\nabla_{\theta}\,\ell(\theta_{t};\,x_{i},y_{i}) \]，其中 \(\ell\) 为单样本损失函数，\((x_{i},y_{i})\) 为本次抽取的样本；若采用小批量（mini‑batch）SGD，则在梯度上取批量平均： \[ \theta_{t+1}= \theta_{t}-\alpha\,\frac{1}{|B|}\sum_{(x_i,y_i)\in B}\nabla_{\theta}\,\ell(\theta_{t};\,x_{i},y_{i}) \]，其中 \(B\) 为当前批量的样本集合。所有这些公式均可直接放入 LaTeX 文档的 display‑math 环境（如 \[...\] 或 $$...$$）或行内环境（如 \( ... \)）使用。
- [[PDF] Lecture 5: Gradient Desent Revisited 5.1 Choose step size](https://www.cs.cmu.edu/~ggordon/10725-F12/scribes/10725_Lecture5.pdf)
  Snippet: 10-725: Optimization Fall 2012 Lecture 5: Gradient Desent Revisited Lecturer: GeoﬀGordon/Ryan Tibshirani Scribes: Cong Lu/Yu Zhao Note: LaTeX template courtesy of UC Berkeley EECS dept. Disclaimer: These notes have not been subjected to the usual scrutiny reserved for formal p...
- [[PDF] 1 Lecture 10: descent methods Gradient descent (reminder)](https://bayen.berkeley.edu/sites/default/files/lecture101.pdf)
  Snippet: (guess) Repeat Determine a descent direction Choose a step Update Until stopping criterion is satisfied Now you are here 12 Generalization to multiple dimensions Start with a point (guess) Repeat Determine a descent direction Choose a step Update Until stopping criterion is sa...
- [[PDF] 基于梯度的三种优化方法及比较](https://pdf.hanspub.org/SA20240100000_26290188.pdf)
  Snippet: 算法框架： 步1 输入：参数 0 0 α > ，随机选取初始点 0 x ， : 0 k = ， 0 ε > ； 步2 设置终止条件，直到满足终止条件，停止迭代，转步6； 步3 随机均匀的从取值范围中进行选择 { } 1,2, , k i n ∈  ； 步4 计算梯度方向 ( ) k k i k d L x = −∇ ； 步5 1 : k k k k x x d α + = + ， : 1 k k = + ，转步2； 步6 输出结果。 随机梯度下降算法中的每次迭代都与N 无关，使用简单、收敛速度快，所以在大规模机器学习算法 中非常具有吸引力，得到了...

### mixed_language | Gradient Descent Update 中文 英文 混合 公式 写法

- Answer Summary: 梯度下降的更新公式常写成 θ←θ−η∇_θL(θ) ，其中 θ 表示模型参数（如权重 w 和偏置 b）， η 是学习率（learning rate）， ∇_θL(θ) 是损失函数 L(θ) 对参数的梯度；若只对单个样本 (x_i,y_i) 使用随机梯度，则写作 θ←θ−η∇_θℓ(x_i,y_i;θ) ，其中 ℓ 是单样本损失。对于线性回归的权重 w 和偏置 b，具体更新可以写为 w←w−η·(−2x_i(y_i−(w x_i+b))) 和 b←b−η·(−2(y_i−(w x_i+b)))。
- [什么是随机梯度下降？ - IBM](https://www.ibm.com/cn-zh/think/topics/stochastic-gradient-descent)
  Snippet: ### 混合方法：  当训练时间成为瓶颈时，SGD 和其他 GD 变体就会派上用场。5  | 变体 | 每个步骤使用的数据 | 主要功能 | 常用 |  ---  --- | | GD | 所有数据 | 稳定但缓慢 | 小型数据集 | | 新加坡元 | 1 个经典 SGD 样本 | 嘈杂但快速 | 在线学习 | | 小批次 GD | 少量样本 | 平衡且可扩展 | 深度学习 | | Momentum | 批次/小批次 | 朝正确的方向加速 | 神经网络 | | NAG | 批次/小批次 | Look-ahead 动量 | 更快的收敛速度 | | A...
- [optimization - 演算法筆記](https://web.ntnu.edu.tw/~algo/Optimization.html)
  Snippet: 梯度是相鄰高度差再除以dx，功效差不多。因為數學家喜歡梯度，所以採用梯度。為了得到梯度，函數必須一次可微。  梯度大小是傾斜程度。梯度方向是最陡的方向，是等高線的垂直方向。朝梯度方向走會上升、得最大值，朝梯度反方向走會下降、得最小值。步伐太大，會走之字路線，無傷大雅。  原始論文只找山谷、未找山峰，因而取名為「下降」。  優點：方向明確，不必隨機亂走試誤，攻頂速度更快。  adaptive gradient descent（自適應梯度下降法）  梯度下降法改良版。隨時調整前進方向、隨時調整步伐大小。調整方式層出不窮，人人有一套理論：  最近走紅的演...
- [什么是梯度下降？机器学习中的优化 - Ultralytics](https://www.ultralytics.com/zh/glossary/gradient-descent)
  Snippet: ``` import torch # Create a tensor representing a weight, tracking gradients w = torch.tensor([5.0], requires_grad=True) # Define a simple loss function: (w - 2)^2. Minimum is at w=2. loss = (w - 2)  2 # Backward pass: Calculate the gradient (slope) of the loss with respect to...

### mixed_language | Gradient Descent Update formula notes shorthand mixed language

- Answer Summary: The basic gradient‑descent step updates the parameters by moving them opposite the gradient of the loss: in vector form θ^{(t+1)} = θ^{(t)} − η ∇_θ J(θ^{(t)}), and component‑wise θ_j^{(t+1)} = θ_j^{(t)} − η ∂J/∂θ_j |_{θ^{(t)}}; in stochastic gradient descent the gradient is evaluated on a single training example i, giving θ^{(t+1)} = θ^{(t)} − η ∇_θ ℓ(θ^{(t)};x_i,y_i). Adaptive variants such as AdaGrad keep a running sum of squared gradients G_{j,j}^{(t)} = ∑_{τ=1}^{t}(g_j^{(τ)})^2 and scale the learning rate per‑parameter: θ_j^{(t+1)} = θ_j^{(t)} − [η/√{G_{j,j}^{(t)}}] g_j^{(t)}. This shorthand captures the standard, stochastic, and per‑parameter forms of the gradient‑descent update.
- [Stochastic gradient descent - Wikipedia](https://en.wikipedia.org/wiki/Stochastic_gradient_descent)
  Snippet: {\displaystyle G_{j,j}=\sum _{\tau =1}^{t}g_{\tau ,j}^{2}.}This vector essentially stores a historical sum of gradient squares by dimension and is updated after every iteration. The formula for an update is now {\displaystyle w:=w-\eta \,\mathrm {diag} (G)^{-{\frac {1}{2}}}\od...
- [[PDF] CS229 Lecture Notes](https://cs229.stanford.edu/main_notes.pdf)
  Snippet: positive rather than negative sign in the update formula, since we’re maximizing, rather than minimizing, a function now.) Let’s start by working with just one training example (x, y), and take derivatives to derive the stochastic gradient ascent rule: ∂ ∂θj ℓ(θ) =  y 1 g(θTx...
- [12.3. Gradient Descent - Dive into Deep Learning](http://d2l.ai/chapter_optimization/gd.html)
  Snippet: Recall that we have the update \(x^{(k+1)} = x^{(k)} - f'(x^{(k)}) / f''(x^{(k)})\). Plugging in this update equation and taking the absolute value of both sides, we have  (12.3.12)¶\[\left|e^{(k+1)}\right| = \frac{1}{2}(e^{(k)})^2 \frac{\left|f'''(\xi^{(k)})\right|}{f''(x^{(k...

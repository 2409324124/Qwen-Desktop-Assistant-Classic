# Historical desktop assistant

原 Tkinter 桌面、全局 Alt+Shift+Q、模拟 Ctrl+C 和剪贴板入口原样保留在此，不再作为正式产品维护。代码仍引用历史 v3 Ollama 模型，其行为与最新 v5.2 实验不同。

这些文件不进入 Python 包或 npm 包，当前安装和 CI 不加载 `tkinter`、`pynput`、`pyperclip`。继续使用会面临原有焦点与全局热键冲突问题。本轮没有修补或运行桌面。

当前用户入口见 [Ollama CLI](../../docs/cli.md)，研究入口见 [研究指南](../../docs/research.md)。

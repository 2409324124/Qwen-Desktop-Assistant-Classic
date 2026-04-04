# Qwen-Desktop-Assistant-Classic

A lightweight, local AI desktop assistant that bridges **Ollama** and your Windows workflow. Featuring a nostalgic **Windows 2000 aesthetic**, global hotkey activation, and real-time streaming responses.

![Assistant Screenshot](file:///C:/Users/xu186/.gemini/antigravity/brain/69309060-dc33-4fda-8f4a-ffc5186fc4a0/media__1774780961053.png)

## ✨ Features

- **Global Hotkey** (`Alt + Shift + Q`): Instantly summon the assistant from any application.
- **Smart Clipboard Capture**: Automatically copies your selected text and processes it via AI.
- **Manual Input**: Don't want to copy? Type directly into the "Command Prompt" box and press Enter.
- **Classic UI**: Powered by `Tkinter`, styled with the iconic Windows 2000 color palette and fonts.
- **Local First**: All processing runs locally via **Ollama** (`qwen2.5:1.5b`). No data### 3. LaTeX 数据生成流水线 (`data_builder_mamut.py`)
*   **核心引擎**: 基于 [MAMUT (Math Mutator)](https://github.com/aieng-lab/math-mutator) 分支的 SymPy。
*   **功能**: 自动生成包含“等价变体”与“对抗性错误”的 SFT 训练数据。
*   **变异规则**: 使用 `FormulaGenerator` 接口，支持符号替换、结构篡改、指数/系数破坏等复杂规则。
*   **输出格式**: 遵循 LLaMA-Factory 规范的 `train_mamut.jsonl`。

#### 数据生成快速开始
1. **安装依赖** (需在 `latex` 环境下):
   ```bash
   pip install antlr4-python3-runtime==4.12
   pip install git+https://github.com/aieng-lab/sympy-random-LaTeX.git
   ```
2. **运行生成器**:
   ```bash
   python data_builder_mamut.py --src formulas.json --out train_mamut.jsonl --equiv 3 --ffactor 2
   ```

#### 4. 待办事项与后续步骤
*   **自动化粘贴**: 实现 AI 响应后自动粘贴回原窗口的功能。
*   **微调集成**: 使用生成的 `train_mamut.jsonl` 在 LLaMA-Factory 中进行规范化微调。
*   **UI 扩展**: 集成 `prompt_manager.py` 到助手主界面。
- **Ultra Responsive**: Built with a non-blocking `asyncio` backend for smooth streaming UI updates.

## 🚀 Getting Started

### Prerequisites

1. **Ollama**: Download and install [Ollama](https://ollama.com/).
2. **Model**: Pull the Qwen model:
   ```bash
   ollama pull qwen2.5:1.5b
   ```

### Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:2409324124/Qwen-Desktop-Assistant-Classic.git
   cd Qwen-Desktop-Assistant-Classic
   ```
2. Set up your environment (recommended via Conda):
   ```bash
   conda create -n qwen-assistant python=3.10
   conda activate qwen-assistant
   pip install httpx pyperclip pynput
   ```

### Usage

1. Run the main application:
   ```bash
   python main.py
   ```
2. The window will start **hidden**. 
3. Select some text in any application (Word, Browser, PDF).
4. Press **Alt + Shift + Q**. 
5. The assistant will pop up and start generating its response!

## 🛠️ Components

- `main.py`: The Tkinter UI and hotkey listener logic.
- `ollama_client.py`: High-performance async client for Ollama API.
- `summon.py`: A utility script to simulate the hotkey (useful for troubleshooting).

## 📜 License

MIT License. Feel free to modify and adapt!

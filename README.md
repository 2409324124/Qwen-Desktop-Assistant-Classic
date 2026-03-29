# Qwen-Desktop-Assistant-Classic

A lightweight, local AI desktop assistant that bridges **Ollama** and your Windows workflow. Featuring a nostalgic **Windows 2000 aesthetic**, global hotkey activation, and real-time streaming responses.

![Assistant Screenshot](file:///C:/Users/xu186/.gemini/antigravity/brain/69309060-dc33-4fda-8f4a-ffc5186fc4a0/media__1774780961053.png)

## ✨ Features

- **Global Hotkey** (`Alt + Shift + Q`): Instantly summon the assistant from any application.
- **Smart Clipboard Capture**: Automatically copies your selected text and processes it via AI.
- **Manual Input**: Don't want to copy? Type directly into the "Command Prompt" box and press Enter.
- **Classic UI**: Powered by `Tkinter`, styled with the iconic Windows 2000 color palette and fonts.
- **Local First**: All processing runs locally via **Ollama** (`qwen2.5:1.5b`). No data leaves your machine.
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
   git clone git@github.com:YourUsername/Qwen-Desktop-Assistant-Classic.git
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

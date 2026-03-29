import tkinter as tk
from tkinter import scrolledtext
import threading
import asyncio
import pyperclip
from pynput import keyboard
import time
import os
from ollama_client import OllamaClient

# Windows 2000 / Classic Style Palette
WIN_GRAY = "#d4d0c8"
WIN_WHITE = "#ffffff"
WIN_BLACK = "#000000"
WIN_BLUE = "#0a246a"
FONT_CLASSIC = ("Tahoma", 10)
FONT_BOLD = ("Tahoma", 10, "bold")

class DesktopAssistantUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Qwen Desktop Assistant - Classic v1.0")
        self.root.attributes("-topmost", True)
        self.root.geometry("420x350")
        self.root.configure(bg=WIN_GRAY)
        
        # Withdraw on start (hide from desktop)
        self.root.withdraw()
        
        # Center window
        self.root.eval('tk::PlaceWindow . center')
        
        # Main Border Frame
        main_frame = tk.Frame(root, bg=WIN_GRAY, relief="raised", borderwidth=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # simulated Menu Bar (Optional, for aesthetic)
        self.label_frame = tk.Frame(main_frame, bg=WIN_GRAY, relief="sunken", borderwidth=1)
        self.label_frame.pack(fill=tk.X, padx=5, pady=5)

        self.label = tk.Label(self.label_frame, text="Waiting for Alt+Q...", font=FONT_CLASSIC, bg=WIN_GRAY)
        self.label.pack(pady=2)
        
        # Output Area with Sunken Border
        self.text_area = scrolledtext.ScrolledText(
            main_frame, 
            wrap=tk.WORD, 
            width=45, 
            height=12, 
            font=("Fixedsys", 10) if time.localtime().tm_min % 2 == 0 else ("Courier", 10), # Fixedsys if found
            bg=WIN_WHITE,
            fg=WIN_BLACK,
            relief="sunken",
            borderwidth=2
        )
        self.text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Manual Input Field
        input_label = tk.Label(main_frame, text="Command Prompt / Manual Input:", font=("Tahoma", 8), bg=WIN_GRAY)
        input_label.pack(padx=10, anchor=tk.W)
        
        self.input_field = tk.Entry(
            main_frame,
            font=("Lucida Console", 10),
            bg=WIN_WHITE,
            fg=WIN_BLACK,
            relief="sunken",
            borderwidth=2
        )
        self.input_field.pack(padx=10, pady=(0, 10), fill=tk.X)
        self.input_field.bind("<Return>", self.on_manual_submit)
        
        # Status Bar with Sunken Border
        self.status_var = tk.StringVar(value="System Ready")
        self.status_bar = tk.Label(
            main_frame, 
            textvariable=self.status_var, 
            anchor=tk.W, 
            relief="sunken", 
            borderwidth=1, 
            bg=WIN_GRAY,
            font=("Tahoma", 8)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.client = OllamaClient()
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self._run_async_loop, daemon=True).start()
        
        # Warm up the model
        asyncio.run_coroutine_threadsafe(self.warm_up(), self.loop)
        
        # Start Hard-Trigger Signaling Polling
        self.signal_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".summon_signal")
        print(f"[{time.strftime('%H:%M:%S')}] >>> KERNEL INITIALIZED: Polling for signals at {self.signal_file}")
        self.check_summon_signal()

    async def warm_up(self):
        self.set_status("Loading kernel components...")
        try:
            await self.client.generate("Hi")
            self.set_status("System Ready")
        except Exception as e:
            self.set_status(f"Error: {e}")

    def _run_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def update_text(self, content, clear=False):
        self.root.after(0, self._update_text_safe, content, clear)

    def _update_text_safe(self, content, clear):
        if clear:
            self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, content)
        self.text_area.see(tk.END)

    def set_status(self, status):
        self.root.after(0, lambda: self.status_var.set(status))

    def check_summon_signal(self):
        """Polls every 500ms for a signal file. Only shows window, no clipboard."""
        try:
            if os.path.exists(self.signal_file):
                os.remove(self.signal_file)
                print(f"[{time.strftime('%H:%M:%S')}] >>> SIGNAL DETECTED: Summoning Interface")
                self.show_window()
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Signal error: {e}")
        self.root.after(500, self.check_summon_signal)

    def show_window(self):
        """Pure UI action: show the window and focus the input field."""
        self.root.after(0, self.root.deiconify)
        self.root.after(0, self.root.lift)
        self.root.after(0, self.root.focus_force)
        self.root.after(100, lambda: self.input_field.focus_set())

    def on_hotkey(self):
        print(f"[{time.strftime('%H:%M:%S')}] >>> HOTKEY TRIGGERED (Alt+Shift+Q)")
        
        # Step 1: Show the window immediately
        self.show_window()
        self.set_status("Reading clipboard...")
        
        # Step 2: CRITICAL - wait for Alt+Shift to be FULLY RELEASED by the OS
        # before simulating Ctrl+C, otherwise we send Ctrl+Alt+Shift+C instead.
        def _do_clipboard_query():
            time.sleep(0.3)  # wait for hotkey keys to release
            
            print(f"[{time.strftime('%H:%M:%S')}] Simulating Ctrl+C...")
            kb_controller = keyboard.Controller()
            kb_controller.press(keyboard.Key.ctrl)
            kb_controller.press('c')
            kb_controller.release('c')
            kb_controller.release(keyboard.Key.ctrl)
            
            time.sleep(0.3)  # wait for clipboard to update
            
            try:
                original_clipboard = pyperclip.paste()
                print(f"[{time.strftime('%H:%M:%S')}] Clipboard captured ({len(original_clipboard)} chars)")
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] Clipboard Error: {e}")
                original_clipboard = ""
            
            if not original_clipboard or original_clipboard.strip() == "":
                self.set_status("No selection found - type manually below")
                self.update_text("No text selected.\n\nTip: Select text before pressing Alt+Shift+Q,\nor just type your question in the box below.", clear=True)
                return

            self.update_text(f"--- [SELECTED TEXT] ---\n{original_clipboard}\n\n--- [AI RESPONSE] ---\n", clear=True)
            asyncio.run_coroutine_threadsafe(self.process_request(original_clipboard), self.loop)
        
        threading.Thread(target=_do_clipboard_query, daemon=True).start()

    def on_manual_submit(self, event=None):
        text = self.input_field.get().strip()
        if not text:
            return
        
        print(f"[{time.strftime('%H:%M:%S')}] >>> MANUAL INPUT: {text}")
        self.input_field.delete(0, tk.END)
        
        self.update_text(f"--- [MANUAL ENTRY] ---\n{text}\n\n--- [AI RESPONSE] ---\n", clear=True)
        asyncio.run_coroutine_threadsafe(self.process_request(text), self.loop)

    async def process_request(self, text):
        print(f"[{time.strftime('%H:%M:%S')}] Processing request via Ollama...")
        self.set_status("Generating output...")
        try:
            async for chunk in self.client.generate_stream(
                prompt=text, 
                system="You are a helpful desktop assistant. Keep responses concise."
            ):
                self.update_text(chunk)
            print(f"[{time.strftime('%H:%M:%S')}] Generation complete.")
            self.set_status("Generation complete")
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] FATAL ERROR: {e}")
            self.update_text(f"\nFATAL ERROR: {str(e)}")
            self.set_status("System Error")

def start_hotkey_listener(ui_app):
    def on_activate():
        ui_app.on_hotkey()

    print(f"[{time.strftime('%H:%M:%S')}] Global listener starting: <alt>+<shift>+q")
    with keyboard.GlobalHotKeys({
        '<alt>+<shift>+q': on_activate
    }) as h:
        h.join()

if __name__ == "__main__":
    root = tk.Tk()
    app = DesktopAssistantUI(root)
    threading.Thread(target=start_hotkey_listener, args=(app,), daemon=True).start()
    print("Windows 2000 UI Initialized.")
    root.mainloop()

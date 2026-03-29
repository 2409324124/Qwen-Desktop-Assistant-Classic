import os
import time

# Get the directory of the current script
DIR = os.path.dirname(os.path.abspath(__file__))
SIGNAL_FILE = os.path.join(DIR, ".summon_signal")

def send_signal():
    print(f"[{time.strftime('%H:%M:%S')}] Sending Hard-Trigger signal to Assistant...")
    try:
        with open(SIGNAL_FILE, 'w') as f:
            f.write('show')
        print("Done. The window should appear within 0.5s.")
    except Exception as e:
        print(f"Error sending signal: {e}")

if __name__ == "__main__":
    send_signal()

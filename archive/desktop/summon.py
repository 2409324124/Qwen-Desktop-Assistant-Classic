from pynput.keyboard import Key, Controller
import time

keyboard = Controller()

def summon():
    print("Simulating Alt + Shift + Q in 2 seconds...")
    time.sleep(2)
    
    # Press Alt + Shift + Q
    with keyboard.pressed(Key.alt):
        with keyboard.pressed(Key.shift):
            keyboard.press('q')
            keyboard.release('q')
            
    print("Command sent.")

if __name__ == "__main__":
    summon()

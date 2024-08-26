import keyboard
import time
import pyautogui


class SystemHotkey:
    def __init__(self):
        keyboard.add_hotkey("s", SystemHotkey.exit)

    @staticmethod
    def exit():
        # browser.quit()
        exit(1)

    @staticmethod
    def copy_all():
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'c')
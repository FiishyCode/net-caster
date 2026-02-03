import ctypes
import sys
import os
import logging

# Setup logging to file
LOG_FILE = os.path.join(os.environ.get('APPDATA', '.'), "Application", "debug.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger("Application")

from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Button as MouseButton, Controller as MouseController

# pynput controllers
pynput_keyboard = KeyboardController()
pynput_mouse = MouseController()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

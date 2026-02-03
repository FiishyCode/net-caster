import ctypes
import sys
import os
import tkinter as tk
from config import APP_NAME

class WindowManager:
    """Manages window operations - tray, minimize, taskbar - tightly coupled to app instance"""
    
    def __init__(self, app):
        self.app = app
    
    def fix_taskbar(self):
        """Make window show in taskbar despite overrideredirect"""
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        SWP_FRAMECHANGED = 0x0020
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOZORDER = 0x0004
        HWND_NOTOPMOST = -2

        self.app.root.update()

        try:
            frame = self.app.root.wm_frame()
            if frame:
                hwnd = int(frame, 16)
            else:
                hwnd = ctypes.windll.user32.GetParent(self.app.root.winfo_id())
        except:
            hwnd = ctypes.windll.user32.GetParent(self.app.root.winfo_id())

        if not hwnd:
            hwnd = self.app.root.winfo_id()

        self.app.hwnd = hwnd
        print(f"[TASKBAR] Window handle: {hwnd} (0x{hwnd:x})")

        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        print(f"[TASKBAR] Current style: 0x{style:x}")

        new_style = (style & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
        print(f"[TASKBAR] New style: 0x{new_style:x}")

        result = ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
        print(f"[TASKBAR] SetWindowLongW result: {result}")

        ctypes.windll.user32.SetWindowPos(
            hwnd, HWND_NOTOPMOST, 0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_FRAMECHANGED
        )

        self.app.root.withdraw()
        self.app.root.after(100, self._show_window)

    def _show_window(self):
        """Show window after taskbar fix"""
        self.app.root.deiconify()
        self.app.root.update()

    def minimize_window(self):
        """Minimize window using Windows API (works with overrideredirect)"""
        if self.app.hwnd:
            SW_MINIMIZE = 6
            ctypes.windll.user32.ShowWindow(self.app.hwnd, SW_MINIMIZE)
        else:
            self.app.root.withdraw()

    def minimize_to_tray(self):
        """Minimize to system tray"""
        if self.app.tray_icon:
            return
        self.app.root.withdraw()
        self._create_tray_icon()

    def _create_tray_icon(self):
        """Create system tray icon"""
        try:
            import pystray
            from PIL import Image

            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))

            icon_path = os.path.join(base_path, "icon.png")
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
            else:
                image = Image.new('RGB', (64, 64), color='#e94560')

            menu = pystray.Menu(
                pystray.MenuItem("Show", self._restore_from_tray, default=True),
                pystray.MenuItem("Exit", self._exit_from_tray)
            )

            self.app.tray_icon = pystray.Icon(APP_NAME, image, APP_NAME, menu)
            import threading
            threading.Thread(target=self.app.tray_icon.run, daemon=True).start()
        except ImportError:
            print("[TRAY] pystray not installed, using normal minimize")
            self.minimize_window()

    def _restore_from_tray(self, icon=None, item=None):
        """Restore window from tray"""
        if self.app.tray_icon:
            self.app.tray_icon.stop()
            self.app.tray_icon = None
        self.app.root.after(0, self._do_restore)

    def _do_restore(self):
        """Actually restore the window (must be called from main thread)"""
        self.app.root.deiconify()
        self.app.root.lift()
        self.app.root.focus_force()

    def _exit_from_tray(self, icon=None, item=None):
        """Exit from tray"""
        if self.app.tray_icon:
            self.app.tray_icon.stop()
            self.app.tray_icon = None
        self.app.root.after(0, self.app.on_close)

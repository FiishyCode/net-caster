import tkinter as tk
import ctypes

class OverlayManager:
    """Manages overlay window for status messages"""
    
    def __init__(self, root, show_overlay_var=None):
        self.root = root
        self.show_overlay_var = show_overlay_var
        self.overlay_window = None
        self.overlay_hide_id = None
        self.overlay_canvas = None
    
    def show_overlay(self, text, force=False):
        """Show overlay message with canvas-based text rendering"""
        if not force and self.show_overlay_var and not self.show_overlay_var.get():
            return
        
        if self.overlay_window is None or not self.overlay_window.winfo_exists():
            self.overlay_window = tk.Toplevel(self.root)
            self.overlay_window.overrideredirect(True)
            self.overlay_window.attributes('-topmost', True)
            self.overlay_window.attributes('-transparentcolor', 'black')
            self.overlay_window.attributes('-disabled', True)  # Prevent focus steal
            self.overlay_window.configure(bg='black')
            self.overlay_window.bell = lambda: None  # Disable bell on overlay
            self.overlay_window.bind('<Key>', lambda e: 'break')  # Eat all key events to prevent beep

            # Windows: Set WS_EX_NOACTIVATE to prevent focus stealing
            self.overlay_window.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.overlay_window.winfo_id())
            GWL_EXSTYLE = -20
            WS_EX_NOACTIVATE = 0x08000000
            WS_EX_APPWINDOW = 0x00040000
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = style | WS_EX_NOACTIVATE
            style = style & ~WS_EX_APPWINDOW  # Also hide from taskbar
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

            # Use canvas for text with outline
            self.overlay_canvas = tk.Canvas(self.overlay_window, bg='black', highlightthickness=0)
            self.overlay_canvas.pack()

        # Clear and redraw
        self.overlay_canvas.delete('all')
        font = ("Arial", 48, "bold")

        # Measure text first
        temp_id = self.overlay_canvas.create_text(0, 0, text=text, font=font, anchor='nw')
        bbox = self.overlay_canvas.bbox(temp_id)
        self.overlay_canvas.delete(temp_id)

        if bbox:
            w, h = bbox[2] - bbox[0] + 40, bbox[3] - bbox[1] + 40
            cx, cy = w // 2, h // 2
            self.overlay_canvas.configure(width=w, height=h)

            # Draw black outline (offset in 8 directions)
            for dx, dy in [(-2,-2), (-2,2), (2,-2), (2,2), (-2,0), (2,0), (0,-2), (0,2)]:
                self.overlay_canvas.create_text(cx+dx, cy+dy, text=text, font=font, fill='black')
            # Draw white text on top
            self.overlay_canvas.create_text(cx, cy, text=text, font=font, fill='white')

        self.overlay_window.update_idletasks()

        # Center on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        overlay_width = self.overlay_window.winfo_reqwidth()
        overlay_height = self.overlay_window.winfo_reqheight()
        x = (screen_width - overlay_width) // 2
        y = (screen_height - overlay_height) // 2
        self.overlay_window.geometry(f"+{x}+{y}")
        self.overlay_window.deiconify()

        if self.overlay_hide_id:
            self.root.after_cancel(self.overlay_hide_id)
        self.overlay_hide_id = self.root.after(3000, self.hide_overlay)
    
    def hide_overlay(self):
        """Hide overlay window"""
        if self.overlay_window and self.overlay_window.winfo_exists():
            self.overlay_window.withdraw()

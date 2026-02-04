import tkinter as tk
import ctypes

class OverlayManager:
    """Manages overlay window for status messages and persistent counters"""
    
    def __init__(self, root, show_overlay_var=None):
        self.root = root
        self.show_overlay_var = show_overlay_var
        self.overlay_window = None
        self.overlay_hide_id = None
        self.overlay_canvas = None
        
        # Persistent counter overlay
        self.counter_window = None
        self.counter_canvas = None
        self.throw_count = 0
    
    def _setup_overlay_window(self, window):
        """Configure a window to be click-through and non-focusable"""
        window.overrideredirect(True)
        window.attributes('-topmost', True)
        window.attributes('-transparentcolor', 'black')
        window.attributes('-disabled', True)
        window.configure(bg='black')
        window.bell = lambda: None
        window.bind('<Key>', lambda e: 'break')
        
        window.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        GWL_EXSTYLE = -20
        WS_EX_NOACTIVATE = 0x08000000
        WS_EX_APPWINDOW = 0x00040000
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = style | WS_EX_NOACTIVATE
        style = style & ~WS_EX_APPWINDOW
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    
    def show_overlay(self, text, force=False):
        """Show overlay message - smaller, positioned top-center"""
        if not force and self.show_overlay_var and not self.show_overlay_var.get():
            return
        
        if self.overlay_window is None or not self.overlay_window.winfo_exists():
            self.overlay_window = tk.Toplevel(self.root)
            self._setup_overlay_window(self.overlay_window)
            self.overlay_canvas = tk.Canvas(self.overlay_window, bg='black', highlightthickness=0)
            self.overlay_canvas.pack()

        # Clear and redraw
        self.overlay_canvas.delete('all')
        font = ("Segoe UI", 18, "bold")

        # Measure text first
        temp_id = self.overlay_canvas.create_text(0, 0, text=text, font=font, anchor='nw')
        bbox = self.overlay_canvas.bbox(temp_id)
        self.overlay_canvas.delete(temp_id)

        if bbox:
            w, h = bbox[2] - bbox[0] + 20, bbox[3] - bbox[1] + 16
            cx, cy = w // 2, h // 2
            self.overlay_canvas.configure(width=w, height=h)

            # Draw outline (thinner for smaller text)
            for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1), (-1,0), (1,0), (0,-1), (0,1)]:
                self.overlay_canvas.create_text(cx+dx, cy+dy, text=text, font=font, fill='#000000')
            # Draw text on top
            self.overlay_canvas.create_text(cx, cy, text=text, font=font, fill='#e4e7eb')

        self.overlay_window.update_idletasks()

        # Position top-center
        screen_width = self.root.winfo_screenwidth()
        overlay_width = self.overlay_window.winfo_reqwidth()
        x = (screen_width - overlay_width) // 2
        y = 80
        self.overlay_window.geometry(f"+{x}+{y}")
        self.overlay_window.deiconify()

        if self.overlay_hide_id:
            self.root.after_cancel(self.overlay_hide_id)
        self.overlay_hide_id = self.root.after(2000, self.hide_overlay)
    
    def hide_overlay(self):
        """Hide overlay window"""
        if self.overlay_window and self.overlay_window.winfo_exists():
            self.overlay_window.withdraw()
    
    def update_throw_counter(self, count=None, increment=False):
        """Update the persistent throw counter display"""
        if increment:
            self.throw_count += 1
        elif count is not None:
            self.throw_count = count
        
        if self.throw_count == 0:
            self.hide_counter()
            return
            
        if self.counter_window is None or not self.counter_window.winfo_exists():
            self.counter_window = tk.Toplevel(self.root)
            self._setup_overlay_window(self.counter_window)
            self.counter_canvas = tk.Canvas(self.counter_window, bg='black', highlightthickness=0)
            self.counter_canvas.pack()
        
        # Clear and redraw
        self.counter_canvas.delete('all')
        text = f"Throws: {self.throw_count}"
        font = ("Segoe UI", 14, "bold")
        
        # Measure text
        temp_id = self.counter_canvas.create_text(0, 0, text=text, font=font, anchor='nw')
        bbox = self.counter_canvas.bbox(temp_id)
        self.counter_canvas.delete(temp_id)
        
        if bbox:
            w, h = bbox[2] - bbox[0] + 16, bbox[3] - bbox[1] + 12
            cx, cy = w // 2, h // 2
            self.counter_canvas.configure(width=w, height=h)
            
            # Draw outline
            for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1), (-1,0), (1,0), (0,-1), (0,1)]:
                self.counter_canvas.create_text(cx+dx, cy+dy, text=text, font=font, fill='#000000')
            # Draw text (green tint)
            self.counter_canvas.create_text(cx, cy, text=text, font=font, fill='#10b981')
        
        self.counter_window.update_idletasks()
        
        # Position top-left corner
        x = 20
        y = 20
        self.counter_window.geometry(f"+{x}+{y}")
        self.counter_window.deiconify()
    
    def reset_throw_counter(self):
        """Reset the throw counter to 0 and hide it"""
        self.throw_count = 0
        self.hide_counter()
    
    def hide_counter(self):
        """Hide the counter window"""
        if self.counter_window and self.counter_window.winfo_exists():
            self.counter_window.withdraw()

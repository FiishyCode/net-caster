import tkinter as tk
from tkinter import ttk, colorchooser
import customtkinter as ctk

class ThemeManager:
    """Manages theme and appearance settings"""
    
    def __init__(self, app):
        self.app = app
    
    def update_theme_colors(self):
        """Update ttk styles with current colors - call after changing colors"""
        style = ttk.Style()
        bg = self.app.colors['bg']
        bg_light = self.app.colors['bg_light']
        bg_lighter = self.app.colors.get('bg_lighter', self.adjust_color(bg, 45))
        text = self.app.colors['text']
        highlight = self.app.colors['highlight']
        text_dim = self.app.colors.get('text_dim', '#888888')

        # Base styles
        style.configure('.', background=bg, foreground=text)
        style.configure('TFrame', background=bg)
        style.configure('TLabel', background=bg, foreground=text)
        style.configure('Header.TLabel', background=bg, foreground=highlight, font=('Arial', 11, 'bold'))
        style.configure('Dim.TLabel', background=bg, foreground=text_dim)
        style.configure('TCheckbutton', background=bg, foreground=text)
        style.map('TCheckbutton', background=[('active', bg)])

        # Buttons - use bg_light for normal, highlight for hover
        style.configure('TButton', background=bg_light, foreground=text, borderwidth=0, relief='flat')
        accent_darker = self.darken_color(highlight, 50)
        style.map('TButton', background=[('active', accent_darker)])

        # Entry fields - companion color
        style.configure('TEntry', fieldbackground=bg_light, foreground=text, borderwidth=0, relief='flat', padding=2)

        # Sliders - companion colors
        style.configure('TScale', background=bg_lighter, troughcolor=bg_light,
                        sliderlength=20, borderwidth=0, relief='flat',
                        lightcolor=bg_lighter, darkcolor=bg_lighter, bordercolor=bg_lighter)
        style.configure('Horizontal.TScale', background=bg_lighter,
                        lightcolor=bg_lighter, darkcolor=bg_lighter, bordercolor=bg_lighter,
                        troughcolor=bg_light)

        # Scrollbar
        style.configure('NoGrip.Vertical.TScrollbar', background=bg_light, troughcolor=bg, borderwidth=0)
        style.map('NoGrip.Vertical.TScrollbar', background=[('active', bg_lighter), ('pressed', bg_lighter)])

        # Combobox
        style.configure('TCombobox', fieldbackground=bg_light, background=bg_light, foreground=text, arrowcolor=text)
        style.map('TCombobox', fieldbackground=[('readonly', bg_light)],
                  selectbackground=[('readonly', bg_lighter)], selectforeground=[('readonly', text)])

        # Separator
        style.configure('TSeparator', background=highlight)

        # Update root
        self.app.root.configure(fg_color=bg)

        # Update modern CustomTkinter widgets
        if hasattr(self.app, 'canvas'):
            self.app.canvas.configure(fg_color=bg)
        if hasattr(self.app, 'notebook'):
            self.app.notebook.configure(
                fg_color=bg,
                segmented_button_fg_color=self.app.colors.get('bg_card', bg_light),
                segmented_button_selected_color=highlight,
                segmented_button_unselected_color=bg_light,
                segmented_button_unselected_hover_color=self.app.colors.get('hover', bg_light)
            )
        
        self.update_title_bar_colors()

    def update_title_bar_colors(self):
        """Update title bar colors to use bg_light"""
        bg_light = self.app.colors['bg_light']
        text = self.app.colors['text']
        if hasattr(self.app, 'title_bar'):
            self.app.title_bar.configure(bg=bg_light)
            for child in self.app.title_bar.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(bg=bg_light, fg=text)

    def pick_bg_color(self):
        """Open color picker for background color"""
        color = colorchooser.askcolor(color=self.app.bg_color_var.get(), title="Choose Background Color")
        if color[1]:
            self.set_bg_color(color[1])

    def set_bg_color(self, color):
        """Set the background color and derive companion colors"""
        self.app.bg_color_var.set(color)
        self.app.colors['bg'] = color
        self.app.colors['bg_light'] = self.adjust_color(color, 25)
        self.app.colors['bg_lighter'] = self.adjust_color(color, 45)
        self.app.config['bg_color'] = color
        self.app.save_settings()
        self.update_theme_colors()
        current_tab = self.app.notebook.get() if hasattr(self.app, 'notebook') else None
        self.app.build_ui()
        if current_tab and hasattr(self.app, 'notebook'):
            self.app.notebook.set(current_tab)

    def pick_fg_color(self):
        """Open color picker for foreground/text color"""
        color = colorchooser.askcolor(color=self.app.fg_color_var.get(), title="Choose Text Color")
        if color[1]:
            self.set_fg_color(color[1])

    def set_fg_color(self, color):
        """Set the foreground/text color"""
        self.app.fg_color_var.set(color)
        self.app.colors['text'] = color
        self.app.config['fg_color'] = color
        self.app.save_settings()
        self.update_theme_colors()
        current_tab = self.app.notebook.get() if hasattr(self.app, 'notebook') else None
        self.app.build_ui()
        if current_tab and hasattr(self.app, 'notebook'):
            self.app.notebook.set(current_tab)

    def pick_accent_color(self):
        """Open color picker for accent color"""
        color = colorchooser.askcolor(color=self.app.accent_color_var.get(), title="Choose Accent Color")
        if color[1]:
            self.set_accent_color(color[1])

    def set_accent_color(self, color):
        """Set the accent color and update UI"""
        self.app.accent_color_var.set(color)
        self.app.colors['highlight'] = color
        self.app.config['accent_color'] = color
        self.app.save_settings()
        self.update_theme_colors()
        current_tab = self.app.notebook.get() if hasattr(self.app, 'notebook') else None
        self.app.build_ui()
        if current_tab and hasattr(self.app, 'notebook'):
            self.app.notebook.set(current_tab)

    def pick_card_bg_color(self):
        """Open color picker for card background color"""
        color = colorchooser.askcolor(color=self.app.card_bg_color_var.get(), title="Choose Card Background Color")
        if color[1]:
            self.set_card_bg_color(color[1])

    def set_card_bg_color(self, color):
        """Set the card background color and update UI"""
        self.app.card_bg_color_var.set(color)
        self.app.colors['bg_card'] = color
        self.app.config['card_bg_color'] = color
        self.app.save_settings()
        self.update_theme_colors()
        current_tab = self.app.notebook.get() if hasattr(self.app, 'notebook') else None
        self.app.build_ui()
        if current_tab and hasattr(self.app, 'notebook'):
            self.app.notebook.set(current_tab)

    def get_luminance(self, hex_color):
        """Get perceived luminance of a color (0-255)"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return 0.299 * r + 0.587 * g + 0.114 * b

    def is_dark_color(self, hex_color):
        """Check if a color is dark (luminance < 128)"""
        return self.get_luminance(hex_color) < 128

    def adjust_color(self, hex_color, amount):
        """Adjust color - automatically lighter if dark bg, darker if light bg"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        if self.is_dark_color(hex_color):
            r = min(255, r + amount)
            g = min(255, g + amount)
            b = min(255, b + amount)
        else:
            r = max(0, r - amount)
            g = max(0, g - amount)
            b = max(0, b - amount)
        return f'#{r:02x}{g:02x}{b:02x}'

    def lighten_color(self, hex_color, amount):
        """Lighten a hex color by amount (0-255)"""
        hex_color = hex_color.lstrip('#')
        r = min(255, int(hex_color[0:2], 16) + amount)
        g = min(255, int(hex_color[2:4], 16) + amount)
        b = min(255, int(hex_color[4:6], 16) + amount)
        return f'#{r:02x}{g:02x}{b:02x}'

    def darken_color(self, hex_color, amount):
        """Darken a hex color by amount (0-255)"""
        hex_color = hex_color.lstrip('#')
        r = max(0, int(hex_color[0:2], 16) - amount)
        g = max(0, int(hex_color[2:4], 16) - amount)
        b = max(0, int(hex_color[4:6], 16) - amount)
        return f'#{r:02x}{g:02x}{b:02x}'

    def on_transparency_change(self, value):
        """Called when transparency slider changes"""
        trans = int(float(value))
        self.app.transparency_var.set(trans)
        if hasattr(self.app, 'trans_label'):
            self.app.trans_label.configure(text=f"{trans}%")
        self.app.config['transparency'] = trans
        self.app.save_settings()
        self.apply_transparency()

    def apply_transparency(self):
        """Apply window transparency"""
        trans = self.app.transparency_var.get() / 100.0
        self.app.root.attributes('-alpha', trans)

    def toggle_stay_on_top(self):
        """Toggle window always-on-top setting"""
        stay_on_top = self.app.stay_on_top_var.get()
        self.app.root.attributes('-topmost', stay_on_top)
        self.app.save_settings()

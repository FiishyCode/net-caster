import tkinter as tk
import customtkinter as ctk
from tkinter import ttk


class ToolTip:
    """Simple tooltip for tkinter/customtkinter widgets"""
    
    def __init__(self, widget, text, colors):
        self.widget = widget
        self.text = text
        self.colors = colors
        self.tooltip_window = None
        
        widget.bind('<Enter>', self.show)
        widget.bind('<Leave>', self.hide)
        widget.bind('<Button-1>', self.hide)
    
    def show(self, event=None):
        if self.tooltip_window:
            return
        
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes('-topmost', True)
        
        # Create frame with border
        frame = tk.Frame(tw, bg=self.colors['highlight'], padx=1, pady=1)
        frame.pack()
        
        inner = tk.Frame(frame, bg=self.colors['bg_card'], padx=10, pady=8)
        inner.pack()
        
        label = tk.Label(
            inner,
            text=self.text,
            justify='left',
            bg=self.colors['bg_card'],
            fg=self.colors['text'],
            font=('Segoe UI', 10),
            wraplength=280
        )
        label.pack()
    
    def hide(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class UIBuilder:
    """Manages UI building - tightly coupled to app instance"""
    
    def __init__(self, app):
        self.app = app
    
    def setup_dark_theme(self):
        """Configure ttk styles for dark mode (legacy compatibility)"""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            pass

        style.configure('.', background=self.app.colors['bg'], foreground=self.app.colors['text'])
        style.configure('TFrame', background=self.app.colors['bg'])
        style.configure('TLabel', background=self.app.colors['bg'], foreground=self.app.colors['text'])
        style.configure('TButton', background=self.app.colors['bg_light'], foreground=self.app.colors['text'],
                        borderwidth=0, relief='flat', focuscolor='')
        accent_darker = self.app.theme_manager.darken_color(self.app.colors['highlight'], 50)
        style.map('TButton', background=[('active', accent_darker)])
        style.configure('TCheckbutton', background=self.app.colors['bg'], foreground=self.app.colors['text'],
                        indicatorbackground=self.app.colors['bg_light'], indicatorforeground=self.app.colors['text'],
                        indicatorsize=16)
        style.map('TCheckbutton', background=[('active', self.app.colors['bg'])])
        style.configure('TEntry', fieldbackground=self.app.colors['bg_light'], foreground=self.app.colors['text'],
                        borderwidth=0, relief='flat', padding=2)
        bg_light = self.app.colors['bg_light']
        bg_lighter = self.app.colors.get('bg_lighter', bg_light)
        style.configure('TCombobox', fieldbackground=bg_light, background=bg_light,
                        foreground=self.app.colors['text'], arrowcolor=self.app.colors['text'])
        style.map('TCombobox', fieldbackground=[('readonly', bg_light)],
                  selectbackground=[('readonly', bg_lighter)],
                  selectforeground=[('readonly', self.app.colors['text'])])
        self.app.root.option_add('*TCombobox*Listbox.background', bg_light)
        self.app.root.option_add('*TCombobox*Listbox.foreground', self.app.colors['text'])
        self.app.root.option_add('*TCombobox*Listbox.selectBackground', bg_lighter)
        self.app.root.option_add('*TCombobox*Listbox.selectForeground', self.app.colors['text'])
        accent_dark = self.app.theme_manager.darken_color(self.app.colors['highlight'], 80)
        style.configure('TSeparator', background=accent_dark)

        try:
            style.element_create('NoGrip.Scrollbar.thumb', 'from', 'alt')
            style.layout('NoGrip.Vertical.TScrollbar', [
                ('Vertical.Scrollbar.trough', {
                    'sticky': 'ns',
                    'children': [
                        ('NoGrip.Scrollbar.thumb', {'sticky': 'nswe', 'expand': True})
                    ]
                })
            ])
        except:
            pass
        style.configure('NoGrip.Vertical.TScrollbar',
                        background=bg_lighter,
                        troughcolor=self.app.colors['bg'],
                        borderwidth=0,
                        relief='flat',
                        width=10)
        style.map('NoGrip.Vertical.TScrollbar',
                  background=[('active', bg_lighter), ('pressed', bg_lighter)])

        style.configure('TScale',
                        background=bg_lighter,
                        troughcolor=bg_light,
                        sliderlength=20,
                        borderwidth=0,
                        relief='flat',
                        gripcount=0,
                        lightcolor=bg_lighter,
                        darkcolor=bg_lighter,
                        bordercolor=bg_lighter,
                        focuscolor='',
                        highlightthickness=0)
        style.configure('Horizontal.TScale',
                        background=bg_lighter,
                        lightcolor=bg_lighter,
                        darkcolor=bg_lighter,
                        bordercolor=bg_lighter,
                        troughcolor=bg_light)

        style.configure('Header.TLabel',
                        background=self.app.colors['bg'],
                        foreground=self.app.colors['highlight'],
                        font=('Arial', 11, 'bold'))

        style.configure('Dim.TLabel',
                        background=self.app.colors['bg'],
                        foreground=self.app.colors['text_dim'])

    def build_ui(self):
        """Build the main UI"""
        for widget in self.app.root.winfo_children():
            widget.destroy()
        
        container = ctk.CTkFrame(self.app.root, fg_color=self.app.colors['bg'], corner_radius=0)
        container.pack(fill='both', expand=True, padx=0, pady=0)

        self.app.canvas = ctk.CTkFrame(
            container,
            fg_color=self.app.colors['bg'],
            corner_radius=0
        )
        self.app.canvas.pack(fill='both', expand=True, padx=15, pady=15)
        
        self.app.scrollable_frame = self.app.canvas
        frame = self.app.scrollable_frame

        self.app.notebook = ctk.CTkTabview(
            frame,
            fg_color=self.app.colors['bg'],
            segmented_button_fg_color=self.app.colors['bg_card'],
            segmented_button_selected_color=self.app.colors['highlight'],
            segmented_button_selected_hover_color=self.app.colors['highlight'],
            segmented_button_unselected_color=self.app.colors['bg_light'],
            segmented_button_unselected_hover_color=self.app.colors['hover'],
            corner_radius=10
        )
        self.app.notebook.pack(fill='both', expand=True, padx=0, pady=0)

        self.app.notebook.add("⚡ Quick Actions")
        self.app.notebook.add("🎨 Appearance")
        
        self.app.config_tab = self.app.notebook.tab("⚡ Quick Actions")
        self.app.appearance_tab = self.app.notebook.tab("🎨 Appearance")

        self.app.timing_variance_var = tk.IntVar(value=self.app.config.get("timing_variance", 0))
        self.app.drag_wait_after = 300

        self._build_config_tab()
        self._build_appearance_tab()

        resize_grip = tk.Frame(self.app.root, bg=self.app.colors['bg_light'], height=8, cursor='sb_v_double_arrow')
        resize_grip.pack(side='bottom', fill='x')

        def start_resize(event):
            self.app._resize_start_y = event.y_root
            self.app._resize_start_height = self.app.root.winfo_height()

        def do_resize(event):
            delta = event.y_root - self.app._resize_start_y
            new_height = max(400, self.app._resize_start_height + delta)
            self.app.root.geometry(f"650x{new_height}")

        resize_grip.bind('<Button-1>', start_resize)
        resize_grip.bind('<B1-Motion>', do_resize)

        # After layout, fit window height to content (title bar + tabs + content + grip)
        def fit_height():
            self.app.root.update_idletasks()
            try:
                # Quick Actions tab content required height
                tab = self.app.config_tab
                rh = tab.winfo_reqheight()
                # Add space for title bar (~30), tabs (~45), padding (30), resize grip (8)
                h = rh + 113
                w = self.app.root.winfo_width()
                self.app.root.geometry(f"{w}x{min(h, 900)}")
            except Exception:
                pass
        self.app.root.after(80, fit_height)

    def _create_action_card(self, parent, title, tooltip_text, has_action=False):
        """Create a modern card-style container for an action"""
        # Use a subtle border color that complements the theme
        border_color = '#2d3441'  # Subtle border that doesn't overpower
        card = ctk.CTkFrame(
            parent,
            fg_color=self.app.colors['bg_card'],
            corner_radius=14,
            border_width=1,
            border_color=border_color
        )
        card.pack(fill='x', padx=10, pady=8)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill='x', padx=16, pady=14)
        
        return card, content
    
    def _add_tooltip(self, widget, text):
        """Add hover tooltip to a widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_attributes('-topmost', True)
            tooltip.configure(bg=self.app.colors['bg_light'])
            label = tk.Label(tooltip, text=text, justify='left', bg=self.app.colors['bg_light'], fg=self.app.colors['text'],
                           relief='solid', borderwidth=1, padx=8, pady=6, font=('Segoe UI', 9))
            label.pack()
            tooltip.update_idletasks()

            tip_width = tooltip.winfo_width()
            screen_width = tooltip.winfo_screenwidth()
            x = event.x_root + 20
            if x + tip_width > screen_width:
                x = event.x_root - tip_width - 10
            tooltip.wm_geometry(f"+{x}+{event.y_root + 20}")
            widget._tooltip = tooltip

        def hide_tooltip(event):
            if hasattr(widget, '_tooltip') and widget._tooltip:
                widget._tooltip.destroy()
                widget._tooltip = None

        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)

    def _is_action_recorded(self, action_type):
        """Check if an action has been recorded"""
        if action_type == 'dc_both':
            return bool(self.app.config.get("dc_both_hotkey", ""))
        elif action_type == 'triggernade':
            has_hotkey = bool(self.app.config.get("triggernade_hotkey", ""))
            has_drag = self.app.config.get("trig_drag_start") and self.app.config.get("trig_drag_end")
            return has_hotkey and has_drag
        elif action_type == 'mine':
            has_hotkey = bool(self.app.config.get("mine_hotkey", ""))
            has_drag = self.app.config.get("mine_drag_start") and self.app.config.get("mine_drag_end")
            return has_hotkey and has_drag
        elif action_type == 'snaphook':
            has_hotkey = bool(self.app.config.get("snap_hotkey", ""))
            has_drag = self.app.config.get("snap_drag_start") and self.app.config.get("snap_drag_end")
            return has_hotkey and has_drag
        elif action_type == 'keycard':
            has_hotkey = bool(self.app.config.get("keycard_hotkey", ""))
            has_drag = self.app.config.get("keycard_drag_start") and self.app.config.get("keycard_drag_end")
            return has_hotkey and has_drag
        elif action_type == 'stop':
            return True
        return False

    def _save_triggernade_repeat(self):
        """Save triggernade repeat setting"""
        from config import save_config
        self.app.config["triggernade_repeat"] = self.app.triggernade_repeat_var.get()
        save_config(self.app.config)

    def _build_config_tab(self):
        """Build the Config tab with keybind controls only"""
        frame = self.app.config_tab

        actions_header = ctk.CTkLabel(
            frame, 
            text="Actions",
            font=("Segoe UI", 18, "bold"),
            text_color=self.app.colors['highlight']
        )
        actions_header.pack(pady=(15, 10), padx=20, anchor='w')

        card, dc_both_frame = self._create_action_card(frame, "Quick DC", "Toggle packet disconnect (DC Both)", has_action=False)
        
        left_side = ctk.CTkFrame(dc_both_frame, fg_color="transparent")
        left_side.pack(side='left', fill='x', expand=True)
        
        title_label = ctk.CTkLabel(
            left_side,
            text="⚡ Quick DC",
            font=("Segoe UI", 14, "bold"),
            text_color=self.app.colors['text']
        )
        title_label.pack(side='top', anchor='w')
        
        desc_label = ctk.CTkLabel(
            left_side,
            text="Disconnect both incoming and outgoing packets",
            font=("Segoe UI", 10),
            text_color=self.app.colors['text_dim']
        )
        desc_label.pack(side='top', anchor='w')
        
        controls_frame = ctk.CTkFrame(dc_both_frame, fg_color="transparent")
        controls_frame.pack(side='right', padx=(10, 0))
        
        is_recorded = self._is_action_recorded('dc_both')
        status_text = "Ready" if is_recorded else "Not Set"
        status_color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
        
        self.app.dc_both_indicator = ctk.CTkLabel(
            controls_frame,
            text=status_text,
            font=("Segoe UI", 9),
            text_color=status_color,
            width=50
        )
        self.app.dc_both_indicator.pack(side='left', padx=(0, 8))
        
        keybind_section = ctk.CTkFrame(controls_frame, fg_color="transparent")
        keybind_section.pack(side='left', padx=(0, 8))
        
        self.app.dc_both_hotkey_var = tk.StringVar(value=self.app.config.get("dc_both_hotkey", ""))
        self.app.dc_both_hotkey_entry = ctk.CTkEntry(
            keybind_section,
            textvariable=self.app.dc_both_hotkey_var,
            width=80,
            height=32,
            state="readonly",
            fg_color=self.app.colors['bg_light'],
            text_color=self.app.colors['text'],
            border_width=0
        )
        self.app.dc_both_hotkey_entry.pack(side='left', padx=(0, 5))
        
        self.app.dc_both_record_btn = ctk.CTkButton(
            keybind_section,
            text="Keybind",
            width=70,
            height=32,
            command=self.app.recording_manager.start_recording_dc_both,
            fg_color=self.app.colors['highlight'],
            hover_color=self.app.colors['hover'],
            corner_radius=8
        )
        self.app.dc_both_record_btn.pack(side='left')
        
        # Spacer to match width of Action button on other cards
        spacer = ctk.CTkFrame(controls_frame, fg_color="transparent", width=70, height=32)
        spacer.pack(side='left')
        spacer.pack_propagate(False)

        card, interact_frame = self._create_action_card(frame, "Interact", "In-game key for interacting with items (used by Keycard dupe)", has_action=False)
        left_side = ctk.CTkFrame(interact_frame, fg_color="transparent")
        left_side.pack(side='left', fill='x', expand=True)
        title_label = ctk.CTkLabel(
            left_side,
            text="Interact",
            font=("Segoe UI", 14, "bold"),
            text_color=self.app.colors['text']
        )
        title_label.pack(side='top', anchor='w')
        desc_label = ctk.CTkLabel(
            left_side,
            text="In-game key for interacting with items (used by Keycard dupe)",
            font=("Segoe UI", 10),
            text_color=self.app.colors['text_dim']
        )
        desc_label.pack(side='top', anchor='w')
        controls_frame_interact = ctk.CTkFrame(interact_frame, fg_color="transparent")
        controls_frame_interact.pack(side='right', padx=(10, 0))
        has_interact = bool(self.app.config.get("keycard_interact_key", ""))
        interact_status_text = "Ready" if has_interact else "Not Set"
        interact_status_color = self.app.colors['recorded'] if has_interact else self.app.colors['not_recorded']
        self.app.keycard_interact_indicator = ctk.CTkLabel(
            controls_frame_interact,
            text=interact_status_text,
            font=("Segoe UI", 9),
            text_color=interact_status_color,
            width=50
        )
        self.app.keycard_interact_indicator.pack(side='left', padx=(0, 8))
        keybind_section_interact = ctk.CTkFrame(controls_frame_interact, fg_color="transparent")
        keybind_section_interact.pack(side='left', padx=(0, 8))
        self.app.keycard_interact_key_var = tk.StringVar(value=self.app.config.get("keycard_interact_key", "e"))
        self.app.keycard_interact_key_entry = ctk.CTkEntry(
            keybind_section_interact,
            textvariable=self.app.keycard_interact_key_var,
            width=80,
            height=32,
            state="readonly",
            fg_color=self.app.colors['bg_light'],
            text_color=self.app.colors['text'],
            border_width=0
        )
        self.app.keycard_interact_key_entry.pack(side='left', padx=(0, 5))
        self.app.keycard_interact_record_btn = ctk.CTkButton(
            keybind_section_interact,
            text="Keybind",
            width=70,
            height=32,
            command=self.app.start_recording_keycard_interact,
            fg_color=self.app.colors['highlight'],
            hover_color=self.app.colors['hover'],
            corner_radius=8
        )
        self.app.keycard_interact_record_btn.pack(side='left')
        spacer_interact = ctk.CTkFrame(controls_frame_interact, fg_color="transparent", width=70, height=32)
        spacer_interact.pack(side='left')
        spacer_interact.pack_propagate(False)

        card, snap_frame = self._create_action_card(frame, "🪝 Snaphook", "Quick switches util with safepocket", has_action=True)
        
        left_side = ctk.CTkFrame(snap_frame, fg_color="transparent")
        left_side.pack(side='left', fill='x', expand=True)
        
        title_label = ctk.CTkLabel(
            left_side,
            text="🪝 Snaphook",
            font=("Segoe UI", 14, "bold"),
            text_color=self.app.colors['text'],
            cursor="hand2"
        )
        title_label.pack(side='top', anchor='w')
        ToolTip(title_label, "Quickly swap items with your safepocket.\nWorks on all items you can drag in inventory.", self.app.colors)
        
        desc_label = ctk.CTkLabel(
            left_side,
            text="Quick switches util with safepocket",
            font=("Segoe UI", 10),
            text_color=self.app.colors['text_dim']
        )
        desc_label.pack(side='top', anchor='w')
        
        controls_frame = ctk.CTkFrame(snap_frame, fg_color="transparent")
        controls_frame.pack(side='right', padx=(10, 0))
        
        is_recorded = self._is_action_recorded('snaphook')
        status_text = "Ready" if is_recorded else "Not Set"
        status_color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
        
        self.app.snap_indicator = ctk.CTkLabel(
            controls_frame,
            text=status_text,
            font=("Segoe UI", 9),
            text_color=status_color,
            width=50
        )
        self.app.snap_indicator.pack(side='left', padx=(0, 8))
        
        keybind_section = ctk.CTkFrame(controls_frame, fg_color="transparent")
        keybind_section.pack(side='left', padx=(0, 8))
        
        self.app.snap_hotkey_var = tk.StringVar(value=self.app.config.get("snap_hotkey", ""))
        self.app.snap_hotkey_entry = ctk.CTkEntry(
            keybind_section,
            textvariable=self.app.snap_hotkey_var,
            width=80,
            height=32,
            state="readonly",
            fg_color=self.app.colors['bg_light'],
            text_color=self.app.colors['text'],
            border_width=0
        )
        self.app.snap_hotkey_entry.pack(side='left', padx=(0, 5))
        
        self.app.snap_record_btn = ctk.CTkButton(
            keybind_section,
            text="Keybind",
            width=70,
            height=32,
            command=self.app.recording_manager.start_recording_snap,
            fg_color=self.app.colors['highlight'],
            hover_color=self.app.colors['hover'],
            corner_radius=8
        )
        self.app.snap_record_btn.pack(side='left')
        
        self.app.snap_drag_btn = ctk.CTkButton(
            controls_frame,
            text="Action",
            width=70,
            height=32,
            command=self.app.recording_manager.start_recording_snap_drag,
            fg_color=self.app.colors['highlight'],
            hover_color=self.app.colors['hover'],
            corner_radius=8
        )
        self.app.snap_drag_btn.pack(side='left')

        dupes_header = ctk.CTkLabel(
            frame, 
            text="Dupes",
            font=("Segoe UI", 18, "bold"),
            text_color=self.app.colors['highlight']
        )
        dupes_header.pack(pady=(25, 10), padx=20, anchor='w')

        card, trig_frame = self._create_action_card(frame, "Throwable", "Throw → DC → Drop → Reconnect → Grab loop", has_action=True)
        
        left_side = ctk.CTkFrame(trig_frame, fg_color="transparent")
        left_side.pack(side='left', fill='x', expand=True)
        
        title_row = ctk.CTkFrame(left_side, fg_color="transparent")
        title_row.pack(side='top', anchor='w')
        
        title_label = ctk.CTkLabel(
            title_row,
            text="🎣 Throwable",
            font=("Segoe UI", 14, "bold"),
            text_color=self.app.colors['text'],
            cursor="hand2"
        )
        title_label.pack(side='left')
        ToolTip(title_label, "Dupes the throw action of throwables.\nOnly disarmable items (like C4) can be picked back up.\nOthers are consumed but you keep the original.\nGreat for WP on Arc and similar.", self.app.colors)
        
        self.app.triggernade_repeat_var = tk.BooleanVar(value=self.app.config.get("triggernade_repeat", True))
        loop_cb = ctk.CTkCheckBox(
            title_row,
            text="Loop",
            variable=self.app.triggernade_repeat_var,
            command=self._save_triggernade_repeat,
            fg_color=self.app.colors['highlight'],
            hover_color=self.app.colors['hover'],
            text_color=self.app.colors['text_dim'],
            checkbox_width=16,
            checkbox_height=16,
            font=("Segoe UI", 10)
        )
        loop_cb.pack(side='left', padx=(10, 0))
        
        desc_label = ctk.CTkLabel(
            left_side,
            text="Throw → DC → Drop → Reconnect → Grab loop",
            font=("Segoe UI", 10),
            text_color=self.app.colors['text_dim']
        )
        desc_label.pack(side='top', anchor='w')
        
        controls_frame = ctk.CTkFrame(trig_frame, fg_color="transparent")
        controls_frame.pack(side='right', padx=(10, 0))
        
        is_recorded = self._is_action_recorded('triggernade')
        status_text = "Ready" if is_recorded else "Not Set"
        status_color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
        
        self.app.trig_indicator = ctk.CTkLabel(
            controls_frame,
            text=status_text,
            font=("Segoe UI", 9),
            text_color=status_color,
            width=50
        )
        self.app.trig_indicator.pack(side='left', padx=(0, 8))
        
        self.app.trig_keybind_indicator = self.app.trig_indicator
        
        keybind_section = ctk.CTkFrame(controls_frame, fg_color="transparent")
        keybind_section.pack(side='left', padx=(0, 8))
        
        self.app.triggernade_hotkey_var = tk.StringVar(value=self.app.config.get("triggernade_hotkey", ""))
        self.app.triggernade_hotkey_entry = ctk.CTkEntry(
            keybind_section,
            textvariable=self.app.triggernade_hotkey_var,
            width=80,
            height=32,
            state="readonly",
            fg_color=self.app.colors['bg_light'],
            text_color=self.app.colors['text'],
            border_width=0
        )
        self.app.triggernade_hotkey_entry.pack(side='left', padx=(0, 5))
        
        self.app.triggernade_record_btn = ctk.CTkButton(
            keybind_section,
            text="Keybind",
            width=70,
            height=32,
            command=self.app.recording_manager.start_recording_triggernade,
            fg_color=self.app.colors['highlight'],
            hover_color=self.app.colors['hover'],
            corner_radius=8
        )
        self.app.triggernade_record_btn.pack(side='left')
        
        self.app.trig_drag_btn = ctk.CTkButton(
            controls_frame,
            text="Action",
            width=70,
            height=32,
            command=self.app.recording_manager.start_recording_triggernade_drag,
            fg_color=self.app.colors['highlight'],
            hover_color=self.app.colors['hover'],
            corner_radius=8
        )
        self.app.trig_drag_btn.pack(side='left')

        card, mine_frame = self._create_action_card(frame, "Deployable", "Cook → Open inv + DC → Drop → Reconnect → Grab", has_action=True)
        
        left_side = ctk.CTkFrame(mine_frame, fg_color="transparent")
        left_side.pack(side='left', fill='x', expand=True)
        
        title_label = ctk.CTkLabel(
            left_side,
            text="🧰 Deployable",
            font=("Segoe UI", 14, "bold"),
            text_color=self.app.colors['text'],
            cursor="hand2"
        )
        title_label.pack(side='top', anchor='w')
        ToolTip(title_label, "Dupes deployable items like mines and barricades.\nWorks on most deployables except ziplines.\nPlace, dupe, pick up the copy.", self.app.colors)
        
        desc_label = ctk.CTkLabel(
            left_side,
            text="Cook → Open inv + DC → Drop → Reconnect → Grab",
            font=("Segoe UI", 10),
            text_color=self.app.colors['text_dim']
        )
        desc_label.pack(side='top', anchor='w')
        
        controls_frame = ctk.CTkFrame(mine_frame, fg_color="transparent")
        controls_frame.pack(side='right', padx=(10, 0))
        
        is_recorded = self._is_action_recorded('mine')
        status_text = "Ready" if is_recorded else "Not Set"
        status_color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
        
        self.app.mine_indicator = ctk.CTkLabel(
            controls_frame,
            text=status_text,
            font=("Segoe UI", 9),
            text_color=status_color,
            width=50
        )
        self.app.mine_indicator.pack(side='left', padx=(0, 8))
        
        self.app.mine_keybind_indicator = self.app.mine_indicator
        
        keybind_section = ctk.CTkFrame(controls_frame, fg_color="transparent")
        keybind_section.pack(side='left', padx=(0, 8))
        
        self.app.mine_hotkey_var = tk.StringVar(value=self.app.config.get("mine_hotkey", ""))
        self.app.mine_hotkey_entry = ctk.CTkEntry(
            keybind_section,
            textvariable=self.app.mine_hotkey_var,
            width=80,
            height=32,
            state="readonly",
            fg_color=self.app.colors['bg_light'],
            text_color=self.app.colors['text'],
            border_width=0
        )
        self.app.mine_hotkey_entry.pack(side='left', padx=(0, 5))
        
        self.app.mine_record_btn = ctk.CTkButton(
            keybind_section,
            text="Keybind",
            width=70,
            height=32,
            command=self.app.recording_manager.start_recording_mine,
            fg_color=self.app.colors['highlight'],
            hover_color=self.app.colors['hover'],
            corner_radius=8
        )
        self.app.mine_record_btn.pack(side='left')
        
        self.app.mine_drag_btn = ctk.CTkButton(
            controls_frame,
            text="Action",
            width=70,
            height=32,
            command=self.app.recording_manager.start_recording_mine_drag,
            fg_color=self.app.colors['highlight'],
            hover_color=self.app.colors['hover'],
            corner_radius=8
        )
        self.app.mine_drag_btn.pack(side='left')

        card, keycard_frame = self._create_action_card(frame, "🔑 Keycard", "Interact → 0.2s → DC → Open inv → Drag to drop → Reconnect", has_action=True)
        
        left_side = ctk.CTkFrame(keycard_frame, fg_color="transparent")
        left_side.pack(side='left', fill='x', expand=True)
        
        title_label = ctk.CTkLabel(
            left_side,
            text="🔑 Keycard",
            font=("Segoe UI", 14, "bold"),
            text_color=self.app.colors['text'],
            cursor="hand2"
        )
        title_label.pack(side='top', anchor='w')
        ToolTip(title_label, "Dupes keycards for rooms and hatches.\nWorks on all keycard types.\nThe dupe is consumed on use, but you keep the original.", self.app.colors)
        
        desc_label = ctk.CTkLabel(
            left_side,
            text="Interact → 0.2s → DC → Open inv → Drag to drop → Reconnect",
            font=("Segoe UI", 10),
            text_color=self.app.colors['text_dim']
        )
        desc_label.pack(side='top', anchor='w')
        
        controls_frame = ctk.CTkFrame(keycard_frame, fg_color="transparent")
        controls_frame.pack(side='right', padx=(10, 0))
        
        is_recorded = self._is_action_recorded('keycard')
        status_text = "Ready" if is_recorded else "Not Set"
        status_color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
        
        self.app.keycard_indicator = ctk.CTkLabel(
            controls_frame,
            text=status_text,
            font=("Segoe UI", 9),
            text_color=status_color,
            width=50
        )
        self.app.keycard_indicator.pack(side='left', padx=(0, 8))
        
        keybind_section = ctk.CTkFrame(controls_frame, fg_color="transparent")
        keybind_section.pack(side='left', padx=(0, 8))
        
        self.app.keycard_hotkey_var = tk.StringVar(value=self.app.config.get("keycard_hotkey", ""))
        self.app.keycard_hotkey_entry = ctk.CTkEntry(
            keybind_section,
            textvariable=self.app.keycard_hotkey_var,
            width=80,
            height=32,
            state="readonly",
            fg_color=self.app.colors['bg_light'],
            text_color=self.app.colors['text'],
            border_width=0
        )
        self.app.keycard_hotkey_entry.pack(side='left', padx=(0, 5))
        
        self.app.keycard_record_btn = ctk.CTkButton(
            keybind_section,
            text="Keybind",
            width=70,
            height=32,
            command=self.app.recording_manager.start_recording_keycard,
            fg_color=self.app.colors['highlight'],
            hover_color=self.app.colors['hover'],
            corner_radius=8
        )
        self.app.keycard_record_btn.pack(side='left')
        
        self.app.keycard_drag_btn = ctk.CTkButton(
            controls_frame,
            text="Action",
            width=70,
            height=32,
            command=self.app.recording_manager.start_recording_keycard_drag,
            fg_color=self.app.colors['highlight'],
            hover_color=self.app.colors['hover'],
            corner_radius=8
        )
        self.app.keycard_drag_btn.pack(side='left')

        self._init_hidden_variables(frame)

    def _init_hidden_variables(self, frame):
        """Initialize hidden variables needed by backend"""
        self.app.dc_both_btn = tk.Button(frame, text="DC BOTH", width=12, bg=self.app.colors['bg_light'], fg=self.app.colors['text'])
        self.app.dc_both_btn.pack_forget()
        
        self.app.dc_outbound_hotkey_var = tk.StringVar(value=self.app.config.get("dc_outbound_hotkey", ""))
        self.app.dc_outbound_hotkey_entry = tk.Entry(frame)
        self.app.dc_outbound_hotkey_entry.pack_forget()
        self.app.dc_outbound_btn = tk.Button(frame, text="DC OUTBOUND", width=12, bg=self.app.colors['bg_light'], fg=self.app.colors['text'])
        self.app.dc_outbound_btn.pack_forget()
        self.app.dc_outbound_record_btn = ttk.Button(frame, text="Set", width=4)
        self.app.dc_outbound_record_btn.pack_forget()
        
        self.app.dc_inbound_hotkey_var = tk.StringVar(value=self.app.config.get("dc_inbound_hotkey", ""))
        self.app.dc_inbound_hotkey_entry = tk.Entry(frame)
        self.app.dc_inbound_hotkey_entry.pack_forget()
        self.app.dc_inbound_btn = tk.Button(frame, text="DC INBOUND", width=12, bg=self.app.colors['bg_light'], fg=self.app.colors['text'])
        self.app.dc_inbound_btn.pack_forget()
        self.app.dc_inbound_record_btn = ttk.Button(frame, text="Set", width=4)
        self.app.dc_inbound_record_btn.pack_forget()
        
        self.app.tamper_hotkey_var = tk.StringVar(value=self.app.config.get("tamper_hotkey", ""))
        self.app.tamper_hotkey_entry = tk.Entry(frame)
        self.app.tamper_hotkey_entry.pack_forget()
        self.app.tamper_btn = tk.Button(frame, text="TAMPER", width=12, bg=self.app.colors['bg_light'], fg=self.app.colors['text'])
        self.app.tamper_btn.pack_forget()
        self.app.tamper_record_btn = ttk.Button(frame, text="Set", width=4)
        self.app.tamper_record_btn.pack_forget()

        self.app.trig_drag_btn = ttk.Button(frame, text="Record", width=12)
        self.app.trig_drag_btn.pack_forget()
        self.app.trig_drag_var = tk.StringVar()
        trig_slot = self.app.config.get("trig_slot_pos", None)
        trig_drop = self.app.config.get("trig_drop_pos", None)
        self.app.trig_slot_pos = tuple(trig_slot) if trig_slot else None
        self.app.trig_drop_pos = tuple(trig_drop) if trig_drop else None
        trig_drag_s = self.app.config.get("trig_drag_start", None)
        trig_drag_e = self.app.config.get("trig_drag_end", None)
        self.app.trig_drag_start = tuple(trig_drag_s) if trig_drag_s else None
        self.app.trig_drag_end = tuple(trig_drag_e) if trig_drag_e else None
        self.app.trig_m1_hold_var = tk.IntVar(value=int(self.app.config.get("trig_m1_hold", 65)))
        self.app.trig_m2_hold_var = tk.IntVar(value=int(self.app.config.get("trig_m2_hold", 51)))
        self.app.trig_drag_speed_var = tk.IntVar(value=int(self.app.config.get("trig_drag_speed", 8)))
        self.app.trig_dc_delay_var = tk.IntVar(value=int(self.app.config.get("trig_dc_delay", 10)))
        self.app.trig_dc_throws_var = tk.IntVar(value=int(self.app.config.get("trig_dc_throws", 10)))
        self.app.trig_throw_delay_var = tk.IntVar(value=int(self.app.config.get("trig_throw_delay", 100)))
        self.app.trig_reconnect_after_var = tk.IntVar(value=int(self.app.config.get("trig_reconnect_after", 1)))
        self.app.wait_before_espam_var = tk.IntVar(value=int(self.app.config.get("wait_before_espam", 0)))
        self.app.espam_duration_var = tk.IntVar(value=int(self.app.config.get("espam_duration", 250)))
        self.app.trig_m1_before_interweave_var = tk.IntVar(value=int(self.app.config.get("trig_m1_before_interweave", 1)))
        self.app.wait_before_cycle_var = tk.IntVar(value=int(self.app.config.get("wait_before_cycle", 100)))
        self.app.wolfpack_m1_hold_var = tk.IntVar(value=int(self.app.config.get("wolfpack_m1_hold", 20)))
        self.app.wolfpack_m1_gap_var = tk.IntVar(value=int(self.app.config.get("wolfpack_m1_gap", 20)))
        self.app.wolfpack_dc_hold_var = tk.IntVar(value=int(self.app.config.get("wolfpack_dc_hold", 20)))
        self.app.wolfpack_dc_gap_var = tk.IntVar(value=int(self.app.config.get("wolfpack_dc_gap", 600)))
        self.app.triggernade_q_spam_var = tk.BooleanVar(value=self.app.config.get("triggernade_q_spam", False))
        self.app.triggernade_status_var = tk.StringVar(value="Ready")
        self.app.triggernade_status_label = ttk.Label(frame, textvariable=self.app.triggernade_status_var, style='Dim.TLabel')
        self.app.triggernade_status_label.pack_forget()

        self.app.mine_drag_btn = ttk.Button(frame, text="Record Path", width=12)
        self.app.mine_drag_btn.pack_forget()
        self.app.mine_repeat_var = tk.BooleanVar(value=self.app.config.get("mine_repeat", False))
        self.app.mine_drag_var = tk.StringVar()
        mine_slot = self.app.config.get("mine_slot_pos", [3032, 1236])
        mine_drop = self.app.config.get("mine_drop_pos", [3171, 1593])
        mine_drag_s = self.app.config.get("mine_drag_start", [3032, 1236])
        mine_drag_e = self.app.config.get("mine_drag_end", [3171, 1593])
        self.app.mine_slot_pos = tuple(mine_slot) if mine_slot else None
        self.app.mine_drop_pos = tuple(mine_drop) if mine_drop else None
        self.app.mine_drag_start = tuple(mine_drag_s) if mine_drag_s else None
        self.app.mine_drag_end = tuple(mine_drag_e) if mine_drag_e else None
        self.app.mine_cook_var = tk.IntVar(value=int(self.app.config.get("mine_cook", 236)))
        self.app.mine_dc_delay_var = tk.IntVar(value=int(self.app.config.get("mine_dc_delay", 99)))
        self.app.mine_drag_speed_var = tk.IntVar(value=int(self.app.config.get("mine_drag_speed", 8)))
        self.app.mine_pre_close_var = tk.IntVar(value=int(self.app.config.get("mine_pre_close", 100)))
        self.app.mine_tab_hold_var = tk.IntVar(value=int(self.app.config.get("mine_tab_hold", 80)))
        self.app.mine_close_reconnect_var = tk.IntVar(value=int(self.app.config.get("mine_close_reconnect", 409)))
        self.app.mine_click_delay_var = tk.IntVar(value=int(self.app.config.get("mine_click_delay", 7)))
        self.app.mine_pickup_hold_var = tk.IntVar(value=int(self.app.config.get("mine_pickup_hold", 1336)))
        self.app.mine_e_delay_var = tk.IntVar(value=int(self.app.config.get("mine_e_delay", 868)))
        self.app.mine_loop_delay_var = tk.IntVar(value=int(self.app.config.get("mine_loop_delay", 550)))
        self.app.mine_reselect_var = tk.BooleanVar(value=self.app.config.get("mine_reselect", True))
        default_q_recording = [
            [1920, 1080], [1920, 1064], [1920, 1046], [1920, 1020], [1920, 982],
            [1920, 949], [1922, 914], [1925, 884], [1928, 852], [1922, 1058],
            [1926, 1035], [1927, 1012], [1930, 993], [1922, 1065], [1924, 1049]
        ]
        self.app.mine_q_mode_var = tk.StringVar(value=self.app.config.get("mine_q_mode", "radial"))
        self.app.mine_q_direction_var = tk.StringVar(value=self.app.config.get("mine_q_direction", "S"))
        self.app.mine_nudge_var = tk.BooleanVar(value=self.app.config.get("mine_nudge", True))
        self.app.mine_nudge_px_var = tk.IntVar(value=self.app.config.get("mine_nudge_px", 50))
        self.app.mine_status_var = tk.StringVar(value="Ready")
        self.app.mine_status_label = ttk.Label(frame, textvariable=self.app.mine_status_var, style='Dim.TLabel')
        self.app.mine_status_label.pack_forget()

        snap_drag_s = self.app.config.get("snap_drag_start", None)
        snap_drag_e = self.app.config.get("snap_drag_end", None)
        self.app.snap_drag_start = tuple(snap_drag_s) if snap_drag_s else None
        self.app.snap_drag_end = tuple(snap_drag_e) if snap_drag_e else None
        self.app._snap_drag_started = False

        keycard_drag_s = self.app.config.get("keycard_drag_start", None)
        keycard_drag_e = self.app.config.get("keycard_drag_end", None)
        self.app.keycard_drag_start = tuple(keycard_drag_s) if keycard_drag_s else None
        self.app.keycard_drag_end = tuple(keycard_drag_e) if keycard_drag_e else None
        self.app._keycard_drag_started = False

    def _build_appearance_tab(self):
        """Build the Appearance tab with visual settings"""
        frame = self.app.appearance_tab

        window_header = ctk.CTkLabel(
            frame, 
            text="Window Options",
            font=("Segoe UI", 18, "bold"),
            text_color=self.app.colors['highlight']
        )
        window_header.pack(pady=(15, 10), padx=20, anchor='w')

        window_card = ctk.CTkFrame(
            frame,
            fg_color=self.app.colors['bg_card'],
            corner_radius=14,
            border_width=1,
            border_color='#2d3441'
        )
        window_card.pack(fill='x', padx=10, pady=8)
        
        window_content = ctk.CTkFrame(window_card, fg_color="transparent")
        window_content.pack(fill='x', padx=16, pady=14)

        self.app.stay_on_top_var = tk.BooleanVar(value=self.app.config.get("stay_on_top", False))
        stay_on_top_cb = ctk.CTkCheckBox(
            window_content,
            text="Stay on top",
            variable=self.app.stay_on_top_var,
            command=self.app.toggle_stay_on_top,
            fg_color=self.app.colors['highlight'],
            hover_color=self.app.colors['hover'],
            text_color=self.app.colors['text']
        )
        stay_on_top_cb.pack(anchor='w', pady=5)

        self.app.show_overlay_var = tk.BooleanVar(value=self.app.config.get("show_overlay", True))
        if self.app.overlay is None:
            from overlay import OverlayManager
            self.app.overlay = OverlayManager(self.app.root, self.app.show_overlay_var)
        show_overlay_cb = ctk.CTkCheckBox(
            window_content,
            text="Show on-screen text",
            variable=self.app.show_overlay_var,
            command=self.app.save_settings,
            fg_color=self.app.colors['highlight'],
            hover_color=self.app.colors['hover'],
            text_color=self.app.colors['text']
        )
        show_overlay_cb.pack(anchor='w', pady=5)

        appearance_header = ctk.CTkLabel(
            frame, 
            text="Appearance",
            font=("Segoe UI", 18, "bold"),
            text_color=self.app.colors['highlight']
        )
        appearance_header.pack(pady=(25, 10), padx=20, anchor='w')
        
        appearance_card = ctk.CTkFrame(
            frame,
            fg_color=self.app.colors['bg_card'],
            corner_radius=14,
            border_width=1,
            border_color='#2d3441'
        )
        appearance_card.pack(fill='x', padx=10, pady=8)
        
        appearance_content = ctk.CTkFrame(appearance_card, fg_color="transparent")
        appearance_content.pack(fill='x', padx=16, pady=14)

        colors_row = ctk.CTkFrame(appearance_content, fg_color="transparent")
        colors_row.pack(fill='x', pady=10)

        ctk.CTkLabel(colors_row, text="BG:", font=("Segoe UI", 11), text_color=self.app.colors['text'], width=30).pack(side='left', padx=(0,5))
        self.app.bg_color_var = tk.StringVar(value=self.app.config.get("bg_color", "#1e1e1e"))
        self.app.bg_color_btn = ctk.CTkButton(
            colors_row, 
            text="", 
            width=35,
            height=28,
            fg_color=self.app.bg_color_var.get(),
            hover_color=self.app.bg_color_var.get(),
            border_width=2,
            border_color=self.app.colors['accent'],
            corner_radius=6,
            command=self.app._pick_bg_color
        )
        self.app.bg_color_btn.pack(side='left', padx=3)

        ctk.CTkLabel(colors_row, text="Text:", font=("Segoe UI", 11), text_color=self.app.colors['text'], width=35).pack(side='left', padx=(10,5))
        self.app.fg_color_var = tk.StringVar(value=self.app.config.get("fg_color", "#e0e0e0"))
        self.app.fg_color_btn = ctk.CTkButton(
            colors_row,
            text="",
            width=35,
            height=28,
            fg_color=self.app.fg_color_var.get(),
            hover_color=self.app.fg_color_var.get(),
            border_width=2,
            border_color=self.app.colors['accent'],
            corner_radius=6,
            command=self.app._pick_fg_color
        )
        self.app.fg_color_btn.pack(side='left', padx=3)

        ctk.CTkLabel(colors_row, text="Accent:", font=("Segoe UI", 11), text_color=self.app.colors['text'], width=45).pack(side='left', padx=(10,5))
        self.app.accent_color_var = tk.StringVar(value=self.app.config.get("accent_color", "#e94560"))
        self.app.accent_color_btn = ctk.CTkButton(
            colors_row,
            text="",
            width=35,
            height=28,
            fg_color=self.app.accent_color_var.get(),
            hover_color=self.app.accent_color_var.get(),
            border_width=2,
            border_color=self.app.colors['accent'],
            corner_radius=6,
            command=self.app._pick_accent_color
        )
        self.app.accent_color_btn.pack(side='left', padx=3)

        ctk.CTkLabel(colors_row, text="Card:", font=("Segoe UI", 11), text_color=self.app.colors['text'], width=35).pack(side='left', padx=(10,5))
        self.app.card_bg_color_var = tk.StringVar(value=self.app.config.get("card_bg_color", self.app.colors['bg_card']))
        self.app.card_bg_color_btn = ctk.CTkButton(
            colors_row,
            text="",
            width=35,
            height=28,
            fg_color=self.app.card_bg_color_var.get(),
            hover_color=self.app.card_bg_color_var.get(),
            border_width=2,
            border_color=self.app.colors['accent'],
            corner_radius=6,
            command=self.app._pick_card_bg_color
        )
        self.app.card_bg_color_btn.pack(side='left', padx=3)

        trans_row = ctk.CTkFrame(appearance_content, fg_color="transparent")
        trans_row.pack(fill='x', pady=10)
        ctk.CTkLabel(trans_row, text="Transparency:", font=("Segoe UI", 12), text_color=self.app.colors['text'], width=120, anchor='w').pack(side='left')
        loaded_trans = self.app.config.get("transparency", 100)
        self.app.transparency_var = tk.IntVar(value=loaded_trans)
        trans_slider = ctk.CTkSlider(
            trans_row,
            from_=50,
            to=100,
            variable=self.app.transparency_var,
            width=150,
            command=self.app._on_transparency_change,
            fg_color=self.app.colors['bg_light'],
            progress_color=self.app.colors['highlight'],
            button_color=self.app.colors['highlight'],
            button_hover_color=self.app.colors['hover']
        )
        trans_slider.pack(side='left', padx=10)
        self.app.trans_label = ctk.CTkLabel(trans_row, text=f"{loaded_trans}%", font=("Segoe UI", 11), text_color=self.app.colors['text'], width=40)
        self.app.trans_label.pack(side='left')

        self.app._apply_transparency()

        settings_row = ctk.CTkFrame(appearance_content, fg_color="transparent")
        settings_row.pack(fill='x', pady=(15, 5))
        ctk.CTkButton(
            settings_row,
            text="Export Settings",
            width=110,
            height=32,
            fg_color=self.app.colors['bg_light'],
            hover_color=self.app.colors['hover'],
            text_color=self.app.colors['text'],
            corner_radius=8,
            command=self.app.export_all_settings
        ).pack(side='left', padx=3)
        ctk.CTkButton(
            settings_row,
            text="Import Settings",
            width=110,
            height=32,
            fg_color=self.app.colors['bg_light'],
            hover_color=self.app.colors['hover'],
            text_color=self.app.colors['text'],
            corner_radius=8,
            command=self.app.import_all_settings
        ).pack(side='left', padx=3)
        ctk.CTkButton(
            settings_row,
            text="Reset Preferences",
            width=120,
            height=32,
            fg_color=self.app.colors['bg_light'],
            hover_color=self.app.colors['hover'],
            text_color=self.app.colors['text'],
            corner_radius=8,
            command=self.app.reset_preferences_only
        ).pack(side='left', padx=3)
        ctk.CTkButton(
            settings_row,
            text="Reset All Settings",
            width=120,
            height=32,
            fg_color=self.app.colors['accent'],
            hover_color="#c73d52",
            text_color=self.app.colors['text'],
            corner_radius=8,
            command=self.app.reset_all_settings
        ).pack(side='left', padx=3)

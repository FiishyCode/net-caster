import keyboard
import ctypes
import sys
import threading
import json
import os
import time
import random
import string
import tkinter as tk
from tkinter import ttk, filedialog
import customtkinter as ctk

# Import from new modules
from config import (
    BUILD_ID, OBFUSCATION_ENABLED, VERSION, APP_NAME, 
    rename_self_and_restart, load_config, save_config, CONFIG_FILE
)
from packet_control import (
    start_packet_drop, stop_packet_drop, is_dropping,
    start_packet_tamper, stop_packet_tamper, is_tampering
)
from utils import (
    log, pynput_keyboard, pynput_mouse, is_admin
)
from overlay import OverlayManager
from settings_manager import SettingsManager
from macro_utils import MacroUtils
from theme import ThemeManager
from hotkeys import HotkeyManager
from macros import MacroExecutor
from recording import RecordingManager
from ui_builder import UIBuilder
from window_manager import WindowManager
from custom_macro_manager import CustomMacroManager
from packet_control_manager import PacketControlManager
from indicator_manager import IndicatorManager
from direction_picker_manager import DirectionPickerManager
from hotkey_recording_handler import HotkeyRecordingHandler
from settings_export_manager import SettingsExportManager
from reset_manager import ResetManager
from pynput.keyboard import Key
from pynput.mouse import Button as MouseButton
from auth import run_login

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Net Caster v1.0")
        self.root.geometry("750x750")
        self.root.resizable(True, True)  # Allow resize
        
        # Modern dark theme with refined colors
        self.colors = {
            'bg': '#0f1419',           # Deep dark background
            'bg_light': '#1a1f2e',     # Slightly lighter for inputs
            'bg_card': '#1a1f2e',      # Card background with subtle contrast
            'accent': '#252a3a',       # Subtle accent for borders
            'text': '#e4e7eb',         # Clean light text
            'text_dim': '#9ca3af',     # Muted grey for secondary text
            'highlight': '#8080c0',    # Purple/lavender accent
            'success': '#10b981',      # Refined green
            'warning': '#f59e0b',      # Refined amber
            'recorded': '#10b981',     # Green for recorded
            'not_recorded': '#f59e0b', # Amber for not recorded
            'hover': '#2d3441'         # Subtle hover effect
        }

        # Configure window colors
        self.root.configure(fg_color=self.colors['bg'])
        
        # Disable tkinter bell sound (prevents beeps during macros)
        self.root.bell = lambda: None
        self.root.bind('<Key>', lambda e: None)  # Suppress key event beeps

        # Set AppUserModelID for Windows taskbar icon
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Application.Main.1')
        except:
            pass

        # Set window icon - fish icon 🐟
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            # Look for fish icon files
            icon_dir = os.path.join(os.path.dirname(base_path), "assets", "icons")
            ico_path = os.path.join(icon_dir, "icon.ico")
            png_path = os.path.join(icon_dir, "icon.png")
            
            # For CustomTkinter windows, use iconbitmap for .ico files
            if os.path.exists(ico_path):
                self.root.iconbitmap(ico_path)
                print(f"[ICON] Fish icon loaded from: {ico_path}")
            elif os.path.exists(png_path):
                # Fallback to PNG
                self.icon_image = tk.PhotoImage(file=png_path)
                self.root.iconphoto(True, self.icon_image)
                print(f"[ICON] Fish icon loaded from: {png_path}")
            else:
                print(f"[ICON] No icon files found in {icon_dir}")
        except Exception as e:
            print(f"[ICON] Could not load fish icon: {e}")
            import traceback
            traceback.print_exc()

        self.config = load_config()

        # Initialize theme_manager early (needed for color derivation)
        self.theme_manager = ThemeManager(self)

        # Load saved colors from config and derive companion colors
        if "bg_color" in self.config:
            bg = self.config['bg_color']
            self.colors['bg'] = bg
            # Derive companion colors based on luminance
            self.colors['bg_light'] = self.theme_manager.adjust_color(bg, 25)
            self.colors['bg_lighter'] = self.theme_manager.adjust_color(bg, 45)
            self.root.configure(bg=bg)
        if "fg_color" in self.config:
            self.colors['text'] = self.config['fg_color']
        if "accent_color" in self.config:
            self.colors['highlight'] = self.config['accent_color']

        # Restore window position if saved and reasonable
        saved_x = self.config.get("window_x")
        saved_y = self.config.get("window_y")
        if saved_x is not None and saved_y is not None:
            # Check if position is on screen (reasonable)
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
            if 0 <= saved_x < screen_w - 100 and 0 <= saved_y < screen_h - 100:
                self.root.geometry(f"+{saved_x}+{saved_y}")

        # State
        self.triggernade_hotkey_registered = None
        self.disconnected = False
        self.triggernade_running = False
        self.triggernade_stop = False
        self.triggernade_m1_count = 13  # ~13 M1s before reconnect
        self.triggernade_dc_delay = 0.050  # Delay before disconnect (seconds)
        self.triggernade_run_count = 0  # Track runs for randomizing delay
        self.mine_running = False
        self.mine_stop = False
        self.mine_hotkey_registered = None
        self.escape_hotkey_registered = None
        # Stop All state
        self.recording_stop = False
        # Quick disconnect state
        self.test_disconnected = False
        self.tampering = False
        self.dc_both_hotkey_registered = None
        self.dc_outbound_hotkey_registered = None
        self.dc_inbound_hotkey_registered = None
        self.tamper_hotkey_registered = None
        self.recording_dc_both = False
        self.recording_dc_outbound = False
        self.recording_dc_inbound = False
        self.recording_tamper = False
        self.recording_triggernade = False
        self.recording_mine = False
        self.recording_snap = False
        self.recording_keycard = False
        self.recording_drag = False
        self._recording_previous_value = None  # Store previous value for ESC cancel
        self._drag_recording_cancelled = False  # For ESC cancel of drag recordings
        self._mine_recording_cancelled = False  # For ESC cancel of mine recordings
        self.drag_mouse_listener = None
        self.listening = True  # Always listening

        # Locks to prevent race conditions in hotkey handlers
        self._mine_lock = threading.Lock()
        self._triggernade_lock = threading.Lock()

        # Overlay (will be initialized after show_overlay_var is created)
        self.overlay = None

        # Window handle for minimize (set in _fix_taskbar)
        self.hwnd = None

        # Tray icon
        self.tray_icon = None

        # Initialize managers (theme_manager already initialized above)
        self.settings_manager = SettingsManager(self)
        self.macro_utils = MacroUtils(self)
        self.hotkey_manager = HotkeyManager(self)
        self.macro_executor = MacroExecutor(self)
        self.recording_manager = RecordingManager(self)
        self.ui_builder = UIBuilder(self)
        self.window_manager = WindowManager(self)
        self.custom_macro_manager = CustomMacroManager(self)
        self.packet_control_manager = PacketControlManager(self)
        self.indicator_manager = IndicatorManager(self)
        self.direction_picker_manager = DirectionPickerManager(self)
        self.hotkey_recording_handler = HotkeyRecordingHandler(self)
        self.settings_export_manager = SettingsExportManager(self)
        self.reset_manager = ResetManager(self)
        
        self.ui_builder.setup_dark_theme()
        self.ui_builder.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _create_action_card(self, parent, title, tooltip_text, has_action=False):
        """Delegate to UI builder"""
        return self.ui_builder._create_action_card(parent, title, tooltip_text, has_action)
    
    def _add_tooltip(self, widget, text):
        """Delegate to UI builder"""
        return self.ui_builder._add_tooltip(widget, text)

    def vary(self, ms):
        return self.macro_utils.vary(ms)

    def vsleep(self, ms):
        return self.macro_utils.vsleep(ms)

    def vary_balanced(self, ms, count):
        return self.macro_utils.vary_balanced(ms, count)

    def curved_drag(self, start, end, steps=20, step_delay=5):
        return self.macro_utils.curved_drag(start, end, steps, step_delay)

    def _fix_taskbar(self):
        """Delegate to window manager"""
        return self.window_manager.fix_taskbar()

    def _show_window(self):
        """Delegate to window manager"""
        return self.window_manager._show_window()

    def minimize_window(self):
        """Delegate to window manager"""
        return self.window_manager.minimize_window()

    def minimize_to_tray(self):
        """Delegate to window manager"""
        return self.window_manager.minimize_to_tray()

    def _create_tray_icon(self):
        """Delegate to window manager"""
        return self.window_manager._create_tray_icon()

    def _restore_from_tray(self, icon=None, item=None):
        """Delegate to window manager"""
        return self.window_manager._restore_from_tray(icon, item)

    def _do_restore(self):
        """Delegate to window manager"""
        return self.window_manager._do_restore()

    def _exit_from_tray(self, icon=None, item=None):
        """Delegate to window manager"""
        return self.window_manager._exit_from_tray(icon, item)

    def _is_action_recorded(self, action_type):
        """Delegate to UI builder"""
        return self.ui_builder._is_action_recorded(action_type)
    
    def _update_record_button_color(self, button, action_type):
        """Delegate to indicator manager"""
        return self.indicator_manager.update_record_button_color(button, action_type)
    
    def _update_all_indicators(self):
        """Delegate to indicator manager"""
        return self.indicator_manager.update_all_indicators()

    def setup_dark_theme(self):
        """Delegate to UI builder"""
        return self.ui_builder.setup_dark_theme()

    def build_ui(self):
        """Delegate to UI builder"""
        return self.ui_builder.build_ui()

    def _build_config_tab(self):
        """Build the Config tab with keybind controls only"""
        frame = self.config_tab

        # Actions section header
        actions_header = ctk.CTkLabel(
            frame, 
            text="Actions",
            font=("Segoe UI", 18, "bold"),
            text_color=self.colors['highlight']
        )
        actions_header.pack(pady=(15, 10), padx=20, anchor='w')

        # Quick DC Card
        card, dc_both_frame = self._create_action_card(frame, "Quick DC", "Toggle packet disconnect (DC Both)", has_action=False)
        
        # Left side - indicator and title
        left_side = ctk.CTkFrame(dc_both_frame, fg_color="transparent")
        left_side.pack(side='left', fill='x', expand=True)
        
        # Single indicator
        is_recorded = self._is_action_recorded('dc_both')
        indicator_color = self.colors['recorded'] if is_recorded else self.colors['not_recorded']
        
        indicator_frame = ctk.CTkFrame(left_side, fg_color="transparent", width=14, height=14)
        indicator_frame.pack(side='left', padx=(0, 10))
        indicator_frame.pack_propagate(False)
        
        self.dc_both_indicator = ctk.CTkLabel(
            indicator_frame,
            text="●",
            font=("Segoe UI", 16),
            text_color=indicator_color,
            width=14,
            height=14
        )
        self.dc_both_indicator.pack(expand=True)
        
        # Title section
        title_frame = ctk.CTkFrame(left_side, fg_color="transparent")
        title_frame.pack(side='left', fill='x', expand=True)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="⚡ Quick DC",
            font=("Segoe UI", 14, "bold"),
            text_color=self.colors['text']
        )
        title_label.pack(side='top', anchor='w')
        
        desc_label = ctk.CTkLabel(
            title_frame,
            text="Disconnect both incoming and outgoing packets",
            font=("Segoe UI", 10),
            text_color=self.colors['text_dim']
        )
        desc_label.pack(side='top', anchor='w')
        
        # Right side controls
        controls_frame = ctk.CTkFrame(dc_both_frame, fg_color="transparent")
        controls_frame.pack(side='right', padx=(10, 0))
        
        self.dc_both_hotkey_var = tk.StringVar(value=self.config.get("dc_both_hotkey", ""))
        self.dc_both_hotkey_entry = ctk.CTkEntry(
            controls_frame,
            textvariable=self.dc_both_hotkey_var,
            width=80,
            height=32,
            state="readonly",
            fg_color=self.colors['bg_light'],
            text_color=self.colors['text'],
            border_width=0
        )
        self.dc_both_hotkey_entry.pack(side='left', padx=(0, 5))
        
        self.dc_both_record_btn = ctk.CTkButton(
            controls_frame,
            text="Keybind",
            width=70,
            height=32,
            command=self.start_recording_dc_both,
            fg_color=self.colors['highlight'],
            hover_color=self.colors['hover'],
            corner_radius=8
        )
        self.dc_both_record_btn.pack(side='left')

        # Snaphook Card
        card, snap_frame = self._create_action_card(frame, "🪝 Snaphook", "Quick switches util with safepocket", has_action=True)
        
        # Left side - indicator and title
        left_side = ctk.CTkFrame(snap_frame, fg_color="transparent")
        left_side.pack(side='left', fill='x', expand=True)
        
        # Single indicator (shows if BOTH keybind and action are recorded)
        is_recorded = self._is_action_recorded('snaphook')
        indicator_color = self.colors['recorded'] if is_recorded else self.colors['not_recorded']
        
        indicator_frame = ctk.CTkFrame(left_side, fg_color="transparent", width=14, height=14)
        indicator_frame.pack(side='left', padx=(0, 10))
        indicator_frame.pack_propagate(False)
        
        self.snap_indicator = ctk.CTkLabel(
            indicator_frame,
            text="●",
            font=("Segoe UI", 16),
            text_color=indicator_color,
            width=14,
            height=14
        )
        self.snap_indicator.pack(expand=True)
        
        title_frame = ctk.CTkFrame(left_side, fg_color="transparent")
        title_frame.pack(side='left', fill='x', expand=True)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🪝 Snaphook",
            font=("Segoe UI", 14, "bold"),
            text_color=self.colors['text'],
            anchor='w'
        )
        title_label.pack(side='top', anchor='w')
        
        desc_label = ctk.CTkLabel(
            title_frame,
            text="Quick switches util with safepocket",
            font=("Segoe UI", 10),
            text_color=self.colors['text_dim']
        )
        desc_label.pack(side='top', anchor='w')
        
        # Right side controls
        controls_frame = ctk.CTkFrame(snap_frame, fg_color="transparent")
        controls_frame.pack(side='right', padx=(10, 0))
        
        # Keybind controls
        keybind_section = ctk.CTkFrame(controls_frame, fg_color="transparent")
        keybind_section.pack(side='left', padx=(0, 8))
        
        self.snap_hotkey_var = tk.StringVar(value=self.config.get("snap_hotkey", ""))
        self.snap_hotkey_entry = ctk.CTkEntry(
            keybind_section,
            textvariable=self.snap_hotkey_var,
            width=80,
            height=32,
            state="readonly",
            fg_color=self.colors['bg_light'],
            text_color=self.colors['text'],
            border_width=0
        )
        self.snap_hotkey_entry.pack(side='left', padx=(0, 5))
        
        self.snap_record_btn = ctk.CTkButton(
            keybind_section,
            text="Keybind",
            width=70,
            height=32,
            command=self.start_recording_snap,
            fg_color=self.colors['highlight'],
            hover_color=self.colors['hover'],
            corner_radius=8
        )
        self.snap_record_btn.pack(side='left')
        
        # Action button
        self.snap_drag_btn = ctk.CTkButton(
            controls_frame,
            text="Action",
            width=70,
            height=32,
            command=self.start_recording_snap_drag,
            fg_color=self.colors['highlight'],
            hover_color=self.colors['hover'],
            corner_radius=8
        )
        self.snap_drag_btn.pack(side='left')

        # Dupes section header
        dupes_header = ctk.CTkLabel(
            frame, 
            text="Dupes",
            font=("Segoe UI", 18, "bold"),
            text_color=self.colors['highlight']
        )
        dupes_header.pack(pady=(25, 10), padx=20, anchor='w')

        # Throwable Card
        card, trig_frame = self._create_action_card(frame, "Throwable", "Throw → DC → Drop → Reconnect → Grab loop", has_action=True)
        
        # Left side - indicator and title
        left_side = ctk.CTkFrame(trig_frame, fg_color="transparent")
        left_side.pack(side='left', fill='x', expand=True)
        
        # Single indicator (shows if BOTH keybind and action are recorded)
        is_recorded = self._is_action_recorded('triggernade')
        indicator_color = self.colors['recorded'] if is_recorded else self.colors['not_recorded']
        
        indicator_frame = ctk.CTkFrame(left_side, fg_color="transparent", width=14, height=14)
        indicator_frame.pack(side='left', padx=(0, 10))
        indicator_frame.pack_propagate(False)
        
        self.trig_indicator = ctk.CTkLabel(
            indicator_frame,
            text="●",
            font=("Segoe UI", 16),
            text_color=indicator_color,
            width=14,
            height=14
        )
        self.trig_indicator.pack(expand=True)
        
        # Keep hidden keybind indicator for compatibility
        self.trig_keybind_indicator = self.trig_indicator
        
        # Title section
        title_frame = ctk.CTkFrame(left_side, fg_color="transparent")
        title_frame.pack(side='left', fill='x', expand=True)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🎯 Throwable",
            font=("Segoe UI", 14, "bold"),
            text_color=self.colors['text']
        )
        title_label.pack(side='top', anchor='w')
        
        desc_label = ctk.CTkLabel(
            title_frame,
            text="Throw → DC → Drop → Reconnect → Grab loop",
            font=("Segoe UI", 10),
            text_color=self.colors['text_dim']
        )
        desc_label.pack(side='top', anchor='w')
        
        # Right side controls
        controls_frame = ctk.CTkFrame(trig_frame, fg_color="transparent")
        controls_frame.pack(side='right', padx=(10, 0))
        
        # Keybind controls
        keybind_section = ctk.CTkFrame(controls_frame, fg_color="transparent")
        keybind_section.pack(side='left', padx=(0, 8))
        
        self.triggernade_hotkey_var = tk.StringVar(value=self.config.get("triggernade_hotkey", ""))
        self.triggernade_hotkey_entry = ctk.CTkEntry(
            keybind_section,
            textvariable=self.triggernade_hotkey_var,
            width=80,
            height=32,
            state="readonly",
            fg_color=self.colors['bg_light'],
            text_color=self.colors['text'],
            border_width=0
        )
        self.triggernade_hotkey_entry.pack(side='left', padx=(0, 5))
        
        self.triggernade_record_btn = ctk.CTkButton(
            keybind_section,
            text="Keybind",
            width=70,
            height=32,
            command=self.start_recording_triggernade,
            fg_color=self.colors['highlight'],
            hover_color=self.colors['hover'],
            corner_radius=8
        )
        self.triggernade_record_btn.pack(side='left')
        
        # Action button
        self.trig_drag_btn = ctk.CTkButton(
            controls_frame,
            text="Action",
            width=70,
            height=32,
            command=self.start_recording_triggernade_drag,
            fg_color=self.colors['highlight'],
            hover_color=self.colors['hover'],
            corner_radius=8
        )
        self.trig_drag_btn.pack(side='left')

        # Deployable Card
        card, mine_frame = self._create_action_card(frame, "Deployable", "Cook → Open inv + DC → Drop → Reconnect → Grab", has_action=True)
        
        # Left side - indicator and title
        left_side = ctk.CTkFrame(mine_frame, fg_color="transparent")
        left_side.pack(side='left', fill='x', expand=True)
        
        # Single indicator (shows if BOTH keybind and action are recorded)
        is_recorded = self._is_action_recorded('mine')
        indicator_color = self.colors['recorded'] if is_recorded else self.colors['not_recorded']
        
        indicator_frame = ctk.CTkFrame(left_side, fg_color="transparent", width=14, height=14)
        indicator_frame.pack(side='left', padx=(0, 10))
        indicator_frame.pack_propagate(False)
        
        self.mine_indicator = ctk.CTkLabel(
            indicator_frame,
            text="●",
            font=("Segoe UI", 16),
            text_color=indicator_color,
            width=14,
            height=14
        )
        self.mine_indicator.pack(expand=True)
        
        # Keep hidden keybind indicator for compatibility
        self.mine_keybind_indicator = self.mine_indicator
        
        # Title section
        title_frame = ctk.CTkFrame(left_side, fg_color="transparent")
        title_frame.pack(side='left', fill='x', expand=True)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="💣 Deployable",
            font=("Segoe UI", 14, "bold"),
            text_color=self.colors['text']
        )
        title_label.pack(side='top', anchor='w')
        
        desc_label = ctk.CTkLabel(
            title_frame,
            text="Cook → Open inv + DC → Drop → Reconnect → Grab",
            font=("Segoe UI", 10),
            text_color=self.colors['text_dim']
        )
        desc_label.pack(side='top', anchor='w')
        
        # Right side controls
        controls_frame = ctk.CTkFrame(mine_frame, fg_color="transparent")
        controls_frame.pack(side='right', padx=(10, 0))
        
        # Keybind controls
        keybind_section = ctk.CTkFrame(controls_frame, fg_color="transparent")
        keybind_section.pack(side='left', padx=(0, 8))
        
        self.mine_hotkey_var = tk.StringVar(value=self.config.get("mine_hotkey", ""))
        self.mine_hotkey_entry = ctk.CTkEntry(
            keybind_section,
            textvariable=self.mine_hotkey_var,
            width=80,
            height=32,
            state="readonly",
            fg_color=self.colors['bg_light'],
            text_color=self.colors['text'],
            border_width=0
        )
        self.mine_hotkey_entry.pack(side='left', padx=(0, 5))
        
        self.mine_record_btn = ctk.CTkButton(
            keybind_section,
            text="Keybind",
            width=70,
            height=32,
            command=self.start_recording_mine,
            fg_color=self.colors['highlight'],
            hover_color=self.colors['hover'],
            corner_radius=8
        )
        self.mine_record_btn.pack(side='left')
        
        # Action button
        self.mine_drag_btn = ctk.CTkButton(
            controls_frame,
            text="Action",
            width=70,
            height=32,
            command=self.start_recording_mine_drag,
            fg_color=self.colors['highlight'],
            hover_color=self.colors['hover'],
            corner_radius=8
        )
        self.mine_drag_btn.pack(side='left')

        # Keycard Card
        card, keycard_frame = self._create_action_card(frame, "🔑 Keycard", "DC → Open inv → Drag to drop → Reconnect", has_action=True)
        
        # Left side - indicator and title
        left_side = ctk.CTkFrame(keycard_frame, fg_color="transparent")
        left_side.pack(side='left', fill='x', expand=True)
        
        # Single indicator (shows if BOTH keybind and action are recorded)
        is_recorded = self._is_action_recorded('keycard')
        indicator_color = self.colors['recorded'] if is_recorded else self.colors['not_recorded']
        
        indicator_frame = ctk.CTkFrame(left_side, fg_color="transparent", width=14, height=14)
        indicator_frame.pack(side='left', padx=(0, 10))
        indicator_frame.pack_propagate(False)
        
        self.keycard_indicator = ctk.CTkLabel(
            indicator_frame,
            text="●",
            font=("Segoe UI", 16),
            text_color=indicator_color,
            width=14,
            height=14
        )
        self.keycard_indicator.pack(expand=True)
        
        title_frame = ctk.CTkFrame(left_side, fg_color="transparent")
        title_frame.pack(side='left', fill='x', expand=True)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🔑 Keycard",
            font=("Segoe UI", 14, "bold"),
            text_color=self.colors['text'],
            anchor='w'
        )
        title_label.pack(side='top', anchor='w')
        
        desc_label = ctk.CTkLabel(
            title_frame,
            text="DC → Open inv → Drag to drop → Reconnect",
            font=("Segoe UI", 10),
            text_color=self.colors['text_dim']
        )
        desc_label.pack(side='top', anchor='w')
        
        # Right side controls
        controls_frame = ctk.CTkFrame(keycard_frame, fg_color="transparent")
        controls_frame.pack(side='right', padx=(10, 0))
        
        # Keybind controls
        keybind_section = ctk.CTkFrame(controls_frame, fg_color="transparent")
        keybind_section.pack(side='left', padx=(0, 8))
        
        self.keycard_hotkey_var = tk.StringVar(value=self.config.get("keycard_hotkey", ""))
        self.keycard_hotkey_entry = ctk.CTkEntry(
            keybind_section,
            textvariable=self.keycard_hotkey_var,
            width=80,
            height=32,
            state="readonly",
            fg_color=self.colors['bg_light'],
            text_color=self.colors['text'],
            border_width=0
        )
        self.keycard_hotkey_entry.pack(side='left', padx=(0, 5))
        
        self.keycard_record_btn = ctk.CTkButton(
            keybind_section,
            text="Keybind",
            width=70,
            height=32,
            command=self.start_recording_keycard,
            fg_color=self.colors['highlight'],
            hover_color=self.colors['hover'],
            corner_radius=8
        )
        self.keycard_record_btn.pack(side='left')
        
        # Action button
        self.keycard_drag_btn = ctk.CTkButton(
            controls_frame,
            text="Action",
            width=70,
            height=32,
            command=self.start_recording_keycard_drag,
            fg_color=self.colors['highlight'],
            hover_color=self.colors['hover'],
            corner_radius=8
        )
        self.keycard_drag_btn.pack(side='left')

        # Initialize hidden timing variables and other variables that are still needed by the backend
        # DC Both button (hidden from UI but needed for backend)
        self.dc_both_btn = tk.Button(frame, text="DC BOTH", width=12, bg=self.colors['bg_light'], fg=self.colors['text'])
        self.dc_both_btn.pack_forget()
        
        # DC Outbound (hidden from UI but needed for backend)
        self.dc_outbound_hotkey_var = tk.StringVar(value=self.config.get("dc_outbound_hotkey", ""))
        self.dc_outbound_hotkey_entry = tk.Entry(frame)
        self.dc_outbound_hotkey_entry.pack_forget()
        self.dc_outbound_btn = tk.Button(frame, text="DC OUTBOUND", width=12, bg=self.colors['bg_light'], fg=self.colors['text'])
        self.dc_outbound_btn.pack_forget()
        self.dc_outbound_record_btn = ttk.Button(frame, text="Set", width=4)
        self.dc_outbound_record_btn.pack_forget()
        
        # DC Inbound (hidden from UI but needed for backend)
        self.dc_inbound_hotkey_var = tk.StringVar(value=self.config.get("dc_inbound_hotkey", ""))
        self.dc_inbound_hotkey_entry = tk.Entry(frame)
        self.dc_inbound_hotkey_entry.pack_forget()
        self.dc_inbound_btn = tk.Button(frame, text="DC INBOUND", width=12, bg=self.colors['bg_light'], fg=self.colors['text'])
        self.dc_inbound_btn.pack_forget()
        self.dc_inbound_record_btn = ttk.Button(frame, text="Set", width=4)
        self.dc_inbound_record_btn.pack_forget()
        
        # Tamper (hidden from UI but needed for backend)
        self.tamper_hotkey_var = tk.StringVar(value=self.config.get("tamper_hotkey", ""))
        self.tamper_hotkey_entry = tk.Entry(frame)
        self.tamper_hotkey_entry.pack_forget()
        self.tamper_btn = tk.Button(frame, text="TAMPER", width=12, bg=self.colors['bg_light'], fg=self.colors['text'])
        self.tamper_btn.pack_forget()
        self.tamper_record_btn = ttk.Button(frame, text="Set", width=4)
        self.tamper_record_btn.pack_forget()

        # Triggernade variables (hidden from UI but needed for backend)
        self.trig_drag_btn = ttk.Button(frame, text="Record", width=12)
        self.trig_drag_btn.pack_forget()
        self.trig_drag_var = tk.StringVar()
        trig_slot = self.config.get("trig_slot_pos", None)
        trig_drop = self.config.get("trig_drop_pos", None)
        self.trig_slot_pos = tuple(trig_slot) if trig_slot else None
        self.trig_drop_pos = tuple(trig_drop) if trig_drop else None
        trig_drag_s = self.config.get("trig_drag_start", None)
        trig_drag_e = self.config.get("trig_drag_end", None)
        self.trig_drag_start = tuple(trig_drag_s) if trig_drag_s else None
        self.trig_drag_end = tuple(trig_drag_e) if trig_drag_e else None
        self.triggernade_repeat_var = tk.BooleanVar(value=self.config.get("triggernade_repeat", False))
        self.trig_m1_hold_var = tk.IntVar(value=int(self.config.get("trig_m1_hold", 65)))
        self.trig_m2_hold_var = tk.IntVar(value=int(self.config.get("trig_m2_hold", 51)))
        self.trig_drag_speed_var = tk.IntVar(value=int(self.config.get("trig_drag_speed", 8)))
        self.trig_dc_delay_var = tk.IntVar(value=int(self.config.get("trig_dc_delay", 10)))
        self.trig_dc_throws_var = tk.IntVar(value=int(self.config.get("trig_dc_throws", 10)))
        self.trig_throw_delay_var = tk.IntVar(value=int(self.config.get("trig_throw_delay", 100)))
        self.trig_reconnect_after_var = tk.IntVar(value=int(self.config.get("trig_reconnect_after", 1)))
        self.wait_before_espam_var = tk.IntVar(value=int(self.config.get("wait_before_espam", 0)))
        self.espam_duration_var = tk.IntVar(value=int(self.config.get("espam_duration", 250)))
        self.trig_m1_before_interweave_var = tk.IntVar(value=int(self.config.get("trig_m1_before_interweave", 1)))
        self.wait_before_cycle_var = tk.IntVar(value=int(self.config.get("wait_before_cycle", 100)))
        self.wolfpack_m1_hold_var = tk.IntVar(value=int(self.config.get("wolfpack_m1_hold", 20)))
        self.wolfpack_m1_gap_var = tk.IntVar(value=int(self.config.get("wolfpack_m1_gap", 20)))
        self.wolfpack_dc_hold_var = tk.IntVar(value=int(self.config.get("wolfpack_dc_hold", 20)))
        self.wolfpack_dc_gap_var = tk.IntVar(value=int(self.config.get("wolfpack_dc_gap", 600)))
        self.triggernade_q_spam_var = tk.BooleanVar(value=self.config.get("triggernade_q_spam", False))
        self.triggernade_status_var = tk.StringVar(value="Ready")
        self.triggernade_status_label = ttk.Label(frame, textvariable=self.triggernade_status_var, style='Dim.TLabel')
        self.triggernade_status_label.pack_forget()

        # Mine variables (hidden from UI but needed for backend)
        self.mine_drag_btn = ttk.Button(frame, text="Record Path", width=12)
        self.mine_drag_btn.pack_forget()
        self.mine_repeat_var = tk.BooleanVar(value=self.config.get("mine_repeat", False))
        self.mine_drag_var = tk.StringVar()
        mine_slot = self.config.get("mine_slot_pos", [3032, 1236])
        mine_drop = self.config.get("mine_drop_pos", [3171, 1593])
        self.mine_slot_pos = tuple(mine_slot)
        self.mine_drop_pos = tuple(mine_drop)
        self.mine_drag_start = tuple(self.config.get("mine_drag_start", [3032, 1236]))
        self.mine_drag_end = tuple(self.config.get("mine_drag_end", [3171, 1593]))
        self.mine_cook_var = tk.IntVar(value=int(self.config.get("mine_cook", 236)))
        self.mine_dc_delay_var = tk.IntVar(value=int(self.config.get("mine_dc_delay", 99)))
        self.mine_drag_speed_var = tk.IntVar(value=int(self.config.get("mine_drag_speed", 8)))
        self.mine_pre_close_var = tk.IntVar(value=int(self.config.get("mine_pre_close", 100)))
        self.mine_tab_hold_var = tk.IntVar(value=int(self.config.get("mine_tab_hold", 80)))
        self.mine_close_reconnect_var = tk.IntVar(value=int(self.config.get("mine_close_reconnect", 409)))
        self.mine_click_delay_var = tk.IntVar(value=int(self.config.get("mine_click_delay", 7)))
        self.mine_pickup_hold_var = tk.IntVar(value=int(self.config.get("mine_pickup_hold", 1336)))
        self.mine_e_delay_var = tk.IntVar(value=int(self.config.get("mine_e_delay", 868)))
        self.mine_loop_delay_var = tk.IntVar(value=int(self.config.get("mine_loop_delay", 550)))
        self.mine_reselect_var = tk.BooleanVar(value=self.config.get("mine_reselect", True))
        default_q_recording = [
            [1920, 1080], [1920, 1064], [1920, 1046], [1920, 1020], [1920, 982],
            [1920, 949], [1922, 914], [1925, 884], [1928, 852], [1922, 1058],
            [1926, 1035], [1927, 1012], [1930, 993], [1922, 1065], [1924, 1049]
        ]
        self.mine_q_mode_var = tk.StringVar(value=self.config.get("mine_q_mode", "radial"))
        self.mine_q_direction_var = tk.StringVar(value=self.config.get("mine_q_direction", "S"))
        self.mine_nudge_var = tk.BooleanVar(value=self.config.get("mine_nudge", True))
        self.mine_nudge_px_var = tk.IntVar(value=self.config.get("mine_nudge_px", 50))
        self.mine_status_var = tk.StringVar(value="Ready")
        self.mine_status_label = ttk.Label(frame, textvariable=self.mine_status_var, style='Dim.TLabel')
        self.mine_status_label.pack_forget()

        # Snaphook variables
        snap_drag_s = self.config.get("snap_drag_start", None)
        snap_drag_e = self.config.get("snap_drag_end", None)
        self.snap_drag_start = tuple(snap_drag_s) if snap_drag_s else None
        self.snap_drag_end = tuple(snap_drag_e) if snap_drag_e else None
        self._snap_drag_started = False

        # Keycard variables
        keycard_drag_s = self.config.get("keycard_drag_start", None)
        keycard_drag_e = self.config.get("keycard_drag_end", None)
        self.keycard_drag_start = tuple(keycard_drag_s) if keycard_drag_s else None
        self.keycard_drag_end = tuple(keycard_drag_e) if keycard_drag_e else None
        self._keycard_drag_started = False

        # Stop hotkey (always ESC, used internally for stopping macros)
        self.stop_hotkey_var = tk.StringVar(value="esc")


    def _build_appearance_tab(self):
        """Delegate to UI builder"""
        return self.ui_builder._build_appearance_tab()

    def create_slider(self, parent, label, config_key, default, min_val, max_val, unit, bold=False, tooltip=None):
        """Create a slider row with label, slider, and editable value entry"""
        row = ttk.Frame(parent)
        row.pack(fill='x', padx=10, pady=2)

        if bold:
            lbl = ttk.Label(row, text=label, width=20, anchor='w', font=('Segoe UI', 9, 'bold'))
        else:
            lbl = ttk.Label(row, text=label, width=20, anchor='w')
        lbl.pack(side='left')

        # Add tooltip if provided
        if tooltip:
            def show_tooltip(event):
                tip = tk.Toplevel(row)
                tip.wm_overrideredirect(True)
                tip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                tip_label = tk.Label(tip, text=tooltip, justify='left', background="#ffffe0",
                                    relief='solid', borderwidth=1, font=("Segoe UI", 8),
                                    wraplength=300)
                tip_label.pack()
                row._tooltip = tip
            def hide_tooltip(event):
                if hasattr(row, '_tooltip'):
                    row._tooltip.destroy()
                    del row._tooltip
            lbl.bind('<Enter>', show_tooltip)
            lbl.bind('<Leave>', hide_tooltip)

        var = tk.IntVar(value=int(self.config.get(config_key, default)))
        setattr(self, f"{config_key}_var", var)

        def on_slide(val):
            var.set(int(float(val)))
            self.save_settings()

        slider = ttk.Scale(row, from_=min_val, to=max_val, variable=var, orient='horizontal', length=100,
                          command=on_slide)
        slider.pack(side='left', padx=5)

        # Editable entry instead of label (no border)
        entry = tk.Entry(row, width=5, justify='center', bd=0, highlightthickness=0,
                        bg=self.colors['bg_light'], fg=self.colors['text'], insertbackground=self.colors['text'])
        entry.pack(side='left')
        entry.insert(0, str(var.get()))

        def on_entry_change(event=None):
            try:
                val = int(entry.get())
                var.set(val)  # No clamping - accept any value
                self.save_settings()
            except ValueError:
                entry.delete(0, 'end')
                entry.insert(0, str(var.get()))

        def on_var_change(*args):
            entry.delete(0, 'end')
            entry.insert(0, str(var.get()))

        entry.bind('<Return>', on_entry_change)
        entry.bind('<FocusOut>', on_entry_change)
        var.trace_add('write', on_var_change)

        if unit:
            ttk.Label(row, text=unit).pack(side='left')

    def start_recording_mine(self):
        """Delegate to recording manager"""
        return self.recording_manager.start_recording_mine()
    
    def start_recording_mine_drag(self):
        """Delegate to recording manager"""
        return self.recording_manager.start_recording_mine_drag()
    
    def start_recording_snap(self):
        """Delegate to recording manager"""
        return self.recording_manager.start_recording_snap()
    
    def start_recording_snap_drag(self):
        """Delegate to recording manager"""
        return self.recording_manager.start_recording_snap_drag()

    def start_recording_keycard(self):
        """Delegate to recording manager"""
        return self.recording_manager.start_recording_keycard()
    
    def start_recording_keycard_drag(self):
        """Delegate to recording manager"""
        return self.recording_manager.start_recording_keycard_drag()

    def _show_direction_picker(self):
        """Delegate to direction picker manager"""
        return self.direction_picker_manager.show_direction_picker()

    def _play_mine_q_radial(self):
        """Delegate to direction picker manager"""
        return self.direction_picker_manager.play_mine_q_radial()

    def start_mine_drag_recording(self):
        """Delegate to recording manager"""
        return self.recording_manager.start_mine_drag_recording()

    def _update_macro_entry_colors(self):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.update_macro_entry_colors()

    def _on_macro_tab_click(self, index):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.on_macro_tab_click(index)

    def _add_new_macro(self):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.add_new_macro()

    def _delete_current_macro(self):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.delete_current_macro()

    def _export_current_macro(self):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.export_current_macro()

    def _import_macro(self):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.import_macro()

    def _get_current_macro(self):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.get_current_macro()

    def _load_current_macro_to_ui(self):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.load_current_macro_to_ui()

    def _save_current_macro_from_ui(self):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.save_current_macro_from_ui()

    def _on_macro_name_change(self):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.on_macro_name_change()

    def _on_macro_speed_change(self, value):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.on_macro_speed_change(value)

    def _on_macro_keep_timing_change(self):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.on_macro_keep_timing_change()

    def _on_macro_repeat_change(self):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.on_macro_repeat_change()

    def _on_macro_infinite_change(self):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.on_macro_infinite_change()

    def _validate_repeat_times(self, event=None):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.validate_repeat_times(event)

    def _validate_repeat_delay(self, event=None):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.validate_repeat_delay(event)

    def _toggle_macro_play(self):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.toggle_macro_play()

    def _start_recording_macro_hotkey(self):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.start_recording_macro_hotkey()

    def _on_macro_hotkey_press(self, event):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.on_macro_hotkey_press(event)

    def start_custom_macro_recording(self):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.start_custom_macro_recording()

    def _save_custom_macro_recording(self):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.save_custom_macro_recording()

    def play_custom_macro(self, macro_index=None):
        """Delegate to custom macro manager"""
        return self.custom_macro_manager.play_custom_macro(macro_index)

    # Public wrappers for macro manager methods (used by UI)
    def add_new_macro(self):
        return self._add_new_macro()
    
    def delete_current_macro(self):
        return self._delete_current_macro()
    
    def export_current_macro(self):
        return self._export_current_macro()
    
    def import_macro(self):
        return self._import_macro()
    
    def on_macro_tab_click(self, index):
        return self._on_macro_tab_click(index)
    
    def on_macro_name_change(self):
        return self._on_macro_name_change()
    
    def on_macro_speed_change(self, value):
        return self._on_macro_speed_change(value)
    
    def on_macro_keep_timing_change(self):
        return self._on_macro_keep_timing_change()
    
    def on_macro_repeat_change(self):
        return self._on_macro_repeat_change()
    
    def on_macro_infinite_change(self):
        return self._on_macro_infinite_change()
    
    def validate_repeat_times(self, event=None):
        return self._validate_repeat_times(event)
    
    def validate_repeat_delay(self, event=None):
        return self._validate_repeat_delay(event)
    
    def toggle_macro_play(self):
        return self._toggle_macro_play()
    
    def start_recording_macro_hotkey(self):
        return self._start_recording_macro_hotkey()
    
    def load_current_macro_to_ui(self):
        return self._load_current_macro_to_ui()

    def start_mine_drag_recording(self):
        """Record mine drag path - drag item to ground"""
        from pynput import mouse

        self.mine_drag_btn.configure(text="Recording...")
        self.show_overlay("DRAG item to ground", force=True)
        self._mine_drag_started = False
        self._mine_drag_start_time = None

        def on_click(x, y, button, pressed):
            if button != mouse.Button.left:
                return

            if pressed:
                self._mine_drag_start_temp = (x, y)
                self._mine_drag_start_time = time.time()
                self._mine_drag_started = True
                self.root.after(0, lambda: self.show_overlay("Now RELEASE...", force=True))
            elif self._mine_drag_started:
                # Validate drag: >20ms hold and >50px distance
                duration_ms = (time.time() - self._mine_drag_start_time) * 1000
                dx = x - self._mine_drag_start_temp[0]
                dy = y - self._mine_drag_start_temp[1]
                distance = (dx*dx + dy*dy) ** 0.5

                if duration_ms < 20 or distance < 50:
                    # Not a valid drag, reset
                    self._mine_drag_started = False
                    self.root.after(0, lambda: self.show_overlay("DRAG item to ground", force=True))
                    return

                self.mine_drag_start = self._mine_drag_start_temp
                self.mine_drag_end = (x, y)
                self.config["mine_drag_start"] = list(self.mine_drag_start)
                self.config["mine_drag_end"] = list(self.mine_drag_end)
                save_config(self.config)
                self.mine_drag_var.set(f"{self.mine_drag_start} → {self.mine_drag_end}")
                self.root.after(0, lambda: self.mine_drag_btn.configure(text="Record"))
                self.root.after(0, lambda: self._update_all_indicators())
                self.root.after(0, lambda: self.show_overlay("Recorded!", force=True))
                print(f"[MINE] Drag: {self.mine_drag_start} → {self.mine_drag_end}")
                # Clean up ESC hook on successful recording
                if esc_hook_ref[0]:
                    try:
                        keyboard.unhook(esc_hook_ref[0])
                    except:
                        pass
                return False  # Stop listener

        listener_ref = [None]
        esc_hook_ref = [None]
        listener_ref[0] = mouse.Listener(on_click=on_click)
        listener_ref[0].start()

        # ESC to cancel and stop all macros
        def on_esc():
            self._mine_recording_cancelled = True
            if listener_ref[0]:
                listener_ref[0].stop()
            self.root.after(0, lambda: self.mine_drag_btn.configure(text="Record"))
            self.root.after(0, lambda: self.show_overlay("Cancelled", force=True))
            self.stop_all_macros()
            if esc_hook_ref[0]:
                try:
                    keyboard.unhook(esc_hook_ref[0])
                except:
                    pass

        esc_hook_ref[0] = keyboard.on_press_key('esc', lambda e: on_esc(), suppress=False)

    def start_recording_triggernade(self):
        """Delegate to recording manager"""
        return self.recording_manager.start_recording_triggernade()
    
    def start_recording_triggernade_drag(self):
        """Delegate to recording manager"""
        return self.recording_manager.start_recording_triggernade_drag()

    def start_quickdrop_pos_recording(self):
        """Delegate to recording manager"""
        return self.recording_manager.start_quickdrop_pos_recording()

    def start_drag_recording(self):
        """Start recording drag coordinates - 10 sec countdown, then waits for mouse down/up"""
        if self.recording_drag:
            return  # Already recording

        self.recording_drag = True
        self.drag_record_btn.configure(text="10...")
        self.drag_label_var.set("Get ready...")

        # Start countdown
        self._drag_countdown(10)

    def _drag_countdown(self, seconds_left):
        """Countdown before starting drag recording"""
        if not self.recording_drag:
            return  # Cancelled

        if seconds_left > 0:
            self.drag_record_btn.configure(text=f"{seconds_left}...")
            self.show_overlay(f"Drag recording in {seconds_left}...", force=True)
            self.root.after(1000, lambda: self._drag_countdown(seconds_left - 1))
        else:
            # Countdown done - start listening
            self._start_drag_listener()

    def _start_drag_listener(self):
        """Actually start the mouse listener for drag recording"""
        from pynput import mouse

        self.drag_record_btn.configure(text="DRAG NOW")
        self.drag_label_var.set("Click and drag item!")
        self.show_overlay("DRAG NOW!", force=True)

        drag_start_pos = [None, None]

        def on_click(x, y, button, pressed):
            if button != mouse.Button.left:
                return  # Only track left clicks

            if pressed:
                # Mouse down - record start position
                drag_start_pos[0] = x
                drag_start_pos[1] = y
                self.root.after(0, lambda: self.drag_label_var.set(f"Start: ({x},{y}) - Release..."))
                self.root.after(0, lambda: self.show_overlay(f"Start: ({x},{y}) - Release...", force=True))
            else:
                # Mouse up - record end position and stop
                if drag_start_pos[0] is not None:
                    self.drag_start = (drag_start_pos[0], drag_start_pos[1])
                    self.drag_end = (x, y)

                    # Update UI
                    self.root.after(0, lambda: self.drag_label_var.set(
                        f"({self.drag_start[0]},{self.drag_start[1]}) → ({self.drag_end[0]},{self.drag_end[1]})"
                    ))
                    self.root.after(0, lambda: self.drag_record_btn.configure(text="Record Drag"))

                    # Save to config
                    self.config["drag_start"] = list(self.drag_start)
                    self.config["drag_end"] = list(self.drag_end)
                    save_config(self.config)

                    print(f"[DRAG] Recorded: {self.drag_start} → {self.drag_end}")
                    self.root.after(0, lambda: self.show_overlay(f"Drag saved!", force=True))

                    self.recording_drag = False
                    return False  # Stop listener

        # Start mouse listener
        self.drag_mouse_listener = mouse.Listener(on_click=on_click)
        self.drag_mouse_listener.start()

    def _start_drag_position_listener(self, target='triggernade'):
        """Listen for drag and record start/end positions only"""
        from pynput import mouse

        if self._drag_recording_cancelled:
            return

        self.show_overlay("Click & drag NOW!", force=True)

        state = {'start_pos': None}
        listener_ref = [None]
        esc_hook_ref = [None]

        def on_click(x, y, button, pressed):
            if self._drag_recording_cancelled:
                return False  # Stop listener

            if button != mouse.Button.left:
                return

            # Convert to int (pynput can return floats on some systems)
            x, y = int(x), int(y)

            if pressed:
                state['start_pos'] = (x, y)
                self.show_overlay(f"Dragging from ({x},{y})...", force=True)
            else:
                if state['start_pos']:
                    start = state['start_pos']
                    end = (x, y)

                    self.trig_drag_start = start
                    self.trig_drag_end = end
                    self.config["trig_drag_start"] = list(start)
                    self.config["trig_drag_end"] = list(end)
                    self.trig_drag_var.set(f"({start[0]},{start[1]}) → ({end[0]},{end[1]})")
                    print(f"[TRIG DRAG] Recorded: {start} → {end}")

                    save_config(self.config)
                    self.root.after(0, lambda: self._update_all_indicators())
                    self.show_overlay(f"Saved! {start} → {end}", force=True)
                    # Clean up ESC hook on successful recording
                    if esc_hook_ref[0]:
                        try:
                            keyboard.unhook(esc_hook_ref[0])
                        except:
                            pass
                    return False  # Stop listener

        listener_ref[0] = mouse.Listener(on_click=on_click)
        listener_ref[0].start()

        # ESC to cancel and stop all macros
        def on_esc():
            self._drag_recording_cancelled = True
            if listener_ref[0]:
                listener_ref[0].stop()
            self.root.after(0, lambda: self.show_overlay("Cancelled", force=True))
            self.stop_all_macros()
            if esc_hook_ref[0]:
                try:
                    keyboard.unhook(esc_hook_ref[0])
                except:
                    pass

        esc_hook_ref[0] = keyboard.on_press_key('esc', lambda e: on_esc(), suppress=False)

    def start_trig_drag_recording(self):
        """Delegate to recording manager"""
        return self.recording_manager.start_trig_drag_recording()

    def _drag_countdown(self, seconds_left, target, record_drag=True):
        if self._drag_recording_cancelled:
            return  # Cancelled
        if seconds_left > 0:
            self.show_overlay(f"Get ready... {seconds_left}", force=True)
            self.root.after(1000, lambda: self._drag_countdown(seconds_left - 1, target, record_drag))
        else:
            if record_drag:
                self._start_drag_position_listener(target)
            else:
                self._start_position_listener(target)

    def _start_position_listener(self, target):
        """Listen for single click to record position"""
        from pynput import mouse

        if self._drag_recording_cancelled:
            return

        self.show_overlay("Click position NOW!", force=True)

        listener_ref = [None]
        esc_hook_ref = [None]

        def on_click(x, y, button, pressed):
            if self._drag_recording_cancelled:
                return False  # Stop listener

            if button != mouse.Button.left:
                return
            if not pressed:  # On release
                x, y = int(x), int(y)
                pos = (x, y)

                self.trig_slot_pos = pos
                self.config["trig_slot_pos"] = list(pos)
                self.trig_drag_var.set(f"Pos: ({x}, {y})")
                print(f"[TRIG POS] Recorded: {pos}")

                save_config(self.config)
                print(f"[CONFIG] Saved to: {CONFIG_FILE}")
                self.show_overlay(f"Position saved: ({x}, {y})", force=True)
                # Clean up ESC hook on successful recording
                if esc_hook_ref[0]:
                    try:
                        keyboard.unhook(esc_hook_ref[0])
                    except:
                        pass
                return False  # Stop listener

        listener_ref[0] = mouse.Listener(on_click=on_click)
        listener_ref[0].start()

        # ESC to cancel and stop all macros
        def on_esc():
            self._drag_recording_cancelled = True
            if listener_ref[0]:
                listener_ref[0].stop()
            self.root.after(0, lambda: self.show_overlay("Cancelled", force=True))
            self.stop_all_macros()
            if esc_hook_ref[0]:
                try:
                    keyboard.unhook(esc_hook_ref[0])
                except:
                    pass

        esc_hook_ref[0] = keyboard.on_press_key('esc', lambda e: on_esc(), suppress=False)

    def start_slot_recording(self):
        """Record drop position - click where the item slot is"""
        self.slot_record_btn.configure(text="3...")
        self._slot_countdown(3)

    def _slot_countdown(self, seconds_left):
        if seconds_left > 0:
            self.slot_record_btn.configure(text=f"{seconds_left}...")
            self.show_overlay(f"Click slot in {seconds_left}...", force=True)
            self.root.after(1000, lambda: self._slot_countdown(seconds_left - 1))
        else:
            self._start_slot_listener()

    def _start_slot_listener(self):
        """Listen for click to record drop position"""
        from pynput import mouse

        self.slot_record_btn.configure(text="CLICK!")
        self.show_overlay("CLICK ON SLOT!", force=True)

        def on_click(x, y, button, pressed):
            if button == mouse.Button.left and pressed:
                self.drag_start = (x, y)

                # Save to config
                self.config["drop_position"] = [x, y]
                save_config(self.config)

                self.root.after(0, lambda: self.slot_pos_var.set(f"({x}, {y})"))
                self.root.after(0, lambda: self.slot_record_btn.configure(text="Record"))
                self.root.after(0, lambda: self.show_overlay(f"Position: ({x}, {y})", force=True))
                print(f"[SLOT] Recorded drop position: ({x}, {y})")
                return False  # Stop listener

        listener = mouse.Listener(on_click=on_click)
        listener.start()

    def start_recording_stop(self):
        """Stop All is always ESC - recording disabled"""
        # Stop All hotkey is fixed to ESC
        return  # Do nothing - ESC is hard-coded

    def on_key_press(self, event):
        """Delegate to hotkey recording handler"""
        return self.hotkey_recording_handler.on_key_press(event)

    # ===== APPEARANCE METHODS =====

    def _update_theme_colors(self):
        self.theme_manager.update_theme_colors()

    def _update_title_bar_colors(self):
        self.theme_manager.update_title_bar_colors()

    def _pick_bg_color(self):
        self.theme_manager.pick_bg_color()

    def _set_bg_color(self, color):
        self.theme_manager.set_bg_color(color)

    def _pick_fg_color(self):
        self.theme_manager.pick_fg_color()

    def _set_fg_color(self, color):
        self.theme_manager.set_fg_color(color)

    def _pick_accent_color(self):
        self.theme_manager.pick_accent_color()

    def _set_accent_color(self, color):
        self.theme_manager.set_accent_color(color)

    def _pick_card_bg_color(self):
        self.theme_manager.pick_card_bg_color()

    def _set_card_bg_color(self, color):
        self.theme_manager.set_card_bg_color(color)

    def _get_luminance(self, hex_color):
        return self.theme_manager.get_luminance(hex_color)

    def _is_dark_color(self, hex_color):
        return self.theme_manager.is_dark_color(hex_color)

    def _adjust_color(self, hex_color, amount):
        return self.theme_manager.adjust_color(hex_color, amount)

    def _lighten_color(self, hex_color, amount):
        return self.theme_manager.lighten_color(hex_color, amount)

    def _darken_color(self, hex_color, amount):
        return self.theme_manager.darken_color(hex_color, amount)

    def _on_transparency_change(self, value):
        self.theme_manager.on_transparency_change(value)

    def _apply_transparency(self):
        self.theme_manager.apply_transparency()

    def toggle_stay_on_top(self):
        self.theme_manager.toggle_stay_on_top()
        print(f"[UI] Stay on top: {self.stay_on_top_var.get()}")

    def _reset_dc_buttons(self):
        """Delegate to packet control manager"""
        return self.packet_control_manager.reset_dc_buttons()

    def toggle_dc_both(self):
        """Delegate to packet control manager"""
        return self.packet_control_manager.toggle_dc_both()

    def toggle_dc_outbound(self):
        """Delegate to packet control manager"""
        return self.packet_control_manager.toggle_dc_outbound()

    def toggle_dc_inbound(self):
        """Delegate to packet control manager"""
        return self.packet_control_manager.toggle_dc_inbound()

    def toggle_tamper(self):
        """Delegate to packet control manager"""
        return self.packet_control_manager.toggle_tamper()

    def start_recording_dc_both(self):
        """Delegate to recording manager"""
        return self.recording_manager.start_recording_dc_both()

    def start_recording_dc_outbound(self):
        """Delegate to recording manager"""
        return self.recording_manager.start_recording_dc_outbound()

    def start_recording_dc_inbound(self):
        """Delegate to recording manager"""
        return self.recording_manager.start_recording_dc_inbound()

    def start_recording_tamper(self):
        """Delegate to recording manager"""
        return self.recording_manager.start_recording_tamper()

    def save_settings(self):
        """Save all settings to config - uses SettingsManager to get current values"""
        # Get all current settings from UI vars
        all_settings = self.settings_manager.get_all_settings()
        
        # Flatten and save to config
        for group_settings in all_settings.values():
            self.config.update(group_settings)
        
        # Handle special cases
        if hasattr(self, 'trig_drag_start') and self.trig_drag_start:
            self.config["trig_drag_start"] = list(self.trig_drag_start)
        if hasattr(self, 'trig_drag_end') and self.trig_drag_end:
            self.config["trig_drag_end"] = list(self.trig_drag_end)
        if hasattr(self, 'mine_drag_start') and self.mine_drag_start:
            self.config["mine_drag_start"] = list(self.mine_drag_start)
        if hasattr(self, 'mine_drag_end') and self.mine_drag_end:
            self.config["mine_drag_end"] = list(self.mine_drag_end)
        
        save_config(self.config)

    def reset_triggernade_defaults(self):
        """Reset all triggernade timing parameters to defaults"""
        # Get defaults but preserve positions
        defaults = self.settings_manager.groups.get("triggernade", {}).copy()
        if self.trig_slot_pos:
            defaults["trig_slot_pos"] = list(self.trig_slot_pos)
        if self.trig_drop_pos:
            defaults["trig_drop_pos"] = list(self.trig_drop_pos)
        if self.trig_drag_start:
            defaults["trig_drag_start"] = list(self.trig_drag_start)
        if self.trig_drag_end:
            defaults["trig_drag_end"] = list(self.trig_drag_end)
        self.settings_manager.set_settings("triggernade", defaults)
        print("[RESET] Triggernade parameters reset to defaults (positions preserved)")

    def reset_mine_defaults(self):
        """Reset all mine dupe timing parameters to defaults"""
        defaults = self.settings_manager.groups.get("mine", {}).copy()
        self.settings_manager.set_settings("mine", defaults)
        if hasattr(self, 'mine_drag_var') and self.mine_drag_start and self.mine_drag_end:
            self.mine_drag_var.set(f"{self.mine_drag_start} → {self.mine_drag_end}")
        print("[RESET] Mine dupe parameters reset to defaults")

    def reset_all_settings(self):
        """Reset ALL settings including hotkeys and recordings to factory defaults"""
        import tkinter.messagebox as mb
        if not mb.askyesno("Reset All Settings", "This will reset EVERYTHING including:\n\n• All hotkeys\n• All timing settings\n• All recorded positions\n• Drag drop preference\n\nAre you sure?"):
            return

        # Clear config file completely
        self.config = {}
        save_config(self.config)

        # Reset ALL hotkeys
        print("[RESET] Clearing all hotkeys...")
        self.triggernade_hotkey_var.set("")
        self.dc_both_hotkey_var.set("")
        self.dc_outbound_hotkey_var.set("")
        self.dc_inbound_hotkey_var.set("")
        self.tamper_hotkey_var.set("")
        self.mine_hotkey_var.set("")
        if hasattr(self, 'snap_hotkey_var'):
            self.snap_hotkey_var.set("")
        if hasattr(self, 'keycard_hotkey_var'):
            self.keycard_hotkey_var.set("")
        if hasattr(self, 'stop_hotkey_var'):
            self.stop_hotkey_var.set("esc")  # Default is esc
        print("[RESET] All hotkeys cleared")

        # Reset checkboxes
        print("[RESET] Resetting checkboxes...")
        self.show_overlay_var.set(True)
        self.stay_on_top_var.set(False)
        self.triggernade_repeat_var.set(True)

        # Clear all drag positions (these affect the "recorded" indicators)
        print("[RESET] Clearing all drag positions...")
        if hasattr(self, 'snap_drag_start'):
            self.snap_drag_start = None
        if hasattr(self, 'snap_drag_end'):
            self.snap_drag_end = None
        if hasattr(self, 'keycard_drag_start'):
            self.keycard_drag_start = None
        if hasattr(self, 'keycard_drag_end'):
            self.keycard_drag_end = None
        if hasattr(self, 'trig_drag_start'):
            self.trig_drag_start = None
        if hasattr(self, 'trig_drag_end'):
            self.trig_drag_end = None
        if hasattr(self, 'trig_slot_pos'):
            self.trig_slot_pos = None
        if hasattr(self, 'trig_drop_pos'):
            self.trig_drop_pos = None
        if hasattr(self, 'mine_drag_start'):
            self.mine_drag_start = None
        if hasattr(self, 'mine_drag_end'):
            self.mine_drag_end = None
        if hasattr(self, 'mine_slot_pos'):
            self.mine_slot_pos = None
        if hasattr(self, 'mine_drop_pos'):
            self.mine_drop_pos = None

        # Reset ALL timing sliders and positions (without preserving positions)
        print("[RESET] Resetting all timing defaults...")
        # Reset triggernade without preserving positions
        defaults = self.settings_manager.groups.get("triggernade", {}).copy()
        defaults["trig_slot_pos"] = None
        defaults["trig_drop_pos"] = None
        defaults["trig_drag_start"] = None
        defaults["trig_drag_end"] = None
        self.settings_manager.set_settings("triggernade", defaults)
        
        # Reset mine without preserving positions
        mine_defaults = self.settings_manager.groups.get("mine", {}).copy()
        mine_defaults["mine_slot_pos"] = None
        mine_defaults["mine_drop_pos"] = None
        mine_defaults["mine_drag_start"] = None
        mine_defaults["mine_drag_end"] = None
        self.settings_manager.set_settings("mine", mine_defaults)
        
        # Clear snaphook and keycard positions
        snap_defaults = self.settings_manager.groups.get("snaphook", {}).copy()
        snap_defaults["snap_drag_start"] = None
        snap_defaults["snap_drag_end"] = None
        self.settings_manager.set_settings("snaphook", snap_defaults)
        
        keycard_defaults = self.settings_manager.groups.get("keycard", {}).copy()
        keycard_defaults["keycard_drag_start"] = None
        keycard_defaults["keycard_drag_end"] = None
        self.settings_manager.set_settings("keycard", keycard_defaults)
        
        # Reset disconnect hotkeys in config explicitly
        disconnect_defaults = self.settings_manager.groups.get("disconnect", {}).copy()
        disconnect_defaults["dc_both_hotkey"] = ""
        disconnect_defaults["dc_outbound_hotkey"] = ""
        disconnect_defaults["dc_inbound_hotkey"] = ""
        disconnect_defaults["tamper_hotkey"] = ""
        self.settings_manager.set_settings("disconnect", disconnect_defaults)
        
        # Explicitly update config dict with cleared hotkeys
        self.config["triggernade_hotkey"] = ""
        self.config["mine_hotkey"] = ""
        self.config["snap_hotkey"] = ""
        self.config["keycard_hotkey"] = ""
        self.config["dc_both_hotkey"] = ""
        self.config["dc_outbound_hotkey"] = ""
        self.config["dc_inbound_hotkey"] = ""
        self.config["tamper_hotkey"] = ""
        self.config["trig_drag_start"] = None
        self.config["trig_drag_end"] = None
        self.config["mine_drag_start"] = None
        self.config["mine_drag_end"] = None
        self.config["snap_drag_start"] = None
        self.config["snap_drag_end"] = None
        self.config["keycard_drag_start"] = None
        self.config["keycard_drag_end"] = None

        # Force clear ALL keyboard hooks before re-registering
        import keyboard
        try:
            keyboard.unhook_all()
            print("[RESET] Force cleared all keyboard hooks")
        except Exception as e:
            print(f"[RESET] Error clearing keyboard hooks: {e}")
        
        # Reset all recording flags
        self.recording_triggernade = False
        self.recording_mine = False
        self.recording_snap = False
        self.recording_keycard = False
        self.recording_dc_both = False
        self.recording_dc_outbound = False
        self.recording_dc_inbound = False
        self.recording_tamper = False
        self.recording_stop = False
        
        # Reset button texts
        if hasattr(self, 'triggernade_record_btn'):
            self.triggernade_record_btn.configure(text="Set")
        if hasattr(self, 'mine_record_btn'):
            self.mine_record_btn.configure(text="Keybind")
        if hasattr(self, 'snap_record_btn'):
            self.snap_record_btn.configure(text="Keybind")
        if hasattr(self, 'keycard_record_btn'):
            self.keycard_record_btn.configure(text="Keybind")
        if hasattr(self, 'dc_both_record_btn'):
            self.dc_both_record_btn.configure(text="Keybind")
        if hasattr(self, 'dc_outbound_record_btn'):
            self.dc_outbound_record_btn.configure(text="Keybind")
        if hasattr(self, 'dc_inbound_record_btn'):
            self.dc_inbound_record_btn.configure(text="Keybind")
        if hasattr(self, 'tamper_record_btn'):
            self.tamper_record_btn.configure(text="Keybind")
        
        # Unbind any existing key press handlers
        try:
            self.root.unbind("<KeyPress>")
        except:
            pass
        
        # Save settings first so config is updated
        self.save_settings()
        
        # Re-register hotkeys (will be empty now, but registers ESC for stop)
        self.register_hotkeys()

        # Update indicators without rebuilding UI (safer)
        self.indicator_manager.update_all_indicators()
        
        # Force GUI refresh
        self.root.update_idletasks()

        print("[RESET] ALL settings reset to factory defaults")
        self.show_overlay("All settings reset!")
    
    def reset_preferences_only(self):
        """Reset only appearance and general preferences, preserving timing settings"""
        return self.reset_manager.reset_preferences_only()

    # ===== EXPORT/IMPORT SETTINGS =====
    def _get_triggernade_settings(self):
        """Get all triggernade-related settings as a dict"""
        return self.settings_manager.get_settings("triggernade")

    def _set_triggernade_settings(self, data):
        """Apply triggernade settings from dict"""
        self.settings_manager.set_settings("triggernade", data)

    def _get_mine_settings(self):
        """Get all mine dupe-related settings as a dict"""
        return self.settings_manager.get_settings("mine")

    def _set_mine_settings(self, data):
        """Apply mine dupe settings from dict"""
        self.settings_manager.set_settings("mine", data)

    def export_triggernade(self):
        """Export triggernade settings to file"""
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")],
                                            initialfile="triggernade_settings.json")
        if path:
            with open(path, 'w') as f:
                json.dump({"type": "triggernade", **self._get_triggernade_settings()}, f, indent=2)
            print(f"[EXPORT] Triggernade settings saved to {path}")

    def import_triggernade(self):
        """Import triggernade settings from file"""
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            with open(path, 'r') as f:
                data = json.load(f)
            self._set_triggernade_settings(data)
            self.register_hotkeys()
            print(f"[IMPORT] Triggernade settings loaded from {path}")

    def export_mine(self):
        """Export mine dupe settings to file"""
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")],
                                            initialfile="mine_settings.json")
        if path:
            with open(path, 'w') as f:
                json.dump({"type": "mine", **self._get_mine_settings()}, f, indent=2)
            print(f"[EXPORT] Mine settings saved to {path}")

    def import_mine(self):
        """Import mine dupe settings from file"""
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            with open(path, 'r') as f:
                data = json.load(f)
            self._set_mine_settings(data)
            self.register_hotkeys()
            print(f"[IMPORT] Mine settings loaded from {path}")

    def export_all_settings(self):
        """Export all macro settings to a single file"""
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")],
                                            initialfile="all_settings.json")
        if path:
            data = {
                "type": "all",
                **self.settings_manager.get_all_settings()
            }
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"[EXPORT] All settings saved to {path}")

    def import_all_settings(self):
        """Import all macro settings from file"""
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            with open(path, 'r') as f:
                data = json.load(f)
            # Handle both single-macro and all-settings files
            if data.get("type") == "all":
                self.settings_manager.set_all_settings(data)
            elif data.get("type") == "triggernade":
                self._set_triggernade_settings(data)
            elif data.get("type") == "mine":
                self._set_mine_settings(data)
            else:
                # Try to detect from keys
                if "triggernade_hotkey" in data: self._set_triggernade_settings(data)
                if "mine_hotkey" in data: self._set_mine_settings(data)
            self.register_hotkeys()
            print(f"[IMPORT] Settings loaded from {path}")

    def register_hotkeys(self):
        """Register all hotkeys - delegates to HotkeyManager"""
        self.hotkey_manager.register_all()

    def stop_all_macros(self):
        """Universal stop - triggered by configurable hotkey"""
        # Don't interrupt custom macro recording
        if getattr(self, '_custom_macro_recording_active', False):
            print("[HOTKEY] Stop All pressed but custom macro recording active - ignoring")
            return
        print("[HOTKEY] Stop All pressed - stopping all macros!")
        self.triggernade_stop = True
        self.mine_stop = True
        # Also cancel any active recordings
        self._drag_recording_cancelled = True
        self._mine_recording_cancelled = True
        self.root.after(0, lambda: self.show_overlay("Stopped"))

    def on_triggernade_hotkey(self):
        """Toggle triggernade macro"""
        if not self._triggernade_lock.acquire(blocking=False):
            return  # Already processing, ignore duplicate
        try:
            print(f"[HOTKEY] Triggernade hotkey PRESSED! running={self.triggernade_running}")
            if self.triggernade_running:
                print("[HOTKEY] Setting triggernade_stop = True")
                self.triggernade_stop = True
                self.root.after(0, lambda: self.triggernade_status_var.set("Stopping..."))
            else:
                print("[HOTKEY] Starting triggernade macro")
                # Reset ALL stop flags so vsleep doesn't exit early
                self.triggernade_stop = False
                self.mine_stop = False
                self.triggernade_running = True
                self.root.after(0, lambda: self.triggernade_status_var.set("RUNNING"))
                self.root.after(0, lambda: self.triggernade_status_label.configure(foreground="orange"))
                self.root.after(0, lambda: self.indicator_manager.set_indicator_running('triggernade'))
                self.root.after(0, lambda: self.show_overlay("Wolfpack/Triggernade started"))
                threading.Thread(target=self.run_triggernade_macro, daemon=True).start()
        finally:
            self._triggernade_lock.release()

    def run_triggernade_macro(self):
        """Delegate to MacroExecutor"""
        return self.macro_executor.run_triggernade_macro()

    def on_mine_hotkey(self):
        """Toggle mine dupe macro"""
        if not self._mine_lock.acquire(blocking=False):
            return  # Already processing, ignore duplicate
        try:
            print(f"[HOTKEY] Mine hotkey PRESSED! running={self.mine_running}")
            if self.mine_running:
                print("[HOTKEY] Setting mine_stop = True")
                self.mine_stop = True
                self.root.after(0, lambda: self.mine_status_var.set("Stopping..."))
            else:
                print("[HOTKEY] Starting mine macro")
                # Reset ALL stop flags so vsleep doesn't exit early
                self.mine_stop = False
                self.triggernade_stop = False
                self.mine_running = True
                self.root.after(0, lambda: self.mine_status_var.set("RUNNING"))
                self.root.after(0, lambda: self.mine_status_label.configure(foreground="orange"))
                self.root.after(0, lambda: self.indicator_manager.set_indicator_running('mine'))
                self.root.after(0, lambda: self.show_overlay("Mine Dupe started"))
                threading.Thread(target=self.macro_executor.run_mine_macro, daemon=True).start()
        finally:
            self._mine_lock.release()

    def on_snap_hotkey(self):
        """Execute snaphook drag action"""
        print(f"[SNAPHOOK] Hotkey pressed!")
        if not self.snap_drag_start or not self.snap_drag_end:
            print("[SNAPHOOK] Drag positions not set!")
            self.root.after(0, lambda: self.show_overlay("Snaphook not configured!", force=True))
            return
        
        self.root.after(0, lambda: self.indicator_manager.set_indicator_running('snaphook'))
        self.root.after(0, lambda: self.show_overlay("Snaphook executing...", force=True))
        threading.Thread(target=self.macro_executor.execute_snap_action, daemon=True).start()

    def on_keycard_hotkey(self):
        """Execute keycard dupe action"""
        print(f"[KEYCARD] Hotkey pressed!")
        if not self.keycard_drag_start or not self.keycard_drag_end:
            print("[KEYCARD] Positions not set!")
            self.root.after(0, lambda: self.show_overlay("Keycard not configured!", force=True))
            return
        
        self.root.after(0, lambda: self.indicator_manager.set_indicator_running('keycard'))
        self.root.after(0, lambda: self.show_overlay("Keycard executing...", force=True))
        threading.Thread(target=self.macro_executor.execute_keycard_action, daemon=True).start()

    def run_mine_macro(self):
        """Delegate to MacroExecutor"""
        return self.macro_executor.run_mine_macro()

    def show_overlay(self, text, force=False):
        """Show overlay message - delegates to OverlayManager"""
        if self.overlay is None:
            # Initialize if not already done
            if hasattr(self, 'show_overlay_var'):
                self.overlay = OverlayManager(self.root, self.show_overlay_var)
            else:
                self.overlay = OverlayManager(self.root)
        self.overlay.show_overlay(text, force)

    def hide_overlay(self):
        """Hide overlay - delegates to OverlayManager"""
        if self.overlay:
            self.overlay.hide_overlay()
    
    def _ensure_overlay(self):
        """Ensure overlay is initialized"""
        if self.overlay is None:
            if hasattr(self, 'show_overlay_var'):
                self.overlay = OverlayManager(self.root, self.show_overlay_var)
            else:
                self.overlay = OverlayManager(self.root)
        return self.overlay

    def on_close(self):
        self.triggernade_stop = True
        self.mine_stop = True

        # ALWAYS ensure network is restored on close
        try:
            stop_packet_drop()
            stop_packet_tamper()
            print("[CLOSE] Network restored")
        except Exception as e:
            print(f"[CLOSE] Error restoring network: {e}")

        # Stop drag recording listener if active
        if self.drag_mouse_listener:
            try:
                self.drag_mouse_listener.stop()
            except:
                pass
        if self.triggernade_hotkey_registered:
            try:
                keyboard.remove_hotkey(self.triggernade_hotkey_registered)
            except:
                pass

        # Save window position
        self.config["window_x"] = self.root.winfo_x()
        self.config["window_y"] = self.root.winfo_y()
        save_config(self.config)

        self.root.destroy()


def start_main_app():
    try:
        # Set CustomTkinter appearance mode and theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        root = ctk.CTk()
        app = MainApp(root)

        # Apply stay-on-top setting from config
        if app.config.get("stay_on_top", False):
            root.attributes('-topmost', True)
            print("[UI] Stay on top enabled from config")

        print(f"[CONFIG] Loaded config: {app.config}")

        app.register_hotkeys()
        print("[STARTUP] Ready - listening for hotkeys")
        print("=" * 50)

        root.mainloop()
    except Exception as e:
        import traceback
        print(f"CRASH ERROR: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    try:
        # Obfuscation: rename exe to UUID name on first run (if enabled)
        rename_self_and_restart()

        # Make app DPI-aware so mouse coordinates are consistent
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware
        except:
            try:
                ctypes.windll.user32.SetProcessDPIAware()  # Fallback
            except:
                pass

        if not is_admin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()

        print("=" * 50)
        print(f"{APP_NAME} Starting...")
        if OBFUSCATION_ENABLED:
            print(f"[OBFUS] Build ID: {BUILD_ID}")
        print("=" * 50)

        # Run login before starting main app
        run_login(start_main_app)

    except Exception as e:
        import traceback
        print(f"CRASH ERROR: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")

"""Hotkey recording handler - handles keyboard input for recording hotkeys"""
import keyboard


class HotkeyRecordingHandler:
    """Handles keyboard input for recording hotkeys"""
    
    def __init__(self, app_instance):
        self.app = app_instance
    
    def on_key_press(self, event):
        # Check if any recording is active
        if not self.app.recording_triggernade and not self.app.recording_mine and not self.app.recording_snap and not self.app.recording_keycard and not self.app.recording_dc_both and not self.app.recording_dc_outbound and not self.app.recording_dc_inbound and not self.app.recording_tamper and not self.app.recording_stop:
            return

        # Use keyboard library to check modifiers (tkinter state flags are unreliable)
        parts = []
        if keyboard.is_pressed('ctrl'):
            parts.append("ctrl")
        if keyboard.is_pressed('alt'):
            parts.append("alt")
        if keyboard.is_pressed('shift'):
            parts.append("shift")

        # Map tkinter keysyms to keyboard library key names
        tkinter_to_keyboard = {
            'next': 'page down',
            'prior': 'page up',
            'escape': 'esc',
            'return': 'enter',
            'control_l': 'ctrl',
            'control_r': 'ctrl',
            'alt_l': 'alt',
            'alt_r': 'alt',
            'shift_l': 'shift',
            'shift_r': 'shift',
            'caps_lock': 'caps lock',
            'num_lock': 'num lock',
            'scroll_lock': 'scroll lock',
            'print': 'print screen',
            'insert': 'insert',
            'delete': 'delete',
            'home': 'home',
            'end': 'end',
            'up': 'up',
            'down': 'down',
            'left': 'left',
            'right': 'right',
            'space': 'space',
            'tab': 'tab',
            'backspace': 'backspace',
            # Symbol keys
            'minus': '-',
            'plus': '+',
            'equal': '=',
            'bracketleft': '[',
            'bracketright': ']',
            'semicolon': ';',
            'apostrophe': "'",
            'grave': '`',
            'backslash': '\\',
            'comma': ',',
            'period': '.',
            'slash': '/',
            # Numpad
            'kp_subtract': '-',
            'kp_add': '+',
            'kp_multiply': '*',
            'kp_divide': '/',
            'kp_decimal': '.',
            'kp_enter': 'enter',
        }

        key = event.keysym.lower()
        key = tkinter_to_keyboard.get(key, key)  # Map if exists, otherwise use as-is

        # ESC clears the hotkey
        if key == 'esc':
            if self.app.recording_triggernade:
                self.app.triggernade_hotkey_var.set("")
                self.app.triggernade_record_btn.configure(text="Set")
                self.app.recording_triggernade = False
            elif self.app.recording_mine:
                self.app.mine_hotkey_var.set("")
                self.app.mine_record_btn.configure(text="Set")
                self.app.recording_mine = False
            elif self.app.recording_snap:
                self.app.snap_hotkey_var.set("")
                self.app.snap_record_btn.configure(text="Keybind")
                self.app.recording_snap = False
            elif self.app.recording_keycard:
                self.app.keycard_hotkey_var.set("")
                self.app.keycard_record_btn.configure(text="Keybind")
                self.app.recording_keycard = False
            elif self.app.recording_stop:
                self.app.stop_hotkey_var.set("")
                self.app.stop_record_btn.configure(text="Set")
                self.app.recording_stop = False
            elif self.app.recording_dc_both:
                self.app.dc_both_hotkey_var.set("")
                self.app.dc_both_record_btn.configure(text="Set")
                self.app.recording_dc_both = False
            elif self.app.recording_dc_outbound:
                self.app.dc_outbound_hotkey_var.set("")
                self.app.dc_outbound_record_btn.configure(text="Set")
                self.app.recording_dc_outbound = False
            elif self.app.recording_dc_inbound:
                self.app.dc_inbound_hotkey_var.set("")
                self.app.dc_inbound_record_btn.configure(text="Set")
                self.app.recording_dc_inbound = False
            elif self.app.recording_tamper:
                self.app.tamper_hotkey_var.set("")
                self.app.tamper_record_btn.configure(text="Set")
                self.app.recording_tamper = False
            self.app.root.unbind("<KeyPress>")
            self.app.root.update_idletasks()  # Force GUI refresh
            self.app.save_settings()
            self.app.register_hotkeys()
            return

        modifier_keys = ['ctrl', 'alt', 'shift', 'control_l', 'control_r', 'alt_l', 'alt_r', 'shift_l', 'shift_r', 'meta_l', 'meta_r']
        if key not in modifier_keys:
            parts.append(key)
            hotkey = "+".join(parts)

            # Clear this hotkey from any other action first
            all_hotkey_vars = [
                self.app.triggernade_hotkey_var,
                self.app.mine_hotkey_var,
                self.app.snap_hotkey_var,
                self.app.keycard_hotkey_var,
                self.app.stop_hotkey_var,
                self.app.dc_both_hotkey_var,
                self.app.dc_outbound_hotkey_var,
                self.app.dc_inbound_hotkey_var,
                self.app.tamper_hotkey_var,
            ]
            for var in all_hotkey_vars:
                if var.get() == hotkey:
                    var.set("")

            if self.app.recording_triggernade:
                self.app.triggernade_hotkey_var.set(hotkey)
                self.app.triggernade_record_btn.configure(text="Record")
                self.app.recording_triggernade = False
            elif self.app.recording_mine:
                self.app.mine_hotkey_var.set(hotkey)
                self.app.mine_record_btn.configure(text="Keybind")
                self.app.recording_mine = False
            elif self.app.recording_snap:
                self.app.snap_hotkey_var.set(hotkey)
                self.app.snap_record_btn.configure(text="Keybind")
                self.app.recording_snap = False
            elif self.app.recording_keycard:
                self.app.keycard_hotkey_var.set(hotkey)
                self.app.keycard_record_btn.configure(text="Keybind")
                self.app.recording_keycard = False
            elif self.app.recording_stop:
                self.app.stop_hotkey_var.set(hotkey)
                self.app.stop_record_btn.configure(text="Record")
                self.app.recording_stop = False
            elif self.app.recording_dc_both:
                self.app.dc_both_hotkey_var.set(hotkey)
                self.app.dc_both_record_btn.configure(text="Record")
                self.app.recording_dc_both = False
            elif self.app.recording_dc_outbound:
                self.app.dc_outbound_hotkey_var.set(hotkey)
                self.app.dc_outbound_record_btn.configure(text="Record")
                self.app.recording_dc_outbound = False
            elif self.app.recording_dc_inbound:
                self.app.dc_inbound_hotkey_var.set(hotkey)
                self.app.dc_inbound_record_btn.configure(text="Record")
                self.app.recording_dc_inbound = False
            elif self.app.recording_tamper:
                self.app.tamper_hotkey_var.set(hotkey)
                self.app.tamper_record_btn.configure(text="Record")
                self.app.recording_tamper = False
            self.app.root.unbind("<KeyPress>")
            self.app.root.update_idletasks()  # Force GUI refresh
            self.app.indicator_manager.update_all_indicators()  # Update recording indicators
            self.app.save_settings()
            self.app.register_hotkeys()

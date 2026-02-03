import json
import os
import time
import threading
import keyboard
import tkinter as tk
from tkinter import filedialog
from pynput import mouse, keyboard as kb
from utils import pynput_keyboard, pynput_mouse

CUSTOM_MACROS_FILE = os.path.join(os.environ.get('APPDATA', '.'), "Application", "custom_macros.json")

def load_custom_macros():
    """Load custom macros from file"""
    if os.path.exists(CUSTOM_MACROS_FILE):
        try:
            with open(CUSTOM_MACROS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"macros": [{"name": "Macro 1", "hotkey": "", "speed": 1.0, "events": []}], "active_index": 0}

def save_custom_macros(data):
    """Save custom macros to file"""
    os.makedirs(os.path.dirname(CUSTOM_MACROS_FILE), exist_ok=True)
    with open(CUSTOM_MACROS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

class CustomMacroManager:
    """Manages custom macro functionality - tightly coupled to app instance"""
    
    def __init__(self, app):
        self.app = app
        self.app.custom_macros_data = load_custom_macros()
        self.app.active_macro_index = self.app.custom_macros_data.get("active_index", 0)
    
    def update_macro_entry_colors(self):
        """Update Entry widget colors to match current theme"""
        bg_light = self.app.colors['bg_light']
        text = self.app.colors['text']
        if hasattr(self.app, 'macro_name_entry'):
            self.app.macro_name_entry.configure(bg=bg_light, fg=text, insertbackground=text,
                                         highlightbackground=self.app.colors.get('bg_lighter', '#555555'))
        if hasattr(self.app, 'macro_hotkey_entry'):
            self.app.macro_hotkey_entry.configure(bg=bg_light, fg=text, readonlybackground=bg_light)

    def on_macro_tab_click(self, index):
        """Switch to a different macro tab"""
        self.save_current_macro_from_ui()
        self.app.active_macro_index = index
        self.app.custom_macros_data["active_index"] = index
        save_custom_macros(self.app.custom_macros_data)
        self.build_macro_tabs()
        self.load_current_macro_to_ui()

    def add_new_macro(self):
        """Add a new macro"""
        macros = self.app.custom_macros_data.get("macros", [])
        new_name = f"Macro {len(macros) + 1}"
        new_macro = {"name": new_name, "hotkey": "", "speed": 1.0, "events": []}
        macros.append(new_macro)
        self.app.custom_macros_data["macros"] = macros
        self.app.active_macro_index = len(macros) - 1
        self.app.custom_macros_data["active_index"] = self.app.active_macro_index
        save_custom_macros(self.app.custom_macros_data)
        self.build_macro_tabs()
        self.load_current_macro_to_ui()
        self.app.register_hotkeys()

    def delete_current_macro(self):
        """Delete the current macro"""
        macros = self.app.custom_macros_data.get("macros", [])
        if len(macros) <= 1:
            self.app.show_overlay("Can't delete last macro", force=True)
            return
        del macros[self.app.active_macro_index]
        self.app.custom_macros_data["macros"] = macros
        if self.app.active_macro_index >= len(macros):
            self.app.active_macro_index = len(macros) - 1
        self.app.custom_macros_data["active_index"] = self.app.active_macro_index
        save_custom_macros(self.app.custom_macros_data)
        self.build_macro_tabs()
        self.load_current_macro_to_ui()
        self.app.register_hotkeys()

    def export_current_macro(self):
        """Export the current macro to a JSON file"""
        macro = self.get_current_macro()
        if not macro.get("events"):
            self.app.show_overlay("No recording to export", force=True)
            return

        name = macro.get("name", "macro")
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            initialfile=f"{name}.json"
        )
        if path:
            with open(path, 'w') as f:
                json.dump(macro, f, indent=2)
            self.app.show_overlay(f"Exported: {name}", force=True)
            print(f"[MACRO] Exported '{name}' to {path}")

    def import_macro(self):
        """Import a macro from a JSON file"""
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            try:
                with open(path, 'r') as f:
                    imported = json.load(f)

                if "events" not in imported:
                    if isinstance(imported, list):
                        imported = {"name": "Imported", "hotkey": "", "speed": 1.0, "events": imported}
                    else:
                        self.app.show_overlay("Invalid macro file", force=True)
                        return

                macros = self.app.custom_macros_data.get("macros", [])
                base_name = imported.get("name", "Imported")
                name = base_name
                counter = 1
                while any(m.get("name") == name for m in macros):
                    name = f"{base_name} ({counter})"
                    counter += 1
                imported["name"] = name

                macros.append(imported)
                self.app.custom_macros_data["macros"] = macros
                self.app.active_macro_index = len(macros) - 1
                self.app.custom_macros_data["active_index"] = self.app.active_macro_index
                save_custom_macros(self.app.custom_macros_data)
                self.build_macro_tabs()
                self.load_current_macro_to_ui()
                self.app.register_hotkeys()
                self.app.show_overlay(f"Imported: {name}", force=True)
                print(f"[MACRO] Imported '{name}' from {path}")
            except Exception as e:
                self.app.show_overlay("Import failed", force=True)
                print(f"[MACRO] Import failed: {e}")

    def get_current_macro(self):
        """Get the current macro data"""
        macros = self.app.custom_macros_data.get("macros", [])
        if 0 <= self.app.active_macro_index < len(macros):
            return macros[self.app.active_macro_index]
        return {"name": "Macro 1", "hotkey": "", "speed": 1.0, "events": []}

    def load_current_macro_to_ui(self):
        """Load current macro data into UI"""
        macro = self.get_current_macro()
        if not hasattr(self.app, 'macro_name_var'):
            return
        self.app.macro_name_var.set(macro.get("name", ""))
        self.app.macro_hotkey_var.set(macro.get("hotkey", ""))
        speed = macro.get("speed", 1.0)
        self.app.macro_speed_var.set(speed)
        if hasattr(self.app, 'macro_speed_label'):
            self.app.macro_speed_label.configure(text=f"{speed:.1f}x")
        self.app.macro_keep_timing_var.set(macro.get("keep_timing", False))
        self.app.macro_repeat_var.set(macro.get("repeat", False))
        self.app.macro_repeat_times_var.set(str(macro.get("repeat_times", 1)))
        self.app.macro_repeat_infinite_var.set(macro.get("repeat_infinite", False))
        self.app.macro_repeat_delay_var.set(str(macro.get("repeat_delay", 0)))
        if self.app.macro_repeat_infinite_var.get():
            self.app.macro_repeat_times_entry.configure(state='disabled')
        else:
            self.app.macro_repeat_times_entry.configure(state='normal')
        events = macro.get("events", [])
        if events:
            self.app.macro_status_var.set(f"{len(events)} events recorded")
        else:
            self.app.macro_status_var.set("Ctrl+Enter to record")

    def save_current_macro_from_ui(self):
        """Save UI data to current macro"""
        if not hasattr(self.app, 'macro_name_var'):
            return
        macros = self.app.custom_macros_data.get("macros", [])
        if 0 <= self.app.active_macro_index < len(macros):
            macros[self.app.active_macro_index]["name"] = self.app.macro_name_var.get()
            macros[self.app.active_macro_index]["hotkey"] = self.app.macro_hotkey_var.get()
            macros[self.app.active_macro_index]["speed"] = self.app.macro_speed_var.get()
            macros[self.app.active_macro_index]["keep_timing"] = self.app.macro_keep_timing_var.get()
            macros[self.app.active_macro_index]["repeat"] = self.app.macro_repeat_var.get()
            macros[self.app.active_macro_index]["repeat_times"] = int(self.app.macro_repeat_times_var.get() or 1)
            macros[self.app.active_macro_index]["repeat_infinite"] = self.app.macro_repeat_infinite_var.get()
            macros[self.app.active_macro_index]["repeat_delay"] = float(self.app.macro_repeat_delay_var.get() or 0)
            save_custom_macros(self.app.custom_macros_data)

    def on_macro_name_change(self):
        """Called when macro name is changed"""
        self.save_current_macro_from_ui()
        self.build_macro_tabs()

    def on_macro_speed_change(self, value):
        """Called when speed slider changes"""
        speed = float(value)
        speed = round(speed, 1)
        self.app.macro_speed_var.set(speed)
        if hasattr(self.app, 'macro_speed_label'):
            self.app.macro_speed_label.configure(text=f"{speed:.1f}x")
        self.save_current_macro_from_ui()

    def on_macro_keep_timing_change(self):
        """Called when keep timing checkbox changes"""
        self.save_current_macro_from_ui()

    def on_macro_repeat_change(self):
        """Called when repeat checkbox changes"""
        self.save_current_macro_from_ui()

    def on_macro_infinite_change(self):
        """Called when infinite repeat checkbox changes"""
        if self.app.macro_repeat_infinite_var.get():
            self.app.macro_repeat_times_entry.configure(state='disabled')
        else:
            self.app.macro_repeat_times_entry.configure(state='normal')
        self.save_current_macro_from_ui()

    def validate_repeat_times(self, event=None):
        """Validate repeat times is integer only"""
        val = self.app.macro_repeat_times_var.get()
        cleaned = ''.join(c for c in val if c.isdigit())
        if cleaned != val:
            self.app.macro_repeat_times_var.set(cleaned)
        if cleaned == '':
            self.app.macro_repeat_times_var.set('1')
        self.save_current_macro_from_ui()

    def validate_repeat_delay(self, event=None):
        """Validate repeat delay is number only"""
        val = self.app.macro_repeat_delay_var.get()
        cleaned = ''
        has_dot = False
        for c in val:
            if c.isdigit():
                cleaned += c
            elif c == '.' and not has_dot:
                cleaned += c
                has_dot = True
        if cleaned != val:
            self.app.macro_repeat_delay_var.set(cleaned)
        self.save_current_macro_from_ui()

    def toggle_macro_play(self):
        """Toggle macro play/stop"""
        if getattr(self.app, '_macro_stop', True) == False:
            self.app._macro_stop = True
            self.app.macro_play_btn.configure(text="Play")
            self.app.macro_status_var.set("Stopped")
        else:
            self.play_custom_macro()

    def start_recording_macro_hotkey(self):
        """Start recording a hotkey for the current macro"""
        self.app._recording_macro_hotkey = True
        self.app.macro_hk_btn.configure(text="...")
        self.app.macro_hotkey_var.set("Press key...")
        self.app.root.bind("<KeyPress>", self.on_macro_hotkey_press)
        self.app.root.focus_force()

    def on_macro_hotkey_press(self, event):
        """Handle hotkey press during macro hotkey recording"""
        if not getattr(self.app, '_recording_macro_hotkey', False):
            return

        key = event.keysym.lower()
        if key in ('escape', 'esc'):
            self.app.macro_hotkey_var.set(self.get_current_macro().get("hotkey", ""))
            self.app.macro_hk_btn.configure(text="Set")
            self.app._recording_macro_hotkey = False
            self.app.root.unbind("<KeyPress>")
            return

        parts = []
        if event.state & 0x4:
            parts.append('ctrl')
        if event.state & 0x8:
            parts.append('alt')
        if event.state & 0x1:
            parts.append('shift')

        tkinter_to_keyboard = {
            'next': 'page down', 'prior': 'page up', 'escape': 'esc', 'return': 'enter',
            'control_l': 'ctrl', 'control_r': 'ctrl', 'alt_l': 'alt', 'alt_r': 'alt',
            'shift_l': 'shift', 'shift_r': 'shift', 'space': 'space', 'tab': 'tab',
            'backspace': 'backspace', 'minus': '-', 'plus': '+', 'equal': '=',
        }
        mapped_key = tkinter_to_keyboard.get(key, key)

        modifier_keys = ['ctrl', 'alt', 'shift', 'control_l', 'control_r', 'alt_l', 'alt_r', 'shift_l', 'shift_r']
        if key not in modifier_keys:
            parts.append(mapped_key)
            hotkey_str = '+'.join(parts)
            self.app.macro_hotkey_var.set(hotkey_str)
            self.app.macro_hk_btn.configure(text="Set")
            self.app._recording_macro_hotkey = False
            self.app.root.unbind("<KeyPress>")
            self.save_current_macro_from_ui()
            self.app.register_hotkeys()
            print(f"[MACRO HOTKEY] Registered: '{hotkey_str}'")

    def start_custom_macro_recording(self):
        """Record a custom macro - Ctrl+Enter to start/stop"""
        self.app.macro_record_btn.configure(text="Ctrl+Enter...")
        self.app.macro_status_var.set("Press Ctrl+Enter to start")
        self.app.show_overlay("Press Ctrl+Enter to START", force=True)

        self.app._custom_macro_recording = []
        self.app._custom_macro_recording_active = False
        self.app._custom_macro_keys_held = set()
        self.app._ctrl_held = False
        self.app._macro_rec_start_time = None

        def on_click(x, y, button, pressed):
            if not self.app._custom_macro_recording_active:
                return
            btn_name = str(button).replace('Button.', '')
            timestamp = (time.perf_counter() - self.app._macro_rec_start_time) * 1000
            event = {'type': 'click', 'x': x, 'y': y, 'button': btn_name, 'down': pressed, 'time': timestamp}
            self.app._custom_macro_recording.append(event)
            action = "down" if pressed else "up"
            print(f"[MACRO REC] {btn_name} {action} at ({x}, {y}) @ {timestamp:.0f}ms")

        def on_key_press(key):
            if key in (kb.Key.ctrl, kb.Key.ctrl_l, kb.Key.ctrl_r):
                self.app._ctrl_held = True
                return

            if key == kb.Key.enter and self.app._ctrl_held:
                if not self.app._custom_macro_recording_active:
                    self.app._custom_macro_recording_active = True
                    self.app._custom_macro_keys_held.clear()
                    self.app._custom_macro_recording = []
                    self.app._macro_rec_start_time = time.perf_counter()
                    self.app.root.after(0, lambda: self.app.macro_record_btn.configure(text="Recording..."))
                    self.app.root.after(0, lambda: self.app.macro_status_var.set("Recording... Ctrl+Enter to stop"))
                    self.app.root.after(0, lambda: self.app.show_overlay("Recording... Ctrl+Enter to stop", force=True))
                else:
                    mouse_listener.stop()
                    keyboard_listener.stop()
                    self.app._custom_macro_recording_active = False
                    self.save_custom_macro_recording()
                    return False
                return

            if not self.app._custom_macro_recording_active:
                return

            try:
                key_name = key.char if hasattr(key, 'char') and key.char else str(key).replace('Key.', '')
            except:
                key_name = str(key).replace('Key.', '')

            if key_name in self.app._custom_macro_keys_held:
                return
            self.app._custom_macro_keys_held.add(key_name)

            timestamp = (time.perf_counter() - self.app._macro_rec_start_time) * 1000
            event = {'type': 'key', 'key': key_name, 'down': True, 'time': timestamp}
            self.app._custom_macro_recording.append(event)
            print(f"[MACRO REC] key {key_name} down @ {timestamp:.0f}ms")

        def on_key_release(key):
            if key in (kb.Key.ctrl, kb.Key.ctrl_l, kb.Key.ctrl_r):
                self.app._ctrl_held = False
                return

            if not self.app._custom_macro_recording_active:
                return

            if key == kb.Key.enter:
                return

            try:
                key_name = key.char if hasattr(key, 'char') and key.char else str(key).replace('Key.', '')
            except:
                key_name = str(key).replace('Key.', '')

            self.app._custom_macro_keys_held.discard(key_name)

            timestamp = (time.perf_counter() - self.app._macro_rec_start_time) * 1000
            event = {'type': 'key', 'key': key_name, 'down': False, 'time': timestamp}
            self.app._custom_macro_recording.append(event)
            print(f"[MACRO REC] key {key_name} up @ {timestamp:.0f}ms")

        mouse_listener = mouse.Listener(on_click=on_click)
        keyboard_listener = kb.Listener(on_press=on_key_press, on_release=on_key_release)
        mouse_listener.start()
        keyboard_listener.start()

    def save_custom_macro_recording(self):
        """Save the recording to current macro"""
        if len(self.app._custom_macro_recording) < 2:
            self.app.macro_status_var.set("Recording too short")
            self.app.macro_record_btn.configure(text="Record")
            self.app.show_overlay("Recording cancelled - too short", force=True)
            return

        macros = self.app.custom_macros_data.get("macros", [])
        if 0 <= self.app.active_macro_index < len(macros):
            macros[self.app.active_macro_index]["events"] = self.app._custom_macro_recording
            save_custom_macros(self.app.custom_macros_data)

        num_events = len(self.app._custom_macro_recording)
        self.app.macro_status_var.set(f"Recorded: {num_events} events")
        self.app.macro_record_btn.configure(text="Record")
        self.app.show_overlay(f"Saved {num_events} events", force=True)
        print(f"[MACRO REC] Saved {num_events} events")

    def play_custom_macro(self, macro_index=None):
        """Play back a custom macro with speed adjustment and repeat"""
        if macro_index is None:
            macro_index = self.app.active_macro_index

        macros = self.app.custom_macros_data.get("macros", [])
        if not (0 <= macro_index < len(macros)):
            return

        macro = macros[macro_index]
        recording = macro.get("events", [])
        speed = macro.get("speed", 1.0)
        keep_timing = macro.get("keep_timing", False)
        do_repeat = macro.get("repeat", False)
        repeat_times = macro.get("repeat_times", 1)
        repeat_infinite = macro.get("repeat_infinite", False)
        repeat_delay = macro.get("repeat_delay", 0)

        if not recording:
            self.app.show_overlay("No recording to play", force=True)
            return

        self.app._macro_stop = False

        def on_esc():
            if not self.app._macro_stop:
                self.app._macro_stop = True
                self.app.root.after(0, lambda: self.app.macro_play_btn.configure(text="Play"))
                self.app.root.after(0, lambda: self.app.macro_status_var.set("Cancelled"))
                self.app.root.after(0, lambda: self.app.show_overlay("Macro cancelled", force=True))
        self.app._macro_esc_hook = keyboard.on_press_key('esc', lambda e: on_esc(), suppress=False)

        self.app.macro_play_btn.configure(text="Stop")
        self.app.macro_status_var.set("Playing macro... (ESC to cancel)")

        def playback():
            from pynput.mouse import Button
            from pynput.keyboard import Key
            import math
            import random

            button_map = {
                'left': Button.left,
                'right': Button.right,
                'middle': Button.middle,
            }

            special_keys = {
                'shift': Key.shift, 'shift_l': Key.shift_l, 'shift_r': Key.shift_r,
                'ctrl': Key.ctrl, 'ctrl_l': Key.ctrl_l, 'ctrl_r': Key.ctrl_r,
                'alt': Key.alt, 'alt_l': Key.alt_l, 'alt_r': Key.alt_r,
                'space': Key.space, 'enter': Key.enter, 'tab': Key.tab,
                'backspace': Key.backspace, 'delete': Key.delete,
                'esc': Key.esc, 'escape': Key.esc,
                'up': Key.up, 'down': Key.down, 'left': Key.left, 'right': Key.right,
                'home': Key.home, 'end': Key.end, 'page_up': Key.page_up, 'page_down': Key.page_down,
                'caps_lock': Key.caps_lock, 'num_lock': Key.num_lock,
            }

            base_delay = 0.005 / speed

            def smooth_move(target_x, target_y):
                current = pynput_mouse.position
                start_x, start_y = current[0], current[1]
                dx = target_x - start_x
                dy = target_y - start_y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < 5:
                    pynput_mouse.position = (target_x, target_y)
                    return
                steps = max(3, int(10 / speed))
                perp_x = -dy / dist
                perp_y = dx / dist
                curve = random.uniform(-8, 8)
                for i in range(1, steps + 1):
                    p = i / steps
                    arc = math.sin(p * math.pi) * curve
                    if i == steps:
                        pynput_mouse.position = (target_x, target_y)
                    else:
                        pynput_mouse.position = (int(start_x + dx*p + perp_x*arc), int(start_y + dy*p + perp_y*arc))
                    time.sleep(base_delay)

            def smooth_drag(target_x, target_y):
                current = pynput_mouse.position
                start_x, start_y = current[0], current[1]
                dx = target_x - start_x
                dy = target_y - start_y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < 5:
                    pynput_mouse.position = (target_x, target_y)
                    return
                steps = max(3, int(10 / speed))
                curve = random.uniform(-6, 6)
                perp_x = -dy / dist
                perp_y = dx / dist
                for i in range(1, steps + 1):
                    p = i / steps
                    arc = math.sin(p * math.pi) * curve
                    if i == steps:
                        pynput_mouse.position = (target_x, target_y)
                    else:
                        pynput_mouse.position = (int(start_x + dx*p + perp_x*arc), int(start_y + dy*p + perp_y*arc))
                    time.sleep(base_delay)

            def run_once():
                buttons_held = {}
                playback_start = time.perf_counter()

                for event in recording:
                    if self.app._macro_stop:
                        return False

                    if keep_timing and 'time' in event:
                        event_time = event['time'] / speed
                        elapsed = (time.perf_counter() - playback_start) * 1000
                        wait_time = event_time - elapsed
                        if wait_time > 0:
                            time.sleep(wait_time / 1000.0)

                    if event['type'] == 'click':
                        x, y = event['x'], event['y']
                        button = button_map.get(event['button'], Button.left)
                        btn_name = event['button']

                        if event['down']:
                            smooth_move(x, y)
                            if not keep_timing:
                                time.sleep(base_delay * 2)
                            pynput_mouse.press(button)
                            buttons_held[btn_name] = (x, y)
                            if not keep_timing:
                                time.sleep(base_delay * 4)
                        else:
                            if btn_name in buttons_held:
                                press_pos = buttons_held[btn_name]
                                dist = ((x - press_pos[0])**2 + (y - press_pos[1])**2) ** 0.5
                                if dist > 50:
                                    smooth_drag(x, y)
                                del buttons_held[btn_name]
                            pynput_mouse.release(button)

                    elif event['type'] == 'key':
                        key_name = event['key']
                        is_press = event['down']
                        key_lower = key_name.lower()

                        if key_lower in special_keys:
                            key = special_keys[key_lower]
                            if is_press:
                                pynput_keyboard.press(key)
                            else:
                                pynput_keyboard.release(key)
                        elif len(key_name) == 1:
                            if is_press:
                                pynput_keyboard.press(key_name)
                            else:
                                pynput_keyboard.release(key_name)
                return True

            if do_repeat:
                iteration = 0
                while True:
                    if self.app._macro_stop:
                        break
                    iteration += 1
                    self.app.root.after(0, lambda i=iteration: self.app.macro_status_var.set(f"Playing... #{i}"))
                    if not run_once():
                        break
                    if not repeat_infinite and iteration >= repeat_times:
                        break
                    if repeat_delay > 0:
                        time.sleep(repeat_delay)
            else:
                run_once()

            if hasattr(self.app, '_macro_esc_hook'):
                try:
                    keyboard.unhook(self.app._macro_esc_hook)
                except:
                    pass
            self.app.root.after(0, lambda: self.app.macro_play_btn.configure(text="Play"))
            if not self.app._macro_stop:
                self.app.root.after(0, lambda: self.app.macro_status_var.set("Playback complete"))
                self.app.root.after(0, lambda: self.app.show_overlay("Macro done", force=True))
            self.app._macro_stop = False

        threading.Thread(target=playback, daemon=True).start()
    
    def build_macro_tabs(self):
        """Build macro tab buttons - placeholder, actual implementation may be in UI builder"""
        if hasattr(self.app, '_build_macro_tabs'):
            self.app._build_macro_tabs()

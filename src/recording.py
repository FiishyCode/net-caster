import keyboard
from pynput import mouse
from config import save_config

class RecordingManager:
    """Manages all recording functionality - tightly coupled to app instance"""
    
    def __init__(self, app):
        self.app = app
    
    def start_recording_mine(self):
        """Record keybind for mine"""
        self.app._recording_previous_value = self.app.mine_hotkey_var.get()
        self.app.recording_mine = True
        self.app.recording_triggernade = False
        self.app.recording_dc_both = False
        self.app.recording_dc_outbound = False
        self.app.recording_dc_inbound = False
        self.app.recording_tamper = False
        self.app.mine_record_btn.configure(text="...")
        self.app.mine_hotkey_var.set("Press key...")
        self.app.root.bind("<KeyPress>", self.app.on_key_press)
        self.app.root.focus_force()
    
    def start_recording_mine_drag(self):
        """Wrapper to start mine drag action recording"""
        self.app.start_mine_drag_recording()
    
    def start_recording_snap(self):
        """Record keybind for snaphook"""
        self.app._recording_previous_value = self.app.snap_hotkey_var.get()
        self.app.recording_snap = True
        self.app.recording_mine = False
        self.app.recording_triggernade = False
        self.app.recording_dc_both = False
        self.app.recording_dc_outbound = False
        self.app.recording_dc_inbound = False
        self.app.recording_tamper = False
        self.app.snap_record_btn.configure(text="...")
        self.app.snap_hotkey_var.set("Press key...")
        self.app.root.bind("<KeyPress>", self.app.on_key_press)
        self.app.root.focus_force()
    
    def start_recording_snap_drag(self):
        """Record drag path for snaphook"""
        self.app.snap_drag_btn.configure(text="Recording...")
        self.app.show_overlay("DRAG item to target location", force=True)
        self.app._snap_drag_started = False

        listener_ref = [None]

        def on_click(x, y, button, pressed):
            if pressed and button == mouse.Button.left:
                if not self.app._snap_drag_started:
                    self.app.snap_drag_start = (x, y)
                    self.app._snap_drag_started = True
                    print(f"[SNAPHOOK] Drag start: {x}, {y}")
                    self.app.root.after(0, lambda: self.app.show_overlay("Release at target location!", force=True))
                    return True
            elif not pressed and button == mouse.Button.left:
                if self.app._snap_drag_started:
                    self.app.snap_drag_end = (x, y)
                    print(f"[SNAPHOOK] Drag end: {x}, {y}")
                    
                    self.app.config["snap_drag_start"] = list(self.app.snap_drag_start)
                    self.app.config["snap_drag_end"] = list(self.app.snap_drag_end)
                    save_config(self.app.config)
                    
                    self.app.root.after(0, lambda: self.app.snap_drag_btn.configure(text="Action"))
                    self.app.root.after(0, lambda: self.app._update_all_indicators())
                    self.app.root.after(0, lambda: self.app.show_overlay("Snaphook drag recorded!", force=True))
                    return False
            return True

        def on_esc():
            if listener_ref[0]:
                listener_ref[0].stop()
            self.app.root.after(0, lambda: self.app.snap_drag_btn.configure(text="Action"))
            self.app.root.after(0, lambda: self.app.show_overlay("Cancelled", force=True))
            self.app.stop_all_macros()

        listener = mouse.Listener(on_click=on_click)
        listener_ref[0] = listener
        listener.start()
        keyboard.on_press_key('esc', lambda e: on_esc(), suppress=False)

    def start_recording_keycard(self):
        """Record keybind for keycard"""
        self.app._recording_previous_value = self.app.keycard_hotkey_var.get()
        self.app.recording_keycard = True
        self.app.recording_mine = False
        self.app.recording_triggernade = False
        self.app.recording_snap = False
        self.app.recording_dc_both = False
        self.app.recording_dc_outbound = False
        self.app.recording_dc_inbound = False
        self.app.recording_tamper = False
        self.app.keycard_record_btn.configure(text="...")
        self.app.keycard_hotkey_var.set("Press key...")
        self.app.root.bind("<KeyPress>", self.app.on_key_press)
        self.app.root.focus_force()
    
    def start_recording_keycard_drag(self):
        """Record keycard drag: from inventory to drop location"""
        self.app.keycard_drag_btn.configure(text="Recording...")
        self.app.show_overlay("DRAG keycard from inventory to ground", force=True)
        self.app._keycard_drag_started = False

        listener_ref = [None]

        def on_click(x, y, button, pressed):
            if pressed and button == mouse.Button.left:
                if not self.app._keycard_drag_started:
                    self.app.keycard_drag_start = (x, y)
                    self.app._keycard_drag_started = True
                    print(f"[KEYCARD] Drag start (keycard position): {x}, {y}")
                    self.app.root.after(0, lambda: self.app.show_overlay("Release at drop location!", force=True))
                    return True
            elif not pressed and button == mouse.Button.left:
                if self.app._keycard_drag_started:
                    self.app.keycard_drag_end = (x, y)
                    print(f"[KEYCARD] Drag end (drop location): {x}, {y}")
                    
                    self.app.config["keycard_drag_start"] = list(self.app.keycard_drag_start)
                    self.app.config["keycard_drag_end"] = list(self.app.keycard_drag_end)
                    save_config(self.app.config)
                    
                    self.app.root.after(0, lambda: self.app.keycard_drag_btn.configure(text="Action"))
                    self.app.root.after(0, lambda: self.app._update_all_indicators())
                    self.app.root.after(0, lambda: self.app.show_overlay("Keycard drag recorded!", force=True))
                    return False
            return True

        def on_esc():
            if listener_ref[0]:
                listener_ref[0].stop()
            self.app.root.after(0, lambda: self.app.keycard_drag_btn.configure(text="Action"))
            self.app.root.after(0, lambda: self.app.show_overlay("Cancelled", force=True))
            self.app.stop_all_macros()

        listener = mouse.Listener(on_click=on_click)
        listener_ref[0] = listener
        listener.start()
        keyboard.on_press_key('esc', lambda e: on_esc(), suppress=False)

    def start_recording_triggernade(self):
        """Record keybind for triggernade"""
        self.app._recording_previous_value = self.app.triggernade_hotkey_var.get()
        self.app.recording_triggernade = True
        self.app.recording_mine = False
        self.app.recording_snap = False
        self.app.recording_keycard = False
        self.app.recording_dc_both = False
        self.app.recording_dc_outbound = False
        self.app.recording_dc_inbound = False
        self.app.recording_tamper = False
        self.app.triggernade_record_btn.configure(text="...")
        self.app.triggernade_hotkey_var.set("Press key...")
        self.app.root.bind("<KeyPress>", self.app.on_key_press)
        self.app.root.focus_force()
    
    def start_recording_triggernade_drag(self):
        """Start recording triggernade drag positions"""
        self.app.start_trig_drag_recording()
    
    def start_recording_dc_both(self):
        """Start recording hotkey for DC both"""
        self.app._recording_previous_value = self.app.dc_both_hotkey_var.get()
        self.app.recording_dc_both = True
        self.app.recording_dc_outbound = False
        self.app.recording_dc_inbound = False
        self.app.recording_tamper = False
        self.app.recording_triggernade = False
        self.app.recording_mine = False
        self.app.dc_both_record_btn.configure(text="...")
        self.app.dc_both_hotkey_var.set("...")
        self.app.root.bind("<KeyPress>", self.app.on_key_press)
        self.app.root.focus_force()

    def start_recording_dc_outbound(self):
        """Start recording hotkey for DC outbound"""
        self.app._recording_previous_value = self.app.dc_outbound_hotkey_var.get()
        self.app.recording_dc_outbound = True
        self.app.recording_dc_both = False
        self.app.recording_dc_inbound = False
        self.app.recording_tamper = False
        self.app.recording_triggernade = False
        self.app.recording_mine = False
        self.app.dc_outbound_record_btn.configure(text="...")
        self.app.dc_outbound_hotkey_var.set("...")
        self.app.root.bind("<KeyPress>", self.app.on_key_press)
        self.app.root.focus_force()

    def start_recording_dc_inbound(self):
        """Start recording hotkey for DC inbound"""
        self.app._recording_previous_value = self.app.dc_inbound_hotkey_var.get()
        self.app.recording_dc_inbound = True
        self.app.recording_dc_both = False
        self.app.recording_dc_outbound = False
        self.app.recording_tamper = False
        self.app.recording_triggernade = False
        self.app.recording_mine = False
        self.app.dc_inbound_record_btn.configure(text="...")
        self.app.dc_inbound_hotkey_var.set("...")
        self.app.root.bind("<KeyPress>", self.app.on_key_press)
        self.app.root.focus_force()

    def start_recording_tamper(self):
        """Start recording hotkey for Tamper"""
        self.app._recording_previous_value = self.app.tamper_hotkey_var.get()
        self.app.recording_tamper = True
        self.app.recording_dc_both = False
        self.app.recording_dc_outbound = False
        self.app.recording_dc_inbound = False
        self.app.recording_triggernade = False
        self.app.recording_mine = False
        self.app.tamper_record_btn.configure(text="...")
        self.app.tamper_hotkey_var.set("...")
        self.app.root.bind("<KeyPress>", self.app.on_key_press)
        self.app.root.focus_force()

    def start_recording_stop(self):
        """Stop All is always ESC - recording disabled"""
        print("[DEBUG] Stop All hotkey is fixed to ESC and cannot be changed")
        return
    
    def start_mine_drag_recording(self):
        """Record mine drag path - drag item to ground"""
        import time
        from pynput import mouse
        from config import save_config
        
        self.app.mine_drag_btn.configure(text="Recording...")
        self.app.show_overlay("DRAG item to ground", force=True)
        self.app._mine_drag_started = False
        self.app._mine_drag_start_time = None

        def on_click(x, y, button, pressed):
            if button != mouse.Button.left:
                return

            if pressed:
                self.app._mine_drag_start_temp = (x, y)
                self.app._mine_drag_start_time = time.time()
                self.app._mine_drag_started = True
                self.app.root.after(0, lambda: self.app.show_overlay("Now RELEASE...", force=True))
            elif self.app._mine_drag_started:
                duration_ms = (time.time() - self.app._mine_drag_start_time) * 1000
                dx = x - self.app._mine_drag_start_temp[0]
                dy = y - self.app._mine_drag_start_temp[1]
                distance = (dx*dx + dy*dy) ** 0.5

                if duration_ms < 20 or distance < 50:
                    self.app._mine_drag_started = False
                    self.app.root.after(0, lambda: self.app.show_overlay("DRAG item to ground", force=True))
                    return

                self.app.mine_slot_pos = self.app._mine_drag_start_temp
                self.app.mine_drop_pos = (x, y)
                self.app.config["mine_slot_pos"] = list(self.app.mine_slot_pos)
                self.app.config["mine_drop_pos"] = list(self.app.mine_drop_pos)
                self.app.save_settings()
                self.app.mine_drag_var.set(f"Slot:{list(self.app.mine_slot_pos)} Drop:{list(self.app.mine_drop_pos)}")
                self.app.root.after(0, lambda: self.app.mine_drag_btn.configure(text="Record"))
                self.app.root.after(0, lambda: self.app.show_overlay("Drag recorded!", force=True))
                return False

        listener = mouse.Listener(on_click=on_click)
        listener.start()
    
    def start_trig_drag_recording(self):
        """Record triggernade drag path - drag item to ground"""
        import time
        import keyboard
        from pynput import mouse
        from config import save_config
        
        self.app.trig_drag_btn.configure(text="Recording...")
        self.app.show_overlay("DRAG item to ground", force=True)
        self.app._trig_drag_started = False
        self.app._trig_drag_start_time = None

        listener_ref = [None]
        esc_hook_ref = [None]

        def on_click(x, y, button, pressed):
            if button != mouse.Button.left:
                return

            if pressed:
                self.app._trig_drag_start_temp = (x, y)
                self.app._trig_drag_start_time = time.time()
                self.app._trig_drag_started = True
                self.app.root.after(0, lambda: self.app.show_overlay("Now RELEASE...", force=True))
            elif self.app._trig_drag_started:
                duration_ms = (time.time() - self.app._trig_drag_start_time) * 1000
                dx = x - self.app._trig_drag_start_temp[0]
                dy = y - self.app._trig_drag_start_temp[1]
                distance = (dx*dx + dy*dy) ** 0.5

                if duration_ms < 20 or distance < 50:
                    self.app._trig_drag_started = False
                    self.app.root.after(0, lambda: self.app.show_overlay("DRAG item to ground", force=True))
                    return

                self.app.trig_drag_start = self.app._trig_drag_start_temp
                self.app.trig_drag_end = (x, y)
                self.app.config["trig_drag_start"] = list(self.app.trig_drag_start)
                self.app.config["trig_drag_end"] = list(self.app.trig_drag_end)
                save_config(self.app.config)
                self.app.trig_drag_var.set(f"{self.app.trig_drag_start} → {self.app.trig_drag_end}")
                self.app.root.after(0, lambda: self.app.trig_drag_btn.configure(text="Record"))
                self.app.root.after(0, lambda: self.app._update_all_indicators())
                self.app.root.after(0, lambda: self.app.show_overlay("Recorded!", force=True))
                print(f"[TRIG] Drag: {self.app.trig_drag_start} → {self.app.trig_drag_end}")
                if esc_hook_ref[0]:
                    try:
                        keyboard.unhook(esc_hook_ref[0])
                    except:
                        pass
                return False

        listener_ref[0] = mouse.Listener(on_click=on_click)
        listener_ref[0].start()

        def on_esc():
            self.app._drag_recording_cancelled = True
            if listener_ref[0]:
                listener_ref[0].stop()
            self.app.root.after(0, lambda: self.app.trig_drag_btn.configure(text="Record"))
            self.app.root.after(0, lambda: self.app.show_overlay("Cancelled", force=True))
            self.app.stop_all_macros()
            if esc_hook_ref[0]:
                try:
                    keyboard.unhook(esc_hook_ref[0])
                except:
                    pass

        esc_hook_ref[0] = keyboard.on_press_key('esc', lambda e: on_esc(), suppress=False)
    
    def start_quickdrop_pos_recording(self):
        """Record quick drop positions - right-click starts, left-click captures drop position"""
        from pynput import mouse
        from config import save_config
        
        self.app.quickdrop_pos_btn.configure(text="Right-click...")
        self.app.show_overlay("RIGHT-CLICK on item", force=True)
        self.app._quickdrop_rclick_pos = None

        def on_click(x, y, button, pressed):
            if not pressed:
                return

            if button == mouse.Button.right and self.app._quickdrop_rclick_pos is None:
                self.app._quickdrop_rclick_pos = (x, y)
                self.app.root.after(0, lambda: self.app.quickdrop_pos_btn.configure(text="Left-click..."))
                self.app.root.after(0, lambda: self.app.show_overlay("LEFT-CLICK 'Drop to Ground'", force=True))
                print(f"[QUICKDROP] Right-click at {x}, {y}")

            elif button == mouse.Button.left and self.app._quickdrop_rclick_pos is not None:
                self.app.quickdrop_rclick_pos = self.app._quickdrop_rclick_pos
                self.app.quickdrop_lclick_pos = (x, y)
                self.app.config["quickdrop_rclick_pos"] = list(self.app.quickdrop_rclick_pos)
                self.app.config["quickdrop_lclick_pos"] = list(self.app.quickdrop_lclick_pos)
                save_config(self.app.config)
                self.app.quickdrop_pos_var.set(f"R:{list(self.app.quickdrop_rclick_pos)} L:{list(self.app.quickdrop_lclick_pos)}")
                self.app.root.after(0, lambda: self.app.quickdrop_pos_btn.configure(text="Record Pos"))
                self.app.root.after(0, lambda: self.app.show_overlay("Recorded!", force=True))
                print(f"[QUICKDROP] Left-click at {x}, {y}")
                print(f"[QUICKDROP] Positions: R:{self.app.quickdrop_rclick_pos} L:{self.app.quickdrop_lclick_pos}")
                return False

        listener = mouse.Listener(on_click=on_click)
        listener.start()
    
    def start_drag_recording(self):
        """Start recording drag coordinates - 10 sec countdown, then waits for mouse down/up"""
        if self.app.recording_drag:
            return

        self.app.recording_drag = True
        self.app.drag_record_btn.configure(text="10...")
        self.app.drag_label_var.set("Get ready...")
        self._drag_countdown(10)
    
    def _drag_countdown(self, seconds_left):
        """Countdown before starting drag recording"""
        if not self.app.recording_drag:
            return

        if seconds_left > 0:
            self.app.drag_record_btn.configure(text=f"{seconds_left}...")
            self.app.show_overlay(f"Drag recording in {seconds_left}...", force=True)
            self.app.root.after(1000, lambda: self._drag_countdown(seconds_left - 1))
        else:
            self._start_drag_listener()
    
    def _start_drag_listener(self):
        """Actually start the mouse listener for drag recording"""
        from pynput import mouse
        from config import save_config
        
        self.app.drag_record_btn.configure(text="DRAG NOW")
        self.app.drag_label_var.set("Click and drag item!")
        self.app.show_overlay("DRAG NOW!", force=True)

        drag_start_pos = [None, None]

        def on_click(x, y, button, pressed):
            if button != mouse.Button.left:
                return

            if pressed:
                drag_start_pos[0] = x
                drag_start_pos[1] = y
                self.app.root.after(0, lambda: self.app.drag_label_var.set(f"Start: ({x},{y}) - Release..."))
                self.app.root.after(0, lambda: self.app.show_overlay(f"Start: ({x},{y}) - Release...", force=True))
            else:
                if drag_start_pos[0] is not None:
                    self.app.drag_start = (drag_start_pos[0], drag_start_pos[1])
                    self.app.drag_end = (x, y)

                    self.app.root.after(0, lambda: self.app.drag_label_var.set(
                        f"({self.app.drag_start[0]},{self.app.drag_start[1]}) → ({self.app.drag_end[0]},{self.app.drag_end[1]})"
                    ))
                    self.app.root.after(0, lambda: self.app.drag_record_btn.configure(text="Record Drag"))

                    self.app.config["drag_start"] = list(self.app.drag_start)
                    self.app.config["drag_end"] = list(self.app.drag_end)
                    save_config(self.app.config)

                    print(f"[DRAG] Recorded: {self.app.drag_start} → {self.app.drag_end}")
                    self.app.root.after(0, lambda: self.app.show_overlay(f"Drag saved!", force=True))

                    self.app.recording_drag = False
                    return False

        self.app.drag_mouse_listener = mouse.Listener(on_click=on_click)
        self.app.drag_mouse_listener.start()
    
    def start_slot_recording(self):
        """Record drop position - click where the item slot is"""
        self.app.slot_record_btn.configure(text="3...")
        self._slot_countdown(3)
    
    def _slot_countdown(self, seconds_left):
        if seconds_left > 0:
            self.app.slot_record_btn.configure(text=f"{seconds_left}...")
            self.app.show_overlay(f"Click slot in {seconds_left}...", force=True)
            self.app.root.after(1000, lambda: self._slot_countdown(seconds_left - 1))
        else:
            self._start_slot_listener()
    
    def _start_slot_listener(self):
        """Listen for click to record drop position"""
        from pynput import mouse
        from config import save_config
        
        self.app.slot_record_btn.configure(text="CLICK!")
        self.app.show_overlay("CLICK ON SLOT!", force=True)

        def on_click(x, y, button, pressed):
            if button == mouse.Button.left and pressed:
                self.app.drag_start = (x, y)

                self.app.config["drop_position"] = [x, y]
                save_config(self.app.config)

                self.app.root.after(0, lambda: self.app.slot_pos_var.set(f"({x}, {y})"))
                self.app.root.after(0, lambda: self.app.slot_record_btn.configure(text="Record"))
                self.app.root.after(0, lambda: self.app.show_overlay(f"Position: ({x}, {y})", force=True))
                print(f"[SLOT] Recorded drop position: ({x}, {y})")
                return False

        listener = mouse.Listener(on_click=on_click)
        listener.start()

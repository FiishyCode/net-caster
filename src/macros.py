import threading
import time
import random
import ctypes
import keyboard
from pynput.keyboard import Key
from pynput.mouse import Button as MouseButton
from utils import pynput_keyboard, pynput_mouse
from packet_control import start_packet_drop, stop_packet_drop

class MacroExecutor:
    """Handles macro execution - tightly coupled to app instance"""
    
    def __init__(self, app):
        self.app = app
    
    def run_triggernade_macro(self):
        """
        Triggernade/Wolfpack macro
        Initial setup runs once, then wolfpack loop repeats if auto-loop enabled
        """
        repeat = self.app.triggernade_repeat_var.get()
        is_disconnected = False
        dc_key = None  # Initialize for finally block

        # Validate positions are recorded
        if not self.app.trig_drag_start or not self.app.trig_drag_end:
            self.app.root.after(0, lambda: self.app.show_overlay("Record drag positions first!", force=True))
            self.app.triggernade_running = False
            self.app.root.after(0, lambda: self.app.triggernade_status_var.set("Ready"))
            self.app.root.after(0, lambda: self.app.triggernade_status_label.configure(foreground="gray"))
            self.app.root.after(0, lambda: self.app.indicator_manager.set_indicator_ready('triggernade'))
            return

        # Validate DC Both hotkey is set if looping is enabled
        if repeat and not self.app.dc_both_hotkey_var.get():
            self.app.root.after(0, lambda: self.app.show_overlay("Set DC Both hotkey to use Wolfpack loop!", force=True))
            self.app.triggernade_running = False
            self.app.root.after(0, lambda: self.app.triggernade_status_var.set("Ready"))
            self.app.root.after(0, lambda: self.app.triggernade_status_label.configure(foreground="gray"))
            self.app.root.after(0, lambda: self.app.indicator_manager.set_indicator_ready('triggernade'))
            return

        print(f"[TRIGGERNADE] Using positions: {self.app.trig_drag_start} → {self.app.trig_drag_end}")

        # Release ALL buttons and keys before starting
        pynput_mouse.release(MouseButton.left)
        pynput_mouse.release(MouseButton.left)
        pynput_mouse.release(MouseButton.right)
        pynput_keyboard.release('e')
        pynput_keyboard.release('q')
        pynput_keyboard.release(Key.tab)

        # Reset throw counter at start
        self.app.root.after(0, lambda: self.app._ensure_overlay().reset_throw_counter())

        # Brief delay so starting hotkey doesn't trigger stop
        time.sleep(0.2)

        try:
            # ===== INITIAL SETUP (runs once) =====
            print(f"\n{'='*50}")
            print(f"INITIAL SETUP")
            print(f"{'='*50}")

            # ===== Left click throw (configurable) =====
            m1_hold = self.app.trig_m1_hold_var.get()
            m2_hold = self.app.trig_m2_hold_var.get()

            pynput_mouse.press(MouseButton.left)
            self.app.vsleep(m1_hold)

            # ===== Right click during throw (configurable) =====
            pynput_mouse.press(MouseButton.right)
            self.app.vsleep(m2_hold)
            pynput_mouse.release(MouseButton.right)
            print(f"Throw (M1:{m1_hold}ms) + M2:{m2_hold}ms")

            pynput_mouse.release(MouseButton.left)
            
            # Increment throw counter
            self.app.root.after(0, lambda: self.app._ensure_overlay().update_throw_counter(increment=True))

            # ===== Delay before disconnect =====
            dc_delay = self.app.trig_dc_delay_var.get()
            if dc_delay > 0:
                self.app.vsleep(dc_delay)

            if self.app.triggernade_stop:
                return

            # ===== Disconnect (outbound only for triggernade) =====
            start_packet_drop(inbound=False)
            is_disconnected = True
            self.app.vsleep(51)
            print(f"Disconnected (outbound only)")

            if self.app.triggernade_stop:
                return

            # ===== TAB to open inventory 51ms =====
            self.app.vsleep(20)
            pynput_keyboard.press(Key.tab)
            self.app.vsleep(301)
            pynput_keyboard.release(Key.tab)
            print(f"Inventory opened")

            if self.app.triggernade_stop:
                return

            # ===== Wait then drop via curved drag =====
            self.app.vsleep(120)
            pynput_mouse.release(MouseButton.left)
            pynput_mouse.position = self.app.trig_drag_start
            self.app.vsleep(30)
            pynput_mouse.press(MouseButton.left)
            self.app.vsleep(50)
            drag_speed = self.app.trig_drag_speed_var.get()
            self.app.curved_drag(self.app.trig_drag_start, self.app.trig_drag_end, steps=25, step_delay=drag_speed)
            pynput_mouse.release(MouseButton.left)
            print(f"Dropped with curved drag")

            if self.app.triggernade_stop:
                return

            # ===== Wait then TAB close =====
            self.app.vsleep(self.app.drag_wait_after)

            pynput_keyboard.press(Key.tab)
            self.app.vsleep(51)
            pynput_keyboard.release(Key.tab)
            print(f"Inventory closed")

            if self.app.triggernade_stop:
                return

            # ===== Reconnect =====
            stop_packet_drop()
            is_disconnected = False
            print(f"Reconnected - Initial setup complete")

            # ===== E spam + clicking to grab the falling object =====
            # Wait for item to start falling before grabbing
            wait_before = self.app.config.get("wait_before_espam", 100)
            self.app.vsleep(wait_before)
            
            # Longer E spam to reliably grab the dropped item
            espam_duration = self.app.config.get("espam_duration", 500)
            print(f"Grabbing falling object (wait:{wait_before}ms, spam:{espam_duration}ms)...")
            
            start_time = time.time()
            while (time.time() - start_time) * 1000 < espam_duration:
                if self.app.triggernade_stop:
                    break
                pynput_keyboard.press('e')
                time.sleep(0.008)
                pynput_keyboard.release('e')
                pynput_mouse.press(MouseButton.left)
                time.sleep(0.020)
                pynput_mouse.release(MouseButton.left)
                time.sleep(0.015)
            
            # If not looping, stop here after single throw
            if not repeat:
                print(f"Single throw complete!")
                return

            print(f"Starting wolfpack loop!")

            # ===== WOLFPACK LOOP SECTION =====
            # Get user's DC Both hotkey and convert to pynput key
            dc_hotkey_str = self.app.dc_both_hotkey_var.get()
            special_keys = {
                'shift': Key.shift, 'ctrl': Key.ctrl, 'alt': Key.alt,
                'space': Key.space, 'enter': Key.enter, 'tab': Key.tab,
                'backspace': Key.backspace, 'delete': Key.delete,
                'esc': Key.esc, 'escape': Key.esc,
                'up': Key.up, 'down': Key.down, 'left': Key.left, 'right': Key.right,
                'home': Key.home, 'end': Key.end, 'page_up': Key.page_up, 'page_down': Key.page_down,
                'insert': Key.insert, 'pause': Key.pause,
                'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
                'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
                'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12,
            }
            dc_key = special_keys.get(dc_hotkey_str.lower(), dc_hotkey_str) if dc_hotkey_str else None

            if not dc_key:
                print("[WOLFPACK] ERROR: No DC Both hotkey configured!")
                return

            print(f"[WOLFPACK] Using DC hotkey: {dc_hotkey_str}")

            # Get timing from UI vars (in ms), convert to seconds
            m1_hold = self.app.wolfpack_m1_hold_var.get() / 1000.0
            m1_gap = self.app.wolfpack_m1_gap_var.get() / 1000.0
            dc_hold = self.app.wolfpack_dc_hold_var.get() / 1000.0
            dc_gap = self.app.wolfpack_dc_gap_var.get() / 1000.0

            print(f"[WOLFPACK] M1: {m1_hold*1000:.0f}ms hold, {m1_gap*1000:.0f}ms gap")
            print(f"[WOLFPACK] DC: {dc_hold*1000:.0f}ms hold, {dc_gap*1000:.0f}ms gap")

            # Continuous click thread
            click_running = [True]
            def click_loop():
                while click_running[0]:
                    pynput_mouse.press(MouseButton.left)
                    time.sleep(m1_hold)
                    pynput_mouse.release(MouseButton.left)
                    time.sleep(m1_gap)

            click_thread = threading.Thread(target=click_loop, daemon=True)
            click_thread.start()

            # Even DC cycle
            dc_cycle_count = 0
            while True:
                pynput_keyboard.press(dc_key)
                is_disconnected = True
                time.sleep(dc_hold)
                pynput_keyboard.release(dc_key)
                is_disconnected = False
                
                # Count every 2 DC cycles (matches actual throw rate better)
                dc_cycle_count += 1
                if dc_cycle_count % 2 == 0:
                    self.app.root.after(0, lambda: self.app._ensure_overlay().update_throw_counter(increment=True))

                if self.app.triggernade_stop:
                    click_running[0] = False
                    # Ensure reconnected - release DC key and force stop packet drop
                    pynput_keyboard.release(dc_key)
                    time.sleep(0.1)
                    stop_packet_drop()
                    is_disconnected = False
                    break

                time.sleep(dc_gap)

        finally:
            # Release ALL buttons and keys
            pynput_mouse.release(MouseButton.left)
            pynput_mouse.release(MouseButton.left)
            pynput_mouse.release(MouseButton.right)
            pynput_keyboard.release('e')
            pynput_keyboard.release('q')
            pynput_keyboard.release(Key.tab)

            # Release DC hotkey if it was set and pressed
            if dc_key is not None:
                try:
                    pynput_keyboard.release(dc_key)
                except Exception:
                    pass

            if is_disconnected:
                stop_packet_drop()
            self.app.triggernade_running = False
            self.app.triggernade_stop = False
            self.app.root.after(0, lambda: self.app.triggernade_status_var.set("Ready"))
            self.app.root.after(0, lambda: self.app.triggernade_status_label.configure(foreground="gray"))
            self.app.root.after(0, lambda: self.app.indicator_manager.set_indicator_ready('triggernade'))
            self.app.root.after(0, lambda: self.app.show_overlay("Wolfpack stopped."))
    
    def run_mine_macro(self):
        """
        Mine dupe macro:
        1. M1 hold (place mine - configurable cook time)
        2. TAB to open inventory + Disconnect almost together
        3. Drag item to drop
        4. TAB close inventory
        5. Reconnect
        6. Click to pick up
        """
        repeat = self.app.mine_repeat_var.get()
        is_disconnected = False
        cycle = 0

        print(f"[MINE] Using drag: {self.app.mine_drag_start} → {self.app.mine_drag_end}")

        # Release all buttons before starting
        pynput_mouse.release(MouseButton.left)
        pynput_mouse.release(MouseButton.right)
        pynput_keyboard.release(Key.tab)

        hotkey = self.app.mine_hotkey_var.get()
        time.sleep(0.2)

        try:
            while True:
                if self.app.mine_stop:
                    print("[MINE] Stop detected at cycle start")
                    break
                if hotkey and keyboard.is_pressed(hotkey):
                    print("[MINE] Hotkey pressed - stopping")
                    self.app.mine_stop = True
                    break

                cycle += 1
                print(f"\n{'='*50}")
                print(f"MINE CYCLE {cycle}")
                print(f"{'='*50}")

                # Read all timing values ONCE at cycle start
                cook_time = self.app.mine_cook_var.get()
                dc_delay = self.app.mine_dc_delay_var.get()
                click_delay = self.app.mine_click_delay_var.get()
                dupe_click_hold = self.app.mine_pickup_hold_var.get()
                e_delay = self.app.mine_e_delay_var.get()
                loop_delay = self.app.mine_loop_delay_var.get()
                tab_hold = self.app.mine_tab_hold_var.get()
                close_reconnect = self.app.mine_close_reconnect_var.get()
                pre_close = self.app.mine_pre_close_var.get()
                print(f"[{cycle}] Timings: cook={cook_time}, dc_delay={dc_delay}, click_delay={click_delay}, dupe_hold={dupe_click_hold}")

                # Clean state
                pynput_mouse.release(MouseButton.left)
                self.app.vsleep(50)

                # 1. M1 PRESS (start cooking mine)
                print(f"[{cycle}] M1 press - cooking for {cook_time}ms...")
                pynput_mouse.press(MouseButton.left)

                # 2. Cook time: hold M1 to cook the mine
                self.app.vsleep(cook_time)
                
                # 3. Release M1 FIRST so server registers placement
                pynput_mouse.release(MouseButton.left)
                print(f"[{cycle}] M1 release - mine placed after {cook_time}ms cook")
                
                # 4. Small delay to ensure mine placement registered
                self.app.vsleep(80)
                
                # 5. TAB press to open inventory
                pynput_keyboard.press(Key.tab)
                print(f"[{cycle}] TAB press - opening inventory")

                # 6. DC delay: wait before DC (inventory opening)
                self.app.vsleep(dc_delay)
                start_packet_drop(inbound=False)
                is_disconnected = True
                print(f"[{cycle}] DC started after {dc_delay}ms")

                # 7. TAB release shortly after DC
                self.app.vsleep(24)
                pynput_keyboard.release(Key.tab)
                print(f"[{cycle}] TAB release")

                if self.app.mine_stop:
                    break

                # 6. Start drag (with variance)
                self.app.vsleep(200 + random.randint(0, 100))  # 200-300ms wait
                pynput_mouse.position = self.app.mine_drag_start
                self.app.vsleep(30 + random.randint(0, 20))
                pynput_mouse.press(MouseButton.left)

                # 7. Drag with varied speed
                drag_speed = self.app.mine_drag_speed_var.get()
                varied_speed = drag_speed + random.randint(-2, 2)  # Vary speed slightly
                self.app.curved_drag(self.app.mine_drag_start, self.app.mine_drag_end, steps=25, step_delay=max(3, varied_speed))
                pynput_mouse.release(MouseButton.left)
                print(f"[{cycle}] Drag complete")

                if self.app.mine_stop:
                    break

                # 8. TAB close after drag
                self.app.vsleep(pre_close)
                pynput_keyboard.press(Key.tab)
                self.app.vsleep(tab_hold)
                pynput_keyboard.release(Key.tab)
                print(f"[{cycle}] Inventory closed (pre_close={pre_close}, tab_hold={tab_hold})")

                if self.app.mine_stop:
                    break

                # 9. Wait then RECONNECT
                self.app.vsleep(close_reconnect)
                stop_packet_drop()
                is_disconnected = False
                print(f"[{cycle}] Reconnected")

                # 10. Wait then M1 click (uses click_delay slider)
                time.sleep(click_delay / 1000.0)
                dupe_click_hold = self.app.mine_pickup_hold_var.get()
                pynput_mouse.press(MouseButton.left)
                print(f"[{cycle}] M1 press after {click_delay}ms (holding {dupe_click_hold}ms)")

                # 11. Hold for dupe - use direct sleep, no variance/interruption
                time.sleep(dupe_click_hold / 1000.0)
                pynput_mouse.release(MouseButton.left)
                print(f"[{cycle}] M1 release after {dupe_click_hold}ms hold")
                print(f"[{cycle}] CYCLE DONE")

                if not repeat:
                    print(f"[{cycle}] Single cycle done")
                    break

                if self.app.mine_stop:
                    break

                # ===== LOOP ONLY: Pause, then E to pick up, then Q to swap =====
                self.app.vsleep(e_delay)

                # Single E press to pick up
                pynput_keyboard.press('e')
                self.app.vsleep(50)
                pynput_keyboard.release('e')
                print(f"[{cycle}] E pressed to pick up")

                if self.app.mine_stop:
                    break

                # Mouse nudge FIRST to avoid mines stacking
                if self.app.mine_nudge_var.get():
                    nudge_px = self.app.mine_nudge_px_var.get()
                    class MOUSEINPUT(ctypes.Structure):
                        _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long), ("mouseData", ctypes.c_ulong),
                                    ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]
                    class INPUT(ctypes.Structure):
                        _fields_ = [("type", ctypes.c_ulong), ("mi", MOUSEINPUT)]
                    MOUSEEVENTF_MOVE = 0x0001
                    inp = INPUT(type=0, mi=MOUSEINPUT(dx=nudge_px, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_MOVE, time=0, dwExtraInfo=None))
                    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
                    print(f"[{cycle}] Nudged mouse {nudge_px}px right")

                # Q to swap back to mine in quick use
                self.app.vsleep(100)
                if self.app.mine_reselect_var.get():
                    q_mode = self.app.mine_q_mode_var.get()
                    if q_mode == "radial":
                        # Use direction-based radial selection
                        self.app._play_mine_q_radial()
                        print(f"[{cycle}] Q radial reselect ({self.app.mine_q_direction_var.get()})")
                    else:
                        # Simple Q tap
                        pynput_keyboard.press('q')
                        self.app.vsleep(50)
                        pynput_keyboard.release('q')
                        print(f"[{cycle}] Q tap to reselect")

                # Wait before next cycle (scales with variance slider - more extreme)
                loop_delay_ms = self.app.mine_loop_delay_var.get()
                variance_pct = self.app.timing_variance_var.get()
                extra_loop_var = random.uniform(0, variance_pct * 10) if variance_pct > 0 else 0
                self.app.vsleep(loop_delay_ms + extra_loop_var)

        finally:
            pynput_mouse.release(MouseButton.left)
            pynput_keyboard.release(Key.tab)
            if is_disconnected:
                stop_packet_drop()
            self.app.mine_running = False
            self.app.mine_stop = False
            self.app.root.after(0, lambda: self.app.mine_status_var.set("Ready"))
            self.app.root.after(0, lambda: self.app.mine_status_label.configure(foreground="gray"))
            self.app.root.after(0, lambda: self.app.indicator_manager.set_indicator_ready('mine'))
            self.app.root.after(0, lambda: self.app.show_overlay("Mine Dupe stopped."))
    
    def execute_snap_action(self):
        """Execute the snaphook action: open inv, drag item, close inv - optimized for speed"""
        from pynput.mouse import Controller as MouseController, Button as MouseButton
        from pynput.keyboard import Controller as KeyboardController, Key
        import time
        
        pynput_mouse = MouseController()
        pynput_keyboard = KeyboardController()
        
        try:
            print(f"[SNAPHOOK] Opening inventory...")
            # Open inventory (TAB key)
            pynput_keyboard.press(Key.tab)
            time.sleep(0.02)
            pynput_keyboard.release(Key.tab)
            time.sleep(0.08)  # Minimal wait for inventory
            
            print(f"[SNAPHOOK] Dragging from {self.app.snap_drag_start} to {self.app.snap_drag_end}")
            # Move to start position
            pynput_mouse.position = self.app.snap_drag_start
            time.sleep(0.02)
            
            # Press and drag immediately
            pynput_mouse.press(MouseButton.left)
            time.sleep(0.02)
            
            # Fast drag
            self.app.curved_drag(self.app.snap_drag_start, self.app.snap_drag_end, steps=12, step_delay=3)
            
            # Release after drag completes
            pynput_mouse.release(MouseButton.left)
            time.sleep(0.03)
            
            print(f"[SNAPHOOK] Closing inventory...")
            # Close inventory (TAB key)
            pynput_keyboard.press(Key.tab)
            time.sleep(0.02)
            pynput_keyboard.release(Key.tab)
            
            print(f"[SNAPHOOK] Complete!")
            self.app.root.after(0, lambda: self.app.indicator_manager.set_indicator_ready('snaphook'))
            self.app.root.after(0, lambda: self.app.show_overlay("Snaphook complete!", force=True))
        except Exception as e:
            print(f"[SNAPHOOK] Error: {e}")
            self.app.root.after(0, lambda: self.app.indicator_manager.set_indicator_ready('snaphook'))
            self.app.root.after(0, lambda: self.app.show_overlay(f"Snaphook error: {e}", force=True))
    
    def _key_to_pynput(self, key_str):
        """Convert key string (e.g. 'e', 'f1') to pynput key for press/release"""
        if not key_str:
            return None
        key_str = key_str.lower().strip()
        special = {
            'shift': Key.shift, 'ctrl': Key.ctrl, 'alt': Key.alt,
            'space': Key.space, 'enter': Key.enter, 'tab': Key.tab,
            'esc': Key.esc, 'escape': Key.esc,
            'up': Key.up, 'down': Key.down, 'left': Key.left, 'right': Key.right,
            'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
            'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
            'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12,
        }
        return special.get(key_str, key_str)
    
    def execute_keycard_action(self):
        """Execute the keycard action: press interact, wait, DC, open inv, drag key to drop, close inv, reconnect"""
        is_disconnected = False
        
        # Validate positions
        if not self.app.keycard_drag_start or not self.app.keycard_drag_end:
            self.app.root.after(0, lambda: self.app.show_overlay("Record keycard drag positions first!", force=True))
            self.app.root.after(0, lambda: self.app.indicator_manager.set_indicator_ready('keycard'))
            return
        
        interact_key_str = self.app.config.get("keycard_interact_key", "e") or "e"
        interact_delay_ms = int(self.app.config.get("keycard_interact_delay", 200))
        interact_key = self._key_to_pynput(interact_key_str)
        
        try:
            # 1. Press interact button (in-game key to interact with items)
            print(f"[KEYCARD] Pressing interact key: {interact_key_str}")
            if interact_key:
                pynput_keyboard.press(interact_key)
                self.app.vsleep(50)
                pynput_keyboard.release(interact_key)
            
            # 2. Wait 0.2s (or configured delay) then DC
            self.app.vsleep(interact_delay_ms)
            
            print(f"[KEYCARD] Disconnecting...")
            start_packet_drop(inbound=False, outbound=True)
            is_disconnected = True
            self.app.vsleep(100)
            
            print(f"[KEYCARD] Opening inventory...")
            pynput_keyboard.press(Key.tab)
            self.app.vsleep(50)
            pynput_keyboard.release(Key.tab)
            self.app.vsleep(350)
            
            print(f"[KEYCARD] Dragging key from {self.app.keycard_drag_start} to {self.app.keycard_drag_end}")
            # Move to key position (same controller curved_drag uses)
            pynput_mouse.position = self.app.keycard_drag_start
            self.app.vsleep(80)
            
            # Press and hold left, then drag (curved_drag moves pynput_mouse)
            pynput_mouse.press(MouseButton.left)
            self.app.vsleep(60)
            self.app.curved_drag(self.app.keycard_drag_start, self.app.keycard_drag_end, steps=25, step_delay=5)
            pynput_mouse.release(MouseButton.left)
            self.app.vsleep(80)
            
            print(f"[KEYCARD] Closing inventory...")
            pynput_keyboard.press(Key.tab)
            self.app.vsleep(50)
            pynput_keyboard.release(Key.tab)
            self.app.vsleep(150)
            
            print(f"[KEYCARD] Reconnecting...")
            stop_packet_drop()
            is_disconnected = False
            self.app.vsleep(100)
            
            print(f"[KEYCARD] Complete!")
            self.app.root.after(0, lambda: self.app.indicator_manager.set_indicator_ready('keycard'))
            self.app.root.after(0, lambda: self.app.show_overlay("Keycard dupe complete!", force=True))
        except Exception as e:
            print(f"[KEYCARD] Error: {e}")
            if is_disconnected:
                stop_packet_drop()
            self.app.root.after(0, lambda: self.app.indicator_manager.set_indicator_ready('keycard'))
            self.app.root.after(0, lambda: self.app.show_overlay(f"Keycard error: {e}", force=True))

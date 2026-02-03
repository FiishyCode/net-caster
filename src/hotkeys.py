import keyboard
from pynput.keyboard import Key

class HotkeyManager:
    """Manages hotkey registration and handling"""
    
    def __init__(self, app):
        self.app = app
        self.registered_hotkeys = {}
    
    def register_all(self):
        """Register all hotkeys"""
        # Clear ALL hooks first to prevent ghost hotkeys
        try:
            keyboard.unhook_all()
            print("[HOTKEY] Cleared all previous hotkeys and hooks")
        except Exception as e:
            print(f"[HOTKEY] Error clearing hotkeys: {e}")

        # Reset all registered hotkey references
        self.app.triggernade_hotkey_registered = None
        self.app.escape_hotkey_registered = None
        self.app.dc_both_hotkey_registered = None
        self.app.dc_outbound_hotkey_registered = None
        self.app.dc_inbound_hotkey_registered = None
        self.app.tamper_hotkey_registered = None
        self.app.mine_hotkey_registered = None
        self.app.snap_hotkey_registered = None
        self.app.keycard_hotkey_registered = None
        self.app.trig_rerecord_registered = None
        self.app.mine_rerecord_registered = None

        # Register main action hotkeys
        self._register_triggernade()
        self._register_mine()
        self._register_snap()
        self._register_keycard()
        self._register_disconnect_hotkeys()
        self._register_stop_all()
        self._register_rerecord_hotkeys()
    
    def _register_triggernade(self):
        """Register triggernade hotkey"""
        trig_hk = self.app.triggernade_hotkey_var.get()
        if trig_hk and trig_hk != "Press key...":
            try:
                self.app.triggernade_hotkey_registered = keyboard.add_hotkey(
                    trig_hk, self.app.on_triggernade_hotkey, suppress=False
                )
                print(f"[HOTKEY] Triggernade registered OK: '{trig_hk}'")
            except Exception as e:
                print(f"[HOTKEY] FAILED triggernade '{trig_hk}': {e}")
    
    def _register_mine(self):
        """Register mine hotkey"""
        mine_hk = self.app.mine_hotkey_var.get()
        if mine_hk and mine_hk != "Press key...":
            try:
                self.app.mine_hotkey_registered = keyboard.add_hotkey(
                    mine_hk, self.app.on_mine_hotkey, suppress=False
                )
                print(f"[HOTKEY] Mine registered OK: '{mine_hk}'")
            except Exception as e:
                print(f"[HOTKEY] FAILED mine '{mine_hk}': {e}")
    
    def _register_snap(self):
        """Register snaphook hotkey"""
        snap_hk = self.app.snap_hotkey_var.get()
        if snap_hk and snap_hk != "Press key...":
            try:
                self.app.snap_hotkey_registered = keyboard.add_hotkey(
                    snap_hk, self.app.on_snap_hotkey, suppress=False
                )
                print(f"[HOTKEY] Snaphook registered OK: '{snap_hk}'")
            except Exception as e:
                print(f"[HOTKEY] FAILED snaphook '{snap_hk}': {e}")
    
    def _register_keycard(self):
        """Register keycard hotkey"""
        keycard_hk = self.app.keycard_hotkey_var.get()
        if keycard_hk and keycard_hk != "Press key...":
            try:
                self.app.keycard_hotkey_registered = keyboard.add_hotkey(
                    keycard_hk, self.app.on_keycard_hotkey, suppress=False
                )
                print(f"[HOTKEY] Keycard registered OK: '{keycard_hk}'")
            except Exception as e:
                print(f"[HOTKEY] FAILED keycard '{keycard_hk}': {e}")
    
    def _register_disconnect_hotkeys(self):
        """Register disconnect hotkeys"""
        # DC Both
        dc_both_hk = self.app.dc_both_hotkey_var.get()
        if dc_both_hk and dc_both_hk not in ["Press key...", "..."]:
            try:
                self.app.dc_both_hotkey_registered = keyboard.on_press_key(
                    dc_both_hk, lambda e: self.app.toggle_dc_both(), suppress=False
                )
                print(f"[HOTKEY] DC Both registered OK: '{dc_both_hk}'")
            except Exception as e:
                print(f"[HOTKEY] FAILED dc_both '{dc_both_hk}': {e}")
        
        # DC Outbound
        dc_outbound_hk = self.app.dc_outbound_hotkey_var.get()
        if dc_outbound_hk and dc_outbound_hk not in ["Press key...", "..."]:
            try:
                self.app.dc_outbound_hotkey_registered = keyboard.on_press_key(
                    dc_outbound_hk, lambda e: self.app.toggle_dc_outbound(), suppress=False
                )
                print(f"[HOTKEY] DC Outbound registered OK: '{dc_outbound_hk}'")
            except Exception as e:
                print(f"[HOTKEY] FAILED dc_outbound '{dc_outbound_hk}': {e}")
        
        # DC Inbound
        dc_inbound_hk = self.app.dc_inbound_hotkey_var.get()
        if dc_inbound_hk and dc_inbound_hk not in ["Press key...", "..."]:
            try:
                self.app.dc_inbound_hotkey_registered = keyboard.on_press_key(
                    dc_inbound_hk, lambda e: self.app.toggle_dc_inbound(), suppress=False
                )
                print(f"[HOTKEY] DC Inbound registered OK: '{dc_inbound_hk}'")
            except Exception as e:
                print(f"[HOTKEY] FAILED dc_inbound '{dc_inbound_hk}': {e}")
        
        # Tamper
        tamper_hk = self.app.tamper_hotkey_var.get()
        if tamper_hk and tamper_hk not in ["Press key...", "..."]:
            try:
                self.app.tamper_hotkey_registered = keyboard.on_press_key(
                    tamper_hk, lambda e: self.app.toggle_tamper(), suppress=False
                )
                print(f"[HOTKEY] Tamper registered OK: '{tamper_hk}'")
            except Exception as e:
                print(f"[HOTKEY] FAILED tamper '{tamper_hk}': {e}")
    
    def _register_stop_all(self):
        """Register stop all hotkey (always ESC)"""
        try:
            self.app.escape_hotkey_registered = keyboard.on_press_key(
                'esc', lambda e: self.app.stop_all_macros(), suppress=False
            )
            print("[HOTKEY] Stop All (ESC) registered")
        except Exception as e:
            print(f"[HOTKEY] FAILED stop all: {e}")
    
    def _register_rerecord_hotkeys(self):
        """Register Alt+hotkey re-record shortcuts"""
        # Triggernade: Alt+hotkey = re-record position
        trig_hk = self.app.triggernade_hotkey_var.get()
        if trig_hk and trig_hk != "Press key...":
            try:
                alt_trig_hk = f"alt+{trig_hk}" if not trig_hk.startswith("alt+") else trig_hk
                self.app.trig_rerecord_registered = keyboard.add_hotkey(
                    alt_trig_hk, self.app.start_trig_drag_recording, suppress=False
                )
                print(f"[HOTKEY] Triggernade re-record registered: '{alt_trig_hk}'")
            except Exception as e:
                print(f"[HOTKEY] FAILED triggernade re-record '{alt_trig_hk}': {e}")

        # Mine: Alt+hotkey = re-record position
        mine_hk = self.app.mine_hotkey_var.get()
        if mine_hk and mine_hk != "Press key...":
            try:
                alt_mine_hk = f"alt+{mine_hk}" if not mine_hk.startswith("alt+") else mine_hk
                self.app.mine_rerecord_registered = keyboard.add_hotkey(
                    alt_mine_hk, self.app.start_mine_drag_recording, suppress=False
                )
                print(f"[HOTKEY] Mine re-record registered: '{alt_mine_hk}'")
            except Exception as e:
                print(f"[HOTKEY] FAILED mine re-record '{alt_mine_hk}': {e}")

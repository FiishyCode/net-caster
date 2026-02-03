"""Reset manager - handles resetting settings to defaults"""
import tkinter.messagebox as mb
from config import save_config


class ResetManager:
    """Manages resetting settings to defaults"""
    
    def __init__(self, app_instance):
        self.app = app_instance
    
    def reset_triggernade_defaults(self):
        """Reset all triggernade timing parameters to defaults"""
        # Get defaults but preserve positions
        defaults = self.app.settings_manager.groups.get("triggernade", {}).copy()
        if self.app.trig_slot_pos:
            defaults["trig_slot_pos"] = list(self.app.trig_slot_pos)
        if self.app.trig_drop_pos:
            defaults["trig_drop_pos"] = list(self.app.trig_drop_pos)
        if self.app.trig_drag_start:
            defaults["trig_drag_start"] = list(self.app.trig_drag_start)
        if self.app.trig_drag_end:
            defaults["trig_drag_end"] = list(self.app.trig_drag_end)
        self.app.settings_manager.set_settings("triggernade", defaults)
        print("[RESET] Triggernade parameters reset to defaults (positions preserved)")
    
    def reset_mine_defaults(self):
        """Reset all mine dupe timing parameters to defaults"""
        defaults = self.app.settings_manager.groups.get("mine", {}).copy()
        self.app.settings_manager.set_settings("mine", defaults)
        if hasattr(self.app, 'mine_drag_var') and self.app.mine_drag_start and self.app.mine_drag_end:
            self.app.mine_drag_var.set(f"{self.app.mine_drag_start} → {self.app.mine_drag_end}")
        print("[RESET] Mine dupe parameters reset to defaults")
    
    def reset_all_settings(self):
        """Reset ALL settings including hotkeys and recordings to factory defaults"""
        if not mb.askyesno("Reset All Settings", "This will reset EVERYTHING including:\n\n• All hotkeys\n• All timing settings\n• All recorded positions\n• Drag drop preference\n\nAre you sure?"):
            return

        # Clear config file completely
        self.app.config = {}
        save_config(self.app.config)

        # Reset ALL hotkeys
        print("[RESET] Clearing all hotkeys...")
        self.app.triggernade_hotkey_var.set("")
        self.app.dc_both_hotkey_var.set("")
        self.app.dc_outbound_hotkey_var.set("")
        self.app.dc_inbound_hotkey_var.set("")
        self.app.tamper_hotkey_var.set("")
        self.app.mine_hotkey_var.set("")
        self.app.stop_hotkey_var.set("esc")  # Default is esc
        print("[RESET] All hotkeys cleared")

        # Reset checkboxes
        print("[RESET] Resetting checkboxes...")
        self.app.show_overlay_var.set(True)
        self.app.stay_on_top_var.set(False)
        self.app.triggernade_repeat_var.set(True)

        # Reset ALL timing sliders and positions
        print("[RESET] Resetting all timing defaults...")
        self.reset_triggernade_defaults()
        self.reset_mine_defaults()

        # Re-register hotkeys (will be empty now)
        self.app.register_hotkeys()

        print("[RESET] ALL settings reset to factory defaults")
        self.app.show_overlay("All settings reset!")

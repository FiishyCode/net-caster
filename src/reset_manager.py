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
        if hasattr(self.app, 'snap_hotkey_var'):
            self.app.snap_hotkey_var.set("")
        if hasattr(self.app, 'keycard_hotkey_var'):
            self.app.keycard_hotkey_var.set("")
        if hasattr(self.app, 'keycard_interact_key_var'):
            self.app.keycard_interact_key_var.set("e")
        if hasattr(self.app, 'stop_hotkey_var'):
            self.app.stop_hotkey_var.set("esc")  # Default is esc
        print("[RESET] All hotkeys cleared")

        # Reset checkboxes
        print("[RESET] Resetting checkboxes...")
        self.app.show_overlay_var.set(True)
        self.app.stay_on_top_var.set(False)
        self.app.triggernade_repeat_var.set(True)

        # Clear all drag positions (these affect the "recorded" indicators)
        print("[RESET] Clearing all drag positions...")
        if hasattr(self.app, 'snap_drag_start'):
            self.app.snap_drag_start = None
        if hasattr(self.app, 'snap_drag_end'):
            self.app.snap_drag_end = None
        if hasattr(self.app, 'keycard_drag_start'):
            self.app.keycard_drag_start = None
        if hasattr(self.app, 'keycard_drag_end'):
            self.app.keycard_drag_end = None
        if hasattr(self.app, 'trig_drag_start'):
            self.app.trig_drag_start = None
        if hasattr(self.app, 'trig_drag_end'):
            self.app.trig_drag_end = None
        if hasattr(self.app, 'trig_slot_pos'):
            self.app.trig_slot_pos = None
        if hasattr(self.app, 'trig_drop_pos'):
            self.app.trig_drop_pos = None
        if hasattr(self.app, 'mine_drag_start'):
            self.app.mine_drag_start = None
        if hasattr(self.app, 'mine_drag_end'):
            self.app.mine_drag_end = None
        if hasattr(self.app, 'mine_slot_pos'):
            self.app.mine_slot_pos = None
        if hasattr(self.app, 'mine_drop_pos'):
            self.app.mine_drop_pos = None

        # Reset ALL timing sliders and positions (without preserving positions)
        print("[RESET] Resetting all timing defaults...")
        # Reset triggernade without preserving positions
        defaults = self.app.settings_manager.groups.get("triggernade", {}).copy()
        defaults["trig_slot_pos"] = None
        defaults["trig_drop_pos"] = None
        defaults["trig_drag_start"] = None
        defaults["trig_drag_end"] = None
        self.app.settings_manager.set_settings("triggernade", defaults)
        
        # Reset mine without preserving positions
        mine_defaults = self.app.settings_manager.groups.get("mine", {}).copy()
        mine_defaults["mine_slot_pos"] = None
        mine_defaults["mine_drop_pos"] = None
        mine_defaults["mine_drag_start"] = None
        mine_defaults["mine_drag_end"] = None
        self.app.settings_manager.set_settings("mine", mine_defaults)
        
        # Clear snaphook and keycard positions
        snap_defaults = self.app.settings_manager.groups.get("snaphook", {}).copy()
        snap_defaults["snap_drag_start"] = None
        snap_defaults["snap_drag_end"] = None
        self.app.settings_manager.set_settings("snaphook", snap_defaults)
        
        keycard_defaults = self.app.settings_manager.groups.get("keycard", {}).copy()
        keycard_defaults["keycard_interact_key"] = "e"
        keycard_defaults["keycard_interact_delay"] = 200
        keycard_defaults["keycard_drag_start"] = None
        keycard_defaults["keycard_drag_end"] = None
        self.app.settings_manager.set_settings("keycard", keycard_defaults)
        
        # Reset disconnect hotkeys
        disconnect_defaults = self.app.settings_manager.groups.get("disconnect", {}).copy()
        disconnect_defaults["dc_both_hotkey"] = ""
        disconnect_defaults["dc_outbound_hotkey"] = ""
        disconnect_defaults["dc_inbound_hotkey"] = ""
        disconnect_defaults["tamper_hotkey"] = ""
        self.app.settings_manager.set_settings("disconnect", disconnect_defaults)
        
        # Explicitly update config dict with cleared values
        self.app.config["triggernade_hotkey"] = ""
        self.app.config["mine_hotkey"] = ""
        self.app.config["snap_hotkey"] = ""
        self.app.config["keycard_hotkey"] = ""
        self.app.config["keycard_interact_key"] = "e"
        self.app.config["keycard_interact_delay"] = 200
        self.app.config["dc_both_hotkey"] = ""
        self.app.config["dc_outbound_hotkey"] = ""
        self.app.config["dc_inbound_hotkey"] = ""
        self.app.config["tamper_hotkey"] = ""
        self.app.config["trig_drag_start"] = None
        self.app.config["trig_drag_end"] = None
        self.app.config["mine_drag_start"] = None
        self.app.config["mine_drag_end"] = None
        self.app.config["snap_drag_start"] = None
        self.app.config["snap_drag_end"] = None
        self.app.config["keycard_drag_start"] = None
        self.app.config["keycard_drag_end"] = None

        # Save settings first so config is updated
        self.app.save_settings()
        
        # Re-register hotkeys (will be empty now)
        self.app.register_hotkeys()

        # Update indicators without rebuilding UI (safer)
        self.app.indicator_manager.update_all_indicators()
        
        # Force GUI refresh
        self.app.root.update_idletasks()

        print("[RESET] ALL settings reset to factory defaults")
        self.app.show_overlay("All settings reset!")
    
    def reset_preferences_only(self):
        """Reset only appearance and general preferences, preserving all timing settings and hotkeys"""
        if not mb.askyesno("Reset Preferences", "This will reset only preferences:\n\n• Appearance settings (colors, transparency)\n• Window preferences (stay on top, show overlay)\n\nTiming settings and hotkeys will be preserved.\n\nContinue?"):
            return
        
        # Save current timing settings and hotkeys
        timing_groups = ["triggernade", "mine", "snaphook", "keycard", "disconnect"]
        preserved_settings = {}
        for group in timing_groups:
            preserved_settings[group] = self.app.settings_manager.get_settings(group)
        
        # Reset only appearance and general groups
        print("[RESET] Resetting preferences only...")
        self.app.settings_manager.reset_to_defaults("appearance")
        self.app.settings_manager.reset_to_defaults("general")
        
        # Update app.colors dict from config
        bg_color = self.app.config.get("bg_color", "#1e1e1e")
        fg_color = self.app.config.get("fg_color", "#e8f4f8")
        accent_color = self.app.config.get("accent_color", "#00d4ff")
        card_bg_color = self.app.config.get("card_bg_color", "#1a2f4d")
        
        self.app.colors['bg'] = bg_color
        self.app.colors['bg_light'] = self.app.theme_manager.adjust_color(bg_color, 25)
        self.app.colors['bg_lighter'] = self.app.theme_manager.adjust_color(bg_color, 45)
        self.app.colors['text'] = fg_color
        self.app.colors['highlight'] = accent_color
        self.app.colors['bg_card'] = card_bg_color
        
        # Update UI variables
        if hasattr(self.app, 'bg_color_var'):
            self.app.bg_color_var.set(bg_color)
        if hasattr(self.app, 'fg_color_var'):
            self.app.fg_color_var.set(fg_color)
        if hasattr(self.app, 'accent_color_var'):
            self.app.accent_color_var.set(accent_color)
        if hasattr(self.app, 'card_bg_color_var'):
            self.app.card_bg_color_var.set(card_bg_color)
        if hasattr(self.app, 'transparency_var'):
            self.app.transparency_var.set(self.app.config.get("transparency", 100))
            self.app.theme_manager.apply_transparency()
        
        # Restore timing settings and hotkeys
        for group, settings in preserved_settings.items():
            self.app.settings_manager.set_settings(group, settings)
        
        # Rebuild UI to apply theme changes
        current_tab = self.app.notebook.get() if hasattr(self.app, 'notebook') else None
        self.app.ui_builder.build_ui()
        if current_tab and hasattr(self.app, 'notebook'):
            self.app.notebook.set(current_tab)
        
        # Update indicators
        self.app.indicator_manager.update_all_indicators()
        
        print("[RESET] Preferences reset (timings preserved)")
        self.app.show_overlay("Preferences reset!")
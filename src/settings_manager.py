import json
import os
import tkinter as tk
from config import CONFIG_FILE

# Load default settings
DEFAULT_SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "default_settings.json")

def load_default_settings():
    """Load default settings from JSON file"""
    try:
        with open(DEFAULT_SETTINGS_FILE, 'r') as f:
            defaults = json.load(f)
        # Flatten nested structure
        flattened = {}
        for category, settings in defaults.items():
            flattened.update(settings)
        return flattened
    except Exception as e:
        print(f"[SETTINGS] Error loading defaults: {e}")
        return {}

def get_setting_groups():
    """Get settings organized by group"""
    try:
        with open(DEFAULT_SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[SETTINGS] Error loading defaults: {e}")
        return {}

class SettingsManager:
    """Generic settings manager that handles get/set operations"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.defaults = load_default_settings()
        self.groups = get_setting_groups()
    
    def get_settings(self, group_name):
        """Get all settings for a group (e.g., 'triggernade', 'mine')"""
        settings = {}
        group_settings = self.groups.get(group_name, {})
        
        for key in group_settings.keys():
            var_name = f"{key}_var"
            if hasattr(self.app, var_name):
                var = getattr(self.app, var_name)
                settings[key] = var.get()
            elif hasattr(self.app, key):
                # Handle non-var attributes (like positions)
                value = getattr(self.app, key)
                if isinstance(value, tuple):
                    settings[key] = list(value) if value else None
                else:
                    settings[key] = value
        
        return settings
    
    def set_settings(self, group_name, data):
        """Set all settings for a group from a dict"""
        for key, value in data.items():
            var_name = f"{key}_var"
            
            # Handle tkinter variables
            if hasattr(self.app, var_name):
                var = getattr(self.app, var_name)
                var.set(value)
            
            # Handle special cases (positions, buttons, etc.)
            elif key.endswith("_pos") or key.endswith("_start") or key.endswith("_end"):
                if value:
                    setattr(self.app, key, tuple(value))
                    self.app.config[key] = value
                    # Update display vars if they exist
                    if key == "trig_slot_pos" and hasattr(self.app, "trig_drag_var"):
                        if hasattr(self.app, "trig_drop_pos") and self.app.trig_drop_pos:
                            self.app.trig_drag_var.set(
                                f"Slot:{list(self.app.trig_slot_pos)} Drop:{list(self.app.trig_drop_pos)}"
                            )
                    elif key == "mine_slot_pos" and hasattr(self.app, "mine_drag_var"):
                        if hasattr(self.app, "mine_drop_pos") and self.app.mine_drop_pos:
                            self.app.mine_drag_var.set(
                                f"Slot:{list(self.app.mine_slot_pos)} Drop:{list(self.app.mine_drop_pos)}"
                            )
            
            # Handle special button updates
            elif key == "mine_q_direction" and hasattr(self.app, "mine_q_dir_btn"):
                if hasattr(self.app, "mine_q_direction_var"):
                    self.app.mine_q_direction_var.set(value)
                self.app.mine_q_dir_btn.configure(text=value)
            
            # Store in config for persistence
            self.app.config[key] = value
        
        self.app.save_settings()
    
    def get_all_settings(self):
        """Get all settings organized by group"""
        return {
            "triggernade": self.get_settings("triggernade"),
            "mine": self.get_settings("mine"),
            "snaphook": self.get_settings("snaphook"),
            "keycard": self.get_settings("keycard"),
            "disconnect": self.get_settings("disconnect"),
            "general": self.get_settings("general"),
            "appearance": self.get_settings("appearance")
        }
    
    def set_all_settings(self, data):
        """Set all settings from grouped dict"""
        for group_name, settings in data.items():
            if isinstance(settings, dict):
                self.set_settings(group_name, settings)
    
    def reset_to_defaults(self, group_name):
        """Reset a group to default values"""
        defaults = self.groups.get(group_name, {})
        self.set_settings(group_name, defaults)

"""Settings export/import manager - handles exporting and importing settings"""
import json
from tkinter import filedialog


class SettingsExportManager:
    """Manages export and import of settings"""
    
    def __init__(self, app_instance):
        self.app = app_instance
    
    def get_triggernade_settings(self):
        """Get all triggernade-related settings as a dict"""
        return self.app.settings_manager.get_settings("triggernade")
    
    def set_triggernade_settings(self, data):
        """Apply triggernade settings from dict"""
        self.app.settings_manager.set_settings("triggernade", data)
    
    def get_mine_settings(self):
        """Get all mine dupe-related settings as a dict"""
        return self.app.settings_manager.get_settings("mine")
    
    def set_mine_settings(self, data):
        """Apply mine dupe settings from dict"""
        self.app.settings_manager.set_settings("mine", data)
    
    def export_triggernade(self):
        """Export triggernade settings to file"""
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")],
                                            initialfile="triggernade_settings.json")
        if path:
            with open(path, 'w') as f:
                json.dump({"type": "triggernade", **self.get_triggernade_settings()}, f, indent=2)
            print(f"[EXPORT] Triggernade settings saved to {path}")
    
    def import_triggernade(self):
        """Import triggernade settings from file"""
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            with open(path, 'r') as f:
                data = json.load(f)
            self.set_triggernade_settings(data)
            self.app.register_hotkeys()
            print(f"[IMPORT] Triggernade settings loaded from {path}")
    
    def export_mine(self):
        """Export mine dupe settings to file"""
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")],
                                            initialfile="mine_settings.json")
        if path:
            with open(path, 'w') as f:
                json.dump({"type": "mine", **self.get_mine_settings()}, f, indent=2)
            print(f"[EXPORT] Mine settings saved to {path}")
    
    def import_mine(self):
        """Import mine dupe settings from file"""
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            with open(path, 'r') as f:
                data = json.load(f)
            self.set_mine_settings(data)
            self.app.register_hotkeys()
            print(f"[IMPORT] Mine settings loaded from {path}")
    
    def export_all_settings(self):
        """Export all macro settings to a single file"""
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")],
                                            initialfile="all_settings.json")
        if path:
            data = {
                "type": "all",
                **self.app.settings_manager.get_all_settings()
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
                self.app.settings_manager.set_all_settings(data)
            elif data.get("type") == "triggernade":
                self.set_triggernade_settings(data)
            elif data.get("type") == "mine":
                self.set_mine_settings(data)
            else:
                # Try to detect from keys
                if "triggernade_hotkey" in data: self.set_triggernade_settings(data)
                if "mine_hotkey" in data: self.set_mine_settings(data)
            self.app.register_hotkeys()
            print(f"[IMPORT] Settings loaded from {path}")

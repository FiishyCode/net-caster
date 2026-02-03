"""Indicator manager - handles updating UI indicators for recording status"""
import tkinter.ttk as ttk


class IndicatorManager:
    """Manages UI indicators for recording status"""
    
    def __init__(self, app_instance):
        self.app = app_instance
    
    def update_record_button_color(self, button, action_type):
        """Update button color based on recording status - green if recorded, yellow if not"""
        is_recorded = self.app._is_action_recorded(action_type)
        color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
        try:
            # For ttk buttons, configure via style
            style_name = f'{action_type.capitalize()}.Record.TButton'
            style = ttk.Style()
            style.configure(style_name, background=color, foreground='#000000')
            button.configure(style=style_name)
        except:
            pass
    
    def update_all_indicators(self):
        """Update all recording indicators (green if recorded, yellow if not)"""
        try:
            # Update DC Both indicator
            if hasattr(self.app, 'dc_both_indicator'):
                is_recorded = self.app._is_action_recorded('dc_both')
                color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
                if hasattr(self.app.dc_both_indicator, 'configure'):
                    self.app.dc_both_indicator.configure(text_color=color)
                else:
                    self.app.dc_both_indicator.delete('all')
                    self.app.dc_both_indicator.create_oval(2, 2, 10, 10, fill=color, outline='', width=0)
            
            # Update Triggernade keybind indicator
            if hasattr(self.app, 'trig_keybind_indicator'):
                is_recorded = bool(self.app.config.get("triggernade_hotkey", ""))
                color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
                if hasattr(self.app.trig_keybind_indicator, 'configure'):
                    self.app.trig_keybind_indicator.configure(text_color=color)
                else:
                    self.app.trig_keybind_indicator.delete('all')
                    self.app.trig_keybind_indicator.create_oval(2, 2, 10, 10, fill=color, outline='', width=0)
            
            # Update Triggernade action indicator
            if hasattr(self.app, 'trig_indicator'):
                is_recorded = self.app._is_action_recorded('triggernade')
                color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
                if hasattr(self.app.trig_indicator, 'configure'):
                    self.app.trig_indicator.configure(text_color=color)
                else:
                    self.app.trig_indicator.delete('all')
                    self.app.trig_indicator.create_oval(2, 2, 10, 10, fill=color, outline='', width=0)
            
            # Update Mine keybind indicator
            if hasattr(self.app, 'mine_keybind_indicator'):
                is_recorded = bool(self.app.config.get("mine_hotkey", ""))
                color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
                if hasattr(self.app.mine_keybind_indicator, 'configure'):
                    self.app.mine_keybind_indicator.configure(text_color=color)
                else:
                    self.app.mine_keybind_indicator.delete('all')
                    self.app.mine_keybind_indicator.create_oval(2, 2, 10, 10, fill=color, outline='', width=0)
            
            # Update Mine action indicator
            if hasattr(self.app, 'mine_indicator'):
                is_recorded = self.app._is_action_recorded('mine')
                color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
                if hasattr(self.app.mine_indicator, 'configure'):
                    self.app.mine_indicator.configure(text_color=color)
                else:
                    self.app.mine_indicator.delete('all')
                    self.app.mine_indicator.create_oval(2, 2, 10, 10, fill=color, outline='', width=0)
            
            # Update Stop indicator
            if hasattr(self.app, 'stop_indicator'):
                is_recorded = self.app._is_action_recorded('stop')
                color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
                if hasattr(self.app.stop_indicator, 'configure'):
                    self.app.stop_indicator.configure(text_color=color)
                else:
                    self.app.stop_indicator.delete('all')
                    self.app.stop_indicator.create_oval(2, 2, 10, 10, fill=color, outline='', width=0)
            
            # Update Snaphook indicator
            if hasattr(self.app, 'snap_indicator'):
                is_recorded = self.app._is_action_recorded('snaphook')
                color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
                if hasattr(self.app.snap_indicator, 'configure'):
                    self.app.snap_indicator.configure(text_color=color)
                else:
                    self.app.snap_indicator.delete('all')
                    self.app.snap_indicator.create_oval(2, 2, 10, 10, fill=color, outline='', width=0)
            
            # Update Keycard indicator
            if hasattr(self.app, 'keycard_indicator'):
                is_recorded = self.app._is_action_recorded('keycard')
                color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
                if hasattr(self.app.keycard_indicator, 'configure'):
                    self.app.keycard_indicator.configure(text_color=color)
                else:
                    self.app.keycard_indicator.delete('all')
                    self.app.keycard_indicator.create_oval(2, 2, 10, 10, fill=color, outline='', width=0)
        except Exception as e:
            print(f"[ERROR] Failed to update indicators: {e}")

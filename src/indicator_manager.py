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
    
    def set_indicator_running(self, action_type):
        """Set an indicator to 'Running' state with highlight color"""
        indicator_map = {
            'triggernade': 'trig_indicator',
            'mine': 'mine_indicator',
            'snaphook': 'snap_indicator',
            'keycard': 'keycard_indicator',
            'dc_both': 'dc_both_indicator'
        }
        indicator_name = indicator_map.get(action_type)
        if indicator_name and hasattr(self.app, indicator_name):
            indicator = getattr(self.app, indicator_name)
            indicator.configure(text_color=self.app.colors['highlight'], text="Running")
    
    def set_indicator_ready(self, action_type):
        """Reset an indicator to normal state (Ready or Not Set)"""
        indicator_map = {
            'triggernade': 'trig_indicator',
            'mine': 'mine_indicator',
            'snaphook': 'snap_indicator',
            'keycard': 'keycard_indicator',
            'dc_both': 'dc_both_indicator'
        }
        indicator_name = indicator_map.get(action_type)
        if indicator_name and hasattr(self.app, indicator_name):
            indicator = getattr(self.app, indicator_name)
            is_recorded = self.app._is_action_recorded(action_type)
            color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
            text = "Ready" if is_recorded else "Not Set"
            indicator.configure(text_color=color, text=text)
    
    def update_all_indicators(self):
        """Update all recording indicators (shows 'Ready' or 'Not Set' with appropriate color)"""
        try:
            # Update DC Both indicator
            if hasattr(self.app, 'dc_both_indicator'):
                is_recorded = self.app._is_action_recorded('dc_both')
                color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
                text = "Ready" if is_recorded else "Not Set"
                self.app.dc_both_indicator.configure(text_color=color, text=text)
            
            # Update Triggernade indicator
            if hasattr(self.app, 'trig_indicator'):
                is_recorded = self.app._is_action_recorded('triggernade')
                color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
                text = "Ready" if is_recorded else "Not Set"
                self.app.trig_indicator.configure(text_color=color, text=text)
            
            # Update Mine indicator
            if hasattr(self.app, 'mine_indicator'):
                is_recorded = self.app._is_action_recorded('mine')
                color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
                text = "Ready" if is_recorded else "Not Set"
                self.app.mine_indicator.configure(text_color=color, text=text)
            
            # Update Snaphook indicator
            if hasattr(self.app, 'snap_indicator'):
                is_recorded = self.app._is_action_recorded('snaphook')
                color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
                text = "Ready" if is_recorded else "Not Set"
                self.app.snap_indicator.configure(text_color=color, text=text)
            
            # Update Keycard indicator
            if hasattr(self.app, 'keycard_indicator'):
                is_recorded = self.app._is_action_recorded('keycard')
                color = self.app.colors['recorded'] if is_recorded else self.app.colors['not_recorded']
                text = "Ready" if is_recorded else "Not Set"
                self.app.keycard_indicator.configure(text_color=color, text=text)
            
            # Update Interact (keycard interact key) indicator
            if hasattr(self.app, 'keycard_interact_indicator'):
                has_interact = bool(self.app.config.get("keycard_interact_key", ""))
                color = self.app.colors['recorded'] if has_interact else self.app.colors['not_recorded']
                text = "Ready" if has_interact else "Not Set"
                self.app.keycard_interact_indicator.configure(text_color=color, text=text)
        except Exception as e:
            print(f"[ERROR] Failed to update indicators: {e}")

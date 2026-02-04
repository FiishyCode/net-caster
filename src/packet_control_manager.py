"""Packet control manager - handles DC and tamper toggle buttons"""
from packet_control import start_packet_drop, stop_packet_drop, is_dropping, start_packet_tamper, stop_packet_tamper


class PacketControlManager:
    """Manages packet control operations (DC and tamper toggles)"""
    
    def __init__(self, app_instance):
        self.app = app_instance
    
    def reset_dc_buttons(self):
        """Reset all DC buttons to default state"""
        self.app.dc_both_btn.configure(text="DC BOTH", bg=self.app.colors['bg_light'])
        self.app.dc_outbound_btn.configure(text="DC OUTBOUND", bg=self.app.colors['bg_light'])
        self.app.dc_inbound_btn.configure(text="DC INBOUND", bg=self.app.colors['bg_light'])
    
    def toggle_dc_both(self):
        """Toggle disconnect both inbound + outbound"""
        if is_dropping():
            # Reconnect
            stop_packet_drop()
            self.reset_dc_buttons()
            self.app.root.after(0, lambda: self.app.indicator_manager.set_indicator_ready('dc_both'))
            self.app.root.after(0, lambda: self.app.show_overlay("RECONNECTED"))
        else:
            start_packet_drop(outbound=True, inbound=True)
            self.reset_dc_buttons()
            self.app.dc_both_btn.configure(text="RECONNECT", bg=self.app.colors['highlight'])
            self.app.root.after(0, lambda: self.app.indicator_manager.set_indicator_running('dc_both'))
            self.app.root.after(0, lambda: self.app.show_overlay("DC BOTH"))
    
    def toggle_dc_outbound(self):
        """Toggle disconnect outbound only"""
        if is_dropping():
            # Reconnect
            stop_packet_drop()
            self.reset_dc_buttons()
            self.app.root.after(0, lambda: self.app.show_overlay("RECONNECTED"))
        else:
            start_packet_drop(outbound=True, inbound=False)
            self.reset_dc_buttons()
            self.app.dc_outbound_btn.configure(text="RECONNECT", bg=self.app.colors['highlight'])
            self.app.root.after(0, lambda: self.app.show_overlay("DC OUTBOUND"))
    
    def toggle_dc_inbound(self):
        """Toggle disconnect inbound only"""
        if is_dropping():
            # Reconnect
            stop_packet_drop()
            self.reset_dc_buttons()
            self.app.root.after(0, lambda: self.app.show_overlay("RECONNECTED"))
        else:
            start_packet_drop(outbound=False, inbound=True)
            self.reset_dc_buttons()
            self.app.dc_inbound_btn.configure(text="RECONNECT", bg=self.app.colors['highlight'])
            self.app.root.after(0, lambda: self.app.show_overlay("DC INBOUND"))
    
    def toggle_tamper(self):
        """Toggle packet tampering - corrupts packets but still sends them"""
        if self.app.tampering:
            stop_packet_tamper()
            self.app.tamper_btn.configure(text="TAMPER", bg=self.app.colors['bg_light'])
            self.app.tampering = False
            self.app.root.after(0, lambda: self.app.show_overlay("TAMPER OFF"))
        else:
            start_packet_tamper(outbound=True, inbound=True)
            self.app.tamper_btn.configure(text="STOP TAMPER", bg=self.app.colors['warning'])
            self.app.tampering = True
            self.app.root.after(0, lambda: self.app.show_overlay("TAMPER ON"))

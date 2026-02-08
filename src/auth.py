import os
import sys
import json
import subprocess
import requests
import hashlib
import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk

# Cloud Function URL for license verification (bypasses Firestore rules)
VERIFY_LICENSE_URL = "https://us-central1-fiishy.cloudfunctions.net/verifyLicense"

class AuthManager:
    def __init__(self):
        self.auth_file = os.path.join(os.getenv('APPDATA', os.getcwd()), "NetCaster", "auth.json")
        os.makedirs(os.path.dirname(self.auth_file), exist_ok=True)
        self.hwid = self._get_hwid()
        self.session = None

    def _get_hwid(self):
        """Get unique hardware ID for Windows"""
        try:
            cmd = 'wmic csproduct get uuid'
            uuid = str(subprocess.check_output(cmd, shell=True))
            return hashlib.sha256(uuid.encode()).hexdigest()
        except Exception as e:
            # Fallback to computer name + username if wmic fails
            fallback = os.environ.get('COMPUTERNAME', '') + os.environ.get('USERNAME', '')
            return hashlib.sha256(fallback.encode()).hexdigest()

    def verify_license(self, email, license_key):
        """Verify license key via Cloud Function (bypasses Firestore rules)"""
        try:
            payload = {
                "email": email.strip(),
                "licenseKey": license_key.strip(),
                "hwid": self.hwid,
            }
            response = requests.post(
                VERIFY_LICENSE_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=15,
            )
            data = response.json()
            success = data.get("success", False)
            message = data.get("message", "Invalid Email or License Key.")
            return success, message
        except Exception as e:
            print(f"[AUTH] Error: {e}")
            return False, f"Connection error: {str(e)}"

    def save_credentials(self, email, license_key):
        with open(self.auth_file, 'w') as f:
            json.dump({"email": email, "license_key": license_key}, f)

    def load_credentials(self):
        if os.path.exists(self.auth_file):
            try:
                with open(self.auth_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return None

class LoginWindow(ctk.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.auth = AuthManager()
        
        self.title("NetCaster - Login")
        self.geometry("400x500")
        self.resizable(False, False)

        # Set window icon
        try:
            if getattr(sys, 'frozen', False):
                ico_path = os.path.join(sys._MEIPASS, "icon.ico")
                png_path = os.path.join(sys._MEIPASS, "icon.png")
            else:
                src_dir = os.path.dirname(os.path.abspath(__file__))
                icon_dir = os.path.join(os.path.dirname(src_dir), "assets", "icons")
                ico_path = os.path.join(icon_dir, "icon.ico")
                png_path = os.path.join(icon_dir, "icon.png")
            if os.path.exists(ico_path):
                self.iconbitmap(ico_path)
            elif os.path.exists(png_path):
                self._icon_image = tk.PhotoImage(file=png_path)
                self.iconphoto(True, self._icon_image)
        except Exception:
            pass
        
        # Center window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

        self.setup_ui()
        
        # Auto-login if credentials exist
        creds = self.auth.load_credentials()
        if creds:
            self.email_entry.insert(0, creds['email'])
            self.key_entry.insert(0, creds['license_key'])
            # Delay auto-login slightly to show UI
            self.after(500, self.handle_login)

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        
        # Logo/Title
        self.logo_label = ctk.CTkLabel(self, text="NetCaster", font=("Segoe UI", 32, "bold"), text_color="#3b82f6")
        self.logo_label.pack(pady=(50, 10))
        
        self.subtitle_label = ctk.CTkLabel(self, text="Arc Raiders Network Suite", font=("Segoe UI", 14), text_color="#9ca3af")
        self.subtitle_label.pack(pady=(0, 40))

        # Email
        self.email_label = ctk.CTkLabel(self, text="Email Address", font=("Segoe UI", 12, "bold"), text_color="#e4e7eb")
        self.email_label.pack(padx=40, anchor="w")
        self.email_entry = ctk.CTkEntry(self, placeholder_text="Enter your email", width=320, height=45, fg_color="#1a1f2e", border_width=1)
        self.email_entry.pack(pady=(5, 20), padx=40)

        # License Key
        self.key_label = ctk.CTkLabel(self, text="License Key", font=("Segoe UI", 12, "bold"), text_color="#e4e7eb")
        self.key_label.pack(padx=40, anchor="w")
        self.key_entry = ctk.CTkEntry(self, placeholder_text="NC-XXXX-XXXX", width=320, height=45, fg_color="#1a1f2e", border_width=1)
        self.key_entry.pack(pady=(5, 30), padx=40)

        # Login Button
        self.login_btn = ctk.CTkButton(self, text="Verify License", command=self.handle_login, width=320, height=50, font=("Segoe UI", 16, "bold"), fg_color="#3b82f6", hover_color="#2563eb")
        self.login_btn.pack(pady=10, padx=40)

        # Footer
        self.footer_label = ctk.CTkLabel(self, text="Don't have a license? Buy at fiishy.app", font=("Segoe UI", 10), text_color="#6b7280", cursor="hand2")
        self.footer_label.pack(pady=(20, 0))

    def handle_login(self):
        email = self.email_entry.get().strip()
        key = self.key_entry.get().strip()

        if not email or not key:
            messagebox.showwarning("Input Error", "Please provide both email and license key.")
            return

        self.login_btn.configure(text="Verifying...", state="disabled")
        self.update()

        success, message = self.auth.verify_license(email, key)

        if success:
            self.auth.save_credentials(email, key)
            self.destroy()
            self.on_success()
        else:
            messagebox.showerror("Auth Failed", message)
            self.login_btn.configure(text="Verify License", state="normal")

def run_login(on_success):
    ctk.set_appearance_mode("dark")
    app = LoginWindow(on_success)
    app.mainloop()

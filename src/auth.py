import os
import sys
import json
import subprocess
import requests
import hashlib
import customtkinter as ctk
from tkinter import messagebox

# Firebase Configuration (From your website)
FIREBASE_API_KEY = "AIzaSyDnrzO83I49pElBGTtS8nBrcJSbgmXE3hg"
PROJECT_ID = "fiishy"

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
        """Verify license key against Firebase Firestore"""
        try:
            # 1. Sign in the user anonymously or via email if you have that setup
            # For simplicity, we'll use the Firestore REST API directly if rules allow,
            # but ideally you'd use a Firebase Function.
            # Since we want to check if the EMAIL and KEY match, we'll query the users collection.
            
            # NOTE: For security, Firestore rules should only allow reading own doc.
            # Here we are searching for a doc where licenseKey == license_key and email == email.
            
            url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents:runQuery?key={FIREBASE_API_KEY}"
            
            query = {
                "structuredQuery": {
                    "from": [{"collectionId": "users"}],
                    "where": {
                        "compositeFilter": {
                            "op": "AND",
                            "filters": [
                                {
                                    "fieldFilter": {
                                        "field": {"fieldPath": "email"},
                                        "op": "EQUAL",
                                        "value": {"stringValue": email}
                                    }
                                },
                                {
                                    "fieldFilter": {
                                        "field": {"fieldPath": "licenseKey"},
                                        "op": "EQUAL",
                                        "value": {"stringValue": license_key}
                                    }
                                }
                            ]
                        }
                    },
                    "limit": 1
                }
            }

            response = requests.post(url, json=query)
            data = response.json()

            if not data or len(data) == 0 or 'document' not in data[0]:
                return False, "Invalid Email or License Key."

            doc = data[0]['document']
            fields = doc['fields']
            
            purchased = fields.get('purchased', {}).get('booleanValue', False)
            if not purchased:
                return False, "This account has not purchased a license."

            # HWID Check
            stored_hwid = fields.get('hwid', {}).get('stringValue', None)
            doc_id = doc['name'].split('/')[-1]

            if not stored_hwid:
                # First time use: Bind HWID
                self._update_hwid(doc_id, self.hwid)
                return True, "Success! Hardware ID bound to your account."
            elif stored_hwid != self.hwid:
                return False, "License is bound to another computer. Contact support to reset HWID."

            return True, "Welcome back!"

        except Exception as e:
            print(f"[AUTH] Error: {e}")
            return False, f"Connection error: {str(e)}"

    def _update_hwid(self, doc_id, hwid):
        """Update HWID in Firestore"""
        url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/users/{doc_id}?updateMask.fieldPaths=hwid&key={FIREBASE_API_KEY}"
        payload = {
            "fields": {
                "hwid": {"stringValue": hwid}
            }
        }
        requests.patch(url, json=payload)

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

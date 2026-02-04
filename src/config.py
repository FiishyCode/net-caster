import sys
import os
import json
import random
import string
import subprocess

# =============================================================================
# OBFUSCATION FEATURES (opt-in: requires "obfuscate" file next to exe)
# This feature allows runtime name randomization for additional privacy.
# Using exploits always carries risk - use at your own discretion.
# =============================================================================
# Unique build identifier - generated fresh each build by build.py
BUILD_ID = "__BUILD_ID_PLACEHOLDER__"

def _check_obfuscation_enabled():
    """Check if obfuscation is enabled by looking for 'obfuscate' file next to exe"""
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.exists(os.path.join(exe_dir, "obfuscate"))

OBFUSCATION_ENABLED = _check_obfuscation_enabled()

VERSION = "1.0"

# Generate random app name (8-18 chars) if obfuscation enabled, otherwise use default
if OBFUSCATION_ENABLED:
    _name_length = random.randint(8, 18)
    _random_name = ''.join(random.choices(string.ascii_letters, k=_name_length))
    APP_NAME = f"{_random_name} {VERSION}"
else:
    _random_name = "netcaster"
    APP_NAME = f"NetCaster {VERSION}"

def rename_self_and_restart():
    """Rename the running EXE to match the random app name.
    Only runs when obfuscation is enabled and running as frozen exe."""
    if not OBFUSCATION_ENABLED:
        return False

    # Only works for frozen exe, not script
    if not getattr(sys, 'frozen', False):
        return False

    current_exe = sys.executable
    current_dir = os.path.dirname(current_exe)
    marker_file = os.path.join(current_dir, "DELETETOCHANGEID")

    # If marker exists, already renamed - skip
    if os.path.exists(marker_file):
        return False

    # Use the random name generated for APP_NAME
    new_name = f"{_random_name}.exe"
    new_path = os.path.join(current_dir, new_name)

    try:
        import shutil
        # Copy to new name
        shutil.copy2(current_exe, new_path)

        # Create marker file so it won't rename again
        with open(marker_file, 'w') as f:
            f.write(new_name)

        # Launch the new exe
        subprocess.Popen([new_path] + sys.argv[1:])

        print(f"[OBFUS] Created: {new_name}")
        print(f"[OBFUS] Delete 'DELETETOCHANGEID' to generate new name.")

        # Exit this instance
        sys.exit(0)

    except Exception as e:
        print(f"[OBFUS] Rename failed: {e}")
        return False

    return True

CONFIG_FILE = os.path.join(os.environ.get('APPDATA', '.'), "Application", "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

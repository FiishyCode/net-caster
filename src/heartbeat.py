"""
NetCaster heartbeat client.

Sends periodic heartbeats to the admin dashboard so you can see
which users have the app running (Online vs Offline).
Sends an offline signal when the app closes for instant detection.
"""

import atexit
import json
import threading
import time
import urllib.request
import urllib.error

HEARTBEAT_URL = "https://us-central1-fiishy.cloudfunctions.net/reportHeartbeat"
OFFLINE_URL = "https://us-central1-fiishy.cloudfunctions.net/reportOffline"
HEARTBEAT_INTERVAL_SEC = 60
_stop_event = threading.Event()
_current_license_key = None


def _send_heartbeat(license_key: str) -> bool:
    try:
        data = json.dumps({"licenseKey": license_key}).encode("utf-8")
        req = urllib.request.Request(
            HEARTBEAT_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False


def _heartbeat_loop(license_key: str):
    while not _stop_event.is_set():
        _send_heartbeat(license_key)
        _stop_event.wait(HEARTBEAT_INTERVAL_SEC)


def start_heartbeat(license_key: str):
    """Start sending heartbeats in a background thread. Call once at app startup."""
    global _current_license_key
    key = str(license_key or "").strip()
    if not key or not key.startswith("NC"):
        return
    _current_license_key = key
    atexit.register(stop_heartbeat)
    thread = threading.Thread(target=_heartbeat_loop, args=(key,), daemon=True)
    thread.start()


def report_offline():
    """Send offline signal to the server. Call when the app shuts down for instant detection."""
    global _current_license_key
    if not _current_license_key:
        return
    try:
        data = json.dumps({"licenseKey": _current_license_key}).encode("utf-8")
        req = urllib.request.Request(
            OFFLINE_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass
    finally:
        _current_license_key = None


def stop_heartbeat():
    """Stop the heartbeat thread and report offline. Call when the app shuts down."""
    report_offline()
    _stop_event.set()

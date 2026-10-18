"""Normal-user sign-in startup. The installer removes the old elevated task."""
from __future__ import annotations

import logging
import subprocess
import sys
import winreg

log = logging.getLogger("orbit.autostart")
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE = "Orbit"


def available() -> bool:
    return bool(getattr(sys, "frozen", False))


def enabled() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            value, kind = winreg.QueryValueEx(key, VALUE)
        return kind == winreg.REG_SZ and value == subprocess.list2cmdline([sys.executable])
    except OSError:
        return False


def set_enabled(on: bool) -> bool:
    try:
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            if on:
                winreg.SetValueEx(key, VALUE, 0, winreg.REG_SZ, subprocess.list2cmdline([sys.executable]))
            else:
                try:
                    winreg.DeleteValue(key, VALUE)
                except FileNotFoundError:
                    pass
    except OSError:
        log.exception("could not change sign-in startup")
        return False
    log.info("start with Windows: %s", "on" if on else "off")
    return True

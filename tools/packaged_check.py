"""Check the production executable without enabling any developer input."""
import ctypes
import os
import secrets
import subprocess
import sys
import tempfile
import time
from pathlib import Path

exe = Path(sys.argv[1]).resolve()
with tempfile.TemporaryDirectory(prefix="orbit-package-") as scratch:
    root = Path(scratch)
    env = dict(os.environ, LOCALAPPDATA=scratch, APPDATA=str(root / "roam"),
               USERNAME="orbit-test-" + secrets.token_hex(6), QT_QPA_PLATFORM="offscreen")
    rejected = subprocess.run([str(exe), "--dev"], env=env, timeout=40)
    if rejected.returncode == 0:
        raise SystemExit("packaged application accepted developer input")
    if ctypes.windll.shell32.IsUserAnAdmin():
        result = subprocess.run([str(exe), "--no-elevate"], env=env, timeout=40)
        if result.returncode != 1 or (root / "Orbit" / "orbit.log").exists():
            raise SystemExit("packaged application did not refuse elevated startup before user files")
        print("packaged check: PASS (developer input disabled; elevated startup refused)")
    else:
        proc = subprocess.Popen([str(exe), "--debug"], env=env)
        try:
            deadline = time.monotonic() + 40
            log = root / "Orbit" / "orbit.log"
            while time.monotonic() < deadline and proc.poll() is None:
                if log.exists() and "Orbit running" in log.read_text(encoding="utf-8"):
                    print("packaged check: PASS (developer input disabled; normal startup succeeded)")
                    break
                time.sleep(0.2)
            else:
                raise SystemExit("packaged application failed normal startup")
        finally:
            proc.terminate()
            proc.wait(timeout=15)

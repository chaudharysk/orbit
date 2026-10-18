"""Start the real app, inject a double press, confirm the engine handled it.

    python tools/startup_check.py
Uses a temporary data dir so it never touches a running Orbit. Exit 0 on success.
"""
import os
import secrets
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from orbit.platform.dev import send  # noqa: E402

tmp = Path(tempfile.mkdtemp(prefix="orbit-check-"))
token = secrets.token_urlsafe(32)
env = dict(os.environ, LOCALAPPDATA=str(tmp), APPDATA=str(tmp / "roam"), HOME=str(tmp),
           USERNAME=tmp.name, USER=tmp.name, PYTHONUNBUFFERED="1", ORBIT_DEV_TOKEN=token, QT_QPA_PLATFORM="offscreen")
if sys.platform == "win32":
    import ctypes
    if ctypes.windll.shell32.IsUserAnAdmin():
        result = subprocess.run([sys.executable, "-m", "orbit", "--no-elevate"], cwd=ROOT, env=env,
                                capture_output=True, text=True, timeout=30)
        ok = result.returncode == 1 and "without administrator privileges" in result.stderr
        print("startup check:", "PASS (elevated launch rejected)" if ok else "FAIL", result.stderr[-1000:])
        sys.exit(0 if ok else 1)
log_file = tmp / ("Orbit/orbit.log" if sys.platform == "win32" else ".orbit/orbit.log")
proc = subprocess.Popen([sys.executable, "-m", "orbit", "--no-elevate", "--dev", "--debug"],
                        cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def log_text():
    return log_file.read_text(encoding="utf-8", errors="replace") if log_file.exists() else ""


def wait_for(needle, timeout):
    end = time.time() + timeout
    while time.time() < end:
        if needle in log_text():
            return True
        if proc.poll() is not None:
            return False
        time.sleep(0.3)
    return False


ok = wait_for("Orbit running", 40)
if ok:
    send("double", token=token)
    ok = wait_for("double <dev-udp>", 10)
    send("rotate", 1, token=token)
    ok = ok and wait_for("rotate(+1) <dev-udp>", 10)
    send("double", token=token)
    time.sleep(1.5)
alive = proc.poll() is None
proc.terminate()
try:
    out = proc.communicate(timeout=10)[0]
except subprocess.TimeoutExpired:
    proc.kill()
    out = proc.communicate()[0]
print(log_text()[-4000:] or out[-4000:])
print("startup check:", "PASS" if ok and alive else "FAIL", f"(alive={alive})")
sys.exit(0 if ok and alive else 1)

"""Privilege, launcher, and untrusted local input regression tests."""
import secrets
import socket
import sys
import threading
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from orbit.platform.dev import UdpDevSource, decode_event, dev_token


@pytest.mark.parametrize("token", ["", "short", "x" * 129, "x" * 31 + " ", "é" * 32])
def test_developer_input_requires_a_valid_secret(token):
    with pytest.raises(ValueError):
        dev_token(token)


@pytest.mark.parametrize("body", ["rotate 0", "rotate 17", "rotate -17", "rotate 9999999999999999999", "click 1", "missing 0", "double", "rotate 1 extra"])
def test_invalid_events_cannot_reach_the_engine(body):
    token = secrets.token_urlsafe(32)
    assert decode_event(f"{token} {body}".encode(), token) is None


def test_untrusted_udp_packets_do_not_trigger_actions():
    token = secrets.token_urlsafe(32)
    source = UdpDevSource(0, token)
    received, ready = [], threading.Event()

    def capture(event):
        received.append(event)
        ready.set()

    source.start(capture)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
            address = source._sock.getsockname()
            for data in [b"hold", b"double 0", b"wrong-token hold 0", f"{token} rotate 2147483647".encode(), b"\xff"]:
                sender.sendto(data, address)
            sender.sendto(f"{token} double 0".encode(), address)
        assert ready.wait(3)
        assert [(e.kind.value, e.delta) for e in received] == [("double", 0)]
    finally:
        source.stop()
    assert not source._thread.is_alive()


@pytest.mark.parametrize("args", [[], ["--no-elevate"], ["--dev", "--no-elevate"]])
def test_elevated_windows_launch_stops_before_user_files(monkeypatch, args):
    from orbit import app
    monkeypatch.setattr(app.sys, "platform", "win32")
    monkeypatch.setattr(app, "get_platform", lambda: SimpleNamespace(is_elevated=lambda: True))
    user_files = MagicMock(side_effect=AssertionError("user files must not be read elevated"))
    monkeypatch.setattr(app, "setup_logging", user_files)
    assert app.main(args) == 1
    user_files.assert_not_called()


def test_packaged_build_rejects_developer_input(monkeypatch):
    from orbit import app
    monkeypatch.setattr(app, "get_platform", lambda: SimpleNamespace(is_elevated=lambda: False))
    monkeypatch.setattr(app.sys, "frozen", True, raising=False)
    with pytest.raises(SystemExit, match="unavailable in packaged builds"):
        app.main(["--dev"])


@pytest.mark.skipif(sys.platform != "win32", reason="Windows launcher")
def test_unknown_launch_target_never_reaches_a_shell(monkeypatch):
    from orbit.platform.windows import output
    import shutil
    import subprocess
    monkeypatch.setattr(shutil, "which", lambda _: None)
    monkeypatch.setattr(output, "find_start_menu_app", lambda _: None)
    monkeypatch.setattr(output, "find_store_app", lambda _: None)
    popen = MagicMock()
    monkeypatch.setattr(subprocess, "Popen", popen)
    output.WindowsOutput.__new__(output.WindowsOutput)._launch("missing-orbit-app & echo forbidden")
    popen.assert_not_called()


@pytest.mark.skipif(sys.platform != "win32", reason="Windows registry")
def test_autostart_uses_only_the_current_users_run_key(monkeypatch):
    from orbit.platform.windows import autostart
    registry = MagicMock()
    monkeypatch.setattr(autostart, "winreg", registry)
    monkeypatch.setattr(autostart.sys, "executable", r"C:\Program Files\Orbit\Orbit.exe")
    assert autostart.set_enabled(True)
    registry.CreateKeyEx.assert_called_once_with(registry.HKEY_CURRENT_USER, autostart.RUN_KEY, 0, registry.KEY_SET_VALUE)
    registry.SetValueEx.assert_called_once_with(registry.CreateKeyEx.return_value.__enter__.return_value,
                                              "Orbit", 0, registry.REG_SZ, '"C:\\Program Files\\Orbit\\Orbit.exe"')

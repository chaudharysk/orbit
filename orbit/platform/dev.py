"""Authenticated loopback test input for source checkouts only.

Set ORBIT_DEV_TOKEN to a random per-session secret in app and injector.
Packaged applications reject --dev and exclude this module.
"""
from __future__ import annotations

import logging
import hmac
import os
import socket
import threading
import time
from collections import deque

from orbit.core.events import Capability, InputEvent, Kind
from orbit.platform.base import InputSource

log = logging.getLogger("orbit.dev")
PORT = 47800
MAX_DELTA = 16
MAX_EVENTS_PER_SECOND = 30


def dev_token(token: str | None = None) -> str:
    token = token if token is not None else os.environ.get("ORBIT_DEV_TOKEN", "")
    if not 32 <= len(token) <= 128 or not token.isascii() or any(c.isspace() for c in token):
        raise ValueError("ORBIT_DEV_TOKEN must be a random 32–128 character ASCII secret without whitespace")
    return token


def decode_event(data: bytes, token: str) -> InputEvent | None:
    try:
        parts = data.decode("ascii").split()
        if len(parts) != 3 or not hmac.compare_digest(parts[0], token):
            return None
        kind, delta = Kind(parts[1]), int(parts[2])
        if (kind == Kind.ROTATE and not 1 <= abs(delta) <= MAX_DELTA) or (kind != Kind.ROTATE and delta != 0):
            return None
        return InputEvent(kind, delta, "dev-udp")
    except (UnicodeError, ValueError):
        return None


class UdpDevSource(InputSource):
    name = "dev-udp"
    capabilities = frozenset({Capability.ROTATE, Capability.CLICKS, Capability.HOLD})

    def __init__(self, port: int = PORT, token: str | None = None):
        self.port, self._token = port, dev_token(token)
        self._sock = None
        self._thread = None

    def start(self, emit):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("127.0.0.1", self.port))
        sock.settimeout(0.2)
        self._sock = sock

        def loop():
            recent = deque()
            while self._sock is sock:
                try:
                    data, _ = sock.recvfrom(512)
                except socket.timeout:
                    continue
                except OSError:
                    return
                ev = decode_event(data, self._token)
                if ev is None:
                    continue
                now = time.monotonic()
                while recent and now - recent[0] >= 1:
                    recent.popleft()
                if len(recent) >= MAX_EVENTS_PER_SECOND:
                    continue
                recent.append(now)
                emit(ev)

        self._thread = threading.Thread(target=loop, name="dev-udp", daemon=True)
        self._thread.start()
        log.info("authenticated dev input on udp://127.0.0.1:%d", sock.getsockname()[1])

    def stop(self):
        sock, self._sock = self._sock, None
        if sock:
            sock.close()
        if self._thread:
            self._thread.join(timeout=1)


def send(kind: str, delta: int = 0, port: int = PORT, token: str | None = None):
    token = dev_token(token)
    data = f"{token} {kind} {delta}".encode("ascii")
    if decode_event(data, token) is None:
        raise ValueError("invalid dev event")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(data, ("127.0.0.1", port))

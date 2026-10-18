"""Windows backend.

Sources
  VolumeRotationSource   rotation   (AVRCP absolute volume on the buds endpoint)
  MediaButtonSource      clicks     (AVRCP play/pause/next/prev via our own SMTC session)
  hold                   disabled  (ETW requires a protected privileged helper)
"""
from __future__ import annotations

from pathlib import Path

from orbit.platform.base import Platform
from orbit.platform.windows import etw


def cache_dir() -> Path:
    import os
    return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Orbit"


class WindowsPlatform(Platform):
    name = "windows"

    def __init__(self):
        self._media = None

    def create_sources(self, cfg):
        from orbit.platform.windows.input_media import MediaButtonSource
        from orbit.platform.windows.input_volume import VolumeRotationSource

        self._media = MediaButtonSource(cache_dir())
        self._volume = VolumeRotationSource(cfg["device"]["audio_endpoint_match"])
        # ETW hold tracing requires elevation. Never elevate the UI or user actions.
        return [self._volume, self._media]

    def create_services(self, cfg):
        from orbit.platform.windows.flyout import FlyoutSuppressor

        f = FlyoutSuppressor(self._volume.last_activity)
        f.enabled = bool(cfg["ui"]["hide_os_volume_flyout"])
        f.toggle_label = "Hide Windows volume bar"
        return [f]

    def create_output(self, cfg):
        from orbit.platform.windows.output import WindowsOutput
        return WindowsOutput(media_source=self._media)

    def is_elevated(self):
        return etw.is_admin()

    def relaunch_elevated(self, argv):
        return False

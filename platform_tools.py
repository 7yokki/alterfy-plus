"""Alterfy+ portable runtime helpers.

The app never assumes VLC/ffmpeg/yt-dlp live on PATH.  A release bundle places
native tools under tools/<platform>-<arch>/ and this module resolves them.
"""
from __future__ import annotations

import os
import platform
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimeTarget:
    platform: str
    arch: str

    @property
    def folder(self) -> str:
        return f"{self.platform}-{self.arch}"


def detect_target() -> RuntimeTarget:
    system = platform.system().lower()
    name = {"windows": "windows", "darwin": "macos", "linux": "linux"}.get(system, system)
    machine = platform.machine().lower()
    arch = "x64" if machine in {"x86_64", "amd64", "x64"} else "arm64" if "arm" in machine or "aarch64" in machine else machine
    return RuntimeTarget(name, arch)


def app_root() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))


def bundled_path(tool: str) -> Path | None:
    root = app_root() / "tools" / detect_target().folder
    candidates = [root / tool, root / f"{tool}.exe" if os.name == "nt" else root / tool]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def resolve_tool(tool: str) -> str | None:
    path = bundled_path(tool)
    return str(path) if path else shutil.which(tool)


def configure_runtime() -> RuntimeTarget:
    """Prepend the matching bundled tool directory to PATH, if present."""
    target = detect_target()
    root = app_root() / "tools" / target.folder
    if root.is_dir():
        os.environ["PATH"] = str(root) + os.pathsep + os.environ.get("PATH", "")
        if target.platform == "windows":
            os.environ.setdefault("VLC_PLUGIN_PATH", str(root / "plugins"))
    return target


def runtime_report() -> dict[str, str | bool]:
    target = detect_target()
    return {"target": target.folder, "vlc": bool(resolve_tool("vlc")), "ffmpeg": bool(resolve_tool("ffmpeg")), "yt_dlp": bool(resolve_tool("yt-dlp"))}

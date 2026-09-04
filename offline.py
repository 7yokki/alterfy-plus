"""Offline download/import service using the bundled yt-dlp executable when available."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Callable

from platform_tools import resolve_tool


class OfflineService:
    def __init__(self, library_dir: str | Path | None = None):
        self.library_dir = Path(library_dir or Path.home() / ".alterfy-plus" / "offline")
        self.library_dir.mkdir(parents=True, exist_ok=True)

    def executable(self) -> str:
        return resolve_tool("yt-dlp") or "yt-dlp"

    def download(self, url: str, quality: str = "best", progress: Callable[[str], None] | None = None) -> Path:
        if not url.strip():
            raise ValueError("A playlist or video URL is required")
        output = self.library_dir / "%(uploader)s" / "%(title)s [%(id)s].%(ext)s"
        fmt = {"best": "bestaudio/best", "high": "bestaudio[abr>=192]/bestaudio", "balanced": "bestaudio[abr>=128]/bestaudio"}.get(quality, "bestaudio/best")
        cmd = [self.executable(), "--newline", "--no-playlist" if "playlist" not in url else "--yes-playlist", "-f", fmt, "-o", str(output), url]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
        for line in proc.stdout or []:
            if progress:
                progress(line.rstrip())
        if proc.wait() != 0:
            raise RuntimeError("yt-dlp could not download the requested media")
        return self.library_dir

    def import_playlist(self, url: str, progress: Callable[[str], None] | None = None) -> Path:
        return self.download(url, quality="best", progress=progress)

    def list_files(self) -> list[Path]:
        return sorted(p for p in self.library_dir.rglob("*") if p.is_file() and p.suffix.lower() in {".mp3", ".m4a", ".opus", ".webm", ".wav", ".flac"})

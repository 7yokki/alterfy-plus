"""Fast artist disambiguation with a local cache and Wikipedia fallback."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from urllib.parse import quote
import requests


class ArtistProfileService:
    def __init__(self, cache_dir: str | Path | None = None):
        self.cache_file = Path(cache_dir or Path.home() / ".alterfy-plus") / "artists.json"
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.cache = json.loads(self.cache_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.cache = {}

    @staticmethod
    def normalize_name(name: str) -> str:
        name = re.sub(r"\s+", " ", name or "").strip()
        return name.split(" - ")[0].strip()

    def lookup(self, name: str, language: str = "tr") -> dict:
        key = self.normalize_name(name).casefold()
        if not key:
            return {}
        if key in self.cache:
            return self.cache[key]
        lang = language if language in {"tr", "en", "de", "fr"} else "en"
        url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote(self.normalize_name(name))}"
        try:
            response = requests.get(url, timeout=6, headers={"User-Agent": "AlterfyPlus/1.0"})
            data = response.json() if response.status_code == 200 else {}
            profile = {
                "name": self.normalize_name(name),
                "description": data.get("extract", ""),
                "image": (data.get("thumbnail") or {}).get("source", ""),
                "wikipedia": (data.get("content_urls") or {}).get("desktop", {}).get("page", ""),
                "updated_at": time.time(),
            }
        except (requests.RequestException, ValueError):
            profile = {"name": self.normalize_name(name), "description": "", "image": "", "wikipedia": "", "updated_at": time.time()}
        self.cache[key] = profile
        self.cache_file.write_text(json.dumps(self.cache, ensure_ascii=False, indent=2), encoding="utf-8")
        return profile

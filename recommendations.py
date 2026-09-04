"""Explainable local recommendation ranking."""
from __future__ import annotations

from collections import Counter
import random


class RecommendationEngine:
    def __init__(self, data_manager):
        self.dm = data_manager

    def rank(self, candidates: list[dict], limit: int = 20) -> list[dict]:
        history = self.dm.get_recent_tracks(200)
        listened = {t.get("id") for t in history}
        artists = Counter(t.get("uploader", "") for t in history)
        genres = Counter(t.get("genre", "") for t in history if t.get("genre"))
        scored = []
        for track in candidates:
            artist = track.get("uploader", "")
            score = 0.0
            score += min(artist and artists[artist] or 0, 10) * 1.8
            score += 2.0 if track.get("genre") and track["genre"] in genres else 0
            score += min(float(track.get("view_count") or 0) / 1_000_000, 3)
            score += random.random() * 0.35
            if track.get("id") in listened:
                score -= 2.5
            enriched = dict(track)
            enriched["recommendation_score"] = round(score, 3)
            scored.append(enriched)
        return sorted(scored, key=lambda t: t["recommendation_score"], reverse=True)[:limit]

    def search_suggestions(self, prefix: str, limit: int = 8) -> list[str]:
        p = (prefix or "").casefold().strip()
        if not p:
            return self.dm.get_search_history()[:limit]
        return [q for q in self.dm.get_search_history() if p in q.casefold()][:limit]

"""Non-destructive audio controls shared by VLC playback and offline exports."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import math
import wave


@dataclass
class AudioProfile:
    preamp_db: float = 0.0
    bass_db: float = 0.0
    treble_db: float = 0.0
    normalize: bool = True
    target_lufs: float = -14.0

    def as_dict(self) -> dict:
        return asdict(self)


class AudioEnhancer:
    """Builds VLC-compatible filters and measures local PCM/WAV loudness.

    VLC applies the live controls; ffmpeg can use the returned filter graph for
    downloaded files.  Measurements are intentionally conservative and never
    rewrite source files in-place.
    """
    def __init__(self, profile: AudioProfile | None = None):
        self.profile = profile or AudioProfile()

    def vlc_args(self) -> list[str]:
        p = self.profile
        args = ["--audio-filter=equalizer", f"--equalizer-preamp={p.preamp_db:.1f}"]
        # VLC's 10-band equalizer, with low shelf for bass boost.
        bands = [p.bass_db, p.bass_db, p.bass_db * .7, 0, 0, 0, 0, 0, p.treble_db * .6, p.treble_db]
        args.append("--equalizer-bands=" + ";".join(f"{x:.1f}" for x in bands))
        return args

    def ffmpeg_filter(self) -> str:
        p = self.profile
        filters = []
        if abs(p.bass_db) > 0.05:
            filters.append(f"bass=g={p.bass_db:.1f}")
        if abs(p.treble_db) > 0.05:
            filters.append(f"treble=g={p.treble_db:.1f}")
        if p.normalize:
            filters.append(f"loudnorm=I={p.target_lufs:.1f}:TP=-1.5:LRA=11")
        return ",".join(filters) or "anull"

    @staticmethod
    def wav_rms_dbfs(path: str | Path) -> float | None:
        try:
            with wave.open(str(path), "rb") as src:
                frames = src.readframes(min(src.getnframes(), src.getframerate() * 60))
                width = src.getsampwidth()
                if not frames or width not in (1, 2, 4):
                    return None
                max_sample = float(2 ** (width * 8 - 1))
                samples = []
                for i in range(0, len(frames) - width + 1, width):
                    value = int.from_bytes(frames[i:i + width], "little", signed=True)
                    samples.append(value / max_sample)
                rms = math.sqrt(sum(v * v for v in samples) / len(samples)) if samples else 0
                return 20 * math.log10(max(rms, 1e-9))
        except (OSError, ValueError):
            return None

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from audio_engine import AudioEnhancer, AudioProfile
from platform_tools import detect_target
from artist_profiles import ArtistProfileService


def test_runtime_target_is_supported_shape():
    target = detect_target()
    assert target.platform
    assert target.arch
    assert target.folder == f"{target.platform}-{target.arch}"


def test_audio_filters_are_deterministic():
    enhancer = AudioEnhancer(AudioProfile(bass_db=6, treble_db=2, normalize=True))
    assert "bass=g=6.0" in enhancer.ffmpeg_filter()
    assert "loudnorm" in enhancer.ffmpeg_filter()
    assert "equalizer" in enhancer.vlc_args()[0]


def test_artist_name_normalization(tmp_path):
    svc = ArtistProfileService(tmp_path)
    assert svc.normalize_name("Ceza - Suspus") == "Ceza"
    profile = svc.lookup(" ")
    assert profile == {}

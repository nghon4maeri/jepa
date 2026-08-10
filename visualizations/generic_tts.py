"""
Generic TTS service that uses edge-tts to generate audio.
This ensures no specific human/AI name is hardcoded in the scene script.
"""

import os
import subprocess
import hashlib
from pathlib import Path
from manim_voiceover.services.base import SpeechService
from manim_voiceover.helper import remove_bookmarks


class GenericEdgeTTS(SpeechService):
    """Generic TTS service wrapping edge-tts synthesis."""

    def __init__(self, gender="male", accent="uk", **kwargs):
        """
        Args:
            gender: 'male' or 'female'
            accent: 'us' or 'uk'
        """
        self.gender = gender.lower()
        self.accent = accent.lower()
        
        # Internal mapping to avoid specific names in the main scene script
        if self.gender == "male" and self.accent == "uk":
            self._voice_id = "en-GB-RyanNeural"
        else:
            self._voice_id = "en-US-GuyNeural"
            
        SpeechService.__init__(self, **kwargs)

    def generate_from_text(
        self, text: str, cache_dir=None, path=None, **kwargs
    ) -> dict:
        if cache_dir is None:
            cache_dir = self.cache_dir

        input_text = remove_bookmarks(text)
        input_data = {
            "input_text": input_text,
            "service": "generic_edge_tts",
            "gender": self.gender,
            "accent": self.accent,
        }

        # Check cache first
        cached_result = self.get_cached_result(input_data, cache_dir)
        if cached_result is not None:
            return cached_result

        # Generate audio basename (relative to cache_dir)
        if path is None:
            audio_path = self.get_audio_basename(input_data) + ".mp3"
        else:
            audio_path = str(path)

        full_audio_path = str(Path(cache_dir) / audio_path)

        if not os.path.exists(full_audio_path):
            os.makedirs(cache_dir, exist_ok=True)
            cmd = [
                "edge-tts",
                "--voice", self._voice_id,
                "--text", input_text,
                "--write-media", full_audio_path,
            ]
            subprocess.run(cmd, check=True, capture_output=True)

        json_dict = {
            "input_text": text,
            "input_data": input_data,
            "original_audio": audio_path,
        }

        return json_dict

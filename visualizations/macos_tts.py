"""
Custom TTS service that uses macOS 'say' command to generate audio.
This avoids the pyttsx3 event loop hang issue in Manim render context.
"""

import os
import subprocess
import hashlib
from pathlib import Path
from manim_voiceover.services.base import SpeechService
from manim_voiceover.helper import remove_bookmarks


class MacOSSayService(SpeechService):
    """Speech service using macOS 'say' command for TTS."""

    def __init__(self, voice="Daniel", rate=180, **kwargs):
        """
        Args:
            voice: macOS voice name (e.g., "Daniel", "Samantha")
            rate: Speech rate in words per minute (default 180)
        """
        self.voice = voice
        self.rate = rate
        SpeechService.__init__(self, **kwargs)

    def generate_from_text(
        self, text: str, cache_dir=None, path=None, **kwargs
    ) -> dict:
        if cache_dir is None:
            cache_dir = self.cache_dir

        input_text = remove_bookmarks(text)
        input_data = {
            "input_text": input_text,
            "service": "macos_say",
            "voice": self.voice,
            "rate": self.rate,
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

            # Generate AIFF using macOS say command
            aiff_path = full_audio_path.replace(".mp3", ".aiff")
            cmd = [
                "say",
                "-v", self.voice,
                "-r", str(self.rate),
                "-o", aiff_path,
                input_text,
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            # Convert AIFF to MP3 using ffmpeg
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-i", aiff_path,
                "-acodec", "libmp3lame",
                "-b:a", "192k",
                full_audio_path,
            ]
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)

            # Cleanup AIFF
            if os.path.exists(aiff_path):
                os.remove(aiff_path)

        json_dict = {
            "input_text": text,
            "input_data": input_data,
            "original_audio": audio_path,
        }

        return json_dict

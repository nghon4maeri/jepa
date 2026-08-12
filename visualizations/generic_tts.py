"""
Generic TTS service that uses edge-tts to generate audio.
This ensures no specific human/AI name is hardcoded in the scene script.
"""

import os
from pathlib import Path

import edge_tts
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
            "timing": "word-boundary-v1",
        }

        # Check cache first
        cached_result = self.get_cached_result(input_data, cache_dir)
        if cached_result is not None:
            cached_audio = Path(cache_dir) / cached_result["final_audio"]
            if (
                cached_audio.exists()
                and cached_audio.stat().st_size > 0
                and cached_result.get("word_boundaries")
            ):
                return cached_result

        # Generate audio basename (relative to cache_dir)
        if path is None:
            audio_path = self.get_audio_basename(input_data) + ".mp3"
        else:
            audio_path = str(path)

        full_audio_path = str(Path(cache_dir) / audio_path)

        os.makedirs(cache_dir, exist_ok=True)
        temp_audio_path = full_audio_path + ".tmp"
        word_boundaries = []
        search_cursor = 0

        try:
            communicator = edge_tts.Communicate(
                input_text,
                voice=self._voice_id,
                boundary="WordBoundary",
            )
            with open(temp_audio_path, "wb") as audio_file:
                for chunk in communicator.stream_sync():
                    if chunk["type"] == "audio":
                        audio_file.write(chunk["data"])
                        continue
                    if chunk["type"] != "WordBoundary":
                        continue

                    word = chunk["text"]
                    text_offset = input_text.lower().find(word.lower(), search_cursor)
                    if text_offset < 0:
                        text_offset = search_cursor
                    search_cursor = text_offset + len(word)
                    word_boundaries.append(
                        {
                            "audio_offset": int(chunk["offset"]),
                            "text_offset": text_offset,
                            "word_length": len(word),
                            "text": word,
                            "boundary_type": "Word",
                        }
                    )

            if os.path.getsize(temp_audio_path) == 0 or len(word_boundaries) < 2:
                raise RuntimeError("Edge TTS returned incomplete audio timing data")
            os.replace(temp_audio_path, full_audio_path)
        finally:
            Path(temp_audio_path).unlink(missing_ok=True)

        json_dict = {
            "input_text": text,
            "input_data": input_data,
            "original_audio": audio_path,
            "word_boundaries": word_boundaries,
        }

        return json_dict

"""Combined V-JEPA Part 1: Chapters 1 through 4.

The chapter scene methods are called directly so their visuals, animation
timing, formulas, and narration remain the single source of truth.

Render at 480p with:
    manim -ql visualizations/part1.py Part1DryRunScene
    manim -ql visualizations/part1.py Part1Scene
"""

from contextlib import contextmanager
from pathlib import Path
import re
import textwrap

from manim import FadeOut, ManimColor, config

from chapter1 import Chapter1Scene
from chapter2 import Chapter2Scene
from chapter3 import Chapter3Scene
from chapter4 import Chapter4Scene
from generic_tts import GenericEdgeTTS


RESULT_DIR = Path(__file__).resolve().parent / "media" / "result"
VOICEOVER_CACHE_DIR = Path(__file__).resolve().parent.parent / "media" / "voiceovers"
RESULT_DIR.mkdir(parents=True, exist_ok=True)

# Keep both final videos directly in visualizations/media/result/. Manim still
# stores its reusable partial clips in a child directory of the same folder.
config.pixel_height = 480
config.pixel_width = 854
config.frame_rate = 15
config.media_dir = str(RESULT_DIR)
config.video_dir = str(RESULT_DIR)
config.partial_movie_dir = str(
    RESULT_DIR / "partial_movie_files" / "{scene_name}"
)
config.images_dir = str(RESULT_DIR / "images")
config.tex_dir = str(RESULT_DIR / "Tex")
config.text_dir = str(RESULT_DIR / "texts")


def _format_srt_time(seconds):
    total_milliseconds = max(0, round(float(seconds) * 1000))
    hours, remainder = divmod(total_milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1_000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


class Part1Scene(Chapter1Scene, Chapter2Scene, Chapter3Scene, Chapter4Scene):
    """All four chapters rendered as one continuous narrated video."""

    def construct(self):
        self.camera.background_color = ManimColor("#1a1a2e")
        self.set_speech_service(
            GenericEdgeTTS(
                gender="male",
                accent="uk",
                cache_dir=VOICEOVER_CACHE_DIR,
            ),
            create_subcaption=False,
        )
        self._srt_entries = []
        self._tracked_trackers = []

        self._run_chapter1()
        self._finish_chapter()
        self._run_chapter2()
        self._finish_chapter()
        self._run_chapter3()
        self._finish_chapter()
        self._run_chapter4()

        self._write_srt()

    def _run_chapter1(self):
        Chapter1Scene.part1_visual_world(self)
        Chapter1Scene.part2_fill_in_blank(self)

    def _run_chapter2(self):
        self._cluster_persist = None
        self._all_clusters_visual = None
        self._cluster_circle_info = []

        Chapter2Scene.act1_title(self)
        Chapter2Scene.act2_build_lake_scene(self)
        Chapter2Scene.act3_overlay_pixel_grid(self)
        Chapter2Scene.act4_mask_blocks(self)
        Chapter2Scene.act5_videomae_reconstruct(self)
        Chapter2Scene.act6_pixel_conclusion(self)
        Chapter2Scene.act7_contrast_split(self)
        Chapter2Scene.act8_encoder(self)
        Chapter2Scene.act9_latent_scatter(self)
        Chapter2Scene.act10_noise_filter(self)
        Chapter2Scene.act11_semantic_vector(self)
        Chapter2Scene.act12_summary(self)

    def _run_chapter3(self):
        self.clip_group = None
        self.feature_grid = None
        self.token_row = None
        self.split_group = None
        self.architecture_group = None

        Chapter3Scene.act1_title(self)
        Chapter3Scene.act2_known_input(self)
        Chapter3Scene.act3_conv3d_scan(self)
        Chapter3Scene.act4_feature_grid(self)
        Chapter3Scene.act5_positional_embedding(self)
        Chapter3Scene.act6_flatten_tokens(self)
        Chapter3Scene.act7_visible_and_mask_tokens(self)
        Chapter3Scene.act8_three_component_architecture(self)
        Chapter3Scene.act9_latent_prediction_match(self)
        Chapter3Scene.act10_recap_bridge(self)

    def _run_chapter4(self):
        Chapter4Scene.act1_title(self)
        Chapter4Scene.act2_temporal_leakage(self)
        Chapter4Scene.act3_sample_spatial_block(self)
        Chapter4Scene.act4_union_and_extrusion(self)
        Chapter4Scene.act5_short_range_mask(self)
        Chapter4Scene.act6_long_range_and_ablations(self)
        Chapter4Scene.act7_multi_mask_prediction(self)
        Chapter4Scene.act8_recap(self)

    def _finish_chapter(self):
        self._fade_scene(run_time=0.55)
        self.clear()

    def _fade_group(self, group, run_time=0.55):
        if group is not None and len(group) > 0:
            self.play(FadeOut(group, run_time=run_time))

    def _fade_scene(self, run_time=0.55):
        for mobject in list(self.mobjects):
            mobject.clear_updaters()
        if self.mobjects:
            self.play(
                *[FadeOut(mobject) for mobject in list(self.mobjects)],
                run_time=run_time,
            )
        self.clear()

    @contextmanager
    def voiceover(self, text, **kwargs):
        """Track every chapter's narration in one continuous subtitle file."""
        with super().voiceover(text=text, **kwargs) as tracker:
            self._current_tracker = tracker
            yield tracker
            self._track_subtitle(text)

    def _track_subtitle(self, text):
        tracker = getattr(self, "_current_tracker", None)
        if tracker is None or any(
            tracker is tracked for tracked in self._tracked_trackers
        ):
            return
        self._tracked_trackers.append(tracker)

        tracker_data = getattr(tracker, "data", None) or {}
        boundaries = tracker_data.get("word_boundaries", [])
        if len(boundaries) < 2:
            boundaries = self._fallback_word_boundaries(text, tracker.duration)
        if not boundaries:
            return

        groups = []
        group_start = 0
        for index, boundary in enumerate(boundaries):
            next_offset = (
                boundaries[index + 1]["text_offset"]
                if index + 1 < len(boundaries)
                else len(text)
            )
            preview = text[
                boundaries[group_start]["text_offset"]:next_offset
            ].strip()
            word_count = index - group_start + 1
            sentence_end = bool(re.search(r"[.!?][\"']?$", preview))
            if (
                word_count >= 7
                or len(preview) >= 44
                or (word_count >= 4 and sentence_end)
            ):
                groups.append((group_start, index))
                group_start = index + 1

        if group_start < len(boundaries):
            groups.append((group_start, len(boundaries) - 1))

        for group_index, (start_index, _) in enumerate(groups):
            start_boundary = boundaries[start_index]
            text_start = start_boundary["text_offset"]
            relative_start = start_boundary["audio_offset"] / 10_000_000

            if group_index + 1 < len(groups):
                next_start_index = groups[group_index + 1][0]
                text_end = boundaries[next_start_index]["text_offset"]
                relative_end = max(
                    relative_start + 0.35,
                    boundaries[next_start_index]["audio_offset"] / 10_000_000
                    - 0.04,
                )
            else:
                text_end = len(text)
                relative_end = tracker.duration

            caption = text[text_start:text_end].strip()
            caption = "\n".join(
                textwrap.wrap(
                    caption,
                    width=42,
                    break_long_words=False,
                    break_on_hyphens=False,
                )
            )
            start = float(tracker.start_t + relative_start)
            end = float(min(tracker.end_t, tracker.start_t + relative_end))
            if caption and end > start:
                self._srt_entries.append(
                    {"start": start, "end": end, "text": caption}
                )

    @staticmethod
    def _fallback_word_boundaries(text, duration):
        matches = list(re.finditer(r"\S+", text))
        if not matches:
            return []
        return [
            {
                "audio_offset": int(
                    duration * 10_000_000 * index / len(matches)
                ),
                "text_offset": match.start(),
                "word_length": len(match.group(0)),
                "text": match.group(0),
                "boundary_type": "Word",
            }
            for index, match in enumerate(matches)
        ]

    def _write_srt(self):
        if not self._srt_entries:
            return
        srt_path = RESULT_DIR / "Part1Scene.srt"
        with srt_path.open("w", encoding="utf-8") as handle:
            for index, entry in enumerate(self._srt_entries, start=1):
                handle.write(f"{index}\n")
                handle.write(
                    f"{_format_srt_time(entry['start'])} --> "
                    f"{_format_srt_time(entry['end'])}\n"
                )
                handle.write(f"{entry['text']}\n\n")


class Part1DryRunScene(Part1Scene):
    """Offline layout render using the same chapter acts without TTS."""

    def set_speech_service(self, *args, **kwargs):
        return None

    @contextmanager
    def voiceover(self, text, **kwargs):
        duration = max(3.2, min(12.0, len(text.split()) * 0.24))
        tracker = type(
            "DryRunTracker",
            (),
            {
                "duration": duration,
                "start_t": float(self.time),
                "end_t": float(self.time + duration),
                "data": {},
            },
        )()
        self._current_tracker = tracker
        yield tracker

    def _track_subtitle(self, text):
        return None

    def _write_srt(self):
        return None

"""
V-JEPA Video - Chapter 4: 3D Multi-Block Masking

This chapter follows implementation_plan_chapter4.md. It assumes that video
tokenization and the three-network architecture were already introduced in
Chapter 3, and focuses on mask construction, temporal leakage, and multi-mask
prediction.
"""

from pathlib import Path
from contextlib import contextmanager
import math
import re
import textwrap

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from generic_tts import GenericEdgeTTS


config.pixel_height = 480
config.pixel_width = 854
config.frame_rate = 15


BG_COLOR = ManimColor("#171923")
CONTEXT_BLUE = ManimColor("#5DADE2")
PREDICTOR_ORANGE = ManimColor("#E59866")
TARGET_GRAY = ManimColor("#AAB7B8")
SHORT_MASK = ManimColor("#F4C95D")
LONG_MASK = ManimColor("#EC7063")
LEAK_GREEN = ManimColor("#58D68D")
PURPLE_ACCENT = ManimColor("#AF7AC5")
SOFT_WHITE = ManimColor("#ECEFF4")
DIM_GRAY = ManimColor("#7F8794")
GRID_GRAY = ManimColor("#3E4655")
DEEP_MASK = ManimColor("#272B38")

SUBTITLE_SAFE_Y = -2.55


def spaced_text(*args, spacing=1.1, **kwargs):
    mob = Text(*args, **kwargs)
    mob.stretch(spacing, 0)
    return mob


def _rt(duration, start_frac, end_frac, fill=0.82, floor=0.32):
    window = max(0.0, end_frac - start_frac) * duration * fill
    return max(floor, window)


def _format_srt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def build_token_grid(rows=14, cols=14, cell_size=0.2):
    cells = VGroup()
    for row in range(rows):
        for col in range(cols):
            cell = Square(
                side_length=cell_size,
                stroke_color=GRID_GRAY,
                stroke_width=0.75,
                fill_color=DEEP_MASK,
                fill_opacity=0.18,
            )
            cell.move_to(
                RIGHT * (col - (cols - 1) / 2) * cell_size
                + DOWN * (row - (rows - 1) / 2) * cell_size
            )
            cells.add(cell)
    cells.rows = rows
    cells.cols = cols
    cells.cell_size = cell_size
    return cells


def sample_block_shape(scale, aspect_ratio, rows=14, cols=14):
    """Match src/masks/multiblock3d.py for one spatial block."""
    area = int(rows * cols * scale)
    height = int(round(math.sqrt(area * aspect_ratio)))
    width = int(round(math.sqrt(area / aspect_ratio)))
    return min(max(height, 1), rows), min(max(width, 1), cols)


def sample_block_position(height, width, rows=14, cols=14, rng=None):
    rng = rng or np.random.default_rng(0)
    top = int(rng.integers(0, rows - height + 1))
    left = int(rng.integers(0, cols - width + 1))
    return top, left


def block_indices(top, left, height, width, rows=14, cols=14):
    return {
        row * cols + col
        for row in range(top, min(top + height, rows))
        for col in range(left, min(left + width, cols))
    }


def build_block_overlay(grid, indices, color, opacity=0.55, stroke_width=0.65):
    overlay = VGroup()
    for index in sorted(indices):
        cell = grid[index].copy()
        cell.set_fill(color, opacity=opacity)
        cell.set_stroke(color, width=stroke_width, opacity=0.9)
        overlay.add(cell)
    return overlay


def build_block_border(grid, indices, color, stroke_width=2.2):
    selected = VGroup(*[grid[index] for index in sorted(indices)])
    return SurroundingRectangle(
        selected,
        buff=0.015,
        color=color,
        stroke_width=stroke_width,
    )


def union_indices(blocks):
    result = set()
    for block in blocks:
        result.update(block)
    return result


def build_lake_frame(label, boat_shift=0.0):
    frame = RoundedRectangle(
        width=3.35,
        height=2.05,
        corner_radius=0.06,
        stroke_color=DIM_GRAY,
        stroke_width=1.4,
        fill_color=BG_COLOR,
        fill_opacity=1,
    )
    sky = Rectangle(
        width=3.2,
        height=0.78,
        stroke_width=0,
        fill_color=CONTEXT_BLUE,
        fill_opacity=0.15,
    ).move_to(frame.get_center() + UP * 0.55)
    lake = Rectangle(
        width=3.2,
        height=1.08,
        stroke_width=0,
        fill_color=CONTEXT_BLUE,
        fill_opacity=0.28,
    ).move_to(frame.get_center() + DOWN * 0.38)
    ripples = VGroup()
    for y_shift in (-0.72, -0.45, -0.18):
        ripple = Arc(
            radius=0.42,
            start_angle=0.12,
            angle=PI - 0.24,
            color=SOFT_WHITE,
            stroke_width=1,
            stroke_opacity=0.38,
        ).stretch(1.5, 0)
        ripple.move_to(frame.get_center() + RIGHT * (0.25 + boat_shift) + UP * y_shift)
        ripples.add(ripple)
    hull = Polygon(
        LEFT * 0.42 + UP * 0.04,
        RIGHT * 0.46 + UP * 0.04,
        RIGHT * 0.28 + DOWN * 0.18,
        LEFT * 0.3 + DOWN * 0.18,
        color=PREDICTOR_ORANGE,
        fill_color=PREDICTOR_ORANGE,
        fill_opacity=0.82,
        stroke_width=1,
    )
    mast = Line(ORIGIN + DOWN * 0.03, ORIGIN + UP * 0.58, color=SOFT_WHITE, stroke_width=1.4)
    sail = Polygon(
        ORIGIN + UP * 0.5,
        ORIGIN + RIGHT * 0.38 + UP * 0.12,
        ORIGIN + UP * 0.12,
        color=SOFT_WHITE,
        fill_color=SOFT_WHITE,
        fill_opacity=0.68,
        stroke_width=1,
    )
    boat = VGroup(hull, mast, sail).scale(0.72)
    boat.move_to(frame.get_center() + RIGHT * boat_shift + DOWN * 0.17)
    time_label = MathTex(label, font_size=23, color=SOFT_WHITE).next_to(frame, DOWN, buff=0.13)
    return VGroup(frame, sky, lake, ripples, boat, time_label)


def make_flow_box(label, formula=None, color=SOFT_WHITE, width=2.0, height=0.72):
    title = spaced_text(label, font_size=14, color=color, weight=BOLD)
    content = VGroup(title)
    if formula:
        math_mob = MathTex(formula, font_size=20, color=SOFT_WHITE)
        content.add(math_mob)
        content.arrange(DOWN, buff=0.07)
    box = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.06,
        stroke_color=color,
        stroke_width=1.8,
        fill_color=color,
        fill_opacity=0.1,
    )
    content.move_to(box)
    return VGroup(box, content)


def make_simple_bar(value, max_value, color, label, score, width=1.0, max_height=1.65):
    base = Line(LEFT * width / 2, RIGHT * width / 2, color=DIM_GRAY, stroke_width=1)
    bar_height = max(0.08, max_height * value / max_value)
    bar = Rectangle(
        width=width * 0.62,
        height=bar_height,
        stroke_width=0,
        fill_color=color,
        fill_opacity=0.8,
    ).next_to(base, UP, buff=0)
    name = spaced_text(label, font_size=12, color=SOFT_WHITE).next_to(base, DOWN, buff=0.1)
    score_mob = DecimalNumber(score, num_decimal_places=2, font_size=21, color=color)
    score_mob.next_to(bar, UP, buff=0.08)
    return VGroup(base, bar, name, score_mob)


class Chapter4Scene(VoiceoverScene):
    """Chapter 4: 3D Multi-Block Masking and multi-mask prediction."""

    def construct(self):
        self.camera.background_color = BG_COLOR
        self.set_speech_service(
            GenericEdgeTTS(gender="male", accent="uk"),
            create_subcaption=False,
        )
        self._srt_entries = []

        self.act1_title()
        self.act2_temporal_leakage()
        self.act3_sample_spatial_block()
        self.act4_union_and_extrusion()
        self.act5_short_range_mask()
        self.act6_long_range_and_ablations()
        self.act7_multi_mask_prediction()
        self.act8_recap()
        self._write_srt()

    def _track_subtitle(self, text):
        tracker = getattr(self, "_current_tracker", None)
        if tracker is None:
            return

        boundaries = tracker.data.get("word_boundaries", [])
        if len(boundaries) < 2:
            boundaries = self._fallback_word_boundaries(text, tracker.duration)

        groups = []
        group_start = 0
        for index, boundary in enumerate(boundaries):
            next_offset = (
                boundaries[index + 1]["text_offset"]
                if index + 1 < len(boundaries)
                else len(text)
            )
            preview = text[boundaries[group_start]["text_offset"]:next_offset].strip()
            word_count = index - group_start + 1
            sentence_end = bool(re.search(r"[.!?][\"']?$", preview))
            if word_count >= 7 or len(preview) >= 44 or (word_count >= 4 and sentence_end):
                groups.append((group_start, index))
                group_start = index + 1

        if group_start < len(boundaries):
            groups.append((group_start, len(boundaries) - 1))

        for group_index, (start_index, _) in enumerate(groups):
            start_boundary = boundaries[start_index]
            text_start = start_boundary["text_offset"]
            if group_index + 1 < len(groups):
                next_start_index = groups[group_index + 1][0]
                text_end = boundaries[next_start_index]["text_offset"]
                relative_end = max(
                    start_boundary["audio_offset"] / 10_000_000 + 0.35,
                    boundaries[next_start_index]["audio_offset"] / 10_000_000 - 0.04,
                )
            else:
                text_end = len(text)
                relative_end = tracker.duration

            caption = text[text_start:text_end].strip()
            lines = textwrap.wrap(
                caption,
                width=42,
                break_long_words=False,
                break_on_hyphens=False,
            )
            caption = "\n".join(lines[:2])
            relative_start = start_boundary["audio_offset"] / 10_000_000
            start = float(tracker.start_t + relative_start)
            end = float(min(tracker.end_t, tracker.start_t + relative_end))
            if not caption or end <= start:
                continue

            self._srt_entries.append({"start": start, "end": end, "text": caption})
            self.add_subcaption(
                caption,
                duration=end - start,
                offset=start - float(self.time),
            )

    @staticmethod
    def _fallback_word_boundaries(text, duration):
        matches = list(re.finditer(r"\S+", text))
        if not matches:
            return []
        return [
            {
                "audio_offset": int(duration * 10_000_000 * index / len(matches)),
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
        srt_path = Path(__file__).resolve().parent.parent / "chapter4_subtitles.srt"
        with open(str(srt_path), "w", encoding="utf-8") as handle:
            for index, entry in enumerate(self._srt_entries, start=1):
                handle.write(f"{index}\n")
                handle.write(
                    f"{_format_srt_time(entry['start'])} --> "
                    f"{_format_srt_time(entry['end'])}\n"
                )
                handle.write(f"{entry['text']}\n\n")
        print(f"Subtitles written to {srt_path}")

    def _fade_scene(self, run_time=0.55):
        for mob in list(self.mobjects):
            mob.clear_updaters()
        if self.mobjects:
            self.play(
                *[FadeOut(mob) for mob in list(self.mobjects)],
                run_time=run_time,
            )
        self.clear()

    def act1_title(self):
        number = spaced_text("4", font_size=76, color=SOFT_WHITE, weight=BOLD)
        title = spaced_text("3D Multi-Block Masking", font_size=31, color=SOFT_WHITE, weight=BOLD)
        subtitle = spaced_text("Make the prediction task non-trivial", font_size=17, color=DIM_GRAY)
        title_group = VGroup(number, title, subtitle).arrange(DOWN, buff=0.23)
        underline = Line(title.get_left(), title.get_right(), color=SHORT_MASK, stroke_width=2)
        underline.next_to(title, DOWN, buff=0.12)

        tiles = VGroup(*[
            Square(
                side_length=0.18,
                stroke_color=GRID_GRAY,
                stroke_width=0.7,
                fill_color=SHORT_MASK if index in (1, 2, 5, 6) else DEEP_MASK,
                fill_opacity=0.7 if index in (1, 2, 5, 6) else 0.2,
            )
            for index in range(9)
        ]).arrange_in_grid(3, 3, buff=0.03)
        layers = VGroup(*[
            tiles.copy().shift(RIGHT * 0.18 * layer + UP * 0.12 * layer).set_opacity(0.2 + 0.14 * layer)
            for layer in range(5)
        ]).scale(0.82).next_to(subtitle, DOWN, buff=0.35)

        voice_text = (
            "Chapter Four builds the mask that makes video prediction difficult: "
            "three-dimensional multi-block masking."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration
            self.play(FadeIn(number, scale=0.65), FadeIn(title, shift=UP * 0.12), run_time=_rt(dur, 0.0, 0.34))
            self.play(Create(underline), FadeIn(subtitle), run_time=_rt(dur, 0.30, 0.62))
            self.play(FadeIn(layers, lag_ratio=0.12), run_time=_rt(dur, 0.58, 0.94))
        self._fade_scene()

    def act2_temporal_leakage(self):
        frames = VGroup(
            build_lake_frame(r"t-1", boat_shift=-0.32),
            build_lake_frame(r"t", boat_shift=0.0),
            build_lake_frame(r"t+1", boat_shift=0.32),
        ).arrange(RIGHT, buff=0.42).scale(0.92).move_to(UP * 0.55)

        mask_offsets = [LEFT * 0.55 + UP * 0.2, RIGHT * 0.15 + DOWN * 0.05, RIGHT * 0.58 + UP * 0.18]
        masks = VGroup()
        for frame, offset in zip(frames, mask_offsets):
            patch = Rectangle(
                width=0.72,
                height=0.58,
                stroke_color=LONG_MASK,
                stroke_width=1.5,
                fill_color=DEEP_MASK,
                fill_opacity=0.94,
            ).move_to(frame[0].get_center() + offset)
            masks.add(patch)

        leak_left = CurvedArrow(
            masks[0].get_center(), masks[1].get_center(), angle=-0.18,
            color=LEAK_GREEN, stroke_width=3, tip_length=0.16,
        )
        leak_right = CurvedArrow(
            masks[2].get_center(), masks[1].get_center(), angle=0.18,
            color=LEAK_GREEN, stroke_width=3, tip_length=0.16,
        )
        shortcut = spaced_text("temporal shortcut", font_size=18, color=LEAK_GREEN, weight=BOLD)
        shortcut.next_to(frames, UP, buff=0.24)
        formula = MathTex(
            r"x_{t,h,w}\ \longleftarrow\ \{x_{t-1,h,w},x_{t+1,h,w}\}",
            font_size=31,
            color=SOFT_WHITE,
        ).move_to(DOWN * 1.65)
        warning = spaced_text(
            "independent masks leave the same place visible nearby",
            font_size=16,
            color=LONG_MASK,
        ).next_to(formula, DOWN, buff=0.2)

        voice_text = (
            "If each frame receives an independent random mask, video redundancy creates "
            "a shortcut. A hidden location at time t may remain visible immediately before "
            "or after it. The model can copy nearby appearance instead of learning scene "
            "structure or motion. The arrows show this leakage path, not a probability law: "
            "the missing token can be inferred from the same spatial location in adjacent frames."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration
            self.play(FadeIn(frames, lag_ratio=0.12), run_time=_rt(dur, 0.0, 0.2))
            self.play(FadeIn(masks, lag_ratio=0.2), run_time=_rt(dur, 0.18, 0.36))
            self.play(Create(leak_left), Create(leak_right), FadeIn(shortcut), run_time=_rt(dur, 0.34, 0.58))
            self.play(FadeIn(formula), run_time=_rt(dur, 0.56, 0.76))
            self.play(FadeIn(warning), Indicate(masks[1], color=LEAK_GREEN), run_time=_rt(dur, 0.74, 0.94))
        self._fade_scene()

    def act3_sample_spatial_block(self):
        grid = build_token_grid(cell_size=0.205).move_to(LEFT * 3.55 + UP * 0.05)
        grid_label = MathTex(r"H'\times W'=14\times14", font_size=26, color=CONTEXT_BLUE)
        grid_label.next_to(grid, UP, buff=0.22)

        scale = 0.15
        aspect_ratio = 0.84
        height, width = sample_block_shape(scale, aspect_ratio)
        top, left = 4, 4
        indices = block_indices(top, left, height, width)
        block = build_block_overlay(grid, indices, SHORT_MASK, opacity=0.68)
        border = build_block_border(grid, indices, SHORT_MASK)

        area_formula = MathTex(
            r"A_b=\lfloor sH'W'\rfloor,\quad r\sim\mathcal{U}(0.75,1.5)",
            font_size=29,
            color=SOFT_WHITE,
        ).move_to(RIGHT * 2.35 + UP * 2.05)
        shape_formula = VGroup(
            MathTex(
                r"h_b=\operatorname{clip}(\operatorname{round}\sqrt{A_b r},1,H')",
                font_size=25,
                color=SOFT_WHITE,
            ),
            MathTex(
                r"w_b=\operatorname{clip}(\operatorname{round}\sqrt{A_b/r},1,W')",
                font_size=25,
                color=SOFT_WHITE,
            ),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(RIGHT * 2.35 + UP * 0.7)
        shape_formula[0].set_color_by_tex("h_b", SHORT_MASK)
        shape_formula[1].set_color_by_tex("w_b", SHORT_MASK)

        number_line = NumberLine(
            x_range=[0.75, 1.5, 0.25],
            length=3.5,
            include_numbers=True,
            font_size=18,
            color=DIM_GRAY,
        ).move_to(RIGHT * 2.35 + DOWN * 0.55)
        ratio_dot = Dot(number_line.n2p(0.75), color=SHORT_MASK, radius=0.08)
        ratio_label = MathTex(r"r=h_b/w_b", font_size=24, color=SHORT_MASK).next_to(number_line, UP, buff=0.16)
        position_formula = MathTex(
            r"u\sim U_{\mathbb Z}[0,H'-h_b],\quad v\sim U_{\mathbb Z}[0,W'-w_b]",
            font_size=24,
            color=SOFT_WHITE,
        ).move_to(RIGHT * 2.35 + DOWN * 1.72)

        h_brace = Brace(border, LEFT, color=SHORT_MASK)
        w_brace = Brace(border, DOWN, color=SHORT_MASK)
        h_label = MathTex(r"h_b", font_size=22, color=SHORT_MASK).next_to(h_brace, LEFT, buff=0.08)
        w_label = MathTex(r"w_b", font_size=22, color=SHORT_MASK).next_to(w_brace, DOWN, buff=0.08)

        voice_text = (
            "A spatial block begins with area A b, the floor of scale s times the "
            "fourteen-by-fourteen lattice. Its aspect ratio r is sampled between zero "
            "point seven five and one point five. The implementation computes height "
            "and width with square roots, then rounds and clips them to the grid. Finally, "
            "integer coordinates u and v place the continuous rectangle. Rounding means "
            "its discrete area can differ slightly from the requested scale."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration
            self.play(FadeIn(grid), FadeIn(grid_label), FadeIn(area_formula), run_time=_rt(dur, 0.0, 0.2))
            self.play(FadeIn(number_line), FadeIn(ratio_label), FadeIn(ratio_dot), run_time=_rt(dur, 0.18, 0.36))
            self.play(ratio_dot.animate.move_to(number_line.n2p(aspect_ratio)), run_time=_rt(dur, 0.34, 0.48))
            self.play(FadeIn(shape_formula), run_time=_rt(dur, 0.46, 0.64))
            self.play(FadeIn(block), Create(border), GrowFromCenter(h_brace), GrowFromCenter(w_brace), FadeIn(h_label), FadeIn(w_label), run_time=_rt(dur, 0.62, 0.8))
            self.play(FadeIn(position_formula), Indicate(border, color=SHORT_MASK), run_time=_rt(dur, 0.78, 0.96))
        self._fade_scene()

    def act4_union_and_extrusion(self):
        grid = build_token_grid(cell_size=0.205).move_to(LEFT * 3.6 + UP * 0.05)
        specs = [(0, 0, 5, 6), (1, 5, 5, 6), (5, 1, 5, 6), (7, 7, 5, 6)]
        blocks = [block_indices(*spec) for spec in specs]
        block_overlays = VGroup(*[
            build_block_overlay(grid, indices, color, opacity=0.38)
            for indices, color in zip(blocks, [SHORT_MASK, PREDICTOR_ORANGE, PURPLE_ACCENT, LONG_MASK])
        ])
        block_borders = VGroup(*[
            build_block_border(grid, indices, color, stroke_width=1.7)
            for indices, color in zip(blocks, [SHORT_MASK, PREDICTOR_ORANGE, PURPLE_ACCENT, LONG_MASK])
        ])
        union = union_indices(blocks)
        union_overlay = build_block_overlay(grid, union, SHORT_MASK, opacity=0.58)

        union_formula = MathTex(
            r"S=\bigcup_{j=1}^{K}B_j",
            font_size=38,
            color=SHORT_MASK,
        ).move_to(RIGHT * 2.65 + UP * 1.75)
        overlap_formula = MathTex(
            r"\left|\bigcup_jB_j\right|\ne\sum_j|B_j|",
            font_size=30,
            color=SOFT_WHITE,
        ).move_to(RIGHT * 2.65 + UP * 0.75)

        frame_stack = VGroup()
        tunnel_masks = VGroup()
        front_center = RIGHT * 2.45 + DOWN * 0.55
        for layer in range(6):
            offset = RIGHT * layer * 0.34 + UP * layer * 0.19
            frame = Rectangle(
                width=3.0,
                height=1.9,
                stroke_color=CONTEXT_BLUE,
                stroke_width=1.1,
                stroke_opacity=0.35 + layer * 0.09,
                fill_opacity=0,
            ).move_to(front_center + offset)
            frame_stack.add(frame)
            for x_shift, y_shift, width, height in [(-0.72, 0.35, 0.72, 0.52), (0.18, 0.12, 0.88, 0.58), (0.72, -0.42, 0.62, 0.42)]:
                mask = Rectangle(
                    width=width,
                    height=height,
                    stroke_color=SHORT_MASK,
                    stroke_width=0.8,
                    fill_color=SHORT_MASK,
                    fill_opacity=0.3,
                ).move_to(frame.get_center() + RIGHT * x_shift + UP * y_shift)
                tunnel_masks.add(mask)

        time_arrow = Arrow(
            frame_stack[0].get_corner(DL) + DOWN * 0.22,
            frame_stack[-1].get_corner(DR) + DOWN * 0.22,
            color=CONTEXT_BLUE,
            stroke_width=2.2,
            buff=0.05,
        )
        time_label = MathTex(r"t=0\ \longrightarrow\ T'-1", font_size=23, color=CONTEXT_BLUE)
        time_label.next_to(time_arrow, DOWN, buff=0.08)
        extrusion_formula = MathTex(
            r"M=\{0,\ldots,T'-1\}\times S,\qquad \rho_t=100\%",
            font_size=29,
            color=SOFT_WHITE,
        ).move_to(UP * 2.75)

        voice_text = (
            "Several possibly overlapping blocks form one spatial mask by union. "
            "Overlap is counted once, so union area is not the sum of block areas. "
            "V-JEPA then copies this same spatial mask through every temporal token. "
            "Mathematically, M is every time index crossed with S. The temporal masking "
            "ratio is therefore one hundred percent, producing continuous masked tunnels "
            "and removing the adjacent-frame shortcut."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration
            self.play(FadeIn(grid), FadeIn(union_formula), run_time=_rt(dur, 0.0, 0.18))
            self.play(FadeIn(block_overlays, lag_ratio=0.12), Create(block_borders, lag_ratio=0.12), run_time=_rt(dur, 0.16, 0.38))
            self.play(FadeIn(overlap_formula), Indicate(block_overlays, color=SOFT_WHITE), run_time=_rt(dur, 0.36, 0.52))
            self.play(FadeOut(block_overlays), FadeOut(block_borders), FadeIn(union_overlay), run_time=_rt(dur, 0.5, 0.62))
            self.play(FadeOut(VGroup(grid, union_overlay, union_formula, overlap_formula)), FadeIn(frame_stack, lag_ratio=0.08), run_time=_rt(dur, 0.6, 0.76))
            self.play(FadeIn(tunnel_masks, lag_ratio=0.02), Create(time_arrow), FadeIn(time_label), FadeIn(extrusion_formula), run_time=_rt(dur, 0.74, 0.96))
        self._fade_scene()

    def act5_short_range_mask(self):
        grid = build_token_grid(cell_size=0.22).move_to(LEFT * 2.65 + UP * 0.05)
        height, width = sample_block_shape(0.15, 0.84)
        positions = [(0, 0), (0, 4), (0, 8), (4, 0), (4, 4), (4, 8), (8, 0), (8, 8)]
        blocks = [block_indices(top, left, height, width) for top, left in positions]
        overlays = VGroup(*[
            build_block_overlay(grid, indices, SHORT_MASK, opacity=0.42)
            for indices in blocks
        ])
        borders = VGroup(*[
            build_block_border(grid, indices, SHORT_MASK, stroke_width=1.3)
            for indices in blocks
        ])
        union = union_indices(blocks)
        final_union = build_block_overlay(grid, union, SHORT_MASK, opacity=0.68)
        visible = set(range(14 * 14)) - union
        context_glow = build_block_overlay(grid, visible, CONTEXT_BLUE, opacity=0.88, stroke_width=1.0)

        title = spaced_text("Short-range mask", font_size=28, color=SHORT_MASK, weight=BOLD)
        title.to_edge(UP, buff=0.35)
        params = VGroup(
            MathTex(r"K=8", font_size=34, color=SHORT_MASK),
            MathTex(r"s=0.15", font_size=34, color=SHORT_MASK),
            MathTex(r"r\sim\mathcal{U}(0.75,1.5)", font_size=30, color=SOFT_WHITE),
            MathTex(r"S_{\mathrm{short}}=\bigcup_{j=1}^{8}B_j", font_size=31, color=SOFT_WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.28).move_to(RIGHT * 2.5 + UP * 0.35)

        counter_value = DecimalNumber(0, num_decimal_places=1, font_size=34, color=SHORT_MASK)
        counter_label = spaced_text("% masked by union", font_size=14, color=DIM_GRAY)
        counter = VGroup(counter_value, counter_label).arrange(DOWN, buff=0.08)
        counter.move_to(RIGHT * 2.5 + DOWN * 1.55)
        count_label = spaced_text("0 / 8 blocks", font_size=16, color=SHORT_MASK)
        count_label.next_to(counter, DOWN, buff=0.18)

        cumulative = set()
        coverages = []
        for indices in blocks:
            cumulative.update(indices)
            coverages.append(100 * len(cumulative) / (14 * 14))

        voice_text = (
            "The short-range mask unions eight smaller blocks, each with spatial scale "
            "zero point one five. As blocks arrive, the counter measures the union, not "
            "eight times fifteen percent. Overlapping cells are counted only once. This "
            "sample reaches about eighty-nine percent coverage, close to the roughly "
            "ninety-percent training regime. Only a sparse blue context remains, forcing "
            "the encoder to connect evidence across many separated regions."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration
            self.play(FadeIn(title), FadeIn(grid), FadeIn(params), FadeIn(counter), FadeIn(count_label), run_time=_rt(dur, 0.0, 0.18))
            for index, (overlay, border, coverage) in enumerate(zip(overlays, borders, coverages), start=1):
                next_label = spaced_text(f"{index} / 8 blocks", font_size=16, color=SHORT_MASK).move_to(count_label)
                self.play(
                    FadeIn(overlay), Create(border),
                    counter_value.animate.set_value(coverage),
                    ReplacementTransform(count_label, next_label),
                    run_time=max(0.34, _rt(dur, 0.18, 0.68, fill=0.09)),
                )
                count_label = next_label
            self.play(FadeOut(overlays), FadeOut(borders), FadeIn(final_union), run_time=_rt(dur, 0.68, 0.8))
            self.play(FadeIn(context_glow), Indicate(context_glow, color=CONTEXT_BLUE), run_time=_rt(dur, 0.8, 0.96))
        self._fade_scene()

    def act6_long_range_and_ablations(self):
        short_grid = build_token_grid(cell_size=0.16).move_to(LEFT * 3.35 + UP * 0.25)
        long_grid = build_token_grid(cell_size=0.16).move_to(RIGHT * 3.35 + UP * 0.25)
        short_positions = [(0, 0), (0, 4), (0, 8), (4, 0), (4, 4), (4, 8), (8, 0), (8, 8)]
        short_blocks = [block_indices(top, left, 5, 6) for top, left in short_positions]
        short_union = union_indices(short_blocks)

        long_shape_a = sample_block_shape(0.70, 1.08)
        long_shape_b = sample_block_shape(0.70, 0.92)
        long_blocks = [
            block_indices(0, 0, *long_shape_a),
            block_indices(14 - long_shape_b[0], 14 - long_shape_b[1], *long_shape_b),
        ]
        long_union = union_indices(long_blocks)

        short_overlay = build_block_overlay(short_grid, short_union, SHORT_MASK, opacity=0.72)
        long_overlays = VGroup(*[
            build_block_overlay(long_grid, indices, LONG_MASK, opacity=0.46)
            for indices in long_blocks
        ])
        long_final = build_block_overlay(long_grid, long_union, LONG_MASK, opacity=0.72)

        short_title = spaced_text("Short-range", font_size=23, color=SHORT_MASK, weight=BOLD).next_to(short_grid, UP, buff=0.2)
        long_title = spaced_text("Long-range", font_size=23, color=LONG_MASK, weight=BOLD).next_to(long_grid, UP, buff=0.2)
        short_params = MathTex(r"8\times0.15", font_size=29, color=SHORT_MASK).next_to(short_grid, DOWN, buff=0.18)
        long_params = MathTex(r"2\times0.70", font_size=29, color=LONG_MASK).next_to(long_grid, DOWN, buff=0.18)
        ratio_formula = MathTex(
            r"\rho=\frac{|S|}{H'W'}\approx0.90,\qquad 1-\rho\approx0.10",
            font_size=33,
            color=SOFT_WHITE,
        ).move_to(DOWN * 2.05)
        comparison_group = VGroup(
            short_grid, long_grid, short_overlay, long_overlays, long_final,
            short_title, long_title, short_params, long_params, ratio_formula,
        )

        block_title = spaced_text("Block-size ablation", font_size=21, color=SOFT_WHITE, weight=BOLD)
        block_title.move_to(LEFT * 3.25 + UP * 2.25)
        block_bars = VGroup(
            make_simple_bar(0.50, 0.55, SHORT_MASK, "8 x 96", 0.50),
            make_simple_bar(0.47, 0.55, LONG_MASK, "1 x 192", 0.47),
        ).arrange(RIGHT, buff=0.55).move_to(LEFT * 3.25 + DOWN * 0.15)
        fixed_note = spaced_text("75% spatial, 100% temporal", font_size=13, color=DIM_GRAY)
        fixed_note.next_to(block_bars, DOWN, buff=0.38)

        temporal_title = spaced_text("Temporal coverage", font_size=21, color=SOFT_WHITE, weight=BOLD)
        temporal_title.move_to(RIGHT * 2.7 + UP * 2.25)
        temporal_bars = VGroup(
            make_simple_bar(0.50, 0.55, LEAK_GREEN, "100%", 0.50, width=0.8),
            make_simple_bar(0.22, 0.55, SHORT_MASK, "75%", 0.22, width=0.8),
            make_simple_bar(0.12, 0.55, LONG_MASK, "50%", 0.12, width=0.8),
        ).arrange(RIGHT, buff=0.38).move_to(RIGHT * 2.7 + DOWN * 0.15)
        temporal_note = spaced_text("at 90% spatial coverage", font_size=13, color=DIM_GRAY)
        temporal_note.next_to(temporal_bars, DOWN, buff=0.38)
        verdict = spaced_text("low coverage makes prediction trivial", font_size=18, color=LONG_MASK, weight=BOLD)
        verdict.move_to(DOWN * 2.05)
        ablation_group = VGroup(block_title, block_bars, fixed_note, temporal_title, temporal_bars, temporal_note, verdict)

        voice_text = (
            "The complementary long-range mask unions two much larger blocks of scale "
            "zero point seven. Both default strategies leave roughly ten percent context, "
            "but their geometry differs. The ablations clarify what matters. At fixed "
            "seventy-five-percent coverage, eight smaller blocks score zero point five zero, "
            "versus zero point four seven for one large block. More importantly, at ninety "
            "percent spatial coverage, reducing temporal coverage from one hundred to "
            "seventy-five or fifty percent drops accuracy from zero point five zero to zero "
            "point two two and zero point one two. Weak coverage makes prediction trivial."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration
            self.play(FadeIn(short_grid), FadeIn(long_grid), FadeIn(short_title), FadeIn(long_title), run_time=_rt(dur, 0.0, 0.14))
            self.play(FadeIn(short_overlay), FadeIn(long_overlays, lag_ratio=0.2), FadeIn(short_params), FadeIn(long_params), run_time=_rt(dur, 0.12, 0.3))
            self.play(FadeOut(long_overlays), FadeIn(long_final), FadeIn(ratio_formula), run_time=_rt(dur, 0.28, 0.42))
            self.play(FadeOut(comparison_group), FadeIn(block_title), FadeIn(fixed_note), run_time=_rt(dur, 0.4, 0.54))
            self.play(FadeIn(block_bars, lag_ratio=0.18), run_time=_rt(dur, 0.52, 0.68))
            self.play(FadeIn(temporal_title), FadeIn(temporal_note), FadeIn(temporal_bars, lag_ratio=0.15), run_time=_rt(dur, 0.66, 0.86))
            self.play(FadeIn(verdict), Indicate(temporal_bars[0], color=LEAK_GREEN), run_time=_rt(dur, 0.84, 0.97))
        self._fade_scene()

    def act7_multi_mask_prediction(self):
        title = spaced_text("Multi-Mask Prediction", font_size=27, color=SOFT_WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.28)

        clip = make_flow_box("full clip", r"x_L", CONTEXT_BLUE, width=1.45).move_to(LEFT * 5.45 + UP * 2.0)
        target_encoder = make_flow_box("Target Encoder", r"E_{\bar\theta}", TARGET_GRAY, width=2.2).move_to(LEFT * 1.4 + UP * 2.0)
        shared_target = make_flow_box("shared target", r"s_L", TARGET_GRAY, width=1.65).move_to(RIGHT * 2.45 + UP * 2.0)
        target_arrows = VGroup(
            Arrow(clip.get_right(), target_encoder.get_left(), color=TARGET_GRAY, buff=0.08, stroke_width=2.2),
            Arrow(target_encoder.get_right(), shared_target.get_left(), color=TARGET_GRAY, buff=0.08, stroke_width=2.2),
        )

        lane_specs = [
            ("short", SHORT_MASK, 0.48, r"M_s", r"N_s"),
            ("long", LONG_MASK, -0.98, r"M_l", r"N_l"),
        ]
        lanes = VGroup()
        gather_arrows = VGroup()
        compare_lines = VGroup()
        for name, color, y_pos, mask_formula, visible_formula in lane_specs:
            mask_box = make_flow_box(f"{name} mask", mask_formula, color, width=1.5).move_to(LEFT * 5.45 + UP * y_pos)
            context_box = make_flow_box("Context", r"E_\theta", CONTEXT_BLUE, width=1.65).move_to(LEFT * 3.25 + UP * y_pos)
            predictor_box = make_flow_box("Predictor", r"P_\phi", PREDICTOR_ORANGE, width=1.65).move_to(LEFT * 0.8 + UP * y_pos)
            prediction = make_flow_box("prediction", r"\hat{s}_{M_q}", PREDICTOR_ORANGE, width=1.55).move_to(RIGHT * 1.55 + UP * y_pos)
            target = make_flow_box("gathered", r"s_{M_q}", TARGET_GRAY, width=1.55).move_to(RIGHT * 4.55 + UP * y_pos)
            visible_tag = MathTex(visible_formula, font_size=19, color=CONTEXT_BLUE).next_to(context_box, UP, buff=0.08)
            arrows = VGroup(
                Arrow(mask_box.get_right(), context_box.get_left(), color=CONTEXT_BLUE, buff=0.07, stroke_width=2),
                Arrow(context_box.get_right(), predictor_box.get_left(), color=CONTEXT_BLUE, buff=0.07, stroke_width=2),
                Arrow(predictor_box.get_right(), prediction.get_left(), color=PREDICTOR_ORANGE, buff=0.07, stroke_width=2),
            )
            gather = CurvedArrow(
                shared_target.get_bottom() + RIGHT * (0.08 if name == "long" else -0.08),
                target.get_top(),
                angle=-0.35 if name == "short" else -0.55,
                color=TARGET_GRAY,
                stroke_width=1.8,
                tip_length=0.13,
            )
            comparison = DashedLine(
                prediction.get_right(), target.get_left(),
                color=SOFT_WHITE, dash_length=0.1, stroke_width=1.6,
            )
            lanes.add(VGroup(mask_box, context_box, predictor_box, prediction, target, visible_tag, arrows))
            gather_arrows.add(gather)
            compare_lines.add(comparison)

        equation = MathTex(
            r"z_{N_q}=E_\theta(x_{N_q}),\quad "
            r"{}\hat{s}_{M_q}=P_\phi(z_{N_q},\{m+p_i\}_{i\in M_q}),\quad "
            r"{}s_{M_q}=\operatorname{Gather}(s_L,M_q)",
            font_size=22,
            color=SOFT_WHITE,
        ).move_to(DOWN * 2.12)
        pipeline_group = VGroup(title, clip, target_encoder, shared_target, target_arrows, lanes, gather_arrows, compare_lines, equation)

        cost_title = spaced_text("Amortise the target computation", font_size=25, color=SOFT_WHITE, weight=BOLD)
        cost_title.to_edge(UP, buff=0.45)
        cost_equations = VGroup(
            MathTex(r"C_{\mathrm{naive}}=2(C_T+C_C+C_P)", font_size=31, color=LONG_MASK),
            MathTex(r"C_{\mathrm{multi}}=C_T+2(C_C+C_P)", font_size=31, color=LEAK_GREEN),
        ).arrange(DOWN, buff=0.25).move_to(LEFT * 2.9 + UP * 0.95)
        pass_table = VGroup(
            spaced_text("forward passes", font_size=15, color=DIM_GRAY, weight=BOLD),
            spaced_text("Target       2  ->  1", font_size=18, color=TARGET_GRAY),
            spaced_text("Context      2  ->  2", font_size=18, color=CONTEXT_BLUE),
            spaced_text("Predictor    2  ->  2", font_size=18, color=PREDICTOR_ORANGE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(LEFT * 2.9 + DOWN * 1.0)

        mask_bars = VGroup(
            make_simple_bar(0.50, 0.6, DIM_GRAY, "1 mask", 0.50, width=0.75, max_height=1.45),
            make_simple_bar(0.55, 0.6, SHORT_MASK, "2 masks", 0.55, width=0.75, max_height=1.45),
            make_simple_bar(0.55, 0.6, LONG_MASK, "3 masks", 0.55, width=0.75, max_height=1.45),
        ).arrange(RIGHT, buff=0.34).move_to(RIGHT * 3.3 + UP * 0.05)
        mask_bar_title = spaced_text("masks per sample", font_size=20, color=SOFT_WHITE, weight=BOLD)
        mask_bar_title.next_to(mask_bars, UP, buff=0.3)
        target_saving = spaced_text("50% fewer Target forward passes", font_size=17, color=LEAK_GREEN, weight=BOLD)
        target_saving.move_to(DOWN * 2.05)
        cost_group = VGroup(cost_title, cost_equations, pass_table, mask_bars, mask_bar_title, target_saving)

        voice_text = (
            "For one clip, V-JEPA samples both short and long masks. The complete clip "
            "enters the Target Encoder once, producing shared representation s L. Each "
            "mask still requires its own Context Encoder and Predictor pass. Gather then "
            "selects the matching target positions for each prediction. If target computation "
            "were repeated, cost would be twice the sum of all three branches. Multi-mask "
            "keeps one target cost and two context-predictor costs. This halves Target forward "
            "passes, not total training compute. In the paper's ablation, one, two, and three "
            "masks score zero point five zero, zero point five five, and zero point five five, "
            "supporting two complementary masks as the default."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration
            self.play(FadeIn(title), FadeIn(clip), FadeIn(target_encoder), FadeIn(shared_target), run_time=_rt(dur, 0.0, 0.13))
            self.play(Create(target_arrows), run_time=_rt(dur, 0.11, 0.22))
            self.play(FadeIn(lanes[0][:-1]), Create(lanes[0][-1]), run_time=_rt(dur, 0.2, 0.34))
            self.play(FadeIn(lanes[1][:-1]), Create(lanes[1][-1]), run_time=_rt(dur, 0.32, 0.46))
            self.play(Create(gather_arrows), Create(compare_lines), FadeIn(equation), run_time=_rt(dur, 0.44, 0.58))
            self.play(FadeOut(pipeline_group), FadeIn(cost_title), FadeIn(cost_equations), run_time=_rt(dur, 0.56, 0.7))
            self.play(FadeIn(pass_table, lag_ratio=0.12), FadeIn(target_saving), run_time=_rt(dur, 0.68, 0.82))
            self.play(FadeIn(mask_bar_title), FadeIn(mask_bars, lag_ratio=0.16), run_time=_rt(dur, 0.8, 0.96))
        self._fade_scene()

    def act8_recap(self):
        items = VGroup()
        specs = [
            ("spatial union", r"S=\bigcup_jB_j", SHORT_MASK),
            ("temporal extrusion", r"M=\{0,\ldots,T'-1\}\times S", CONTEXT_BLUE),
            ("shared target", r"1\times E_{\bar\theta}(x_L)", TARGET_GRAY),
        ]
        for label, formula, color in specs:
            items.add(make_flow_box(label, formula, color, width=3.45, height=1.0))
        items.arrange(RIGHT, buff=0.45).scale(0.92).move_to(UP * 0.62)
        arrows = VGroup(*[
            Arrow(left.get_right(), right.get_left(), color=DIM_GRAY, buff=0.07, stroke_width=2)
            for left, right in zip(items[:-1], items[1:])
        ])
        facts = VGroup(
            spaced_text("~90% masked", font_size=22, color=SHORT_MASK, weight=BOLD),
            spaced_text("~10% context", font_size=22, color=CONTEXT_BLUE, weight=BOLD),
            spaced_text("1 shared Target pass", font_size=22, color=TARGET_GRAY, weight=BOLD),
        ).arrange(RIGHT, buff=0.75).move_to(DOWN * 0.78)
        bridge = spaced_text(
            "Next: how predictions become a learning signal",
            font_size=22,
            color=SOFT_WHITE,
            weight=BOLD,
        ).move_to(DOWN * 1.75)

        voice_text = (
            "Chapter Four leaves three precise ideas. Spatial blocks are united, that "
            "union is extruded through every time step, and two masks share one Target "
            "Encoder result. Roughly ninety percent is hidden while ten percent remains "
            "as context. Next, Chapter Five defines how predictions and targets become "
            "a learning signal."
        )
        recap_group = VGroup(items, arrows, facts, bridge)
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration
            self.play(FadeIn(items[0]), run_time=_rt(dur, 0.0, 0.18))
            self.play(Create(arrows[0]), FadeIn(items[1]), run_time=_rt(dur, 0.16, 0.36))
            self.play(Create(arrows[1]), FadeIn(items[2]), run_time=_rt(dur, 0.34, 0.54))
            self.play(FadeIn(facts, lag_ratio=0.18), run_time=_rt(dur, 0.52, 0.76))
            self.play(FadeIn(bridge, shift=UP * 0.12), run_time=_rt(dur, 0.74, 0.95))
        self.play(FadeOut(recap_group), run_time=0.75)
        self.clear()


class Chapter4LayoutPreview(Scene):
    """Voice-free static layout check for the densest Chapter 4 compositions."""

    def construct(self):
        self.camera.background_color = BG_COLOR
        title = spaced_text("Chapter 4 layout check", font_size=24, color=SOFT_WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.3)

        short_grid = build_token_grid(cell_size=0.115).move_to(LEFT * 4.7 + UP * 0.4)
        long_grid = build_token_grid(cell_size=0.115).move_to(LEFT * 2.55 + UP * 0.4)
        short_blocks = [
            block_indices(top, left, 5, 6)
            for top, left in [(0, 0), (0, 4), (0, 8), (4, 0), (4, 4), (4, 8), (8, 0), (8, 8)]
        ]
        long_blocks = [block_indices(0, 0, 12, 11), block_indices(2, 3, 12, 11)]
        short_overlay = build_block_overlay(short_grid, union_indices(short_blocks), SHORT_MASK, opacity=0.72)
        long_overlay = build_block_overlay(long_grid, union_indices(long_blocks), LONG_MASK, opacity=0.72)
        short_label = MathTex(r"8\times0.15", font_size=22, color=SHORT_MASK).next_to(short_grid, DOWN, buff=0.12)
        long_label = MathTex(r"2\times0.70", font_size=22, color=LONG_MASK).next_to(long_grid, DOWN, buff=0.12)

        equations = VGroup(
            MathTex(r"S=\bigcup_jB_j", font_size=25, color=SHORT_MASK),
            MathTex(r"M=\{0,\ldots,T'-1\}\times S", font_size=25, color=CONTEXT_BLUE),
            MathTex(r"\rho=|S|/(H'W')\approx0.90", font_size=25, color=SOFT_WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(RIGHT * 1.0 + UP * 0.55)

        target = make_flow_box("Target once", r"s_L", TARGET_GRAY, width=1.7).move_to(RIGHT * 4.65 + UP * 1.45)
        short_lane = make_flow_box("short lane", r"E_\theta\to P_\phi", SHORT_MASK, width=2.25).move_to(RIGHT * 4.65 + UP * 0.15)
        long_lane = make_flow_box("long lane", r"E_\theta\to P_\phi", LONG_MASK, width=2.25).move_to(RIGHT * 4.65 + DOWN * 1.05)
        arrows = VGroup(
            CurvedArrow(
                target.get_left() + DOWN * 0.08,
                short_lane.get_right(),
                angle=0.42,
                color=TARGET_GRAY,
                tip_length=0.12,
            ),
            CurvedArrow(
                target.get_right() + DOWN * 0.08,
                long_lane.get_right(),
                angle=-0.48,
                color=TARGET_GRAY,
                tip_length=0.12,
            ),
        )
        safe_line = DashedLine(
            LEFT * 6.8 + UP * SUBTITLE_SAFE_Y,
            RIGHT * 6.8 + UP * SUBTITLE_SAFE_Y,
            color=DIM_GRAY,
            stroke_opacity=0.35,
        )
        safe_label = spaced_text("subtitle-safe zone", font_size=12, color=DIM_GRAY)
        safe_label.next_to(safe_line, DOWN, buff=0.08)

        # Construct every dense formula once so the preview also catches TeX errors.
        _formula_compile_checks = VGroup(
            MathTex(r"x_{t,h,w}\longleftarrow\{x_{t-1,h,w},x_{t+1,h,w}\}"),
            MathTex(r"A_b=\lfloor sH'W'\rfloor,\quad r\sim\mathcal U(0.75,1.5)"),
            MathTex(r"h_b=\operatorname{clip}(\operatorname{round}\sqrt{A_b r},1,H')"),
            MathTex(r"w_b=\operatorname{clip}(\operatorname{round}\sqrt{A_b/r},1,W')"),
            MathTex(r"u\sim U_{\mathbb Z}[0,H'-h_b],\quad v\sim U_{\mathbb Z}[0,W'-w_b]"),
            MathTex(r"\left|\bigcup_jB_j\right|\ne\sum_j|B_j|"),
            MathTex(r"M=\{0,\ldots,T'-1\}\times S,\qquad\rho_t=100\%"),
            MathTex(
                r"z_{N_q}=E_\theta(x_{N_q}),\quad "
                r"{}\hat{s}_{M_q}=P_\phi(z_{N_q},\{m+p_i\}_{i\in M_q}),\quad "
                r"{}s_{M_q}=\operatorname{Gather}(s_L,M_q)"
            ),
            MathTex(r"C_{\mathrm{naive}}=2(C_T+C_C+C_P)"),
            MathTex(r"C_{\mathrm{multi}}=C_T+2(C_C+C_P)"),
        )
        _formula_compile_checks.set_opacity(0)

        self.add(
            title, short_grid, long_grid, short_overlay, long_overlay,
            short_label, long_label, equations, target, short_lane, long_lane,
            arrows, safe_line, safe_label,
        )


class Chapter4DryRunScene(Chapter4Scene):
    """Fast visual-only execution check; production renders use Chapter4Scene."""

    def set_speech_service(self, *args, **kwargs):
        return None

    @contextmanager
    def voiceover(self, text, **kwargs):
        tracker = type("DryTracker", (), {"duration": 3.2})()
        yield tracker

    def _track_subtitle(self, text):
        return None

    def _write_srt(self):
        return None

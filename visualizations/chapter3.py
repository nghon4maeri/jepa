"""
V-JEPA Video - Chapter 3: Architecture & Tokenization
Style: 3Blue1Brown-inspired Manim
Voiceover: English, Generic TTS male UK accent

This chapter assumes Chapter 1 already explained images, video tensors,
matrices, and RGB channels. It starts directly from the known input clip
shape and focuses only on V-JEPA tokenization and the three-part architecture.
"""

from pathlib import Path
from contextlib import contextmanager
import re
import textwrap

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from generic_tts import GenericEdgeTTS


# Development render target: Manim -ql equivalent.
config.pixel_height = 480
config.pixel_width = 854
config.frame_rate = 15


BG_COLOR = ManimColor("#1a1a2e")
CONTEXT_BLUE = ManimColor("#5DADE2")
PREDICTOR_ORANGE = ManimColor("#E59866")
TARGET_GRAY = ManimColor("#AAB7B8")
HIGHLIGHT_YELLOW = ManimColor("#F4D03F")
TOKEN_GREEN = ManimColor("#58D68D")
STOP_GRAD_RED = ManimColor("#E74C3C")
PURPLE_ACCENT = ManimColor("#AF7AC5")
SOFT_WHITE = ManimColor("#E8E8E8")
DIM_GRAY = ManimColor("#888888")
DEEP_MASK = ManimColor("#242436")


def spaced_text(*args, spacing=1.14, **kwargs):
    text = Text(*args, **kwargs)
    text.stretch(spacing, 0)
    return text


def _rt(duration, start_frac, end_frac, fill=0.86, floor=0.35):
    window = max(0.0, end_frac - start_frac) * duration * fill
    return max(floor, window)


def _format_srt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def make_module(title, formula, color, width=2.45, height=1.1):
    title_mob = spaced_text(title, font_size=18, color=color, weight=BOLD)
    formula_mob = MathTex(formula, font_size=25, color=SOFT_WHITE)
    content = VGroup(title_mob, formula_mob).arrange(DOWN, buff=0.12)
    box = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.08,
        stroke_color=color,
        stroke_width=2,
        fill_color=color,
        fill_opacity=0.11,
    )
    content.move_to(box)
    return VGroup(box, content)


def make_token_row(count=24, color=TOKEN_GREEN, radius=0.055, gap=0.18):
    dots = VGroup()
    for index in range(count):
        dot = Dot(radius=radius, color=color)
        dot.move_to(RIGHT * (index * gap))
        dots.add(dot)
    dots.center()
    return dots


def make_isometric_clip():
    front = Rectangle(
        width=3.35,
        height=2.15,
        stroke_color=CONTEXT_BLUE,
        stroke_width=2,
        fill_color=CONTEXT_BLUE,
        fill_opacity=0.08,
    )
    offset = np.array([0.42, 0.28, 0.0])

    layers = VGroup()
    for index in range(6):
        layer = Rectangle(
            width=3.35,
            height=2.15,
            stroke_color=CONTEXT_BLUE,
            stroke_width=1.2,
            stroke_opacity=0.35 + 0.07 * index,
            fill_color=CONTEXT_BLUE,
            fill_opacity=0.035,
        )
        layer.move_to(front.get_center() + offset * (index + 1))
        layers.add(layer)

    edges = VGroup()
    for corner in (UR, UL, DR, DL):
        edges.add(
            Line(
                front.get_corner(corner),
                layers[-1].get_corner(corner),
                color=CONTEXT_BLUE,
                stroke_width=1.1,
                stroke_opacity=0.55,
            )
        )

    clip = VGroup(layers, front, edges)
    clip.set_z_index(1)
    return clip


def make_feature_grid(rows=4, cols=7):
    cells = VGroup()
    for row in range(rows):
        for col in range(cols):
            cell = RoundedRectangle(
                width=0.28,
                height=0.22,
                corner_radius=0.035,
                stroke_color=TOKEN_GREEN,
                stroke_width=1,
                stroke_opacity=0.65,
                fill_color=TOKEN_GREEN,
                fill_opacity=0.16,
            )
            cell.move_to(RIGHT * col * 0.34 + DOWN * row * 0.28)
            cells.add(cell)
    cells.arrange_in_grid(rows=rows, cols=cols, buff=(0.06, 0.06))

    back = cells.copy().shift(RIGHT * 0.35 + UP * 0.25)
    back.set_stroke(opacity=0.35)
    back.set_fill(opacity=0.06)
    grid = VGroup(back, cells).center()
    return grid


def make_sine_curve(color, shift_y):
    curve = FunctionGraph(
        lambda x: 0.18 * np.sin(2.2 * x),
        x_range=[-2.4, 2.4],
        color=color,
        stroke_width=2.2,
    )
    curve.shift(UP * shift_y)
    return curve


def make_filter_cuboid():
    front = Square(
        side_length=0.62,
        stroke_color=HIGHLIGHT_YELLOW,
        stroke_width=2,
        fill_color=HIGHLIGHT_YELLOW,
        fill_opacity=0.14,
    )
    front.stretch(1.25, 0)
    front.stretch(0.75, 1)
    offset = RIGHT * 0.22 + UP * 0.16
    back = front.copy().shift(offset)
    back.set_stroke(opacity=0.55)
    back.set_fill(opacity=0.06)
    edges = VGroup()
    for corner in (UR, UL, DR, DL):
        edges.add(
            Line(
                front.get_corner(corner),
                back.get_corner(corner),
                color=HIGHLIGHT_YELLOW,
                stroke_width=1.4,
                stroke_opacity=0.7,
            )
        )
    return VGroup(back, front, edges)


class Chapter3Scene(VoiceoverScene):
    """Chapter 3: Tokenization and the three-part V-JEPA architecture."""

    def construct(self):
        self.camera.background_color = BG_COLOR
        self.set_speech_service(
            GenericEdgeTTS(gender="male", accent="uk"),
            create_subcaption=False,
        )
        self._srt_entries = []

        self.clip_group = None
        self.feature_grid = None
        self.token_row = None
        self.split_group = None
        self.architecture_group = None

        self.act1_title()
        self.act2_known_input()
        self.act3_conv3d_scan()
        self.act4_feature_grid()
        self.act5_positional_embedding()
        self.act6_flatten_tokens()
        self.act7_visible_and_mask_tokens()
        self.act8_three_component_architecture()
        self.act9_latent_prediction_match()
        self.act10_recap_bridge()
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
            preview = text[
                boundaries[group_start]["text_offset"]:next_offset
            ].strip()
            word_count = index - group_start + 1
            sentence_end = bool(re.search(r"[.!?][\"']?$", preview))
            if word_count >= 7 or len(preview) >= 44 or (word_count >= 4 and sentence_end):
                groups.append((group_start, index))
                group_start = index + 1

        if group_start < len(boundaries):
            groups.append((group_start, len(boundaries) - 1))

        for group_index, (start_index, end_index) in enumerate(groups):
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
            caption_lines = textwrap.wrap(
                caption,
                width=42,
                break_long_words=False,
                break_on_hyphens=False,
            )
            caption = "\n".join(caption_lines)
            relative_start = start_boundary["audio_offset"] / 10_000_000
            start = float(tracker.start_t + relative_start)
            end = float(min(tracker.end_t, tracker.start_t + relative_end))
            if not caption or end <= start:
                continue

            entry = {"start": start, "end": end, "text": caption}
            self._srt_entries.append(entry)
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
        srt_path = Path(__file__).resolve().parent.parent / "chapter3_subtitles.srt"
        with open(str(srt_path), "w", encoding="utf-8") as handle:
            for index, entry in enumerate(self._srt_entries, start=1):
                handle.write(f"{index}\n")
                handle.write(
                    f"{_format_srt_time(entry['start'])} --> "
                    f"{_format_srt_time(entry['end'])}\n"
                )
                handle.write(f"{entry['text']}\n\n")
        print(f"Subtitles written to {srt_path}")

    def _fade_group(self, group, run_time=0.55):
        if group is not None and len(group) > 0:
            self.play(FadeOut(group, run_time=run_time))

    def _fade_scene(self, run_time=0.55):
        if self.mobjects:
            self.play(
                *[FadeOut(mobject) for mobject in list(self.mobjects)],
                run_time=run_time,
            )
        self.clear()

    def act1_title(self):
        number = spaced_text("3", font_size=74, color=SOFT_WHITE, weight=BOLD)
        title = spaced_text(
            "Architecture & Tokenization",
            font_size=28,
            color=SOFT_WHITE,
            weight=BOLD,
        )
        subtitle = spaced_text(
            "From latent prediction to actual data flow",
            font_size=16,
            color=DIM_GRAY,
        )
        title_group = VGroup(number, title, subtitle).arrange(DOWN, buff=0.25)
        underline = Line(
            title.get_left() + DOWN * 0.18,
            title.get_right() + DOWN * 0.18,
            color=CONTEXT_BLUE,
            stroke_width=2,
        )
        color_dots = VGroup(
            Dot(color=CONTEXT_BLUE),
            Dot(color=TARGET_GRAY),
            Dot(color=PREDICTOR_ORANGE),
        ).arrange(RIGHT, buff=0.35)
        color_dots.next_to(subtitle, DOWN, buff=0.35)

        act_group = VGroup(title_group, underline, color_dots)
        self.play(FadeIn(number, scale=0.6), FadeIn(title, shift=UP * 0.15), run_time=0.9)
        self.play(FadeIn(subtitle, shift=UP * 0.1), Create(underline), run_time=0.8)
        self.play(FadeIn(color_dots, lag_ratio=0.25), run_time=0.7)
        self.wait(0.4)
        self._fade_group(act_group, run_time=0.55)

    def act2_known_input(self):
        clip = make_isometric_clip().move_to(LEFT * 1.65 + DOWN * 0.1)
        formula = MathTex(
            r"x \in \mathbb{R}^{16 \times 224 \times 224 \times 3}",
            font_size=32,
            color=SOFT_WHITE,
        ).to_edge(UP, buff=0.55)
        formula_box = SurroundingRectangle(formula, buff=0.18, color=CONTEXT_BLUE)

        sample_formula = MathTex(
            r"x_n=v_{f_0+4n},\quad n=0,\ldots,15",
            font_size=25,
            color=CONTEXT_BLUE,
        )
        source_span = spaced_text(
            "64 source frames  |  about 2 s at 30 fps",
            font_size=15,
            color=TOKEN_GREEN,
        )
        labels = VGroup(sample_formula, source_span).arrange(DOWN, buff=0.18)
        labels.next_to(clip, RIGHT, buff=0.65)

        tag = spaced_text(
            "not tokens yet",
            font_size=18,
            color=HIGHLIGHT_YELLOW,
            weight=BOLD,
        )
        tag.next_to(labels, DOWN, buff=0.35)
        tag_box = SurroundingRectangle(tag, buff=0.14, color=HIGHLIGHT_YELLOW)

        act_group = VGroup(clip, formula, formula_box, labels, tag, tag_box)
        voice_text = (
            "Now that we know why V-JEPA predicts in latent space, we can look at "
            "the exact route through the model. We reuse the established input shape "
            "without re-explaining its axes. During pretraining, sample n is taken "
            "from source frame f zero plus four n, for n from zero through fifteen. "
            "This temporal sampling stride of four makes the clip cover sixty-four "
            "source frames, roughly two seconds at thirty frames per second. The "
            "next operation turns this working block into space-time tokens."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration
            self.play(FadeIn(formula), Create(formula_box), run_time=_rt(dur, 0.00, 0.20))
            self.play(FadeIn(clip, shift=RIGHT * 0.2), run_time=_rt(dur, 0.18, 0.42))
            self.play(FadeIn(labels, lag_ratio=0.2), run_time=_rt(dur, 0.40, 0.62))
            self.play(FadeIn(tag), Create(tag_box), run_time=_rt(dur, 0.62, 0.78))
            self.play(clip.animate.scale(0.92).shift(LEFT * 0.2), rate_func=there_and_back, run_time=_rt(dur, 0.78, 0.94))

        self._fade_scene()
        self.clip_group = None

    def act3_conv3d_scan(self):
        clip = self.clip_group
        if clip is None:
            clip = make_isometric_clip().move_to(LEFT * 2.5)
            self.add(clip)

        clip.generate_target()
        clip.target.scale(0.82).move_to(LEFT * 3.75 + DOWN * 0.2)
        filter_box = make_filter_cuboid()
        filter_box.move_to(clip.target.get_center() + RIGHT * 0.15 + UP * 0.25)
        filter_label = spaced_text("3D Conv", font_size=19, color=HIGHLIGHT_YELLOW, weight=BOLD)
        filter_dims = MathTex(r"2 \times 16 \times 16", font_size=26, color=HIGHLIGHT_YELLOW)
        filter_text = VGroup(filter_label, filter_dims).arrange(DOWN, buff=0.08)
        filter_text.next_to(filter_box, UP, buff=0.2)
        filter_group = VGroup(filter_box, filter_text)

        stride_t = spaced_text("temporal stride = 2", font_size=15, color=CONTEXT_BLUE)
        stride_s = spaced_text("spatial stride = 16", font_size=15, color=TOKEN_GREEN)
        strides = VGroup(stride_t, stride_s).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        strides.to_edge(DOWN, buff=0.65).shift(LEFT * 3.1)

        tubelets = VGroup()
        tubelet_targets = [
            RIGHT * 0.3 + UP * 1.5,
            RIGHT * 1.0 + UP * 0.85,
            RIGHT * 1.55 + UP * 0.2,
            RIGHT * 2.0 + DOWN * 0.45,
            RIGHT * 2.45 + DOWN * 1.1,
            RIGHT * 2.9 + UP * 1.15,
        ]
        for target in tubelet_targets:
            cube = Square(
                side_length=0.26,
                stroke_color=TOKEN_GREEN,
                stroke_width=1.4,
                fill_color=TOKEN_GREEN,
                fill_opacity=0.28,
            )
            cube.rotate(PI / 4)
            cube.move_to(filter_box)
            cube.set_opacity(0)
            tubelets.add(cube)

        formula = MathTex(
            r"k=(k_t,k_h,k_w)=(2,16,16),\quad s=(2,16,16)",
            font_size=29,
            color=SOFT_WHITE,
        ).to_edge(UP, buff=0.45)
        output_shape_formula = MathTex(
            r"T'=\left\lfloor\frac{16-2}{2}\right\rfloor+1=8,\quad "
            r"H'=W'=\left\lfloor\frac{224-16}{16}\right\rfloor+1=14",
            font_size=25,
            color=TOKEN_GREEN,
        ).to_edge(UP, buff=0.45)
        embedding_formula = MathTex(
            r"e_{t,h,w}=W_e\,\mathrm{vec}(\tau_{t,h,w})+b_e,\quad "
            r"W_e\in\mathbb{R}^{d\times(2\cdot16\cdot16\cdot3)}",
            font_size=22,
            color=SOFT_WHITE,
        ).to_edge(UP, buff=0.45)

        act_group = VGroup(filter_group, strides, tubelets, formula)
        voice_text = (
            "The first operation is a three-dimensional convolution. A small filter "
            "with size two by sixteen by sixteen scans through time and space at the "
            "same time. Its temporal stride is two, so it advances through pairs of "
            "frames. Its spatial stride is sixteen, so each stop covers one sixteen "
            "by sixteen patch. Every stop extracts a small space-time cube, called a "
            "tubelet, and each of the d convolutional filters contributes one output "
            "channel. A tubelet spans two sampled instants, so its feature can encode "
            "local temporal evidence without claiming to reconstruct either frame. "
            "Formally, the output length on each "
            "axis is the floor of input size minus kernel size, divided by stride, "
            "plus one. That gives eight temporal positions and fourteen positions on "
            "each spatial axis. If tau at t, h, w denotes the selected tubelet, its "
            "flattened values are projected by W e and shifted by b e to produce the "
            "d-dimensional feature e at that position."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration
            self.play(MoveToTarget(clip), FadeIn(formula), run_time=_rt(dur, 0.00, 0.16))
            self.play(FadeIn(filter_group), FadeIn(strides), run_time=_rt(dur, 0.14, 0.30))

            scan_offsets = [RIGHT * 0.0, RIGHT * 0.5, RIGHT * 1.0 + DOWN * 0.18, RIGHT * 1.45 + UP * 0.22, RIGHT * 1.85 + DOWN * 0.35, RIGHT * 2.15]
            for index, offset in enumerate(scan_offsets):
                target_pos = clip.get_center() + LEFT * 0.05 + UP * 0.38 + offset * 0.38
                self.play(
                    filter_box.animate.move_to(target_pos),
                    filter_text.animate.move_to(target_pos + UP * 0.85),
                    run_time=max(0.35, _rt(dur, 0.30, 0.72, fill=0.10)),
                    rate_func=smooth,
                )
                self.play(
                    tubelets[index].animate.set_opacity(1).move_to(tubelet_targets[index]),
                    run_time=max(0.3, _rt(dur, 0.30, 0.72, fill=0.06)),
                )

            self.play(
                tubelets.animate.arrange(RIGHT, buff=0.18).move_to(RIGHT * 1.75 + DOWN * 1.7),
                ReplacementTransform(formula, output_shape_formula),
                run_time=_rt(dur, 0.72, 0.84),
            )
            self.play(
                ReplacementTransform(output_shape_formula, embedding_formula),
                tubelets.animate.set_fill(opacity=0.5),
                run_time=_rt(dur, 0.84, 0.96),
            )

        self._fade_scene()
        self.tubelets = VGroup()

    def act4_feature_grid(self):
        tubelets = getattr(self, "tubelets", VGroup())
        grid = make_feature_grid().scale(1.05).move_to(RIGHT * 0.95 + DOWN * 0.05)
        grid_label = MathTex(r"8 \times 14 \times 14 \times d", font_size=34, color=TOKEN_GREEN)
        grid_label.to_edge(UP, buff=0.45)

        counters = VGroup(
            MathTex(r"16 \rightarrow 8", font_size=27, color=CONTEXT_BLUE),
            MathTex(r"224 \rightarrow 14", font_size=27, color=TOKEN_GREEN),
            MathTex(r"224 \rightarrow 14", font_size=27, color=TOKEN_GREEN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        counters.next_to(grid, LEFT, buff=0.75)

        vector_tails = VGroup()
        for cell in grid[1][::5]:
            tail = Line(cell.get_center(), cell.get_center() + RIGHT * 0.35 + UP * 0.18, color=PURPLE_ACCENT, stroke_width=2)
            vector_tails.add(tail)
        d_label = MathTex(r"d", font_size=28, color=PURPLE_ACCENT).next_to(vector_tails, RIGHT, buff=0.15)
        index_formula = MathTex(
            r"G\in\mathbb{R}^{8\times14\times14\times d},\quad "
            r"G_{t,h,w}\in\mathbb{R}^{d}",
            font_size=27,
            color=SOFT_WHITE,
        ).move_to(DOWN * 2.35)

        act_group = VGroup(grid, grid_label, counters, vector_tails, d_label, index_formula)
        voice_text = (
            "After the convolution has swept across the clip, the result is not an "
            "image and not a reconstruction. It is a three-dimensional grid of "
            "feature vectors. Sixteen frames become eight temporal positions. Each "
            "two hundred and twenty-four pixel spatial side becomes fourteen patch "
            "positions. So the grid has shape eight by fourteen by fourteen, and "
            "each cell carries a d-dimensional feature vector. We can write the "
            "complete grid as G in R to the eight by fourteen by fourteen by d. "
            "A single indexed entry, G at t, h, w, is therefore one vector in R to d, "
            "rather than one scalar value."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration
            self.play(FadeIn(grid_label), run_time=_rt(dur, 0.00, 0.15))
            if len(tubelets) > 0:
                self.play(ReplacementTransform(tubelets.copy(), grid), run_time=_rt(dur, 0.12, 0.38))
                self.remove(tubelets)
            else:
                self.play(FadeIn(grid, scale=0.9), run_time=_rt(dur, 0.12, 0.38))
            self.play(FadeIn(counters, lag_ratio=0.25), run_time=_rt(dur, 0.38, 0.58))
            self.play(Create(vector_tails, lag_ratio=0.08), FadeIn(d_label), run_time=_rt(dur, 0.58, 0.74))
            self.play(FadeIn(index_formula, shift=UP * 0.1), run_time=_rt(dur, 0.74, 0.86))
            self.play(grid.animate.set_fill(opacity=0.25), rate_func=there_and_back, run_time=_rt(dur, 0.86, 0.97))

        self._fade_scene()
        self.feature_grid = None

    def act5_positional_embedding(self):
        grid = make_feature_grid().scale(1.08).move_to(RIGHT * 2.2 + DOWN * 0.1)
        grid_label = MathTex(
            r"G\in\mathbb{R}^{8\times14\times14\times d}",
            font_size=29,
            color=TOKEN_GREEN,
        ).next_to(grid, DOWN, buff=0.25)

        waves = VGroup(
            make_sine_curve(CONTEXT_BLUE, 0).scale(0.62),
            make_sine_curve(TOKEN_GREEN, 0).scale(0.62),
            make_sine_curve(PREDICTOR_ORANGE, 0).scale(0.62),
        ).arrange(DOWN, buff=0.38).move_to(LEFT * 3.55 + UP * 0.15)
        wave_labels = VGroup(
            spaced_text("time t", font_size=14, color=CONTEXT_BLUE),
            spaced_text("height h", font_size=14, color=TOKEN_GREEN),
            spaced_text("width w", font_size=14, color=PREDICTOR_ORANGE),
        )
        for wave, label in zip(waves, wave_labels):
            label.next_to(wave, LEFT, buff=0.16)

        pe_formula = MathTex(
            r"p_{t,h,w}=\big[PE_t(t)\,\Vert\,PE_h(h)\,\Vert\,PE_w(w)\big]_{1:d}",
            font_size=29,
            color=SOFT_WHITE,
        ).to_edge(UP, buff=0.38)
        frequency_formula = MathTex(
            r"\omega_k=10000^{-k/(d_a/2)},\quad "
            r"PE_a(u)=[\sin(u\omega)\,\Vert\,\cos(u\omega)]",
            font_size=23,
            color=PURPLE_ACCENT,
        ).move_to(DOWN * 2.25)
        final_formula = MathTex(
            r"\widetilde{G}_{t,h,w}=G_{t,h,w}+p_{t,h,w}",
            font_size=31,
            color=TOKEN_GREEN,
        ).to_edge(UP, buff=0.38)

        arrows = VGroup(*[
            Arrow(wave.get_right(), grid.get_left() + UP * offset, color=color, buff=0.16, stroke_width=2)
            for wave, offset, color in zip(
                waves,
                (0.55, 0.0, -0.55),
                (CONTEXT_BLUE, TOKEN_GREEN, PREDICTOR_ORANGE),
            )
        ])
        rings = VGroup()
        for index, cell in enumerate(grid[1][::4]):
            color = (CONTEXT_BLUE, TOKEN_GREEN, PREDICTOR_ORANGE)[index % 3]
            rings.add(SurroundingRectangle(cell, buff=0.025, color=color, stroke_width=2))

        act_group = VGroup(
            grid, grid_label, waves, wave_labels, pe_formula, frequency_formula,
            final_formula, arrows, rings,
        )
        voice_text = (
            "Before flattening, the paper adds an absolute three-dimensional sin-cos "
            "positional embedding to the space-time feature map. For one coordinate "
            "u, frequencies omega k form a geometric scale. Sine and cosine values "
            "encode that coordinate. The implementation constructs separate encodings "
            "for time, height, and width, concatenates them, and keeps d channels. "
            "This is an important correction: the three axis encodings are concatenated, "
            "not summed with one another. The resulting vector p at t, h, w is then "
            "added elementwise to feature G at the same grid position."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration
            self.play(FadeIn(grid), FadeIn(grid_label), FadeIn(pe_formula), run_time=_rt(dur, 0.00, 0.18))
            self.play(FadeIn(waves, lag_ratio=0.16), FadeIn(wave_labels, lag_ratio=0.16), run_time=_rt(dur, 0.18, 0.42))
            self.play(FadeIn(frequency_formula), Create(arrows, lag_ratio=0.16), run_time=_rt(dur, 0.42, 0.68))
            self.play(Create(rings, lag_ratio=0.08), run_time=_rt(dur, 0.68, 0.80))
            self.play(ReplacementTransform(pe_formula, final_formula), run_time=_rt(dur, 0.80, 0.91))
            self.play(rings.animate.set_stroke(width=3.5), rate_func=there_and_back, run_time=_rt(dur, 0.91, 0.98))

        self._fade_scene()

    def act6_flatten_tokens(self):
        grid = make_feature_grid().scale(0.86).move_to(LEFT * 4.45 + DOWN * 0.15)
        token_row = make_token_row(28).move_to(RIGHT * 1.25 + DOWN * 0.15)
        ellipsis = spaced_text("...", font_size=22, color=DIM_GRAY)
        ellipsis.next_to(token_row, RIGHT, buff=0.18)
        token_group = VGroup(token_row, ellipsis)
        flow_formula = MathTex(
            r"\widetilde{G}\in\mathbb{R}^{8\times14\times14\times d}"
            r"\xrightarrow{\mathrm{flatten}}x_L\in\mathbb{R}^{1568\times d}",
            font_size=29,
            color=SOFT_WHITE,
        ).to_edge(UP, buff=0.42)
        count_formula = MathTex(
            r"L=T'H'W'=8\cdot14\cdot14=1568",
            font_size=31,
            color=HIGHLIGHT_YELLOW,
        ).move_to(UP * 1.75)
        index_map = MathTex(
            r"\ell=196t+14h+w+1,\quad 1\leq\ell\leq L",
            font_size=26,
            color=CONTEXT_BLUE,
        ).move_to(DOWN * 1.45)
        sequence_formula = MathTex(
            r"x_L=(x_1,x_2,\ldots,x_L),\quad x_\ell\in\mathbb{R}^{d}",
            font_size=27,
            color=TOKEN_GREEN,
        ).move_to(DOWN * 2.1)
        flatten_arrow = Arrow(grid.get_right(), token_group.get_left(), color=HIGHLIGHT_YELLOW, buff=0.28, stroke_width=2.5)
        counter = DecimalNumber(0, num_decimal_places=0, font_size=31, color=HIGHLIGHT_YELLOW)
        counter.next_to(token_group, DOWN, buff=0.35)

        act_group = VGroup(
            grid, token_group, flow_formula, count_formula, index_map,
            sequence_formula, flatten_arrow, counter,
        )
        voice_text = (
            "Now flatten the position-aware grid in a fixed time, height, width order. "
            "The sequence length L is T prime times H prime times W prime: eight times "
            "fourteen times fourteen, exactly one thousand five hundred and sixty-eight. "
            "Using one-based paper notation, grid coordinate t, h, w maps to index ell "
            "equal to one hundred and ninety-six t plus fourteen h plus w plus one. "
            "The result x L is an ordered sequence from x one through x L, and every "
            "row remains a d-dimensional token. V-JEPA uses no class token during "
            "pretraining, so these fifteen hundred and sixty-eight patch tokens are "
            "the complete transformer input sequence."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration
            self.play(FadeIn(grid), FadeIn(flow_formula), run_time=_rt(dur, 0.00, 0.18))
            self.play(Create(flatten_arrow), ReplacementTransform(grid.copy(), token_row), FadeIn(ellipsis), run_time=_rt(dur, 0.18, 0.44))
            self.play(FadeIn(count_formula), ChangeDecimalToValue(counter, 1568), run_time=_rt(dur, 0.44, 0.67), rate_func=linear)
            self.play(FadeIn(index_map, shift=UP * 0.1), run_time=_rt(dur, 0.67, 0.82))
            self.play(FadeIn(sequence_formula, shift=UP * 0.1), run_time=_rt(dur, 0.82, 0.96))

        self._fade_scene()
        self.token_row = None

    def act7_visible_and_mask_tokens(self):
        token_row = self.token_row
        if token_row is None:
            dots = make_token_row(28)
            ellipsis = spaced_text("...", font_size=22, color=DIM_GRAY)
            ellipsis.next_to(dots, RIGHT, buff=0.18)
            token_row = VGroup(dots, ellipsis).move_to(DOWN * 0.4)
            self.add(token_row)

        full_lane = VGroup(token_row[0].copy(), token_row[1].copy())
        full_lane.scale(0.92).move_to(UP * 1.55)
        visible_tokens = VGroup()
        masked_slots = VGroup()
        mask_tokens = VGroup()
        for index, dot in enumerate(full_lane[0]):
            if index % 5 == 0:
                visible_tokens.add(dot.copy().set_color(CONTEXT_BLUE).shift(DOWN * 1.35))
            else:
                slot = Square(side_length=0.14, color=TARGET_GRAY, stroke_width=1.1)
                slot.move_to(dot.get_center() + DOWN * 1.35)
                slot.set_fill(DEEP_MASK, opacity=0.45)
                masked_slots.add(slot)
                mask = Dot(dot.get_center() + DOWN * 2.55, radius=0.055, color=PREDICTOR_ORANGE)
                mask_tokens.add(mask)

        full_label = MathTex(r"x_L", font_size=32, color=SOFT_WHITE).next_to(full_lane, LEFT, buff=0.35)
        context_lane = VGroup(visible_tokens, masked_slots)
        visible_label = MathTex(r"x_N\ (\text{about }10\%\ visible)", font_size=27, color=CONTEXT_BLUE).next_to(context_lane, LEFT, buff=0.3)
        mask_label = MathTex(r"m_M", font_size=32, color=PREDICTOR_ORANGE).next_to(mask_tokens, LEFT, buff=0.35)
        set_formula = MathTex(
            r"L=1568,\quad M=(i_1,\ldots,i_M),\quad N=L-M",
            font_size=28,
            color=SOFT_WHITE,
        ).to_edge(UP, buff=0.45)
        route_formula = MathTex(
            r"x_N=(x_{j_1},\ldots,x_{j_N}),\quad m_{i_k}=m+p_{i_k}",
            font_size=27,
            color=PREDICTOR_ORANGE,
        ).move_to(DOWN * 2.05)

        act_group = VGroup(full_lane, visible_tokens, masked_slots, mask_tokens, full_label, visible_label, mask_label, set_formula, route_formula)
        voice_text = (
            "The paper next separates the full sequence into indexed roles. L is one "
            "thousand five hundred and sixty-eight. The masked indices are i one "
            "through i M, while j one through j N are their complement, with N equal "
            "to L minus M. Only x at the j indices enters the Context Encoder as x N. "
            "With the paper's masking settings, this visible sequence is about ten "
            "percent of the tokens, but Chapter Four handles how those indices are "
            "sampled. For each requested index i k, the Predictor receives a mask token "
            "formed from a shared learnable vector m plus the absolute position code "
            "p at i k. No hidden pixel values are passed along this route."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration
            self.play(FadeOut(token_row), FadeIn(full_lane), FadeIn(full_label), FadeIn(set_formula), run_time=_rt(dur, 0.00, 0.22))
            self.play(FadeIn(visible_tokens, lag_ratio=0.05), FadeIn(visible_label), run_time=_rt(dur, 0.22, 0.45))
            self.play(FadeIn(masked_slots, lag_ratio=0.03), run_time=_rt(dur, 0.45, 0.62))
            self.play(FadeIn(mask_tokens, lag_ratio=0.03), FadeIn(mask_label), run_time=_rt(dur, 0.62, 0.78))
            self.play(FadeIn(route_formula), run_time=_rt(dur, 0.78, 0.9))
            self.play(Indicate(mask_tokens, color=HIGHLIGHT_YELLOW), run_time=_rt(dur, 0.9, 0.98))

        self._fade_scene()
        self.split_group = None

    def act8_three_component_architecture(self):
        context = make_module("Context Encoder", r"E_\theta", CONTEXT_BLUE).move_to(LEFT * 4.15 + UP * 0.95)
        target = make_module("Target Encoder", r"\bar E_\theta", TARGET_GRAY).move_to(RIGHT * 4.15 + UP * 0.95)
        predictor = make_module("Predictor", r"P_\phi", PREDICTOR_ORANGE).move_to(DOWN * 1.82)
        gather = make_module("Gather masked", r"M", TARGET_GRAY, width=1.65, height=0.72).move_to(RIGHT * 4.15 + DOWN * 0.42)

        visible_input = MathTex(r"x_N", font_size=30, color=CONTEXT_BLUE).move_to(LEFT * 4.15 + UP * 2.55)
        full_input = MathTex(r"x_L", font_size=30, color=TARGET_GRAY).move_to(RIGHT * 4.15 + UP * 2.55)
        ctx_out = VGroup(*[Dot(radius=0.055, color=CONTEXT_BLUE) for _ in range(8)]).arrange(RIGHT, buff=0.1)
        tgt_full_out = VGroup(*[Dot(radius=0.05, color=TARGET_GRAY) for _ in range(12)]).arrange(RIGHT, buff=0.07)
        tgt_out = VGroup(*[Dot(radius=0.055, color=TARGET_GRAY) for _ in range(8)]).arrange(RIGHT, buff=0.1)
        pred_out = VGroup(*[Dot(radius=0.055, color=PREDICTOR_ORANGE) for _ in range(8)]).arrange(RIGHT, buff=0.1)
        ctx_out.next_to(context, DOWN, buff=0.35)
        tgt_full_out.next_to(target, DOWN, buff=0.28)
        tgt_out.move_to(RIGHT * 4.15 + DOWN * 1.22)
        pred_out.move_to(RIGHT * 2.25 + DOWN * 1.82)

        mask_dots = VGroup(*[Dot(radius=0.055, color=PREDICTOR_ORANGE) for _ in range(6)]).arrange(RIGHT, buff=0.1)
        mask_label = MathTex(r"m_M=(m_{i_k})_{k=1}^{M}", font_size=22, color=PREDICTOR_ORANGE)
        mask_queries = VGroup(mask_dots, mask_label).arrange(DOWN, buff=0.13).move_to(LEFT * 3.55 + DOWN * 1.82)
        ctx_label = MathTex(r"z_N", font_size=24, color=CONTEXT_BLUE).next_to(ctx_out, LEFT, buff=0.18)
        tgt_full_label = MathTex(r"s_L", font_size=24, color=TARGET_GRAY).next_to(tgt_full_out, LEFT, buff=0.16)
        tgt_label = MathTex(r"s_M", font_size=24, color=TARGET_GRAY).next_to(tgt_out, DOWN, buff=0.16)
        pred_label = MathTex(r"\hat{s}_M", font_size=24, color=PREDICTOR_ORANGE).next_to(pred_out, DOWN, buff=0.16)

        ctx_input_arrow = Arrow(visible_input.get_bottom(), context.get_top(), color=CONTEXT_BLUE, buff=0.1, stroke_width=2.5)
        tgt_input_arrow = Arrow(full_input.get_bottom(), target.get_top(), color=TARGET_GRAY, buff=0.1, stroke_width=2.5)
        ctx_output_arrow = Arrow(context.get_bottom(), ctx_out.get_top(), color=CONTEXT_BLUE, buff=0.08, stroke_width=2.5)
        tgt_output_arrow = Arrow(target.get_bottom(), tgt_full_out.get_top(), color=TARGET_GRAY, buff=0.08, stroke_width=2.5)
        gather_input_arrow = Arrow(tgt_full_out.get_bottom(), gather.get_top(), color=TARGET_GRAY, buff=0.08, stroke_width=2.2)
        gather_output_arrow = Arrow(gather.get_bottom(), tgt_out.get_top(), color=TARGET_GRAY, buff=0.08, stroke_width=2.2)
        ctx_predict_arrow = Arrow(ctx_out.get_bottom(), predictor.get_left() + UP * 0.2, color=CONTEXT_BLUE, buff=0.1, stroke_width=2.5)
        mask_predict_arrow = Arrow(mask_queries.get_right(), predictor.get_left(), color=PREDICTOR_ORANGE, buff=0.12, stroke_width=2.5)
        prediction_arrow = Arrow(predictor.get_right(), pred_out.get_left(), color=PREDICTOR_ORANGE, buff=0.12, stroke_width=2.5)
        comparison = DashedLine(pred_out.get_right(), tgt_out.get_left(), color=HIGHLIGHT_YELLOW, dash_length=0.12)
        comparison_label = spaced_text("same indices", font_size=12, color=HIGHLIGHT_YELLOW).next_to(comparison, UP, buff=0.12)

        stop_wall = Rectangle(
            width=0.16,
            height=0.62,
            color=STOP_GRAD_RED,
            fill_color=STOP_GRAD_RED,
            fill_opacity=0.72,
        ).next_to(tgt_out, RIGHT, buff=0.42)
        stop_label = spaced_text("stop-gradient", font_size=13, color=STOP_GRAD_RED, weight=BOLD)
        stop_label.next_to(stop_wall, DOWN, buff=0.12)
        blocked_grad = Arrow(
            stop_wall.get_right() + RIGHT * 0.9,
            stop_wall.get_right(),
            color=STOP_GRAD_RED,
            buff=0.05,
            stroke_width=3,
        )
        blocked_x = Cross(stop_wall, stroke_color=STOP_GRAD_RED, stroke_width=4).scale(0.48)

        eq_context = MathTex(r"z_N=E_\theta(x_N)", font_size=31, color=CONTEXT_BLUE).to_edge(UP, buff=0.38)
        eq_target = MathTex(
            r"s_L=\bar E_\theta(x_L),\quad s_M=\operatorname{Gather}(s_L,M)",
            font_size=29,
            color=TARGET_GRAY,
        ).to_edge(UP, buff=0.38)
        eq_predictor = MathTex(
            r"\hat{s}_M=P_\phi(z_N,m_M)=(\hat{s}_{i_1},\ldots,\hat{s}_{i_M})",
            font_size=29,
            color=PREDICTOR_ORANGE,
        ).to_edge(UP, buff=0.38)

        architecture = VGroup(
            context, target, predictor, gather, visible_input, full_input, ctx_out,
            tgt_full_out, tgt_out, pred_out, mask_queries, ctx_label, tgt_full_label,
            tgt_label, pred_label, stop_wall,
            stop_label, blocked_grad, blocked_x, ctx_input_arrow, tgt_input_arrow,
            ctx_output_arrow, tgt_output_arrow, gather_input_arrow,
            gather_output_arrow, ctx_predict_arrow,
            mask_predict_arrow, prediction_arrow, comparison, comparison_label,
        )
        voice_text = (
            "Now follow the three functions exactly as written in the paper. "
            "The blue Context Encoder receives only x N and produces z N equal to E "
            "theta of x N. The gray Target Encoder receives the complete sequence x L. "
            "It first produces the full sequence s L. Gather then selects the rows at "
            "masked indices M to obtain s M; this selection step was missing from the "
            "earlier diagram. The red barrier marks stop-gradient on this target route. "
            "It blocks backward gradients, not the forward target features. The orange "
            "Predictor receives z N and the indexed mask-token sequence m M, producing "
            "s hat at exactly i one through i M. The dashed connector pairs predictions "
            "with targets carrying the same indices. It is not a data arrow from the "
            "Target Encoder into the Predictor."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration
            self.play(FadeIn(eq_context), FadeIn(visible_input), FadeIn(context), run_time=_rt(dur, 0.00, 0.13))
            self.play(Create(ctx_input_arrow), Create(ctx_output_arrow), FadeIn(ctx_out), FadeIn(ctx_label), run_time=_rt(dur, 0.13, 0.27))
            self.play(ReplacementTransform(eq_context, eq_target), FadeIn(full_input), FadeIn(target), run_time=_rt(dur, 0.27, 0.4))
            self.play(Create(tgt_input_arrow), Create(tgt_output_arrow), FadeIn(tgt_full_out), FadeIn(tgt_full_label), run_time=_rt(dur, 0.4, 0.5))
            self.play(FadeIn(gather), Create(gather_input_arrow), Create(gather_output_arrow), FadeIn(tgt_out), FadeIn(tgt_label), run_time=_rt(dur, 0.5, 0.6))
            self.play(FadeIn(stop_wall), FadeIn(stop_label), Create(blocked_grad), FadeIn(blocked_x), run_time=_rt(dur, 0.6, 0.7))
            self.play(ReplacementTransform(eq_target, eq_predictor), FadeIn(predictor), FadeIn(mask_queries), run_time=_rt(dur, 0.7, 0.79))
            self.play(Create(ctx_predict_arrow), Create(mask_predict_arrow), run_time=_rt(dur, 0.79, 0.87))
            self.play(Create(prediction_arrow), FadeIn(pred_out), FadeIn(pred_label), run_time=_rt(dur, 0.87, 0.93))
            self.play(Create(comparison), FadeIn(comparison_label), run_time=_rt(dur, 0.93, 0.97))
            self.play(
                Indicate(predictor[0], color=HIGHLIGHT_YELLOW),
                Indicate(pred_out, color=HIGHLIGHT_YELLOW),
                run_time=_rt(dur, 0.96, 0.995),
            )

        self._fade_scene()
        self.architecture_group = None

    def act9_latent_prediction_match(self):
        title = spaced_text("Architecture and shape contract", font_size=24, color=SOFT_WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.32)

        context = make_module("Context", r"E_\theta", CONTEXT_BLUE, width=1.8, height=0.78).move_to(LEFT * 4.85 + UP * 1.05)
        target = make_module("Target", r"\bar E_\theta", TARGET_GRAY, width=1.8, height=0.78).move_to(LEFT * 4.85 + DOWN * 0.25)
        twin_arrow = DoubleArrow(context.get_bottom(), target.get_top(), color=HIGHLIGHT_YELLOW, buff=0.1, tip_length=0.12)
        twin_label = MathTex(r"\bar\theta_0=\theta_0", font_size=23, color=HIGHLIGHT_YELLOW).next_to(twin_arrow, RIGHT, buff=0.14)
        encoder_spec = VGroup(
            spaced_text("ViT-L or ViT-H", font_size=16, color=SOFT_WHITE, weight=BOLD),
            spaced_text("joint space-time attention", font_size=14, color=DIM_GRAY),
        ).arrange(DOWN, buff=0.1).move_to(LEFT * 4.25 + DOWN * 1.55)

        input_shapes = VGroup(
            MathTex(r"z_N\in\mathbb{R}^{N\times d}", font_size=25, color=CONTEXT_BLUE),
            MathTex(r"\Pi(z_N)\in\mathbb{R}^{N\times384}", font_size=25, color=CONTEXT_BLUE),
            MathTex(r"m_M\in\mathbb{R}^{M\times384}", font_size=25, color=PREDICTOR_ORANGE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(LEFT * 1.35 + UP * 0.2)
        projection_arrow = Arrow(input_shapes[0].get_right(), input_shapes[1].get_right(), color=CONTEXT_BLUE, buff=0.18, stroke_width=2)

        concat_formula = MathTex(
            r"[\Pi(z_N);m_M]\in\mathbb{R}^{L\times384}",
            font_size=25,
            color=SOFT_WHITE,
        ).move_to(RIGHT * 2.45 + UP * 1.15)
        blocks = VGroup(*[
            RoundedRectangle(
                width=0.42,
                height=0.78,
                corner_radius=0.04,
                stroke_color=PREDICTOR_ORANGE,
                stroke_width=1.6,
                fill_color=PREDICTOR_ORANGE,
                fill_opacity=0.13,
            )
            for _ in range(6)
        ]).arrange(RIGHT, buff=0.11).move_to(RIGHT * 2.45 + UP * 0.05)
        blocks_label = spaced_text("12 transformer blocks  |  width 384", font_size=15, color=PREDICTOR_ORANGE, weight=BOLD)
        blocks_label.next_to(blocks, DOWN, buff=0.16)
        predictor_arrow = Arrow(concat_formula.get_bottom(), blocks.get_top(), color=PREDICTOR_ORANGE, buff=0.12, stroke_width=2.2)

        output_formula = MathTex(
            r"\operatorname{Select}_M\!\circ P_\phi\to\hat{s}_M\in\mathbb{R}^{M\times d}",
            font_size=25,
            color=PREDICTOR_ORANGE,
        ).move_to(RIGHT * 2.45 + DOWN * 1.55)
        output_arrow = Arrow(blocks.get_bottom(), output_formula.get_top(), color=PREDICTOR_ORANGE, buff=0.2, stroke_width=2.2)
        pairing = MathTex(
            r"\hat{s}_{i_k}\longleftrightarrow s_{i_k},\quad k=1,\ldots,M",
            font_size=27,
            color=HIGHLIGHT_YELLOW,
        ).move_to(DOWN * 2.18)

        act_group = VGroup(
            title, context, target, twin_arrow, twin_label, encoder_spec,
            input_shapes, projection_arrow, concat_formula, blocks, blocks_label,
            predictor_arrow, output_formula, output_arrow, pairing,
        )
        voice_text = (
            "The paper also specifies the networks behind those symbols. Context and "
            "Target are matching ViT-L or ViT-H backbones with joint space-time "
            "attention, and the Target Encoder is initialized identically to Context. "
            "The Predictor is deliberately narrow: twelve transformer blocks with "
            "embedding width three hundred and eighty-four, using the same number of "
            "attention heads as its backbone. Internally, a linear map Pi sends z N "
            "from width d to width three hundred and eighty-four. The M mask tokens "
            "have that same predictor width. Concatenation restores L positions for "
            "self-attention. After twelve blocks, only the M requested outputs are kept "
            "and projected back to width d, producing s hat M. Each s hat i k pairs with "
            "target s i k. Chapter Five will define the distance used for those pairs."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration
            self.play(FadeIn(title), FadeIn(context), FadeIn(target), run_time=_rt(dur, 0.00, 0.16))
            self.play(Create(twin_arrow), FadeIn(twin_label), FadeIn(encoder_spec), run_time=_rt(dur, 0.16, 0.32))
            self.play(FadeIn(input_shapes[0]), FadeIn(input_shapes[1]), Create(projection_arrow), run_time=_rt(dur, 0.32, 0.48))
            self.play(FadeIn(input_shapes[2]), FadeIn(concat_formula), run_time=_rt(dur, 0.48, 0.62))
            self.play(Create(predictor_arrow), FadeIn(blocks, lag_ratio=0.08), FadeIn(blocks_label), run_time=_rt(dur, 0.62, 0.78))
            self.play(Create(output_arrow), FadeIn(output_formula), run_time=_rt(dur, 0.78, 0.9))
            self.play(FadeIn(pairing, shift=UP * 0.12), Indicate(output_formula, color=HIGHLIGHT_YELLOW), run_time=_rt(dur, 0.9, 0.98))

        self._fade_group(act_group, run_time=0.65)

    def act10_recap_bridge(self):
        icons = VGroup()
        labels = [
            "clip",
            "tubelets",
            "1568 tokens",
            "3D PE",
            "three networks",
            "latent prediction",
        ]
        colors = [CONTEXT_BLUE, TOKEN_GREEN, TOKEN_GREEN, PURPLE_ACCENT, PREDICTOR_ORANGE, HIGHLIGHT_YELLOW]
        for label, color in zip(labels, colors):
            text = spaced_text(label, font_size=15, color=color, weight=BOLD)
            box = SurroundingRectangle(text, buff=0.16, color=color)
            icons.add(VGroup(box, text))
        icons.arrange(RIGHT, buff=0.25).scale(0.88).move_to(UP * 0.55)

        arrows = VGroup()
        for left, right in zip(icons[:-1], icons[1:]):
            arrows.add(Arrow(left.get_right(), right.get_left(), color=DIM_GRAY, buff=0.08, stroke_width=2))

        question = spaced_text("Which tokens should be hidden?", font_size=26, color=SOFT_WHITE, weight=BOLD)
        question.next_to(icons, DOWN, buff=0.85)
        bridge = spaced_text("Chapter 4: 3D Multi-Block Masking", font_size=24, color=HIGHLIGHT_YELLOW, weight=BOLD)
        bridge.next_to(question, DOWN, buff=0.35)
        spotlight = Dot(radius=0.09, color=HIGHLIGHT_YELLOW).move_to(icons[0].get_top() + UP * 0.22)

        act_group = VGroup(icons, arrows, question, bridge, spotlight)
        voice_text = (
            "So Chapter Three gives us the complete data route: the clip becomes "
            "tubelets, tubelets become fifteen hundred and sixty-eight tokens, "
            "positional embeddings attach space-time identity, and the three neural "
            "networks turn visible context into latent predictions. One question is "
            "now left open: which tokens should be hidden so the task is hard enough "
            "for video? That is where three-dimensional multi-block masking begins."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration
            self.play(FadeIn(icons[0]), run_time=_rt(dur, 0.00, 0.12))
            for index in range(1, len(icons)):
                self.play(
                    Create(arrows[index - 1]),
                    FadeIn(icons[index], shift=RIGHT * 0.1),
                    spotlight.animate.move_to(icons[index].get_top() + UP * 0.22),
                    run_time=max(0.45, _rt(dur, 0.12, 0.58, fill=0.12)),
                )
            self.play(FadeIn(question, shift=UP * 0.15), run_time=_rt(dur, 0.58, 0.76))
            self.play(FadeIn(bridge, shift=UP * 0.15), run_time=_rt(dur, 0.76, 0.92))

        self._fade_group(act_group, run_time=0.8)
        self.clear()


class Chapter3DryRunScene(Chapter3Scene):
    """Fast visual-only execution check; production renders use Chapter3Scene."""

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

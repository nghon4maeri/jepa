"""
V-JEPA Video - Chapter 2: Pixel-Level vs Latent-Space (12-Act Storyboard)
Style: 3Blue1Brown
Voiceover: English (Generic TTS - Male, UK accent)
Render: 420p15 (custom resolution)

COMPREHENSIVE REWRITE (2026-08-10):
✅ Target duration: ~5:00 (300s)
✅ Wider letter spacing (default 1.20x stretch)
✅ Correct subtitle timing using tracker.start_t / tracker.end_t
✅ Proportional animation pacing — animations fill ~95% of their phase window
✅ Minimized transition pauses (≤0.08s waits, 0.4-0.5s FadeOut)
✅ Act 5→6: Error bar moves to center, fills to max → ✗ conclusion
✅ Acts 9-11: Voice-synced cluster grouping (clustering starts when voice says so)
✅ Random cluster positions (rejection sampling for min separation)
✅ Lighter cluster text (font_size=13, stroke_width=0, NORMAL weight)
✅ Act 12: Prominent "1 vector" pipeline visualization
✅ Cluster persistence — dimmed through act 12, only removed at final fadeout
✅ Robust subtitle generation (12 SRT entries, 300s coverage)
"""

from manim import *
from manim_voiceover import VoiceoverScene
from generic_tts import GenericEdgeTTS
import numpy as np
import os
from pathlib import Path

# ─────────────────── 420p Render Config ───────────────────
config.pixel_height = 420
config.pixel_width = 746         # 16:9 aspect ratio
config.frame_rate = 15

# ─────────────────── Color Palette (3B1B Style) ───────────────────
BG_COLOR          = ManimColor("#1a1a2e")
CONTEXT_BLUE      = ManimColor("#5DADE2")
PREDICTOR_ORANGE  = ManimColor("#E59866")
TARGET_GRAY       = ManimColor("#AAB7B8")
HIGHLIGHT_YELLOW  = ManimColor("#F4D03F")
MASK_DARK         = ManimColor("#2a2a2a")
MASK_BORDER       = ManimColor("#8B0000")
RED_CHANNEL       = ManimColor("#E74C3C")
GREEN_CHANNEL     = ManimColor("#2ECC71")
BLUE_CHANNEL      = ManimColor("#3498DB")
SOFT_WHITE        = ManimColor("#E8E8E8")
DIM_GRAY          = ManimColor("#888888")
DARK_RED          = ManimColor("#922B21")
LAKE_BLUE         = ManimColor("#1A5276")
DEEP_MASK         = ManimColor("#1a1a1a")
CLUSTER_BLUE      = ManimColor("#5DADE2")
CLUSTER_GREEN     = ManimColor("#2ECC71")
CLUSTER_ORANGE    = ManimColor("#E59866")


# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════
def spaced_text(*args, spacing=1.20, **kwargs):
    """Create text with wider letter spacing by horizontal glyph stretch."""
    t = Text(*args, **kwargs)
    t.stretch(spacing, 0)
    return t


def _rt(dur, start_frac, end_frac, fill=0.90, floor=0.25):
    """Run-time that fills a phase window [start_frac, end_frac] of voice duration.

    Args:
        dur: Total voiceover duration.
        start_frac / end_frac: Fractional window in [0, 1].
        fill: How much of the window to fill with the animation (default 0.90).
        floor: Minimum run_time in seconds.
    """
    window = (end_frac - start_frac) * dur * fill
    return max(floor, window)


def _scatter_points(rng, center, radius, n, min_sep=0.25):
    """Generate n random 3D points inside a 2D circle with minimum separation."""
    pts = []
    max_attempts = 200
    for _ in range(n * max_attempts):
        if len(pts) == n:
            break
        angle = rng.uniform(0, TAU)
        dist = rng.uniform(0.05, radius)
        offset = np.array([dist * np.cos(angle), dist * np.sin(angle), 0.0])
        p = center + offset
        if np.linalg.norm(p[:2] - center[:2]) <= radius:
            if all(np.linalg.norm(p[:2] - q[:2]) >= min_sep for q in pts):
                pts.append(p)
    # Fallback: fill remaining with uniform ring
    while len(pts) < n:
        angle = TAU * len(pts) / n + rng.uniform(-0.2, 0.2)
        dist = radius * (0.5 + 0.45 * (len(pts) / n))
        pts.append(center + np.array([dist * np.cos(angle), dist * np.sin(angle), 0.0]))
    return pts


def _format_srt_time(seconds: float) -> str:
    """Convert float seconds → SRT timestamp HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# ═══════════════════════════════════════════════════════════════════
# MAIN SCENE
# ═══════════════════════════════════════════════════════════════════
class Chapter2Scene(VoiceoverScene):
    """Chapter 2: Pixel-Level vs Latent-Space — 12 Acts (5-minute Rewrite)"""

    def construct(self):
        self.camera.background_color = BG_COLOR
        self.set_speech_service(
            GenericEdgeTTS(gender="male", accent="uk"),
            create_subcaption=True,
        )

        # ── Subtitle tracking ──
        self._srt_entries = []

        # ── Cluster persistence tracking ──
        self._cluster_persist = None   # VGroup: ALL cluster visuals (dots, labels, circles, axes)
        self._all_clusters_visual = None
        self._cluster_circle_info = []

        self.act1_title()
        self.act2_build_lake_scene()
        self.act3_overlay_pixel_grid()
        self.act4_mask_blocks()
        self.act5_videomae_reconstruct()
        self.act6_pixel_conclusion()
        self.act7_contrast_split()
        self.act8_encoder()
        self.act9_latent_scatter()
        self.act10_noise_filter()
        self.act11_semantic_vector()
        self.act12_summary()

        # ── Write .srt subtitle file ──
        self._write_srt()

    # ══════════════════════════════════════════════════════════════
    # Subtitle helpers
    # ══════════════════════════════════════════════════════════════
    def _track_subtitle(self, text: str):
        """Store subtitle entry using tracker's real scene times."""
        tracker = getattr(self, '_current_tracker', None)
        if tracker is not None:
            self._srt_entries.append({
                'start': float(tracker.start_t),
                'end':   float(tracker.end_t),
                'text':  text,
            })

    def _write_srt(self):
        """Write accumulated subtitles to .srt file."""
        if not self._srt_entries:
            return
        srt_path = Path(__file__).resolve().parent.parent / "chapter2_subtitles.srt"
        with open(str(srt_path), "w", encoding="utf-8") as f:
            for i, entry in enumerate(self._srt_entries):
                f.write(f"{i + 1}\n")
                f.write(f"{_format_srt_time(entry['start'])} --> {_format_srt_time(entry['end'])}\n")
                f.write(f"{entry['text']}\n\n")
        print(f"✅ Subtitles written to {srt_path}")

    # ══════════════════════════════════════════════════════════════
    # ACT 1: Title Card (~4s)
    # ══════════════════════════════════════════════════════════════
    def act1_title(self):
        num = spaced_text(
            "2", font_size=72, color=SOFT_WHITE, font="sans-serif", weight=BOLD,
            spacing=1.25,
        ).move_to(UP * 0.8)

        subtitle = spaced_text(
            "Pixel-Level vs. Latent-Space",
            font_size=28, color=DIM_GRAY, font="sans-serif",
            spacing=1.22,
        ).move_to(DOWN * 0.3)

        underline = Line(
            subtitle.get_left() + DOWN * 0.15,
            subtitle.get_right() + DOWN * 0.15,
            color=CONTEXT_BLUE, stroke_width=2,
        )

        self.play(
            FadeIn(num, scale=0.5, run_time=1.0),
            FadeIn(subtitle, shift=UP * 0.2, run_time=1.0),
        )
        self.play(Create(underline, run_time=0.7))
        self.wait(0.1)
        self.play(
            FadeOut(num, shift=UP * 0.3),
            FadeOut(subtitle), FadeOut(underline),
            run_time=0.4,
        )

    # ══════════════════════════════════════════════════════════════
    # ACT 2: Build Lake Scene (~17s)
    # ══════════════════════════════════════════════════════════════
    def act2_build_lake_scene(self):
        rng = np.random.default_rng(42)

        # ── Sky ──
        sky = Rectangle(
            width=14.22, height=5.5,
            fill_color=BG_COLOR, fill_opacity=1, stroke_width=0,
        ).to_edge(UP, buff=0).set_z_index(-5)

        # ── Lake ──
        lake = Rectangle(
            width=14.22, height=2.8,
            fill_color=LAKE_BLUE, fill_opacity=0.2, stroke_width=0,
        ).to_edge(DOWN, buff=0)

        # ── Boat ──
        hull = Polygon(
            [-0.8, -0.2, 0], [0.8, -0.2, 0], [1.0, 0.3, 0], [-1.0, 0.3, 0],
            fill_color=SOFT_WHITE, fill_opacity=0.9, stroke_width=1, stroke_color=DIM_GRAY,
        )
        mast = Rectangle(
            width=0.12, height=0.9,
            fill_color=PREDICTOR_ORANGE, fill_opacity=0.9, stroke_width=0,
        ).next_to(hull, UP, buff=0)
        sail = Polygon(
            [0.15, 0, 0], [0.7, 0, 0], [0.15, 0.7, 0],
            fill_color=HIGHLIGHT_YELLOW, fill_opacity=0.8, stroke_width=0,
        ).next_to(mast, RIGHT, buff=0).align_to(mast, DOWN)
        boat = VGroup(hull, mast, sail).scale(0.7)
        boat.move_to(LEFT * 4 + DOWN * 1.0)

        # ── Ripples ──
        ripples = VGroup()
        for i in range(8):
            ripple = FunctionGraph(
                lambda x, offset=i: 0.04 * np.sin(5 * x + offset * 1.2),
                x_range=[-1.2, 1.2],
                color=CONTEXT_BLUE, stroke_width=1.5, stroke_opacity=0.5,
            )
            ripple.move_to(LEFT * rng.uniform(-5, 5) + DOWN * (1.8 + i * 0.25))
            ripples.add(ripple)

        # ── Tree ──
        trunk = Rectangle(
            width=0.3, height=2.0,
            fill_color=DIM_GRAY, fill_opacity=1, stroke_width=0,
        ).move_to(RIGHT * 5 + UP * 0.5)
        leaves = VGroup()
        for _ in range(18):
            leaf = Circle(
                radius=rng.uniform(0.2, 0.45),
                fill_color=GREEN_CHANNEL, fill_opacity=0.5, stroke_width=0,
            )
            leaf.move_to(
                RIGHT * 5 + UP * 2.0
                + RIGHT * rng.uniform(-1.2, 1.2)
                + UP * rng.uniform(-0.8, 1.2)
            )
            leaves.add(leaf)
        tree = VGroup(trunk, leaves)

        self._scene_group = VGroup(sky, lake, boat, ripples, tree)
        self._boat = boat
        self._ripples = ripples
        self._lake = lake
        self._tree = tree

        voice_text = (
            "Traditional self-supervised learning methods, such as Video M A E, "
            "approach the fill-in-the-blank problem by attempting to "
            "reconstruct every single masked pixel with absolute precision. "
            "They believe that if you can perfectly redraw what was hidden, "
            "you must have truly understood the scene. But is that really the case? "
            "Let us build a simple scene to find out."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration

            # sky + lake 0–22%
            self.play(FadeIn(sky, run_time=_rt(dur, 0, 0.22, fill=0.5)),
                      FadeIn(lake, run_time=_rt(dur, 0, 0.22, fill=0.5)))
            # boat 0.22–0.42
            self.play(FadeIn(boat, shift=RIGHT * 0.5, run_time=_rt(dur, 0.22, 0.42)))
            # ripples + tree 0.42–0.62
            self.play(
                FadeIn(ripples, lag_ratio=0.1, run_time=_rt(dur, 0.42, 0.62)),
                FadeIn(tree, shift=UP * 0.3, run_time=_rt(dur, 0.42, 0.62)),
            )
            # boat glide + subtle motion 0.62–0.95
            self.play(
                boat.animate.shift(RIGHT * 0.5),
                ripples.animate.shift(LEFT * 0.08),
                run_time=_rt(dur, 0.62, 0.95),
            )
            self.wait(max(0.05, dur * 0.05))

    # ══════════════════════════════════════════════════════════════
    # ACT 3: Overlay Pixel Grid (~18s)
    # ══════════════════════════════════════════════════════════════
    def act3_overlay_pixel_grid(self):
        grid = NumberPlane(
            x_range=[-7, 7, 0.5], y_range=[-4, 4, 0.5],
            background_line_style={
                "stroke_color": DIM_GRAY,
                "stroke_width": 0.8,
                "stroke_opacity": 0.25,
            },
            axis_config={"stroke_opacity": 0},
            faded_line_ratio=0,
        ).set_z_index(5)

        rng = np.random.default_rng(99)
        pixel_nums = VGroup()
        for r in range(-3, 0):
            for c in range(-6, 6):
                val = rng.integers(0, 256)
                num = Integer(val, font_size=7, color=SOFT_WHITE).set_opacity(0.5)
                num.move_to(RIGHT * (c * 0.5 + 0.25) + UP * (r * 0.5 + 0.25))
                pixel_nums.add(num)
        pixel_nums.set_z_index(6)

        self._grid_overlay = VGroup(grid, pixel_nums)

        voice_text = (
            "Look at this frame carefully. "
            "The lake surface is rippling with complex wave patterns. "
            "Leaves are rustling in the wind. "
            "To a computer, every single pixel in this image is just a number, "
            "between zero and two hundred and fifty-five, "
            "representing the intensity of red, green, and blue light. "
            "A seemingly simple natural scene is actually a massive grid "
            "of raw numerical values."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration

            # grid 0–0.32
            self.play(Create(grid, run_time=_rt(dur, 0, 0.32)))
            # numbers 0.32–0.58
            self.play(FadeIn(pixel_nums, lag_ratio=0.02, run_time=_rt(dur, 0.32, 0.58)))
            # ripple + boat subtle motion 0.58–0.95
            self.play(
                self._ripples.animate.shift(LEFT * 0.15),
                self._boat.animate.shift(RIGHT * 0.2),
                run_time=_rt(dur, 0.58, 0.95),
            )
            self.wait(max(0.05, dur * 0.05))

    # ══════════════════════════════════════════════════════════════
    # ACT 4: Mask Blocks (~18s)
    # ══════════════════════════════════════════════════════════════
    def act4_mask_blocks(self):
        mask_positions = [
            LEFT * 3 + UP * 0.5,
            RIGHT * 1 + DOWN * 0.8,
            LEFT * 0.5 + DOWN * 1.5,
            RIGHT * 3.5 + UP * 1.0,
            RIGHT * 5 + DOWN * 0.5,
        ]
        masks = VGroup()
        mask_labels = VGroup()
        rng = np.random.default_rng(44)
        for pos in mask_positions:
            w = rng.uniform(1.5, 2.5)
            h = rng.uniform(1.0, 1.8)
            mask = Rectangle(
                width=w, height=h,
                fill_color=DEEP_MASK, fill_opacity=0.92,
                stroke_color=MASK_BORDER, stroke_width=2,
            ).move_to(pos).set_z_index(10)
            label = spaced_text(
                "[MASK]", font_size=16, color=RED_CHANNEL, weight=BOLD,
                spacing=1.18,
            ).move_to(mask).set_z_index(11)
            masks.add(mask)
            mask_labels.add(label)

        arrows = VGroup()
        for i in range(min(3, len(mask_positions))):
            start = mask_positions[i] + LEFT * 1.5
            end = mask_positions[i]
            arrow = DashedLine(
                start, end, color=HIGHLIGHT_YELLOW, stroke_width=2, dash_length=0.1,
            ).set_z_index(12)
            arrow.add_tip(tip_length=0.15, tip_width=0.12)
            arrows.add(arrow)

        self._mask_group = VGroup(masks, mask_labels, arrows)

        voice_text = (
            "The model must reconstruct what lies beneath these heavily masked regions. "
            "It tries to guess every hidden pixel value by looking at the surrounding "
            "visible context. The idea sounds reasonable at first: if you can fill in "
            "the blanks correctly, you must know what the scene contains. "
            "But this is where the problem begins."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration

            # masks drop 0–0.32
            self.play(
                AnimationGroup(
                    *[FadeIn(m, shift=DOWN * 0.5) for m in masks],
                    lag_ratio=0.15,
                ),
                run_time=_rt(dur, 0, 0.32),
            )
            # labels 0.32–0.55
            self.play(FadeIn(mask_labels, run_time=_rt(dur, 0.32, 0.55)))
            # arrows 0.55–0.95
            self.play(Create(arrows, run_time=_rt(dur, 0.55, 0.95)))
            self.wait(max(0.05, dur * 0.05))

    # ══════════════════════════════════════════════════════════════
    # ACT 5: VideoMAE Pixel Reconstruction Chaos (~35s)
    # ══════════════════════════════════════════════════════════════
    def act5_videomae_reconstruct(self):
        rng = np.random.default_rng(77)
        flash_cells = VGroup()
        for _ in range(30):
            cell = Square(
                side_length=0.5,
                fill_color=RED_CHANNEL, fill_opacity=0.5, stroke_width=0,
            )
            cell.move_to(RIGHT * rng.uniform(-6, 6) + UP * rng.uniform(-3, 2))
            cell.set_z_index(15)
            flash_cells.add(cell)

        # L2 Loss formula
        loss_eq = MathTex(
            r"\mathcal{L}_{\text{pixel}} = \sum_{i,j} \| x_{i,j} - \hat{x}_{i,j} \|^2",
            font_size=36, color=RED_CHANNEL,
        ).to_edge(UP, buff=0.4).set_z_index(20)

        # Error bar components
        bar_bg = Rectangle(
            width=4, height=0.3,
            fill_color=DARK_RED, fill_opacity=0.3,
            stroke_color=DIM_GRAY, stroke_width=1,
        ).to_edge(UP, buff=0.5).shift(DOWN * 1.2).set_z_index(20)
        
        bar_fill = Rectangle(
            width=0.2, height=0.25,
            fill_color=RED_CHANNEL, fill_opacity=0.8, stroke_width=0,
        ).align_to(bar_bg, LEFT).move_to(bar_bg, LEFT).shift(RIGHT * 0.05).set_z_index(21)

        bar_label = spaced_text(
            "Error", font_size=16, color=RED_CHANNEL, spacing=1.18,
        ).next_to(bar_bg, LEFT, buff=0.2).set_z_index(20)

        # 🔑 Gom toàn bộ Error Bar thành 1 VGroup duy nhất
        error_bar_unit = VGroup(bar_bg, bar_fill, bar_label)
        
        # 🔑 Gom Error Bar và Công thức vào_error_bar_group chung
        self._error_bar_group = VGroup(error_bar_unit, loss_eq)

        voice_text = (
            "Forcing the model to precisely predict every random water ripple, "
            "every tiny dust particle, and every flickering leaf shadow is an "
            "impossible and completely meaningless task. Nature is chaotic and "
            "unpredictable at the pixel level. The pixel-level loss function "
            "generates a massive amount of noise, penalizing the model for failing "
            "to guess values that are fundamentally random. "
            "It forces the neural network to waste enormous computational "
            "resources on the lowest-level details, instead of learning the "
            "higher-level semantic structure of the action, such as the simple "
            "understanding that a boat is moving forward across the water. "
            "The error bar keeps climbing because the model is trying to solve "
            "a problem that has no correct answer."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration

            # formula 0–0.10
            self.play(FadeIn(loss_eq, shift=DOWN * 0.3, run_time=_rt(dur, 0, 0.10)))
            # bar setup 0.10–0.18
            self.play(
                FadeIn(error_bar_unit),
                run_time=_rt(dur, 0.10, 0.18),
            )

            # Chaos loops: 6 steps 0.18–0.72
            loop_window = 0.72 - 0.18
            per_loop = loop_window * dur / 6.0
            for i in range(6):
                self.play(
                    FadeIn(flash_cells, run_time=per_loop * 0.55),
                    bar_fill.animate.stretch_to_fit_width(
                        0.5 + i * 0.62, about_edge=LEFT,
                    ),
                    self._ripples.animate.shift(RIGHT * 0.05 * (1 if i % 2 == 0 else -1)),
                    run_time=per_loop * 0.55,
                )
                self.play(FadeOut(flash_cells, run_time=per_loop * 0.40))

            # Fill to max 0.72–0.86
            self.play(
                bar_fill.animate.stretch_to_fit_width(3.9, about_edge=LEFT),
                bar_fill.animate.set_color(RED_CHANNEL).set_opacity(1.0),
                run_time=_rt(dur, 0.72, 0.86),
            )
            self.wait(max(0.05, dur * 0.04))

        # ═══════════════════════════════════════════════════════
        # 🔑 CLEANUP scene objects, KEEP error bar
        # ═══════════════════════════════════════════════════════
        scene_cleanup = VGroup(
            self._scene_group,
            self._grid_overlay,
            self._mask_group,
        )
        self.play(FadeOut(scene_cleanup, run_time=0.6))

        # 🔑 ANIMATE cả cụm error_bar_unit và loss_eq cùng lúc thông qua VGroup
        self.play(
            loss_eq.animate.move_to(UP * 0.4),
            error_bar_unit.animate.move_to(DOWN * 1.2),
            run_time=1.4,
            rate_func=smooth,
        )
        
        # Fill bar chuẩn xát theo viền trong của bar_bg
        self.play(
            bar_fill.animate.stretch_to_fit_width(
                bar_bg.width - 0.1, about_edge=LEFT
            ).set_color(RED_CHANNEL).set_opacity(1.0),
            run_time=0.6,
        )
        self.wait(0.08)

    # ══════════════════════════════════════════════════════════════
    # ACT 6: Pixel Conclusion — Error bar at center → ✗ (~12s)
    # ══════════════════════════════════════════════════════════════
    def act6_pixel_conclusion(self):
        # Error bar is already centered from act 5, bar filled to max

        x_mark = spaced_text(
            "✗", font_size=140, color=RED_CHANNEL, spacing=1.0,
        ).set_z_index(30)
        label = spaced_text(
            "Pixel Reconstruction: Inefficient",
            font_size=28, color=RED_CHANNEL, spacing=1.18,
        )
        label.next_to(x_mark, DOWN, buff=0.5)

        voice_text = (
            "The model gets completely lost in a sea of chaotic "
            "and unpredictable data. Pixel-level reconstruction "
            "is fundamentally inefficient and wasteful."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration

            # Pulse error bar group 0–0.22
            self.play(
                self._error_bar_group.animate.scale(1.15),
                rate_func=there_and_back, run_time=_rt(dur, 0, 0.22),
            )

            self.wait(0.3)

            # Fade out error bar group, then show ✗  0.22–0.55
            self.play(
                FadeOut(self._error_bar_group, run_time=_rt(dur, 0.22, 0.38)),
            )
            self.play(GrowFromCenter(x_mark, run_time=_rt(dur, 0.38, 0.58)))
            # Wiggle ✗ 0.58–0.78
            self.play(
                Wiggle(x_mark, scale_value=1.1, rotation_angle=0.04 * TAU),
                run_time=_rt(dur, 0.58, 0.78),
            )
            # Label 0.78–0.95
            self.play(
                FadeIn(label, shift=UP * 0.2, run_time=_rt(dur, 0.78, 0.92)),
            )
            self.wait(max(0.03, dur * 0.05))

        self.play(FadeOut(x_mark), FadeOut(label), run_time=0.4)
        self.wait(0.05)

    # ══════════════════════════════════════════════════════════════
    # ACT 7: Contrast Split Screen (~28s)
    # ══════════════════════════════════════════════════════════════
    def act7_contrast_split(self):
        divider = Line(UP * 3.5, DOWN * 3.5, color=SOFT_WHITE, stroke_width=2)

        # ── Left: VideoMAE (red) ──
        left_title = spaced_text(
            "VideoMAE", font_size=26, color=RED_CHANNEL, weight=BOLD, spacing=1.20,
        ).move_to(LEFT * 3.5 + UP * 3)
        left_desc = spaced_text(
            "Pixel Reconstruction", font_size=16, color=DIM_GRAY, spacing=1.16,
        ).next_to(left_title, DOWN, buff=0.2)

        rng = np.random.default_rng(55)
        pixel_chaos = VGroup()
        for r in range(6):
            for c in range(8):
                sq = Square(side_length=0.35, stroke_width=0.3, stroke_color=DIM_GRAY)
                val = rng.integers(0, 256)
                sq.set_fill(
                    color=interpolate_color(RED_CHANNEL, SOFT_WHITE, val / 255.0),
                    opacity=0.6,
                )
                sq.move_to(LEFT * 3.5 + RIGHT * (c - 4) * 0.37 + DOWN * (r - 2) * 0.37)
                pixel_chaos.add(sq)

        # ── Right: V-JEPA (green) ──
        right_title = spaced_text(
            "V-JEPA", font_size=26, color=GREEN_CHANNEL, weight=BOLD, spacing=1.20,
        ).move_to(RIGHT * 3.5 + UP * 3)
        right_desc = spaced_text(
            "Semantic Understanding", font_size=16, color=DIM_GRAY, spacing=1.16,
        ).next_to(right_title, DOWN, buff=0.2)

        clean_boat = Polygon(
            [-0.6, -0.15, 0], [0.6, -0.15, 0], [0.8, 0.25, 0], [-0.8, 0.25, 0],
            fill_color=SOFT_WHITE, fill_opacity=0.9, stroke_width=1, stroke_color=DIM_GRAY,
        ).scale(0.8).move_to(RIGHT * 3 + DOWN * 0.5)
        direction_arrow = Arrow(
            RIGHT * 2.2 + DOWN * 0.5, RIGHT * 5 + DOWN * 0.5,
            color=GREEN_CHANNEL, stroke_width=4, buff=0,
        )
        semantic_label = spaced_text(
            "→ Moving Right", font_size=18, color=GREEN_CHANNEL, spacing=1.16,
        ).next_to(direction_arrow, UP, buff=0.2)

        all_act7 = VGroup(
            divider, left_title, left_desc, pixel_chaos,
            right_title, right_desc, clean_boat, direction_arrow, semantic_label,
        )

        voice_text = (
            "This is where the philosophical contrast truly shines. "
            "While Video M A E drowns in its hopeless attempt to recreate "
            "the randomness of nature, desperately trying to guess every "
            "flickering pixel value, V-JEPA chooses a far more elegant path. "
            "Its core philosophy is simple yet deeply profound: "
            "we do not need to reconstruct the physical world pixel by pixel. "
            "We only need to understand it. The goal is meaning, not mimicry."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration

            # divider 0–0.12
            self.play(Create(divider, run_time=_rt(dur, 0, 0.12)))
            # left side 0.12–0.35
            self.play(
                FadeIn(left_title), FadeIn(left_desc), FadeIn(pixel_chaos),
                run_time=_rt(dur, 0.12, 0.35),
            )
            # right side 0.35–0.58
            self.play(
                FadeIn(right_title), FadeIn(right_desc), FadeIn(clean_boat),
                run_time=_rt(dur, 0.35, 0.58),
            )
            # arrow + label 0.58–0.75
            self.play(
                Create(direction_arrow, run_time=_rt(dur, 0.58, 0.75)),
                FadeIn(semantic_label, run_time=_rt(dur, 0.58, 0.75)),
            )
            # dim left, brighten right 0.75–0.95
            self.play(
                pixel_chaos.animate.set_opacity(0.3),
                clean_boat.animate.set_opacity(1.0),
                direction_arrow.animate.set_stroke(width=6),
                run_time=_rt(dur, 0.75, 0.95),
            )
            self.wait(max(0.03, dur * 0.05))

        self.play(FadeOut(all_act7, run_time=0.5))
        self.wait(0.05)

    # ══════════════════════════════════════════════════════════════
    # ACT 8: Encoder Pipeline (~35s)
    # ══════════════════════════════════════════════════════════════
    def act8_encoder(self):
        # ── Video frame thumbnail ──
        frame_rect = Rectangle(
            width=2.0, height=1.4,
            stroke_color=SOFT_WHITE, stroke_width=2,
            fill_color=LAKE_BLUE, fill_opacity=0.15,
        ).move_to(LEFT * 5)
        mini_boat = Polygon(
            [-0.3, -0.05, 0], [0.3, -0.05, 0], [0.4, 0.1, 0], [-0.4, 0.1, 0],
            fill_color=SOFT_WHITE, fill_opacity=0.7, stroke_width=0.5, stroke_color=DIM_GRAY,
        ).move_to(frame_rect.get_center() + DOWN * 0.15)
        frame_label = spaced_text(
            "Video Frame", font_size=13, color=DIM_GRAY, spacing=1.16,
        ).next_to(frame_rect, UP, buff=0.15)
        thumb_group = VGroup(frame_rect, mini_boat, frame_label)

        # ── Encoder box ──
        enc_box = Rectangle(
            width=3.2, height=4.2,
            color=PREDICTOR_ORANGE, fill_opacity=0.08, stroke_width=3,
        ).move_to(ORIGIN)
        enc_title = spaced_text(
            "Encoder", font_size=22, color=PREDICTOR_ORANGE, weight=BOLD, spacing=1.20,
        ).next_to(enc_box, UP, buff=0.15)
        enc_formula = MathTex(r"E_\theta", font_size=30, color=PREDICTOR_ORANGE)
        enc_formula.next_to(enc_title, DOWN, buff=0.1)

        # ── Gear ──
        gear_center_pt = enc_box.get_corner(UR) + RIGHT * 0.4 + DOWN * 0.4
        gear_center = Dot(gear_center_pt, radius=0.08, color=PREDICTOR_ORANGE)
        gear_teeth = VGroup()
        for i in range(8):
            angle = i * TAU / 8
            tooth = Rectangle(
            width=0.05, height=0.12,
            fill_color=PREDICTOR_ORANGE, fill_opacity=0.7, stroke_width=0,
        )
        tooth.move_to(
            gear_center_pt + RIGHT * 0.18 * np.cos(angle) + UP * 0.18 * np.sin(angle)
        )
        tooth.rotate(angle, about_point=tooth.get_center())
        gear_teeth.add(tooth)
        
        gear_ring = Circle(
            radius=0.16, color=PREDICTOR_ORANGE, stroke_width=1.5, fill_opacity=0,
        ).move_to(gear_center_pt)
    
        gear = VGroup(gear_teeth, gear_ring, gear_center)

        # ── Internal layers ──
        layer_names = ["Conv3D", "Self-Attention", "LayerNorm", "Pooling"]
        layers = VGroup()
        for i, lbl in enumerate(layer_names):
            layer_rect = Rectangle(
                width=2.4, height=0.5,
                fill_color=PREDICTOR_ORANGE, fill_opacity=0.08 + i * 0.06,
                stroke_color=PREDICTOR_ORANGE, stroke_width=1.5,
            )
            layer_rect.move_to(enc_box.get_center() + UP * (1.3 - i * 0.85))
            layer_text = spaced_text(
                lbl, font_size=13, color=SOFT_WHITE, spacing=1.14,
            ).move_to(layer_rect)
            layers.add(VGroup(layer_rect, layer_text))

        layer_arrows = VGroup()
        for i in range(len(layers) - 1):
            arr = Arrow(
                layers[i].get_bottom(), layers[i + 1].get_top(),
                color=DIM_GRAY, stroke_width=2, buff=0.05,
                max_tip_length_to_length_ratio=0.2,
            )
            layer_arrows.add(arr)

        # ── Compression bars ──
        compress_bars = VGroup()
        for i in range(5):
            bar = Rectangle(
                width=2.5 - i * 0.4, height=0.06,
                fill_color=PREDICTOR_ORANGE, fill_opacity=0.25, stroke_width=0,
            )
            bar.move_to(enc_box.get_center() + DOWN * (2.4 + i * 0.12))
            compress_bars.add(bar)

        # ── Output latent dot ──
        latent_dot = Dot(color=HIGHLIGHT_YELLOW, radius=0.18).move_to(RIGHT * 5.2)
        latent_glow = Circle(
            radius=0.35, color=HIGHLIGHT_YELLOW,
            fill_opacity=0.1, stroke_width=1, stroke_opacity=0.5,
        ).move_to(latent_dot)
        latent_label = spaced_text(
            "Latent Representation", font_size=15, color=HIGHLIGHT_YELLOW, spacing=1.18,
        ).next_to(latent_dot, DOWN, buff=0.3)
        latent_annotation = spaced_text(
            "Encodes: Motion direction, Object type, Scene context...",
            font_size=11, color=DIM_GRAY, spacing=1.14,
        ).next_to(latent_label, DOWN, buff=0.12)

        # ── Connecting arrows ──
        start_pt = thumb_group.get_right()
        end_pt = np.array([enc_box.get_left()[0], start_pt[1], 0])
        in_arrow = Arrow(
            start_pt, end_pt,
            color=SOFT_WHITE, stroke_width=3, buff=0.15,
        )
        out_arrow = Arrow(
            enc_box.get_right(), latent_dot.get_left(),
            color=HIGHLIGHT_YELLOW, stroke_width=3, buff=0.15,
        )

        all_act8 = VGroup(
            thumb_group, enc_box, enc_title, enc_formula,
            gear, layers, layer_arrows, compress_bars,
            in_arrow, out_arrow, latent_dot, latent_glow,
            latent_label, latent_annotation,
        )

        voice_text = (
            "Instead of reconstructing pixels, V-JEPA passes the entire video frame "
            "through a powerful Encoder. This encoder is a deep neural network "
            "consisting of multiple specialized processing layers. "
            "First, a 3D convolution layer extracts small spacetime cubes "
            "called tubelets from the raw video. "
            "Then, self-attention layers analyze how each tubelet relates to "
            "every other tubelet across the entire frame. "
            "Layer normalization keeps the computations stable, "
            "and pooling progressively reduces the dimensions. "
            "Each layer compresses and abstracts the raw pixel data, "
            "stripping away low-level noise and retaining only the meaningful "
            "semantic patterns. "
            "At the output, the complex frame of millions of numbers "
            "gets compressed into a single compact feature vector "
            "in the latent space."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration

            # thumb 0–0.06
            self.play(FadeIn(thumb_group, run_time=_rt(dur, 0, 0.06)))
            # enc box + title + in_arrow 0.06–0.16
            self.play(
                FadeIn(enc_box), FadeIn(enc_title), FadeIn(enc_formula),
                Create(in_arrow),
                run_time=_rt(dur, 0.06, 0.16),
            )
            # gear 0.16–0.24
            self.play(FadeIn(gear, scale=0.5, run_time=_rt(dur, 0.16, 0.24)))
            # gear rotates 0.24–0.34
            self.play(Rotate(gear, angle=TAU, run_time=_rt(dur, 0.24, 0.34), rate_func=linear))
            # layers + arrows 0.34–0.62
            layer_time = _rt(dur, 0.34, 0.62)
            per_layer = layer_time / len(layers)
            for i, layer in enumerate(layers):
                self.play(FadeIn(layer, shift=DOWN * 0.1, run_time=per_layer * 0.55))
                if i < len(layer_arrows):
                    self.play(Create(layer_arrows[i], run_time=per_layer * 0.40))
            # compression bars 0.62–0.70
            self.play(FadeIn(compress_bars, lag_ratio=0.2, run_time=_rt(dur, 0.62, 0.70)))
            # output dot + arrow 0.70–0.86
            self.play(Create(out_arrow, run_time=_rt(dur, 0.70, 0.76)))
            self.play(
                FadeIn(latent_dot, scale=0.3, run_time=_rt(dur, 0.76, 0.82)),
                FadeIn(latent_glow, run_time=_rt(dur, 0.76, 0.82)),
                FadeIn(latent_label, run_time=_rt(dur, 0.76, 0.82)),
                FadeIn(latent_annotation, run_time=_rt(dur, 0.82, 0.88)),
            )
            # pulse latent dot 0.86–0.95
            self.play(
                latent_dot.animate.scale(1.5),
                latent_glow.animate.scale(1.5).set_opacity(0.2),
                rate_func=there_and_back, run_time=_rt(dur, 0.86, 0.95),
            )
            self.wait(max(0.03, dur * 0.05))

        self.play(FadeOut(all_act8, run_time=0.5))
        self.wait(0.05)

    # ══════════════════════════════════════════════════════════════
    # ACT 9: Latent Space Scatter Plot — VOICE SYNCED (~48s)
    #   Clusters form ONLY when voice mentions "naturally cluster together"
    #   Random positions via _scatter_points
    # ══════════════════════════════════════════════════════════════
    def act9_latent_scatter(self):
        rng = np.random.default_rng(42)

        # ── Axes ──
        axes = Axes(
            x_range=[-4, 4, 1], y_range=[-3, 3, 1],
            x_length=10, y_length=8,
            axis_config={"color": DIM_GRAY, "stroke_width": 2, "include_ticks": False},
            tips=True,
        ).scale(0.72).move_to(DOWN * 0.2)

        x_label = spaced_text(
            "Semantic Dim 1", font_size=14, color=DIM_GRAY, spacing=1.16,
        ).next_to(axes.x_axis, DOWN, buff=0.15)
        y_label = spaced_text(
            "Semantic Dim 2", font_size=14, color=DIM_GRAY, spacing=1.16,
        ).next_to(axes.y_axis, LEFT, buff=0.15).rotate(PI / 2)

        title = spaced_text(
            "Latent Space", font_size=30, color=SOFT_WHITE, weight=BOLD, spacing=1.22,
        ).to_edge(UP, buff=0.25)

        # ── Cluster definitions ──
        cluster_defs = [
            (np.array([-2.3, 1.2, 0]), ["Boat", "Ship", "Canoe", "Kayak"], CLUSTER_BLUE),
            (np.array([2.2, 1.5, 0]), ["Tree", "Forest", "Leaf", "Grass"], CLUSTER_GREEN),
            (np.array([0.0, -1.6, 0]), ["Walking", "Running", "Jumping", "Dancing"], CLUSTER_ORANGE),
        ]

        # Bố cục cố định cho các cụm có nhãn dài/dễ chồng chữ.
        # Mỗi offset được tính tương đối so với tâm của vòng tròn.
        cluster_layouts = {
            "Boat": np.array([-0.42, 0.12, 0]),
            "Ship": np.array([0.34, 0.10, 0]),
            "Canoe": np.array([0.38, 0.62, 0]),
            "Kayak": np.array([-0.20, -0.48, 0]),
            "Walking": np.array([-0.45, 0.34, 0]),
            "Running": np.array([-0.28, -0.48, 0]),
            "Jumping": np.array([0.18, -0.12, 0]),
            "Dancing": np.array([0.52, 0.26, 0]),
        }

        # Hướng đặt nhãn riêng cho từng điểm để nhãn không đè lên nhau.
        label_directions = {
            "Boat": LEFT,
            "Ship": RIGHT,
            "Canoe": DOWN,
            "Kayak": DOWN,
            "Walking": LEFT,
            "Running": DOWN,
            "Jumping": UP,
            "Dancing": RIGHT,
        }

        # ── Build thumbnails, scattered-entry dots, and final cluster objects ──
        all_thumbnails = VGroup()
        all_scattered_dots = VGroup()
        cluster_data = []  # (final_dots, labels, enc_circle, center, color, cluster_radius, names, scattered_indices)

        y_start = 3.0
        y_step = 0.55
        dot_idx = 0

        for center, names, color in cluster_defs:
            n = len(names)
            cluster_radius = 0.50 + 0.10 * n

            # Blue/orange dùng bố cục cố định; các cụm còn lại vẫn rải ngẫu nhiên.
            if all(name in cluster_layouts for name in names):
                final_positions = [
                    center + cluster_layouts[name] for name in names
                ]
            else:
                final_positions = _scatter_points(
                    rng, center, cluster_radius, n, min_sep=0.28,
                )
            final_dots = VGroup()
            labels = VGroup()

            start_idx = dot_idx
            for i, (name, fpos) in enumerate(zip(names, final_positions)):
                # Final dot tại vị trí đã tính cho cụm
                final_dot = Dot(fpos, radius=0.07, color=color)
                final_dots.add(final_dot)

                # 🔑 LIGHTER text: font_size=13, NORMAL, no stroke
                lbl = spaced_text(
                    name, font_size=13, color=color, weight=NORMAL,
                    font="sans-serif", spacing=1.14,
                )
                lbl.set_stroke(width=0)
                lbl.set_fill(opacity=0.90)
                label_direction = label_directions.get(name, DOWN)
                lbl.next_to(final_dot, label_direction, buff=0.10)
                lbl.set_opacity(0)
                labels.add(lbl)

                # Scattered entry dot
                scattered_dot = Dot(radius=0.07, color=color).set_opacity(0)
                all_scattered_dots.add(scattered_dot)

                # Thumbnail on far left
                thumb = RoundedRectangle(
                    width=0.7, height=0.48, corner_radius=0.1,
                    fill_color=color, fill_opacity=0.2,
                    stroke_color=color, stroke_width=1.5,
                )
                thumb_label = spaced_text(
                    name, font_size=10, color=color, weight=NORMAL, spacing=1.14,
                )
                thumb_label.set_stroke(width=0)
                thumb_label.move_to(thumb)
                thumb_item = VGroup(thumb, thumb_label)
                y_pos = y_start - dot_idx * y_step
                thumb_item.move_to(LEFT * 6.2 + UP * y_pos)
                all_thumbnails.add(thumb_item)
                dot_idx += 1

            end_idx = dot_idx

            # 🔑 LIGHTER cluster circle
            enc_circle = DashedVMobject(
                Circle(
                    radius=cluster_radius + 0.38, color=color, stroke_width=1.6,
                ).move_to(center),
                num_dashes=16,
            )
            enc_circle.set_stroke(opacity=0)

            cluster_data.append((
                final_dots, labels, enc_circle, center, color,
                cluster_radius, names, (start_idx, end_idx),
            ))

        # ── Store for downstream acts ──
        self._latent_axes = axes
        self._latent_title = title
        self._latent_labels = VGroup(x_label, y_label)

        voice_text = (
            "Now let us explore the latent space, the abstract mathematical world "
            "where the encoder maps every video. "
            "In this space, something truly remarkable happens. "
            "Each video frame is no longer millions of pixel values. "
            "It becomes a single point, a compact vector, in a high-dimensional "
            "semantic coordinate system. "
            "But here is the truly beautiful part: "
            "concepts with similar visual meaning naturally cluster together. "
            "Boats, ships, canoes, and kayaks are all close to each other "
            "because they share the concept of watercraft on water. "
            "Trees, forests, leaves, and grass form their own vegetation group. "
            "And actions like walking, running, jumping, and dancing "
            "cluster together as human motion patterns. "
            "Notice the distances: similar concepts are extremely close, "
            "separated by tiny distances in this space, "
            "while unrelated concepts are far apart, "
            "showing that the encoder has truly learned the semantic "
            "relationships between different visual concepts."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration

            # ── Phase A (0–0.35): Build axes & title ──
            self.play(
                Create(axes, run_time=_rt(dur, 0, 0.35, fill=0.50)),
                FadeIn(title, run_time=_rt(dur, 0, 0.35, fill=0.30)),
                FadeIn(x_label, run_time=_rt(dur, 0, 0.35, fill=0.25)),
                FadeIn(y_label, run_time=_rt(dur, 0, 0.35, fill=0.25)),
            )
            # 🔑 FadeOut axis labels to reduce visual clutter before thumbnails arrive
            self.play(
                FadeOut(x_label, run_time=_rt(dur, 0.32, 0.36, fill=0.50)),
                FadeOut(y_label, run_time=_rt(dur, 0.32, 0.36, fill=0.50)),
            )

            # ── Phase B1 (0.35–0.48): Thumbnails appear on left ──
            self.play(
                FadeIn(all_thumbnails, shift=RIGHT * 0.3, lag_ratio=0.05,
                       run_time=_rt(dur, 0.35, 0.48)),
            )

            # ── Phase B2 (0.48–0.58): Thumbnails fly → scattered dots ──
            transforms_scatter = []
            for i, thumb_item in enumerate(all_thumbnails):
                if i < len(all_scattered_dots):
                    sx = rng.uniform(-3.0, 3.0)
                    sy = rng.uniform(-2.0, 2.0)
                    target_pos = axes.coords_to_point(sx, sy)
                    all_scattered_dots[i].move_to(target_pos).set_opacity(1)
                    transforms_scatter.append(
                        ReplacementTransform(thumb_item, all_scattered_dots[i])
                    )
            self.play(
                AnimationGroup(*transforms_scatter, lag_ratio=0.03),
                run_time=_rt(dur, 0.48, 0.58),
            )

            # ── Phase B3a (0.55–0.68): 🔑 Cluster 1 (Boat/Ship/Canoe/Kayak) — voice says "Boats, ships..." ──
            cd0 = cluster_data[0]
            transforms_c1 = []
            for j in range(*cd0[7]):  # scattered indices
                scattered = all_scattered_dots[j]
                final_dot = cd0[0][j - cd0[7][0]]
                transforms_c1.append(ReplacementTransform(scattered, final_dot))
            transforms_c1.append(FadeIn(cd0[1], shift=DOWN * 0.08))
            transforms_c1.append(cd0[2].animate.set_stroke(opacity=0.45))
            self.play(
                AnimationGroup(*transforms_c1, lag_ratio=0.10),
                run_time=_rt(dur, 0.55, 0.68, fill=0.95),
            )

            # ── Phase B3b (0.68–0.80): 🔑 Cluster 2 (Tree/Forest/Leaf/Grass) — voice says "Trees, forests..." ──
            cd1 = cluster_data[1]
            transforms_c2 = []
            for j in range(*cd1[7]):
                scattered = all_scattered_dots[j]
                final_dot = cd1[0][j - cd1[7][0]]
                transforms_c2.append(ReplacementTransform(scattered, final_dot))
            transforms_c2.append(FadeIn(cd1[1], shift=DOWN * 0.08))
            transforms_c2.append(cd1[2].animate.set_stroke(opacity=0.45))
            self.play(
                AnimationGroup(*transforms_c2, lag_ratio=0.10),
                run_time=_rt(dur, 0.68, 0.80, fill=0.95),
            )

            # ── Phase B3c (0.80–0.90): 🔑 Cluster 3 (Walking/Running/Jumping/Dancing) — voice says "And actions..." ──
            cd2 = cluster_data[2]
            transforms_c3 = []
            for j in range(*cd2[7]):
                scattered = all_scattered_dots[j]
                final_dot = cd2[0][j - cd2[7][0]]
                transforms_c3.append(ReplacementTransform(scattered, final_dot))
            transforms_c3.append(FadeIn(cd2[1], shift=DOWN * 0.08))
            transforms_c3.append(cd2[2].animate.set_stroke(opacity=0.45))
            self.play(
                AnimationGroup(*transforms_c3, lag_ratio=0.10),
                run_time=_rt(dur, 0.80, 0.90, fill=0.95),
            )

            # ── Build persistent cluster reference ──
            all_cluster_visuals = VGroup()
            self._cluster_circle_info = []
            for cd in cluster_data:
                all_cluster_visuals.add(cd[0], cd[1], cd[2])
                self._cluster_circle_info.append((
                    cd[3], cd[5] + 0.38, cd[4], cd[2],
                ))
            self._all_clusters_visual = all_cluster_visuals
            self._cluster_persist = VGroup(
                axes, title, all_cluster_visuals,
            )
            self._cluster_axes = VGroup(axes, title)

            # 🔑 Store cluster configs for act10 rebuild (after FadeOut transition)
            self._stored_cluster_configs = []
            for cd in cluster_data:
                final_dots, labels, enc_circle, center, color, cluster_radius, names, scattered_indices = cd
                positions = [d.get_center() for d in final_dots]
                self._stored_cluster_configs.append((positions, names, color, center, cluster_radius))

            # ── Phase C (0.87–0.98): Distance annotations ──
            boat_dots = cluster_data[0][0]
            tree_dots = cluster_data[1][0]

            short_line = DashedLine(
                boat_dots[0].get_center(), boat_dots[1].get_center(),
                color=HIGHLIGHT_YELLOW, stroke_width=2, dash_length=0.08,
            )
            short_dist = spaced_text(
                "d = 0.12", font_size=11, color=HIGHLIGHT_YELLOW, spacing=1.14,
            ).next_to(short_line, RIGHT, buff=0.1)

            long_line = DashedLine(
                boat_dots[0].get_center(), tree_dots[0].get_center(),
                color=RED_CHANNEL, stroke_width=2, dash_length=0.1,
            )
            long_dist = spaced_text(
                "d = 3.75", font_size=11, color=RED_CHANNEL, spacing=1.14,
            ).move_to(long_line.get_center() + UP * 0.25)

            sim_text = spaced_text(
                "Similar concepts → close together",
                font_size=17, color=HIGHLIGHT_YELLOW, spacing=1.18,
            ).to_edge(DOWN, buff=0.4)

            self._distance_annotations = VGroup(short_line, short_dist, long_line, long_dist, sim_text)

            phase_c_time = _rt(dur, 0.87, 0.92)
            self.play(
                Create(short_line, run_time=phase_c_time * 0.30),
                FadeIn(short_dist, run_time=phase_c_time * 0.25),
            )
            self.play(
                Create(long_line, run_time=phase_c_time * 0.30),
                FadeIn(long_dist, run_time=phase_c_time * 0.25),
            )
            self.play(FadeIn(sim_text, shift=UP * 0.15, run_time=phase_c_time * 0.20))
            self.wait(max(0.03, dur * 0.02))

        # Fade Out toàn bộ Act 9 trước khi chuyển sang Act 10.
        # Dùng trực tiếp self.mobjects để không bỏ sót các phần tử đã được
        # thêm riêng lẻ vào Scene (axes, dots, labels, circle, annotations...).
        act9_mobjects = list(self.mobjects)
        if act9_mobjects:
            self.play(
                *[FadeOut(mob) for mob in act9_mobjects],
                run_time=0.7,
            )

        # Bảo đảm Scene hoàn toàn sạch, tránh hình Act 9 còn mờ phía sau Act 10.
        self.clear()
        self.wait(0.4)

    # ══════════════════════════════════════════════════════════════
    # ACT 10: Noise Filtering — VOICE SYNCED (~38s)
    #   Rebuilds latent space view (act9 FadeOut → clean transition)
    # ══════════════════════════════════════════════════════════════
    def act10_noise_filter(self):
        rng = np.random.default_rng(123)

        # ── 🔑 Rebuild latent space view (clean slate after act9 FadeOut) ──
        if hasattr(self, '_stored_cluster_configs') and self._stored_cluster_configs:
            axes = Axes(
                x_range=[-4, 4, 1], y_range=[-3, 3, 1],
                x_length=10, y_length=5.5,
                axis_config={"color": DIM_GRAY, "stroke_width": 2, "include_ticks": False},
                tips=True,
            ).scale(0.72).move_to(DOWN * 0.2)

            title = spaced_text(
                "Latent Space", font_size=30, color=SOFT_WHITE, weight=BOLD, spacing=1.22,
            ).to_edge(UP, buff=0.25)

            all_cluster_visuals = VGroup()
            self._cluster_circle_info = []
            for positions, names, color, center, cluster_radius in self._stored_cluster_configs:
                final_dots = VGroup()
                labels = VGroup()
                for pos, name in zip(positions, names):
                    dot = Dot(pos, radius=0.07, color=color)
                    final_dots.add(dot)
                    lbl = spaced_text(
                        name, font_size=13, color=color, weight=NORMAL,
                        font="sans-serif", spacing=1.14,
                    )
                    lbl.set_stroke(width=0)
                    lbl.set_fill(opacity=0.90)
                    lbl.next_to(dot, DOWN, buff=0.08)
                    labels.add(lbl)

                enc_circle = DashedVMobject(
                    Circle(
                        radius=cluster_radius + 0.38, color=color, stroke_width=1.6,
                    ).move_to(center),
                    num_dashes=16,
                )
                enc_circle.set_stroke(opacity=0.45)

                all_cluster_visuals.add(final_dots, labels, enc_circle)
                self._cluster_circle_info.append((
                    center, cluster_radius + 0.38, color, enc_circle,
                ))

            self._all_clusters_visual = all_cluster_visuals
            self._cluster_persist = VGroup(axes, title, all_cluster_visuals)

            # Brief pause to show clean screen, then show rebuilt view
            self.wait(0.3)
            self.play(FadeIn(self._cluster_persist, run_time=0.8))

        # ── Phase A: Scatter noise dots ──
        noise_names = [
            "ripple₁", "ripple₂", "ripple₃", "ripple₄",
            "dust₁", "dust₂", "dust₃",
            "shadow₁", "shadow₂",
            "flicker₁", "grain₁", "blur₁",
        ]
        noise_dots = VGroup()
        noise_labels = VGroup()
        # Place noise away from existing clusters
        cluster_centers_xy = [np.array([-2.3, 1.2]), np.array([2.2, 1.5]), np.array([0.0, -1.6])]
        for name in noise_names:
            # Try to place noise away from cluster centers
            for _ in range(50):
                pos2d = np.array([rng.uniform(-3.5, 3.5), rng.uniform(-2.2, 2.2)])
                if all(np.linalg.norm(pos2d - cc) > 1.0 for cc in cluster_centers_xy):
                    break
            pos = np.array([pos2d[0], pos2d[1], 0])
            dot = Dot(pos, radius=0.04, color=RED_CHANNEL)
            lbl = spaced_text(
                name, font_size=7, color=RED_CHANNEL, weight=NORMAL, spacing=1.12,
            ).next_to(dot, DOWN, buff=0.04)
            lbl.set_stroke(width=0)
            noise_dots.add(dot)
            noise_labels.add(lbl)

        noise_group = VGroup(noise_dots, noise_labels)

        # Callout
        noise_callout = spaced_text(
            "← Pixel-level noise", font_size=15, color=RED_CHANNEL, spacing=1.16,
        ).next_to(noise_dots[0], RIGHT, buff=0.3)

        # ── Phase B: Filtering ring ──
        pulse_ring = Circle(
            radius=0.15, color=HIGHLIGHT_YELLOW,
            stroke_width=3, stroke_opacity=0.9,
        ).move_to(ORIGIN)

        # Result labels
        noise_result = spaced_text(
            "Noise → Discarded", font_size=18, color=RED_CHANNEL, spacing=1.16,
        ).to_edge(DOWN, buff=0.8).shift(LEFT * 3)
        semantic_result = spaced_text(
            "Semantics → Preserved", font_size=18, color=GREEN_CHANNEL, spacing=1.16,
        ).to_edge(DOWN, buff=0.8).shift(RIGHT * 3)

        # Phase C: Pure result
        pure_text = spaced_text(
            "Pure Semantic Structure", font_size=22,
            color=HIGHLIGHT_YELLOW, weight=BOLD, spacing=1.20,
        ).to_edge(DOWN, buff=0.4)

        voice_text = (
            "Now watch what happens to all the noise in this space. "
            "These small red dots represent unpredictable pixel-level details: "
            "individual water ripple positions, tiny floating dust particles, "
            "flickering shadows, and random sensor grain. "
            "As the encoder processes the data, a natural filtering mechanism "
            "activates. The encoding process automatically pushes away everything "
            "that cannot be reliably predicted from context. "
            "All of these noisy, unpredictable details are pushed to the edges "
            "and completely eliminated from the final representation. "
            "They carry absolutely no semantic value, they tell us nothing "
            "about what is actually happening in the scene, "
            "so the latent space simply discards them. "
            "What remains is only the pure, meaningful semantic structure, "
            "the true understanding of the visual world."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration

            # ── Phase A (0–0.30): Show noise dots with FLICKER ──
            self.play(FadeIn(noise_group, run_time=_rt(dur, 0, 0.15)))
            self.play(FadeIn(noise_callout, run_time=_rt(dur, 0.15, 0.20)))
            # Flicker noise dots
            flicker_time = _rt(dur, 0.20, 0.30)
            for _ in range(3):
                self.play(noise_dots.animate.set_opacity(0.2), run_time=flicker_time * 0.17)
                self.play(noise_dots.animate.set_opacity(1.0), run_time=flicker_time * 0.17)
            self.wait(max(0.03, dur * 0.02))

            # ── Phase B (0.30–0.68): Filter ring expands; noise eliminated ──
            self.play(FadeOut(noise_callout, run_time=_rt(dur, 0.30, 0.33)))
            self.add(pulse_ring)
            # Ring expands
            self.play(
                pulse_ring.animate.scale(50).set_opacity(0),
                run_time=_rt(dur, 0.33, 0.52),
                rate_func=smooth,
            )
            self.remove(pulse_ring)
            # Noise dots SHRINK and FADE staggered
            self.play(
                AnimationGroup(
                    *[
                        AnimationGroup(
                            dot.animate.scale(0.3).set_opacity(0),
                            lbl.animate.set_opacity(0),
                            run_time=_rt(dur, 0.52, 0.68, fill=0.40) / len(noise_dots) * 2,
                        )
                        for dot, lbl in zip(noise_dots, noise_labels)
                    ],
                    lag_ratio=0.03,
                ),
                run_time=_rt(dur, 0.52, 0.68, fill=0.85),
            )
            self.remove(noise_group)

            # ── Phase C (0.68–0.98): Pure result, solid circles, labels ──
            # Semantic clusters flash green briefly
            if self._all_clusters_visual:
                self.play(
                    self._all_clusters_visual.animate.set_opacity(1.2),
                    run_time=_rt(dur, 0.68, 0.73, fill=0.50),
                )
                self.play(
                    self._all_clusters_visual.animate.set_opacity(1.0),
                    run_time=_rt(dur, 0.73, 0.78, fill=0.50),
                )

            self.play(
                FadeIn(noise_result, shift=UP * 0.15, run_time=_rt(dur, 0.78, 0.84)),
                FadeIn(semantic_result, shift=UP * 0.15, run_time=_rt(dur, 0.78, 0.84)),
            )

            # Convert dashed cluster circles to SOLID
            solid_circles = VGroup()
            if self._cluster_circle_info:
                for center, radius, color, dashed_circle in self._cluster_circle_info:
                    new_circle = Circle(
                        radius=radius, color=color,
                        stroke_width=2.2, stroke_opacity=0.55, fill_opacity=0,
                    ).move_to(center)
                    solid_circles.add(new_circle)
                    dashed_circle.set_stroke(opacity=0)
            # Add solid circles to persist group
            if len(solid_circles) > 0:
                self.play(FadeIn(solid_circles, run_time=_rt(dur, 0.84, 0.90)))
                self._cluster_persist.add(solid_circles)

            # Show pure text
            self.play(
                FadeOut(noise_result), FadeOut(semantic_result),
                run_time=_rt(dur, 0.90, 0.93),
            )
            self.play(FadeIn(pure_text, shift=UP * 0.1, run_time=_rt(dur, 0.93, 0.98)))
            self.wait(max(0.02, dur * 0.02))

        self.play(FadeOut(pure_text, run_time=0.3))
        # 🔑 Clusters persist (rebuilt at act10 start, used through act12)

    # ══════════════════════════════════════════════════════════════
    # ACT 11: Pure Semantic Vector & Comparison — VOICE SYNCED (~38s)
    #   Clusters remain visible (dimmed in Phase C)
    # ══════════════════════════════════════════════════════════════
    def act11_semantic_vector(self):
        # ── Phase A+B: Semantic arrow + formula (voice part 1) ──
        sem_arrow = Arrow(
            LEFT * 3 + UP * 1.0, RIGHT * 0 + UP * 1.0,
            color=CONTEXT_BLUE, stroke_width=6, buff=0,
        )
        sem_label = spaced_text(
            "Boat is moving right →", font_size=20,
            color=CONTEXT_BLUE, weight=BOLD, spacing=1.20,
        ).next_to(sem_arrow, UP, buff=0.2)

        formula = MathTex(
            r"z = E_\theta(x) \in \mathbb{R}^{d}",
            font_size=34, color=HIGHLIGHT_YELLOW,
        ).to_edge(DOWN, buff=0.8)
        formula_desc = spaced_text(
            "Pure semantic embedding — 1 compact vector, d dimensions",
            font_size=15, color=DIM_GRAY, spacing=1.16,
        ).next_to(formula, DOWN, buff=0.12)

        voice_text_1 = (
            "What remains after this filtering process is an extremely pure "
            "and crystal-clear semantic vector. "
            "It carries only the essential message: "
            "there is a boat, and it is moving to the right. "
            "No wasted computation on random noise. No futile attempts "
            "to guess unpredictable pixel values. "
            "Just pure, distilled understanding of the visual world."
        )
        with self.voiceover(text=voice_text_1) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text_1)
            dur1 = tracker.duration

            # arrow + label 0–0.40
            self.play(
                Create(sem_arrow, run_time=_rt(dur1, 0, 0.40)),
                FadeIn(sem_label, run_time=_rt(dur1, 0, 0.40)),
            )
            # glow pulse 0.40–0.60
            self.play(
                sem_arrow.animate.set_stroke(width=12),
                rate_func=there_and_back, run_time=_rt(dur1, 0.40, 0.60),
            )
            # formula 0.60–0.95
            self.play(
                Write(formula, run_time=_rt(dur1, 0.60, 0.95)),
                FadeIn(formula_desc, run_time=_rt(dur1, 0.60, 0.95)),
            )
            self.wait(max(0.03, dur1 * 0.05))

        # ── Cleanup arrow + formula ──
        fade_away = VGroup(sem_arrow, sem_label, formula, formula_desc)
        self.play(FadeOut(fade_away, run_time=0.5))

        # ── 🔑 DIM clusters to ~12% opacity (keep as background context) ──
        if self._cluster_persist:
            self.play(
                self._cluster_persist.animate.set_opacity(0.12),
                run_time=1.0,
            )

        # ── Phase C: Side-by-side comparison (voice part 2) ──
        # ── Pixel Space box (left) ──
        pixel_box_rect = Rectangle(
            width=4.5, height=3.5,
            color=RED_CHANNEL, fill_opacity=0.06, stroke_width=2,
        ).move_to(LEFT * 3.5).set_z_index(5)
        pixel_box_title = spaced_text(
            "Pixel Space", font_size=19, color=RED_CHANNEL, weight=BOLD, spacing=1.20,
        ).next_to(pixel_box_rect, UP, buff=0.15)
        pixel_box_dim = MathTex(
            r"\mathbb{R}^{H \times W \times 3}",
            font_size=20, color=RED_CHANNEL,
        ).next_to(pixel_box_title, DOWN, buff=0.1)

        rng = np.random.default_rng(88)
        pixel_mini = VGroup()
        for r in range(6):
            for c in range(6):
                sq = Square(side_length=0.4, stroke_width=0.3, stroke_color=DIM_GRAY)
                val = rng.integers(0, 256)
                sq.set_fill(
                    color=interpolate_color(RED_CHANNEL, SOFT_WHITE, val / 255.0),
                    opacity=0.6,
                )
                sq.move_to(
                    pixel_box_rect.get_center()
                    + RIGHT * (c - 2.5) * 0.42
                    + DOWN * (r - 2.5) * 0.42
                    + DOWN * 0.2,
                )
                pixel_mini.add(sq)

        # ── Latent Space box (right) ──
        latent_box_rect = Rectangle(
            width=4.5, height=3.5,
            color=GREEN_CHANNEL, fill_opacity=0.06, stroke_width=2,
        ).move_to(RIGHT * 3.5).set_z_index(5)
        latent_box_title = spaced_text(
            "Latent Space", font_size=19, color=GREEN_CHANNEL, weight=BOLD, spacing=1.20,
        ).next_to(latent_box_rect, UP, buff=0.15)
        latent_box_dim = MathTex(
            r"\mathbb{R}^{d}", font_size=20, color=GREEN_CHANNEL,
        ).next_to(latent_box_title, DOWN, buff=0.1)

        # 🔑 "1 vector" — prominent visualization
        clean_dot = Dot(
            latent_box_rect.get_center() + UP * 0.2,
            radius=0.22, color=HIGHLIGHT_YELLOW,
        )
        clean_glow = Circle(
            radius=0.45, color=HIGHLIGHT_YELLOW,
            fill_opacity=0.08, stroke_width=1, stroke_opacity=0.4,
        ).move_to(clean_dot)
        clean_arrow = Arrow(
            clean_dot.get_center(),
            clean_dot.get_center() + RIGHT * 1.2,
            color=CONTEXT_BLUE, stroke_width=3,
        )
        clean_label = spaced_text(
            "1 compact vector = pure meaning",
            font_size=15, color=HIGHLIGHT_YELLOW, weight=BOLD, spacing=1.18,
        ).next_to(clean_dot, DOWN, buff=0.55)

        # Transform arrow between boxes
        transform_arrow = Arrow(
            pixel_box_rect.get_right() + LEFT * 0.1,
            latent_box_rect.get_left() + RIGHT * 0.1,
            color=SOFT_WHITE, stroke_width=3, buff=0.1,
        ).set_z_index(5)
        transform_label = spaced_text(
            "Encoder compresses", font_size=15, color=SOFT_WHITE, spacing=1.16,
        ).next_to(transform_arrow, UP, buff=0.1)

        # Size contrast labels
        pixel_size = spaced_text(
            "millions of pixel values → chaos",
            font_size=12, color=DIM_GRAY, spacing=1.16,
        ).next_to(pixel_box_rect, DOWN, buff=0.15)
        latent_size = spaced_text(
            "1 stable vector → pure semantics",
            font_size=12, color=DIM_GRAY, spacing=1.16,
        ).next_to(latent_box_rect, DOWN, buff=0.15)

        all_comparison = VGroup(
            pixel_box_rect, pixel_box_title, pixel_box_dim, pixel_mini,
            latent_box_rect, latent_box_title, latent_box_dim,
            clean_dot, clean_glow, clean_arrow, clean_label,
            transform_arrow, transform_label,
            pixel_size, latent_size,
        ).set_z_index(5)

        voice_text_2 = (
            "By predicting in the latent space instead of the pixel space, "
            "V-JEPA completely eliminates all computational waste. "
            "On the left, you see the pixel space: millions of chaotic, "
            "fluctuating numbers that the model would have to reconstruct "
            "with painstaking precision. On the right, the latent space: "
            "a single, clean, stable vector that captures only the semantic "
            "essence of the scene. "
            "This dramatic compression, from millions of values down to "
            "a single compact vector of just a few hundred dimensions, "
            "is what makes V-JEPA so fundamentally powerful and efficient."
        )
        with self.voiceover(text=voice_text_2) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text_2)
            dur2 = tracker.duration

            # left box 0–0.16
            self.play(
                FadeIn(pixel_box_rect, run_time=_rt(dur2, 0, 0.08)),
                FadeIn(pixel_box_title, run_time=_rt(dur2, 0, 0.08)),
                FadeIn(pixel_box_dim, run_time=_rt(dur2, 0, 0.08)),
            )
            # pixel mini grid 0.08–0.22
            self.play(FadeIn(pixel_mini, lag_ratio=0.01, run_time=_rt(dur2, 0.08, 0.22)))
            # transform arrow 0.22–0.35
            self.play(
                Create(transform_arrow, run_time=_rt(dur2, 0.22, 0.35)),
                FadeIn(transform_label, run_time=_rt(dur2, 0.22, 0.30)),
            )
            # right box 0.35–0.50
            self.play(
                FadeIn(latent_box_rect, run_time=_rt(dur2, 0.35, 0.50)),
                FadeIn(latent_box_title, run_time=_rt(dur2, 0.35, 0.45)),
                FadeIn(latent_box_dim, run_time=_rt(dur2, 0.35, 0.45)),
            )
            # 1-dot + glow + arrow 0.50–0.70
            self.play(
                FadeIn(clean_dot, scale=0.3, run_time=_rt(dur2, 0.50, 0.70)),
                FadeIn(clean_glow, run_time=_rt(dur2, 0.50, 0.60)),
                Create(clean_arrow, run_time=_rt(dur2, 0.60, 0.70)),
                FadeIn(clean_label, run_time=_rt(dur2, 0.60, 0.70)),
            )
            # size labels 0.70–0.85
            self.play(
                FadeIn(pixel_size, run_time=_rt(dur2, 0.70, 0.78)),
                FadeIn(latent_size, run_time=_rt(dur2, 0.70, 0.78)),
            )
            # pulse clean dot 0.85–0.95
            self.play(
                clean_dot.animate.scale(1.4),
                clean_glow.animate.scale(1.4),
                rate_func=there_and_back, run_time=_rt(dur2, 0.85, 0.95),
            )
            self.wait(max(0.03, dur2 * 0.05))

        self.play(FadeOut(all_comparison, run_time=0.8))
        # 🔑 Keep clusters dimmed — not removed!
        self.wait(0.05)

    # ══════════════════════════════════════════════════════════════
    # ACT 12: Summary & Bridge to Chapter 3 (~29s)
    #   🔑 Dimmed clusters remain visible as background
    #   🔑 Prominent "1 vector" pipeline visualization
    # ══════════════════════════════════════════════════════════════
    def act12_summary(self):
        rng = np.random.default_rng(99)

        # ── Red box: Pixel Space ──
        red_box = Rectangle(
            width=5, height=2.8,
            color=RED_CHANNEL, fill_opacity=0.06, stroke_width=2,
        ).move_to(LEFT * 3.5).set_z_index(5)
        red_title = spaced_text(
            "Pixel Space", font_size=24, color=RED_CHANNEL, weight=BOLD, spacing=1.20,
        ).next_to(red_box, UP, buff=0.15).set_z_index(5)
        red_x = Text("✗", font_size=56, color=RED_CHANNEL).move_to(
            red_box.get_center() + UP * 0.4,
        ).set_z_index(5)
        red_desc1 = spaced_text(
            "Millions of pixel values",
            font_size=16, color=DIM_GRAY, spacing=1.16,
        ).move_to(red_box.get_center() + DOWN * 0.2).set_z_index(5)
        red_desc2 = spaced_text(
            "High noise · Low efficiency",
            font_size=16, color=DIM_GRAY, spacing=1.16,
        ).move_to(red_box.get_center() + DOWN * 0.6).set_z_index(5)

        # ── Green box: Latent Space ──
        green_box = Rectangle(
            width=5, height=2.8,
            color=GREEN_CHANNEL, fill_opacity=0.06, stroke_width=2,
        ).move_to(RIGHT * 3.5).set_z_index(5)
        green_title = spaced_text(
            "Latent Space", font_size=24, color=GREEN_CHANNEL, weight=BOLD, spacing=1.20,
        ).next_to(green_box, UP, buff=0.15).set_z_index(5)
        green_check = Text("✓", font_size=56, color=GREEN_CHANNEL).move_to(
            green_box.get_center() + UP * 0.4,
        ).set_z_index(5)
        green_desc1 = spaced_text(
            "1 compact semantic vector",
            font_size=16, color=DIM_GRAY, spacing=1.16,
        ).move_to(green_box.get_center() + DOWN * 0.2).set_z_index(5)
        green_desc2 = spaced_text(
            "Low noise · High generalization",
            font_size=16, color=DIM_GRAY, spacing=1.16,
        ).move_to(green_box.get_center() + DOWN * 0.6).set_z_index(5)

        red_group = VGroup(red_box, red_title, red_x, red_desc1, red_desc2).set_z_index(5)
        green_group = VGroup(green_box, green_title, green_check, green_desc1, green_desc2).set_z_index(5)

        # 🔑 Center pipeline: many pixel dots → Encoder arrow → 1 vector dot
        # Small pixel dots (left of center)
        pixel_dots = VGroup()
        for _ in range(8):
            d = Dot(
                point=np.array([rng.uniform(-0.9, -0.2), rng.uniform(-0.5, 0.5), 0]),
                radius=0.05, color=RED_CHANNEL,
            )
            pixel_dots.add(d)
        pixel_dots_label = spaced_text(
            "many values", font_size=11, color=RED_CHANNEL, spacing=1.14,
        ).next_to(pixel_dots, DOWN, buff=0.15)

        # Encoder arrow in center
        center_arrow = Arrow(LEFT * 0.0, RIGHT * 0.5, color=SOFT_WHITE, stroke_width=3, buff=0.1)
        center_arrow_label = spaced_text(
            "Encoder", font_size=13, color=PREDICTOR_ORANGE, spacing=1.16,
        ).next_to(center_arrow, DOWN, buff=0.1)

        # 1 vector dot (right of center)
        one_vector_dot = Dot(point=RIGHT * 0.8, radius=0.18, color=HIGHLIGHT_YELLOW)
        one_vector_glow = Circle(
            radius=0.36, color=HIGHLIGHT_YELLOW,
            fill_opacity=0.1, stroke_width=1.5, stroke_opacity=0.5,
        ).move_to(one_vector_dot)
        one_vector_label = spaced_text(
            "1 vector", font_size=14, color=HIGHLIGHT_YELLOW, weight=BOLD, spacing=1.20,
        ).next_to(one_vector_dot, DOWN, buff=0.3)

        pipeline_group = VGroup(
            pixel_dots, pixel_dots_label,
            center_arrow, center_arrow_label,
            one_vector_dot, one_vector_glow, one_vector_label,
        ).move_to(DOWN * 1.2).set_z_index(10)

        # V-JEPA logo
        vjepa_text = spaced_text(
            "V-JEPA", font_size=42, color=HIGHLIGHT_YELLOW, weight=BOLD, spacing=1.25,
        ).move_to(DOWN * 2.8).set_z_index(5)

        chapter3_hint = spaced_text(
            "→ Chapter 3: Architecture & Tokenization",
            font_size=18, color=DIM_GRAY, spacing=1.18,
        ).to_edge(DOWN, buff=0.3).set_z_index(5)

        all_act12 = VGroup(
            red_group, green_group, pipeline_group, vjepa_text, chapter3_hint,
        ).set_z_index(5)

        voice_text = (
            "This is the fundamental philosophical advantage of V-JEPA. "
            "Pixel-level methods are plagued by noise and inefficiency "
            "because they try to copy every meaningless detail at the "
            "expense of actual understanding. "
            "In contrast, the latent-space approach compresses everything "
            "into a single, clean vector that captures only the semantic "
            "essence of the scene. "
            "Instead of millions of fluctuating pixel values, V-JEPA works "
            "with just one compact vector that represents pure meaning. "
            "It delivers dramatically lower noise and far superior generalization. "
            "Now that we understand why predicting in latent space is so powerful, "
            "the natural question is: what does the actual architecture look like? "
            "How does V-JEPA transform raw video into these semantic tokens, "
            "and how do its three neural networks work together "
            "to make this prediction happen? "
            "Let us find out in Chapter 3."
        )
        with self.voiceover(text=voice_text) as tracker:
            self._current_tracker = tracker
            self._track_subtitle(voice_text)
            dur = tracker.duration

            # boxes stagger 0–0.20
            self.play(
                AnimationGroup(
                    FadeIn(red_group, shift=UP * 0.3),
                    FadeIn(green_group, shift=UP * 0.3),
                    lag_ratio=0.3,
                ),
                run_time=_rt(dur, 0, 0.20),
            )
            # pixel dots appear 0.20–0.32
            self.play(
                FadeIn(pixel_dots, lag_ratio=0.08, run_time=_rt(dur, 0.20, 0.28)),
                FadeIn(pixel_dots_label, run_time=_rt(dur, 0.20, 0.28)),
            )
            # encoder arrow + 1 vector dot 0.28–0.45
            self.play(
                Create(center_arrow, run_time=_rt(dur, 0.28, 0.38)),
                FadeIn(center_arrow_label, run_time=_rt(dur, 0.28, 0.38)),
            )
            self.play(
                FadeIn(one_vector_dot, scale=0.3, run_time=_rt(dur, 0.38, 0.45)),
                FadeIn(one_vector_glow, run_time=_rt(dur, 0.38, 0.45)),
                FadeIn(one_vector_label, run_time=_rt(dur, 0.38, 0.45)),
            )
            # 🔑 Transform pixel dots → shrink toward single vector 0.45–0.55
            self.play(
                pixel_dots.animate.scale(0.3).set_opacity(0.2),
                one_vector_dot.animate.scale(1.6),
                one_vector_glow.animate.scale(1.4),
                rate_func=there_and_back, run_time=_rt(dur, 0.45, 0.58),
            )
            # V-JEPA text 0.58–0.70
            self.play(FadeIn(vjepa_text, scale=0.6, run_time=_rt(dur, 0.58, 0.70)))
            # Pulse V-JEPA 0.70–0.82
            self.play(
                vjepa_text.animate.scale(1.15),
                rate_func=there_and_back, run_time=_rt(dur, 0.70, 0.82),
            )
            # Chapter 3 hint 0.82–0.95
            self.play(FadeIn(chapter3_hint, shift=UP * 0.15, run_time=_rt(dur, 0.82, 0.95)))
            self.wait(max(0.03, dur * 0.05))

        # Final fadeout — everything including dimmed clusters
        if self._cluster_persist:
            self.play(
                FadeOut(all_act12, run_time=1.0),
                FadeOut(self._cluster_persist, run_time=1.0),
            )
        else:
            self.play(FadeOut(all_act12, run_time=1.0))
        self.wait(0.2)

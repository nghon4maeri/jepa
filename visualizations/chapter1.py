"""
V-JEPA Video - Chapter 1: Images & Video from a Computer's Perspective
Style: 3Blue1Brown (dark background, smooth vector graphics, mathematical visualization)
Voiceover: English (Generic TTS - Male, UK accent)
Render: 480p15 (-ql)
"""

from manim import *
from manim_voiceover import VoiceoverScene
from generic_tts import GenericEdgeTTS
import numpy as np
import os
import numpy as np

def _create_brain_icon(self):
    brain = VGroup()

    # ── Brain outline ──────────────────────────────────────────
    left = VMobject()
    left.set_points_smoothly([
        LEFT * 1.35 + UP * 0.15,
        LEFT * 1.45 + UP * 0.75,
        LEFT * 1.05 + UP * 1.25,
        LEFT * 0.45 + UP * 1.40,
        LEFT * 0.10 + UP * 1.05,
        LEFT * 0.05 + UP * 0.45,
        LEFT * 0.10 + DOWN * 0.25,
        LEFT * 0.45 + DOWN * 0.85,
        LEFT * 1.00 + DOWN * 0.80,
        LEFT * 1.35 + DOWN * 0.25,
        LEFT * 1.35 + UP * 0.15,
    ])

    right = VMobject()
    right.set_points_smoothly([
        RIGHT * 1.35 + UP * 0.15,
        RIGHT * 1.45 + UP * 0.75,
        RIGHT * 1.05 + UP * 1.25,
        RIGHT * 0.45 + UP * 1.40,
        RIGHT * 0.10 + UP * 1.05,
        RIGHT * 0.05 + UP * 0.45,
        RIGHT * 0.10 + DOWN * 0.25,
        RIGHT * 0.45 + DOWN * 0.85,
        RIGHT * 1.00 + DOWN * 0.80,
        RIGHT * 1.35 + DOWN * 0.25,
        RIGHT * 1.35 + UP * 0.15,
    ])

    for hemisphere in [left, right]:
        hemisphere.set_stroke(
            color=SOFT_WHITE,
            width=3,
            opacity=0.9,
        )
        hemisphere.set_fill(
            color=BLUE_E,
            opacity=0.18,
        )

    brain.add(left, right)

    # ── Central separation ─────────────────────────────────────
    center = Line(
        UP * 1.15,
        DOWN * 0.75,
        color=SOFT_WHITE,
        stroke_width=2,
    )
    brain.add(center)

    # ── Brain folds ────────────────────────────────────────────
    folds = VGroup()

    fold_data = [
        ([-1.25, 0.75], [-0.65, 0.85], [-0.25, 0.65]),
        ([-1.30, 0.20], [-0.75, 0.35], [-0.25, 0.15]),
        ([-1.10, -0.35], [-0.65, -0.15], [-0.20, -0.30]),
        ([-0.90, -0.65], [-0.50, -0.55], [-0.20, -0.70]),

        ([1.25, 0.75], [0.65, 0.85], [0.25, 0.65]),
        ([1.30, 0.20], [0.75, 0.35], [0.25, 0.15]),
        ([1.10, -0.35], [0.65, -0.15], [0.20, -0.30]),
        ([0.90, -0.65], [0.50, -0.55], [0.20, -0.70]),
    ]

    for p1, p2, p3 in fold_data:
        curve = VMobject()
        curve.set_points_smoothly([
            np.array([p1[0], p1[1], 0]),
            np.array([p2[0], p2[1], 0]),
            np.array([p3[0], p3[1], 0]),
        ])
        curve.set_stroke(
            color=SOFT_WHITE,
            width=2,
            opacity=0.65,
        )
        folds.add(curve)

    brain.add(folds)

    # ── Neural network nodes ───────────────────────────────────
    nodes = VGroup(
        Dot(LEFT * 0.85 + UP * 0.65, radius=0.07),
        Dot(LEFT * 0.95 + DOWN * 0.15, radius=0.07),
        Dot(LEFT * 0.55 + DOWN * 0.55, radius=0.07),

        Dot(RIGHT * 0.85 + UP * 0.65, radius=0.07),
        Dot(RIGHT * 0.95 + DOWN * 0.15, radius=0.07),
        Dot(RIGHT * 0.55 + DOWN * 0.55, radius=0.07),
    )

    nodes.set_color(SOFT_WHITE)

    # Connections
    connections = VGroup(
        Line(nodes[0].get_center(), nodes[1].get_center()),
        Line(nodes[1].get_center(), nodes[2].get_center()),
        Line(nodes[3].get_center(), nodes[4].get_center()),
        Line(nodes[4].get_center(), nodes[5].get_center()),
        Line(nodes[0].get_center(), nodes[4].get_center()),
        Line(nodes[3].get_center(), nodes[1].get_center()),
    )

    connections.set_stroke(
        color=SOFT_WHITE,
        width=1,
        opacity=0.35,
    )

    brain.add(connections, nodes)

    return brain

# ─────────────────── Color Palette (3B1B Style) ───────────────────
BG_COLOR = ManimColor("#1a1a2e")
CONTEXT_BLUE = ManimColor("#5DADE2")
PREDICTOR_ORANGE = ManimColor("#E59866")
TARGET_GRAY = ManimColor("#AAB7B8")
HIGHLIGHT_YELLOW = ManimColor("#F4D03F")
MASK_GRAY = ManimColor("#555555")
RED_CHANNEL = ManimColor("#E74C3C")
GREEN_CHANNEL = ManimColor("#2ECC71")
BLUE_CHANNEL = ManimColor("#3498DB")
SOFT_WHITE = ManimColor("#E8E8E8")
DIM_GRAY = ManimColor("#888888")

# Path to dog image
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DOG_IMAGE_PATH = os.path.join(PROJECT_DIR, "media", "images", "dog_photo.png")


class Chapter1Scene(VoiceoverScene):
    """Chapter 1: Images & Video from a Computer's Perspective & Fill-in-the-Blank"""

    def construct(self):
        self.camera.background_color = BG_COLOR
        self.set_speech_service(GenericEdgeTTS(gender="male", accent="uk"))

        self.part1_visual_world()
        self.part2_fill_in_blank()

    # ══════════════════════════════════════════════════════════════
    # PART 1.1: The Visual World Through the Lens of Mathematics
    # ══════════════════════════════════════════════════════════════
    def part1_visual_world(self):
        # ── Segment 1: Title + Grid background ──
        title = Text(
            "1", font_size=48, color=SOFT_WHITE,
            font="sans-serif", weight=BOLD
        ).move_to(UP * 1.2)
        subtitle = Text(
            "Images & Video from a Computer's Perspective",
            font_size=28, color=DIM_GRAY, font="sans-serif"
        ).move_to(ORIGIN)

        grid = NumberPlane(
            x_range=[-7, 7, 1], y_range=[-4, 4, 1],
            background_line_style={
                "stroke_color": BLUE_E,
                "stroke_width": 0.5,
                "stroke_opacity": 0.15,
            },
            axis_config={"stroke_opacity": 0},
            faded_line_ratio=0,
        )
        grid.set_z_index(-10)

        self.play(FadeIn(grid, run_time=1.0))
        self.play(
            FadeIn(title, shift=DOWN * 0.3, run_time=0.8),
            FadeIn(subtitle, shift=DOWN * 0.2, run_time=0.8),
        )
        self.wait(1.0)
        self.play(FadeOut(title), FadeOut(subtitle), run_time=0.8)

        # ── Segment 2: Dog image + voiceover start ──
        dog_img = ImageMobject(DOG_IMAGE_PATH)
        dog_img.set_height(4.0)
        dog_img.move_to(ORIGIN)

        # Border around image
        img_border = SurroundingRectangle(
            dog_img, color=SOFT_WHITE, buff=0.05, stroke_width=1.5
        )

        with self.voiceover(
            text=(
                "To understand how an AI algorithm like V-JEPA perceives the world, "
                "we must first shed our biological lens. "
                "For a computer, an image has no shape or vivid emotion. "
                "It is simply a two-dimensional grid of numbers "
                "representing the light intensity of three color channels: "
                "Red, Green, and Blue."
            )
        ) as tracker:
            # Show dog image
            self.play(
                FadeIn(dog_img, scale=0.8, run_time=1.2),
                Create(img_border, run_time=1.2),
            )
            self.wait(1.0)



            # Shrink image to left side
            self.play(
                dog_img.animate.scale(0.6).to_edge(LEFT, buff=1.0),
                img_border.animate.scale(0.6).to_edge(LEFT, buff=1.0),
                run_time=1.0,
            )

            # ── Segment 3: Pixel grid (zoomed-in view) ──
            pixel_grid = self._create_pixel_grid(rows=6, cols=8)
            pixel_grid.scale_to_fit_height(3.0)
            pixel_grid.to_edge(RIGHT, buff=1.0)

            arrow = Arrow(
                start=dog_img.get_right(),
                end=pixel_grid.get_left(),
                buff=0.2,
                color=SOFT_WHITE,
            )

            self.play(Create(arrow), run_time=0.8)

            pixel_label = Text(
                "Pixel Values (0–255)", font_size=20, color=DIM_GRAY
            ).next_to(pixel_grid, UP, buff=0.3)

            self.play(
                FadeIn(pixel_grid, shift=RIGHT * 0.3, run_time=1.0),
                FadeIn(pixel_label, run_time=0.8),
            )
            self.wait(1.0)

            self.play(FadeOut(arrow), run_time=0.8)

            # ── Segment 4: Split into RGB channels ──

            r_grid = self._create_channel_grid(6, 4, RED_CHANNEL, "R")
            g_grid = self._create_channel_grid(6, 4, GREEN_CHANNEL, "G")
            b_grid = self._create_channel_grid(6, 4, BLUE_CHANNEL, "B")
            
            arrow = Arrow(
                start=dog_img.get_right(),
                end=r_grid.get_left(),
                buff=0.2,
                color=SOFT_WHITE,
            )
            self.play(Create(arrow), run_time=0.8)


            rgb_group = VGroup(r_grid, g_grid, b_grid).arrange(RIGHT, buff=0.5)
            rgb_group.scale_to_fit_height(2.5)
            rgb_group.move_to(RIGHT * 2.5)

            self.play(
                FadeOut(pixel_grid),
                FadeOut(pixel_label),
                FadeOut(arrow),
                run_time=0.5,
            )
            self.play(
                FadeIn(rgb_group, shift=UP * 0.2, run_time=1.0),
            )

            # Wait for remaining voiceover duration
            self.wait(1.0)

        # ── Segment 5: Image Tensor formula ──
        with self.voiceover(
            text=(
                "A Tensor of shape H multiple W multiple 3."
            )
        ) as tracker:
            formula_img = MathTex(
                r"\text{Image}", r"\in", r"\mathbb{R}^{H \times W \times 3}",
                font_size=40, color=SOFT_WHITE
            )
            formula_img.next_to(rgb_group, DOWN, buff=0.5)

            self.play(Write(formula_img, run_time=1.2))
            self.wait(tracker.duration - 1.2 if tracker.duration > 1.2 else 0.5)

        # ── Cleanup for 3D transition ──
        self.play(
            FadeOut(dog_img), FadeOut(img_border),
            FadeOut(rgb_group), FadeOut(formula_img),
            run_time=0.8,
        )

        # ── Segment 6: Video = stacked frames along time axis ──
        with self.voiceover(
            text=(
                "And when we stack these still images along the time axis, "
                "we get a video. A three-dimensional block representing "
                "the continuous flow of visual information "
                "in the space T multiple H multiple W multiple 3. "
                "But this very continuity creates an enormous challenge: "
                "How can a computer understand the deep meaning "
                "of millions of constantly changing numbers "
                "without being overwhelmed by noisy details?"
            )
        ) as tracker:
            # Create a series of "frame" rectangles stacked to simulate 3D
            video_block = self._create_video_3d_block()
            video_block.move_to(LEFT * 1.5)

            self.play(FadeIn(video_block, shift=UP * 0.3, run_time=1.2))
            self.wait(1.0)

            # Time axis label
            time_label = Text("Time", font_size=22, color=HIGHLIGHT_YELLOW)
            time_label.next_to(video_block, DOWN + LEFT * 0.5, buff=0.3)
            time_arrow = Arrow(
                start=video_block.get_corner(DL) + DOWN * 0.1,
                end=video_block.get_corner(DL) + DOWN * 0.1 + LEFT * 1.5,
                color=HIGHLIGHT_YELLOW, stroke_width=2, buff=0.1,
            )
            time_label.next_to(time_arrow, DOWN, buff=0.15)

            h_label = Text("H", font_size=20, color=CONTEXT_BLUE)
            w_label = Text("W", font_size=20, color=CONTEXT_BLUE)
            h_brace = Brace(video_block, RIGHT, color=CONTEXT_BLUE, buff=0.1)
            h_label.next_to(h_brace, RIGHT, buff=0.1)
            w_brace = Brace(video_block, UP, color=CONTEXT_BLUE, buff=0.1)
            w_label.next_to(w_brace, UP, buff=0.1)

            self.play(
                Create(time_arrow, run_time=0.8),
                FadeIn(time_label, run_time=0.6),
                FadeIn(h_brace, run_time=0.6), FadeIn(h_label, run_time=0.6),
                FadeIn(w_brace, run_time=0.6), FadeIn(w_label, run_time=0.6),
            )
            self.wait(1.0)

            # Video tensor formula
            formula_video = MathTex(
                r"\text{Video}", r"\in",
                r"\mathbb{R}^{T \times H \times W \times 3}",
                font_size=40, color=SOFT_WHITE
            )
            formula_video.to_edge(RIGHT, buff=1.2)

            annotation = Text(
                "T = frames, H×W = resolution, 3 = RGB",
                font_size=16, color=DIM_GRAY
            ).next_to(formula_video, DOWN, buff=0.3)

            self.play(Write(formula_video, run_time=1.2))
            self.play(FadeIn(annotation, shift=UP * 0.1, run_time=0.8))

            # Question mark to build tension
            self.wait(2.0)
            question = Text("?", font_size=80, color=HIGHLIGHT_YELLOW)
            question.move_to(RIGHT * 3 + UP * 1.5)
            self.play(FadeIn(question, scale=0.5, run_time=0.6))
            self.wait(1.5)

        # ── Cleanup Part 1 ──
        part1_all = VGroup(
            video_block, time_arrow, time_label,
            h_brace, h_label, w_brace, w_label,
            formula_video, annotation, question, grid,
        )
        self.play(FadeOut(part1_all, run_time=1.0))
        self.wait(0.3)

    # ══════════════════════════════════════════════════════════════
    # PART 1.2: Fill in the Blank — Self-Supervised Learning
    # ══════════════════════════════════════════════════════════════
    def part2_fill_in_blank(self):
        # Background grid
        grid = NumberPlane(
            x_range=[-7, 7, 1], y_range=[-4, 4, 1],
            background_line_style={
                "stroke_color": BLUE_E, "stroke_width": 0.5, "stroke_opacity": 0.12,
            },
            axis_config={"stroke_opacity": 0}, faded_line_ratio=0,
        )
        grid.set_z_index(-10)
        self.add(grid)
 
        # ── Segment 1: Video block with masking ──
        with self.voiceover(
            text=(
                "The answer lies in a natural learning mechanism of our brain: Prediction. "
                "If I cover most of this video block, your brain is not confused at all. "
                "You still know which direction the dog is moving, "
                "how the ball will bounce. "
                "You don't need to see every pixel to understand the world. "
                "You only need to grasp the semantics of the motion."
            )
        ) as tracker:
            # Recreate video block
            video_block = self._create_video_3d_block()
            video_block.move_to(LEFT * 2.0)
            self.play(FadeIn(video_block, run_time=0.8))
            self.wait(0.8)

            # Create mask blocks covering ~90% of the video block
            masks = self._create_mask_blocks(video_block)
            self.play(
                FadeIn(masks, run_time=1.2),
            )
            self.wait(1.0)

            # Dashed trajectory curve (prediction)
            trajectory = self._create_trajectory_curve(video_block)
            self.play(Create(trajectory, run_time=1.5))
            self.wait(0.5)

            # Brain icon with "Prediction!" label
            brain_group = self._create_brain_icon()
            brain_group.scale(1.2)
            brain_group.to_edge(RIGHT, buff=1.5)

            self.play(
                FadeIn(brain_group, scale=0.8),
                run_time=1.0,
            )

            pred_label = Text(
                "Prediction!", font_size=32, color=HIGHLIGHT_YELLOW,
                font="sans-serif", weight=BOLD
            ).next_to(brain_group, DOWN, buff=0.3)

            self.play(
                FadeIn(brain_group, scale=0.8, run_time=0.8),
                FadeIn(pred_label, shift=UP * 0.2, run_time=0.8),
            )
            self.wait(2.0)

        # Cleanup
        seg1_group = VGroup(video_block, masks, trajectory, brain_group, pred_label)
        self.play(FadeOut(seg1_group, run_time=0.8))
        self.wait(0.3)

        # ── Segment 2: Self-Supervised Learning concept ──
        with self.voiceover(
            text=(
                "That is exactly the philosophy of Self-Supervised Learning: "
                "learning by filling in the blanks. "
                "This principle has fueled the resounding success "
                "of large language models by predicting missing words."
            )
        ) as tracker:
            # SSL Title
            ssl_title = Text(
                "Self-Supervised Learning",
                font_size=36, color=CONTEXT_BLUE,
                font="sans-serif", weight=BOLD
            ).to_edge(UP, buff=0.8)
            ssl_subtitle = Text(
                "Learning by Filling in the Blanks",
                font_size=24, color=DIM_GRAY
            ).next_to(ssl_title, DOWN, buff=0.2)

            self.play(
                Write(ssl_title, run_time=1.0),
                FadeIn(ssl_subtitle, shift=UP * 0.15, run_time=0.8),
            )
            self.wait(0.5)

            # NLP analogy: sentence with masked word
            sentence_parts = self._create_nlp_mask_demo()
            sentence_parts.move_to(ORIGIN + UP * 0.3)

            self.play(FadeIn(sentence_parts, shift=UP * 0.2, run_time=1.0))
            self.wait(0.5)

            # Animate fill-in
            mask_box = sentence_parts[2]  # The [MASK] element
            filled_word = Text(
                "stick", font_size=28, color=GREEN_CHANNEL,
                font="sans-serif", weight=BOLD
            ).move_to(mask_box.get_center())

            self.play(
                ReplacementTransform(mask_box, filled_word, run_time=1.0),
            )
            self.wait(1.5)

        # ── Segment 3: From NLP to Video ──
        with self.voiceover(
            text=(
                "But how do we apply this principle to video most effectively? "
                "That is when we need V-JEPA."
            )
        ) as tracker:
            # Transition: NLP → Video
            nlp_label = Text("NLP: Predict words", font_size=22, color=DIM_GRAY)
            video_label = Text("Video: Predict regions", font_size=22, color=DIM_GRAY)

            nlp_box = self._create_concept_box("Text", CONTEXT_BLUE, "[MASK]")
            video_box = self._create_concept_box("Video", PREDICTOR_ORANGE, "???")

            comparison = VGroup(
                VGroup(nlp_box, nlp_label.next_to(nlp_box, DOWN, buff=0.2)),
                VGroup(video_box, video_label.next_to(video_box, DOWN, buff=0.2)),
            ).arrange(RIGHT, buff=1.5)
            comparison.move_to(DOWN * 1.0)

            arrow_between = Arrow(
                nlp_box.get_right(), video_box.get_left(),
                color=HIGHLIGHT_YELLOW, stroke_width=2, buff=0.2,
            )

            # Cleanup old NLP demo
            old_parts = VGroup(ssl_title, ssl_subtitle, sentence_parts, filled_word)
            self.play(FadeOut(old_parts, run_time=0.6))

            self.play(
                FadeIn(comparison, shift=UP * 0.2, run_time=1.0),
                Create(arrow_between, run_time=0.8),
            )
            self.wait(1.0)

            # V-JEPA Logo Reveal
            seg3_cleanup = VGroup(comparison, arrow_between)
            self.play(FadeOut(seg3_cleanup, run_time=0.6))

            vjepa_logo = self._create_vjepa_logo()
            vjepa_logo.move_to(ORIGIN)

            self.play(
                FadeIn(vjepa_logo, scale=0.6, run_time=1.2),
            )
            # Glow pulse effect
            self.play(
                vjepa_logo.animate.scale(1.1),
                rate_func=there_and_back,
                run_time=1.0,
            )
            self.wait(1.0)

        # Final cleanup
        final_group = VGroup(vjepa_logo, grid)
        self.play(FadeOut(final_group, run_time=1.0))
        self.wait(0.5)

    # ══════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ══════════════════════════════════════════════════════════════

    def _create_pixel_grid(self, rows=6, cols=8):
        """Create a grid of colored squares with random pixel values."""
        rng = np.random.default_rng(42)
        grid = VGroup()
        for r in range(rows):
            for c in range(cols):
                val = rng.integers(0, 256)
                sq = Square(side_length=0.4, stroke_width=0.5, stroke_color=DIM_GRAY)
                brightness = val / 255.0
                sq.set_fill(
                    color=interpolate_color(BLACK, WHITE, brightness),
                    opacity=0.8,
                )
                num = Integer(val, font_size=10, color=WHITE if brightness < 0.5 else BLACK)
                num.move_to(sq.get_center())
                cell = VGroup(sq, num)
                cell.move_to(np.array([c * 0.42, -r * 0.42, 0]))
                grid.add(cell)
        grid.center()
        return grid

    def _create_channel_grid(self, rows, cols, color, label_text):
        """Create a single color channel grid with label."""
        rng = np.random.default_rng(hash(label_text) % 2**31)
        channel = VGroup()
        for r in range(rows):
            for c in range(cols):
                val = rng.integers(0, 256)
                sq = Square(side_length=0.35, stroke_width=0.5, stroke_color=color)
                brightness = val / 255.0
                sq.set_fill(
                    color=interpolate_color(BLACK, color, brightness),
                    opacity=0.7,
                )
                num = Integer(val, font_size=8, color=WHITE)
                num.move_to(sq.get_center())
                cell = VGroup(sq, num)
                cell.move_to(np.array([c * 0.37, -r * 0.37, 0]))
                channel.add(cell)
        channel.center()

        label = Text(label_text, font_size=18, color=color, weight=BOLD)
        label.next_to(channel, UP, buff=0.15)
        result = VGroup(channel, label)
        return result

    def _create_video_3d_block(self):
        """Create a pseudo-3D video block using stacked rectangles with offset."""
        frames = VGroup()
        num_frames = 8
        for i in range(num_frames):
            rect = Rectangle(
                width=3.0, height=2.0,
                stroke_width=1.0,
                stroke_color=interpolate_color(CONTEXT_BLUE, BLUE_CHANNEL, i / num_frames),
                fill_color=interpolate_color(BG_COLOR, BLUE_E, 0.1 + 0.05 * i),
                fill_opacity=0.6,
            )
            # Offset each frame to create 3D illusion
            offset = np.array([-0.15 * i, 0.1 * i, 0])
            rect.shift(offset)

            # Small frame number
            frame_num = Text(f"t={i}", font_size=12, color=DIM_GRAY)
            frame_num.move_to(rect.get_corner(UL) + RIGHT * 0.3 + DOWN * 0.15)

            frames.add(VGroup(rect, frame_num))

        frames.set_z_index(0)
        return frames

    def _create_mask_blocks(self, video_block):
        """Create gray mask blocks covering ~90% of the video block."""
        masks = VGroup()
        rng = np.random.default_rng(99)
        center = video_block.get_center()

        # Create several overlapping mask rectangles
        for _ in range(6):
            w = rng.uniform(0.8, 2.0)
            h = rng.uniform(0.5, 1.5)
            mask = Rectangle(
                width=w, height=h,
                fill_color=MASK_GRAY, fill_opacity=0.75,
                stroke_width=0.5, stroke_color=MASK_GRAY,
            )
            offset_x = rng.uniform(-1.2, 0.8)
            offset_y = rng.uniform(-0.8, 0.8)
            mask.move_to(center + np.array([offset_x, offset_y, 0]))
            masks.add(mask)

        masks.set_z_index(2)
        return masks

    def _create_trajectory_curve(self, video_block):
        """Create a dashed prediction trajectory curve."""
        center = video_block.get_center()
        points = [
            center + np.array([-1.0, -0.5, 0]),
            center + np.array([-0.3, 0.3, 0]),
            center + np.array([0.5, 0.0, 0]),
            center + np.array([1.2, 0.6, 0]),
        ]
        curve = CubicBezier(*points, color=HIGHLIGHT_YELLOW, stroke_width=2.5)
        dashed = DashedVMobject(curve, num_dashes=20)
        dashed.set_z_index(5)

        # Arrow tip at end
        tip = Triangle(fill_color=HIGHLIGHT_YELLOW, fill_opacity=1, stroke_width=0)
        tip.scale_to_fit_height(0.15)
        tip.move_to(points[-1])
        tip.rotate(
            angle_of_vector(points[-1] - points[-2]),
            about_point=tip.get_center(),
        )
        tip.set_z_index(5)

        return VGroup(dashed, tip)

    def _create_brain_icon(self):
        """Create a simple geometric brain icon."""
        # Main brain shape (two bumpy ellipses)
        left_lobe = Ellipse(width=0.9, height=1.2, color=PREDICTOR_ORANGE, stroke_width=2)
        right_lobe = Ellipse(width=0.9, height=1.2, color=PREDICTOR_ORANGE, stroke_width=2)
        left_lobe.shift(LEFT * 0.25)
        right_lobe.shift(RIGHT * 0.25)

        # Center line
        center_line = Line(
            UP * 0.6, DOWN * 0.6,
            color=PREDICTOR_ORANGE, stroke_width=1.5
        )

        # Neural connection dots
        dots = VGroup()
        for pos in [UL * 0.3, UR * 0.3, DOWN * 0.3, LEFT * 0.4, RIGHT * 0.4]:
            dot = Dot(pos, radius=0.04, color=HIGHLIGHT_YELLOW)
            dots.add(dot)

        # Sparks / emanating lines
        sparks = VGroup()
        for angle in [PI / 6, PI / 3, -PI / 6, -PI / 3, PI * 5 / 6, -PI * 5 / 6]:
            start = np.array([0.6 * np.cos(angle), 0.6 * np.sin(angle), 0])
            end = np.array([0.9 * np.cos(angle), 0.9 * np.sin(angle), 0])
            spark = Line(start, end, color=HIGHLIGHT_YELLOW, stroke_width=1.5)
            sparks.add(spark)

        brain = VGroup(left_lobe, right_lobe, center_line, dots, sparks)
        brain.scale_to_fit_height(1.5)
        return brain

    def _create_nlp_mask_demo(self):
        """Create a NLP mask demonstration sentence."""
        parts = VGroup()

        text_before = Text("The dog is holding a ", font_size=26, color=SOFT_WHITE)
        parts.add(text_before)

        # [MASK] token
        mask_box = VGroup()
        mask_rect = Rectangle(
            width=1.2, height=0.45,
            fill_color=RED_CHANNEL, fill_opacity=0.3,
            stroke_color=RED_CHANNEL, stroke_width=1.5,
        )
        mask_text = Text("[MASK]", font_size=22, color=RED_CHANNEL, weight=BOLD)
        mask_text.move_to(mask_rect.get_center())
        mask_box.add(mask_rect, mask_text)
        parts.add(mask_box)

        text_after = Text(" in its mouth.", font_size=26, color=SOFT_WHITE)
        parts.add(text_after)

        parts.arrange(RIGHT, buff=0.15)
        return parts

    def _create_concept_box(self, title_text, color, content_text):
        """Create a concept box with title and content."""
        box = Rectangle(
            width=2.5, height=1.8,
            stroke_color=color, stroke_width=2,
            fill_color=color, fill_opacity=0.08,
        )
        title = Text(
            title_text, font_size=22, color=color, weight=BOLD
        )
        title.next_to(box.get_top(), DOWN, buff=0.2)

        content = Text(
            content_text, font_size=28, color=SOFT_WHITE,
        )
        content.move_to(box.get_center() + DOWN * 0.1)

        return VGroup(box, title, content)

    def _create_vjepa_logo(self):
        """Create an illuminated V-JEPA logo."""
        logo_text = Text(
            "V-JEPA", font_size=64, color=CONTEXT_BLUE,
            font="sans-serif", weight=BOLD,
        )
        # Glow rectangle behind
        glow = Rectangle(
            width=logo_text.width + 0.8,
            height=logo_text.height + 0.5,
            fill_color=CONTEXT_BLUE, fill_opacity=0.1,
            stroke_color=CONTEXT_BLUE, stroke_width=1,
        )
        glow.move_to(logo_text.get_center())

        subtitle = Text(
            "Video Joint-Embedding Predictive Architecture",
            font_size=20, color=DIM_GRAY,
        )
        subtitle.next_to(logo_text, DOWN, buff=0.3)

        tagline = Text(
            "Predicting the World in Latent Space",
            font_size=16, color=PREDICTOR_ORANGE,
        )
        tagline.next_to(subtitle, DOWN, buff=0.2)

        return VGroup(glow, logo_text, subtitle, tagline)

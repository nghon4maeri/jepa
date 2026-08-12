# Implementation Plan - Chapter 3: Architecture & Tokenization

## Approval Gate

This file is the proposed plan only. Implementation must not begin until this plan is reviewed and approved.

## Source Requirements Read

- Source: `video.md`, paper/
- Chapter: `CHUONG 3: KIEN TRUC BA PHAN VA TOKEN HOA VIDEO`
- Required duration: `7:30 - 12:00`, about 4.5 minutes.
- Required output style: 3Blue1Brown-style Manim, English voiceover, male UK TTS from `visualizations/media/generic_tts.py`, 480p/15fps development render.
- Required Chapter 3 content:
  - Input video block size: `16 x 224 x 224 x 3`.
  - 3D convolution/tubelet embedding with kernel `2 x 16 x 16`.
  - Temporal stride `2`, spatial stride `16`.
  - Feature grid: `8 x 14 x 14 x d`.
  - Flattened token sequence: exactly `1568` tokens.
  - Add `3D sin-cos positional embeddings`.
  - Three neural components:
    - Context Encoder `E_theta`: receives visible/unmasked tokens `x_N`.
    - Target Encoder `E_bar_theta`: receives full token sequence `x_L`; output has red `stop-gradient`.
    - Predictor `P_phi`: receives context representations plus learnable mask tokens `m_M`, predicts missing latent features.

## Scope Correction

Chapter 3 will not re-explain what an image, video, matrix, RGB channel, or tensor means. Those ideas were already introduced in Chapter 1. Chapter 3 will treat `16 x 224 x 224 x 3` as the already-known input format and immediately focus on how V-JEPA tokenizes and routes it through the architecture.

## Target Runtime

- Target final runtime: `4:30` to `4:45`.
- Development render: `420p15` or Manim `-ql` compatible settings.
- No static screen should remain unchanged for more than about 15-18 seconds.
- Each act must end with a grouped `FadeOut(act_group)` or a clean replacement transition before the next act starts.

## Proposed Act Structure

### Act 1 - Chapter Title and Immediate Handoff

- Target duration: 8-10 seconds.
- Purpose: Open Chapter 3 and connect from Chapter 2 without repeating Chapter 1 concepts.
- On-screen content:
  - `3`
  - `Architecture & Tokenization`
  - Small subtitle: `From latent prediction to actual data flow`
- Animation:
  - Fade in chapter number and title.
  - Thin underline draws left-to-right.
  - Three colored dots appear briefly: blue, gray, orange, foreshadowing the three components.
  - Fade out all title objects as one `VGroup`.

### Act 2 - Input Clip as a Working Object, Not a Re-Explanation

- Target duration: 25-30 seconds.
- Purpose: Show the required input size only as the object V-JEPA processes.
- On-screen content:
  - A compact isometric video block labeled `x in R^{16 x 224 x 224 x 3}`.
  - Edge labels: `16 frames`, `224 x 224`, `RGB`.
  - A small tag: `Already raw video tokens? Not yet.`
- Animation:
  - A clean 3D-looking block appears with 16 thin frame slices.
  - Dimension braces/labels slide in.
  - The block pulses once, then compresses slightly toward the center to indicate it is about to be processed.
  - Fade out labels that are no longer needed, keeping only the block for the next act through `ReplacementTransform`.
- Constraint handling:
  - Voiceover will not explain image/video/matrix basics; it will say this is the input already established earlier.

### Act 3 - 3D Convolution Filter Scans the Clip

- Target duration: 45-50 seconds.
- Purpose: Make the tubelet embedding operation concrete.
- On-screen content:
  - Video block on the left.
  - Transparent cuboid filter labeled `2 x 16 x 16`.
  - Stride labels: `temporal stride = 2`, `spatial stride = 16`.
  - Formula: `Conv3D kernel = 2 x 16 x 16`.
- Animation:
  - Filter cuboid appears over the first two frame slices and one spatial patch.
  - Filter sweeps through a few sampled positions, not all 1568 positions.
  - At each sampled stop, a glowing small tubelet cube pops out and moves right.
  - Use `AnimationGroup(..., lag_ratio=0.2)` for sweep -> extract -> move.
  - Accumulate 6-8 representative tubelets only to avoid excessive objects.
  - End with `ReplacementTransform` from extracted tubelets into the first cells of a feature grid.
- Constraint handling:
  - No thousands of mobjects.
  - All filter, highlights, tubelets, and labels are contained in `act3_group`.
  - Fade out transition-specific labels before Act 4.

### Act 4 - Feature Grid: `8 x 14 x 14 x d`

- Target duration: 35-40 seconds.
- Purpose: Show the exact output of Conv3D.
- On-screen content:
  - A 3D grid of small feature cells labeled `8 x 14 x 14 x d`.
  - Three counters:
    - `16 -> 8` along time.
    - `224 -> 14` along height.
    - `224 -> 14` along width.
- Animation:
  - The extracted tubelets morph into a compact 3D lattice.
  - Three dimension counters animate with `DecimalNumber` or prebuilt number labels.
  - Depth `d` is shown as a glowing vector tail behind several cells.
  - Brief ripple of light moves across grid cells to show all positions contain feature vectors.
  - Fade out counters; keep grid for flattening via `ReplacementTransform`.
- Constraint handling:
  - The grid will use a small representative `VGroup`, not 8*14*14 individual cubes.
  - No updater-heavy animations.

### Act 5 - Flatten to 1568 Tokens

- Target duration: 35-40 seconds.
- Purpose: Convert the 3D feature grid into the required token sequence.
- On-screen content:
  - Formula: `8 x 14 x 14 = 1568 tokens`.
  - A horizontal sequence of token beads with ellipsis.
  - Label: `x_L in R^{1568 x d}`.
- Animation:
  - Grid rotates/tilts slightly, then slices peel off row by row.
  - Representative cells stream into a 1D row of token beads.
  - A counter climbs to `1568`.
  - Token row settles into a stable pipeline lane.
  - Fade out old grid remnants; token sequence remains for Act 6.
- Constraint handling:
  - Use 24-32 visible beads plus ellipsis, not 1568 separate dots.

### Act 6 - Add 3D Sin-Cos Positional Embeddings

- Target duration: 35-40 seconds.
- Purpose: Show positional embeddings being added to tokens.
- On-screen content:
  - Token sequence `x_L`.
  - Three wave strips labeled `time`, `height`, `width`.
  - Formula: `token + PE_3D(t,h,w)`.
- Animation:
  - Three sinusoidal wave ribbons flow in from above/below.
  - Small colored phase marks land on token beads.
  - Each token bead gains a thin colored ring indicating spatial-temporal identity.
  - A plus sign and final label `position-aware tokens` appear.
  - Fade out wave strips and formula, keeping final token sequence.
- Constraint handling:
  - Sine waves are prebuilt curves, not updater-generated.

### Act 7 - Split Tokens into Visible and Masked Positions

- Target duration: 30-35 seconds.
- Purpose: Prepare for the three-component architecture without entering Chapter 4 masking details.
- On-screen content:
  - `x_L`: full token sequence.
  - `x_N`: visible tokens, about 10%.
  - `m_M`: learnable mask tokens.
- Animation:
  - Token row duplicates into two lanes.
  - Top lane keeps a sparse blue subset labeled `visible x_N`.
  - Missing positions glow as gray placeholders.
  - Orange learnable mask tokens appear under the missing positions.
  - Fade out explanatory labels; keep three lanes for the architecture diagram.
- Constraint handling:
  - Do not explain how masks are sampled; save that for Chapter 4.

### Act 8 - Three Neural Components

- Target duration: 55-60 seconds.
- Purpose: Fulfill the required architecture diagram.
- On-screen content:
  - Blue Context Encoder `E_theta`.
  - Gray Target Encoder `E_bar_theta`.
  - Orange Predictor `P_phi`.
  - Red `stop-gradient` barrier at Target Encoder output.
- Animation:
  - Visible tokens `x_N` flow into Context Encoder.
  - Full sequence `x_L` flows into Target Encoder.
  - Context output plus orange `m_M` tokens flow into Predictor.
  - Target output creates gray target vectors `s_M`.
  - Predictor output creates orange predicted vectors `s_hat_M`.
  - Red stop-gradient wall appears with a short pulse and blocks backward arrows.
  - All arrows are created once and updated or faded as groups; no arrow recreation loops.
- Constraint handling:
  - Components use established colors from `video.md`.
  - Each component and all arrows are grouped in `architecture_group`.

### Act 9 - Prediction Match in Latent Space

- Target duration: 35-40 seconds.
- Purpose: Show the final learning target of Chapter 3 without going into Chapter 5 loss details.
- On-screen content:
  - Predicted masked features `s_hat_M`.
  - Target masked features `s_M`.
  - Simple comparison: `predict missing latent features`.
- Animation:
  - Orange predicted vectors slide toward gray target vectors.
  - Pairs align with subtle glow when close.
  - A small latent-space panel appears behind them as a geometric coordinate surface.
  - A clean check mark or low-error pulse appears, but no detailed loss formula.
  - Fade out comparison panel and vectors as one group.
- Constraint handling:
  - Avoid Chapter 5 math details like full L1 derivation or EMA theory.

### Act 10 - Full Pipeline Recap and Bridge to Chapter 4

- Target duration: 30-35 seconds.
- Purpose: Recap only the Chapter 3 pipeline and bridge naturally to masking.
- On-screen content:
  - `video clip -> tubelets -> 1568 tokens + PE -> Context/Target/Predictor -> latent prediction`
  - Final question: `Which tokens should be hidden?`
  - Bridge label: `Chapter 4: 3D Multi-Block Masking`.
- Animation:
  - Five compact icons appear in sequence and connect with arrows.
  - A spotlight travels from input to output.
  - The token lane dims except masked slots, setting up Chapter 4.
  - Fade out the entire recap group cleanly.

## Voiceover Plan

- Language: English.
- Style: concise, direct, explanatory.
- Total spoken length: about 4.5 minutes.
- No long introduction explaining what pixels, images, RGB, matrices, or video tensors mean.
- The first line should explicitly continue from prior chapters, for example:
  - "Now that we know why V-JEPA predicts in latent space, let us look at how the video is actually turned into tokens and routed through the model."
- Required terms to include:
  - `tubelet`
  - `3D convolution`
  - `2 by 16 by 16`
  - `temporal stride of 2`
  - `spatial stride of 16`
  - `8 by 14 by 14`
  - `1568 tokens`
  - `3D sin-cos positional embedding`
  - `Context Encoder`
  - `Target Encoder`
  - `Predictor`
  - `stop-gradient`
  - `learnable mask tokens`

## Cleanup and Transition Rules

- Every act will build a main `VGroup`, for example `act3_group`, `act4_group`, etc.
- Before moving to a new conceptual act:
  - Either use `ReplacementTransform` for objects that intentionally persist.
  - Or call one grouped `self.play(FadeOut(act_group), run_time=...)`.
- No old labels, formulas, arrows, or highlights should remain in the next act unless explicitly listed as persistent.
- At major scene changes, use `self.clear()` after fade out only when no object should persist.

## Validation Plan After Approval and Implementation

1. Render a static final-frame preview with `-s` for layout checks.
2. Render development version at `420p15`/`-ql`.
3. Verify output files:
   - `media/videos/chapter3/420p15/Chapter3Scene.mp4`
   - `media/videos/chapter3/420p15/Chapter3Scene.srt`
   - `chapter3_subtitles.srt`
4. Check duration with `ffprobe`; target is `4:30` to `4:45`.
5. Scrub key frames around act transitions to confirm old mobjects are faded out.
6. If needed, make one polish pass for overlapping labels, too-long screens, or missing subtitle timing.

## Out of Scope Until Approval

- No changes to `visualizations/chapter3.py`.
- No render or re-render of Chapter 3.
- No deletion or cleanup of existing Chapter 3 media artifacts.

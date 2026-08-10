# Kế Hoạch Triển Khai Video V-JEPA - Chương 1

## Tổng Quan

Xây dựng video hoạt họa Manim (phong cách 3Blue1Brown) cho **Chương 1** của kịch bản V-JEPA: "Ảnh và Video dưới góc nhìn máy tính & Bài toán điền vào chỗ trống". Video sẽ có **lồng tiếng tiếng Anh** bằng gTTS, render ở **480p15** (`-ql`).

**Thời lượng mục tiêu:** ~4 phút (0:00 – 4:00)

---

## User Review Required

> [!IMPORTANT]
> Video sẽ sử dụng **gTTS** (Google Text-to-Speech) cho voiceover vì đây là giải pháp miễn phí có sẵn. Chất lượng giọng đọc sẽ ở mức cơ bản. Nếu cần chất lượng cao hơn (ElevenLabs, Azure TTS), cần cung cấp API key.

> [!IMPORTANT]
> Ảnh chú chó (dog.png) sẽ được tạo bằng công cụ generate_image để minh họa phần 1.1. Nếu có ảnh sẵn, xin chỉ định đường dẫn.

---

## Cấu Trúc File

```
V-JEPA/
├── visualizations/
│   ├── chapter1.py          # [NEW] Manim scene cho Chương 1
│   └── media/               # Output render tự động
├── media/
│   ├── images/
│   │   └── dog_photo.png    # [NEW] Ảnh minh họa chú chó
│   └── voiceover/           # [NEW] Cache file âm thanh gTTS
```

---

## Proposed Changes

### Phần 1.1: Thế giới thị giác dưới lăng kính toán học (0:00 – 1:00)

#### Scene: `Part1_VisualWorld`

**Voiceover (English):**
> "To understand how an AI algorithm like V-JEPA perceives the world, we must first shed our biological lens. For a computer, an image has no shape or vivid emotion. It is simply a two-dimensional grid of numbers representing the light intensity of three color channels: Red, Green, and Blue — a Tensor of shape H times W times 3.
>
> And when we stack these still images along the time axis, we get a video — a three-dimensional block representing the continuous flow of visual information in the space T times H times W times 3. But this very continuity creates an enormous challenge: How can a computer understand the deep meaning of millions of constantly changing numbers without being overwhelmed by noisy details?"

**Chi tiết Animation (theo timeline):**

| Thời gian | Animation | Mô tả chi tiết | Kỹ thuật Manim |
|-----------|-----------|-----------------|----------------|
| 0:00–0:03 | Nền lưới tọa độ | Lưới tọa độ tối giản xuất hiện mượt mà trên nền đen | `NumberPlane` với opacity thấp (0.15), màu xám nhạt, `FadeIn` |
| 0:03–0:06 | Ảnh chú chó | Ảnh chú chó (ImageMobject) xuất hiện ở trung tâm với hiệu ứng scale-in | `ImageMobject` + `GrowFromCenter` hoặc `FadeIn(scale=0.5)` |
| 0:06–0:10 | Zoom vào pixel | Camera zoom cận cảnh vào vùng mắt chú chó, hiện rõ các ô vuông pixel | Dùng `self.camera.frame.animate.scale(0.3).move_to(eye_region)` với `MovingCameraScene` |
| 0:10–0:15 | Chuyển sang ma trận | Ảnh mờ dần, thay thế bằng grid 2D các ô vuông với số nguyên 0-255 | `FadeOut(image)` + `FadeIn(pixel_grid)`, pixel_grid = `VGroup` các `Square` + `Integer` |
| 0:15–0:22 | Tách 3 kênh RGB | Ma trận tách thành 3 lớp song song (R, G, B) xếp chồng | `AnimationGroup` di chuyển 3 VGroup theo trục z hoặc trục y, mỗi lớp có màu Đỏ/Lục/Lam |
| 0:22–0:28 | Công thức Image Tensor | Công thức $\text{Image} \in \mathbb{R}^{H \times W \times 3}$ xuất hiện bên cạnh | `MathTex` + `Write` animation, đặt `.next_to()` bên phải ma trận |
| 0:28–0:40 | Xoay góc 3D → Video Tensor | Camera xoay perspective, các frame nhân bản kéo dài theo trục "Time" tạo khối hộp 3D | Chuyển sang `ThreeDScene` hoặc dùng perspective transform, tạo `VGroup` các frame lặp lại dọc trục mới, nhãn "Time" |
| 0:40–0:50 | Công thức Video Tensor | Công thức cập nhật: $\text{Video} \in \mathbb{R}^{T \times H \times W \times 3}$ | `TransformMatchingTex` từ công thức cũ sang công thức mới |
| 0:50–1:00 | Chú thích T, H, W, 3 | Các chú thích nhỏ giải thích ý nghĩa từng chiều | `BraceLabel` hoặc `Tex` nhỏ gắn vào từng chiều, `FadeIn` theo `lag_ratio=0.2` |

**Ràng buộc kỹ thuật tuân thủ:**
- Dùng `VGroup` cho tất cả grid/pixel objects
- `FadeIn/FadeOut` thay vì `Create/Write` cho các nhóm lớn
- Gom animation đồng thời vào một `self.play()`
- Giải phóng objects bằng `FadeOut` sau khi hết cần
- `run_time` trong khoảng 0.5s–1.5s
- Tọa độ nằm trong giới hạn khung nhìn (8.0 × 14.22 units)

---

### Phần 1.2: Trực giác thị giác và bài toán "Điền vào chỗ trống" (1:00 – 4:00)

#### Scene: `Part2_FillInTheBlank`

**Voiceover (English):**
> "The answer lies in a natural learning mechanism of our brain: Prediction. If I cover most of this video block, your brain is not confused at all. You still know which direction the dog is moving, how the ball will bounce. You don't need to see every pixel to understand the world — you only need to grasp the 'semantics' of the motion.
>
> That is exactly the philosophy of Self-Supervised Learning — learning by filling in the blanks. This principle has fueled the resounding success of large language models by predicting missing words. But how do we apply this principle to video most effectively? That is when we need V-JEPA."

**Chi tiết Animation (theo timeline):**

| Thời gian | Animation | Mô tả chi tiết | Kỹ thuật Manim |
|-----------|-----------|-----------------|----------------|
| 1:00–1:08 | Khối video 3D chuyển động | Khối hộp video 3D đang chuyển động mượt mà từ scene trước | Giữ nguyên khối 3D, thêm `rate_func=smooth` cho chuyển động oscillating |
| 1:08–1:20 | Khối xám che khuất | Các khối 3D màu xám mờ đè lên, che ~90% thông tin | `VGroup` các `Prism`/`Cube` xám với `opacity=0.7`, `FadeIn` với `lag_ratio=0.15` |
| 1:20–1:35 | Đường cong quỹ đạo | Đường cong vector nét đứt tự vẽ tiếp quỹ đạo chuyển động dựa trên 10% còn lại | `DashedVMobject(CubicBezier(...))` + `Create` animation, màu vàng sáng |
| 1:35–1:45 | Dấu hỏi → Trả lời | Dấu "?" lớn xuất hiện rồi biến thành "Prediction!" | `Tex("?")` → `ReplacementTransform` → `Tex("Prediction!")` |
| 1:45–2:00 | Minh họa não dự đoán | Icon não (đơn giản bằng hình học) với các tia sáng, kết nối tới phần visible | `VGroup` hình elip + đường cong = não đơn giản, `ShowPassingFlash` cho tia sáng |
| 2:00–2:20 | So sánh pixel vs semantic | Chia đôi màn hình: bên trái hiện pixel rời rạc, bên phải hiện vector ngữ nghĩa trừu tượng | `VGroup` trái (dots rối) vs phải (arrows có hướng rõ ràng), `Line` chia đôi |
| 2:20–2:40 | Self-Supervised Learning text | Dòng chữ "Self-Supervised Learning" xuất hiện viết tay, giải thích bằng diagram nhỏ | `Tex` + `Write` animation, kèm sơ đồ: input → [mask] → predict |
| 2:40–3:00 | Analogy NLP | Hiển thị câu văn có từ bị che "[MASK]" → mô hình điền từ | `Tex` với highlight, `Indicate` trên từ bị mask, animation điền từ |
| 3:00–3:20 | Chuyển từ NLP sang Video | Chuyển đổi từ sơ đồ NLP sang sơ đồ Video masking | `ReplacementTransform` từ text blocks sang video cube blocks |
| 3:20–3:40 | V-JEPA Logo reveal | Logo "V-JEPA" xuất hiện phát sáng với subtitle | `Tex("V-JEPA")` + `GlowDot` effect hoặc `Indicate` + `scale` animation |
| 3:40–4:00 | Cleanup & transition | Tất cả objects gom vào VGroup, FadeOut đồng loạt | `self.play(FadeOut(all_objects_group))` |

**Ràng buộc kỹ thuật tuân thủ:**
- Không chiếu 1 screen quá 20 giây → mỗi segment animation ≤ 15-20s
- Dùng `SurroundingRectangle(target, buff=...)` cho box bao quanh text
- Dùng `AnimationGroup(..., lag_ratio=0.2)` cho chuỗi animation nối tiếp
- Set `z_index` rõ ràng: nền < 0, objects chính = 0, highlight > 0
- Cleanup cuối scene bằng 1 lệnh `FadeOut(group)` duy nhất

---

## Chi Tiết Kỹ Thuật Lồng Tiếng

### Cơ chế TTS:
- Sử dụng **`manim-voiceover`** với **`GTTSService`** (Google Text-to-Speech)
- Ngôn ngữ: English (`lang="en"`)
- Scene kế thừa `VoiceoverScene`
- Mỗi đoạn voiceover bọc trong `with self.voiceover(text=...) as tracker:`
- Animation tự đồng bộ thời lượng với voiceover bằng `tracker.duration`

### Cấu trúc code:
```python
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService

class Chapter1Scene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(GTTSService(lang="en"))
        self.part1_visual_world()
        self.part2_fill_in_blank()
    
    def part1_visual_world(self):
        # Animation Part 1.1
        ...
    
    def part2_fill_in_blank(self):
        # Animation Part 1.2
        ...
```

---

## Cấu Hình Render

| Tham số | Giá trị |
|---------|---------|
| Quality flag | `-ql` (480p15) |
| Frame rate | 15 fps |
| Resolution | 854×480 |
| Output format | MP4 |
| Media dir | `--media_dir ./media` |

### Lệnh render:
```bash
cd /Users/mac/Documents/AI/V-JEPA
manim -ql visualizations/chapter1.py Chapter1Scene --media_dir ./media
```

---

## Tổng Quan Màu Sắc (Phong cách 3Blue1Brown)

| Đối tượng | Mã màu | Mô tả |
|-----------|--------|-------|
| Nền | `#1a1a2e` | Nền tối xanh đậm |
| Context Encoder | `#5DADE2` | Xanh dương sáng |
| Predictor | `#E59866` | Cam ấm |
| Target Encoder | `#AAB7B8` | Xám bạc |
| Highlight/Arrows | `#F4D03F` | Vàng sáng |
| Masked regions | `#555555` opacity 0.7 | Xám mờ |
| Text chính | `#FFFFFF` | Trắng |
| Kênh Red | `#E74C3C` | Đỏ |
| Kênh Green | `#2ECC71` | Lục |
| Kênh Blue | `#3498DB` | Lam |

---

## Verification Plan

### Automated Tests
```bash
# 1. Kiểm tra bố cục tĩnh (frame cuối)
manim -ql -s visualizations/chapter1.py Chapter1Scene --media_dir ./media

# 2. Render đầy đủ 480p
manim -ql visualizations/chapter1.py Chapter1Scene --media_dir ./media

# 3. Kiểm tra output file tồn tại
ls -la media/videos/chapter1/480p15/Chapter1Scene.mp4
```

### Manual Verification
- Xem video output để kiểm tra:
  - Voiceover đồng bộ với animation
  - Không có objects chồng chéo
  - Không có screen tĩnh quá 20 giây
  - Công thức toán hiển thị chính xác
  - Transitions mượt mà giữa các phần

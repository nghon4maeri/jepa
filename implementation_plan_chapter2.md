# V-JEPA Video - Chapter 2: Chi tiết từng Act & Animation

Mục tiêu: **12+ act riêng biệt**, thời lượng **≥ 3.6 phút**, đồ họa vector phong phú 3B1B.

---

## PHẦN 2.1: Điểm yếu của Pixel Reconstruction (~1:40)

### Act 1 — Title Card (0:00 - 0:04)
- Số "2" lớn + subtitle "Pixel-Level vs. Latent-Space"
- FadeIn → FadeOut

### Act 2 — Dựng cảnh mặt hồ (0:04 - 0:14)
- Vẽ nền hồ nước (Rectangle gradient xanh)
- Chiếc thuyền (Polygon) trượt vào từ bên trái
- Cây (thân + tán lá tròn) mọc lên ở bên phải
- Sóng nước (FunctionGraph sin) gợn lên dưới thuyền
- **Voice:** "Traditional methods like VideoMAE try to fill in the blanks by reconstructing every masked pixel."

### Act 3 — Overlay lưới pixel (0:14 - 0:24)
- Một lưới ô vuông mỏng phủ lên toàn bộ cảnh (NumberPlane)
- Zoom cận cảnh vào vùng sóng nước: scale lưới + sóng lên to
- Hiện số pixel (0-255) chạy ngẫu nhiên bên trong các ô lưới ở vùng zoom
- **Voice:** "Look at this frame. The lake surface is rippling, leaves are blowing in the wind."

### Act 4 — Mask blocks che khuất (0:24 - 0:34)
- 4-6 khối xám (Rectangle) đè lên các vùng ngẫu nhiên của cảnh
- Nhãn `[MASK]` hiện trên mỗi khối
- Mũi tên nét đứt từ vùng không bị che → vùng bị che, thể hiện "cố gắng đoán"
- **Voice:** "The model must reconstruct what lies beneath these masks."

### Act 5 — VideoMAE cố gắng tái tạo pixel (0:34 - 0:54)
- Các khối mask chuyển dần từ xám sang đỏ nhạt (thể hiện sai số cao)
- Bên trong mask, hiện các pixel nhấp nháy loạn xạ (ô vuông đổi màu liên tục)
- Công thức L2 Loss xuất hiện: $\text{Loss} = \sum ||x_i - \hat{x}_i||^2$
- Một thanh progress bar đỏ "Error" tăng dần lên cao
- **Voice:** "Forcing the model to predict every random ripple is impossible. The pixel loss generates massive noise, wasting resources on low-level details instead of learning the semantic structure."

### Act 6 — Kết luận Pixel: "Thua cuộc" (0:54 - 1:04)
- Dấu ✗ đỏ lớn hiện trên màn hình
- Nhãn "Pixel Reconstruction: Inefficient" FadeIn
- Toàn bộ cảnh pixel nhiễu FadeOut
- **Voice:** "The model gets lost in a sea of chaotic, unpredictable data."

---

## Chuyển cảnh tương phản (1:04 - 1:20)

### Act 7 — So sánh song song (1:04 - 1:20)
- Chia đôi màn hình bằng một đường kẻ dọc
- **Bên trái (đỏ):** Thu nhỏ cảnh pixel chaos + nhãn "VideoMAE"
- **Bên phải (xanh):** Cảnh thuyền sạch sẽ + nhãn "V-JEPA" + mũi tên xanh cho hướng di chuyển
- **Voice:** "While VideoMAE drowns in pixel chaos, V-JEPA chooses a more elegant path: understanding meaning instead of reconstructing noise."

---

## PHẦN 2.2: Latent Space (~2:20)

### Act 8 — Video đi qua Encoder (1:20 - 1:40)
- Toàn bộ cảnh thu nhỏ thành 1 "khung hình video" (viền trắng)
- Một hộp lớn "Encoder $E_\theta$" hiện ở giữa (viền cam, có bánh răng quay nhẹ bên trong)
- Khung hình video trượt từ trái → chui vào Encoder → biến mất
- Ở đầu ra bên phải, một chấm sáng vàng (Dot) nhỏ bay ra
- **Voice:** "V-JEPA passes the video through an Encoder. The complex frame of millions of numbers gets compressed into a single compact feature vector."

### Act 9 — Latent Space bằng Scatter Plot 2D (1:40 - 2:10)
- Dựng hệ tọa độ 2D (Axes) với nhãn trục: "Semantic Dim 1" / "Semantic Dim 2"
- Nhãn "Latent Space" ở trên
- Nhiều chấm tròn (Dot) xuất hiện, mỗi chấm đại diện cho 1 khái niệm:
  - Cụm xanh dương (3-4 chấm): "Boat", "Ship", "Canoe" — gần nhau
  - Cụm xanh lá (3-4 chấm): "Tree", "Forest", "Leaf" — gần nhau
  - Cụm cam (3-4 chấm): "Walking", "Running", "Jumping" — gần nhau
- Các nhãn text nhỏ bên cạnh mỗi cụm
- **Voice:** "In this latent space, concepts with similar meaning naturally cluster together. Boats and ships are close, while trees and forests form their own group. This is the power of learning semantic representations."

### Act 10 — Lọc nhiễu trực quan (2:10 - 2:40)
- Bên cạnh các cụm "sạch", hiện thêm nhiều chấm đỏ nhỏ li ti rải rác (đại diện cho nhiễu: ripple1, ripple2, dust1, dust2...)
- Một vòng tròn lọc (Circle pulse) lan ra từ tâm
- Tất cả chấm đỏ nhỏ bị đẩy ra rìa và FadeOut (bị loại bỏ)
- Chỉ còn lại các cụm ngữ nghĩa lớn, sáng rõ hơn
- **Voice:** "Here, the magic happens. Unpredictable pixel noise is automatically filtered out. Ripple positions, dust particles — they carry no semantic value, so they are discarded."

### Act 11 — Vector ngữ nghĩa thuần khiết (2:40 - 3:10)
- Từ cụm "Boat", 1 mũi tên lớn màu xanh dương vẽ ra, kèm nhãn "Boat is moving right →"
- Mũi tên này glow/pulse (sáng lên rồi tối đi) để nhấn mạnh
- Hiện công thức: $z = E_\theta(x) \in \mathbb{R}^d$ — "Pure semantic embedding"
- Đặt cạnh nhau: Pixel Space (ma trận số hỗn loạn, mờ) vs Latent Space (vector sạch, sáng)
- **Voice:** "What remains is a pure, crystal-clear semantic vector. It carries only the essential message: there is a boat, and it is moving to the right. By predicting in latent space instead of pixel space, V-JEPA eliminates all computational waste."

### Act 12 — Tổng kết & Chuyển tiếp (3:10 - 3:40)
- Hai hộp so sánh cuối cùng:
  - Hộp đỏ: "Pixel Space" + dấu ✗ + "High noise, Low efficiency"
  - Hộp xanh: "Latent Space" + dấu ✓ + "Low noise, High generalization"
- V-JEPA logo (text) hiện giữa màn hình, pulse glow
- FadeOut toàn bộ
- **Voice:** "This is the fundamental philosophical advantage. V-JEPA achieves far greater generalization by learning to understand the world, not merely copy it."

---

## Tổng kết kỹ thuật

| Thuộc tính | Giá trị |
|---|---|
| Số act | 12 |
| Thời lượng dự kiến | ~3:40 (220s) |
| Voice | GenericEdgeTTS(gender="male", accent="uk") |
| Render | `-ql` (480p15) |
| Subtitle | Tự động xuất `.srt` |

> [!IMPORTANT]
> Đây là storyboard chi tiết từng act. Bạn hãy review và cho phản hồi:
> - Có act nào cần thêm/bớt/sửa không?
> - Nội dung latent space (Act 9-11 dùng scatter plot cụm ngữ nghĩa thay vì chỉ vector) đã đủ phong phú chưa?
> - Thời lượng ~3:40 có chấp nhận được không?

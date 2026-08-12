# Ke hoach trien khai Chapter 4 - 3D Multi-Block Masking

## Cong phe duyet

Tai lieu nay chi la ke hoach trien khai. Chua duoc tao `visualizations/chapter4.py`, chua tao loi thoai, chua tong hop giong doc va chua render video.

Chi bat dau hien thuc sau khi ke hoach nay duoc nguoi dung phe duyet ro rang.

## Nguon noi dung da doi chieu

Ke hoach khong chi dua vao kich ban tong quat ma da doi chieu cac nguon sau:

- `video.md`, muc **CHUONG 4: CO CHE CHE KHUAT DA KHOI 3D**.
- `paper/3520_V_JEPA_Latent_Video_Predi.pdf`, paper goc 21 trang.
- `paper/paper_text.md`, cac muc **3D Multi-Block Masking**, **Multi-Mask Prediction** va **Appendix C.3 Masking Strategy**.
- `paper/V_JEPA_Analysis_and_Manim_Plan.md`, phan tong hop masking va goi y truc quan hoa.
- `configs/pretrain/vitl16.yaml`, cau hinh mask dung trong du an.
- `src/masks/multiblock3d.py`, cach lay mau kich thuoc va hop cac block trong ma nguon.

### Cac ket luan bat buoc phai dung theo paper

- Mot mask 2D duoc tao bang cach lay mau nhieu block khong gian lien tuc, co the chong len nhau, sau do lay hop.
- Mask 2D duoc lap tren toan bo truc thoi gian de tao 3D Multi-Block mask.
- `temporal_scale = 1.0`, nghia la moi block che xuyen suot toan bo cac time step.
- Short-range mask: hop cua 8 block, moi block co spatial scale `0.15`.
- Long-range mask: hop cua 2 block, moi block co spatial scale `0.70`.
- Ca hai dung aspect ratio lay mau trong khoang `(0.75, 1.5)`.
- Ty le che trung binh xap xi `90%`; Context Encoder chi xu ly xap xi `10%` token.
- Voi cung mot clip, short-range va long-range duoc dung nhu hai mask rieng.
- Context Encoder va Predictor chay rieng cho tung mask; Target Encoder chi chay mot lan tren clip day du.
- Appendix C.3 cho thay coverage thoi gian thap tao bai toan qua de; che xuyen suot thoi gian va coverage khong gian cao la quan trong.
- Table 15 cho thay 2 mask tren moi sample tot hon 1 mask trong thiet lap ablation (`0.55` so voi `0.50` K400 accuracy); 3 mask khong tang them so voi 2 mask trong bang nay.

### Anh xa Figure/Table cua paper vao Chapter 4

| Nguon trong paper | Noi dung da xac minh | Cach dung trong Chapter 4 |
|---|---|---|
| Figure 2 | Short-range gom 8 block scale `0.15`; long-range gom 2 block scale `0.7`; ca hai lay union va hien tren chuoi frame. | Lam tham chieu hinh hoc cho Act 5 va Act 6, khong sao chep nguyen figure. |
| Figure 3 | Context branch nhan token visible, Predictor nhan them mask token, Target branch nhan full clip. | Bao dam so do Act 7 dung luong du lieu da trinh bay o Chapter 3. |
| Table 5 | `block_aspect_ratio=(0.75,1.5)`, short-range `8/0.15`, long-range `2/0.7` tren cac model pretraining. | Khoa cac tham so hien tren man hinh, khong thay bang so uoc luong. |
| Figure 5 | Ba ablation: masks per sample, blocks per mask va masking ratio. | Dinh huong hai callout ablation ngan o Act 6 va Act 7. |
| Table 13 | Coverage thoi gian va khong gian thap lam bai toan trivial; tai spatial `90%`, cac moc temporal `100/75/50%` cho `0.50/0.22/0.12`. | Bieu do nho trong Act 6. |
| Table 14 | Tai effective spatial masking `75%` va temporal `100%`, 8 block `96x96` dat `0.50`, mot block `192x192` dat `0.47`. | Callout ngan ve loi ich cua nhieu block; khong dung de xep hang short-range va long-range mac dinh. |
| Table 15 | `1/2/3` mask moi sample dat `0.50/0.55/0.55`. | Callout trong Act 7 de giai thich lua chon 2 mask. |
| Figure 6 | Minh hoa cac mask co nhieu block nho den it block lon, cac block co the overlap. | Tham chieu chuyen dong block-union o Act 4 va strip so sanh o Act 6. |

Figure/Table ngoai cac muc tren da duoc doc de hieu mach paper, nhung khong dua vao Chapter 4 neu thuoc ket qua downstream, loss hoac EMA.

## Pham vi Chapter 4

### Noi dung se trinh bay

1. Vi sao mask doc lap tren tung frame lam ro ri thong tin theo thoi gian.
2. Cach lay mau mot block khong gian tu scale va aspect ratio.
3. Cach lay hop nhieu block co the chong lap.
4. Cach keo mask khong gian qua toan bo truc thoi gian.
5. Short-range mask va long-range mask.
6. Cach tinh ty le che va ty le token con nhin thay.
7. Multi-Mask Prediction va phep chia se ket qua Target Encoder.
8. Bang chung ablation ngan gon de giai thich tai sao phai che manh theo ca khong gian va thoi gian.

### Noi dung khong lap lai

- Khong giai thich lai anh, video, pixel, RGB, matrix hay tensor.
- Khong giai thich lai tubelet, 3D convolution, `8 x 14 x 14`, chuoi `1568` token hay ba mang tu dau; Chapter 3 da thuc hien cac noi dung do.
- Khong trinh bay chi tiet ham mat mat `L1`, backpropagation, stop-gradient, EMA hoac representation collapse; day la noi dung Chapter 5.
- Chapter 4 chi dung ky hieu kien truc da co de giai thich luong tinh toan cua multi-mask.

## Muc tieu thoi luong

- Tran tuyet doi: `4:30` = `270 giay`.
- Muc tieu sau render: `4:18-4:24`.
- Ngan sach trong ke hoach: `4:20` = `260 giay`.
- Du phong: `10 giay` cho sai lech TTS, pause va fade chuyen canh.
- Moi act da bao gom thoi gian fade-in, fade-out va khoang nghi can thiet.
- Khong co bo cuc tinh nao duoc giu nguyen qua `20 giay`; trong cac act dai, animation se doi nhip sau moi `6-12 giay`.

| Act | Noi dung | Ngan sach |
|---:|---|---:|
| 1 | Tieu de va ket noi tu Chapter 3 | 9 giay |
| 2 | Temporal leakage voi mask doc lap | 31 giay |
| 3 | Ham lay mau mot spatial block | 38 giay |
| 4 | Union va temporal extrusion | 34 giay |
| 5 | Short-range mask | 39 giay |
| 6 | Long-range, so sanh va ablation | 43 giay |
| 7 | Multi-Mask Prediction | 48 giay |
| 8 | Tong ket va cau noi sang Chapter 5 | 18 giay |
|  | **Tong** | **260 giay (4:20)** |

Thoi luong cuoi se duoc do tu audio TTS va file MP4 thuc te, khong chi uoc luong tu so tu.

## He ky hieu toan hoc

Chapter 4 tiep tuc dung token lattice da co tu Chapter 3:

$$
\Omega = \{0,\ldots,T'-1\}\times\{0,\ldots,H'-1\}\times\{0,\ldots,W'-1\},
$$

voi:

$$
(T',H',W')=(8,14,14),\qquad |\Omega|=8\cdot14\cdot14=1568.
$$

Quy uoc:

- `S`: tap chi so khong gian bi che tren luoi `H' x W'`.
- `M`: tap chi so token khong gian-thoi gian bi che.
- `N = Omega \ M`: tap token con nhin thay.
- `rho`: ty le token bi che.
- `q in {short, long}`: chi so loai mask.

## Cac cong thuc va ham bat buoc hien thi

### 1. Lay mau dien tich va aspect ratio cua mot block

Voi spatial scale `s` va luoi `H' x W'`:

$$
A_b=\left\lfloor sH'W'\right\rfloor,
\qquad r\sim\mathcal{U}(0.75,1.5).
$$

Theo cach hien thuc trong `src/masks/multiblock3d.py`, `r=h_b/w_b` va kich thuoc block la:

$$
h_b=\operatorname{clip}\!\left(\operatorname{round}\sqrt{A_b r},1,H'\right),
$$

$$
w_b=\operatorname{clip}\!\left(\operatorname{round}\sqrt{A_b/r},1,W'\right).
$$

Vi co `round` va `clip`, dien tich block roi rac co the lech nhe so voi `sH'W'`.

### 2. Lay mau vi tri block

$$
u\sim\operatorname{UniformInt}(0,H'-h_b),
\qquad
v\sim\operatorname{UniformInt}(0,W'-w_b).
$$

$$
B(u,v,h_b,w_b)
=\{(h,w):u\le h<u+h_b,\ v\le w<v+w_b\}.
$$

### 3. Lay hop cac block

$$
S=\bigcup_{j=1}^{K}B_j.
$$

Hai cau hinh cu the:

$$
S_{\text{short}}
=\bigcup_{j=1}^{8}B_j
\quad\text{voi}\quad s=0.15,
$$

$$
S_{\text{long}}
=\bigcup_{j=1}^{2}B_j
\quad\text{voi}\quad s=0.70.
$$

Can nhan manh truc quan va loi thoai:

$$
\left|\bigcup_j B_j\right|\ne\sum_j|B_j|
$$

trong truong hop cac block chong lap. Vi vay khong duoc noi `8 x 15% = 120%` hoac `2 x 70% = 140%` la ty le che cuoi.

### 4. Keo mask qua truc thoi gian

$$
M=\{0,\ldots,T'-1\}\times S.
$$

Dang indicator tuong duong:

$$
m(t,h,w)=m_{\text{spatial}}(h,w),
\qquad \forall t\in\{0,\ldots,T'-1\}.
$$

Do `temporal_scale=1.0`:

$$
\rho_t=\frac{T'}{T'}=1=100\%.
$$

### 5. Ty le che va token context

$$
\rho=\frac{|M|}{|\Omega|}
=\frac{T'|S|}{T'H'W'}
=\frac{|S|}{H'W'}\approx0.90.
$$

$$
\frac{|N|}{|\Omega|}=1-\rho\approx0.10,
\qquad |N|\approx157\ \text{token tren trung binh}.
$$

`157` chi la phep lam tron cua `0.10 x 1568`, khong phai so token co dinh cho moi mask ngau nhien.

### 6. Temporal leakage

Minh hoa mot duong tat de du doan token bi che tai thoi diem `t` khi cung vi tri van hien o frame ke ben:

$$
x_{t,h,w}\ \longleftarrow\ \{x_{t-1,h,w},x_{t+1,h,w}\}.
$$

Day la so do phu thuoc truc quan, khong duoc trinh bay nhu cong thuc xac suat chinh thuc cua V-JEPA. Khi mask duoc lap theo thoi gian, ca cot `(t,h,w)` bi che va duong tat nay bien mat.

### 7. Multi-Mask Prediction

Target Encoder xu ly clip day du dung mot lan:

$$
s_L=\operatorname{sg}\!\left(E_{\bar\theta}(x_L)\right).
$$

Voi moi `q in {short, long}`:

$$
z_{N_q}=E_\theta(x_{N_q}),
$$

$$
\hat{s}_{M_q}
=P_\phi\!\left(z_{N_q},\{m+p_i\}_{i\in M_q}\right),
$$

$$
s_{M_q}=\operatorname{Gather}(s_L,M_q).
$$

Chapter 4 chi tao hai cap `(hat{s}_{M_q}, s_{M_q})`. Cong thuc `L1` de danh gia hai cap nay se duoc mo o Chapter 5.

### 8. Mo hinh chi phi tinh toan

Ky hieu chi phi mot lan chay Target, Context va Predictor lan luot la `C_T`, `C_C`, `C_P`.

Neu tinh Target rieng cho tung mask:

$$
C_{\text{naive}}=2(C_T+C_C+C_P).
$$

Voi Multi-Mask Prediction:

$$
C_{\text{multi}}=C_T+2(C_C+C_P).
$$

So lan chay:

| Thanh phan | Cach naive | Multi-mask |
|---|---:|---:|
| Target Encoder | 2 | 1 |
| Context Encoder | 2 | 2 |
| Predictor | 2 | 2 |

Chi duoc ket luan **giam 50% so forward pass cua nhanh Target cho hai mask**. Khong duoc noi tong chi phi huan luyen giam 50%.

## Ke hoach animation theo tung act

### Act 1 - Tieu de va handoff

- **Thoi luong:** 9 giay.
- **Noi dung man hinh:** `Chapter 4`, `3D Multi-Block Masking`, dong phu `Make the prediction task non-trivial`.
- **Animation:** luoi token tu Chapter 3 xuat hien mo; mot mat na 2D phat sang roi keo dai thanh khoi 3D; tieu de vao bang `FadeIn` va `TransformMatchingShapes`.
- **Chuyen canh:** tieu de, luoi va khoi mask duoc `FadeOut` cung luc; man hinh sach truoc Act 2.

### Act 2 - Mask doc lap va temporal leakage

- **Thoi luong:** 31 giay.
- **Noi dung:** ba frame dai dien `t-1`, `t`, `t+1` dung lai motif mat ho va chiec thuyen tu Chapter 2, nhung khong giai thich lai video hay pixel.
- **Animation 1:** cac o bi che xuat hien o vi tri khac nhau tren tung frame.
- **Animation 2:** mot vi tri bi che o frame `t` duoc noi bang mui ten xanh tu cung vung noi dung o `t-1` va `t+1`.
- **Animation 3:** duong tat sang len, nhan `temporal shortcut`; frame `t` duoc noi suy truc quan de cho thay bai toan qua de.
- **Cong thuc tren man hinh:** `x_(t,h,w) <- {x_(t-1,h,w), x_(t+1,h,w)}`.
- **Chuyen canh:** tat mui ten truoc, sau do fade cong thuc, mask va ba frame theo mot `VGroup`; khong de mui ten sot sang act tiep theo.

### Act 3 - Tu scale va aspect ratio den mot spatial block

- **Thoi luong:** 38 giay.
- **Bo cuc:** luoi `14 x 14` ben trai; chuoi cong thuc ben phai, nam hoan toan phia tren subtitle-safe zone.
- **Animation 1:** `s` chuyen tu nhan sang dien tich `A_b=floor(sH'W')`; cac cell dai dien duoc to mau theo dien tich.
- **Animation 2:** thanh aspect-ratio chay trong `[0.75,1.5]`; hinh chu nhat bien doi tu nam ngang, gan vuong sang dung.
- **Animation 3:** `h_b`, `w_b` duoc tinh tu square root; braces bam dung hai canh block.
- **Animation 4:** block truot den vi tri `(u,v)` lay mau ngau nhien, nhung dung seed co dinh de render tai lap.
- **Cong thuc:** `A_b`, `r`, `h_b`, `w_b`, `u`, `v` nhu muc cong thuc bat buoc.
- **Chuyen canh:** cong thuc duoc thu gon thanh mot the `B_j`; cac nhan trung gian fade out; luoi duoc `ReplacementTransform` sang Act 4.

### Act 4 - Union va tao duong ham 3D

- **Thoi luong:** 34 giay.
- **Animation 1:** nhieu block `B_1, B_2, ...` roi xuong luoi; vung chong lap doi mau de chung minh union khong phai tong dien tich.
- **Animation 2:** cong thuc `S = union B_j` bien doi thanh mot mask 2D duy nhat.
- **Animation 3:** xep 8 time slice theo phoi canh; mask 2D duoc sao chep lien tiep qua moi slice.
- **Animation 4:** cac ban sao noi lai thanh nhung `masked tunnels`; camera dich nhe de thay khoi keo dai toan truc `T'`.
- **Cong thuc:** `M={0,...,T'-1} x S`, `rho_t=100%`.
- **Chuyen canh:** camera tro ve goc chinh dien, fade toan bo tunnel va nhan 3D truoc Act 5.

### Act 5 - Short-range mask

- **Thoi luong:** 39 giay.
- **Noi dung:** `K=8`, `s=0.15`, `r ~ U(0.75,1.5)`.
- **Animation 1:** tam block nho duoc dat lan luot voi `LaggedStart`; moi block co aspect ratio khac nhau.
- **Animation 2:** cac block chong lap hoa vao mot union mask; bo dem hien `1/8` den `8/8`.
- **Animation 3:** bo dem coverage cap nhat theo union thuc, khong cong don `15%` mot cach sai.
- **Animation 4:** mask 2D keo thanh cac tunnel hep, phan context con lai phat sang xanh.
- **Thong diep:** short-range tao nhieu khoang khuyet cuc bo, buoc context lien ket chi tiet o nhieu vung.
- **Chuyen canh:** tat bo dem va chu giai, sau do fade mask; giu lai khung so sanh rong bang `ReplacementTransform` cho Act 6.

### Act 6 - Long-range, so sanh va bang chung ablation

- **Thoi luong:** 43 giay.
- **Bo cuc:** short-range ben trai, long-range ben phai; moi ben la mot luoi rieng, khong dung card long nhau.
- **Animation 1:** hai block lon `s=0.70` mo rong tren luoi long-range, co vung chong lap ro rang.
- **Animation 2:** hai mask duoc chuan hoa ve cung kich thuoc; nhan `8 x 0.15` va `2 x 0.70` vao dong thoi.
- **Animation 3:** dong cong thuc `rho=|S|/(H'W') approx 0.90` xuat hien; thanh context thu lai con `approx 10%`.
- **Animation 4:** strip theo Figure 6/Table 14 chuyen nhanh tu nhieu block nho sang mot block lon; callout tai effective spatial coverage `75%`, temporal `100%`: `8 x 96x96 -> 0.50`, `1 x 192x192 -> 0.47`.
- **Animation 5:** mot bieu do ablation nho tai spatial coverage `90%`: temporal coverage `100%`, `75%`, `50%` lan luot dat `0.50`, `0.22`, `0.12` K400 accuracy trong Table 13; nhan ket luan `low coverage -> trivial task`.
- **Thong diep:** short-range va long-range la hai nhiem vu bo tro, khong gan cung nhac `local`/`global` nhu mot dinh ly ma paper khong chung minh truc tiep.
- **Chuyen canh:** fade bieu do, sau do fade ca hai mask va cong thuc; man hinh sach truoc so do mang.

### Act 7 - Multi-Mask Prediction

- **Thoi luong:** 48 giay.
- **Bo cuc:** clip day du va Target Encoder o lan tren; hai nhanh short/long song song o ben duoi. Vung day `15-18%` de trong cho phu de.
- **Animation 1:** clip day du vao `E_bar_theta` dung mot lan; ket qua `s_L` duoc cache truc quan bang mot hang vector mau xam.
- **Animation 2:** cung clip tach thanh `N_short` va `N_long`; moi nhanh vao mot lan Context Encoder va Predictor.
- **Animation 3:** hai lenh `Gather(s_L,M_q)` tach target chung thanh `s_M_short` va `s_M_long`.
- **Animation 4:** `hat{s}_M_short` va `hat{s}_M_long` can cap voi target tuong ung.
- **Animation 5:** bang dem forward pass chuyen tu `(Target, Context, Predictor)=(2,2,2)` sang `(1,2,2)`.
- **Bang chung ngan:** callout tu Table 15 hien `1 mask: 0.50`, `2 masks: 0.55`, `3 masks: 0.55`, roi nhan manh thiet lap mac dinh 2 mask tao hai tac vu bo tro ma khong tang Target pass.
- **Cong thuc:** ba dong multi-mask va hai cong thuc chi phi `C_naive`, `C_multi`.
- **Mui ten:** dau mui ten phai cham dung canh box dich; Target di tu clip den encoder roi den `s_L`; moi nhanh Context di tu mask den Context Encoder, sau do toi Predictor; `Gather` di tu `s_L` xuong dung cap target. Khong co mui ten nguoc hoac giao nhau voi nhan.
- **Chuyen canh:** mui ten va flow particle fade truoc; sau do box, vector va cong thuc fade theo nhom.

### Act 8 - Tong ket va cau noi

- **Thoi luong:** 18 giay.
- **Animation:** ba bieu tuong lan luot vao: `spatial union`, `100% temporal extrusion`, `shared target`; mot net sang ket noi chung thanh chuoi.
- **Noi dung:** `~90% masked`, `~10% context`, `1 shared target pass`.
- **Cau ket:** ket qua du doan va target da san sang; Chapter 5 se dinh nghia cach so sanh chung va cap nhat cac encoder.
- **Chuyen canh:** moi doi tuong trong `act8_group` fade out hoan toan, ket thuc tren nen sach.

## Cac ham du kien trong `chapter4.py`

Danh sach nay dinh nghia ranh gioi trien khai, chua phai ma nguon:

| Ham | Trach nhiem |
|---|---|
| `build_token_grid(rows=14, cols=14)` | Tao luoi dai dien co so cell vua du cho 480p. |
| `sample_block_shape(scale, aspect_ratio, rows, cols)` | Tinh `(h_b,w_b)` dung cong thuc va cach clamp cua ma nguon V-JEPA. |
| `sample_block_position(h_b, w_b, rows, cols, rng)` | Lay `(u,v)` tai lap bang random seed co dinh. |
| `build_spatial_block(grid, u, v, h_b, w_b, color)` | Tao block va highlight cac cell lien tuc. |
| `build_union_mask(blocks)` | Tao union logic va coverage counter; xu ly vung chong lap mot lan. |
| `extrude_mask_through_time(mask_2d, depth=8)` | Lap mask 2D qua 8 time step va tao phoi canh tunnel. |
| `build_leakage_triptych()` | Tao ba frame va cac duong temporal shortcut cho Act 2. |
| `build_mask_comparison()` | Tao bo cuc short-range/long-range dong kich thuoc. |
| `build_ablation_callouts()` | Tao strip/bieu do toi gian tu Table 13, 14 va 15, voi du lieu precompute. |
| `build_multi_mask_pipeline()` | Tao flow dung huong va chia se `s_L` cho hai mask. |
| `fade_act(group)` | Fade out tron nhom, don updater va remove cac mobject da het vong doi. |

### Nguyen tac hien thuc ham

- Khong tao `14 x 14 x 8` Cube 3D nang neu khong can; dung luoi 2D, layer dai dien va `VGroup` de giu hieu nang.
- Precompute block indices, union coverage va du lieu ablation truoc animation.
- Khong tao `MathTex` trong updater.
- Khong lam phep hop tap hop hay doc file trong updater.
- Khong lam dung `always_redraw`; mui ten dong chi dung updater nhe khi box thuc su di chuyen, sau do phai `clear_updaters()`.
- Dung `ReplacementTransform` hoac `TransformMatchingShapes` cho doi tuong can tiep tuc qua hai act.
- Tat ca object cua moi act nam trong mot `VGroup` quan ly vong doi.

## Ke hoach loi thoai va phu de real-time

- Ngon ngu loi thoai: English.
- Giong doc: Male UK qua `visualizations/media/generic_tts.py`.
- Loi thoai du kien: khoang `500-560` tu; se do thoi luong audio that truoc khi render.
- Cau van ngan, cong thuc duoc doc theo tung buoc thay vi doc mot khoi ky hieu dai.
- Khong doc lai dinh nghia co ban ve video, matrix hay tokenization.
- Khong noi qua muc paper, dac biet khong bien dien giai short-range/local va long-range/global thanh ket luan dinh luong.

### Quy tac phu de

- Dung timing `WordBoundary` thuc tu TTS, khong chia deu theo do dai doan van.
- Voice den dau, phu de hien den do; khong hien ca doan loi thoai cung luc.
- Toi da 2 dong moi cue.
- Toi da 42 ky tu moi dong, uu tien ngat theo menh de.
- Cac cue khong duoc chong thoi gian; co khoang an toan nho giua hai cue neu timing cho phep.
- Danh rieng `15-18%` phia duoi khung hinh lam subtitle-safe zone.
- Khong dat cong thuc, nhan truc, coverage counter, box mang hoac dau mui ten trong vung phu de.
- Neu player/dat subtitle che noi dung trong ban xem thu, uu tien doi noi dung len tren hoac chuyen phu de sang khoang trong, khong chap nhan che lap.
- Xuat ca file phu de di kem va subtitle track trong MP4 theo quy trinh dang dung o Chapter 3.

## Bo cuc va mau sac

- Nen toi, phong cach vector 3Blue1Brown nhu `video.md`.
- Context/visible token: xanh duong sang.
- Predictor/prediction: cam am.
- Target/shared representation: xam bac.
- Mask short-range: vang/cam de phan biet voi context.
- Mask long-range: do hong nhat, khong trung mau dau mui ten leakage.
- Leakage shortcut: xanh la sang; bi tat hoan toan truoc khi chuyen sang giai phap.
- Cong thuc chinh: trang; tham so dang duoc noi den se doi mau dong bo voi animation.
- Moi man hinh dung `arrange`, `next_to`, braces va `SurroundingRectangle`; han che toa do tuyet doi.
- Moi cong thuc duoc gioi han chieu rong truoc khi vao canh; khong de vuot khung `14.22 x 8.0`.

## Quy tac chuyen act

- Moi act co `act_group` rieng.
- Object khong tiep tuc sang act sau phai duoc fade out truoc khi voiceover sang y moi.
- Mui ten, flow particle, nhan highlight va updater phai bien mat truoc box nen.
- Chi giu object qua act khi ke hoach ghi ro `ReplacementTransform`.
- Sau moi chuyen canh lon, kiem tra `self.mobjects` de khong con object mo hoac object nam ngoai khung.
- Man hinh cuoi moi act phai ro rang, khong chong lop voi man hinh dau act ke tiep.

## Ke hoach kiem thu sau khi duoc phe duyet

1. Kiem tra import/compile cua `chapter4.py`.
2. Render anh tinh bang `-s` de kiem tra bo cuc cuoi va cac cong thuc dai.
3. Render phat trien bang `-ql` o `480p15` co long tieng.
4. Dung `ffprobe` xac nhan MP4 co H.264, audio AAC va thoi luong `<=270.0 giay`.
5. Xac nhan audio TTS khong bi cat o dau/cuoi va khong co khoang im lang bat thuong.
6. Kiem tra SRT: timing tang dan, khong overlap, toi da 2 dong, toi da 42 ky tu moi dong.
7. Tao contact sheet tai cac moc dau/giua/cuoi cua 8 act de tim chong lap va object con sot.
8. Kiem tra rieng Act 2: mui ten leakage chi dung vi tri qua ba frame.
9. Kiem tra rieng Act 7: moi mui ten cham dung box, dung chieu va khong cat qua cong thuc/nhan.
10. Kiem tra subtitle-safe zone tren cac frame co nhieu cong thuc nhat: Act 3, 6 va 7.
11. Kiem tra coverage counter duoc tinh tu union thuc, khong tu tong dien tich block.
12. Kiem tra cac tham so tren video khop paper va config: `8`, `0.15`, `2`, `0.70`, `(0.75,1.5)`, `100% temporal`, `~90% masked`, `~10% visible`.
13. Do thoi luong cuoi; neu vuot `4:30`, rut gon loi thoai/pause ma khong bo bat ky noi dung bat buoc nao.

## Tieu chi chap nhan Chapter 4

- Video khong vuot `4 phut 30 giay`.
- Noi dung khop paper goc, Appendix C.3, config va cach tinh block trong ma nguon.
- Tat ca cong thuc lay mau, union, temporal extrusion, masking ratio va multi-mask compute deu xuat hien ro rang.
- Short-range va long-range hien dung tham so va duoc minh hoa bang cac block co chong lap.
- Temporal leakage va cach chan leakage duoc the hien bang chuyen dong, khong chi bang chu.
- Moi act co animation da dang va moi act cu duoc fade out sach truoc act moi.
- Phu de bam timing voice theo WordBoundary va khong che noi dung.
- Act 7 co mui ten dung huong, dung diem dau/cuoi va so lan forward chinh xac `1 Target + 2 Context + 2 Predictor`.
- Khong lap lai noi dung nen tang da giai thich o Chapter 1 va Chapter 3.
- Khong lan sang chi tiet ham mat mat va EMA cua Chapter 5.

## Ngoai pham vi truoc khi duyet

- Khong tao hoac sua `visualizations/chapter4.py`.
- Khong tao voiceover Chapter 4.
- Khong tao `chapter4_subtitles.srt`.
- Khong render preview hay MP4 Chapter 4.
- Khong sua bat ky chapter hoac media hien co nao.

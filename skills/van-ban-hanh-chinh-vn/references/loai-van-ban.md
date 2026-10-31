# 29 loại văn bản hành chính và chữ viết tắt

Danh mục loại: **Điều 7** Nghị định 30/2020/NĐ-CP. Bảng chữ viết tắt tên loại:
**Mục I Phụ lục III** cùng Nghị định. Mẫu trình bày: Phụ lục III.

## Mục lục

- [Bảng tra cứu](#bảng-tra-cứu)
- [Thành phần bắt buộc theo họ bố cục](#thành-phần-bắt-buộc-theo-họ-bố-cục)
- [Ghi chú từng loại](#ghi-chú-từng-loại)
- [Bản sao văn bản](#bản-sao-văn-bản)

## Bảng tra cứu

`loai` là giá trị đưa vào `spec.json`.

| # | Tên loại | `loai` | Viết tắt | Mẫu | Họ bố cục |
| --- | --- | --- | --- | --- | --- |
| 1 | Nghị quyết (cá biệt) | `nghi-quyet` | `NQ` | 1.1 | nghị quyết |
| 2 | Quyết định (cá biệt) | `quyet-dinh` | `QĐ` | 1.2 / 1.3 | quyết định |
| 3 | Chỉ thị | `chi-thi` | `CT` | 1.4 | có tên loại |
| 4 | Quy chế | `quy-che` | `QC` | 1.4 | có tên loại |
| 5 | Quy định | `quy-dinh` | `QyĐ` | 1.4 | có tên loại |
| 6 | Thông cáo | `thong-cao` | `TC` | 1.4 | có tên loại |
| 7 | Thông báo | `thong-bao` | `TB` | 1.4 | có tên loại |
| 8 | Hướng dẫn | `huong-dan` | `HD` | 1.4 | có tên loại |
| 9 | Chương trình | `chuong-trinh` | `CTr` | 1.4 | có tên loại |
| 10 | Kế hoạch | `ke-hoach` | `KH` | 1.4 | có tên loại |
| 11 | Phương án | `phuong-an` | `PA` | 1.4 | có tên loại |
| 12 | Đề án | `de-an` | `ĐA` | 1.4 | có tên loại |
| 13 | Dự án | `du-an` | `DA` | 1.4 | có tên loại |
| 14 | Báo cáo | `bao-cao` | `BC` | 1.4 | có tên loại + Kính gửi |
| 15 | Biên bản | `bien-ban` | `BB` | 1.9 | biên bản |
| 16 | Tờ trình | `to-trinh` | `TTr` | 1.4 | có tên loại + Kính gửi |
| 17 | Hợp đồng | `hop-dong` | `HĐ` | 1.4 | có tên loại |
| 18 | Công văn | `cong-van` | *(không có)* | 1.5 | công văn |
| 19 | Công điện | `cong-dien` | `CĐ` | 1.6 | công điện |
| 20 | Bản ghi nhớ | `ban-ghi-nho` | `BGN` | 1.4 | có tên loại |
| 21 | Bản thỏa thuận | `ban-thoa-thuan` | `BTT` | 1.4 | có tên loại |
| 22 | Giấy ủy quyền | `giay-uy-quyen` | `GUQ` | 1.4 | có tên loại |
| 23 | Giấy mời | `giay-moi` | `GM` | 1.7 | biểu mẫu |
| 24 | Giấy giới thiệu | `giay-gioi-thieu` | `GGT` | 1.8 | biểu mẫu |
| 25 | Giấy nghỉ phép | `giay-nghi-phep` | `GNP` | 1.10 | biểu mẫu |
| 26 | Phiếu gửi | `phieu-gui` | `PG` | 1.4 | có tên loại |
| 27 | Phiếu chuyển | `phieu-chuyen` | `PC` | 1.4 | có tên loại |
| 28 | Phiếu báo | `phieu-bao` | `PB` | 1.4 | có tên loại |
| 29 | Thư công | `thu-cong` | *(không có)* | 1.5 | công văn |

> Nghị định 30/2020 đã **bỏ** bản cam kết, giấy chứng nhận, giấy đi đường, giấy
> biên nhận hồ sơ so với Nghị định 09/2010, và **bổ sung** phiếu báo. Những loại đã
> bỏ không còn là văn bản hành chính theo Điều 7.

## Thành phần bắt buộc theo họ bố cục

| Thành phần | công văn | có tên loại | quyết định / nghị quyết | biên bản | biểu mẫu | công điện |
| --- | --- | --- | --- | --- | --- | --- |
| Tên loại (ô 5a) | **không** | có | có | có | có | có |
| Trích yếu | sau `V/v` (ô 5b) | dưới tên loại | dưới tên loại | dưới tên loại | dưới tên loại | dưới tên loại |
| Căn cứ (`can_cu`) | không | khi cần | **có** | không | không | không |
| Kính gửi (ô 9a) | **có** | chỉ Tờ trình, Báo cáo gửi cấp trên | không | không | không (ghi trong thân) | có |
| Điều, khoản (`dieu`) | không | khi cần | **có** | không | không | không |
| Nơi nhận (ô 9b) | có | có | có | **không** | có | có |
| Khối chữ ký | 1 người | 1 người | 1 người | **2 cột** (`chu_ky`) | 1 người | 1 người |

## Ghi chú từng loại

- **Công văn** (`cong-van`): không có tên loại; trích yếu đặt sau `V/v`; ký hiệu là
  `<viết tắt cơ quan>-<viết tắt đơn vị soạn thảo>`, **không** chứa `CV`. Dòng đầu
  Nơi nhận là `Như trên`.
- **Thư công** (`thu-cong`): trình bày như công văn, dùng cho thư của người đứng đầu
  gửi cá nhân, tổ chức. Thường không có ký hiệu tên loại.
- **Quyết định** (`quyet-dinh`): Mẫu 1.2 quy định trực tiếp (nội dung nằm trong các
  Điều) và Mẫu 1.3 quy định gián tiếp (ban hành kèm theo quy chế, quy định, danh
  sách...). Phần căn cứ in nghiêng, sau đó là dòng `QUYẾT ĐỊNH:` canh giữa in hoa
  đậm, rồi đến `Điều 1.`, `Điều 2.`... Điều cuối cùng luôn nói về hiệu lực và trách
  nhiệm thi hành.
- **Nghị quyết** (`nghi-quyet`): giống quyết định nhưng dòng chuyển tiếp là
  `QUYẾT NGHỊ:` và người ký thường dùng quyền hạn `TM.` (ký thay mặt tập thể).
- **Báo cáo** và **Tờ trình** (`bao-cao`, `to-trinh`): khi cấp dưới gửi cấp trên thì
  **có** `Kính gửi` (ô 9a) và dòng đầu Nơi nhận là `Như trên`; báo cáo nội bộ lưu
  hành ngang cấp thì bỏ `Kính gửi`.
- **Biên bản** (`bien-ban`): mở đầu ghi thời gian, địa điểm, thành phần tham dự;
  kết thúc ghi giờ kết thúc, số bản, việc đã đọc lại và thông qua. **Không có Nơi
  nhận**; khối ký là hai cột (thư ký bên trái, chủ tọa bên phải) qua trường
  `chu_ky`.
- **Giấy mời** (`giay-moi`): người được mời ghi trong thân bài sau `trân trọng kính
  mời:`, không dùng `Kính gửi`. Các dòng `Ông/Bà`, `Tới dự`, `Thời gian`, `Địa điểm`
  dùng block `dots`.
- **Giấy giới thiệu** (`giay-gioi-thieu`): không có trích yếu. Kết thúc bằng dòng
  nghiêng ghi thời hạn giá trị của giấy.
- **Giấy nghỉ phép** (`giay-nghi-phep`): không có trích yếu, không có Nơi nhận; có
  phần xác nhận của cơ quan nơi nghỉ phép ở cuối.
- **Công điện** (`cong-dien`): thường kèm dấu mức độ khẩn (`do_khan`), nội dung ngắn,
  đánh số thứ tự yêu cầu 1, 2, 3.
- **Hợp đồng** (`hop-dong`): khối ký hai cột giống biên bản; dùng `chu_ky`.

## Bản sao văn bản

Nghị định quy định ba hình thức bản sao, ký hiệu theo Mục I Phụ lục III. Skill này
**không** sinh bản sao; phần dưới chỉ để tra cứu.

| Tên loại bản sao | Viết tắt |
| --- | --- |
| Bản sao y | `SY` |
| Bản trích sao | `TrS` |
| Bản sao lục | `SL` |

Thể thức bản sao (Phần II Phụ lục I): các thành phần được trình bày **trên cùng tờ
giấy A4, ngay sau phần cuối của văn bản cần sao, dưới một đường kẻ nét liền kéo dài
hết chiều ngang vùng trình bày**; các cụm từ `SAO Y`, `SAO LỤC`, `TRÍCH SAO` in hoa,
cỡ 13 - 14, đứng, đậm.

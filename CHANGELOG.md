# Changelog

Phiên bản theo [Semantic Versioning](https://semver.org/lang/vi/).

## [1.0.0] - 2026-10-31

Bản phát hành đầu tiên ra công chúng. Tổng quát hóa từ một skill chỉ sinh công văn
thành bộ công cụ cho toàn bộ văn bản hành chính.

### Added

- **Đủ 29 loại văn bản hành chính** tại Điều 7 Nghị định 30/2020/NĐ-CP, kèm chữ viết
  tắt chính thức theo Mục I Phụ lục III.
- **Sáu họ bố cục**: công văn, văn bản có tên loại, quyết định / nghị quyết (căn cứ,
  `QUYẾT ĐỊNH:`, các `Điều`), biên bản (hai cột chữ ký, không Nơi nhận), biểu mẫu
  (giấy mời, giấy giới thiệu, giấy nghỉ phép), công điện.
- **`scripts/kiem_tra.py`** - trình kiểm tra thể thức, hơn 40 quy tắc, mỗi thông báo
  dẫn chiếu khoản điểm tương ứng. Không phụ thuộc thư viện ngoài.
- **Thành phần thể thức khác**: dấu chỉ độ mật, dấu mức độ khẩn, chỉ dẫn phạm vi lưu
  hành, ký hiệu người soạn thảo, chân trang địa chỉ - điện thoại - email, số trang
  canh giữa lề trên và ẩn ở trang đầu.
- **Phụ lục** nhiều tệp, tự đánh số La Mã, tự dựng dòng `(Kèm theo ... số ... ngày ...)`.
- Khối block mới: `heading`, `dots` (dòng chấm điền tay), `center`, `italic`,
  `signatures`, `pagebreak`; bảng có `widths`.
- Tự định dạng ngày tháng theo II.4.b và tự thêm số 0 cho số văn bản theo II.3.c.
- Mười ví dụ chạy được ngay trong `assets/`, mỗi họ bố cục một tệp.
- Ba tài liệu tham chiếu: thể thức theo khoản điểm, danh mục loại văn bản, lược đồ JSON.
- Bộ kiểm thử `tests/` và quy trình CI trên Python 3.11, 3.12, 3.13.
- Cài đặt dạng plugin qua `.claude-plugin/marketplace.json`.

### Fixed

- `Kính gửi` không còn in đậm - II.9.d quy định in thường, kiểu đứng.
- Số và ký hiệu nay nằm **cùng dòng** với địa danh và ngày tháng, đúng II.4.c.
- Đường kẻ dưới tên cơ quan và dưới trích yếu rút về **1/3 - 1/2** độ dài dòng chữ
  theo II.2.b và II.5.b, thay vì kéo hết chiều ngang.
- Nơi nhận tự thêm dấu chấm phẩy cuối mỗi dòng và dấu chấm ở dòng cuối (II.9.d).
- Cỡ chữ các thành phần bám đúng quy định: Quốc hiệu 12, Tiêu ngữ 13, tên cơ quan 12,
  `Nơi nhận:` 12 nghiêng đậm, danh sách nơi nhận 11.

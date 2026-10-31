# Lược đồ `spec.json`

Toàn bộ trường của tệp mô tả đưa vào `scripts/tao_vanban.py`. Mọi trường đều không
bắt buộc trừ khi ghi **bắt buộc**. Khóa viết sai chính tả sẽ bị `scripts/kiem_tra.py`
báo là `CANH BAO ... khoa khong duoc dung den`.

## Mục lục

- [Thứ tự trình bày](#thứ-tự-trình-bày)
- [Khối đầu văn bản](#khối-đầu-văn-bản)
- [Tên loại, trích yếu, căn cứ, kính gửi](#tên-loại-trích-yếu-căn-cứ-kính-gửi)
- [Nội dung](#nội-dung)
- [Các loại block](#các-loại-block)
- [Khối cuối: nơi nhận và chữ ký](#khối-cuối-nơi-nhận-và-chữ-ký)
- [Phụ lục](#phụ-lục)
- [Thành phần tùy chọn](#thành-phần-tùy-chọn)
- [Ví dụ đầy đủ](#ví-dụ-đầy-đủ)

## Thứ tự trình bày

Script luôn xuất theo trình tự sau, bất kể thứ tự khóa trong JSON:

```
pham_vi_luu_hanh → do_mat → do_khan
khối đầu (co_quan_chu_quan, co_quan, so/ky_hieu, dia_danh/ngay, V/v)
ten_loai + trich_yeu
can_cu
kinh_gui
mo_dau
"QUYẾT ĐỊNH:" / "QUYẾT NGHỊ:"   (chỉ khi loai là quyet-dinh / nghi-quyet và có can_cu)
dieu[]
muc[]
noi_dung[]
ket
noi_nhan + ky_hieu_nguoi_soan  |  nguoi_ky   (hoặc chu_ky[])
phu_luc[]
```

## Khối đầu văn bản

| Trường | Kiểu | Ý nghĩa |
| --- | --- | --- |
| `loai` | chuỗi | **Bắt buộc.** Một trong 29 khóa ở [loai-van-ban.md](loai-van-ban.md). |
| `co_quan` | chuỗi | **Bắt buộc.** Tên cơ quan ban hành. Script tự in hoa. |
| `co_quan_chu_quan` | chuỗi | Cơ quan chủ quản trực tiếp, in hoa, không đậm, không gạch chân. |
| `so` | chuỗi/số | Số văn bản. Để trống `""` để chừa chỗ Văn thư điền. Số 1 chữ số được tự thêm `0`. |
| `ky_hieu` | chuỗi | Ký hiệu, ví dụ `QĐ-MV` hoặc `MV-HCNS`. |
| `viet_tat_co_quan` | chuỗi | Nếu khai, script tự ghép `<viết tắt loại>-<giá trị này>` khi `ky_hieu` trống. |
| `dia_danh` | chuỗi | **Bắt buộc** (nếu không dùng `dia_danh_ngay`). Ví dụ `Hà Nội`. |
| `ngay` | chuỗi | **Bắt buộc** (nếu không dùng `dia_danh_ngay`). `YYYY-MM-DD` hoặc `DD/MM/YYYY`; script tự viết thành `ngày 09 tháng 3 năm 2026`. |
| `dia_danh_ngay` | chuỗi | Ghi đè cả dòng địa danh - ngày khi cần định dạng đặc biệt. |
| `co_chu` | 13 hoặc 14 | Cỡ chữ thân bài. Mặc định 13. |
| `so_trang` | boolean | Đánh số trang từ trang 2. Mặc định `true`. |

## Tên loại, trích yếu, căn cứ, kính gửi

| Trường | Kiểu | Ý nghĩa |
| --- | --- | --- |
| `ten_loai` | chuỗi | Ghi đè tên loại mặc định. **Không khai cho công văn** - script sẽ báo lỗi. |
| `trich_yeu` | chuỗi hoặc mảng chuỗi | Công văn: in sau `V/v` (mảng = nhiều dòng). Loại khác: canh giữa dưới tên loại, kèm đường kẻ ngang. |
| `can_cu` | chuỗi hoặc mảng | Căn cứ pháp lý, in nghiêng. Script tự thêm `;` cuối mỗi dòng và `.` ở dòng cuối - **đừng tự thêm**. |
| `tu_quyet_dinh` | chuỗi | Ghi đè dòng `QUYẾT ĐỊNH:` / `QUYẾT NGHỊ:`. |
| `kinh_gui` | chuỗi hoặc mảng | Nơi nhận trực tiếp. Một phần tử = cùng dòng với `Kính gửi:`; nhiều phần tử = mỗi dòng một nơi, script tự thêm `-`, `;`, `.`. |

## Nội dung

Ba cách khai, dùng được đồng thời:

| Trường | Kiểu | Dùng khi |
| --- | --- | --- |
| `mo_dau` | chuỗi hoặc mảng | Đoạn dẫn nhập, căn đều, thụt dòng đầu. |
| `dieu` | mảng `{heading, blocks}` | Quyết định, nghị quyết. `heading` dạng `Điều 1. Tiêu đề`. |
| `muc` | mảng `{heading, blocks}` | Báo cáo, kế hoạch, tờ trình... `heading` dạng `I. TIÊU ĐỀ` hoặc `1. Tiêu đề`. |
| `noi_dung` | mảng block | Nội dung phẳng, không chia mục (biểu mẫu, công điện ngắn). |
| `ket` | chuỗi hoặc mảng | Đoạn kết, ví dụ `Trân trọng.`. |

`heading` bắt đầu bằng `Phần`, `Chương`, `Mục`, `Tiểu mục` sẽ được canh giữa theo
II.6.đ; các trường hợp còn lại in đậm, thụt dòng 1 cm như thân bài.

## Các loại block

```jsonc
{ "type": "para",  "text": "Đoạn văn.", "indent": true }   // indent mặc định true
{ "type": "list",  "items": ["1. ...", "a) ...", "- ..."] } // tự ghi số/gạch đầu dòng
{ "type": "heading", "text": "2.1. Tiêu đề con" }
{ "type": "table", "header": ["Cột A", "Cột B"],
                   "rows": [["1", "2"]],
                   "widths": [4, 12],          // cm, tùy chọn; tổng nên bằng 16
                   "mono_body": false }        // true: thân bảng dùng phông Courier
{ "type": "code",  "lines": ["lệnh / log minh chứng"] }
{ "type": "dots",  "label": "Ông/Bà", "value": "" }  // value trống -> dòng chấm điền tay
{ "type": "center","text": "DÒNG CANH GIỮA", "bold": true }
{ "type": "italic","text": "Ghi chú in nghiêng." }
{ "type": "signatures", "columns": [ { "chuc_vu": "THƯ KÝ", "ho_ten": "" },
                                     { "chuc_vu": "CHỦ TỌA", "ho_ten": "" } ] }
{ "type": "pagebreak" }
```

Một chuỗi đứng một mình trong mảng block tương đương `{ "type": "para", "text": ... }`.

## Khối cuối: nơi nhận và chữ ký

```jsonc
"noi_nhan": [
  "Như trên",                       // không cần ghi "-" và ";" - script tự thêm
  "Sở Nội vụ (để b/c)",
  "Lưu: VT, HCNS (02 bản)"          // dòng cuối BẮT BUỘC bắt đầu bằng "Lưu"
],
"nguoi_ky": {
  "quyen_han":    "KT.",            // TM. | Q. | KT. | TL. | TUQ. - tùy chọn
  "chuc_vu":      "Giám đốc",       // bắt buộc; script in hoa
  "chuc_vu_khac": "Phó Giám đốc",   // ô 7b, in ngay dưới dòng quyền hạn
  "ghi_chu":      "(Ký, ghi rõ họ tên, đóng dấu)",  // đặt "" để bỏ
  "ho_ten":       ""                // trống -> chừa chỗ ký và ghi tên
}
```

Biên bản, hợp đồng và các văn bản hai người ký dùng `chu_ky` thay cho `nguoi_ky`:

```jsonc
"chu_ky": [ { "chuc_vu": "Thư ký", "ho_ten": "" },
            { "chuc_vu": "Chủ tịch Hội đồng", "ho_ten": "" } ]
```

## Phụ lục

```jsonc
"phu_luc": [
  {
    "so": "I",                       // tùy chọn; từ 2 phụ lục trở lên script tự đánh I, II, III
    "tieu_de": "Danh sách thành viên",
    "kem_theo": "(Kèm theo Quyết định số 58/QĐ-MV ngày 02 tháng 02 năm 2026 của ...)",
    "blocks": [ { "type": "table", "header": ["STT", "Họ và tên"], "rows": [["1", ""]] } ]
  }
]
```

`kem_theo` để trống sẽ được script tự dựng từ `so`, `ky_hieu`, `ngay`, `co_quan`
khi đủ cả bốn; nếu thiếu, dòng chỉ dẫn được bỏ qua. Mỗi phụ lục bắt đầu một trang mới.

## Thành phần tùy chọn

| Trường | Kiểu | Ý nghĩa |
| --- | --- | --- |
| `do_mat` | `MẬT` / `TỐI MẬT` / `TUYỆT MẬT` | Dấu chỉ độ mật (ô 10a), in trong khung. |
| `do_khan` | `KHẨN` / `THƯỢNG KHẨN` / `HOẢ TỐC` | Dấu mức độ khẩn (ô 10b). |
| `pham_vi_luu_hanh` | chuỗi | `LƯU HÀNH NỘI BỘ`, `XEM XONG TRẢ LẠI` (ô 11), căn phải. |
| `ky_hieu_nguoi_soan` | chuỗi | Ký hiệu người soạn thảo và số bản phát hành (ô 12), ví dụ `NV.30`. |
| `lien_he` | đối tượng | Chân trang **trang 1** (ô 13): `dia_chi`, `dien_thoai`, `fax`, `email`, `website`. |
| `ghi_chu_noi_bo` | tự do | Không được in. Dùng để ghi chú cho người soạn. |

## Ví dụ đầy đủ

Mười tệp trong `assets/` là ví dụ chạy được ngay, mỗi họ bố cục một tệp:

| Tệp | Minh họa |
| --- | --- |
| `cong-van.json` | công văn có cơ quan chủ quản, phụ lục bảng, chân trang liên hệ, ký hiệu người soạn |
| `quyet-dinh.json` | căn cứ pháp lý, `QUYẾT ĐỊNH:`, các `Điều`, phụ lục danh sách |
| `bao-cao.json` | mục La Mã, bảng số liệu, `Kính gửi` nhiều nơi |
| `to-trinh.json` | bảng kinh phí có `widths`, block `italic`, `Kính gửi` một nơi |
| `thong-bao.json` | văn bản có tên loại không `Kính gửi`, người ký `TL.` |
| `ke-hoach.json` | căn cứ + bảng tiến độ 4 cột |
| `bien-ban.json` | không `Kính gửi`, không `Nơi nhận`, khối ký hai cột |
| `giay-moi.json` | block `dots` điền tay |
| `giay-gioi-thieu.json` | biểu mẫu không trích yếu, dòng thời hạn in nghiêng |
| `cong-dien.json` | dấu `HOẢ TỐC`, nội dung phẳng không chia mục |

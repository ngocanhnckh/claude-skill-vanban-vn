<div align="center">

<img src=".claude-plugin/icon.png" width="104" alt="">

# văn bản hành chính VN

**Government-grade Vietnamese paperwork, drafted by Claude.**

A Claude Agent Skill that turns a sentence into a `.docx` laid out exactly the way
**Decree 30/2020/NĐ-CP** requires. All 29 official document types. Ships with a
validator that quotes the clause you broke.

[![CI](https://github.com/ngocanhnckh/claude-skill-vanban-vn/actions/workflows/ci.yml/badge.svg)](https://github.com/ngocanhnckh/claude-skill-vanban-vn/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-0b7285.svg)](LICENSE)
[![Agent Skill](https://img.shields.io/badge/Claude-Agent%20Skill-d97757)](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
[![Nghị định](https://img.shields.io/badge/N%C4%90-30%2F2020%2FN%C4%90--CP-c8102e)](https://thuvienphapluat.vn/van-ban/bo-may-hanh-chinh/Nghi-dinh-30-2020-ND-CP-cong-tac-van-thu-436532.aspx)
[![Stars](https://img.shields.io/github/stars/ngocanhnckh/claude-skill-vanban-vn?style=flat&color=f2c744)](https://github.com/ngocanhnckh/claude-skill-vanban-vn/stargazers)

[Install](#install) · [Use it](#use-it) · [29 types](#the-29-document-types) ·
[What it refuses to do](#what-it-refuses-to-do) · [**Tiếng Việt**](#hướng-dẫn-tiếng-việt)

<img src="docs/assets/layout.svg" width="900" alt="Sơ đồ bố trí các thành phần thể thức văn bản hành chính">

</div>

---

## Why

In Vietnam the *layout* of an official document is law, not taste. Decree
30/2020/NĐ-CP fixes the paper size, the margins in millimetres, the font, the size
and weight of every line, where the underline goes and how long it is, which
punctuation ends each recipient line, and which fields a công văn may not have at
all. A document that gets this wrong comes back.

A language model asked for a công văn will write excellent prose and then format it
like a Western business letter. This skill splits the problem: **the model writes the
content, a script owns the layout.** The layout is checked against the decree, clause
by clause, before anything is rendered.

```
          you say what you need
                   ↓
       Claude writes  spec.json      ← content only: who, what, why
                   ↓
          kiem_tra.py validates      ← 40+ rules, each citing its clause
                   ↓
         tao_vanban.py renders       ← owns every millimetre
                   ↓
            ketqua.docx + .pdf
```

## Install

**Claude Code, as a plugin** (keeps itself updated):

```bash
claude plugin marketplace add ngocanhnckh/claude-skill-vanban-vn
claude plugin install van-ban-hanh-chinh-vn@vanban-vn
```

**Claude Code, as a personal skill:**

```bash
git clone https://github.com/ngocanhnckh/claude-skill-vanban-vn.git
cp -r claude-skill-vanban-vn/skills/van-ban-hanh-chinh-vn ~/.claude/skills/
```

**claude.ai / the API:** zip `skills/van-ban-hanh-chinh-vn/` and upload it as a Skill.

Python needs `python-docx`. PDF export additionally needs LibreOffice, and is
skipped with a warning when it is missing.

```bash
pip install python-docx
```

## Use it

Just ask. The skill triggers on any request for an official Vietnamese document:

> *"Soạn công văn gửi Sở Kế hoạch và Đầu tư đề nghị gia hạn thời gian nộp báo cáo
> đầu tư quý III, công ty mình là Công ty Cổ phần Mẫu Việt ở Đà Nẵng."*

> *"Draft a quyết định establishing a digital transformation task force, effective
> on signature, with the member list as an appendix."*

Claude writes the spec, validates it, renders the file, and hands you the `.docx`
plus a list of the blanks only you can fill - the document number, the signer's
name, the seal.

Driving the scripts by hand works too:

```bash
cd skills/van-ban-hanh-chinh-vn
python scripts/kiem_tra.py assets/cong-van.json      # validate
python scripts/tao_vanban.py assets/cong-van.json out.docx --pdf
```

The validator is the interesting part. It does not say "invalid"; it says which
clause and how to fix it:

```
=== cong-van.json ===
LOI       $.ten_loai     cong van KHONG co ten loai (II.5.b). Dat trich yeu vao
                         'trich_yeu', script in sau chu 'V/v'.
LOI       $.noi_nhan     dong cuoi phai la 'Luu: VT, <don vi soan thao>, <so ban>.'
                         (II.9.d).
CANH BAO  $.ky_hieu      loai 'quyet-dinh' thuong co ky hieu bat dau bang 'QĐ'
                         (Phu luc III).
GHI CHU   $.so           de trong - chua cho Van thu dien so khi dang ky van ban.
-> 2 loi, 1 canh bao
```

## The 29 document types

Every type listed in Article 7 of the decree, with the abbreviation its symbol must
use (Appendix III). Pick one as `"loai"`.

| | | | |
| --- | --- | --- | --- |
| `nghi-quyet` `NQ` | `quyet-dinh` `QĐ` | `chi-thi` `CT` | `quy-che` `QC` |
| `quy-dinh` `QyĐ` | `thong-cao` `TC` | `thong-bao` `TB` | `huong-dan` `HD` |
| `chuong-trinh` `CTr` | `ke-hoach` `KH` | `phuong-an` `PA` | `de-an` `ĐA` |
| `du-an` `DA` | `bao-cao` `BC` | `bien-ban` `BB` | `to-trinh` `TTr` |
| `hop-dong` `HĐ` | `cong-van` | `cong-dien` `CĐ` | `ban-ghi-nho` `BGN` |
| `ban-thoa-thuan` `BTT` | `giay-uy-quyen` `GUQ` | `giay-moi` `GM` | `giay-gioi-thieu` `GGT` |
| `giay-nghi-phep` `GNP` | `phieu-gui` `PG` | `phieu-chuyen` `PC` | `phieu-bao` `PB` |
| `thu-cong` | | | |

They render through six layout families, because the decree gives some types their
own form: a **công văn** has no type name and carries its subject after `V/v`; a
**quyết định** opens with italic legal bases, a centred `QUYẾT ĐỊNH:` and numbered
`Điều`; a **biên bản** has no recipients block and two signature columns; **giấy
mời**, **giấy giới thiệu** and **giấy nghỉ phép** are fill-in forms; a **công điện**
carries an urgency stamp. Ten runnable examples, one per family, live in
[`assets/`](skills/van-ban-hanh-chinh-vn/assets).

## What it gets right that hand-formatting gets wrong

- Số `7` is written `Số: 07/...`; `ngày 9 tháng 3` becomes `ngày 09 tháng 3`, and
  January and February are padded too.
- The rule under the issuing body is **1/3 to 1/2** of the line, centred - not the
  full width.
- `Kính gửi` is upright, **not bold**. One recipient stays on the same line; several
  go one per line with `-`, `;`, and a final `.`.
- `Nơi nhận:` is italic bold size 12, its list is size 11, and the last line is
  always `Lưu: VT, ...`.
- Page numbers are centred in the top margin and **hidden on page one**.
- Legal bases are italic, one per line, semicolons throughout and a period at the end.
- The em dash `U+2014` is refused everywhere. The decree uses the hyphen.
- Two or more appendices are numbered in Roman numerals, each on a new page, each
  with its `(Kèm theo ... số ... ngày ...)` reference line.

## What it refuses to do

It will **never invent** the document number, the signer's name, their position, or
a date. Those fields stay blank, the renderer reserves the space, and Claude tells
you what to fill in. A document with a fabricated `Số` or a fabricated signer is not
a formatting problem - it is a forgery.

It also does not touch typography on request. The margins, font and sizes come from
the decree; the only knob is body size 13 or 14, which the decree itself allows.

## What is in the box

```
skills/van-ban-hanh-chinh-vn/
├── SKILL.md                      # what Claude loads: workflow, hard rules, pointers
├── references/
│   ├── the-thuc-nd30.md          # the formatting rules, clause by clause
│   ├── loai-van-ban.md           # 29 types, abbreviations, per-type components
│   └── luoc-do-json.md           # every spec field and block type
├── scripts/
│   ├── tao_vanban.py             # renderer; every constant traced to its clause
│   └── kiem_tra.py               # validator; no dependencies
└── assets/*.json                 # 10 complete, runnable examples
```

`SKILL.md` stays small on purpose. Claude loads it when the task is a Vietnamese
document, and only then reaches for the reference file it actually needs - the
progressive-disclosure pattern from Anthropic's
[skill authoring guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).
The scripts are never loaded into context at all; they are run.

## Develop

```bash
pip install python-docx
python tests/test_render.py     # renders all 10 examples, asserts the layout rules
python tests/test_skill_md.py   # frontmatter limits, link hygiene, plugin manifests
```

CI runs both on Python 3.9, 3.11 and 3.13. Contributions welcome - especially real
(anonymised) documents that this gets wrong. Please cite the clause you are fixing;
see [CONTRIBUTING.md](CONTRIBUTING.md).

## Note on the law

This is a community tool, not an official publication of any Vietnamese authority.
It implements Appendix I of Decree 30/2020/NĐ-CP as published, but individual
ministries, provinces and companies add their own conventions on top, and the decree
can be amended. **Check the output against your organisation's own rules before
sending anything.** Always open the PDF and look at it.

---

# Hướng dẫn tiếng Việt

## Skill này làm gì

Biến một câu yêu cầu thành tệp `.docx` **đúng thể thức Nghị định 30/2020/NĐ-CP**:
Quốc hiệu, Tiêu ngữ, tên cơ quan, số và ký hiệu, địa danh ngày tháng, trích yếu,
Kính gửi, nội dung, Nơi nhận, khối chữ ký, phụ lục - đủ **29 loại văn bản hành
chính** tại Điều 7.

Bạn chỉ viết **nội dung**. Phần trình bày do script lo: khổ A4, lề 20-25 / 30-35 /
15-20 mm, Times New Roman, cỡ chữ và kiểu chữ từng thành phần, đường kẻ ngang dài
đúng 1/3 - 1/2 dòng chữ, số 0 thêm vào số văn bản và ngày tháng, dấu chấm phẩy cuối
mỗi dòng Nơi nhận.

## Cài đặt

Trong Claude Code:

```bash
claude plugin marketplace add ngocanhnckh/claude-skill-vanban-vn
claude plugin install van-ban-hanh-chinh-vn@vanban-vn
```

Hoặc chép tay vào thư mục skill cá nhân:

```bash
git clone https://github.com/ngocanhnckh/claude-skill-vanban-vn.git
cp -r claude-skill-vanban-vn/skills/van-ban-hanh-chinh-vn ~/.claude/skills/
pip install python-docx
```

## Dùng thế nào

Cứ nói bình thường, không cần gọi tên skill:

> *"Soạn công văn gửi Cục Thuế tỉnh đề nghị gia hạn nộp hồ sơ quyết toán, công ty
> mình là Công ty Cổ phần Mẫu Việt, trụ sở Đà Nẵng."*

> *"Làm quyết định thành lập Tổ công tác chuyển đổi số, danh sách thành viên để ở
> phụ lục."*

Claude sẽ soạn tệp mô tả, chạy trình kiểm tra, xuất `.docx` (kèm `.pdf` nếu máy có
LibreOffice) rồi **liệt kê những ô bạn phải tự điền**: số văn bản, họ tên người ký,
con dấu.

## Những gì skill tuyệt đối không làm

**Không bịa** số văn bản, tên người ký, chức vụ hay ngày tháng. Thiếu thì để trống và
báo bạn điền. Một văn bản có số hoặc người ký bịa ra không còn là lỗi trình bày.

## Tài liệu kèm theo

| Tệp | Nội dung |
| --- | --- |
| [`references/the-thuc-nd30.md`](skills/van-ban-hanh-chinh-vn/references/the-thuc-nd30.md) | Toàn bộ thể thức, từng khoản từng điểm, kèm sơ đồ bố trí 14 ô và 10 lỗi thường gặp |
| [`references/loai-van-ban.md`](skills/van-ban-hanh-chinh-vn/references/loai-van-ban.md) | 29 loại văn bản, chữ viết tắt, mẫu áp dụng, thành phần bắt buộc từng loại |
| [`references/luoc-do-json.md`](skills/van-ban-hanh-chinh-vn/references/luoc-do-json.md) | Mọi trường của tệp mô tả và các loại block nội dung |
| [`assets/`](skills/van-ban-hanh-chinh-vn/assets) | 10 ví dụ hoàn chỉnh chạy được ngay |

## Lưu ý pháp lý

Đây là công cụ cộng đồng, **không phải ấn phẩm chính thức** của cơ quan nhà nước.
Skill bám theo Phụ lục I Nghị định 30/2020/NĐ-CP, nhưng mỗi bộ, ngành, địa phương,
doanh nghiệp còn có quy định riêng và nghị định có thể được sửa đổi. **Hãy mở PDF
xem bằng mắt và đối chiếu quy định nội bộ trước khi gửi đi.**

---

<div align="center">

MIT · Nếu skill tiết kiệm được cho bạn một buổi chiều chỉnh lề, hãy để lại một ⭐

</div>

---
name: van-ban-hanh-chinh-vn
description: >-
  Drafts and renders Vietnamese administrative documents as .docx files laid out
  exactly as Decree 30/2020/ND-CP requires - Quoc hieu/Tieu ngu, issuing body,
  So/ky hieu, V/v, Kinh gui, Noi nhan, signature block, Times New Roman, legal
  margins - for all 29 document types of Article 7. Use when the user asks for a
  cong van, quyet dinh, bao cao, to trinh, thong bao, ke hoach, bien ban, giay
  moi, giay gioi thieu, cong dien, chi thi, quy che, huong dan, hop dong, phieu
  gui or any other "van ban hanh chinh" / official letter addressed to a
  Vietnamese agency, company or school; also use for "thể thức văn bản", "Nghị
  định 30", "công văn giải trình", "soạn văn bản hành chính", "mẫu công văn",
  "văn bản gửi cơ quan nhà nước".
---

# Vietnamese administrative documents (Decree 30/2020/ND-CP)

Write the *content* into a JSON spec; the bundled script renders a `.docx` whose
layout follows Appendix I of the decree. Never hand-format the document yourself.

## Workflow

Copy this checklist and tick it off:

```
- [ ] 1. Pick the type (`loai`) and collect the facts the decree demands
- [ ] 2. Write spec.json
- [ ] 3. Validate: python scripts/kiem_tra.py spec.json  -> 0 errors
- [ ] 4. Render:   python scripts/tao_vanban.py spec.json out.docx --pdf
- [ ] 5. Look at the PDF, then hand over the files and list what the user must fill in
```

**1. Pick the type.** One of the 29 types in Article 7 - the `loai` keys are listed
in [references/loai-van-ban.md](references/loai-van-ban.md) together with each
type's official abbreviation and the components it must carry. When unsure between
a `cong-van` and a typed document: a cong van is a letter about one piece of
business, everything else has a name printed at the top.

**2. Write the spec.** Full field reference:
[references/luoc-do-json.md](references/luoc-do-json.md). Start from the closest
bundled example in `assets/` - there is one per layout family. Minimal spec:

```json
{
  "loai": "cong-van",
  "co_quan": "Công ty Cổ phần Mẫu Việt",
  "so": "", "ky_hieu": "MV-HCNS",
  "dia_danh": "Hà Nội", "ngay": "2026-10-31",
  "trich_yeu": "đề nghị phối hợp kiểm tra chất lượng hàng hóa",
  "kinh_gui": "Chi cục Quản lý thị trường tỉnh Mẫu",
  "mo_dau": "Căn cứ hợp đồng số 12/2026/HĐ-MV ngày 02 tháng 9 năm 2026, Công ty đề nghị Quý cơ quan phối hợp như sau:",
  "muc": [{ "heading": "1. Nội dung đề nghị", "blocks": [
    { "type": "para", "text": "..." }
  ]}],
  "ket": ["Trân trọng cảm ơn sự phối hợp của Quý cơ quan."],
  "noi_nhan": ["Như trên", "Lưu: VT, HCNS (02 bản)"],
  "nguoi_ky": { "chuc_vu": "Tổng Giám đốc", "ho_ten": "" }
}
```

**3. Validate.** `kiem_tra.py` checks the spec against the decree and names the
clause behind every message. Fix every `LOI`, read every `CANH BAO`, then run it
again. Do not render while errors remain.

```bash
python scripts/kiem_tra.py spec.json
```

**4. Render.**

```bash
uv run --with python-docx python scripts/tao_vanban.py spec.json ketqua.docx --pdf
```

Drop the `uv run --with python-docx` prefix if `python-docx` is already installed.
`--pdf` needs LibreOffice (`soffice`); without it the step is skipped with a
warning and only the `.docx` is produced.

**5. Check with your eyes.** Layout errors survive every automated check. Open the
PDF (or convert the first page to an image and look at it) and confirm: Quoc hieu
top right, Tieu ngu underlined, issuing body top left with its own short rule,
So/ky hieu under the issuing body, place and date on that same line to the right,
"Kinh gui" centred, body justified, "Noi nhan:" bottom left, signature block
bottom right with room for the seal.

Then give the user both files and **list every blank left for them**, typically:
`So`, the signer's `ho_ten`, and the seal.

## Hard rules

- **Never invent** the document number, the signer's name, their position, or a
  date. Leave the field empty - the renderer reserves the space - and tell the
  user what to fill in. A wrong `So` or a wrong signer makes the document invalid.
- **No em dash (U+2014) anywhere.** The decree uses the hyphen `-`. Both scripts
  refuse to run otherwise.
- **A cong van has no type name.** Its subject goes after `V/v` in the left column,
  never as a centred "CÔNG VĂN" heading.
- **Do not touch the typography.** Times New Roman, body 13-14, margins 20-25 mm
  top and bottom, 30-35 mm left, 15-20 mm right. The script owns all of it; the
  only knob is `"co_chu": 13 | 14`.
- **The last line of `noi_nhan` is always** `Lưu: VT, <đơn vị soạn thảo> (<số> bản)`.
- **Quote, don't paraphrase, legal bases.** A `can_cu` line must carry the type,
  number, symbol, date, issuing body and subject of the document it cites.
- Hand over files. Do not paste the document into a chat artifact or a web page as
  a substitute for the `.docx`.

## Layout families

| `loai` | Layout | Distinctive components |
| --- | --- | --- |
| `cong-van`, `thu-cong` | letter | no type name, `V/v`, `Kính gửi` |
| `quyet-dinh`, `nghi-quyet` | resolution | `can_cu`, "QUYẾT ĐỊNH:", `dieu` |
| `bien-ban` | minutes | no `Kính gửi`, no `Nơi nhận`, `chu_ky` columns |
| `giay-moi`, `giay-gioi-thieu`, `giay-nghi-phep` | form | `dots` fill-in lines |
| `cong-dien` | telegram | urgency stamp, `Kính gửi` |
| the other 20 types | typed document | centred type name + subject + rule |

## References

- [references/loai-van-ban.md](references/loai-van-ban.md) - the 29 types, their
  abbreviations, which form of Appendix III applies, per-type required components.
- [references/the-thuc-nd30.md](references/the-thuc-nd30.md) - the formatting rules
  themselves, clause by clause: sizes, styles, positions, punctuation.
- [references/luoc-do-json.md](references/luoc-do-json.md) - every spec field and
  every block type, with examples.
- `assets/*.json` - ten complete, runnable examples, one per layout family.

## Dependencies

- `python-docx` (required). Install with `pip install python-docx` or run through
  `uv run --with python-docx python ...`.
- LibreOffice (optional, for `--pdf`): `brew install --cask libreoffice` on macOS,
  `apt install libreoffice` on Debian/Ubuntu.

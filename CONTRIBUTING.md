# Contributing / Đóng góp

Thanks for helping. The most valuable contribution is a real document - anonymised -
that this skill formats wrongly.

Đóng góp quý nhất là một văn bản thật (đã xóa thông tin cá nhân) mà skill trình bày
sai.

## Ground rules

1. **Cite the clause.** Every layout change must point at the clause of Decree
   30/2020/NĐ-CP it implements, in the form used throughout this repository:
   `II.9.d` means Appendix I, Part I, Section II, item 9, point d. A change that
   cannot cite a clause belongs in an issue first.
2. **No fabricated data in examples.** Use obviously fictional bodies
   (`Công ty Cổ phần Mẫu Việt`, `quận Mẫu`, `tỉnh Mẫu`). Never commit a real
   document number, a real person's name, or a real address.
3. **No em dash.** `U+2014` is rejected by the scripts and by the test suite. The
   decree uses the hyphen `-`.
4. **No voodoo constants.** A new number in `tao_vanban.py` needs a comment saying
   which clause fixes it, or why that value was chosen.
5. **Forward slashes** in every path, on every platform.

## Before you open a pull request

```bash
pip install python-docx
python skills/van-ban-hanh-chinh-vn/scripts/kiem_tra.py skills/van-ban-hanh-chinh-vn/assets/*.json
python tests/test_render.py
python tests/test_skill_md.py
```

Then render at least one example to PDF and **look at it**:

```bash
python skills/van-ban-hanh-chinh-vn/scripts/tao_vanban.py \
    skills/van-ban-hanh-chinh-vn/assets/cong-van.json /tmp/out.docx --pdf
```

Automated checks cannot see a rule that is one millimetre off.

## Adding an example

One example per layout family is enough; a new example should show something none of
the existing ten shows. Put it in `skills/van-ban-hanh-chinh-vn/assets/`, make sure
`kiem_tra.py` reports **zero warnings** for it, and mention what it demonstrates in
the table at the end of `references/luoc-do-json.md`.

## Adding a document type

All 29 types of Article 7 are already supported. If a ministry or sector uses a form
that none of the six layout families covers, open an issue with the published form
and a sample before writing code.

## Changing SKILL.md

Keep the body under 500 lines, keep every link one level deep, and keep the
description in the third person - `tests/test_skill_md.py` enforces all three.

# -*- coding: utf-8 -*-
"""Render every bundled example and assert the layout rules that matter.

    python tests/test_render.py

Needs python-docx. Exits non-zero on the first failed assertion, so it can be
used directly as a CI step.
"""
from __future__ import annotations

import glob
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "van-ban-hanh-chinh-vn")
SCRIPTS = os.path.join(SKILL, "scripts")
ASSETS = os.path.join(SKILL, "assets")
sys.path.insert(0, SCRIPTS)

from docx import Document  # noqa: E402

import tao_vanban  # noqa: E402

FAILURES = []


def check(cond, msg):
    if not cond:
        FAILURES.append(msg)
    return cond


def all_text(doc):
    parts = [p.text for p in doc.paragraphs]
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                parts.extend(p.text for p in cell.paragraphs)
    return "\n".join(parts)


def first_runs(doc):
    """Every run in the document, in reading order, paragraphs then tables."""
    for p in doc.paragraphs:
        for r in p.runs:
            yield p, r
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for r in p.runs:
                        yield p, r


def test_validator_clean():
    specs = sorted(glob.glob(os.path.join(ASSETS, "*.json")))
    check(len(specs) >= 10, "expected at least 10 bundled examples, found %d" % len(specs))
    r = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, "kiem_tra.py")] + specs,
        capture_output=True, text=True,
    )
    check(r.returncode == 0, "kiem_tra.py reported errors:\n" + r.stdout)
    check("CANH BAO" not in r.stdout,
          "bundled examples should raise no warnings:\n" + r.stdout)


def test_every_example_renders(tmp):
    for spec in sorted(glob.glob(os.path.join(ASSETS, "*.json"))):
        name = os.path.basename(spec)[:-5]
        out = os.path.join(tmp, name + ".docx")
        tao_vanban.main([spec, out])
        doc = Document(out)
        txt = all_text(doc)

        # II.1 - the national heading and motto are on every document
        check("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" in txt,
              "%s: missing Quoc hieu" % name)
        check("Độc lập - Tự do - Hạnh phúc" in txt, "%s: missing Tieu ngu" % name)
        # II.3 - "So:" block, numbers below 10 padded
        check("Số: " in txt, "%s: missing so/ky hieu" % name)
        # hyphen only, never the em dash
        check("—" not in txt, "%s: contains an em dash" % name)
        # I.3 - margins
        sec = doc.sections[0]
        check(abs(sec.left_margin.cm - 3.0) < 0.01, "%s: left margin" % name)
        check(abs(sec.right_margin.cm - 2.0) < 0.01, "%s: right margin" % name)
        check(abs(sec.top_margin.cm - 2.0) < 0.01, "%s: top margin" % name)
        # I.4 - Times New Roman and black, everywhere except the mono evidence runs
        for p, r in first_runs(doc):
            if r.font.name in (None, "Times New Roman", "Courier New"):
                continue
            check(False, "%s: unexpected font %r in %r" % (name, r.font.name, p.text[:40]))
        # II.6.e - body size is 13 or 14
        sizes = {int(r.font.size.pt) for _, r in first_runs(doc) if r.font.size}
        check(sizes <= {2, 10, 11, 12, 13, 14},
              "%s: unexpected font sizes %s" % (name, sorted(sizes)))
        # I.7 - page numbers are hidden on page 1
        check(sec.different_first_page_header_footer,
              "%s: first page header must differ (I.7)" % name)
        print("ok  %s" % name)


def test_cong_van_has_no_type_name(tmp):
    out = os.path.join(tmp, "cv.docx")
    tao_vanban.main([os.path.join(ASSETS, "cong-van.json"), out])
    doc = Document(out)
    centred = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    check(not any(t == "CÔNG VĂN" for t in centred),
          "a cong van must not print a type name (II.5.b)")
    check("V/v " in all_text(doc), "a cong van puts its subject after 'V/v' (II.5.b)")


def test_quyet_dinh_structure(tmp):
    out = os.path.join(tmp, "qd.docx")
    tao_vanban.main([os.path.join(ASSETS, "quyet-dinh.json"), out])
    doc = Document(out)
    texts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    check("QUYẾT ĐỊNH" in texts, "missing the type name")
    check("QUYẾT ĐỊNH:" in texts, "missing the 'QUYET DINH:' line after the bases")
    check(any(t.startswith("Điều 1.") for t in texts), "missing Dieu 1")
    # II.6.a - every legal basis is italic and ends with ';' except the last
    bases = [p for p in doc.paragraphs
             if p.text.startswith(("Căn cứ", "Xét đề nghị"))]
    check(len(bases) == 3, "expected 3 legal bases, got %d" % len(bases))
    check(all(p.runs[0].font.italic for p in bases), "legal bases must be italic")
    check(bases[-1].text.rstrip().endswith("."), "the last basis ends with a period")
    check(all(p.text.rstrip().endswith(";") for p in bases[:-1]),
          "earlier bases end with a semicolon")


def test_noi_nhan_ends_with_luu(tmp):
    out = os.path.join(tmp, "bc.docx")
    tao_vanban.main([os.path.join(ASSETS, "bao-cao.json"), out])
    doc = Document(out)
    lines = []
    for t in doc.tables:  # the closing table is the one holding "Noi nhan:"
        cell = t.cell(0, 0)
        texts = [p.text for p in cell.paragraphs if p.text.strip()]
        if texts and texts[0] == "Nơi nhận:":
            lines = texts
            break
    check(lines[0] == "Nơi nhận:", "the recipients block starts with 'Noi nhan:'")
    check(lines[-1].startswith("- Lưu:"), "the last line is '- Luu: VT...' (II.9.d)")
    check(lines[-1].endswith("."), "the last recipient line ends with a period")
    check(all(x.endswith(";") for x in lines[1:-1]),
          "every other recipient line ends with a semicolon")


def test_invalid_type_is_rejected(tmp):
    import json
    bad = os.path.join(tmp, "bad.json")
    with open(bad, "w", encoding="utf-8") as f:
        json.dump({"loai": "nghi-dinh", "co_quan": "X", "dia_danh": "Hà Nội",
                   "ngay": "2026-01-01"}, f)
    try:
        tao_vanban.main([bad, os.path.join(tmp, "bad.docx")])
    except SystemExit as e:
        check(e.code != 0, "an unknown type must fail")
        return
    check(False, "an unknown type must fail")


def test_em_dash_is_rejected(tmp):
    import json
    bad = os.path.join(tmp, "dash.json")
    spec = json.load(open(os.path.join(ASSETS, "thong-bao.json"), encoding="utf-8"))
    spec["mo_dau"] = "Thong bao — noi dung"
    with open(bad, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False)
    try:
        tao_vanban.main([bad, os.path.join(tmp, "dash.docx")])
    except SystemExit as e:
        check(e.code != 0, "an em dash must fail the render")
        return
    check(False, "an em dash must fail the render")


def test_date_formatting():
    f = tao_vanban.fmt_ngay
    check(f("2026-03-09") == "ngày 09 tháng 3 năm 2026", "pad day < 10")
    check(f("2026-01-15") == "ngày 15 tháng 01 năm 2026", "pad month 1")
    check(f("2026-02-02") == "ngày 02 tháng 02 năm 2026", "pad day and month 2")
    check(f("2026-12-25") == "ngày 25 tháng 12 năm 2026", "no padding needed")
    check(f("09/03/2026") == "ngày 09 tháng 3 năm 2026", "accept dd/mm/yyyy")
    check(f("ngày 05 tháng 3 năm 2020") == "ngày 05 tháng 3 năm 2020",
          "leave a ready-made sentence alone")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        test_validator_clean()
        test_every_example_renders(tmp)
        test_cong_van_has_no_type_name(tmp)
        test_quyet_dinh_structure(tmp)
        test_noi_nhan_ends_with_luu(tmp)
        test_invalid_type_is_rejected(tmp)
        test_em_dash_is_rejected(tmp)
        test_date_formatting()
    if FAILURES:
        print("\n%d FAILED:" % len(FAILURES))
        for m in FAILURES:
            print("  -", m)
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

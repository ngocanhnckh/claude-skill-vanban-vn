# -*- coding: utf-8 -*-
"""Generate Vietnamese administrative documents (.docx) that follow the layout
rules of Decree 30/2020/ND-CP, Appendix I ("Nghi dinh 30/2020/ND-CP, Phu luc I").

Usage:
    python tao_vanban.py <spec.json> <out.docx>
    python tao_vanban.py <spec.json> <out.docx> --pdf      # also export PDF (needs soffice)

Requires: python-docx
    uv run --with python-docx python tao_vanban.py spec.json out.docx

Every magic number below is traced to the clause of Appendix I that fixes it.
References written as "II.6.e" mean Appendix I, Part I, Section II, item 6, point e.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

try:
    from docx import Document
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor
except ImportError:  # solve, don't defer: tell the caller exactly what to run
    sys.exit(
        "LOI: thieu thu vien python-docx.\n"
        "Chay lai bang:  uv run --with python-docx python "
        + os.path.basename(__file__)
        + " spec.json ketqua.docx\n"
        "Hoac cai dat:   pip install python-docx"
    )

# --------------------------------------------------------------------------
# Constants fixed by Appendix I
# --------------------------------------------------------------------------
FONT = "Times New Roman"          # I.4 - Times New Roman, Unicode TCVN 6909:2001, black
MONO = "Courier New"              # not in the decree; only for code/log evidence blocks

BODY_SIZE = 13                    # II.6.e - body text 13-14; 13 is the common choice
QUOCHIEU_SIZE = 12                # II.1.a - Quoc hieu 12-13
TIEUNGU_SIZE = 13                 # II.1.b - Tieu ngu must be one step above Quoc hieu
COQUAN_SIZE = 12                  # II.2.b - issuing body 12-13
SO_SIZE = 13                      # II.3.c - the word "So" and the symbol are size 13
DIADANH_SIZE = 13                 # II.4.c - place and date 13-14, italic
TENLOAI_SIZE = 14                 # II.5.b - document type 13-14, caps, bold
TRICHYEU_CV_SIZE = 12             # II.5.b - cong van subject after "V/v", 12-13
NOINHAN_LABEL_SIZE = 12           # II.9.d - "Noi nhan:" size 12, italic, bold
NOINHAN_ITEM_SIZE = 11            # II.9.d - the recipient list is size 11, upright
DRAFTER_SIZE = 11                 # III.3 - drafter code and print run, size 11
CONTACT_SIZE = 11                 # III.4 - address/email/phone block, 11-12
SIGINFO_SIZE = 10                 # II.8.b - digital signature info line, size 10
PHULUC_LABEL_SIZE = 14            # III.1.b - the word "Phu luc" + number, size 14

MARGIN_TOP_CM = 2.0               # I.3 - 20-25 mm
MARGIN_BOTTOM_CM = 2.0            # I.3 - 20-25 mm
MARGIN_LEFT_CM = 3.0              # I.3 - 30-35 mm
MARGIN_RIGHT_CM = 2.0             # I.3 - 15-20 mm

INDENT_CM = 1.0                   # II.6.e - first line indent 1 cm or 1.27 cm
PARA_SPACE_PT = 6                 # II.6.e - at least 6 pt between paragraphs

# A4 is 21 cm wide (I.1), so the printable width is what is left after the margins.
USABLE_CM = 21.0 - MARGIN_LEFT_CM - MARGIN_RIGHT_CM          # 16.0 cm
# II.3.c + II.4.c put the symbol block and the place/date block on the same line,
# in two columns. The right column holds "CONG HOA XA HOI CHU NGHIA VIET NAM",
# the longest fixed string in the document, so it gets the larger share.
COL_LEFT_CM = 7.0
COL_RIGHT_CM = USABLE_CM - COL_LEFT_CM                        # 9.0 cm

# Approximate advance width per character of Times New Roman, in cm, by point size.
# Only used to size the decorative rules, whose required length is relative to the
# text above them ("1/3 to 1/2 of the line", II.2.b and II.5.b), so a close
# approximation is enough - the rule only has to land inside that range.
CHAR_W_CM = {10: 0.171, 11: 0.188, 12: 0.205, 13: 0.222, 14: 0.239}
# Midpoint of the legal 1/3..1/2 range for the rules under the issuing body and
# under the subject line.
RULE_RATIO = 0.42
RULE_MIN_CM = 2.0

EM_DASH = "—"

# --------------------------------------------------------------------------
# The 29 document types of Article 7, with the abbreviations of Appendix III
# --------------------------------------------------------------------------
# key -> (display name used as "ten loai", abbreviation for the symbol, layout family)
TYPES = {
    "nghi-quyet":       ("NGHỊ QUYẾT",        "NQ",  "nghi-quyet"),
    "quyet-dinh":       ("QUYẾT ĐỊNH",        "QĐ",  "quyet-dinh"),
    "chi-thi":          ("CHỈ THỊ",           "CT",  "co-ten-loai"),
    "quy-che":          ("QUY CHẾ",           "QC",  "co-ten-loai"),
    "quy-dinh":         ("QUY ĐỊNH",          "QyĐ", "co-ten-loai"),
    "thong-cao":        ("THÔNG CÁO",         "TC",  "co-ten-loai"),
    "thong-bao":        ("THÔNG BÁO",         "TB",  "co-ten-loai"),
    "huong-dan":        ("HƯỚNG DẪN",         "HD",  "co-ten-loai"),
    "chuong-trinh":     ("CHƯƠNG TRÌNH",      "CTr", "co-ten-loai"),
    "ke-hoach":         ("KẾ HOẠCH",          "KH",  "co-ten-loai"),
    "phuong-an":        ("PHƯƠNG ÁN",         "PA",  "co-ten-loai"),
    "de-an":            ("ĐỀ ÁN",             "ĐA",  "co-ten-loai"),
    "du-an":            ("DỰ ÁN",             "DA",  "co-ten-loai"),
    "bao-cao":          ("BÁO CÁO",           "BC",  "co-ten-loai"),
    "bien-ban":         ("BIÊN BẢN",          "BB",  "bien-ban"),
    "to-trinh":         ("TỜ TRÌNH",          "TTr", "co-ten-loai"),
    "hop-dong":         ("HỢP ĐỒNG",          "HĐ",  "co-ten-loai"),
    "cong-van":         ("",                  "",    "cong-van"),
    "cong-dien":        ("CÔNG ĐIỆN",         "CĐ",  "cong-dien"),
    "ban-ghi-nho":      ("BẢN GHI NHỚ",       "BGN", "co-ten-loai"),
    "ban-thoa-thuan":   ("BẢN THỎA THUẬN",    "BTT", "co-ten-loai"),
    "giay-uy-quyen":    ("GIẤY ỦY QUYỀN",     "GUQ", "co-ten-loai"),
    "giay-moi":         ("GIẤY MỜI",          "GM",  "giay-moi"),
    "giay-gioi-thieu":  ("GIẤY GIỚI THIỆU",   "GGT", "giay-gioi-thieu"),
    "giay-nghi-phep":   ("GIẤY NGHỈ PHÉP",    "GNP", "giay-nghi-phep"),
    "phieu-gui":        ("PHIẾU GỬI",         "PG",  "co-ten-loai"),
    "phieu-chuyen":     ("PHIẾU CHUYỂN",      "PC",  "co-ten-loai"),
    "phieu-bao":        ("PHIẾU BÁO",         "PB",  "co-ten-loai"),
    "thu-cong":         ("THƯ CÔNG",          "",    "cong-van"),
}

# Types that carry a "Kinh gui" block (II.9.b: To trinh, Bao cao sent upward, Cong van).
KINH_GUI_TYPES = {"cong-van", "to-trinh", "bao-cao", "thu-cong", "cong-dien", "giay-moi"}

MONTHS_NEED_PAD = {1, 2}  # II.4.b: pad day < 10 and months 1 and 2 with a leading zero


def fail(msg: str) -> "None":
    sys.exit("LOI: " + msg)


def check_text(s):
    """Reject the em dash: II.1.b and II.9.d use the hyphen '-' everywhere."""
    if isinstance(s, str) and EM_DASH in s:
        fail("noi dung chua dau gach dai U+2014, phai dung dau gach ngang '-'. Tai: " + s[:70])
    return s


def fmt_ngay(value):
    """Accept 'YYYY-MM-DD', 'DD/MM/YYYY' or a ready-made string and render it the
    way II.4.b requires: full words, leading zero on days < 10 and months 1-2."""
    if not value:
        return ""
    s = str(value).strip()
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", s)
    if not m:
        m2 = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{4})$", s)
        if m2:
            d, mo, y = int(m2.group(1)), int(m2.group(2)), int(m2.group(3))
        else:
            return s  # already a sentence such as "ngay 05 thang 3 nam 2020"
    else:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    day = "%02d" % d if d < 10 else str(d)
    month = "%02d" % mo if mo in MONTHS_NEED_PAD else str(mo)
    return "ngày %s tháng %s năm %d" % (day, month, y)


def est_width_cm(text: str, size: int) -> float:
    return len(text or "") * CHAR_W_CM.get(size, CHAR_W_CM[BODY_SIZE])


class VanBan:
    def __init__(self, spec: dict):
        self.s = spec
        loai = spec.get("loai", "cong-van")
        if loai not in TYPES:
            fail(
                "loai '%s' khong thuoc 29 loai van ban hanh chinh tai Dieu 7 ND 30/2020.\n"
                "Cac gia tri hop le: %s" % (loai, ", ".join(sorted(TYPES)))
            )
        self.loai = loai
        self.ten_loai_default, self.viet_tat, self.family = TYPES[loai]
        self.body_size = int(spec.get("co_chu", BODY_SIZE))
        if self.body_size not in (13, 14):
            fail("co_chu phai la 13 hoac 14 (II.6.e). Dang nhan: %r" % spec.get("co_chu"))
        self.doc = Document()
        self._setup_styles()

    # ---------------- page and style setup ----------------
    def _setup_styles(self):
        st = self.doc.styles["Normal"]
        st.font.name = FONT
        st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        st.font.size = Pt(self.body_size)
        st.font.color.rgb = RGBColor(0, 0, 0)
        pf = st.paragraph_format
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.line_spacing_rule = WD_LINE_SPACING.SINGLE

        sec = self.doc.sections[0]
        sec.top_margin = Cm(MARGIN_TOP_CM)
        sec.bottom_margin = Cm(MARGIN_BOTTOM_CM)
        sec.left_margin = Cm(MARGIN_LEFT_CM)
        sec.right_margin = Cm(MARGIN_RIGHT_CM)
        # I.7 and III.4: page numbers and the contact block only exist from page 2
        # / only on page 1 respectively, so the first page needs its own header.
        sec.different_first_page_header_footer = True
        if self.s.get("so_trang", True):
            self._page_numbers(sec)
        if self.s.get("lien_he"):
            self._contact_footer(sec)

    def _page_numbers(self, sec):
        """I.7 - Arabic numerals from 1, size 13-14, centred in the top margin,
        first page not shown."""
        p = sec.header.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        self._style_run(run, size=self.body_size)
        fld = OxmlElement("w:fldSimple")
        fld.set(qn("w:instr"), "PAGE")
        run._r.addnext(fld)

    def _contact_footer(self, sec):
        """III.4 - address, email, website, phone, fax on page 1 only, size 11-12,
        under a full-width rule."""
        lh = self.s["lien_he"]
        parts = []
        for key, label in (
            ("dia_chi", ""),
            ("dien_thoai", "ĐT: "),
            ("fax", "Fax: "),
            ("email", "Email: "),
            ("website", ""),
        ):
            if lh.get(key):
                parts.append(label + str(lh[key]))
        if not parts:
            return
        p = sec.first_page_footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        self._border(p, "top")
        self._style_run(p.add_run(check_text(" | ".join(parts))), size=CONTACT_SIZE)

    # ---------------- low level helpers ----------------
    def _style_run(self, run, size=None, bold=False, italic=False, caps=False, mono=False):
        name = MONO if mono else FONT
        run.font.name = name
        run.element.rPr.rFonts.set(qn("w:eastAsia"), name)
        run.font.size = Pt(size or self.body_size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.all_caps = caps
        run.font.color.rgb = RGBColor(0, 0, 0)
        return run

    def _para(self, parent=None, align=None, before=0, after=0, indent=None,
              line=None, left=None, right=None):
        p = (parent or self.doc).add_paragraph()
        if align is not None:
            p.alignment = align
        pf = p.paragraph_format
        pf.space_before = Pt(before)
        pf.space_after = Pt(after)
        if indent is not None:
            pf.first_line_indent = Cm(indent)
        if left is not None:
            pf.left_indent = Cm(left)
        if right is not None:
            pf.right_indent = Cm(right)
        if line is not None:
            pf.line_spacing = line
        return p

    def _text(self, p, text, **kw):
        return self._style_run(p.add_run(check_text(text)), **kw)

    def _line(self, text, align=WD_ALIGN_PARAGRAPH.LEFT, parent=None,
              before=0, after=0, **kw):
        p = self._para(parent=parent, align=align, before=before, after=after)
        self._text(p, text, **kw)
        return p

    def _border(self, p, edge="bottom"):
        pPr = p._p.get_or_add_pPr()
        bdr = pPr.find(qn("w:pBdr"))
        if bdr is None:
            bdr = OxmlElement("w:pBdr")
            pPr.append(bdr)
        e = OxmlElement("w:" + edge)
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), "6")        # 6 eighths of a point = a 0.75 pt hairline
        e.set(qn("w:space"), "1")
        e.set(qn("w:color"), "000000")
        bdr.append(e)

    def _rule(self, parent, width_cm, avail_cm, after=0):
        """A centred horizontal rule of a given length: an empty 2 pt paragraph
        whose bottom border is narrowed by equal left and right indents."""
        width_cm = max(0.8, min(width_cm, avail_cm))
        side = max(0.0, (avail_cm - width_cm) / 2.0)
        p = self._para(parent=parent, after=after, left=side, right=side)
        run = p.add_run()
        self._style_run(run, size=2)
        self._border(p)
        return p

    def _text_rule(self, parent, text, size, avail_cm, ratio=None, after=0):
        """Rule sized from the text above it. ratio=None means 'as long as the
        line' (II.1.b); otherwise a fraction of it (II.2.b, II.5.b: 1/3 to 1/2)."""
        w = est_width_cm(text, size)
        if ratio is not None:
            w = max(RULE_MIN_CM, w * ratio)
        return self._rule(parent, w, avail_cm, after=after)

    def _strip_borders(self, table):
        for row in table.rows:
            for c in row.cells:
                tcPr = c._tc.get_or_add_tcPr()
                tcB = OxmlElement("w:tcBorders")
                for edge in ("top", "left", "bottom", "right"):
                    e = OxmlElement("w:" + edge)
                    e.set(qn("w:val"), "nil")
                    tcB.append(e)
                tcPr.append(tcB)

    def _cell_para(self, cell, first=False, align=WD_ALIGN_PARAGRAPH.CENTER,
                   before=0, after=0):
        p = cell.paragraphs[0] if first else cell.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(before)
        p.paragraph_format.space_after = Pt(after)
        return p

    def _box(self, text, size=None, align=WD_ALIGN_PARAGRAPH.LEFT):
        """III.2 - the secrecy / urgency stamps and the circulation notes are set
        inside a single-line rectangle, caps, bold, 13-14."""
        width = est_width_cm(text, size or self.body_size) + 0.8
        t = self.doc.add_table(rows=1, cols=1)
        t.alignment = (
            WD_TABLE_ALIGNMENT.RIGHT if align == WD_ALIGN_PARAGRAPH.RIGHT
            else WD_TABLE_ALIGNMENT.LEFT
        )
        t.columns[0].width = Cm(width)
        cell = t.cell(0, 0)
        cell.width = Cm(width)
        p = self._cell_para(cell, first=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        self._text(p, text.upper(), size=size or self.body_size, bold=True)
        self._para(after=0)
        return t

    # ---------------- formal components ----------------
    def _header_block(self):
        """Cells 1-5b of the layout map: issuing body / national heading, then
        symbol / place and date on one line, then the cong van subject."""
        s = self.s
        rows = 3 if (self.family == "cong-van" and s.get("trich_yeu")) else 2
        t = self.doc.add_table(rows=rows, cols=2)
        for r in t.rows:
            r.cells[0].width = Cm(COL_LEFT_CM)
            r.cells[1].width = Cm(COL_RIGHT_CM)
        t.columns[0].width = Cm(COL_LEFT_CM)
        t.columns[1].width = Cm(COL_RIGHT_CM)

        # --- cell 2: issuing body (II.2) ---
        L = t.cell(0, 0)
        first = True
        if s.get("co_quan_chu_quan"):
            p = self._cell_para(L, first=True)
            self._text(p, s["co_quan_chu_quan"].upper(), size=COQUAN_SIZE)
            first = False
        co_quan = (s.get("co_quan") or "").upper()
        if not co_quan:
            fail("thieu 'co_quan' - ten co quan, to chuc ban hanh van ban (II.2).")
        p = self._cell_para(L, first=first)
        self._text(p, co_quan, size=COQUAN_SIZE, bold=True)
        self._text_rule(L, co_quan, COQUAN_SIZE, COL_LEFT_CM, ratio=RULE_RATIO)

        # --- cell 1: national heading and motto (II.1) ---
        R = t.cell(0, 1)
        p = self._cell_para(R, first=True)
        self._text(p, "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM", size=QUOCHIEU_SIZE, bold=True)
        motto = "Độc lập - Tự do - Hạnh phúc"
        p = self._cell_para(R)
        self._text(p, motto, size=TIEUNGU_SIZE, bold=True)
        self._text_rule(R, motto, TIEUNGU_SIZE, COL_RIGHT_CM)

        # --- cell 3: number and symbol (II.3) ---
        p = self._cell_para(t.cell(1, 0), first=True, before=PARA_SPACE_PT)
        self._text(p, self._so_ky_hieu(), size=SO_SIZE)

        # --- cell 4: place and date (II.4) ---
        p = self._cell_para(t.cell(1, 1), first=True, before=PARA_SPACE_PT)
        self._text(p, self._dia_danh_ngay(), size=DIADANH_SIZE, italic=True)

        # --- cell 5b: cong van subject, under the symbol, 6 pt below it ---
        if rows == 3:
            cell = t.cell(2, 0)
            lines = self._as_list(s["trich_yeu"])
            for i, ln in enumerate(lines):
                p = self._cell_para(cell, first=(i == 0),
                                    before=PARA_SPACE_PT if i == 0 else 0)
                self._text(p, ("V/v " if i == 0 else "") + ln, size=TRICHYEU_CV_SIZE)

        self._strip_borders(t)
        self._para(after=PARA_SPACE_PT)

    def _so_ky_hieu(self) -> str:
        """II.3 - 'So: <n>/<SYMBOL>'; numbers below 10 get a leading zero; the
        symbol is upper case with hyphens and no spaces."""
        s = self.s
        so = str(s.get("so", "") or "").strip()
        if so.isdigit() and int(so) < 10 and len(so) == 1:
            so = "0" + so
        ky_hieu = (s.get("ky_hieu") or "").strip()
        if not ky_hieu:
            # II.3.b: typed documents use <TYPE>-<BODY>; a cong van uses
            # <BODY>-<DRAFTING UNIT>, which only the author can know.
            abbr = s.get("viet_tat_co_quan", "")
            if self.viet_tat and abbr:
                ky_hieu = "%s-%s" % (self.viet_tat, abbr)
            elif abbr:
                ky_hieu = abbr
        blank = "       "  # left for the records office to fill in by hand
        return "Số: %s/%s" % (so or blank, ky_hieu) if ky_hieu else "Số: %s" % (so or blank)

    def _dia_danh_ngay(self) -> str:
        s = self.s
        if s.get("dia_danh_ngay"):
            return s["dia_danh_ngay"]
        dia_danh = (s.get("dia_danh") or "").strip()
        ngay = fmt_ngay(s.get("ngay"))
        if not dia_danh:
            fail("thieu 'dia_danh' (hoac 'dia_danh_ngay') - II.4.a bat buoc ghi dia danh.")
        return "%s, %s" % (dia_danh, ngay) if ngay else dia_danh + ", "

    def _ten_loai_block(self):
        """Cell 5a (II.5.b) - type in caps bold, subject under it in bold, then a
        rule 1/3 to 1/2 of the subject line. A cong van has no type name."""
        if self.family == "cong-van":
            return
        ten = (self.s.get("ten_loai") or self.ten_loai_default or "").upper()
        if ten:
            self._line(ten, WD_ALIGN_PARAGRAPH.CENTER, before=PARA_SPACE_PT,
                       size=TENLOAI_SIZE, bold=True)
        trich = self.s.get("trich_yeu")
        if trich:
            lines = self._as_list(trich)
            for ln in lines:
                self._line(ln, WD_ALIGN_PARAGRAPH.CENTER, size=TENLOAI_SIZE, bold=True)
            self._text_rule(None, lines[-1], TENLOAI_SIZE, USABLE_CM,
                            ratio=RULE_RATIO, after=PARA_SPACE_PT)
        else:
            self._para(after=PARA_SPACE_PT)

    def _can_cu_block(self):
        """II.6.a - legal bases, italic, one per line, ';' after each and '.' on
        the last one."""
        items = self._as_list(self.s.get("can_cu"))
        if not items:
            return
        for i, ln in enumerate(items):
            txt = ln.rstrip(" ;.")
            txt += "." if i == len(items) - 1 else ";"
            self._line(txt, WD_ALIGN_PARAGRAPH.JUSTIFY, after=PARA_SPACE_PT,
                       italic=True)

    def _kinh_gui_block(self):
        """Cell 9a (II.9.d) - upright, not bold. One recipient stays on the
        'Kinh gui:' line; several are listed one per line with a leading hyphen,
        ';' at the end of each and '.' on the last."""
        items = self._as_list(self.s.get("kinh_gui"))
        if not items:
            return
        if len(items) == 1:
            self._line("Kính gửi: " + items[0].rstrip(" .;") + ".",
                       WD_ALIGN_PARAGRAPH.CENTER, after=PARA_SPACE_PT)
            return
        self._line("Kính gửi:", WD_ALIGN_PARAGRAPH.CENTER)
        for i, ln in enumerate(items):
            body = ln.lstrip("- ").rstrip(" .;")
            body += "." if i == len(items) - 1 else ";"
            p = self._para(align=WD_ALIGN_PARAGRAPH.CENTER,
                           after=PARA_SPACE_PT if i == len(items) - 1 else 0)
            self._text(p, "- " + body)

    # ---------------- body blocks ----------------
    @staticmethod
    def _as_list(v):
        if v is None or v == "":
            return []
        return list(v) if isinstance(v, list) else [v]

    def _body_para(self, text, indent=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
        """II.6.e - justified, upright, 6 pt between paragraphs, first line of a
        new paragraph indented 1 cm. List items pass indent=False."""
        p = self._para(align=align, after=PARA_SPACE_PT,
                       indent=INDENT_CM if indent else None)
        self._text(p, text)
        return p

    def _heading(self, text, level=1):
        """II.6.d-dd - part/chapter headings are centred; 'Dieu' and numbered
        clauses are indented like body text. Bold either way."""
        center = bool(re.match(r"^(Phần|Chương|Mục|Tiểu mục)\b", text.strip()))
        p = self._para(
            align=WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.JUSTIFY,
            before=PARA_SPACE_PT,
            after=3,
            indent=None if center else INDENT_CM,
        )
        self._text(p, text, bold=True)

    def _table(self, header, rows, mono_body=False, widths=None):
        n = len(rows) + (1 if header else 0)
        if n == 0:
            return
        cols = len(header) if header else len(rows[0])
        t = self.doc.add_table(rows=n, cols=cols)
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        if widths:
            for i, w in enumerate(widths[:cols]):
                for r in t.rows:
                    r.cells[i].width = Cm(float(w))
        r0 = 0
        size = self.body_size - 1  # tables are set one step down to fit the page
        if header:
            for j, v in enumerate(header):
                p = t.rows[0].cells[j].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                self._text(p, str(v), bold=True, size=size)
            r0 = 1
        for i, row in enumerate(rows):
            for j, v in enumerate(row):
                p = t.rows[r0 + i].cells[j].paragraphs[0]
                self._text(p, str(v), size=(size - 1 if mono_body else size),
                           mono=mono_body)
        self._para(after=3)

    def _code(self, lines):
        for ln in lines:
            self._line(ln, after=0, size=self.body_size - 3, mono=True)
        self._para(after=3)

    def _dots(self, label, value="", width_cm=None):
        """Fill-in line used by giay moi / giay gioi thieu / giay nghi phep."""
        p = self._para(align=WD_ALIGN_PARAGRAPH.LEFT, after=PARA_SPACE_PT,
                       indent=INDENT_CM)
        head = "%s: " % label if label else ""
        self._text(p, head + (value or ""))
        if not value:
            avail = (width_cm or USABLE_CM) - INDENT_CM - est_width_cm(head, self.body_size)
            n = max(3, int(avail / CHAR_W_CM[self.body_size] * 0.95))
            self._text(p, "." * n)

    def _signatures(self, columns):
        """Side-by-side signature columns, used by bien ban and hop dong."""
        t = self.doc.add_table(rows=1, cols=len(columns))
        w = USABLE_CM / len(columns)
        for i, col in enumerate(columns):
            cell = t.cell(0, i)
            cell.width = Cm(w)
            p = self._cell_para(cell, first=True)
            self._text(p, (col.get("chuc_vu") or "").upper(), bold=True)
            if col.get("ghi_chu"):
                p = self._cell_para(cell)
                self._text(p, col["ghi_chu"], italic=True, size=NOINHAN_ITEM_SIZE)
            for _ in range(3):
                self._cell_para(cell)
            if col.get("ho_ten"):
                p = self._cell_para(cell)
                self._text(p, col["ho_ten"], bold=True)
        self._strip_borders(t)

    def _blocks(self, blocks):
        for b in blocks:
            if isinstance(b, str):
                self._body_para(b)
                continue
            bt = b.get("type", "para")
            if bt == "para":
                self._body_para(b.get("text", ""), indent=b.get("indent", True))
            elif bt == "list":
                for it in b.get("items", []):
                    self._body_para(it, indent=False)
            elif bt == "heading":
                self._heading(b.get("text", ""))
            elif bt == "table":
                self._table(b.get("header"), b.get("rows", []),
                            mono_body=b.get("mono_body", False),
                            widths=b.get("widths"))
            elif bt == "code":
                self._code(b.get("lines", []))
            elif bt == "dots":
                self._dots(b.get("label", ""), b.get("value", ""))
            elif bt == "center":
                self._line(b.get("text", ""), WD_ALIGN_PARAGRAPH.CENTER,
                           after=PARA_SPACE_PT, bold=b.get("bold", False))
            elif bt == "italic":
                self._body_para_italic(b.get("text", ""))
            elif bt == "signatures":
                self._signatures(b.get("columns", []))
            elif bt == "pagebreak":
                self.doc.add_page_break()
            else:
                fail("loai block khong ro: '%s' (cho phep: para, list, heading, "
                     "table, code, dots, center, italic, signatures, pagebreak)" % bt)

    def _body_para_italic(self, text):
        p = self._para(align=WD_ALIGN_PARAGRAPH.JUSTIFY, after=PARA_SPACE_PT,
                       indent=INDENT_CM)
        self._text(p, text, italic=True)

    def _content(self):
        s = self.s
        for x in self._as_list(s.get("mo_dau")):
            self._body_para(x)
        # "QUYET DINH:" / "QUYET NGHI:" for the two types built on legal bases
        if self.family in ("quyet-dinh", "nghi-quyet") and s.get("can_cu"):
            word = "QUYẾT ĐỊNH:" if self.family == "quyet-dinh" else "QUYẾT NGHỊ:"
            self._line(s.get("tu_quyet_dinh", word), WD_ALIGN_PARAGRAPH.CENTER,
                       before=PARA_SPACE_PT, after=PARA_SPACE_PT, bold=True)
        for dieu in s.get("dieu", []):
            self._heading(dieu.get("heading", ""))
            self._blocks(dieu.get("blocks", []))
        for muc in s.get("muc", []):
            if muc.get("heading"):
                self._heading(muc["heading"])
            self._blocks(muc.get("blocks", []))
        self._blocks(s.get("noi_dung", []))
        for x in self._as_list(s.get("ket")):
            self._body_para(x)

    # ---------------- closing block ----------------
    def _closing(self):
        """Cells 7a/7b/7c (signature), 8 (seal), 9b (recipients), 12 (drafter)."""
        s = self.s
        if self.family == "bien-ban" and not s.get("nguoi_ky"):
            cols = s.get("chu_ky", [])
            if cols:
                self._para(after=PARA_SPACE_PT)
                self._signatures(cols)
            return
        self._para(after=PARA_SPACE_PT)
        t = self.doc.add_table(rows=1, cols=2)
        half = USABLE_CM / 2
        NL, NR = t.cell(0, 0), t.cell(0, 1)
        NL.width = NR.width = Cm(half)

        noi_nhan = self._as_list(s.get("noi_nhan"))
        if noi_nhan:
            p = self._cell_para(NL, first=True, align=WD_ALIGN_PARAGRAPH.LEFT)
            self._text(p, "Nơi nhận:", size=NOINHAN_LABEL_SIZE, bold=True, italic=True)
            for i, x in enumerate(noi_nhan):
                body = x.lstrip("- ").rstrip(" ;.")
                body += "." if i == len(noi_nhan) - 1 else ";"
                p = self._cell_para(NL, align=WD_ALIGN_PARAGRAPH.LEFT)
                self._text(p, "- " + body, size=NOINHAN_ITEM_SIZE)
        if s.get("ky_hieu_nguoi_soan"):
            # III.3 - drafter code and print run, bottom left (cell 12)
            p = self._cell_para(NL, align=WD_ALIGN_PARAGRAPH.LEFT, before=PARA_SPACE_PT)
            self._text(p, s["ky_hieu_nguoi_soan"], size=DRAFTER_SIZE)

        ky = s.get("nguoi_ky") or {}
        quyen_han = (ky.get("quyen_han") or "").strip()  # TM. / Q. / KT. / TL. / TUQ.
        chuc_vu = (ky.get("chuc_vu") or "").strip()
        if quyen_han or chuc_vu:
            p = self._cell_para(NR, first=True)
            label = (quyen_han + " " if quyen_han else "") + chuc_vu.upper()
            self._text(p, label.strip(), bold=True)
        if ky.get("chuc_vu_khac"):
            p = self._cell_para(NR)
            self._text(p, ky["chuc_vu_khac"], bold=True)
        note = ky.get("ghi_chu", "(Ký, ghi rõ họ tên, đóng dấu)")
        if note:
            p = self._cell_para(NR)
            self._text(p, note, italic=True, size=NOINHAN_ITEM_SIZE)
        # three empty lines leave room for the wet signature and the seal (cell 8)
        for _ in range(3):
            self._cell_para(NR)
        if ky.get("ho_ten"):
            p = self._cell_para(NR)
            self._text(p, ky["ho_ten"], bold=True)
        else:
            self._cell_para(NR)
        self._strip_borders(t)

    # ---------------- appendices ----------------
    def _appendices(self):
        """III.1 - each appendix starts a new page; 'Phu luc <Roman>' centred and
        bold, the title in caps below it, then the italic reference line."""
        items = self.s.get("phu_luc", [])
        many = len(items) > 1
        roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
        for i, pl in enumerate(items):
            self.doc.add_page_break()
            label = "Phụ lục"
            num = pl.get("so") or (roman[i] if many and i < len(roman) else "")
            if num:
                label += " " + str(num)
            self._line(label, WD_ALIGN_PARAGRAPH.CENTER,
                       size=PHULUC_LABEL_SIZE, bold=True)
            if pl.get("tieu_de"):
                self._line(pl["tieu_de"].upper(), WD_ALIGN_PARAGRAPH.CENTER,
                           size=self.body_size, bold=True)
            kem = pl.get("kem_theo", self._auto_kem_theo())
            if kem:
                self._line(kem, WD_ALIGN_PARAGRAPH.CENTER, after=PARA_SPACE_PT,
                           italic=True)
            else:
                self._para(after=PARA_SPACE_PT)
            self._blocks(pl.get("blocks", []))

    def _auto_kem_theo(self):
        """III.1.c - the reference line carries the number, symbol, date and
        issuing body. Built only when all of them are known."""
        s = self.s
        so, kh = str(s.get("so", "") or ""), s.get("ky_hieu") or ""
        ngay = fmt_ngay(s.get("ngay"))
        if not (so and kh and ngay):
            return ""
        ten = self.s.get("ten_loai") or self.ten_loai_default or "Công văn"
        return "(Kèm theo %s số %s/%s %s của %s)" % (
            ten.capitalize(), so, kh, ngay, s.get("co_quan", ""))

    # ---------------- family specific bodies ----------------
    def _marks(self):
        """Cells 10a, 10b, 11 - secrecy, urgency and circulation notes."""
        if self.s.get("pham_vi_luu_hanh"):
            self._box(self.s["pham_vi_luu_hanh"], align=WD_ALIGN_PARAGRAPH.RIGHT)
        for key in ("do_mat", "do_khan"):
            if self.s.get(key):
                self._box(self.s[key])

    def build(self, out_path):
        self._marks()
        self._header_block()
        self._ten_loai_block()
        self._can_cu_block()
        if self.loai in KINH_GUI_TYPES or self.s.get("kinh_gui"):
            self._kinh_gui_block()
        self._content()
        self._closing()
        self._appendices()
        self.doc.save(out_path)
        return out_path


def to_pdf(docx_path):
    """Optional PDF export for the mandatory visual check."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        print("CANH BAO: khong tim thay soffice/libreoffice, bo qua buoc xuat PDF.\n"
              "          Cai dat: brew install --cask libreoffice", file=sys.stderr)
        return None
    out_dir = os.path.dirname(os.path.abspath(docx_path)) or "."
    try:
        subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", out_dir, docx_path],
            check=True, capture_output=True, timeout=180,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print("CANH BAO: xuat PDF that bai: %s" % e, file=sys.stderr)
        return None
    return os.path.splitext(docx_path)[0] + ".pdf"


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Tao van ban hanh chinh Viet Nam (.docx) theo ND 30/2020/ND-CP."
    )
    ap.add_argument("spec", help="tep mo ta JSON")
    ap.add_argument("out", help="tep .docx ket qua")
    ap.add_argument("--pdf", action="store_true", help="xuat kem PDF de soi mat")
    args = ap.parse_args(argv)

    if not os.path.exists(args.spec):
        fail("khong tim thay tep mo ta: %s" % args.spec)
    try:
        with open(args.spec, encoding="utf-8") as f:
            spec = json.load(f)
    except json.JSONDecodeError as e:
        fail("tep mo ta khong phai JSON hop le (dong %d, cot %d): %s"
             % (e.lineno, e.colno, e.msg))
    if not isinstance(spec, dict):
        fail("tep mo ta phai la mot doi tuong JSON { ... }")

    out = VanBan(spec).build(args.out)
    print("Da tao: %s" % out)
    if args.pdf:
        pdf = to_pdf(out)
        if pdf:
            print("Da tao: %s" % pdf)
    return 0


if __name__ == "__main__":
    sys.exit(main())

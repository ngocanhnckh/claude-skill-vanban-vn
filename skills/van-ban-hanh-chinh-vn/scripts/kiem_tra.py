# -*- coding: utf-8 -*-
"""Check a spec.json against the rules of Decree 30/2020/ND-CP before rendering.

Usage:
    python kiem_tra.py <spec.json> [<spec2.json> ...]

Exit code 0 means no blocking error (warnings may still be printed), 1 means at
least one error. No third-party dependency: this runs on a bare Python 3.

Each message names the clause of Appendix I it comes from, so the author can
check the source instead of trusting this script.
"""
from __future__ import annotations

import json
import os
import re
import sys

EM_DASH = "—"

TYPE_ABBR = {
    "nghi-quyet": "NQ", "quyet-dinh": "QĐ", "chi-thi": "CT", "quy-che": "QC",
    "quy-dinh": "QyĐ", "thong-cao": "TC", "thong-bao": "TB", "huong-dan": "HD",
    "chuong-trinh": "CTr", "ke-hoach": "KH", "phuong-an": "PA", "de-an": "ĐA",
    "du-an": "DA", "bao-cao": "BC", "bien-ban": "BB", "to-trinh": "TTr",
    "hop-dong": "HĐ", "cong-van": "", "cong-dien": "CĐ", "ban-ghi-nho": "BGN",
    "ban-thoa-thuan": "BTT", "giay-uy-quyen": "GUQ", "giay-moi": "GM",
    "giay-gioi-thieu": "GGT", "giay-nghi-phep": "GNP", "phieu-gui": "PG",
    "phieu-chuyen": "PC", "phieu-bao": "PB", "thu-cong": "",
}

# II.9.b - only these carry a "Kinh gui" block. Giay moi puts the invitee in the
# body instead (Appendix III, form 1.7).
NEED_KINH_GUI = {"cong-van", "to-trinh", "bao-cao", "cong-dien", "thu-cong"}
NEED_CAN_CU = {"quyet-dinh", "nghi-quyet"}
NO_TEN_LOAI = {"cong-van", "thu-cong"}
# Forms 1.8, 1.9 and 1.10 have no subject line and no "Noi nhan" block.
NO_TRICH_YEU = {"giay-gioi-thieu", "giay-nghi-phep"}
NO_NOI_NHAN = {"bien-ban", "giay-nghi-phep"}

QUYEN_HAN = {"TM.", "Q.", "KT.", "TL.", "TUQ."}
DO_MAT = {"MẬT", "TỐI MẬT", "TUYỆT MẬT"}
DO_KHAN = {"KHẨN", "THƯỢNG KHẨN", "HOẢ TỐC", "HỎA TỐC"}

TOP_KEYS = {
    "loai", "ten_loai", "co_quan", "co_quan_chu_quan", "viet_tat_co_quan",
    "so", "ky_hieu", "dia_danh", "ngay", "dia_danh_ngay", "trich_yeu", "can_cu",
    "kinh_gui", "mo_dau", "muc", "dieu", "noi_dung", "ket", "noi_nhan",
    "nguoi_ky", "chu_ky", "tu_quyet_dinh", "phu_luc", "do_mat", "do_khan",
    "pham_vi_luu_hanh", "ky_hieu_nguoi_soan", "lien_he", "so_trang", "co_chu",
    "ghi_chu_noi_bo",
}
BLOCK_TYPES = {"para", "list", "heading", "table", "code", "dots", "center",
               "italic", "signatures", "pagebreak"}


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.notes = []

    def err(self, where, msg):
        self.errors.append((where, msg))

    def warn(self, where, msg):
        self.warnings.append((where, msg))

    def note(self, where, msg):
        self.notes.append((where, msg))

    def print(self, label):
        print("=== %s ===" % label)
        for tag, items in (("LOI", self.errors), ("CANH BAO", self.warnings),
                           ("GHI CHU", self.notes)):
            for where, msg in items:
                print("%-9s %-24s %s" % (tag, where, msg))
        if not (self.errors or self.warnings or self.notes):
            print("Khong phat hien van de.")
        print("-> %d loi, %d canh bao" % (len(self.errors), len(self.warnings)))
        return 1 if self.errors else 0


def walk_strings(node, path="$"):
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from walk_strings(v, "%s.%s" % (path, k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_strings(v, "%s[%d]" % (path, i))


def as_list(v):
    if v is None or v == "":
        return []
    return list(v) if isinstance(v, list) else [v]


def check_blocks(blocks, where, r):
    for i, b in enumerate(blocks):
        w = "%s[%d]" % (where, i)
        if isinstance(b, str):
            continue
        if not isinstance(b, dict):
            r.err(w, "block phai la doi tuong JSON hoac mot chuoi.")
            continue
        bt = b.get("type", "para")
        if bt not in BLOCK_TYPES:
            r.err(w, "type '%s' khong hop le. Cho phep: %s"
                  % (bt, ", ".join(sorted(BLOCK_TYPES))))
            continue
        if bt == "para" and not b.get("text"):
            r.err(w, "block para thieu 'text'.")
        if bt == "list" and not b.get("items"):
            r.err(w, "block list thieu 'items'.")
        if bt == "table":
            rows = b.get("rows")
            if not rows:
                r.err(w, "block table thieu 'rows'.")
            else:
                ncol = len(b["header"]) if b.get("header") else len(rows[0])
                for j, row in enumerate(rows):
                    if len(row) != ncol:
                        r.err("%s.rows[%d]" % (w, j),
                              "co %d o nhung bang co %d cot." % (len(row), ncol))
        if bt == "code" and not b.get("lines"):
            r.err(w, "block code thieu 'lines'.")


def check(spec, r):
    # --- type ---
    loai = spec.get("loai")
    if not loai:
        r.err("$.loai", "thieu 'loai'. Dung mot trong 29 loai tai Dieu 7 ND 30/2020.")
        return
    if loai not in TYPE_ABBR:
        r.err("$.loai", "'%s' khong thuoc 29 loai tai Dieu 7. Hop le: %s"
              % (loai, ", ".join(sorted(TYPE_ABBR))))
        return

    # --- em dash (II.1.b, II.9.d use the hyphen) ---
    for path, text in walk_strings(spec):
        if EM_DASH in text:
            r.err(path, "chua dau gach dai U+2014, phai thay bang dau gach ngang '-'.")

    # --- unknown keys: catches typos before they silently disappear ---
    for k in spec:
        if k not in TOP_KEYS:
            r.warn("$." + k, "khoa khong duoc dung den - kiem tra lai chinh ta.")

    # --- issuing body (II.2) ---
    if not spec.get("co_quan"):
        r.err("$.co_quan", "thieu ten co quan, to chuc ban hanh (II.2.a).")
    elif spec["co_quan"] != spec["co_quan"].upper():
        r.note("$.co_quan", "se duoc in hoa tu dong (II.2.b).")

    # --- number and symbol (II.3) ---
    so = str(spec.get("so", "") or "").strip()
    if not so:
        r.note("$.so", "de trong - chua cho Van thu dien so khi dang ky van ban.")
    elif not so.isdigit():
        r.err("$.so", "'%s' phai la chu so A Rap (II.3.a)." % so)
    elif len(so) == 1:
        r.note("$.so", "so nho hon 10 se duoc them so 0 phia truoc (II.3.c).")

    ky_hieu = (spec.get("ky_hieu") or "").strip()
    if not ky_hieu and not spec.get("viet_tat_co_quan"):
        r.warn("$.ky_hieu", "thieu ky hieu. Van ban co ten loai: <VIET TAT LOAI>-"
                            "<VIET TAT CO QUAN>; cong van: <CO QUAN>-<DON VI SOAN "
                            "THAO> (II.3.b).")
    if ky_hieu:
        if " " in ky_hieu:
            r.err("$.ky_hieu", "khong duoc co dau cach; cac nhom chu viet tat noi "
                               "bang dau gach noi '-' (II.3.c).")
        abbr = TYPE_ABBR[loai]
        # II.3.c - upper case, except inside an abbreviation that the decree itself
        # writes with lower case letters (QyD, CTr, TTr, BGN...).
        rest = ky_hieu[len(abbr):] if abbr and ky_hieu.startswith(abbr) else ky_hieu
        if rest != rest.upper():
            r.warn("$.ky_hieu", "ky hieu trinh bay bang chu in hoa (II.3.c).")
        if abbr and not ky_hieu.upper().startswith(abbr.upper()):
            r.warn("$.ky_hieu", "loai '%s' thuong co ky hieu bat dau bang '%s' "
                                "(Phu luc III)." % (loai, abbr))
        if loai in NO_TEN_LOAI and re.match(r"^(CV|TC)-", ky_hieu.upper()):
            r.warn("$.ky_hieu", "ky hieu cong van khong gom ten loai: dung "
                                "<CO QUAN>-<DON VI SOAN THAO> (II.3.b).")

    # --- place and date (II.4) ---
    if not spec.get("dia_danh") and not spec.get("dia_danh_ngay"):
        r.err("$.dia_danh", "thieu dia danh - la ten goi chinh thuc cua don vi "
                            "hanh chinh noi co quan dong tru so (II.4.a).")
    ngay = spec.get("ngay")
    if not ngay and not spec.get("dia_danh_ngay"):
        r.err("$.ngay", "thieu ngay ban hanh (II.4.b).")
    if ngay and not re.match(r"^\d{4}-\d{1,2}-\d{1,2}$|^\d{1,2}[/-]\d{1,2}[/-]\d{4}$",
                             str(ngay).strip()):
        r.warn("$.ngay", "nen ghi dang YYYY-MM-DD de script tu dinh dang theo "
                         "II.4.b; gia tri hien tai duoc giu nguyen.")

    # --- type name and subject (II.5) ---
    if loai in NO_TEN_LOAI:
        if spec.get("ten_loai"):
            r.err("$.ten_loai", "cong van KHONG co ten loai (II.5.b). Dat trich yeu "
                                "vao 'trich_yeu', script in sau chu 'V/v'.")
        if not spec.get("trich_yeu"):
            r.warn("$.trich_yeu", "cong van nen co trich yeu sau 'V/v' (II.5.b).")
    else:
        if not spec.get("trich_yeu") and loai not in NO_TRICH_YEU:
            r.warn("$.trich_yeu", "van ban co ten loai nen co trich yeu dat ngay "
                                  "duoi ten loai (II.5.b).")

    # --- legal bases (II.6.a) ---
    can_cu = as_list(spec.get("can_cu"))
    if loai in NEED_CAN_CU and not can_cu:
        r.warn("$.can_cu", "loai '%s' thuong co phan can cu phap ly (II.6.a)." % loai)
    if can_cu and loai not in NEED_CAN_CU:
        r.note("$.can_cu", "phan can cu se duoc in nghieng theo II.6.a.")

    # --- Dieu / khoan / diem (II.6.dd) ---
    for i, d in enumerate(spec.get("dieu", [])):
        h = (d.get("heading") or "").strip()
        if not re.match(r"^Điều\s+\d+\.", h):
            r.warn("$.dieu[%d].heading" % i,
                   "nen co dang 'Dieu <so A Rap>. <tieu de>' (II.6.dd). Dang co: %r" % h)
        check_blocks(d.get("blocks", []), "$.dieu[%d].blocks" % i, r)

    # --- recipients (II.9) ---
    kinh_gui = as_list(spec.get("kinh_gui"))
    if loai in NEED_KINH_GUI and not kinh_gui:
        r.warn("$.kinh_gui", "loai '%s' co phan 'Kinh gui' (o so 9a, II.9.b)." % loai)
    if kinh_gui and loai not in NEED_KINH_GUI:
        r.note("$.kinh_gui", "II.9.b chi quy dinh 'Kinh gui' cho To trinh, Bao cao "
                             "gui cap tren va Cong van; van se duoc in.")
    for i, x in enumerate(kinh_gui):
        if x.strip().startswith("-"):
            r.note("$.kinh_gui[%d]" % i, "khong can tu them '-', script tu them.")

    noi_nhan = as_list(spec.get("noi_nhan"))
    if not noi_nhan:
        if loai not in NO_NOI_NHAN:
            r.warn("$.noi_nhan", "thieu noi nhan (o so 9b, II.9.c): phai co phan liet "
                                 "ke va dong cuoi 'Luu: VT, ...'.")
    else:
        last = noi_nhan[-1]
        if "Lưu" not in last:
            r.err("$.noi_nhan", "dong cuoi phai la 'Luu: VT, <don vi soan thao>, "
                                "<so ban>.' (II.9.d).")
        if loai in NEED_KINH_GUI and kinh_gui:
            first = noi_nhan[0].lstrip("- ").strip().rstrip(";.")
            if first.lower() != "như trên":
                r.warn("$.noi_nhan[0]", "voi To trinh, Bao cao va Cong van, dong dau "
                                        "cua Noi nhan la 'Nhu tren' (II.9.b).")

    # --- signer (II.7) ---
    ky = spec.get("nguoi_ky") or {}
    chu_ky = spec.get("chu_ky") or []
    if not ky and not chu_ky:
        r.err("$.nguoi_ky", "thieu khoi chuc vu, ho ten nguoi ky (II.7).")
    if ky:
        if not ky.get("chuc_vu"):
            r.err("$.nguoi_ky.chuc_vu", "phai ghi chuc vu lanh dao chinh thuc cua "
                                        "nguoi ky (II.7.c).")
        qh = (ky.get("quyen_han") or "").strip()
        if qh and qh not in QUYEN_HAN:
            r.err("$.nguoi_ky.quyen_han",
                  "'%s' khong hop le. Chi dung: %s (II.7.b)."
                  % (qh, ", ".join(sorted(QUYEN_HAN))))
        if not ky.get("ho_ten"):
            r.note("$.nguoi_ky.ho_ten", "de trong - chua cho nguoi co tham quyen ky "
                                        "va ghi ro ho ten.")
        for bad in ("TS.", "ThS.", "PGS.", "GS.", "TS ", "BS."):
            if bad in (ky.get("ho_ten") or ""):
                r.warn("$.nguoi_ky.ho_ten", "khong ghi hoc ham, hoc vi truoc ho ten "
                                            "nguoi ky (II.7.c).")
                break

    # --- optional stamps (III.2) ---
    if spec.get("do_mat") and spec["do_mat"].upper() not in DO_MAT:
        r.err("$.do_mat", "chi co 3 muc: MAT, TOI MAT, TUYET MAT (III.2.a).")
    if spec.get("do_khan") and spec["do_khan"].upper() not in DO_KHAN:
        r.err("$.do_khan", "chi co 3 muc: KHAN, THUONG KHAN, HOA TOC (III.2.b).")

    # --- font size (II.6.e) ---
    if spec.get("co_chu") not in (None, 13, 14):
        r.err("$.co_chu", "co chu than van ban chi 13 hoac 14 (II.6.e).")

    # --- body blocks ---
    for i, m in enumerate(spec.get("muc", [])):
        check_blocks(m.get("blocks", []), "$.muc[%d].blocks" % i, r)
    check_blocks(spec.get("noi_dung", []), "$.noi_dung", r)
    for i, pl in enumerate(spec.get("phu_luc", [])):
        check_blocks(pl.get("blocks", []), "$.phu_luc[%d].blocks" % i, r)
        if not pl.get("tieu_de"):
            r.warn("$.phu_luc[%d].tieu_de" % i, "phu luc nen co tieu de (III.1.b).")
    if len(spec.get("phu_luc", [])) > 1:
        r.note("$.phu_luc", "tu 2 phu luc tro len phai danh so thu tu bang chu so "
                            "La Ma (III.1.a) - script tu danh I, II, III...")


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    rc = 0
    for path in argv[1:]:
        if not os.path.exists(path):
            print("LOI       %-24s khong tim thay tep." % path)
            rc = 1
            continue
        try:
            with open(path, encoding="utf-8") as f:
                spec = json.load(f)
        except json.JSONDecodeError as e:
            print("LOI       %-24s JSON khong hop le (dong %d, cot %d): %s"
                  % (path, e.lineno, e.colno, e.msg))
            rc = 1
            continue
        r = Report()
        if not isinstance(spec, dict):
            r.err("$", "tep mo ta phai la mot doi tuong JSON { ... }")
        else:
            check(spec, r)
        rc |= r.print(os.path.basename(path))
        print()
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))

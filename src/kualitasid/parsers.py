"""Parser dan validator untuk format data khas Indonesia."""
from __future__ import annotations

import difflib
import re
from datetime import date
from typing import Optional

BULAN = {
    "januari": 1, "jan": 1, "februari": 2, "feb": 2, "pebruari": 2,
    "maret": 3, "mar": 3, "april": 4, "apr": 4, "mei": 5,
    "juni": 6, "jun": 6, "juli": 7, "jul": 7,
    "agustus": 8, "agu": 8, "agt": 8, "ags": 8, "agus": 8,
    "september": 9, "sep": 9, "sept": 9, "oktober": 10, "okt": 10,
    "november": 11, "nov": 11, "nop": 11, "desember": 12, "des": 12,
}

PROVINSI = {
    "11": "Aceh", "12": "Sumatera Utara", "13": "Sumatera Barat", "14": "Riau",
    "15": "Jambi", "16": "Sumatera Selatan", "17": "Bengkulu", "18": "Lampung",
    "19": "Kepulauan Bangka Belitung", "21": "Kepulauan Riau",
    "31": "DKI Jakarta", "32": "Jawa Barat", "33": "Jawa Tengah",
    "34": "DI Yogyakarta", "35": "Jawa Timur", "36": "Banten", "51": "Bali",
    "52": "Nusa Tenggara Barat", "53": "Nusa Tenggara Timur",
    "61": "Kalimantan Barat", "62": "Kalimantan Tengah",
    "63": "Kalimantan Selatan", "64": "Kalimantan Timur",
    "65": "Kalimantan Utara", "71": "Sulawesi Utara", "72": "Sulawesi Tengah",
    "73": "Sulawesi Selatan", "74": "Sulawesi Tenggara", "75": "Gorontalo",
    "76": "Sulawesi Barat", "81": "Maluku", "82": "Maluku Utara",
    "91": "Papua Barat", "92": "Papua Barat Daya", "93": "Papua Selatan",
    "94": "Papua Tengah", "95": "Papua Pegunungan", "96": "Papua",
}

_ALIAS_PROVINSI = {
    "nad": "Aceh", "nanggroe aceh darussalam": "Aceh",
    "jakarta": "DKI Jakarta", "dki": "DKI Jakarta",
    "jogja": "DI Yogyakarta", "yogyakarta": "DI Yogyakarta",
    "diy": "DI Yogyakarta", "di yogyakarta": "DI Yogyakarta",
    "d.i. yogyakarta": "DI Yogyakarta", "babel": "Kepulauan Bangka Belitung",
    "bangka belitung": "Kepulauan Bangka Belitung", "kepri": "Kepulauan Riau",
    "sumut": "Sumatera Utara", "sumbar": "Sumatera Barat",
    "sumsel": "Sumatera Selatan", "jabar": "Jawa Barat", "jateng": "Jawa Tengah",
    "jatim": "Jawa Timur", "ntb": "Nusa Tenggara Barat",
    "ntt": "Nusa Tenggara Timur", "kalbar": "Kalimantan Barat",
    "kalteng": "Kalimantan Tengah", "kalsel": "Kalimantan Selatan",
    "kaltim": "Kalimantan Timur", "kaltara": "Kalimantan Utara",
    "sulut": "Sulawesi Utara", "sulteng": "Sulawesi Tengah",
    "sulsel": "Sulawesi Selatan", "sultra": "Sulawesi Tenggara",
    "sulbar": "Sulawesi Barat",
}


def _kosong(v) -> bool:
    if v is None or type(v).__name__ == "NAType":
        return True
    return (isinstance(v, float) and v != v) or str(v).strip() == ""


def parse_rupiah(v) -> Optional[float]:
    """'Rp 1.500.000,50' -> 1500000.5 ; '1,5 jt' -> 1500000 ; '500rb' -> 500000."""
    if _kosong(v):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).lower().strip()
    s = re.sub(r"\b(rp|idr)\.?", "", s).replace(" ", "")
    m = re.fullmatch(r"(-?[\d.,]+)(rb|ribu|k|jt|juta|m|miliar|milyar|t|triliun)?", s)
    if not m:
        return None
    angka, suf = m.groups()
    kali = {"rb": 1e3, "ribu": 1e3, "k": 1e3, "jt": 1e6, "juta": 1e6,
            "m": 1e9, "miliar": 1e9, "milyar": 1e9, "t": 1e12, "triliun": 1e12}.get(suf, 1)
    try:
        if suf:  # '1,5jt' atau '1.5jt' -> desimal
            angka = angka.replace(",", ".")
            if angka.count(".") > 1:
                angka = angka.replace(".", "")
        else:  # format Indonesia: titik ribuan, koma desimal
            if "," in angka:
                angka = angka.replace(".", "").replace(",", ".")
            elif re.fullmatch(r"-?\d{1,3}(\.\d{3})+", angka):
                angka = angka.replace(".", "")
        return float(angka) * kali
    except ValueError:
        return None


def parse_tanggal(v) -> Optional[date]:
    """'17 Agustus 2026', '17-08-2026', '17/8/26' -> date."""
    if _kosong(v):
        return None
    if isinstance(v, date):
        return v
    s = str(v).strip().lower().replace(",", " ")
    s = re.sub(r"\s+", " ", s)
    d = m = y = None
    r = re.fullmatch(r"(\d{1,2}) ([a-z]+)\.? (\d{2,4})", s)
    if r and r.group(2) in BULAN:
        d, m, y = int(r.group(1)), BULAN[r.group(2)], int(r.group(3))
    else:
        r = re.fullmatch(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{2,4})", s)
        if r:
            d, m, y = int(r.group(1)), int(r.group(2)), int(r.group(3))
        else:
            r = re.fullmatch(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", s)
            if r:
                y, m, d = int(r.group(1)), int(r.group(2)), int(r.group(3))
    if d is None:
        return None
    if y < 100:
        y += 2000 if y < 50 else 1900
    try:
        return date(y, m, d)
    except ValueError:
        return None


def normalize_telepon(v) -> Optional[str]:
    """'0812-3456-7890' -> '+6281234567890'. None bila tidak valid."""
    if _kosong(v):
        return None
    s = re.sub(r"[^\d+]", "", str(v))
    if s.startswith("+62"):
        s = s[3:]
    elif s.startswith("62"):
        s = s[2:]
    elif s.startswith("0"):
        s = s[1:]
    else:
        return None
    if not s.isdigit() or not s.startswith("8") or not 9 <= len(s) <= 12:
        return None
    return "+62" + s


def validate_nik(v) -> bool:
    """Cek struktur NIK 16 digit: kode provinsi, tanggal lahir (+40 untuk perempuan)."""
    if _kosong(v):
        return False
    s = re.sub(r"\D", "", str(v))
    if len(s) != 16 or s[:2] not in PROVINSI or s[2:6] == "0000":
        return False
    hari, bulan, tahun = int(s[6:8]), int(s[8:10]), int(s[10:12])
    if hari > 40:
        hari -= 40
    try:
        date(2000 + tahun, bulan, hari)
    except ValueError:
        return False
    return True


def normalize_provinsi(v, cutoff: float = 0.8) -> Optional[str]:
    """'jabar', 'Jawa barat ', 'D.I. Yogyakarta' -> nama baku."""
    if _kosong(v):
        return None
    s = re.sub(r"^(provinsi|prov\.?)\s+", "", str(v).strip().lower())
    s = re.sub(r"\s+", " ", s)
    if s in _ALIAS_PROVINSI:
        return _ALIAS_PROVINSI[s]
    baku = {p.lower(): p for p in PROVINSI.values()}
    if s in baku:
        return baku[s]
    cocok = difflib.get_close_matches(s, list(baku), n=1, cutoff=cutoff)
    return baku[cocok[0]] if cocok else None


def info_nik(v) -> Optional[dict]:
    """Uraikan NIK yang strukturnya valid. None bila tidak valid.

    Hanya isi yang tertanam di NIK: kode provinsi, tanggal lahir
    (tanpa abad, hanya 2 digit tahun), dan jenis kelamin.
    """
    if not validate_nik(v):
        return None
    s = re.sub(r"\D", "", str(v))
    hari = int(s[6:8])
    perempuan = hari > 40
    return {
        "kode_provinsi": s[:2],
        "provinsi": PROVINSI[s[:2]],
        "hari": hari - 40 if perempuan else hari,
        "bulan": int(s[8:10]),
        "tahun2": int(s[10:12]),
        "jenis_kelamin": "P" if perempuan else "L",
    }


def validate_npwp(v) -> bool:
    """Cek struktur NPWP: 15 digit (format lama) atau 16 digit (format baru)."""
    if _kosong(v):
        return False
    s = re.sub(r"[.\-\s]", "", str(v))
    if not s.isdigit():
        return False
    if len(s) == 15:
        return set(s) != {"0"}
    if len(s) == 16:
        return validate_nik(s) or (s[0] == "0" and set(s[1:]) != {"0"})
    return False


def normalize_npwp(v) -> Optional[str]:
    """'012345678901234' -> '01.234.567.8-901.234'. 16 digit dikembalikan apa adanya."""
    if not validate_npwp(v):
        return None
    s = re.sub(r"[.\-\s]", "", str(v))
    if len(s) == 16:
        return s
    return f"{s[:2]}.{s[2:5]}.{s[5:8]}.{s[8]}-{s[9:12]}.{s[12:]}"


_PLAT = re.compile(r"([A-Z]{1,2})(\d{1,4})([A-Z]{0,3})")


def normalize_plat(v) -> Optional[str]:
    """'b1234abc' / 'B-1234-ABC' -> 'B 1234 ABC'. None bila bentuknya tidak cocok."""
    if _kosong(v):
        return None
    s = re.sub(r"[\s.\-]", "", str(v)).upper()
    m = _PLAT.fullmatch(s)
    if not m:
        return None
    return " ".join(p for p in m.groups() if p)


def validate_plat(v) -> bool:
    return normalize_plat(v) is not None


def normalize_jk(v) -> Optional[str]:
    """'Laki-laki' / 'pria' / 'L' -> 'L' ; 'Perempuan' / 'wanita' / 'P' -> 'P'."""
    if _kosong(v):
        return None
    s = re.sub(r"[\s\-_.]", "", str(v)).lower()
    if s in {"l", "lk", "laki", "lakilaki", "pria", "m", "male"}:
        return "L"
    if s in {"p", "pr", "perempuan", "wanita", "f", "female"}:
        return "P"
    return None


def samarkan_nik(v) -> str:
    """'3171011708900001' -> '317101******0001'."""
    s = re.sub(r"\D", "", str(v))
    if len(s) == 16:
        return s[:6] + "******" + s[-4:]
    return samarkan_nilai(v)


def samarkan_nilai(v) -> str:
    """Sembunyikan bagian tengah nilai: '081234567890' -> '08********90'."""
    s = str(v)
    if len(s) < 6:
        return "*" * len(s)
    return s[:2] + "*" * (len(s) - 4) + s[-2:]
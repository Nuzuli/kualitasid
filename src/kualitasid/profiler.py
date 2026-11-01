"""Profil kualitas data untuk DataFrame dengan format Indonesia."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

from .konsistensi import cek_konsistensi
from .parsers import (normalize_npwp, normalize_plat, normalize_provinsi,
                      normalize_telepon, parse_rupiah, parse_tanggal,
                      samarkan_nilai, validate_nik, validate_npwp)

DETEKTOR = {
    "nik": validate_nik,
    "npwp": validate_npwp,
    "plat": lambda v: normalize_plat(v) is not None,
    "telepon": lambda v: normalize_telepon(v) is not None,
    "tanggal": lambda v: parse_tanggal(v) is not None,
    "rupiah": lambda v: parse_rupiah(v) is not None,
    "provinsi": lambda v: normalize_provinsi(v) is not None,
}
# Urutan prioritas: yang lebih spesifik dicek dulu.
URUTAN = ["nik", "npwp", "plat", "telepon", "provinsi", "tanggal", "rupiah"]
# Contoh nilai tidak valid dari tipe ini disamarkan secara bawaan.
TIPE_SENSITIF = {"nik", "npwp", "telepon"}

KATA_LAHIR = ("lahir", "birth", "dob")
NAMA_JK = {"jenis_kelamin", "jk", "gender", "kelamin", "sex"}
BOBOT_KONSISTENSI = 0.5


def _teks(seri: pd.Series) -> bool:
    return pd.api.types.is_object_dtype(seri) or pd.api.types.is_string_dtype(seri)


def _terisi(seri: pd.Series) -> pd.Series:
    t = seri.dropna().astype(str).str.strip()
    return t[t != ""]


def _nama(kolom: Any) -> str:
    return str(kolom).strip().lower().replace(" ", "_")


def deteksi_tipe(seri: pd.Series, ambang: float = 0.6, sampel: int = 200):
    """Tebak tipe kolom. Return (tipe, rasio_cocok) atau (None, 0)."""
    data = _terisi(seri)
    if data.empty:
        return None, 0.0
    data = data.head(sampel)
    for tipe in URUTAN:
        rasio = float(data.map(DETEKTOR[tipe]).mean())
        if rasio >= ambang:
            return tipe, rasio
    return None, 0.0


def _cari_kolom_konsistensi(df: pd.DataFrame, tipe_kolom: Dict[Any, Optional[str]]):
    nik = next((c for c, t in tipe_kolom.items() if t == "nik"), None)
    lahir = next(
        (c for c, t in tipe_kolom.items()
         if t == "tanggal" and any(k in _nama(c) for k in KATA_LAHIR)),
        None,
    )
    jk = next(
        (c for c in df.columns if _nama(c) in NAMA_JK or "kelamin" in _nama(c)),
        None,
    )
    return nik, lahir, jk


def profil(df: pd.DataFrame, ambang: float = 0.6, samarkan: bool = True) -> dict:
    """Hasilkan laporan kualitas data per kolom + skor keseluruhan (0-100).

    Contoh nilai tidak valid dari kolom NIK/NPWP/telepon disamarkan secara
    bawaan; set ``samarkan=False`` untuk menampilkan nilai asli.
    """
    kolom: Dict[Any, Dict[str, Any]] = {}
    tipe_kolom: Dict[Any, Optional[str]] = {}
    skor: List[float] = []
    for nama in df.columns:
        seri = df[nama]
        terisi = _terisi(seri)
        mentah = seri.dropna().astype(str)
        info: Dict[str, Any] = {
            "kosong_persen": round(100 * (1 - len(terisi) / max(len(seri), 1)), 1),
            "tipe": None, "tidak_valid": 0, "contoh_tidak_valid": [],
            "spasi_berlebih": int((mentah != mentah.str.strip()).sum()),
        }
        if _teks(seri) and len(terisi):
            tipe, _ = deteksi_tipe(seri, ambang)
            info["tipe"] = tipe
            if tipe:
                salah = terisi[~terisi.map(DETEKTOR[tipe])]
                info["tidak_valid"] = int(len(salah))
                contoh = salah.head(3).tolist()
                if samarkan and tipe in TIPE_SENSITIF:
                    contoh = [samarkan_nilai(c) for c in contoh]
                info["contoh_tidak_valid"] = contoh
        tipe_kolom[nama] = info["tipe"]
        penalti = info["kosong_persen"] + 100 * info["tidak_valid"] / max(len(terisi), 1)
        skor.append(max(0.0, 100 - penalti))
        kolom[nama] = info

    nik, lahir, jk = _cari_kolom_konsistensi(df, tipe_kolom)
    konsistensi = cek_konsistensi(df, nik, lahir, jk)
    baris_salah = len({i["baris"] for i in konsistensi})
    n = max(len(df), 1)
    rata = sum(skor) / max(len(skor), 1)
    dup = float(df.duplicated().mean()) if len(df) else 0.0
    penalti_total = 100 * dup + BOBOT_KONSISTENSI * 100 * baris_salah / n
    return {
        "baris": len(df),
        "duplikat": int(df.duplicated().sum()),
        "skor": round(max(0.0, rata - penalti_total), 1),
        "kolom": kolom,
        "konsistensi": konsistensi,
        "baris_tidak_konsisten": baris_salah,
    }


def bersihkan(df: pd.DataFrame, ambang: float = 0.6) -> pd.DataFrame:
    """Normalisasi otomatis kolom yang tipenya terdeteksi."""
    out = df.copy()
    peta = {"telepon": normalize_telepon, "tanggal": parse_tanggal,
            "rupiah": parse_rupiah, "provinsi": normalize_provinsi,
            "npwp": normalize_npwp, "plat": normalize_plat}
    for nama in out.columns:
        if not _teks(out[nama]):
            continue
        tipe, _ = deteksi_tipe(out[nama], ambang)
        if tipe in peta:
            out[nama] = out[nama].map(peta[tipe])
    return out


def teks(laporan: dict) -> str:
    baris = [
        f"Baris: {laporan['baris']} | Duplikat: {laporan['duplikat']} "
        f"| Skor: {laporan['skor']}/100",
        "",
    ]
    for n, i in laporan["kolom"].items():
        s = f"- {n}: tipe={i['tipe'] or '-'}, kosong={i['kosong_persen']}%"
        if i["tidak_valid"]:
            s += f", tidak valid={i['tidak_valid']} (contoh: {i['contoh_tidak_valid']})"
        if i["spasi_berlebih"]:
            s += f", spasi berlebih={i['spasi_berlebih']}"
        baris.append(s)
    konsistensi = laporan.get("konsistensi", [])
    if konsistensi:
        baris += ["", f"Konsistensi antar kolom: {len(konsistensi)} masalah "
                      f"di {laporan['baris_tidak_konsisten']} baris"]
        for i in konsistensi[:5]:
            baris.append(
                f"- baris {i['baris']}: {i['jenis']} (NIK {i['nik']}, "
                f"nilai={i['nilai']}, menurut NIK={i['menurut_nik']})"
            )
    return "\n".join(baris)
"""Pemeriksaan konsistensi antar kolom, mis. NIK vs tanggal lahir."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

from .parsers import info_nik, normalize_jk, parse_tanggal, samarkan_nik


def cek_konsistensi(
    df: pd.DataFrame,
    kolom_nik: Optional[str],
    kolom_lahir: Optional[str] = None,
    kolom_jk: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Bandingkan isi NIK dengan kolom tanggal lahir dan jenis kelamin.

    NIK yang strukturnya tidak valid dilewati (sudah dilaporkan sebagai
    tidak valid). NIK selalu disamarkan di hasil. Kolom provinsi sengaja
    tidak dibandingkan: provinsi di NIK adalah tempat pendaftaran, bukan
    domisili sekarang.
    """
    isu: List[Dict[str, Any]] = []
    if kolom_nik is None:
        return isu
    n = len(df)
    lahir = df[kolom_lahir] if kolom_lahir is not None else [None] * n
    jk = df[kolom_jk] if kolom_jk is not None else [None] * n
    for label, nik_v, lahir_v, jk_v in zip(df.index, df[kolom_nik], lahir, jk):
        info = info_nik(nik_v)
        if info is None:
            continue
        tgl = parse_tanggal(lahir_v)
        if tgl is not None and (tgl.day, tgl.month, tgl.year % 100) != (
            info["hari"], info["bulan"], info["tahun2"]
        ):
            isu.append({
                "jenis": "nik_tanggal_lahir",
                "baris": label,
                "nik": samarkan_nik(nik_v),
                "nilai": str(lahir_v),
                "menurut_nik": f"{info['hari']:02d}-{info['bulan']:02d}-xx{info['tahun2']:02d}",
            })
        gender = normalize_jk(jk_v)
        if gender is not None and gender != info["jenis_kelamin"]:
            isu.append({
                "jenis": "nik_jenis_kelamin",
                "baris": label,
                "nik": samarkan_nik(nik_v),
                "nilai": str(jk_v),
                "menurut_nik": info["jenis_kelamin"],
            })
    return isu
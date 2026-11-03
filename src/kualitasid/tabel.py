"""Membaca tabel dari CSV atau Excel menjadi DataFrame bertipe teks."""
from __future__ import annotations

import importlib.util
import zipfile
from pathlib import Path
from typing import Optional

import pandas as pd

EKSTENSI_EXCEL = {".xlsx", ".xlsm"}
PESAN_EXCEL = 'Dukungan Excel butuh openpyxl. Pasang dengan: pip install "kualitasid[excel]"'


class BacaError(Exception):
    """Berkas tidak bisa dibaca sebagai tabel."""


def baca_tabel(path, sep: str = ",", sheet: Optional[str] = None) -> pd.DataFrame:
    """Baca CSV atau Excel (.xlsx/.xlsm) dengan semua kolom sebagai teks.

    ``sheet`` hanya untuk Excel (nama lembar; bawaan: lembar pertama).
    Masalah yang bisa diperbaiki pengguna dilaporkan sebagai ``BacaError``.
    """
    p = Path(path)
    ekstensi = p.suffix.lower()
    if ekstensi in EKSTENSI_EXCEL:
        return _baca_excel(p, sheet)
    if ekstensi == ".xls":
        raise BacaError("Format .xls lama tidak didukung. Simpan ulang sebagai .xlsx atau CSV.")
    if sheet is not None:
        raise BacaError("Opsi lembar (--sheet) hanya berlaku untuk file Excel (.xlsx).")
    try:
        return pd.read_csv(p, sep=sep, dtype=str)
    except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError) as error:
        raise BacaError(f"tidak bisa membaca {path}: {error}") from error


def _baca_excel(p: Path, sheet: Optional[str]) -> pd.DataFrame:
    if importlib.util.find_spec("openpyxl") is None:
        raise BacaError(PESAN_EXCEL)
    if not p.is_file():
        raise BacaError(f"tidak bisa membaca {p}: file tidak ditemukan")
    if not zipfile.is_zipfile(p):
        raise BacaError(f"{p} bukan file Excel .xlsx yang valid")
    try:
        return pd.read_excel(p, sheet_name=sheet if sheet is not None else 0, dtype=str)
    except (zipfile.BadZipFile, KeyError) as error:
        raise BacaError(f"{p} bukan file Excel .xlsx yang valid") from error
    except ValueError as error:
        raise BacaError(str(error)) from error
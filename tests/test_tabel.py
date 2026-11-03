import os
import tempfile
from unittest import mock

import pytest
from openpyxl import Workbook

from kualitasid.tabel import BacaError, baca_tabel


def _tulis_excel(path, lembar=None):
    wb = Workbook()
    ws = wb.active
    ws.title = "Data"
    ws.append(["nik", "hp"])
    ws.append(["3171011708900001", "0812-3456-7890"])
    ws.append(["3171015708900002", "0857 1111 2222"])
    if lembar:
        extra = wb.create_sheet(lembar)
        extra.append(["nama"])
        extra.append(["Budi"])
    wb.save(path)


def test_baca_csv_sebagai_teks():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "a.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write("nik,hp\n3171011708900001,0812\n")
        df = baca_tabel(path)
    assert df["nik"].iloc[0] == "3171011708900001"
    assert df["hp"].iloc[0] == "0812"


def test_baca_excel_lembar_pertama():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "a.xlsx")
        _tulis_excel(path, lembar="Lain")
        df = baca_tabel(path)
    assert list(df.columns) == ["nik", "hp"]
    assert len(df) == 2
    assert df["nik"].iloc[1] == "3171015708900002"


def test_baca_excel_lembar_dipilih_dengan_nama():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "a.xlsx")
        _tulis_excel(path, lembar="Lain")
        df = baca_tabel(path, sheet="Lain")
    assert list(df.columns) == ["nama"]
    assert df["nama"].iloc[0] == "Budi"


def test_lembar_tidak_ada_dilaporkan_jelas():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "a.xlsx")
        _tulis_excel(path)
        with pytest.raises(BacaError) as info:
            baca_tabel(path, sheet="TidakAda")
    assert "TidakAda" in str(info.value)


def test_file_xls_lama_ditolak_dengan_saran():
    with pytest.raises(BacaError) as info:
        baca_tabel("data.xls")
    assert ".xlsx" in str(info.value)


def test_sheet_untuk_csv_ditolak():
    with pytest.raises(BacaError) as info:
        baca_tabel("data.csv", sheet="Data")
    assert "--sheet" in str(info.value)


def test_file_rusak_bukan_excel_valid():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "palsu.xlsx")
        with open(path, "w", encoding="utf-8") as f:
            f.write("ini bukan excel")
        with pytest.raises(BacaError) as info:
            baca_tabel(path)
    assert "bukan file Excel" in str(info.value)


def test_file_excel_tidak_ada():
    with pytest.raises(BacaError) as info:
        baca_tabel("tidak_ada.xlsx")
    assert "tidak bisa membaca" in str(info.value)


def test_tanpa_openpyxl_ada_saran_pemasangan():
    with mock.patch("kualitasid.tabel.importlib.util.find_spec", return_value=None):
        with pytest.raises(BacaError) as info:
            baca_tabel("data.xlsx")
    assert 'kualitasid[excel]' in str(info.value)
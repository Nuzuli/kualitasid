import json

import pandas as pd

from kualitasid import ke_html, ke_json, profil


def _laporan():
    df = pd.DataFrame({
        "nama": ["<script>alert(1)</script>", "Budi"],
        "nik": ["3171011708900001", "3171015708900002"],
        "jenis_kelamin": ["Laki-laki", "Laki-laki"],
    })
    return profil(df)


def test_json_valid_dan_utf8():
    data = json.loads(ke_json(_laporan()))
    assert data["baris"] == 2
    assert "kolom" in data and "konsistensi" in data


def test_html_meng_escape_isi():
    html = ke_html(_laporan())
    assert "<script>alert(1)</script>" not in html
    assert html.startswith("<!doctype html>")
    assert "Skor:" in html


def test_html_memuat_bagian_konsistensi():
    assert "Konsistensi antar kolom" in ke_html(_laporan())
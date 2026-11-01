"""Ekspor laporan profil ke JSON dan HTML."""
from __future__ import annotations

import html
import json


def ke_json(laporan: dict) -> str:
    """Laporan sebagai JSON (UTF-8, tanpa escape non-ASCII)."""
    return json.dumps(laporan, ensure_ascii=False, indent=2, default=str)


def ke_html(laporan: dict, judul: str = "Laporan kualitas data") -> str:
    """Laporan sebagai satu halaman HTML mandiri (tanpa sumber luar)."""
    e = lambda v: html.escape(str(v))  # noqa: E731
    baris_kolom = "".join(
        f"<tr><td>{e(n)}</td><td>{e(i['tipe'] or '-')}</td>"
        f"<td>{e(i['kosong_persen'])}%</td><td>{e(i['tidak_valid'])}</td>"
        f"<td>{e(', '.join(map(str, i['contoh_tidak_valid'])))}</td></tr>"
        for n, i in laporan["kolom"].items()
    )
    baris_isu = "".join(
        f"<tr><td>{e(i['baris'])}</td><td>{e(i['jenis'])}</td><td>{e(i['nik'])}</td>"
        f"<td>{e(i['nilai'])}</td><td>{e(i['menurut_nik'])}</td></tr>"
        for i in laporan.get("konsistensi", [])
    )
    isu = (
        "<h2>Konsistensi antar kolom</h2><table><tr><th>Baris</th><th>Jenis</th>"
        f"<th>NIK</th><th>Nilai</th><th>Menurut NIK</th></tr>{baris_isu}</table>"
        if baris_isu else ""
    )
    return (
        "<!doctype html><html lang=\"id\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<title>{e(judul)}</title><style>body{{font-family:sans-serif;margin:1rem}}"
        "table{border-collapse:collapse;margin:1rem 0}td,th{border:1px solid #888;"
        "padding:4px 8px;text-align:left}</style></head><body>"
        f"<h1>{e(judul)}</h1><p>Baris: {e(laporan['baris'])} | Duplikat: "
        f"{e(laporan['duplikat'])} | <b>Skor: {e(laporan['skor'])}/100</b></p>"
        "<table><tr><th>Kolom</th><th>Tipe</th><th>Kosong</th><th>Tidak valid</th>"
        f"<th>Contoh</th></tr>{baris_kolom}</table>{isu}</body></html>"
    )
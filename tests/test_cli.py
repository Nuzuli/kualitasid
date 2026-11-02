import contextlib
import io
import json
import os
import tempfile

from kualitasid.cli import main

CONTOH = os.path.join(os.path.dirname(__file__), "..", "examples", "data_kotor.csv")


def _jalankan(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


def test_laporan_teks():
    code, out, _ = _jalankan([CONTOH])
    assert code == 0
    assert "Skor:" in out
    assert "Konsistensi antar kolom" in out


def test_laporan_json():
    code, out, _ = _jalankan([CONTOH, "--json"])
    assert code == 0
    assert json.loads(out)["baris_tidak_konsisten"] == 2


def test_html_dan_bersihkan_menulis_file():
    with tempfile.TemporaryDirectory() as d:
        html = os.path.join(d, "laporan.html")
        bersih = os.path.join(d, "bersih.csv")
        code, _, _ = _jalankan([CONTOH, "--html", html, "--bersihkan", bersih])
        assert code == 0
        assert os.path.getsize(html) > 0
        assert "npwp" in open(bersih, encoding="utf-8").read()


def test_file_tidak_ada_keluar_kode_2():
    code, _, err = _jalankan(["tidak_ada.csv"])
    assert code == 2
    assert "tidak bisa membaca" in err
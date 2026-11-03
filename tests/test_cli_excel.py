import contextlib
import io
import json
import os
import tempfile

from openpyxl import Workbook

from kualitasid.cli import main


def _excel(path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Data"
    ws.append(["nik", "tgl_lahir", "jenis_kelamin"])
    ws.append(["3171011708900001", "17 Agustus 1990", "Laki-laki"])
    ws.append(["3171015708900002", "17 Agustus 1990", "Laki-laki"])
    wb.save(path)


def _jalankan(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


def test_cli_membaca_excel():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "orang.xlsx")
        _excel(path)
        code, out, _ = _jalankan([path, "--json"])
    assert code == 0
    assert json.loads(out)["baris_tidak_konsisten"] == 1


def test_cli_lembar_tidak_ada_keluar_kode_2():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "orang.xlsx")
        _excel(path)
        code, _, err = _jalankan([path, "--sheet", "TidakAda"])
    assert code == 2
    assert "TidakAda" in err


def test_cli_xls_lama_keluar_kode_2():
    code, _, err = _jalankan(["data.xls"])
    assert code == 2
    assert ".xlsx" in err
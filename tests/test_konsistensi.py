import pandas as pd

from kualitasid import cek_konsistensi


def _df():
    return pd.DataFrame({
        "nik": [
            "3171011708900001",  # L, 17-08-90
            "3171015708900002",  # P, 17-08-90
            "3273011503850004",  # L, 15-03-85
            "123",               # tidak valid: dilewati
        ],
        "lahir": ["17 Agustus 1990", "17 Agustus 1990", "16-03-1985", "1/1/2000"],
        "jk": ["Laki-laki", "Laki-laki", "Laki-laki", "Perempuan"],
    })


def test_menemukan_ketidakcocokan():
    isu = cek_konsistensi(_df(), "nik", "lahir", "jk")
    jenis = sorted((i["baris"], i["jenis"]) for i in isu)
    assert jenis == [(1, "nik_jenis_kelamin"), (2, "nik_tanggal_lahir")]


def test_nik_disamarkan_di_hasil():
    for i in cek_konsistensi(_df(), "nik", "lahir", "jk"):
        assert "******" in i["nik"]
        assert i["nik"].startswith("3") and len(i["nik"]) == 16


def test_tanpa_kolom_nik_tidak_ada_isu():
    assert cek_konsistensi(_df(), None, "lahir", "jk") == []


def test_kolom_opsional():
    isu = cek_konsistensi(_df(), "nik", kolom_jk="jk")
    assert [i["jenis"] for i in isu] == ["nik_jenis_kelamin"]


def test_nilai_kosong_tidak_dihitung():
    df = pd.DataFrame({"nik": ["3171011708900001"], "lahir": [None], "jk": [None]})
    assert cek_konsistensi(df, "nik", "lahir", "jk") == []
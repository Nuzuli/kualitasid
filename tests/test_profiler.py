import pandas as pd

from kualitasid import bersihkan, deteksi_tipe, profil, teks


def _df():
    return pd.DataFrame({
        "hp": ["0812-3456-7890", "+6281398765432", "0857 1111 2222", "salah"],
        "gaji": ["Rp 5.000.000", "7,5 jt", "Rp 6.000.000", "4jt"],
        "lahir": ["17 Agustus 1990", "1/2/95", "03-04-1988", "5 Mei 2000"],
        "prov": ["jabar", "DKI Jakarta", "Jawa Tengah", "jatim"],
    })


def _df_orang():
    return pd.DataFrame({
        "nik": ["3171011708900001", "3171015708900002", "3273011503850004"],
        "npwp": ["012345678901234", "01.234.567.8-901.234", "bukan"],
        "plat": ["b1234abc", "AB-123-CD", "D 4321 XY"],
        "tgl_lahir": ["17 Agustus 1990", "17 Agustus 1990", "16-03-1985"],
        "jenis_kelamin": ["Laki-laki", "Laki-laki", "Laki-laki"],
    })


def test_deteksi():
    df = _df()
    assert deteksi_tipe(df["hp"])[0] == "telepon"
    assert deteksi_tipe(df["gaji"])[0] == "rupiah"
    assert deteksi_tipe(df["lahir"])[0] == "tanggal"
    assert deteksi_tipe(df["prov"])[0] == "provinsi"


def test_deteksi_npwp_plat_nik():
    df = _df_orang()
    assert deteksi_tipe(df["nik"])[0] == "nik"
    assert deteksi_tipe(df["npwp"])[0] == "npwp"
    assert deteksi_tipe(df["plat"])[0] == "plat"


def test_profil_dan_bersih():
    df = _df()
    r = profil(df)
    assert r["kolom"]["hp"]["tidak_valid"] == 1
    assert 0 <= r["skor"] <= 100
    assert bersihkan(df)["gaji"].iloc[1] == 7_500_000


def test_bersihkan_npwp_dan_plat():
    out = bersihkan(_df_orang())
    assert out["npwp"].iloc[0] == "01.234.567.8-901.234"
    assert out["plat"].iloc[0] == "B 1234 ABC"


def test_contoh_tidak_valid_disamarkan_bawaan():
    r = profil(_df_orang())
    contoh = r["kolom"]["npwp"]["contoh_tidak_valid"]
    assert contoh == ["*****"]
    r2 = profil(_df_orang(), samarkan=False)
    assert r2["kolom"]["npwp"]["contoh_tidak_valid"] == ["bukan"]


def test_profil_menemukan_ketidakkonsistenan():
    r = profil(_df_orang())
    assert r["baris_tidak_konsisten"] == 2
    assert {i["jenis"] for i in r["konsistensi"]} == {
        "nik_tanggal_lahir", "nik_jenis_kelamin"
    }
    bersih = _df_orang().iloc[[0]]
    assert profil(bersih)["baris_tidak_konsisten"] == 0


def test_skor_turun_karena_konsistensi():
    df = _df_orang()
    sama = df.copy()
    sama.loc[:, "tgl_lahir"] = ["17 Agustus 1990", "17 Agustus 1990", "15-03-1985"]
    sama.loc[:, "jenis_kelamin"] = ["Laki-laki", "Perempuan", "Laki-laki"]
    assert profil(sama)["skor"] > profil(df)["skor"]


def test_teks_memuat_ringkasan():
    out = teks(profil(_df_orang()))
    assert "Skor:" in out
    assert "Konsistensi antar kolom" in out
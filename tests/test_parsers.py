from datetime import date

from kualitasid import (info_nik, normalize_jk, normalize_npwp, normalize_plat,
                        normalize_provinsi, normalize_telepon, parse_rupiah,
                        parse_tanggal, samarkan_nik, samarkan_nilai,
                        validate_nik, validate_npwp, validate_plat)


def test_rupiah():
    assert parse_rupiah("Rp 1.500.000,50") == 1500000.5
    assert parse_rupiah("1,5 jt") == 1_500_000
    assert parse_rupiah("500rb") == 500_000
    assert parse_rupiah("Rp1.500") == 1500
    assert parse_rupiah("abc") is None


def test_tanggal():
    assert parse_tanggal("17 Agustus 2026") == date(2026, 8, 17)
    assert parse_tanggal("17/8/26") == date(2026, 8, 17)
    assert parse_tanggal("2026-08-17") == date(2026, 8, 17)
    assert parse_tanggal("31 Februari 2026") is None


def test_telepon():
    assert normalize_telepon("0812-3456-7890") == "+6281234567890"
    assert normalize_telepon("+62 812 3456 7890") == "+6281234567890"
    assert normalize_telepon("12345") is None


def test_nik():
    assert validate_nik("3171011708900001")
    assert validate_nik("3171015708900001")  # perempuan (tgl+40)
    assert not validate_nik("9971011708900001")
    assert not validate_nik("123")


def test_provinsi():
    assert normalize_provinsi("jabar") == "Jawa Barat"
    assert normalize_provinsi("Jawa barat ") == "Jawa Barat"
    assert normalize_provinsi("Provinsi Jawa Tengah") == "Jawa Tengah"
    assert normalize_provinsi("Jawa Brat") == "Jawa Barat"
    assert normalize_provinsi("Mars") is None


def test_info_nik():
    laki = info_nik("3171011708900001")
    assert laki == {
        "kode_provinsi": "31", "provinsi": "DKI Jakarta",
        "hari": 17, "bulan": 8, "tahun2": 90, "jenis_kelamin": "L",
    }
    perempuan = info_nik("3171015708900001")
    assert perempuan["hari"] == 17 and perempuan["jenis_kelamin"] == "P"
    assert info_nik("123") is None


def test_npwp():
    assert validate_npwp("01.234.567.8-901.234")
    assert validate_npwp("012345678901234")
    assert normalize_npwp("012345678901234") == "01.234.567.8-901.234"
    assert normalize_npwp("01.234.567.8-901.234") == "01.234.567.8-901.234"
    assert validate_npwp("3171011708900001")  # format baru = NIK
    assert validate_npwp("0012345678901234")  # 16 digit badan usaha
    assert not validate_npwp("000000000000000")
    assert not validate_npwp("12345")
    assert not validate_npwp("abcdefghijklmno")


def test_plat():
    assert normalize_plat("b1234abc") == "B 1234 ABC"
    assert normalize_plat("AB-123-CD") == "AB 123 CD"
    assert normalize_plat("D 4321") == "D 4321"
    assert validate_plat("F 77 A")
    assert not validate_plat("1234")
    assert not validate_plat("ABC 123 D")
    assert not validate_plat("")


def test_jenis_kelamin():
    assert normalize_jk("Laki-laki") == "L"
    assert normalize_jk("pria") == "L"
    assert normalize_jk("Perempuan") == "P"
    assert normalize_jk("wanita") == "P"
    assert normalize_jk("lainnya") is None
    assert normalize_jk(None) is None


def test_samarkan():
    assert samarkan_nik("3171011708900001") == "317101******0001"
    assert samarkan_nilai("081234567890") == "08********90"
    assert samarkan_nilai("abc") == "***"


def test_info_nik_provinsi_papua():
    # kode wilayah Kemendagri yang dipakai di NIK
    assert info_nik("9171011708900001")["provinsi"] == "Papua"
    assert info_nik("9271011708900001")["provinsi"] == "Papua Barat"
    assert info_nik("9671011708900001")["provinsi"] == "Papua Barat Daya"

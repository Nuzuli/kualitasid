# kualitasid 🇮🇩

[

![CI](https://github.com/Nuzuli/kualitasid/actions/workflows/ci.yml/badge.svg)

](https://github.com/Nuzuli/kualitasid/actions/workflows/ci.yml)
[

![PyPI](https://img.shields.io/pypi/v/kualitasid)

](https://pypi.org/project/kualitasid/)
[

![Python](https://img.shields.io/pypi/pyversions/kualitasid)

](https://pypi.org/project/kualitasid/)


Profil dan pembersih kualitas data **untuk DataFrame/CSV berformat Indonesia**. Yang dikerjakan di
level kolom dan baris, bukan hanya satu nilai:

- mendeteksi tipe tiap kolom (NIK, NPWP, HP, tanggal, Rupiah, plat, provinsi),
- menghitung skor kualitas 0-100 dan melaporkan nilai tidak valid, kosong, duplikat, spasi berlebih,
- **memeriksa konsistensi antar kolom**: NIK vs tanggal lahir dan jenis kelamin,
- membersihkan otomatis (`Rp 1,5 jt` → `1500000`, `0812-3456-7890` → `+6281234567890`),
- laporan teks, JSON, atau satu halaman HTML.

Semua diproses lokal. Tidak ada data yang dikirim ke mana pun.

## Contoh

```bash
pip install kualitasid
kualitasid data_saya.csv --html laporan.html --bersihkan bersih.csv
```

Untuk mencoba dengan data fiktif, unduh
[`examples/data_kotor.csv`](https://github.com/Nuzuli/kualitasid/blob/main/examples/data_kotor.csv)
dari repo ini.

```python
import pandas as pd
from kualitasid import profil, bersihkan, teks

df = pd.read_csv("examples/data_kotor.csv", dtype=str)
laporan = profil(df)        # NIK/NPWP/HP pada contoh disamarkan secara bawaan
print(teks(laporan))
df_bersih = bersihkan(df)
```

Cuplikan keluaran:

```
Konsistensi antar kolom: 2 masalah di 2 baris
- baris 1: nik_jenis_kelamin (NIK 317101******0002, nilai=Laki-laki, menurut NIK=P)
- baris 2: nik_tanggal_lahir (NIK 327301******0004, nilai=16-03-1985, menurut NIK=15-03-xx85)

```


## Batasan (penting)

- Validasi NIK dan NPWP hanya **struktur**, bukan bukti orangnya ada. Kode wilayah di bawah provinsi
  belum diperiksa.
- Provinsi di NIK adalah tempat pendaftaran, jadi kolom provinsi **tidak** dibandingkan dengan NIK.
- Tahun di NIK hanya 2 digit, jadi abad tidak diperiksa.
- Jangan unggah data pribadi asli ke repo publik. Contoh di `examples/` fiktif.

## Alternatif

Kalau yang kamu butuhkan validator/parser per-nilai, data wilayah lengkap, atau penyamaran PII untuk
teks bebas, pustaka seperti [`lokal-id`](https://pypi.org/project/lokal-id/),
[`nik-lookup`](https://pypi.org/project/nik-lookup/), dan
[`daerah-indonesia`](https://pypi.org/project/daerah-indonesia/) lebih lengkap di sisi itu.
`kualitasid` fokus pada profil per kolom, skor, dan konsistensi antar kolom pada DataFrame.

## Pengembangan

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v --cov=kualitasid
ruff check src tests && mypy src
```

## Lisensi

MIT. Lihat `LICENSE`.
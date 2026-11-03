import argparse
import sys

from .laporan import ke_html, ke_json
from .profiler import bersihkan, profil, teks
from .tabel import BacaError, baca_tabel


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="kualitasid", description="Cek kualitas data CSV/Excel format Indonesia"
    )
    p.add_argument("csv", help="path file CSV atau Excel (.xlsx)")
    p.add_argument("--sep", default=",", help="pemisah kolom CSV (default ',')")
    p.add_argument("--sheet", help="nama lembar Excel (default: lembar pertama)")
    p.add_argument("--json", action="store_true", help="cetak laporan sebagai JSON")
    p.add_argument("--html", metavar="OUT", help="simpan laporan HTML ke file ini")
    p.add_argument("--bersihkan", metavar="OUT", help="simpan versi bersih ke CSV ini")
    p.add_argument(
        "--tanpa-samar", action="store_true",
        help="tampilkan nilai asli (NIK/NPWP/HP) pada contoh tidak valid",
    )
    a = p.parse_args(argv)
    try:
        df = baca_tabel(a.csv, sep=a.sep, sheet=a.sheet)
    except BacaError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    laporan = profil(df, samarkan=not a.tanpa_samar)
    print(ke_json(laporan) if a.json else teks(laporan))
    if a.html:
        with open(a.html, "w", encoding="utf-8") as f:
            f.write(ke_html(laporan))
        print(f"\nLaporan HTML: {a.html}", file=sys.stderr)
    if a.bersihkan:
        bersihkan(df).to_csv(a.bersihkan, index=False)
        print(f"Tersimpan: {a.bersihkan}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
# Changelog

All notable changes to this project are documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Fixed

- NIK province codes 91, 92, and 96 now follow the Kemendagri codes (Papua, Papua Barat, Papua Barat Daya).

## [0.3.0] - 2026-11-05

### Added

- Excel input: `kualitasid data.xlsx` reads the first sheet, and `--sheet NAME` picks another one. Install with `pip install "kualitasid[excel]"`.
- `kualitasid.tabel.baca_tabel()` reads CSV or Excel into a text-only DataFrame.
- Clear errors (exit code 2) for a missing sheet, an invalid `.xlsx`, the old `.xls` format, and a missing `openpyxl`.

## [0.2.0] - 2026-11-02

### Added

- Column types `npwp` (15 or 16 digits, structure only) and `plat` (Indonesian vehicle plates), with `validate_npwp`, `normalize_npwp`, `validate_plat`, and `normalize_plat`.
- `info_nik()`: province code, birth day/month/two-digit year, and gender encoded in a NIK.
- Cross-column consistency checks (`cek_konsistensi`): NIK versus a birth-date column and a gender column. The province column is deliberately not compared, because the NIK province is the registration place, not the current home.
- `samarkan_nik()` and `samarkan_nilai()`. Examples of invalid NIK, NPWP, and phone values are masked by default (`samarkan=False` shows raw values).
- JSON (`--json`) and single-file HTML (`--html OUT`) reports.
- GitHub Actions CI with ruff, mypy, and a coverage gate.

### Changed

- The overall score now also drops with the share of rows that fail a consistency check.
- The CLI reports unreadable files with exit code 2 instead of a traceback.

## [0.1.0] - 2026-11-01

### Added

- Column type detection for NIK, phone, date, Rupiah, and province.
- Parsers for Rupiah (`Rp 1.500.000,50`, `1,5 jt`, `500rb`), Indonesian dates, and `+62` phone numbers.
- Quality score, duplicate and whitespace detection, and automatic cleaning.
# Vibe Data Engineering — Volatilitas Saham IDX dengan Genie Code

Selamat datang di workshop **Vibe Data Engineering**! Dalam tutorial hands-on ini, Anda akan menggunakan **Genie Code** — asisten coding AI yang tertanam langsung di workspace Databricks Anda — untuk membangun pipeline data lengkap: dari CSV mentah harga saham **Bursa Efek Indonesia (IDX)** hingga gold-layer analitik volatilitas, Genie Space, dan dashboard.

Yang ingin kita analisis: **harga saham dengan volatilitas tinggi** — saham mana yang paling bergejolak, bagaimana trennya dari waktu ke waktu, dan bagaimana volatilitas tiap saham dibandingkan dengan pasar (IHSG).

> **Apa itu Vibe Data Engineering?** Praktik menggunakan asisten AI untuk membangun dan mengelola pipeline data melalui prompt konversasional, bukan menulis setiap baris kode secara manual. Anda mendeskripsikan *apa* yang diinginkan, dan AI membantu membangunnya.

---

## Daftar Isi

1. [Prerequisites](#1-prerequisites)
2. [Repository Overview](#2-repository-overview)
3. [Getting the Data](#3-getting-the-data)
4. [Enabling Genie Code](#4-enabling-genie-code)
5. [Mulai Tutorial](#5-mulai-tutorial)

---

## 1. Prerequisites

Sebelum mulai, pastikan Anda memiliki:

- Akses ke **Databricks workspace** ([daftar free trial](https://www.databricks.com/try-databricks) jika belum punya)
- **Genie Code** aktif di workspace (aktif secara default di sebagian besar workspace)
- Browser modern (Chrome, Firefox, Edge, atau Safari)
- **Python 3.9+** di komputer lokal (hanya jika Anda ingin men-generate ulang data sampel dengan yfinance)

### Checklist

Sebelum lanjut, konfirmasi:

- [ ] Anda bisa login ke Databricks workspace
- [ ] Anda melihat bagian **Catalog** di sidebar kiri
- [ ] Anda bisa membuat **ETL pipeline** baru (klik **New** di sidebar)
- [ ] File CSV di `data/idx/` sudah tersedia di komputer lokal (lihat [Getting the Data](#3-getting-the-data))

---

## 2. Repository Overview

Repository ini berisi data sampel harga saham IDX dalam **3 file CSV** — satu folder per tabel:

```
data/
└── idx/                                       # Bursa Efek Indonesia
    ├── listed_companies/
    │   └── listed_companies.csv               # master emiten (~30 baris)
    ├── daily_prices/
    │   └── daily_prices.csv                   # harga harian OHLCV per saham (~14.400 baris)
    └── index_prices/
        └── index_prices.csv                   # harga harian IHSG / ^JKSE (~476 baris)
```

**Skema tabel:**


| Tabel              | Peran                    | Kolom kunci                                                                                        |
| ------------------ | ------------------------ | -------------------------------------------------------------------------------------------------- |
| `listed_companies` | Dimensi (master)         | `ticker, company_name, sector, sub_sector, listing_board, index_membership, ipo_year`              |
| `daily_prices`     | Fakta (inti volatilitas) | `ticker, trade_date, open, high, low, close, adj_close, volume, daily_return_pct, daily_range_pct` |
| `index_prices`     | Fakta (benchmark IHSG)   | `index_date, index_open, index_high, index_low, index_close, index_volume, index_return_pct`       |


Kolom `daily_return_pct` (perubahan close harian %) dan `daily_range_pct` (`(high-low)/open*100`) sudah dihitung di data, sehingga agregasi gold dan pertanyaan Genie menjadi langsung.

Data mencakup campuran tiga kelompok sehingga kontras volatilitas terlihat sangat jelas:

- **Blue chip LQ45** yang relatif stabil — BBCA, BBRI, TLKM, ASII, ICBP, INDF, …
- **Saham bervolatilitas tinggi** — GOTO, BREN, BUMI, CUAN, ANTM, MDKA, …
- **Saham kontroversial / "gorengan"** dengan pergerakan ekstrem — BUVA, ZATA, DEWA, BRMS, BNBR, ELTY (grup Bakrie), RAJA, PTRO, PANI (PIK2), dan GIAA (Garuda, restrukturisasi) — beberapa di antaranya bergerak jauh lebih liar dibanding pasar (IHSG).

---

## 3. Getting the Data

File CSV sudah tersedia di folder `data/idx/`. Jika Anda ingin **men-generate ulang** (mis. memperbarui rentang tanggal atau menambah ticker), gunakan script yfinance yang disertakan:

```bash
# (opsional) buat virtual environment
python3 -m venv .venv
source .venv/bin/activate

# install dependensi
pip install -r requirements.txt

# generate data (mengunduh ~2 tahun harga harian dari yfinance)
python generate_data.py
```

Script akan menulis ulang ketiga CSV ke `data/idx/<tabel>/<tabel>.csv`. Untuk mengubah daftar saham, rentang waktu, atau indeks, edit konstanta `COMPANIES`, `PERIOD`, dan `INDEX_SYMBOL` di bagian atas `generate_data.py`.

> **Catatan:** yfinance memerlukan koneksi internet dan sesekali dibatasi rate limit. CSV yang sudah ter-commit memastikan tutorial tetap bisa dijalankan meskipun regenerasi gagal.

---

## 4. Enabling Genie Code

Genie Code adalah asisten coding AI yang tertanam di pipeline IDE, notebook, SQL editor, dan permukaan workspace lainnya. Biasanya aktif secara default.

Untuk memverifikasi:

1. Buka Databricks workspace Anda
2. Klik **New** > **ETL pipeline** di sidebar
3. Cari ikon **Genie Code** (ikon sparkle/bintang) di toolbar editor pipeline
4. Jika terlihat, Anda siap — Anda bisa membatalkan pembuatan pipeline untuk saat ini

> **Tidak melihat Genie Code?** Minta admin workspace mengaktifkannya di **Settings** > **Workspace settings**.

---

## 5. Mulai Tutorial

Ikuti tutorial langkah-demi-langkah di [**TUTORIAL_IDX_SIMPLE.md**](TUTORIAL_IDX_SIMPLE.md) — 8 exercise yang memandu Anda membangun pipeline data lengkap menggunakan workspace UI dan Genie Code.


| Fase         | Exercise                                       | Tool                      |
| ------------ | ---------------------------------------------- | ------------------------- |
| **Setup**    | 1. Buat schema, 2. Buat volume, 3. Upload data | Workspace UI              |
| **Pipeline** | 4. Pipeline & bronze layer, 5. Gold layer      | Workspace UI + Genie Code |
| **Eksekusi** | 6. Jalankan pipeline                           | Workspace UI              |
| **Analitik** | 7. Buat Genie Space, 8. Buat dashboard         | Workspace UI + Genie Code |


---

> **Vibe Data Engineering dengan Genie Code** — semuanya di browser, langsung ke gold layer.


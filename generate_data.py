"""
Generate sample data for the IDX (Indonesia Stock Exchange) stock-volatility tutorial.

Uses the yfinance library to download ~2 years of real daily prices for a mix of
LQ45 blue chips and high-volatility names, plus the IDX Composite index (IHSG / ^JKSE).

Produces three CSV files, one folder per table, mirroring the reference tutorial layout:

    data/idx/listed_companies/listed_companies.csv   (master / dimension, ~20 rows)
    data/idx/daily_prices/daily_prices.csv           (OHLCV fact table, ~10k rows)
    data/idx/index_prices/index_prices.csv           (IHSG benchmark, ~500 rows)

Run:
    pip install -r requirements.txt
    python generate_data.py
"""

import os
import sys
import time

import pandas as pd
import yfinance as yf

# --------------------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------------------

PERIOD = "2y"          # ~2 years of daily history
INDEX_SYMBOL = "^JKSE"  # IHSG - IDX Composite Index
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "idx")
PAUSE_SECONDS = 0.6     # be polite between requests to reduce rate limiting

# Curated master data. Kept static (not scraped via yfinance .info) so sector/board/
# index labels stay clean, Indonesian, and reproducible. Mix of stable blue chips and
# notoriously volatile names so the volatility analysis has strong contrast.
COMPANIES = [
    # ticker,    company_name,                         sector,                sub_sector,                 board,          index_membership, ipo_year
    ("BBCA.JK", "Bank Central Asia Tbk",              "Keuangan",            "Bank",                     "utama",        "LQ45",           2000),
    ("BBRI.JK", "Bank Rakyat Indonesia Tbk",          "Keuangan",            "Bank",                     "utama",        "LQ45",           2003),
    ("BMRI.JK", "Bank Mandiri Tbk",                   "Keuangan",            "Bank",                     "utama",        "LQ45",           2003),
    ("BBNI.JK", "Bank Negara Indonesia Tbk",          "Keuangan",            "Bank",                     "utama",        "LQ45",           1996),
    ("TLKM.JK", "Telkom Indonesia Tbk",               "Infrastruktur",       "Telekomunikasi",           "utama",        "LQ45",           1995),
    ("ASII.JK", "Astra International Tbk",             "Perindustrian",       "Otomotif & Komponen",      "utama",        "LQ45",           1990),
    ("UNVR.JK", "Unilever Indonesia Tbk",             "Konsumen Primer",     "Barang Konsumsi",          "utama",        "LQ45",           1982),
    ("ICBP.JK", "Indofood CBP Sukses Makmur Tbk",     "Konsumen Primer",     "Makanan & Minuman",        "utama",        "LQ45",           2010),
    ("INDF.JK", "Indofood Sukses Makmur Tbk",         "Konsumen Primer",     "Makanan & Minuman",        "utama",        "LQ45",           1994),
    ("KLBF.JK", "Kalbe Farma Tbk",                    "Kesehatan",           "Farmasi",                  "utama",        "LQ45",           1991),
    ("GOTO.JK", "GoTo Gojek Tokopedia Tbk",           "Teknologi",           "Aplikasi & Jasa Internet", "utama",        "IDX30",          2022),
    ("BREN.JK", "Barito Renewables Energy Tbk",       "Infrastruktur",       "Energi Terbarukan",        "utama",        "-",              2023),
    ("BUMI.JK", "Bumi Resources Tbk",                 "Energi",              "Batu Bara",                "utama",        "-",              1990),
    ("ANTM.JK", "Aneka Tambang Tbk",                  "Barang Baku",         "Logam & Mineral",          "utama",        "LQ45",           1997),
    ("MDKA.JK", "Merdeka Copper Gold Tbk",            "Barang Baku",         "Logam & Mineral",          "utama",        "LQ45",           2015),
    ("ADRO.JK", "Adaro Energy Indonesia Tbk",         "Energi",              "Batu Bara",                "utama",        "LQ45",           2008),
    ("PTBA.JK", "Bukit Asam Tbk",                     "Energi",              "Batu Bara",                "utama",        "-",              2002),
    ("INCO.JK", "Vale Indonesia Tbk",                 "Barang Baku",         "Logam & Mineral",          "utama",        "LQ45",           1990),
    ("ARTO.JK", "Bank Jago Tbk",                      "Keuangan",            "Bank Digital",             "utama",        "-",              2016),
    ("CUAN.JK", "Petrindo Jaya Kreasi Tbk",           "Energi",              "Batu Bara",                "pengembangan", "-",              2023),
    # Saham kontroversial / bervolatilitas ekstrem ("gorengan", restrukturisasi,
    # likuiditas tipis) — untuk mempertajam cerita volatilitas.
    ("BUVA.JK", "Bukit Uluwatu Villa Tbk",            "Properti & Real Estat", "Hotel & Pariwisata",     "utama",        "-",              2010),
    ("ZATA.JK", "Bersama Zatta Jaya Tbk",             "Konsumen Non-Primer", "Ritel Fesyen",             "pengembangan", "-",              2023),
    ("BNBR.JK", "Bakrie & Brothers Tbk",              "Perindustrian",       "Holding Investasi",        "utama",        "-",              1989),
    ("ELTY.JK", "Bakrieland Development Tbk",         "Properti & Real Estat", "Pengembang Kawasan",     "utama",        "-",              2004),
    ("RAJA.JK", "Rukun Raharja Tbk",                  "Energi",              "Distribusi Gas",           "utama",        "-",              2006),
    ("PTRO.JK", "Petrosea Tbk",                       "Energi",              "Jasa Pertambangan",        "utama",        "-",              1990),
    ("DEWA.JK", "Darma Henwa Tbk",                    "Energi",              "Jasa Pertambangan",        "utama",        "-",              2007),
    ("BRMS.JK", "Bumi Resources Minerals Tbk",        "Barang Baku",         "Logam & Mineral",          "utama",        "-",              2010),
    ("PANI.JK", "Pantai Indah Kapuk Dua Tbk",         "Properti & Real Estat", "Pengembang Kawasan",     "utama",        "LQ45",           2018),
    ("GIAA.JK", "Garuda Indonesia Tbk",               "Transportasi & Logistik", "Maskapai Penerbangan", "utama",        "-",              2011),
]

COMPANY_COLUMNS = [
    "ticker", "company_name", "sector", "sub_sector",
    "listing_board", "index_membership", "ipo_year",
]


def write_csv(df: pd.DataFrame, table: str) -> None:
    """Write a dataframe to data/idx/<table>/<table>.csv (creating dirs as needed)."""
    out_dir = os.path.join(DATA_DIR, table)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{table}.csv")
    df.to_csv(out_path, index=False)
    print(f"  wrote {out_path}  ({len(df):,} rows)")


def download_history(symbol: str) -> pd.DataFrame:
    """Download daily history for one symbol. Returns empty df on failure."""
    try:
        hist = yf.Ticker(symbol).history(period=PERIOD, auto_adjust=False)
    except Exception as exc:  # noqa: BLE001 - want to keep going for other tickers
        print(f"  ! {symbol}: download failed ({exc})")
        return pd.DataFrame()
    if hist is None or hist.empty:
        print(f"  ! {symbol}: no data returned")
        return pd.DataFrame()
    return hist


def build_listed_companies() -> pd.DataFrame:
    return pd.DataFrame(COMPANIES, columns=COMPANY_COLUMNS)


def build_daily_prices() -> pd.DataFrame:
    frames = []
    print("Downloading daily prices...")
    for ticker, *_ in COMPANIES:
        hist = download_history(ticker)
        if hist.empty:
            continue
        df = hist.reset_index()
        df["ticker"] = ticker
        df = df.rename(
            columns={
                "Date": "trade_date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Adj Close": "adj_close",
                "Volume": "volume",
            }
        )
        df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y-%m-%d")
        # Pre-compute volatility helper columns (per ticker).
        df["daily_return_pct"] = (df["close"].pct_change() * 100).round(4)
        df["daily_range_pct"] = ((df["high"] - df["low"]) / df["open"] * 100).round(4)
        for col in ["open", "high", "low", "close", "adj_close"]:
            df[col] = df[col].round(2)
        df["volume"] = df["volume"].fillna(0).astype("int64")
        frames.append(
            df[[
                "ticker", "trade_date", "open", "high", "low", "close",
                "adj_close", "volume", "daily_return_pct", "daily_range_pct",
            ]]
        )
        print(f"  {ticker}: {len(df):,} rows")
        time.sleep(PAUSE_SECONDS)

    if not frames:
        raise SystemExit(
            "ERROR: no price data downloaded for any ticker. "
            "Check your network connection / yfinance availability and retry."
        )
    return pd.concat(frames, ignore_index=True)


def build_index_prices() -> pd.DataFrame:
    print("Downloading IDX Composite index (IHSG / ^JKSE)...")
    hist = download_history(INDEX_SYMBOL)
    if hist.empty:
        raise SystemExit(
            "ERROR: could not download the IHSG (^JKSE) index. "
            "Check your network connection / yfinance availability and retry."
        )
    df = hist.reset_index().rename(
        columns={
            "Date": "index_date",
            "Open": "index_open",
            "High": "index_high",
            "Low": "index_low",
            "Close": "index_close",
            "Volume": "index_volume",
        }
    )
    df["index_date"] = pd.to_datetime(df["index_date"]).dt.strftime("%Y-%m-%d")
    df["index_return_pct"] = (df["index_close"].pct_change() * 100).round(4)
    for col in ["index_open", "index_high", "index_low", "index_close"]:
        df[col] = df[col].round(2)
    df["index_volume"] = df["index_volume"].fillna(0).astype("int64")
    print(f"  ^JKSE: {len(df):,} rows")
    return df[[
        "index_date", "index_open", "index_high", "index_low",
        "index_close", "index_volume", "index_return_pct",
    ]]


def main() -> None:
    print(f"Output directory: {DATA_DIR}\n")

    companies = build_listed_companies()
    daily = build_daily_prices()
    index = build_index_prices()

    print("\nWriting CSV files...")
    write_csv(companies, "listed_companies")
    write_csv(daily, "daily_prices")
    write_csv(index, "index_prices")

    print("\nDone. Summary:")
    print(f"  listed_companies : {len(companies):,} rows")
    print(f"  daily_prices     : {len(daily):,} rows ({daily['ticker'].nunique()} tickers)")
    print(f"  index_prices     : {len(index):,} rows")


if __name__ == "__main__":
    main()

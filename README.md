# Currency Wars

**English** · [Bahasa Indonesia](README.id.md)

An interactive dashboard that tracks how the Indonesian rupiah (IDR) and other currencies move against the IMF's Special Drawing Rights (SDR), and compares each currency against ASEAN and world peers using an x-bar control chart. It opens on IDR, supports switching to any currency in the dataset, and runs in the browser from a single `index.html` file.

- **Live dashboard:** https://febrianggi.github.io/currency-wars/

## Key findings

Across the saved monthly snapshot in [`data/rates.json`](data/rates.json) (171 currencies across 67 month-ends from April 2021 to October 2026; updated daily by GitHub Actions):

- **IDR sits on the weak side of its control band:** Over the 67 monthly observations, IDR averages **21,296.51** per 1 SDR (sample SD **1,450.77**, lower control limit **18,394.97**, upper control limit **24,198.05**).
- **Six consecutive out-of-control months in 2026:** IDR stayed above the upper control limit (weaker than normal historical variation) every month from May 2026 (**24,453.90**) through October 2026 (**24,842.63**), with the latest daily live reading at **24,594.29** per SDR.
- **Cross-currency context:** Standardizing each currency into a z-score against its own history separates broad dollar/SDR moves from country-specific weakness across ASEAN and global peers. Open the live dashboard for the most recent daily values.

## What the dashboard shows

| Section | Content |
|---|---|
| **Overview** | Latest rate for the selected currency, a gauge showing its position between control limits, summary cards, and its per-SDR x-bar control chart with center line, upper and lower control limits, out-of-control months, a date range selector, and optional recomputed limits. |
| **vs World** | Control chart across every currency in the dataset (each point is a z-score), highlighting the limits and currencies currently outside them. |
| **vs ASEAN** | The same z-score comparison for the ten ASEAN currencies. Appears whenever the selected currency is an ASEAN member. |
| **Country view** | Plain-language summary for the selected currency, its monthly z-score control chart, and its yearly trajectory compared against a second currency. |
| **Data tables** | Tables for the selected currency, world ranking, and two-currency comparison with date filtering, search, status filter, column sorting, and CSV download. |
| **Live data and sources** | Status of the XE feed, in-browser Python scraper button, custom Excel workbook loader, and method notes. |

The dashboard includes light and dark modes. Every chart, table, and summary updates automatically when you change the currency or date range at the top.

## How to read the charts

- **Rate direction:** Rates are quoted in units of the selected currency per 1 SDR. A higher value means more local currency is needed for 1 SDR, which means a **weaker** currency.
- **Control limits:** The center line is the sample mean across the selected period, and the upper/lower control limits sit two sample standard deviations (`mean ± 2 SD`) on either side. Any point beyond a limit is flagged as out of control relative to historical variation.
- **Z-score comparisons:** To compare currencies on different scales, each currency is standardized against its own history. A positive z-score means the currency is weaker than its own historical average; yearly values are the average of that year's monthly z-scores.

## How to run locally

Serve the repository root over HTTP so `index.html` can fetch `data/rates.json` cleanly:

```bash
python -m http.server 8000
```

Then open http://localhost:8000 in your browser. Stop the server with `Ctrl+C`.

If you edit [`scripts/xe_scraper.py`](scripts/xe_scraper.py), refresh the embedded browser copy and run the unit tests from the repository root:

```bash
python scripts/embed_python.py
python -m unittest discover -s tests
```

## Live data from XE

Rates come from the [XE Currency Exchange Rate Tables](https://www.xe.com/currencytables/?from=XDR) using SDR (`XDR`) as the base:

```text
XE -> scripts/update_data.py (GitHub Actions, hourly) -> data/rates.json -> index.html
```

- [`scripts/xe_scraper.py`](scripts/xe_scraper.py) parses an XE table using only the Python standard library.
- [`scripts/update_data.py`](scripts/update_data.py) fills any missing month-ends and appends the latest daily table to [`data/rates.json`](data/rates.json). The workflow [`.github/workflows/update-data.yml`](.github/workflows/update-data.yml) runs hourly and commits only when XE publishes new data (typically once per day).
- `index.html` loads `data/rates.json` on startup and refreshes every 30 minutes while open. The newest daily reading appears as one extra **live** point after the latest month-end until the month closes.
- **Run the Python scraper here** (in **Live data and sources**) loads Pyodide to run the embedded Python scraper in the browser. Because XE does not send CORS headers for direct browser fetches, the browser normally blocks the request, explains why, and keeps the data from `data/rates.json`.

To populate a fresh fork, open the **Actions** tab, select **Update XE rates**, and click **Run workflow**. Check XE's terms of use before scraping at scale; if an automated run fails, the dashboard keeps its previous dataset.

## Use your own Excel workbook

In **Live data and sources**, select or drop an `.xlsx` file to inspect your own rates locally in the browser (nothing is uploaded). The bundled [`data.xlsx`](data.xlsx) works out of the box. In Chrome and Edge, **Refresh from the same file** reloads updates after you save in Excel.

Place dates in column A and currency codes in row 1 of a sheet named **Global Data**. The dashboard extracts IDR and the ten ASEAN currencies from that sheet; `Data IDR`, `Data ASEAN`, `IDR VS ASEAN`, and `IDR VS Global` are optional.

## Notebooks

- [`currency_control_chart.ipynb`](currency_control_chart.ipynb): reproduces the main calculations in Python (Google Colab), including z-scores, selected-currency and world control charts, and yearly two-currency comparisons.
- [`fetch_xe_data.ipynb`](fetch_xe_data.ipynb): downloads monthly XE rates into an Excel workbook.

## Repository structure

| Path | Contents |
|---|---|
| [`index.html`](index.html) | Self-contained dashboard |
| [`data/rates.json`](data/rates.json) | Monthly history and latest daily reading updated by GitHub Actions |
| [`scripts/xe_scraper.py`](scripts/xe_scraper.py) | XE table parser (also embedded in `index.html`) |
| [`scripts/update_data.py`](scripts/update_data.py) | Updates `data/rates.json` |
| [`scripts/embed_python.py`](scripts/embed_python.py) | Syncs `xe_scraper.py` into `index.html` |
| [`tests/test_xe_scraper.py`](tests/test_xe_scraper.py) | Unit tests for the scraper |
| [`.github/workflows/update-data.yml`](.github/workflows/update-data.yml) | Hourly automated update workflow |
| [`currency_control_chart.ipynb`](currency_control_chart.ipynb) | Colab analysis notebook |
| [`fetch_xe_data.ipynb`](fetch_xe_data.ipynb) | Colab XE data fetcher |
| [`data.xlsx`](data.xlsx) | Bundled fallback Excel workbook |

## Technical notes

- Plain HTML, CSS, and JavaScript in one file with no build step.
- [Chart.js](https://www.chartjs.org/) 4.4.1 and [SheetJS](https://sheetjs.com/) 0.18.5 are inlined. Pyodide 0.26.4 is downloaded only when you click the Python scraper button.

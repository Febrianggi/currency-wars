# Currency Wars

An interactive dashboard that shows how any currency behaves against the IMF's Special Drawing Rights (SDR) and how it compares with ASEAN and world currencies. It opens on the Indonesian rupiah (IDR) and you can pick any other currency. It uses an x̄ control chart and runs from a single `index.html` file in the browser.

Live page: https://febrianggi.github.io/currency-wars/

## What it shows

| Section | Content |
|---|---|
| Overview | The latest value for the selected currency, a meter showing where it sits between the limits, a row of key numbers, and its per SDR control chart with center line, upper and lower control limits, out-of-control months, a date range and optional recomputed limits |
| vs World | A control chart across every currency in the data (each point is a z-score), with the limits and the currencies that fall outside them |
| vs ASEAN | The same chart for the ten ASEAN currencies. It appears only when the selected currency is an ASEAN member |
| Country view | A written conclusion for the selected currency, its monthly z-score control chart, and its yearly position against a second currency |
| Data tables | Selected currency, world ranking and selected-vs-compared tables with a date range, search, status filter, sorting and CSV download |
| Live data and sources | Status of the XE feed, the Python scraper, your own workbook, and the method notes |

The page has a light and a dark mode. Every chart and sentence updates when you change the currency or the period at the top.

## How to read it

The rate is units of the selected currency per one SDR, so a higher value means a weaker currency. The center line is the mean, and the control limits sit two sample standard deviations either side. A point beyond a limit means the currency moved further from its own average than normal variation explains.

For comparisons, each currency is standardized against its own history (z-score). A positive z-score means the currency is weaker than its own average, and a z-score beyond the limits means it is out of control. Yearly values are the average of that year's monthly z-scores.

## Live data from XE

The rates come from the XE Currency Exchange Rate Tables with SDR (XDR) as the base: https://www.xe.com/currencytables/?from=XDR

```
XE  ->  scripts/update_data.py (GitHub Actions, every hour)  ->  data/rates.json  ->  index.html
```

- `scripts/xe_scraper.py` reads an XE table. It uses only the Python standard library.
- `scripts/update_data.py` adds any missing month ends and the latest daily table to `data/rates.json`. The workflow `.github/workflows/update-data.yml` runs it every hour and commits only when XE published something new (XE updates its table once a day).
- `index.html` reads `data/rates.json` when it opens and every 30 minutes while it stays open. The newest daily table appears as one extra point labelled "live" after the last month end. It becomes a normal month-end value once the month closes.
- The Python code is also inside `index.html`. **Run the Python scraper here** (in the Live data section) loads Pyodide, which is Python in the browser, and runs that code. A browser can only read XE directly if XE allows it. XE does not send the headers for that, so the browser normally blocks the request and the page keeps the data from `data/rates.json`. The page says so when it happens.

First time: open the **Actions** tab, choose **Update XE rates**, and press **Run workflow**. This fills the months after the last row of `data.xlsx` and adds the live value.

Edited `scripts/xe_scraper.py`? Run `python scripts/embed_python.py` so the copy in the page matches, and `python -m unittest discover -s tests` to check.

Check XE's terms of use before scraping at scale. The job waits between requests, but XE can change its layout or block automated access. If a run fails, the page keeps the previous data.

## Use your own Excel workbook

The dashboard can also read a workbook directly. In the **Live data and sources** section, choose an `.xlsx` file or drop it on the drop area. A built-in copy (`data.xlsx`) works without choosing a file. Nothing is uploaded; the file is read in your browser. In Chrome and Edge, **Refresh from the same file** re-reads the file after you save it in Excel.

`data.xlsx` has one sheet named `Global Data` (dates in column A, currency codes in row 1). The dashboard takes the IDR series and the ten ASEAN currencies from it. The sheets `Data IDR`, `Data ASEAN`, `IDR VS ASEAN` and `IDR VS Global` are optional.

## Notebooks

- `currency_control_chart.ipynb` repeats the main calculations in Python in Google Colab: z-scores, the control chart of the selected currency, the world control chart and the yearly position of two currencies.
- `fetch_xe_data.ipynb` downloads the monthly rates from XE into an Excel workbook.

## Files

```
index.html                         the whole dashboard
data/rates.json                    monthly rates and the live value, refreshed by the workflow
scripts/xe_scraper.py              reads an XE table (also embedded in index.html)
scripts/update_data.py             updates data/rates.json
scripts/embed_python.py            copies xe_scraper.py into index.html
tests/test_xe_scraper.py           tests for the scraper
.github/workflows/update-data.yml  hourly job
currency_control_chart.ipynb       Colab notebook with the same calculations
fetch_xe_data.ipynb                Colab notebook that downloads the rates from XE
data.xlsx                          the source workbook
```

## Technical notes

- Plain HTML, CSS and JavaScript in one file. No build step is needed to use it.
- Charts use [Chart.js](https://www.chartjs.org/) 4.4.1 and Excel parsing uses [SheetJS](https://sheetjs.com/) 0.18.5. Both are inlined. Pyodide 0.26.4 is downloaded only when you press the Python button.

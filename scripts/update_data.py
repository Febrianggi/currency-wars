"""Refresh data/rates.json from XE. Run by .github/workflows/update-data.yml, or by hand:

    python scripts/update_data.py                       # add missing month ends and refresh the live row
    python scripts/update_data.py --init data.xlsx      # first run: build the store from the workbook
"""
import argparse
import json
import re
import sys
import time
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import xe_scraper as xe  # noqa: E402

STORE = Path(__file__).resolve().parent.parent / "data" / "rates.json"
UA = {"User-Agent": "Mozilla/5.0 (compatible; currency-wars-dashboard)"}


def get(url, tries=3):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # network errors, 403, 429 ...
            print(f"  retry {k + 1}/{tries}: {e}", file=sys.stderr)
            time.sleep(5 * (k + 1))
    raise RuntimeError(f"could not download {url}")


def month_ends(after, until):
    """Month-end dates strictly after ``after`` and strictly before ``until`` (both date objects)."""
    d = after.replace(day=1)
    while True:
        d = (d + timedelta(days=32)).replace(day=1)
        end = (d + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        if end >= until:
            return
        yield end


def init_from_workbook(path):
    from openpyxl import load_workbook

    ws = load_workbook(path, read_only=True, data_only=True)["Global Data"]
    rows = list(ws.iter_rows(values_only=True))
    head = rows[0]
    n = next((i for i, c in enumerate(head) if i and c in (None, "")), len(head))
    codes = [str(c).strip() for c in head[1:n]]
    store = {"source": xe.table_url(), "base": xe.BASE, "unit": "units of currency per 1 SDR",
             "updated": None, "codes": codes, "dates": [], "rates": {c: [] for c in codes}, "live": None}
    for r in rows[1:]:
        d = r[0].date().isoformat() if isinstance(r[0], datetime) else str(r[0] or "")[:10]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
            continue  # skips blank and summary rows
        store["dates"].append(d)
        for c, v in zip(codes, r[1:n]):
            store["rates"][c].append(float(v))
    return store


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", metavar="XLSX", help="build the store from a workbook with a 'Global Data' sheet")
    ap.add_argument("--no-history", action="store_true", help="only refresh the live row")
    a = ap.parse_args()
    store = init_from_workbook(a.init) if a.init else json.loads(STORE.read_text())
    before = json.dumps(store, sort_keys=True)

    if not a.no_history:
        last = date.fromisoformat(store["dates"][-1])
        for end in month_ends(last, date.today()):
            print("month end", end)
            try:
                rates, _ = xe.parse_table(get(xe.table_url(end.isoformat())))
            except Exception as e:
                print(f"  skipped {end}: {e}", file=sys.stderr)
                break  # keep months in order; the next run tries again
            xe.merge_month(store, end.isoformat(), rates)
            time.sleep(2)

    try:
        rates, asof = xe.parse_table(get(xe.table_url()))
        xe.set_live(store, rates, asof)
        store["updated"] = asof
        print("live rates as of", asof)
    except Exception as e:
        print(f"live row not refreshed: {e}", file=sys.stderr)

    if a.init or json.dumps(store, sort_keys=True) != before:
        STORE.parent.mkdir(exist_ok=True)
        STORE.write_text(xe.dumps(store) + "\n")
        print("data/rates.json updated")
    else:
        print("nothing new from XE")


if __name__ == "__main__":
    main()

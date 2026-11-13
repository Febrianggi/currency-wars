"""Scraper for the XE Currency Exchange Rate Tables (base currency XDR, the IMF's SDR).

Source: https://www.xe.com/currencytables/?from=XDR

This file uses only the Python standard library, so the very same code runs in two places:

* on a computer or in GitHub Actions (``scripts/update_data.py`` imports it), and
* inside the dashboard page, where Pyodide (Python in WebAssembly) runs a copy of it.

``parse_table`` and ``merge_month`` are pure functions with no network access, so they are easy to test.
"""
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser

URL = "https://www.xe.com/currencytables/"
BASE = "XDR"
_STAMP = re.compile(r"([A-Z][a-z]{2,8}\.? \d{1,2}, \d{4}, \d{1,2}:\d{2}(?::\d{2})? ?UTC)")


def table_url(day=None):
    """URL of the XE table in units of currency per 1 SDR, for a date (YYYY-MM-DD) or for now."""
    return f"{URL}?from={BASE}" + (f"&date={day}" if day else "")


class _Page(HTMLParser):
    """Collects every <table> as a list of rows, and the visible text of the page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables, self.text = [], []
        self._row = self._cell = None
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._depth += 1
            self.tables.append([])
        elif tag == "tr" and self.tables:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None and self.tables:
            if self._row:
                self.tables[-1].append(self._row)
            self._row = None
        elif tag == "table":
            self._depth = max(0, self._depth - 1)

    def handle_data(self, data):
        self.text.append(data)
        if self._cell is not None:
            self._cell.append(data)


def _number(text):
    return float(re.sub(r"[^0-9eE+\-.]", "", text or ""))


def parse_table(html):
    """Return ``(rates, asof)`` from one XE page.

    ``rates`` maps a currency code to units of that currency per 1 SDR. ``asof`` is the timestamp XE prints
    above the table as an ISO string in UTC (or ``None`` if it is not found).
    """
    page = _Page()
    page.feed(html)
    for rows in page.tables:
        head = next((r for r in rows if any(c.lower() == "currency" for c in r)), None)
        if head is None:
            continue
        ic = next(i for i, c in enumerate(head) if c.lower() == "currency")
        iv = next((i for i, c in enumerate(head) if c.lower().startswith("units per")), None)
        if iv is None:
            continue
        rates = {}
        for r in rows[rows.index(head) + 1:]:
            if len(r) <= max(ic, iv):
                continue
            code = r[ic].split()[0].upper() if r[ic] else ""
            if not re.fullmatch(r"[A-Z0-9]{3,5}", code):
                continue
            try:
                rates[code] = _number(r[iv])
            except ValueError:
                continue
        if rates:
            m = _STAMP.search(" ".join(page.text))
            return rates, _iso(m.group(1)) if m else None
    raise ValueError("No XE rate table found (the page layout may have changed or access was blocked).")


def _iso(stamp):
    stamp = stamp.replace(".", "").replace(" UTC", "").strip()
    for fmt in ("%b %d, %Y, %H:%M:%S", "%b %d, %Y, %H:%M", "%B %d, %Y, %H:%M:%S", "%B %d, %Y, %H:%M"):
        try:
            return datetime.strptime(stamp, fmt).replace(tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            pass
    return None


def merge_month(store, day, rates):
    """Add one month-end row to the store. A code missing from ``rates`` carries its previous value."""
    if day in store["dates"]:
        return False
    store["dates"].append(day)
    for code in store["codes"]:
        prev = store["rates"][code][-1] if store["rates"][code] else None
        store["rates"][code].append(rates.get(code, prev))
    return True


def set_live(store, rates, asof):
    """Keep the latest daily table next to the monthly history, for the month in progress."""
    live = {code: rates[code] for code in store["codes"] if code in rates}
    if len(live) < len(store["codes"]) * 0.8:
        raise ValueError(f"Live table has only {len(live)} of {len(store['codes'])} known codes; not using it.")
    for code in store["codes"]:  # carry forward the few that are missing today
        live.setdefault(code, store["rates"][code][-1])
    store["live"] = {"asof": asof, "rates": live}


async def fetch_in_browser(day=None):
    """Browser version (Pyodide). XE does not send CORS headers, so this normally fails in the page; the
    dashboard then keeps using data/rates.json, which the scheduled job refreshes."""
    from pyodide.http import pyfetch  # only exists inside Pyodide

    resp = await pyfetch(table_url(day))
    if not resp.ok:
        raise RuntimeError(f"XE answered HTTP {resp.status}")
    return parse_table(await resp.string())


def dumps(store):
    return json.dumps(store, separators=(",", ":"), sort_keys=False)

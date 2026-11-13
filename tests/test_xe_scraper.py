import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import xe_scraper as xe  # noqa: E402
from update_data import month_ends  # noqa: E402

PAGE = """<html><body><h1>XE Currency Tables</h1><p>Nov 12, 2026, 17:00 UTC</p>
<table><thead><tr><th>Currency</th><th>Name</th><th>Units per XDR</th><th>XDR per unit</th></tr></thead>
<tbody><tr><td>USD</td><td>US Dollar</td><td>1.3494003</td><td>0.7410699</td></tr>
<tr><td>IDR</td><td>Indonesian Rupiah</td><td>22,345.50</td><td>0.0000447</td></tr>
<tr><td>EUR</td><td>Euro</td><td>1.2204131</td><td>0.8193947</td></tr></tbody></table></body></html>"""


class Scraper(unittest.TestCase):
    def test_parse(self):
        rates, asof = xe.parse_table(PAGE)
        self.assertEqual(rates, {"USD": 1.3494003, "IDR": 22345.5, "EUR": 1.2204131})
        self.assertEqual(asof, "2026-11-12T17:00:00Z")

    def test_no_table(self):
        with self.assertRaises(ValueError):
            xe.parse_table("<html><body>Access denied</body></html>")

    def test_merge_and_live(self):
        store = {"codes": ["USD", "IDR", "EUR", "JPY", "XXX"], "dates": ["2026-04-30"],
                 "rates": {"USD": [1.0], "IDR": [20000.0], "EUR": [0.9], "JPY": [150.0], "XXX": [5.0]}, "live": None}
        self.assertTrue(xe.merge_month(store, "2026-05-31", {"USD": 1.1, "IDR": 21000.0, "EUR": 1.0, "JPY": 151.0}))
        self.assertFalse(xe.merge_month(store, "2026-05-31", {"USD": 9}))
        self.assertEqual(store["rates"]["XXX"], [5.0, 5.0])  # missing code carries forward
        xe.set_live(store, {"USD": 1.2, "IDR": 22000.0, "EUR": 1.1, "JPY": 152.0}, "2026-11-12T17:00:00Z")
        self.assertEqual(store["live"]["rates"]["XXX"], 5.0)
        with self.assertRaises(ValueError):
            xe.set_live(store, {"USD": 1.2}, "x")

    def test_month_ends(self):
        got = [d.isoformat() for d in month_ends(date(2026, 4, 30), date(2026, 11, 13))]
        self.assertEqual(got, ["2026-05-31", "2026-06-30", "2026-07-31", "2026-08-31", "2026-09-30", "2026-10-31"])
        self.assertEqual(list(month_ends(date(2026, 10, 31), date(2026, 11, 13))), [])

    def test_page_carries_same_python(self):
        root = Path(__file__).resolve().parent.parent
        html = (root / "index.html").read_text(encoding="utf-8")
        code = (root / "scripts" / "xe_scraper.py").read_text(encoding="utf-8").rstrip("\n")
        self.assertIn(code + "\n</script>", html, "run: python scripts/embed_python.py")


if __name__ == "__main__":
    unittest.main()

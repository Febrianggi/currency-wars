"""Copy scripts/xe_scraper.py into index.html, so the Python shown and run in the page is the repo's code.

Run this after editing scripts/xe_scraper.py:  python scripts/embed_python.py
"""
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
html = (root / "index.html").read_text(encoding="utf-8")
code = (root / "scripts" / "xe_scraper.py").read_text(encoding="utf-8").rstrip("\n")
assert "</script" not in code
pattern = re.compile(r'(<script type="text/x-python" id="xe-py">).*?(</script>)', re.S)
new, n = pattern.subn(lambda m: m.group(1) + code + "\n" + m.group(2), html)
assert n == 1, "marker script not found in index.html"
(root / "index.html").write_text(new, encoding="utf-8")
print("index.html now carries the current xe_scraper.py")

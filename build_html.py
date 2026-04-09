# -*- coding: utf-8 -*-
"""从 data.json 注入 window.__ROWS__ 到 场景一.html（请先运行 export_data.py 从 xlsx 更新 data.json）"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
rows = data["rows"] if isinstance(data, dict) and "rows" in data else data
payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
html = (ROOT / "场景一.html").read_text(encoding="utf-8")
pat = r"<script>window\.__ROWS__\s*=\s*.*?</script>"
rep = f"<script>window.__ROWS__ = {payload};</script>"
new_html, n = re.subn(pat, rep, html, count=1, flags=re.DOTALL)
if n != 1:
    raise SystemExit("未能替换 __ROWS__，请检查 场景一.html 中是否存在 <script>window.__ROWS__ = ...</script>")
(ROOT / "场景一.html").write_text(new_html, encoding="utf-8")
print("OK, injected", len(rows), "rows")

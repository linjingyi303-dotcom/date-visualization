# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).resolve().parent
main = (ROOT / "场景一.html").read_text(encoding="utf-8")
charts = (ROOT / "_charts_only.js").read_text(encoding="utf-8")
tail = (ROOT / "_tail_custom.js").read_text(encoding="utf-8")

s = main.find("  /** 全图统一网格线（较明显但仍不抢数据） */")
if s < 0:
    raise SystemExit("grid block start not found")
e = main.find("  const CHART_AXIS_DOMAIN_STROKE", s)
if e < 0:
    raise SystemExit("CHART_AXIS not found")
main = main[:s] + main[e:]

corrupt = "\n\n          .attr(\"href\", href)"
c = main.find(corrupt)
if c < 0:
    raise SystemExit("corruption marker not found")
head = main[:c]

out = head + "\n" + charts + tail + "\n    </script>\n</body>\n</html>\n"
(ROOT / "场景一.html").write_text(out, encoding="utf-8")
print("OK, length", len(out))

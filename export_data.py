# -*- coding: utf-8 -*-
"""导出完整表格为 data.json（含「编码备注」，供悬停展示；可视化列由页面逻辑排除）。"""
import json
import pandas as pd

path = r"c:\Users\林靖怡\Desktop\数据\场景一\数据表格.xlsx"
df = pd.read_excel(path)
cols = list(df.columns)
print("COLS:", cols)

records = []
for _, row in df.iterrows():
    rec = {}
    for c in df.columns:
        v = row[c]
        if pd.isna(v):
            rec[str(c)] = ""
        elif isinstance(v, (int, float)) and float(v).is_integer():
            rec[str(c)] = int(v)
        else:
            rec[str(c)] = str(v)
    records.append(rec)

out = r"c:\Users\林靖怡\Desktop\数据可视化\data.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump({"columns": [str(c) for c in df.columns], "rows": records}, f, ensure_ascii=False, indent=2)
print("saved", out, "rows", len(records))

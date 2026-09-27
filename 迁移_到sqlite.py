# 迁移_到sqlite.py —— 一次性工具：把 money.json 的账本搬进 money.db
# 用法：在 money-ledger 目录下执行 python 迁移_到sqlite.py
# 说明：不会删 money.json（留着当备份）；重复运行会重复插入，所以只跑一次。

import json
import sqlite3

with open("money.json", "r", encoding="utf-8") as f:
    records = json.load(f)

conn = sqlite3.connect("money.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS bills (id INTEGER PRIMARY KEY, item TEXT, money INTEGER, category TEXT)")

rows = []
for i in range(len(records)):
    item = records[i].get("item", "未知")
    money = int(records[i].get("money", 0))
    category = records[i].get("category", "未分类")
    rows.append((item, money, category))

cur.executemany("INSERT INTO bills (item, money, category) VALUES (?, ?, ?)", rows)
conn.commit()

cur.execute("SELECT COUNT(*) FROM bills")
print("money.db 现在有", cur.fetchone()[0], "条")

cur.execute("SELECT item, money, category FROM bills LIMIT 3")
for item, money, category in cur.fetchall():
    print("  ", item, money, category)

conn.close()
print("迁移完成（money.json 没动，留着当备份）")

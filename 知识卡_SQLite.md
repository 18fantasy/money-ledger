# 知识卡 · SQLite（v2.0a · **逐行教学版**）

> **这一版总共只做 4 个动作**：①顶部加 import＋连接＋建表 ②把"读 json"换成 `SELECT` ③每收一笔加 `INSERT` ④把"写回 json"删掉换成 `commit()+close()`
> **要求**：全部**手打**，不许复制粘贴。打完 Run 一次，看输出有没有变。
> **判据**：屏幕和 `报表.txt` **一个字都不变** —— 换的只是"数据存在哪"。

---

## 第 1 节 · SQLite 是什么（先有个画面）

- 它是**一个文件**，整个数据库就在这个文件里（我们的叫 `money.db`）
- Python **自带** `sqlite3`，不用装任何东西、不用开服务器
- 里面是**表**（像 Excel 的一个 sheet）：行 = 一条记录，列 = 一个字段
- 我们的表叫 **`bills`**，四列：

| id | item | money | category |
|---|---|---|---|
| 1 | 苹果 | 5 | 未分类 |
| 2 | 手表 | 100 | 未分类 |
| … | | | |

`id` 是**自动编号**的主键（不用你管，插一行它自己 +1）。

---

## 第 2 节 · 先看一个能跑的 12 行小例子（逐行注释）

```python
import sqlite3                                              # ① 拿工具箱
conn = sqlite3.connect("demo.db")                           # ② 打开数据库文件（没有就新建）
cur = conn.cursor()                                         # ③ 拿"遥控器"
cur.execute("CREATE TABLE IF NOT EXISTS demo (name TEXT, n INTEGER)")   # ④ 建表（已有就不建）
cur.execute("INSERT INTO demo (name, n) VALUES (?, ?)", ("张三", 14))    # ⑤ 插一行
conn.commit()                                               # ⑥ 保存（不写这句，关掉就没了）
cur.execute("SELECT name, n FROM demo")                     # ⑦ 查询
for name, n in cur.fetchall():                              # ⑧ 取回所有行，每行是一个元组
    print(name, n)                                          # ⑨ 打印
cur.execute("UPDATE demo SET n = ? WHERE name = ?", (20, "张三"))        # ⑩ 改（先不用管）
conn.commit()                                               # ⑪ 再保存
conn.close()                                                # ⑫ 关门
```

**跑之前你能猜到输出吗？** → `张三 14`。把它存成 `demo.py` 跑一次试试（跑完目录里会多一个 `demo.db`）。

---

## 第 3 节 · 每个动作为什么（汇总表）

| 代码 | 人话 | 为什么必须有它 / 少了会怎样 |
|---|---|---|
| `import sqlite3` | 拿工具箱 | 不 import → `NameError: name 'sqlite3' is not defined` |
| `sqlite3.connect("money.db")` | 打开数据库文件 | 文件不存在会**自动新建**（所以第一次跑就成功） |
| `conn.cursor()` | 拿遥控器 | 所有 SQL 都要通过 `cur.execute(...)` 发出去 |
| `CREATE TABLE IF NOT EXISTS bills (...)` | 建表，有了就跳过 | 少了 `IF NOT EXISTS` → **第二次运行报错** `table bills already exists` |
| `INSERT INTO bills (...) VALUES (?, ?, ?)` | 插一行 | `?` 是**占位符**，真正的值从**第二个参数**（元组）按顺序填进去 |
| `conn.commit()` | 保存 | **不写 = 没存**。程序一关，刚插的行就没了（这是新手最常踩的坑） |
| `SELECT item, money, category FROM bills` | 查出这三列 | 查出来的每一行是**元组**，不是字典 |
| `cur.fetchall()` | 把结果全取回来 | 不取回来，结果就还在数据库那边躺着 |
| `for item, money, category in ...` | 元组**解包** | 和你写过的 `for k, v in 排名:` 是**同一个动作** |
| `conn.close()` | 关门 | 程序要结束了再关；**中途关掉，后面再用 `cur` 会报** `Cannot operate on a closed database` |

---

## 第 4 节 · 套到 `ledger.py` 上（**4 处，完整前后对照**）

### 第 1 处 · 文件最上面

**你现在写的**（表名错了、多了两行）：

```python
import sqlite3
import json
conn = sqlite3.connect("money.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS money (item TEXT, money INTEGER)")
conn.commit()
conn.close()
```

**改成**：

```python
import sqlite3
import json

conn = sqlite3.connect("money.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS bills (id INTEGER PRIMARY KEY, item TEXT, money INTEGER, category TEXT)")
```

**为什么**：
- 表名必须是 **`bills`**、四列写全 —— 因为 `money.db` 里**已经有这张表**（13 条数据在里面）；你叫 `money` 就等于另开一张空表，读的还是老表 → 看起来"数据不见了"
- **`conn.commit()` / `conn.close()` 删掉** —— 后面还要用 `cur` 读、写；现在关掉会报 `Cannot operate on a closed database`（表在库里已经建好了，也不需要 commit）

### 第 2 处 · 读账本那一段

**原文**：

```python
records = []
total = 0
try:
    with open("money.json", "r", encoding="utf-8") as f:
        records = json.load(f)
except FileNotFoundError:
    records = []
```

**改成**：

```python
records = []
total = 0
cur.execute("SELECT item, money, category FROM bills")
for item, money, category in cur.fetchall():
    records.append({"item": item, "money": money, "category": category})
```

**逐行为什么**：
1. `SELECT item, money, category FROM bills` → "把 `bills` 表这三列**全拿出来**"
2. `cur.fetchall()` → 把结果**全取回来**，形状是 `[("苹果", 5, "未分类"), ("手表", 100, "未分类"), ...]`（**列表套元组**）
3. `for item, money, category in ...` → 每个元组**解包**成三个变量（**和 `for k, v in 排名:` 同一个动作**）
4. `records.append({...})` → **重新拼成你原来的形状**（列表套字典）→ **所以后面 60 行代码一个字都不用改**

**`try/except FileNotFoundError` 为什么不要了**：数据库文件/表在上面第 1 处已经保证存在了，不会有"文件找不到"这回事。

### 第 3 处 · 每收一笔

**原文**（在 `while` 循环里）：

```python
    records.append({"item": parts[0], "money": int(parts[1]), "category": parts[2]})
```

**在这一行下面加两行**：

```python
    cur.execute("INSERT INTO bills (item, money, category) VALUES (?, ?, ?)", (parts[0], int(parts[1]), parts[2]))
    conn.commit()
```

**为什么**：
- 你收一笔，**内存里的 `records` 加一条**（老写法，屏幕清单/汇总要用），**数据库里也插一条**（新写法，存下来）
- `?` 三个，第二个参数的元组也三个，**按顺序一一对应**：第 1 个 `?` ← `parts[0]`（物品），第 2 个 ← `int(parts[1])`（金额），第 3 个 ← `parts[2]`（类别）
- **`commit()` 紧跟其后**：一收到就落盘，程序崩了也不丢

### 第 4 处 · 文件最后

**原文**：

```python
with open("money.json", "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False)
```

**改成**：

```python
conn.commit()
conn.close()
```

**为什么**：
- 数据**已经一笔一笔进库了**（第 3 处），不需要再"把整个列表写回文件"
- 收尾了：`commit()` 保证全部落盘 → `close()` 关门
- **`json.dump` 删掉** → 副作用：跑完 `money.json` **不再被改动**（正好当备份留着）

---

## 第 5 节 · 4 步串起来（数据流图）

```
                        ┌──────────────────────────────┐
   启动 ──► 连库/建表 ──►│  SELECT  FROM bills          │──► records（列表套字典，形状不变）
                        └──────────────────────────────┘            │
                                                                    ▼
                                                        （下面 60 行老代码全不动：
                                                         清单/汇总/统计/排序/报表）
    收一笔 ──► records.append(...)  ──►  INSERT INTO bills ──► commit()
                                                                    │
                                                                    ▼
                                                        money.db（磁盘上，永久）
    收工 ──► conn.commit() ──► conn.close()
```

**一句话**：**"读"和"写"两头的存储换成了 SQLite，中间那 60 行一个字没变。**

---

## 第 6 节 · 报错对照表（撞上了就来查）

| 报错 | 原因 | 怎么修 |
|---|---|---|
| `no such table: bills` | 建表那句没写/写错表名 | 检查第 1 处的表名是 `bills` |
| `table bills already exists` | 建表时漏了 `IF NOT EXISTS` | 补上 |
| `no column named category` | 建表时少写了 `category` 列 | 列写全（见第 1 处） |
| `Cannot operate on a closed database` | 中途 `close()` 了 | 把 `close()` 挪到最后（第 4 处） |
| `Incorrect number of bindings supplied` | `?` 的个数和元组里的个数不一样 | 三个 `?` 对三个值 |
| 屏幕数据变少/为空 | 建成了另一张表（表名不对） | 表名统一 `bills` |

---

## 第 7 节 · 判据（改完自己验）

- [ ] 屏幕：13 行清单 ＋ 汇总 ＋ 6 行"按类别"（金额降序）—— **与搬之前一字不差**
- [ ] `报表.txt` 6 行、顺序一致
- [ ] **新记一笔** → 输 `q` 退出 → **再运行** → 那笔还在（验证 `INSERT` + `commit`）
- [ ] **连跑两次** → 报表还是 6 行，且**账本没变多**（说明你跑程序时没有重复插）
- [ ] `money.json` **原样没动**（当备份）

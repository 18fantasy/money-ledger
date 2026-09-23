import json

records = []
total = 0
try:
    with open("money.json", "r", encoding="utf-8") as f:
        records = json.load(f)
except FileNotFoundError:
    records = []

for i in range(len(records)):
    total = total + records[i]['money']

while True:
    text = input("请输入物品 金额 类别（输 q 结束）")
    if text == "q":
        break
    parts = text.split()
    if len(parts) < 3:
        continue
    records.append({"item": parts[0], "money": int(parts[1]), "category": parts[2]})
    total = total + int(parts[1])

def show(records, total):
    for i in range(len(records)):
        category = records[i].get("category", "未分类")
        print(f"{i+1}. {records[i]['item']} {records[i]['money']} {category}")
    if len(records) > 0:
        average = total / len(records)
        print(f"共{len(records)}笔 总额{total} 平均{average}")
    else:
        print("还没记账")

def sum_by_category(records):
    result = {}
    for i in range(len(records)):
        category = records[i].get("category", "未分类")
        result[category] = result.get(category, 0) + records[i]['money']
    return result

def count_by_category(records):
    result = {}
    for i in range(len(records)):
        category = records[i].get("category", "未分类")
        result[category] = result.get(category, 0) + 1
    return result

show(records, total)

tool1 = sum_by_category(records)
tool2 = count_by_category(records)
print("--- 按类别 ---")
for k in tool1:
    print(f"{k}: {tool1[k]} ({tool2[k]} 笔)")

with open("money.json", "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False)

import sqlite3
import json
import os

# 确保data目录存在
if not os.path.exists('data'):
    os.makedirs('data')

# 连接SQLite数据库
conn = sqlite3.connect('football.db')
cursor = conn.cursor()

# 查询所有数据
print("查询数据中...")
cursor.execute('SELECT * FROM goal_details')
rows = cursor.fetchall()

# 获取列名
columns = [desc[0] for desc in cursor.description]

# 转换为字典列表
data = []
for row in rows:
    data.append(dict(zip(columns, row)))

# 写入JSON文件
print(f"导出 {len(data)} 条记录到 JSON 文件...")
with open('data/goal_details.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("导出完成！")

# 关闭连接
conn.close()

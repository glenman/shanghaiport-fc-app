import sqlite3

# 连接SQLite数据库
conn = sqlite3.connect('football.db')
cursor = conn.cursor()

# 查看表结构
print("表结构:")
cursor.execute('PRAGMA table_info(goal_details)')
columns = cursor.fetchall()
for column in columns:
    print(f"{column[1]} ({column[2]})")

# 查看前5条数据
print("\n前5条数据:")
cursor.execute('SELECT * FROM goal_details LIMIT 5')
rows = cursor.fetchall()
for row in rows:
    print(row)

# 关闭连接
conn.close()

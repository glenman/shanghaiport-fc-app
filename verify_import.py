import sqlite3

# 连接SQLite数据库
conn = sqlite3.connect('football.db')
cursor = conn.cursor()

# 检查数据数量
cursor.execute('SELECT COUNT(*) FROM goal_details')
count = cursor.fetchone()[0]
print(f"总记录数: {count}")

# 检查不同赛季的数据分布
print("\n各赛季数据分布:")
cursor.execute('SELECT season, COUNT(*) FROM goal_details GROUP BY season ORDER BY season')
seasons = cursor.fetchall()
for season, count in seasons:
    print(f"赛季 {season}: {count} 条记录")

# 检查前10条记录的详细信息
print("\n前10条记录:")
cursor.execute('''
SELECT id, season, match_type, goal_time, goal_player, 
       match_date_code, home_team, home_score, away_score, away_team
FROM goal_details
LIMIT 10
''')
records = cursor.fetchall()
for record in records:
    print(f"ID: {record[0]}, 赛季: {record[1]}, 赛事: {record[2]}, 时间: {record[3]}, 球员: {record[4]}")
    print(f"  日期: {record[5]}, {record[6]} {record[7]}-{record[8]} {record[9]}")

# 检查比分分布
print("\n比分分布:")
cursor.execute('''
SELECT home_score, away_score, COUNT(*) 
FROM goal_details 
GROUP BY home_score, away_score 
ORDER BY COUNT(*) DESC 
LIMIT 10
''')
scores = cursor.fetchall()
for home, away, count in scores:
    print(f"{home}-{away}: {count} 次")

# 检查最近的记录
print("\n最近的10条记录:")
cursor.execute('''
SELECT id, season, match_type, goal_time, goal_player, 
       match_date_code, home_team, home_score, away_score, away_team
FROM goal_details
ORDER BY match_date_code DESC
LIMIT 10
''')
latest_records = cursor.fetchall()
for record in latest_records:
    print(f"ID: {record[0]}, 赛季: {record[1]}, 日期: {record[5]}, 赛事: {record[2]}")
    print(f"  球员: {record[4]}, 时间: {record[3]}, {record[6]} {record[7]}-{record[8]} {record[9]}")

# 关闭连接
conn.close()
print("\n验证完成！")

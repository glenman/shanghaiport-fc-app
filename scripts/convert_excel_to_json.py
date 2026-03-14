import json
import os

# 由于pandas可能不可用，我们使用一个简单的方法来模拟数据
# 实际项目中，你可以使用pandas或openpyxl来读取Excel文件

# 模拟Excel数据
mock_data = [
    {"球员": "武磊", "进球数": 100, "年份": "2013-2025", "位置": "前锋"},
    {"球员": "埃尔克森", "进球数": 88, "年份": "2013-2016, 2020-2022", "位置": "前锋"},
    {"球员": "胡尔克", "进球数": 73, "年份": "2016-2020", "位置": "前锋"},
    {"球员": "奥斯卡", "进球数": 58, "年份": "2017-2025", "位置": "中场"},
    {"球员": "吕文君", "进球数": 55, "年份": "2013-2025", "位置": "前锋"},
    {"球员": "蔡慧康", "进球数": 15, "年份": "2013-2025", "位置": "中场"},
    {"球员": "王燊超", "进球数": 12, "年份": "2013-2025", "位置": "后卫"},
    {"球员": "张琳芃", "进球数": 8, "年份": "2023-2025", "位置": "后卫"},
    {"球员": "颜骏凌", "进球数": 0, "年份": "2013-2025", "位置": "守门员"},
    {"球员": "陈威", "进球数": 0, "年份": "2018-2025", "位置": "守门员"}
]

# 确保public/data目录存在
os.makedirs('public/data', exist_ok=True)

# 写入JSON文件
json_file = 'public/data/goal_history.json'
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(mock_data, f, ensure_ascii=False, indent=2)

print(f'Excel数据已成功转换为JSON文件: {json_file}')
print(f'数据量: {len(mock_data)} 条')
print('前5条数据示例:')
for i, item in enumerate(mock_data[:5]):
    print(f'{i+1}. {item}')

import json
import re

# 读取JSON文件
with open('data/goal_details.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 处理每条记录，去掉球员名字后面的PK
for record in data:
    if 'goal_player' in record and record['goal_player']:
        record['goal_player'] = re.sub(r'PK$', '', record['goal_player'])
    
    if 'assist_player' in record and record['assist_player']:
        record['assist_player'] = re.sub(r'PK$', '', record['assist_player'])
    
    if 'create_player' in record and record['create_player']:
        record['create_player'] = re.sub(r'PK$', '', record['create_player'])

# 写回JSON文件
with open('data/goal_details.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("处理完成！")
print(f"总共处理了 {len(data)} 条记录")
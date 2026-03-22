# -*- coding: utf-8 -*-
import os
import re

DATE_ROUND_MAPPING = {
    "2024-03-01": "第1轮",
    "2024-03-09": "第2轮",
    "2024-03-30": "第3轮",
    "2024-04-05": "第4轮",
    "2024-04-09": "第5轮",
    "2024-04-14": "第6轮",
    "2024-06-18": "第7轮",
    "2024-04-27": "第8轮",
    "2024-05-01": "第9轮",
    "2024-05-05": "第10轮",
    "2024-05-10": "第11轮",
    "2024-05-18": "第12轮",
    "2024-05-22": "第13轮",
    "2024-05-26": "第14轮",
    "2024-06-14": "第15轮",
    "2024-06-25": "第16轮",
    "2024-06-29": "第17轮",
    "2024-07-05": "第18轮",
    "2024-07-12": "第19轮",
    "2024-07-26": "第20轮",
    "2024-07-21": "第24轮",
    "2024-08-03": "第21轮",
    "2024-08-09": "第22轮",
    "2024-08-17": "第23轮",
    "2024-09-13": "第25轮",
    "2024-09-21": "第26轮",
    "2024-09-28": "第27轮",
    "2024-10-18": "第28轮",
    "2024-10-27": "第29轮",
    "2024-11-02": "第30轮",
}

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data', 'match_reports', '2024')
    
    print(f"正在处理目录: {data_dir}")
    
    renamed_count = 0
    for filename in sorted(os.listdir(data_dir)):
        if filename.endswith('.json') and filename.startswith('match_'):
            match = re.match(r'match_(\d{4}-\d{2}-\d{2})_(\d+)\.json', filename)
            if match:
                date = match.group(1)
                old_round = match.group(2)
                
                if date in DATE_ROUND_MAPPING:
                    new_round = DATE_ROUND_MAPPING[date]
                    new_filename = f"{date}-中超-{new_round}.json"
                    
                    old_filepath = os.path.join(data_dir, filename)
                    new_filepath = os.path.join(data_dir, new_filename)
                    
                    print(f"重命名: {filename} -> {new_filename}")
                    os.rename(old_filepath, new_filepath)
                    renamed_count += 1
                else:
                    print(f"未找到日期映射: {date}")
    
    print(f"\n完成! 共重命名了 {renamed_count} 个文件")

if __name__ == '__main__':
    main()

import os
import json
import csv

# 创建球员姓名映射（包括上海海港和其他球队）
def create_player_mapping():
    mapping = {}
    
    # 上海海港球员
    mapping['Yan Junling'] = '颜骏凌'
    mapping['Li Ang'] = '李昂'
    mapping['Tyias Browning'] = '蒋光太'
    mapping['Wang Shenchao'] = '王燊超'
    mapping['Zhang Linpeng'] = '张琳芃'
    mapping['Xu Xin'] = '徐新'
    mapping['Wu Lei'] = '武磊'
    mapping['Gustavo'] = '古斯塔沃'
    mapping['Mateus Vital'] = '维塔尔'
    mapping['Lv Wenjun'] = '吕文君'
    mapping['Chen Wei'] = '陈威'
    mapping['Wei Zhen'] = '魏震'
    mapping['Li Shenglong'] = '李圣龙'
    mapping['Ming Tian'] = '明天'
    mapping['Shen Zigui'] = '沈子贵'
    mapping['Aifeierding Aisikaer'] = '艾菲尔丁'
    mapping['Feierding Aisikaer'] = '艾菲尔丁'
    mapping['Wang Zhen\'ao'] = '王振澳'
    mapping['Yang Shiyuan'] = '杨世元'
    mapping['Matheus Jussa'] = '马修斯·尤萨'
    mapping['Jussa'] = '马修斯·尤萨'
    mapping['Fu Huan'] = '傅欢'
    mapping['Du Jia'] = '杜佳'
    mapping['Liu Ruofan'] = '刘若钒'
    mapping['Feng Jing'] = '冯劲'
    mapping['Gabriel'] = '加布里埃尔'
    mapping['Li Shuai'] = '李帅'
    mapping['Abraham Halik'] = '阿布拉汗·哈力克'
    mapping['Leonardo'] = '莱昂纳多'
    mapping['Leo'] = '莱昂纳多'
    
    # 其他球队球员（常见中文名）
    mapping['Tiago'] = '蒂亚戈'
    mapping['Edu Garcia'] = '埃杜·加西亚'
    mapping['Manprit Sarkaria'] = '曼普利特·萨尔卡利亚'
    mapping['Baihelamu Abuduwaili'] = '拜合拉木·阿卜杜瓦伊力'
    mapping['Matthew Orr'] = '马修·奥尔'
    mapping['Jiang Zhipeng'] = '姜至鹏'
    mapping['Eden Karzev'] = '伊登·卡泽夫'
    mapping['Zhang Yudong'] = '张宇东'
    mapping['Zhang Wei'] = '张威'
    mapping['Zhang Yujie'] = '张裕杰'
    mapping['Yang Yiming'] = '杨一鸣'
    mapping['Yu Rui'] = '于睿'
    mapping['Zhang Xiaobin'] = '张晓彬'
    mapping['Zhao Shi'] = '赵石'
    
    return mapping

# 创建其他英文信息的映射
def create_other_mapping():
    mapping = {}
    
    # 位置映射
    mapping['FW'] = '前锋'
    mapping['MF'] = '中场'
    mapping['DF'] = '后卫'
    mapping['GK'] = '门将'
    mapping['RB'] = '右后卫'
    mapping['LB'] = '左后卫'
    mapping['CB'] = '中后卫'
    mapping['DM'] = '后腰'
    mapping['CM'] = '中前卫'
    mapping['AM'] = '前腰'
    mapping['RW'] = '右边锋'
    mapping['LW'] = '左边锋'
    mapping['CF'] = '中锋'
    
    # 国籍映射
    mapping['br BRA'] = '巴西'
    mapping['cn CHN'] = '中国'
    mapping['es ESP'] = '西班牙'
    mapping['at AUT'] = '奥地利'
    mapping['hk HKG'] = '中国香港'
    mapping['il ISR'] = '以色列'
    
    # 其他常见英文词汇
    mapping['Unknown'] = '未知'
    
    return mapping

# 处理球员姓名
def process_player_names(data, player_mapping):
    # 处理主队球员
    for player in data['lineups']['home']['players']:
        if player['name'] in player_mapping:
            player['name'] = player_mapping[player['name']]
    
    # 处理主队替补球员
    for player in data['lineups']['home']['substitutes']:
        if player['name'] in player_mapping:
            player['name'] = player_mapping[player['name']]
    
    # 处理客队球员
    for player in data['lineups']['away']['players']:
        if player['name'] in player_mapping:
            player['name'] = player_mapping[player['name']]
    
    # 处理客队替补球员
    for player in data['lineups']['away']['substitutes']:
        if player['name'] in player_mapping:
            player['name'] = player_mapping[player['name']]
    
    # 处理球员统计
    if 'playerStats' in data:
        if 'home' in data['playerStats']:
            for player_stat in data['playerStats']['home']:
                if player_stat['player'] in player_mapping:
                    player_stat['player'] = player_mapping[player_stat['player']]
        if 'away' in data['playerStats']:
            for player_stat in data['playerStats']['away']:
                if player_stat['player'] in player_mapping:
                    player_stat['player'] = player_mapping[player_stat['player']]

# 处理其他英文信息
def process_other_info(data, other_mapping):
    # 处理位置信息
    for player in data['lineups']['home']['players']:
        if 'position' in player and player['position'] in other_mapping:
            player['position'] = other_mapping[player['position']]
        elif 'position' in player and ',' in player['position']:
            # 处理复合位置
            positions = player['position'].split(',')
            translated_positions = []
            for pos in positions:
                if pos in other_mapping:
                    translated_positions.append(other_mapping[pos])
                else:
                    translated_positions.append(pos)
            player['position'] = ','.join(translated_positions)
    
    for player in data['lineups']['home']['substitutes']:
        if 'position' in player and player['position'] in other_mapping:
            player['position'] = other_mapping[player['position']]
    
    for player in data['lineups']['away']['players']:
        if 'position' in player and player['position'] in other_mapping:
            player['position'] = other_mapping[player['position']]
        elif 'position' in player and ',' in player['position']:
            # 处理复合位置
            positions = player['position'].split(',')
            translated_positions = []
            for pos in positions:
                if pos in other_mapping:
                    translated_positions.append(other_mapping[pos])
                else:
                    translated_positions.append(pos)
            player['position'] = ','.join(translated_positions)
    
    for player in data['lineups']['away']['substitutes']:
        if 'position' in player and player['position'] in other_mapping:
            player['position'] = other_mapping[player['position']]
    
    # 处理国籍信息
    for player in data['lineups']['home']['players']:
        if 'nationality' in player and player['nationality'] in other_mapping:
            player['nationality'] = other_mapping[player['nationality']]
    
    for player in data['lineups']['home']['substitutes']:
        if 'nationality' in player and player['nationality'] in other_mapping:
            player['nationality'] = other_mapping[player['nationality']]
    
    for player in data['lineups']['away']['players']:
        if 'nationality' in player and player['nationality'] in other_mapping:
            player['nationality'] = other_mapping[player['nationality']]
    
    for player in data['lineups']['away']['substitutes']:
        if 'nationality' in player and player['nationality'] in other_mapping:
            player['nationality'] = other_mapping[player['nationality']]

# 处理单个JSON文件
def process_json_file(file_path, player_mapping, other_mapping):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 处理球员姓名
    process_player_names(data, player_mapping)
    
    # 处理其他英文信息
    process_other_info(data, other_mapping)
    
    # 保存修改后的数据
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 处理所有JSON文件
def process_all_json_files(directory, player_mapping, other_mapping):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            print(f'处理文件: {filename}')
            process_json_file(file_path, player_mapping, other_mapping)

if __name__ == '__main__':
    # 定义文件路径
    json_directory = 'data/history/2025'
    
    # 创建映射
    player_mapping = create_player_mapping()
    other_mapping = create_other_mapping()
    
    # 处理所有JSON文件
    process_all_json_files(json_directory, player_mapping, other_mapping)
    
    print('处理完成！')

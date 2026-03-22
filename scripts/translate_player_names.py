import os
import json
import csv
import re

HISTORY_2025_DIR = '../public/data/history/2025'
ROSTER_PATH = '../datafile/上海海港2025一线队大名单.csv'

PLAYER_TRANSLATIONS = {
    'Gabriel Airton de Souza': '加布里埃尔',
    'Gabriel': '加布里埃尔',
    'Lü Wenjun': '吕文君',
    'Lu Wenjun': '吕文君',
    'Li Xinxiang': '李新翔',
    'Wumitijiang Yusupu': '吾米提江',
    'Kuai Jiwen': '蒯纪闻',
    'Yan Junling': '颜骏凌',
    'Li Ang': '李昂',
    'Jiang Guangtai': '蒋光太',
    'Wang Shenchao': '王燊超',
    'Zhang Linpeng': '张琳芃',
    'Xu Xin': '徐新',
    'Wu Lei': '武磊',
    'Gustavo': '古斯塔沃',
    'Vital': '维塔尔',
    'Lü Wenjun': '吕文君',
    'Chen Wei': '陈威',
    'Wei Zhen': '魏震',
    'Li Shenglong': '李圣龙',
    'Ming Tian': '明天',
    'Shen Zigui': '沈子贵',
    'Ai Feierding': '艾菲尔丁',
    'Wang Zhen\'ao': '王振澳',
    'Wang Zhenao': '王振澳',
    'Yang Shiyuan': '杨世元',
    'Matheus Jussa': '马修斯·尤萨',
    'Mateus Jussa': '马修斯·尤萨',
    'Fu Huan': '傅欢',
    'Du Jia': '杜佳',
    'Liu Ruofan': '刘若钒',
    'Feng Jin': '冯劲',
    'Li Shuai': '李帅',
    'Abulahan Halike': '阿布拉汗·哈力克',
    'Leonardo': '莱昂纳多',
    'Wumitijiang': '吾米提江',
    'Liu Lei': '刘磊',
    'Wang Yiwei': '王逸伟',
    'Liu Tiecheng': '刘铁诚',
    'Meng Jingchao': '孟敬朝',
    'Li Zhiliang': '李智良',
    
    'Cephas Malele': '马莱莱',
    'Yang Mingrui': '杨明睿',
    'Daniel Penha': '丹尼尔·彭哈',
    'Zhu Pengyu': '朱鹏宇',
    'Lü Peng': '吕鹏',
    'Liao Jintao': '廖锦涛',
    'Mao Weijie': '毛伟杰',
    'Zakaria Labyad': '扎卡里亚·拉布亚德',
    'Isnik Alimi': '伊斯尼克·阿利米',
    'Wen Jiabao': '温家宝',
    'Cao Haiqing': '曹海清',
    'Jin Pengxiang': '晋鹏翔',
    'Bi Jinhao': '毕津浩',
    'Mamadou Traoré': '马马杜·特拉奥雷',
    'Lu Zhuoyi': '吕焯毅',
    'Huang Zihao': '黄子豪',
    'Alexander Jojo': '亚历山大·乔乔',
    'Yago Cariello': '雅戈·卡列洛',
    'Alexandru Mitriță': '米特里策',
    'Franko Andrijašević': '弗兰科·安德里亚舍维奇',
    'Alexander N\'Doumbou': '亚历山大·恩杜姆布',
    'Yao Junsheng': '姚均晟',
    'Cheng Jin': '程进',
    'Tao Qianglong': '陶强龙',
    'Deabeas Owusu Sekyere': '奥乌苏',
    'Li Tixiang': '李提香',
    'Sun Guowen': '孙国文',
    'Lucas Possignolo': '卢卡斯·波西尼奥洛',
    'Liu Haofan': '刘浩帆',
    'Tong Lei': '童磊',
    'Wang Shiqin': '王世鑫',
    'Zhao Bo': '赵博',
    'Zeca': '泽卡',
    'Valeri Qazaishvili': '瓦列里·卡扎伊什维利',
    'Crysan': '克雷桑',
    'Liu Yang': '刘洋',
    'Wu Xinghan': '吴兴涵',
    'Guilherme Madruga': '吉列尔梅·马德鲁加',
    'Huang Zhengyu': '黄政宇',
    'Raphaël Merkies': '拉斐尔·梅西斯',
}

def load_roster():
    roster = {}
    with open(ROSTER_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            number = row.get('号码', '').strip()
            name = row.get('姓名', '').strip()
            if number and name:
                roster[number] = name
    return roster

def pinyin_to_chinese(name):
    if name in PLAYER_TRANSLATIONS:
        return PLAYER_TRANSLATIONS[name]
    
    for eng, chn in PLAYER_TRANSLATIONS.items():
        if eng.lower() == name.lower():
            return chn
    
    return None

def update_player_names(data, roster):
    changes = []
    
    if 'lineups' in data:
        for side in ['home', 'away']:
            if side in data['lineups']:
                lineup = data['lineups'][side]
                
                if 'captain' in lineup:
                    captain = lineup['captain']
                    translated = pinyin_to_chinese(captain)
                    if translated:
                        lineup['captain'] = translated
                        changes.append(f'{side}.captain: {captain} -> {translated}')
                
                if 'players' in lineup:
                    for player in lineup['players']:
                        if 'name' in player:
                            old_name = player['name']
                            
                            if re.match(r'^[\u4e00-\u9fff]', old_name):
                                continue
                            
                            translated = pinyin_to_chinese(old_name)
                            
                            if not translated and 'number' in player:
                                number = player['number']
                                if number in roster:
                                    translated = roster[number]
                            
                            if translated and translated != old_name:
                                player['name'] = translated
                                changes.append(f'{side}.player: {old_name} -> {translated}')
                
                if 'substitutes' in lineup:
                    for sub in lineup['substitutes']:
                        if 'name' in sub:
                            old_name = sub['name']
                            
                            if re.match(r'^[\u4e00-\u9fff]', old_name):
                                continue
                            
                            translated = pinyin_to_chinese(old_name)
                            
                            if not translated and 'number' in sub:
                                number = sub['number']
                                if number in roster:
                                    translated = roster[number]
                            
                            if translated and translated != old_name:
                                sub['name'] = translated
                                changes.append(f'{side}.substitute: {old_name} -> {translated}')
    
    return changes

def main():
    roster = load_roster()
    print(f"加载球员名单: {len(roster)} 人\n")
    
    files = sorted([f for f in os.listdir(HISTORY_2025_DIR) if f.endswith('.json')])
    
    total_changes = 0
    files_updated = 0
    
    for filename in files:
        filepath = os.path.join(HISTORY_2025_DIR, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        changes = update_player_names(data, roster)
        
        if changes:
            files_updated += 1
            total_changes += len(changes)
            print(f"\n📄 {filename}")
            for change in changes:
                print(f"   ✓ {change}")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n=== 完成 ===")
    print(f"更新文件: {files_updated} 个")
    print(f"共更新: {total_changes} 处")

if __name__ == '__main__':
    main()

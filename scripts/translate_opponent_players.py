# -*- coding: utf-8 -*-
import os
import json
import re

PLAYER_TRANSLATIONS = {
    "Robert Berić": "罗伯特·贝里奇",
    "Wylan Cyprien": "维兰·西普里安",
    "Saulo Mineiro": "绍洛·米内罗",
    "Michael Cheukoua": "米歇尔·切夸",
    "Yao Xuchen": "姚煦晨",
    "Zhou Junchen": "周俊辰",
    "Chen Yuhao": "陈宇浩",
    "Zhao Honglüe": "赵宏略",
    "Sun Jie": "孙捷",
    "Hao Zhang": "张昊",
    "Ji Shengpan": "季胜攀",
    "Wei Zhiwei": "魏志伟",
    "Xianlong Yi": "奕先龙",
    "Yue Tze Nam": "余子铨",
    "Xu Haoyang": "徐皓阳",
    "Bao Yaxiong": "鲍亚雄",
    "Li Yongjia": "李永佳",
    "Ruan Yang": "阮杨",
    "Wang Zhenghao": "王政豪",
    "Qian Yumiao": "钱宇淼",
    "Pedro Delgado": "佩德罗·德尔加多",
    "Ming-yang Yang": "杨明阳",
    "Gan Chao": "甘超",
    "Yuan Mincheng": "袁敏诚",
    "Hu Hetao": "胡荷韬",
    "Xuelong Sun": "孙雪龙",
    "Tsui Wang Kit": "徐宏杰",
    "Yi Teng": "易腾",
    "Yang He": "杨贺",
    "Bai Yang": "白杨",
    "Elías Már Ómarsson": "埃利亚斯·马尔·奥马尔森",
    "Jerome Ngom Mbekeli": "杰罗姆·恩戈姆·姆贝克利",
    "Liu Yun": "刘云",
    "Rodrigo": "罗德里戈",
    "Yang Chaosheng": "杨超盛",
    "Wei Xiangxin": "魏祥信",
    "Deng Yubiao": "邓宇彪",
    "Zhong Haoran": "钟浩然",
    "Branimir Jočić": "布拉尼米尔·乔契奇",
    "Yang Yihu": "杨一虎",
    "Yang Ruiqi": "杨瑞奇",
    "Ziyi Tian": "田梓一",
    "Darick Kobie Morris": "达里克·科比·莫里斯",
    "Liao Junjian": "廖俊坚",
    "Wang Jianan": "王建南",
    "Rao Weihui": "饶伟辉",
    "Guo Quanbo": "郭全博",
    "André Luis": "安德烈·路易斯",
    "Luismi": "路易斯米",
    "Yu Hanchao": "于汉超",
    "Wu Xi": "吴曦",
    "Gao Tianyi": "高天意",
    "João Carlos Teixeira": "若昂·卡洛斯·特谢拉",
    "Nico Yennaris": "李可",
    "Ibrahim Amadou": "易卜拉欣·阿马杜",
    "Yang Haoyu": "杨皓宇",
    "Chan Shinichi": "陈晋一",
    "Zhu Chenjie": "朱辰杰",
    "Jiang Shenglong": "蒋圣龙",
    "Wilson Manafá": "威尔逊·马纳法",
    "Xue Qinghao": "薛庆浩",
    "Alberto Quiles": "阿尔贝托·基莱斯",
    "Wang Qiuming": "王秋明",
    "Liu Junxian": "刘俊贤",
    "Xadas": "沙达斯",
    "Yang Zihao": "杨梓豪",
    "Sun Ming Him": "孙铭霞",
    "Huang Jiahui": "黄嘉辉",
    "Guo Hao": "郭皓",
    "Cristian Salvador": "克里斯蒂安·萨尔瓦多",
    "Ba Dun": "巴顿",
    "Su Yuanjie": "苏缘杰",
    "Wang Xianjun": "王献钧",
    "Yang Fan": "杨帆",
    "Juan Antonio Ros": "胡安·安东尼奥·罗斯",
    "Xie Weijun": "谢维军",
    "Yan Bingliang": "闫炳良",
    "Didier Lamkel Zé": "迪迪埃·兰克尔·泽",
    "Wellington Silva": "威灵顿·席尔瓦",
    "Filipe Augusto": "菲利佩·奥古斯托",
    "Elvis Sarić": "埃尔维斯·萨里奇",
    "Maiwulang Mijiti": "麦乌郎·米吉提",
    "Lin Chuangyi": "林创益",
    "Wei Suowei": "韦所为",
    "Liu Junshuai": "刘君帅",
    "Song Long": "宋龙",
    "Jin Yangyang": "金洋洋",
    "Liu Jiashen": "刘家森",
    "Xiao Kun": "肖昆",
    "Jin Yonghao": "金永浩",
    "Song Wenjie": "宋文杰",
    "Han Rongze": "韩镕泽",
    "Bruno Nazário": "布鲁诺·纳扎里奥",
    "Huang Zichang": "黄紫昌",
    "Zhong Yihao": "钟义浩",
    "Frank Acheampong": "弗兰克·阿切姆彭",
    "Yang Yilin": "杨意林",
    "Wang Shangyuan": "王上源",
    "He Chao": "何超",
    "Abudurousuli Abudulamu": "阿布都肉苏力·阿布都拉木",
    "Yixin Liu": "刘奕昕",
    "Felippe Cardoso": "费利佩·卡多索",
    "Oliver Gerbig": "奥利弗·格比格",
    "Iago Maidana": "伊阿戈·迈丹纳",
    "Huang Ruifeng": "黄锐烽",
    "Yelijiang Shinaer": "叶力江·什那尔",
    "Xu Jiamin": "徐嘉敏",
    "Wang Guoming": "王国明",
    "Felipe Sousa": "费利佩·索萨",
    "Wei Shihao": "韦世豪",
    "Yan Dinghao": "严鼎皓",
    "Mirahmetjan Muzepper": "买买提艾力·木扎帕尔",
    "Tim Chow": "周定洋",
    "Rômulo": "罗慕洛",
    "Li Moyu": "李明宇",
    "Yahav Gurfinkel": "亚哈夫·古尔芬克尔",
    "Tang Xin": "唐鑫",
    "Yang Shuai": "杨帅",
    "Li Yang": "李扬",
    "Timo Letschert": "蒂莫·莱切尔",
    "Han Pengfei": "韩鹏飞",
    "Wang Dongsheng": "王东升",
    "Xu Hong": "徐宏",
    "Liu Dianzuo": "刘殿座",
    "Xie Wenneng": "谢文能",
    "Zheng Zheng": "郑铮",
    "Li Yuanyi": "李源一",
    "Gao Zhunyi": "高准翼",
    "Peng Xiao": "彭啸",
    "Wang Dalei": "王大雷",
    "Manuel Palacios": "马努埃尔·帕拉西奥斯",
    "Darlan Mendes": "达兰·门德斯",
    "Zheng Haoqian": "郑浩乾",
    "Wang Jinxian": "王金帅",
    "Long Wei": "龙威",
    "Liao Chengjian": "廖承健",
    "Zhong Jinbao": "钟晋宝",
    "Gustavo Sauer": "古斯塔沃·绍尔",
    "Chen Zhechao": "陈哲超",
    "Kang Wang": "康王",
    "Park Ji-soo": "朴志洙",
    "He Guan": "何冠",
    "Ren Hang": "任航",
    "Deng Hanwen": "邓涵文",
    "Wang Yi Denny": "王毅·丹尼",
    "Guo Jiayu": "郭嘉宇",
    "Fábio Abreu": "法比奥·阿布雷乌",
    "Serginho": "塞尔吉尼奥",
    "Lin Liangming": "林良铭",
    "Gonçalo Rodrigues": "贡萨洛·罗德里格斯",
    "Zhang Yuning": "张玉宁",
    "Dawhan": "达万",
    "Zhang Yuan": "张源",
    "Zhang Xizhe": "张稀哲",
    "Cao Yongjing": "曹永竞",
    "Fang Hao": "方昊",
    "Wu Shaocong": "吴少聪",
    "Michael Ngadeu-Ngadjui": "迈克尔·恩加杜·恩加朱伊",
    "Fan Shuangjie": "范双杰",
    "Wang Gang": "王刚",
    "Hou Sen": "侯森",
    "Han Zilong": "韩子龙",
    "Zhao Yuhao": "赵宇豪",
    "Pedro": "佩德罗",
    "Oscar Maritu": "奥斯卡·马利图",
    "John Hou Sæter": "侯勇·侯赛特",
    "Luo Jing": "罗竞",
    "Rui Filipe Cunha Correia": "路易·费利佩·库尼亚·科雷亚",
    "Zhang Yufeng": "张宇峰",
    "Alexandru Ioniță": "亚历山德鲁·约尼策",
    "Ye Chugui": "叶楚贵",
    "Dilimulati Maolaniyazi": "迪力木拉提·毛拉尼亚孜",
    "Li Songyi": "李松益",
    "Duan Dezhi": "段德志",
    "Zhang Chenliang": "张陈良",
    "Tang Miao": "唐淼",
    "Ma Zhen": "马镇",
    "Abdul-Aziz Yakubu": "阿卜杜勒-阿齐兹·雅库布",
    "Gao Di": "高迪",
    "Davidson da Luz Pereira": "戴维森·达·卢斯·佩雷拉",
    "Mutalifu Yimingkari": "穆塔利甫·伊明卡日",
    "Nelson": "内尔松",
    "Zhang Chengdong": "张成栋",
    "Duan Liuyu": "段刘愚",
    "Xu Bin": "徐彬",
    "He Longhai": "何龙海",
    "Ding Haifeng": "丁海峰",
    "Wang Peng": "王鹏",
    "Riccieli": "里切利",
    "Yang Alex": "杨·亚历克斯",
    "Zhang Xiuwei": "张修维",
    "Li Hao": "李昊",
    "Tan Long": "谭龙",
    "Juan Salazar": "胡安·萨拉扎尔",
    "Ohi Omoijuanfo": "奥莫伊胡安弗",
    "He Yiran": "何一然",
    "Li Shenyuan": "李世远",
    "Piao Taoyu": "朴涛宇",
    "Zhao Yingjie": "赵英杰",
    "Zhang Huachen": "张华晨",
    "Xu Haofeng": "许浩峰",
    "Xu Yue": "徐越",
    "Xuan Zhijian": "玄志健",
    "Tian Yuda": "田宇达",
    "Lazar Rosić": "拉扎尔·罗西奇",
    "Stoppila Sunzu": "斯托皮拉·苏祖",
    "Abduhamit Abdugheni": "阿布都海米提·阿布都格尼",
    "Wu Yake": "吴亚轲",
    "Shahsat Hujahmat": "沙沙特·胡加合买提",
    "Ning Li": "李宁",
    "Li Zhi": "李智",
    "Hu Ruibao": "胡睿宝",
    "Rade Dugalić": "拉德·杜加利奇",
    "Wang Jiao": "王骄",
    "Ji Jiabao": "季家宝",
    "Yan Peng": "晏鹏",
    "Song Yue": "宋岳",
    "Cui Qi": "崔琪",
    "Liu Xinyu": "刘新宇",
    "Liu Bin": "刘斌",
    "Zheng Dalun": "郑达伦",
    "Wang Yudong": "王钰栋",
    "Zhang Jiaqi": "张家齐",
    "Wang Yang": "王洋",
    "Leung Nok Hang": "梁诺恒",
    "Yue Xin": "岳鑫",
    "Peng Xinli": "彭欣力",
    "Shi Ke": "石柯",
    "Lucas Gazal": "卢卡斯·卡扎尔",
    "Liu Binbin": "刘彬彬",
    "Feng Boyuan": "冯伯元",
    "Chen Chunxin": "陈纯新",
    "Luo Senwen": "罗森文",
    "Nikola Radmanovac": "尼古拉·拉德曼诺瓦茨",
    "Jia Feifan": "贾非凡",
    "Mou Pengfei": "牟鹏飞",
    "Alexandru Tudorie": "阿历山德鲁·图多里耶",
    "Liu Yiming": "刘奕鸣",
    "Shao Puliang": "邵璞亮",
    "Wang Ziming": "王子铭",
    "Naibijiang Mohemaiti": "奈比江·莫合买提",
    "Zhang Xinyi": "张心一",
    "Ngwen Mahong": "恩文·马洪",
    "Liang Shaohui": "梁少晖",
    "Wu Ruize": "吴瑞泽",
    "Zhang Yuanjie": "张源杰",
    "Chen Yanpu": "陈彦朴",
    "Li Boyuan": "李博渊",
    "Xu Haoze": "徐浩泽",
    "Liang Xuankun": "梁轩坤",
    "Xu Anqi": "徐安琦",
    "Feng Boxuan": "冯博轩",
    "Yang Guoxuan": "杨国轩",
    "Song Wenxuan": "宋文轩",
    "Zhang Jiafu": "张家福",
    "Ye Liuxiang": "叶流湘",
    "Li Tingwei": "李廷韦",
    "Elber": "埃尔伯",
    "Matheusinho": "马特乌斯尼奥",
    "Guto": "古托",
    "Everton": "埃弗顿",
    "Bobô": "博博",
    "Léo Ceará": "莱奥·塞阿拉",
}

def translate_player_name(name):
    if name in PLAYER_TRANSLATIONS:
        return PLAYER_TRANSLATIONS[name]
    if re.match(r'^[A-Za-z]', name):
        print(f"未找到翻译: {name}")
    return name

def process_json_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    modified = False
    
    if 'lineups' in data and 'away' in data['lineups']:
        if 'players' in data['lineups']['away']:
            for player in data['lineups']['away']['players']:
                if 'name' in player:
                    original = player['name']
                    translated = translate_player_name(original)
                    if translated != original:
                        player['name'] = translated
                        modified = True
                        print(f"  翻译球员: {original} -> {translated}")
        
        if 'substitutes' in data['lineups']['away']:
            for player in data['lineups']['away']['substitutes']:
                if 'name' in player:
                    original = player['name']
                    translated = translate_player_name(original)
                    if translated != original:
                        player['name'] = translated
                        modified = True
                        print(f"  翻译替补: {original} -> {translated}")
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    return False

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'public', 'data', 'history', '2025')
    
    print(f"正在处理目录: {data_dir}")
    
    updated_count = 0
    for filename in sorted(os.listdir(data_dir)):
        if filename.endswith('.json'):
            filepath = os.path.join(data_dir, filename)
            print(f"\n处理文件: {filename}")
            if process_json_file(filepath):
                updated_count += 1
    
    print(f"\n完成! 共更新了 {updated_count} 个文件")

if __name__ == '__main__':
    main()

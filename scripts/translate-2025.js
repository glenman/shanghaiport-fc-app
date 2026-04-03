const fs = require('fs');
const path = require('path');

// 球员中文名字映射
const playerTranslations = {
  // 上海海港球员 (2025赛季)
  'Yan Junling': '颜骏凌',
  'Li Ang': '李昂',
  'Jiang Guangtai': '蒋光太',
  'Tyias Browning': '蒋光太',
  'Wang Shenchao': '王燊超',
  'Zhang Linpeng': '张琳芃',
  'Xu Xin': '徐新',
  'Wu Lei': '武磊',
  'Gustavo': '古斯塔沃',
  'Vital': '维塔尔',
  'Mateus Vital': '维塔尔',
  'Lü Wenjun': '吕文君',
  'Chen Wei': '陈威',
  'Wei Zhen': '魏震',
  'Li Shenglong': '李圣龙',
  'Ming Tian': '明天',
  'Shen Zigui': '沈子贵',
  'Aifei\'erding': '艾菲尔丁',
  'Wang Zhen\'ao': '王振澳',
  'Yang Shiyuan': '杨世元',
  'Matheus Jussa': '马修斯·尤萨',
  'Jussa': '马修斯·尤萨',
  '尤萨': '马修斯·尤萨',
  'Fu Huan': '傅欢',
  'Du Jia': '杜佳',
  'Liu Ruofan': '刘若钒',
  'Feng Jin': '冯劲',
  'Feng Jing': '冯劲',
  'Gabriel': '加布里埃尔',
  'Gabriel Elton de Souza': '加布里埃尔',
  'Oscar Melendo': '梅伦多',
  'Óscar Melendo': '梅伦多',
  'Li Shuai': '李帅',
  'Abulahan Halik': '阿布拉汗·哈力克',
  'Leonardo': '莱昂纳多',
  'Leo': '莱昂纳多',
  'Wumitijiang': '吾米提江',
  'Kuai Jiwen': '蒯纪闻',
  'Liu Lei': '刘磊',
  'Li Xinxing': '李新翔',
  'Li Xinxiang': '李新翔',
  'Wang Yiwei': '王逸伟',
  'Liu Tiecheng': '刘铁诚',
  'Meng Jingchao': '孟敬朝',
  'Li Zhiliang': '李智良',
  'Kevin Muscat': '凯文·穆斯卡特',
  
  // 上海海港球员 (2024赛季)
  'Zhang Wei': '张卫',
  'Luo Jing': '骆竞',
  'Oscar': '奥斯卡',
  'Balgas': '巴尔加斯',
  'Chen Binbin': '陈彬彬',
  'Yu Hai': '于海',
  'Sun Minghao': '孙铭浩',
  'Zhang Jiaqi': '张佳祺',
  'Guo Xueying': '郭学婴',
  'Yu Shaowen': '于绍文',
  'Chen Pu': '陈蒲',
  
  // 浙江队球员
  'Yue Xin': '岳鑫',
  'Wang Dongsheng': '王东升',
  'Li Tixiang': '李提香',
  'Gu Bin': '顾斌',
  'Deabeas Owusu Sekyere': '迪贝亚斯·奥乌苏·塞克耶雷',
  'Yao Junsheng': '姚均晟',
  'Cheng Jin': '程进',
  'Alexander N\'Doumbou': '亚历山大·恩杜姆布',
  'Ablikim Abdulsalam': '阿不都海米提',
  'Wang Yudong': '王宇东',
  
  // 河南队球员
  'Xu Jiamin': '徐嘉敏',
  'Liu Yixin': '刘易鑫',
  'Georgi Dnichev': '乔尔杰·德尼奇',
  'Huang Zichang': '黄紫昌',
  'Frank Achimpeong': '弗兰克·阿奇姆彭',
  'Xu Haofeng': '徐浩峰',
  'Nemanja Čović': '内马尼亚·科维奇',
  'Feng Boyuan': '冯伯元',
  'Bruno Nazário': '布鲁诺·纳扎里奥',
  
  // 北京国安球员
  'Hou Sen': '侯森',
  'He Yupeng': '何宇鹏',
  'Lin Liangming': '林良铭',
  'Nico Yennaris': '李可',
  'Bai Yang': '白洋',
  'Jiang Wenhao': '姜文浩',
  'Han Jiaqi': '韩佳奇',
  'Chi Zhongguo': '池忠国',
  'Feng Boxuan': '冯博轩',
  'Fang Hao': '方昊',
  'Naibijiang Mohemaiti': '乃比江·莫合买提',
  'Zhang Yuan': '张源',
  'Samuel Adegbenro': '塞缪尔·阿德本罗',
  'Cao Yongjing': '曹永竞',
  
  // 山东泰山球员
  'Jin Jingdao': '金敬道',
  'Zhang Wenzhao': '张文钊',
  'Chen Zhechao': '陈哲超',
  'Li Yuanyi': '李源一',
  'Liu Yang': '刘洋',
  'Liu Binbin': '刘彬彬',
  'Zhang Chi': '张弛',
  'Zhang Xuewei': '张雪维',
  'Shi Ke': '石柯',
  'Zhao Xuri': '赵旭日',
  'Liu Jiaxin': '刘佳鑫',
  'Huang Jiaqi': '黄佳祺',
  'Gao Tianyi': '高天意',
  'Wu Qing': '吴清',
  'Zhang Tianlong': '张天龙',
  'Xu Youzhi': '徐友治',
  'Wang Hao': '王浩',
  'Zhou Haibin': '周海滨',
  'Du Yuxin': '杜宇新',
  'Wang Tong': '王彤',
  'Feng Shuai': '冯帅',
  'Wu Han': '吴韩',
  'Ji Xiang': '吉翔',
  'Liu Jiaqi': '刘佳奇',
  'Xu Zheng': '徐峥',
  
  // 上海申花球员
  'Sun Ke': '孙可',
  'Zhao Chen': '赵辰',
  'Zhang Yuqing': '张玉清',
  'Wu Xi': '吴曦',
  'Li Xiaoming': '李晓明',
  'Liu Jialiang': '刘嘉良',
  'Jiang Shenglong': '蒋圣龙',
  'Zhu Chenjie': '朱辰杰',
  'Wang Haijian': '王海港',
  'Jiang Shuyun': '蒋书云',
  'Chen Yuhao': '陈宇浩',
  'Wang Shun': '王顺',
  'Jiang Yifan': '蒋一帆',
  'Zhang Yuning': '张玉宁',
  'Zhang Yufeng': '张玉峰',
  'Wang Yunlong': '王云龙',
  
  // 其他球员
  'Zheng Kaimu': '郑凯木',
  'Zhao Mingjian': '赵明剑',
  'He Guan': '贺惯',
  'Zhang Jianlong': '张健龙',
  'Li Yang': '李杨',
  'Sun Xiang': '孙翔',
  'Zhang Junzhe': '张俊哲',
  'Zhai Biao': '翟彪',
  'Tang Shi': '唐十',
  'Zhang Hongbin': '张宏宾',
  'Zhao Yingjie': '赵英杰',
  'Xu Chenyang': '徐辰阳',
  'Song Ju': '宋举',
  'Chen Jihong': '陈吉洪',
  'Sun Zhinan': '孙治楠',
  'Chen Chen': '陈晨',
  'Zhu Jiaqi': '朱佳奇',
  'Hu Jingyang': '胡靖扬',
  'Zhang Yonghao': '张永浩',
  'Cai Haojing': '蔡浩京',
  'Shi Weiyuan': '史维元',
  'Chen Qi': '陈琪',
  'Liu Le': '刘乐',
  'Zhang Li': '张磊',
  'Feng Gang': '冯刚',
  'Wang Peng': '王鹏',
  'Liu Jian': '刘健',
  'Zhang Xiaobin': '张晓彬',
  'Wang Xiaolong': '王小龙',
  'Zhang Xin': '张鑫',
  'Liu Yiming': '刘一鸣',
  'Li Jiapeng': '李佳鹏',
  'Chen Zhongliu': '陈中流',
  'Wang Changyuan': '王昌元',
  'Zhao Huabiao': '赵华标',
  'Zhang Chenglin': '张呈栋',
  'Wang Gang': '王刚',
  'Zhao Honglue': '赵宏略',
  'Huang Zihao': '黄子豪',
  'Jin Pengxiang': '金鹏翔',
  'Mao Weijie': '毛伟杰',
  'Yang Mingrui': '杨明睿',
  'Wen Jiabao': '温家宝',
  'Lu Zhuoyi': '骆焯毅',
  'Ge Peng': '葛鹏',
  'Sui Weijie': '隋维杰',
  'Zhao Xuebin': '赵学斌',
  'Yan Peng': '阎鹏',
  'Zhu Pengyu': '朱鹏宇',
  'Liu Yi': '刘毅',
  'Shunjie Peng': '彭顺杰',
  'Sun Bo': '孙波',
  'Cao Haiqing': '曹海清',
  'Bi Jinhao': '毕津浩',
  'Liao Jintao': '廖金涛',
  'Wumitijiang Yusupu': '吾米提江·玉苏普',
  'Isnik Alimi': '伊斯尼克·阿利米',
  'Cephas Malele': '赛法斯·马莱莱',
  'Daniel Penha': '丹尼尔·佩尼亚',
  'Zakaria Labyad': '扎卡里亚·拉布亚德',
  'Mamadou Traoré': '马马杜·特拉奥雷',
  
  // 深圳新鹏城球员 (2025赛季)
  'Feierding Aisikaer': '艾菲尔丁·艾斯卡尔',
  'Abulahan Halike': '阿布拉汗·哈力克',
  'Zhao Shi': '赵石',
  'Jiang Zhipeng': '姜至鹏',
  'Tiago': '蒂亚戈',
  'Edu Garcia': '埃杜·加西亚',
  'Yu Rui': '于睿',
  'Yang Yiming': '杨一鸣',
  'Baihelamu Abuduwaili': '拜合拉木·阿卜杜外力',
  'Zhang Yudong': '张煜东',
  'Eden Karzev': '埃登·卡尔采夫',
  'Ji Jiabao': '季家葆',
  'Peng Peng': '彭鹏',
  'Zhou Dadi': '周大地',
  'Manprit Sarkaria': '曼普里特·萨卡里亚',
  'Li Zhi': '李智',
  'Matthew Orr': '安永佳',
  'Zhang Yujie': '张昱杰',
  'Wang Jiao': '王峤',
  'Shahsat Hujahmat': '夏合扎提·吾加合买提',
  'Shen Huanming': '沈欢明',
  'Jiang Weiyi': '江唯一',
  
  // 裁判名字翻译
  'Ai Kun': '艾堃',
  'Shi Xiang': '石祥',
  'Xi Fei': '席飞',
  'Zhen Wei': '甄伟',
  'Wang Wei': '王伟',
  'Shunqi Tang': '唐顺奇',
  'Sun Kai': '孙凯',
  'Xie Lijun': '谢丽君',
  'Wenbin Zhu': '朱文斌',
  'Du Jianxin': '杜建新',
  'Kim Heegon': '金希坤',
  'Guo Jingtao': '郭静涛',
  'Wu Mingfeng': '吴明峰',
  'Danao Shan': '单丹奥',
  'Yi Huang': '黄毅',
  'Fu Ming': '傅明',
  'Ma Ji': '马济',
  'Zhou Xu': '周旭',
  'Niu Minghui': '牛明辉',
  'Ilgiz Tantashev': '伊尔吉兹·坦塔舍夫',
  'Wang Xihong': '王西红',
  'He Xin': '何鑫',
  'Jing Wang': '王静',
  'Yingbin Li': '李英彬',
  'Su Xiaofei': '苏晓飞',
  'Gao Peng': '高鹏',
  
  // 球员名字翻译（其他球队）
  'Gabriel Airton de Souza': '加布里埃尔',
  '加布里埃尔·艾尔顿·德索萨': '加布里埃尔',
  'Alexander Jojo': '亚历斯祖',
  '亚历山大·乔乔': '亚历斯祖',
  'Li Hao': '李昊',
  'Zhao Honglüe': '赵宏略',
  'Riccieli': '里奇埃利',
  'Sun Jie': '孙捷',
  'Gao Di': '高迪',
  'Zhao Bo': '赵博',
  'Liu Haofan': '刘浩帆',
  'Tong Lei': '童磊',
  'Alexandru Mitriță': '亚历山德鲁·米特里塔',
  'Sun Guowen': '孙国文',
  'Yago Cariello': '亚戈·卡里埃洛',
  'Lucas Possignolo': '卢卡斯·波西尼奥洛',
  'Dong Hengyi': '董恒毅',
  'Huo Shenping': '霍深平',
  'Leung Nok Hang': '梁诺恒',
  'Wang Yang': '王洋',
  'Tao Qianglong': '陶强龙',
  'Franko Andrijašević': '弗兰科·安德里亚舍维奇',
  'Ma Haoqi': '马浩淇',
  'Wu Wei': '吴伟',
  'Wang Shiqin': '王诗勤',
  'Wang Dalei': '王大雷',
  'Zheng Zheng': '郑铮',
  'Guilherme Madruga': '吉列尔梅·马达加',
  'Valeri Qazaishvili': '瓦列里·卡扎伊什维利',
  'Gao Zhunyi': '高准翼',
  'Huang Zhengyu': '黄政宇',
  'Raphaël Merkies': '拉斐尔·梅克斯',
  'Peng Xiao': '彭啸',
  'Sun Qihang': '孙启航',
  'Wu Xinghan': '吴兴涵',
  'Xie Wenneng': '谢文能',
  'Zhao Jianfei': '赵建飞',
  'Han Rongze': '韩镕泽',
  'Liu Junshuai': '刘军帅',
  'Jin Yangyang': '金洋洋',
  'Filipe Augusto': '菲利佩·奥古斯托',
  'Elvis Sarić': '埃尔维斯·萨里奇',
  'Wellington Silva': '威灵顿·席尔瓦',
  'Maiwulang Mijiti': '买吾兰·米吉提',
  'Liu Jiashen': '刘佳燊',
  'Jin Yonghao': '金泳镐',
  'Wei Suowei': '魏绍伟',
  'Didier Lamkel Zé': '迪迪埃·兰克尔·泽',
  'Liu Jun': '刘军',
  
  // 青岛西海岸球员
  'Xu Bin': '徐斌',
  'Zhang Xiuwei': '张修维',
  'Abdul-Aziz Yakubu': '阿卜杜勒-阿齐兹·亚库布',
  'Davidson da Luz Pereira': '戴维森·达卢斯·佩雷拉',
  'He Longhai': '何龙海',
  'Zhang Chengdong': '张呈栋',
  'Wang Hanyi': '王涵一',
  'Song Bowei': '宋博伟',
  'Chen Po-liang': '陈柏良',
  'Ding Haifeng': '丁海峰',
  'Yang Alex': '杨超声',
  'Duan Liuyu': '段刘愚',
  'He Xiaoke': '何小可',
  
  // 青岛海牛球员
  'Mou Pengfei': '牟鹏飞',
  'Xiao Kun': '肖鲲',
  'Sha Yibo': '沙一博',
  'Lin Chuangyi': '林创益',
  'Sun Zheng\'ao': '孙正傲',
  'Li Hailong': '李海龙',
  'Song Wenjie': '宋文杰',
  'Song Long': '宋龙',
  'Zheng Long': '郑龙',
  'Che Shiwei': '车世伟',
  'Luo Senwen': '罗森文',
  
  // 河南队球员
  'Park Ji-soo': '朴志洙',
  'Guo Jiayu': '郭嘉宇',
  'Long Wei': '龙威',
  'Gustavo Sauer': '古斯塔沃·绍尔',
  'Darlan Mendes': '达兰·门德斯',
  'Manuel Palacios': '曼努埃尔·帕拉西奥斯',
  'Liao Chengjian': '廖承坚',
  'Deng Hanwen': '邓涵文',
  'Zheng Haoqian': '郑昊乾',
  'Wei Minzhe': '魏敏哲',
  'Shao Puliang': '邵璞亮',
  'Wang Jinxian': '王进贤',
  'Ren Hang': '任航',
  'Wang Yi Denny': '王毅（丹尼）',
  'Zhong Jinbao': '钟晋宝',
  'Zikrulla Memetimin': '孜克热拉·麦麦提敏',
  'Ruan Jingwei': '阮靖伟',
  'Kang Wang': '康旺',
  
  // 裁判名字翻译（补充）
  'Qi Xing': '齐星',
  'Luo Zheng': '罗政',
  'Yang Xin': '杨欣',
  'Zhang Chao': '张超',
  'George King': '乔治·金',
  'Zhang Lei': '张雷',
  'Taqi Aljaafari': '塔奇·阿尔贾法里',
  'Cao Yi': '曹毅',
  'Hu Chengjun': '胡成军',
  'Jansen Mehmetjan': '詹森·梅米特江',
  'Shuran Gan': '甘树然',
  
  // 北京国安球员
  'Wu Shaocong': '吴少聪',
  'Michael Ngadeu-Ngadjui': '迈克尔·恩加德乌-恩加朱伊',
  'Gonçalo Rodrigues': '贡萨洛·罗德里格斯',
  'Fan Shuangjie': '樊双杰',
  'Zheng Tuluo': '郑图洛',
  'Li Lei': '李磊',
  'Zhang Xizhe': '张稀哲',
  'Wang Ziming': '王子铭',
  
  // 云南玉昆球员
  'Ma Zhen': '马振',
  'Li Songyi': '李思怡',
  'Dilimulati Maolaniyazi': '迪力木拉提·毛拉尼亚孜',
  'Alexandru Ioniță': '亚历山德鲁·约尼查',
  'Rui Filipe Cunha Correia': '鲁伊·菲利佩·库尼亚·科雷亚',
  'Tang Miao': '唐淼',
  'Oscar Maritu': '奥斯卡·马里图',
  'Zhang Chenliang': '张呈栋',
  'Han Zilong': '韩子龙',
  'John Hou Sæter': '约翰·侯·塞特',
  'Yu Jianxian': '余健贤',
  'Geng Xiaofeng': '耿晓锋',
  'Zhao Yuhao': '赵宇豪',
  'Ye Chugui': '叶楚贵',
  'Xiangshuo Zhang': '张祥硕',
  'Xuelong Sun': '孙学龙',
  'Duan Dezhi': '段德智',
  'Yin Congyao': '尹聪耀',
  'Yang He': '杨贺',
  
  // 成都蓉城球员
  'Liu Dianzuo': '刘殿座',
  'Timo Letschert': '蒂莫·莱切尔特',
  'Wei Shihao': '韦世豪',
  'Tim Chow': '周定洋',
  'Felipe Sousa': '费利佩·索萨',
  'Yahav Gurfinkel': '亚哈夫·古尔芬克尔',
  'Yan Dinghao': '严鼎皓',
  'Yang Shuai': '杨帅',
  'Jian Tao': '蹇韬',
  'Ran Weifeng': '冉伟峰',
  'Tang Xin': '唐鑫',
  'Han Pengfei': '韩鹏飞',
  'Dong Yanfeng': '董岩峰',
  'Tang Chuang': '唐创',
  'Mirahmetjan Muzepper': '买提江·木扎帕尔',
  'Gan Chao': '甘超',
  'Li Moyu': '李 moyu',
  'Xu Hong': '许宏',
  'Liao Rongxiang': '廖荣祥',
  'Wang Ziteng': '王梓腾',
  
  // 天津津门虎球员
  'Yan Bingliang': '闫炳良',
  'Wang Xianjun': '王贤君',
  'Alberto Quiles': '阿尔贝托·基莱斯',
  'Cristian Salvador': '克里斯蒂安·萨尔瓦多',
  'Xie Weijun': '谢维军',
  'Huang Jiahui': '黄家辉',
  'Yang Zihao': '杨梓豪',
  'Ba Dun': '巴顿',
  'Wang Qiuming': '王秋明',
  'Juan Antonio Ros': '胡安·安东尼奥·罗斯',
  'Li Yuefeng': '李悦峰',
  'Wang Zhenghao': '王政豪',
  'Yang Fan': '杨帆',
  'Li Yongjia': '李勇嘉',
  'Liu Junxian': '刘俊贤',
  'Qian Yumiao': '钱宇淼',
  'Chen Zhexuan': '陈哲宣',
  'Li Sirong': '李松睿',
  'Sun Ming Him': '孙铭徽',
  'Su Yuanjie': '苏缘杰',
  'Guo Hao': '郭皓',
  'Shi Yan': '史岩',
  
  // 河南队球员（补充）
  'Yixin Liu': '刘逸欣',
  'Oliver Gerbig': '奥利弗·格比格',
  'Yelijiang Shinaer': '叶力江·什那尔',
  'Zhong Yihao': '钟义浩',
  'Abudurousuli Abudulamu': '阿布都热西提·阿布都拉木',
  'Yang Yilin': '杨意林',
  'He Chao': '何超',
  'Huang Ruifeng': '黄锐峰',
  'Iago Maidana': '伊亚戈·马伊达纳',
  'Wang Guoming': '王国明',
  'Wang Shangyuan': '王上源',
  'Felippe Cardoso': '菲利佩·卡多佐',
  'Frank Acheampong': '弗兰克·阿奇姆彭',
  'Liu Bin': '刘斌',
  'Yang Kuo': '杨阔',
  'Niu Ziyi': '牛梓屹',
  'Zheng Dalun': '郑达伦',
  'Liu Xinyu': '刘鑫宇',
  'Lu Yongtao': '芦永涛',
  
  // 上海申花球员
  'Shanghai Shen': '上海申花',
  'Xue Qinghao': '薛庆浩',
  'Ibrahim Amadou': '易卜拉欣·阿马杜',
  'André Luis': '安德烈·路易斯',
  'Wilson Manafá': '威尔逊·马法',
  'Chan Shinichi': '陈俊乐',
  'Bao Yaxiong': '鲍亚雄',
  'Wang Shilong': '王诗龙',
  'Jin Shunkai': '金顺凯',
  'Xu Haoyang': '徐皓阳',
  'João Carlos Teixeira': '若昂·卡洛斯·特谢拉',
  'Yang Zexiang': '杨泽翔',
  'Yu Hanchao': '于汉超',
  'Aidi Fulangxisi': '艾迪·弗兰西斯',
  'Liu Chengyu': '刘诚宇',
  'Yang Haoyu': '杨皓宇',
  'Han Jiawen': '韩佳文',
  'Luismi': '路易西米',
  
  // 梅州客家球员
  'Darick Kobie Morris': '达里克·科比·莫里斯',
  'Guo Quanbo': '郭全博',
  'Branimir Jočić': '布拉尼米尔·约契奇',
  'Liao Junjian': '廖均健',
  'Jerome Ngom Mbekeli': '杰罗姆·恩戈姆·姆贝凯利',
  'Yang Chaosheng': '杨超声',
  'Yang Yihu': '杨一虎',
  'Wang Jianan': '王建南',
  'Deng Yubiao': '邓宇彪',
  'Mai Gaoling': '麦高崚',
  'Sun Jianxiang': '孙健祥',
  'Wei Minghe': '韦明赫',
  'Ziyi Tian': '田子弈',
  'Ji Shengpan': '吉盛潘',
  'Wei Xiangxin': '魏祥鑫',
  'Yang Ruiqi': '杨瑞琦',
  'Liu Yun': '刘云',
  'Zhong Haoran': '钟浩然',
  'Rao Weihui': '饶伟辉',
  'Wen Zhanlin': '温展霖',
  'Xianlong Yi': '易贤龙',
  'Rodrigo': '罗德里戈',
  'Elías Már Ómarsson': '埃利亚斯·马尔·奥马尔松',
  
  // 第18轮球员
  'Mutalifu Yimingkari': '木塔力甫·依明卡日',
  'Dong Hang': '董航',
  'Song Haoyu': '宋昊宇',
  
  // 长春亚泰球员（第17轮）
  'Wu Yake': '吴亚轲',
  'Abduhamit Abdugheni': '阿不都海米提',
  'Lazar Rosić': '拉扎尔·罗西奇',
  'Ohi Omoijuanfo': '奥希·奥莫伊胡安福',
  'He Yiran': '何一然',
  'Xuan Zhijian': '宣芷健',
  'Piao Taoyu': '朴韬宇',
  'Tan Long': '谭龙',
  'Stoppila Sunzu': '斯托皮拉·苏祖',
  'An Zhicheng': '安志成',
  'Zou Dehai': '邹德海',
  'Wang Yaopeng': '王耀鹏',
  'Li Shenyuan': '李申圆',
  'Zhang Huachen': '张华晨',
  'Tian Yuda': '田玉达',
  'Jing Boxi': '荆博雅',
  'Xu Yue': '徐越',
  'Yan Zhiyu': '闫雨',
  'Juan Salazar': '胡安·萨拉萨尔',
  'Sun Qinhan': '孙沁涵',
  'Wu Zhicheng': '吴智城',
  
  // 深圳新鹏城球员（第16轮）
  'Hu Ruibao': '胡睿宝',
  'Ning Li': '宁理',
  'Rade Dugalić': '拉德·杜加利奇',
  'Nan Song': '南松',
  
  // 大连英博球员（第15轮）
  'Song Yue': '宋岳',
  'Zhao Jianan': '赵健男',
  'Wang Chengkuai': '王呈奎',
  'Huang Shan': '黄山',
  'Cui Qi': '崔麒',
  
  // 河南队球员（第6轮）
  'Liu Jiahui': '刘家辉',
  'Du Zhixuan': '杜智轩',
  'Chen Keqiang': '陈克强',
  'Xingxian Li': '李星贤',
  
  // 浙江队球员（第14轮、第13轮）
  'Dong Yu': '董宇',
  'Will Donkin': '威尔·唐金',
  'Lucas Gazal': '卢卡斯·加扎尔',
  'Peng Xinli': '彭欣力',
  'Yu Jinyong': '俞金勇',
  'Liu Guobao': '刘国博',
  
  // 青岛海牛球员（第12轮）
  'Jia Feifan': '贾非凡',
  'Nikola Radmanovac': '尼古拉·拉德马诺维奇',
  'Chen Chunxin': '陈纯新',
  'Hu Jinghang': '胡靖航',
  'Anson Wong': '黄振声',
  
  // 武汉三镇球员（第11轮）
  'Alexandru Tudorie': '亚历山德鲁·图多里',
  'Xiaokaitijiang Taiyer': '肖开提江·塔依尔',
  'Zhang Tao': '张涛',
  'Liu Yiheng': '刘奕恒',
  'You Wenjie': '游文杰',
  'Zhang Zhenyang': '张振洋',
  
  // 北京国安球员（第10轮）
  'Yi Teng': '伊腾',
  'Yang Liyu': '杨立瑜',
  'Li Ruiyue': '李睿悦',
  'Li Shanghan': '李尚涵',
  
  // 云南玉昆球员（第9轮）
  'Tsui Wang Kit': '徐宏杰',
  'Qiu Shengjun': '邱盛炯',
  'Li Biao': '李彪',
  
  // 成都蓉城球员（第8轮）
  'Hu Hetao': '胡荷韬',
  'Ming-yang Yang': '杨明洋',
  'Yuan Mincheng': '元敏诚',
  'Pedro Delgado': '佩德罗·德尔加多',
  'Liao Lisheng': '廖力生',
  
  // 天津津门虎球员（第7轮）
  'Ruan Yang': '阮洋',
  'Fang Jingqi': '方镜淇',
  
  // 上海申花球员（第5轮）
  'Saulo Mineiro': '萨洛·梅内罗',
  'Zhou Zhengkai': '周正凯',
  'Xie Pengfei': '谢鹏飞',
  
  // 沧州雄狮球员（第4轮）
  'Wei Zhiwei': '魏志伟',
  'Yue Tze Nam': '余子谦',
  'Michael Cheukoua': '迈克尔·朱库瓦',
  'Wen Da': '文达',
  'Hao Zhang': '张浩',
  'Ling Zhongyang': '凌中阳',
  'Zhang Jiajie': '张家杰',
  
  // 第2轮球员（长春亚泰）
  'Robert Berić': '罗伯特·贝里奇',
  'Wylan Cyprien': '维兰·西普里安',
  'Zhou Junchen': '周俊辰',
  'Yao Xuchen': '姚旭晨',
  'Tudi Dilyimit': '迪力依米提·土地',
  
  // 裁判名字翻译（补充）
  'Adham Makhadmeh': '阿德哈姆·马赫德梅',
  'Xing Liu': '刘星',
  'Su Zihao': '苏子豪',
  'Tao Wan': '陶万',
  'Yige Dai': '戴弋戈',
  'Ma Ning': '马宁',
  'Zhao Boyang': '赵博扬',
  'Yan Lifu': '严立夫',
  'Zhao Liu': '赵亮',
  'Shengyu Sun': '孙盛宇',
  'Kai He': '贺凯',
  'Yang Yang': '杨杨',
  'Jindong Chen': '陈劲东',
  'He Long': '何龙',
  'Mu Yuchen': '穆宇辰',
  'Jin Jingyuan': '金京元',
  'Liang Songshang': '梁松尚',
  'Tang Chao': '唐超',
  'Choi Kanghee': '崔康熙',
  'Peng Deng': '彭登',
  'Guan Changliang': '关长亮',
  'Zhang Yangfan': '张扬帆',
  'Yunkun Ma': '马运坤',
  'Li Haixin': '李海新',
  'Jia Zhiliang': '贾志亮',
  'Gu Chunhan': '顾春含',
  'Wei Liu': '刘伟',
  'Milan Ristić': '米兰·里斯蒂奇',
  'Tang Rongdi': '唐荣地',
  'Xie Hui': '谢晖'
};

// 教练中文名字映射
const coachTranslations = {
  'Slaven Bilić': '斯拉文·比利奇',
  'Branko Ivanković': '布兰科·伊万科维奇',
  'Choi Kang-hee': '崔康熙',
  'Janković': '扬科维奇',
  'Dragan Stojković': '德拉甘·斯托伊科维奇',
  'Miloš Kruščić': '米洛斯·克鲁什契奇',
  'Siniša Jokanović': '西尼萨·约卡诺维奇',
  'Wu Jingui': '吴金贵',
  'Hao Wei': '郝伟',
  'Li Tie': '李铁',
  'Li Xiaopeng': '李小鹏',
  'Zhang Xiaorui': '张晓瑞',
  'Sun Jihai': '孙继海',
  'Zhu Jiong': '朱炯',
  'Gao Hongbo': '高洪波',
  'Fu Bo': '傅博',
  'Cui Enlang': '崔恩郎',
  'Kevin Muscat': '凯文·穆斯卡特',
  'Daniel Ramos': '丹尼尔·拉莫斯',
  'Leonid Slutskii': '莱昂尼德·斯卢茨基',
  'Ricardo Soares': '里卡多·苏亚雷斯',
  'Christian Lattanzio': '克里斯蒂安·拉坦齐奥',
  'Raúl Caneda': '劳尔·卡内达',
  'Quique Setién': '基克·塞蒂恩',
  'Seo Jung-won': '徐正源',
  'Li Guoxu': '李国旭',
  'Deng Zhuoxiang': '邓卓翔',
  'Yu Genwei': '于根伟',
  'Qu Gang': '瞿岗',
  'Shao Jiayi': '邵佳一',
  'Han Peng': '韩鹏'
};

// 球队中文名映射
const teamTranslations = {
  'Shanghai Port': '上海海港',
  'Shanghai Shenhua': '上海申花',
  'Wuhan Three Towns': '武汉三镇',
  'Zhejiang': '浙江队',
  'Zhejiang Professional': '浙江队',
  'Henan': '河南队',
  'Beijing Guoan': '北京国安',
  'Nantong Zhiyun': '南通支云',
  'Shandong Taishan': '山东泰山',
  'Meizhou Hakka': '梅州客家',
  'Qingdao Hainiu': '青岛海牛',
  'Shenzhen New Pengcheng': '深圳新鹏城',
  'Shenzhen Peng City': '深圳新鹏城',
  'Changchun Yatai': '长春亚泰',
  'Qingdao West Coast': '青岛西海岸',
  'Chengdu Rongcheng': '成都蓉城',
  'Cangzhou Mighty Lions': '沧州雄狮',
  'Tianjin Jinmen Tiger': '天津津门虎',
  'Jinmen Tiger': '天津津门虎',
  'Yunnan Yukun': '云南玉昆',
  'Dalian Yingbo': '大连英博',
  'Shanghai SIPG': '上海海港',
  'Shanghai Shen': '上海申花',
  'Wuhan Zall': '武汉三镇',
  'Beijing Sinobo Guoan': '北京国安',
  'Shandong Luneng': '山东泰山',
  'Qingdao FC': '青岛海牛',
  'Shenzhen FC': '深圳新鹏城',
  'Changchun Yatai FC': '长春亚泰',
  'Chengdu Better City': '成都蓉城',
  'Cangzhou Lions': '沧州雄狮',
  'Tianjin Teda': '天津津门虎'
};

// 赛事名称翻译
const competitionTranslations = {
  'Chinese Football Association Super League': '中国足球协会超级联赛'
};

// 球场名称翻译
const venueTranslations = {
  'Dalian Suoyuwan Football Stadium': '大连梭鱼湾专业足球场',
  'SAIC Motor Pudong Arena': '上汽浦东足球场',
  'Jinan Olympic Sports Center Stadium': '济南奥体中心体育场',
  'Qingdao Youth Football Stadium': '青岛青春足球场',
  'Qingdao West Coast University City Stadium': '青岛西海岸大学城体育场',
  'Workers\' Stadium': '工人体育场',
  'Chengdu Phoenix Hill Stadium': '成都凤凰山体育场',
  'Shanghai Stadium': '上海体育场',
  'Huitang Stadium': '五华体育场',
  'Changchun Stadium': '长春体育场',
  'Shenzhen City Stadium': '深圳大运中心体育场',
  'Zhengzhou Hanghai Stadium': '郑州航海体育场',
  'Yellow Dragon Sports Center': '黄龙体育中心',
  'Wuhan Sports Center Stadium': '武汉体育中心体育场',
  'Yuxi Highland Sports Center Stadium': '玉溪高原体育中心体育场',
  'TEDA Football Stadium': '泰达足球场'
};

// 事件类型中文名称
const typeNames = {
  'goal': '进球',
  'yellow_card': '黄牌',
  'red_card': '红牌',
  'substitution': '换人'
};

const dataDir = path.join(__dirname, '..', 'public', 'data', 'history', '2025');
const files = fs.readdirSync(dataDir).filter(f => f.endsWith('.json'));

let totalFiles = 0;
let totalTranslations = 0;
let totalTeamUpdates = 0;
let totalCoachUpdates = 0;
let totalCompetitionUpdates = 0;

files.forEach(file => {
  const filePath = path.join(dataDir, file);
  const content = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(content);
  
  let fileModified = false;
  let translationCount = 0;
  let teamUpdateCount = 0;
  let coachUpdateCount = 0;
  let competitionUpdateCount = 0;
  
  // 更新赛事名称
  if (data.match_info && data.match_info.competition && data.match_info.competition.name) {
    if (competitionTranslations[data.match_info.competition.name]) {
      data.match_info.competition.name = competitionTranslations[data.match_info.competition.name];
      fileModified = true;
      competitionUpdateCount++;
    }
  }
  
  // 更新球场名称
  if (data.match_info && data.match_info.venue && data.match_info.venue.name) {
    if (venueTranslations[data.match_info.venue.name]) {
      data.match_info.venue.name = venueTranslations[data.match_info.venue.name];
      fileModified = true;
      competitionUpdateCount++;
    }
  }
  
  // 更新轮次名称
  if (data.match_info && data.match_info.competition && data.match_info.competition.round) {
    const round = data.match_info.competition.round;
    if (round === 'Matchweek 1') {
      data.match_info.competition.round = '第1轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 2') {
      data.match_info.competition.round = '第2轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 3') {
      data.match_info.competition.round = '第3轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 4') {
      data.match_info.competition.round = '第4轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 5') {
      data.match_info.competition.round = '第5轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 6') {
      data.match_info.competition.round = '第6轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 7') {
      data.match_info.competition.round = '第7轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 8') {
      data.match_info.competition.round = '第8轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 9') {
      data.match_info.competition.round = '第9轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 10') {
      data.match_info.competition.round = '第10轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 11') {
      data.match_info.competition.round = '第11轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 12') {
      data.match_info.competition.round = '第12轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 13') {
      data.match_info.competition.round = '第13轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 14') {
      data.match_info.competition.round = '第14轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 15') {
      data.match_info.competition.round = '第15轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 16') {
      data.match_info.competition.round = '第16轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 17') {
      data.match_info.competition.round = '第17轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 18') {
      data.match_info.competition.round = '第18轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 19') {
      data.match_info.competition.round = '第19轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 20') {
      data.match_info.competition.round = '第20轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 21') {
      data.match_info.competition.round = '第21轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 22') {
      data.match_info.competition.round = '第22轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 23') {
      data.match_info.competition.round = '第23轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 24') {
      data.match_info.competition.round = '第24轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 25') {
      data.match_info.competition.round = '第25轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 26') {
      data.match_info.competition.round = '第26轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 27') {
      data.match_info.competition.round = '第27轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 28') {
      data.match_info.competition.round = '第28轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 29') {
      data.match_info.competition.round = '第29轮';
      fileModified = true;
      competitionUpdateCount++;
    } else if (round === 'Matchweek 30') {
      data.match_info.competition.round = '第30轮';
      fileModified = true;
      competitionUpdateCount++;
    }
  }
  
  // 更新裁判名字（处理特殊空格字符）
  if (data.match_info && data.match_info.referee) {
    const referee = data.match_info.referee;
    ['main', 'ar1', 'ar2', 'fourth', 'var'].forEach(refType => {
      if (referee[refType]) {
        let refName = referee[refType];
        // 移除特殊空格字符并转换为标准空格
        refName = refName.replace(/\u00A0/g, ' ').trim();
        if (playerTranslations[refName]) {
          referee[refType] = playerTranslations[refName];
          fileModified = true;
          translationCount++;
        }
      }
    });
  }
  
  // 更新球队信息
  if (data.teams) {
    ['home', 'away'].forEach(teamType => {
      if (data.teams[teamType]) {
        const team = data.teams[teamType];
        
        // 更新球队名字
        if (team.name && teamTranslations[team.name]) {
          team.name = teamTranslations[team.name];
          fileModified = true;
          teamUpdateCount++;
        }
        
        // 更新球队全名
        if (team.full_name) {
          if (team.full_name === 'Shenzhen Peng City足球俱乐部') {
            team.full_name = '深圳新鹏城足球俱乐部';
            fileModified = true;
            teamUpdateCount++;
          } else if (team.full_name === 'Jinmen Tiger足球俱乐部') {
            team.full_name = '天津津门虎足球俱乐部';
            fileModified = true;
            teamUpdateCount++;
          } else if (team.full_name === 'Shanghai Shen足球俱乐部') {
            team.full_name = '上海申花足球俱乐部';
            fileModified = true;
            teamUpdateCount++;
          }
        }
        
        // 扩展full_name
        if (team.name && (!team.full_name || team.full_name === team.name)) {
          if (team.name.includes('队')) {
            team.full_name = team.name.replace('队', '足球俱乐部');
          } else {
            team.full_name = team.name + '足球俱乐部';
          }
          fileModified = true;
          teamUpdateCount++;
        }
        
        // 更新教练名字（处理特殊空格字符）
        if (team.coach) {
          let coachName = team.coach.replace(/\u00A0/g, ' ').trim();
          if (coachTranslations[coachName]) {
            team.coach = coachTranslations[coachName];
            fileModified = true;
            coachUpdateCount++;
          }
        }
        
        // 更新队长名字（处理特殊空格字符）
        if (team.captain) {
          let captainName = team.captain.replace(/\u00A0/g, ' ').trim();
          if (playerTranslations[captainName]) {
            team.captain = playerTranslations[captainName];
            fileModified = true;
            translationCount++;
          }
        }
        
        // 翻译首发球员
        if (team.lineup) {
          team.lineup.forEach(player => {
            if (player.name) {
              let playerName = player.name.replace(/\u00A0/g, ' ').trim();
              if (playerTranslations[playerName]) {
                player.name = playerTranslations[playerName];
                fileModified = true;
                translationCount++;
              }
            }
          });
        }
        
        // 翻译替补球员
        if (team.substitutes) {
          team.substitutes.forEach(player => {
            if (player.name) {
              let playerName = player.name.replace(/\u00A0/g, ' ').trim();
              if (playerTranslations[playerName]) {
                player.name = playerTranslations[playerName];
                fileModified = true;
                translationCount++;
              }
            }
          });
        }
        
        // 翻译换人信息
        if (team.substitutions) {
          team.substitutions.forEach(sub => {
            if (sub.player_out) {
              let playerName = sub.player_out.replace(/\u00A0/g, ' ').trim();
              if (playerTranslations[playerName]) {
                sub.player_out = playerTranslations[playerName];
                fileModified = true;
                translationCount++;
              }
            }
            if (sub.player_in) {
              let playerName = sub.player_in.replace(/\u00A0/g, ' ').trim();
              if (playerTranslations[playerName]) {
                sub.player_in = playerTranslations[playerName];
                fileModified = true;
                translationCount++;
              }
            }
          });
        }
      }
    });
  }
  
  // 翻译事件中的球员名字并更新描述
  if (data.events) {
    data.events.forEach(event => {
      const type = event.type;
      const minute = event.minute;
      const minuteExtra = event.minute_extra;
      
      // 翻译球员名字（处理特殊空格字符）
      if (event.player) {
        let playerName = event.player.replace(/\u00A0/g, ' ').trim();
        if (playerTranslations[playerName]) {
          event.player = playerTranslations[playerName];
          fileModified = true;
          translationCount++;
        }
      }
      
      if (event.player2) {
        let playerName = event.player2.replace(/\u00A0/g, ' ').trim();
        if (playerTranslations[playerName]) {
          event.player2 = playerTranslations[playerName];
          fileModified = true;
          translationCount++;
        }
      }
      
      if (event.player_out) {
        let playerName = event.player_out.replace(/\u00A0/g, ' ').trim();
        if (playerTranslations[playerName]) {
          event.player_out = playerTranslations[playerName];
          fileModified = true;
          translationCount++;
        }
      }
      
      // 更新事件描述
      if (type === 'goal') {
        let timeDisplay = minute.toString();
        if (minuteExtra !== null && minuteExtra !== undefined) {
          timeDisplay += `+${minuteExtra}`;
        }
        if (event.player2) {
          event.description = `${event.player}在${timeDisplay}'进球，助攻球员：${event.player2}`;
        } else {
          event.description = `${event.player}在${timeDisplay}'进球`;
        }
        fileModified = true;
      } else if (type === 'yellow_card' || type === 'red_card') {
        let timeDisplay = minute.toString();
        if (minuteExtra !== null && minuteExtra !== undefined) {
          timeDisplay += `+${minuteExtra}`;
        }
        event.description = `${event.player}获得${typeNames[type]}`;
        fileModified = true;
      } else if (type === 'substitution') {
        let timeDisplay = minute.toString();
        if (minuteExtra !== null && minuteExtra !== undefined) {
          timeDisplay += `+${minuteExtra}`;
        }
        event.description = `${event.player_out}被换下，${event.player}替补登场`;
        fileModified = true;
      }
    });
  }
  
  if (fileModified) {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf-8');
    console.log(`✓ ${file}: 翻译了 ${translationCount} 处球员名字，更新了 ${teamUpdateCount} 处球队信息，更新了 ${coachUpdateCount} 处教练名字，更新了 ${competitionUpdateCount} 处赛事名称`);
    totalFiles++;
    totalTranslations += translationCount;
    totalTeamUpdates += teamUpdateCount;
    totalCoachUpdates += coachUpdateCount;
    totalCompetitionUpdates += competitionUpdateCount;
  } else {
    console.log(`- ${file}: 无需更新`);
  }
});

console.log(`\n总计: 处理了 ${totalFiles} 个文件，翻译了 ${totalTranslations} 处球员名字，更新了 ${totalTeamUpdates} 处球队信息，更新了 ${totalCoachUpdates} 处教练名字，更新了 ${totalCompetitionUpdates} 处赛事名称`);

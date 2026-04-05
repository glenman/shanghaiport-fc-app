const fs = require('fs');
const path = require('path');

// 翻译映射表
const translations = {
  // 球队名称翻译（基于2023中超联赛比赛结果）
  teams: {
    'Shanghai Port': '上海海港',
    'Wuhan Three Towns': '武汉三镇',
    'Shenzhen': '深圳队',
    'Cangzhou Mighty Lions': '沧州雄狮',
    'Shanghai Shenhua': '上海申花',
    'Tianjin Jinmen Tiger': '天津津门虎',
    'Jinmen Tiger': '天津津门虎',
    'Qingdao Hainiu': '青岛海牛',
    'Zhejiang': '浙江队',
    'Meizhou Hakka': '梅州客家',
    'Henan': '河南队',
    'Changchun Yatai': '长春亚泰',
    'Chengdu Rongcheng': '成都蓉城',
    'Nantong Zhiyun': '南通支云',
    'Beijing Guoan': '北京国安',
    'Shandong Taishan': '山东泰山',
    'Dalian Professional': '大连人'
  },

  // 球员名称翻译（基于上海海港2023一线队大名单）
  players: {
    // 上海海港球员
    'Yan Junling': '颜骏凌',
    'Li Ang': '李昂',
    'Tyias Browning': '蒋光太',
    'Wang Shenchao': '王燊超',
    'Zhang Linpeng': '张琳芃',
    'Cai Huikang': '蔡慧康',
    'Wu Lei': '武磊',
    'Oscar': '奥斯卡',
    'Paulinho': '保利尼奥',
    'Markus Pink': '马库斯·平科',
    'Lü Wenjun': '吕文君',
    'Chen Wei': '陈威',
    'Wei Zhen': '魏震',
    'Li Shenglong': '李圣龙',
    'Li Shenyuan': '李申圆',
    'Xu Xin': '徐新',
    'Chen Binbin': '陈彬彬',
    'Yang Shiyuan': '杨世元',
    'Yu Hai': '于海',
    'Du Jia': '杜佳',
    'Matías Vargas': '巴尔加斯',
    'Mirahmetjan Muzepper': '买提江',
    'Feng Jing': '冯劲',
    'He Guan': '贺惯',
    'Zhang Huachen': '张华晨',
    'Xi Anjie': '奚安杰',
    'Li Shuai': '李帅',
    'Liu Zhurun': '刘祝润',
    'Issa Kallon': '伊萨·卡隆',
    'Abduhamit Halik': '阿布拉汗·哈力克',
    'Liang Kun': '梁锟',
    'Xiang Rongjun': '向荣峻',
    'Wang Yiwei': '王逸伟',
    'Lv Kun': '吕坤',
    'Liu Xiaolong': '刘小龙',
    
    // 其他球队球员（基于2023赛季比赛数据）
    'Liu Dianzuo': '刘殿座',
    'Wallace': '华莱士',
    'Wei Shihao': '韦世豪',
    'Abdul-Aziz Yakubu': '雅库布',
    'Nicolae Stanciu': '斯坦丘',
    'Davidson da Luz Pereira': '戴维森',
    'Liu Yiming': '刘一鸣',
    'Gao Zhunyi': '高准翼',
    'He Chao': '何超',
    'Deng Hanwen': '邓涵文',
    'Xie Pengfei': '谢鹏飞',
    'Wu Fei': '吴飞',
    'Li Yang': '李扬',
    'Luo Senwen': '罗森文',
    'Yan Dinghao': '严鼎皓',
    'Zhang Xiaobin': '张晓彬',
    'Luo Jing': '罗竞',
    'Zhang Wentao': '张卫',
    'Ren Hang': '任航',
    'Wang Yi Denny': '王逸',
    'Tao Qianglong': '陶强龙',
    'Lü Haidong': '吕海东',
    'Zhang Hui': '张辉',
    'Xie Hui': '谢晖',
    'Yan Xiangchuang': '阎相闯',
    'Wu Yan': '吴龑',
    'Wang Xianjun': '王献钧',
    'Borislav Tsonev': '博里斯拉夫·措内夫',
    'Wang Yaopeng': '王耀鹏',
    'César Manzoki': '塞萨尔·曼佐基',
    'Wang Zhen\'ao': '王振奥',
    'Chen Rong': '陈荣',
    'Fei Yu': '费煜',
    'Lü Peng': '吕鹏',
    'Dong Hengyi': '董宏毅',
    'Pei Shuai': '裴帅',
    'Frank Acheampong': '弗兰克·阿切安庞',
    'Zhang Yuan': '张远',
    'Xu Haofeng': '徐浩峰',
    'Ning Li': '宁理',
    'Mi Haolun': '糜昊伦',
    'Yang Boyu': '杨博宇',
    'Huang Ruifeng': '黄瑞峰',
    'Shahsat Hujahmat': '沙赫萨特·胡贾马特',
    'Wei Minzhe': '魏敏哲',
    'Jiang Zhipeng': '姜至鹏',
    'Will Donkin': '沈子贵',
    'Romain Alessandrini': '罗曼·亚历山德里尼',
    'Liao Lei': '廖磊',
    'Zheng Dalun': '郑达伦',
    'Xu Yue': '徐越',
    'Wu Xingyu': '吴星宇',
    'Yuan Mincheng': '元敏诚',
    'Zhou Xin': '周鑫',
    'Du Yuezheng': '杜月征',
    'Chen Guoliang': '陈国良',
    'David Andújar': '戴维-安杜哈尔',
    'Robert Berić': '罗伯特·贝里奇',
    'Farley Vieira Rosa': '法利佩',
    'Ming Tian': '明天',
    'Ba Dun': '巴顿',
    'Wang Qiuming': '王秋明',
    'Su Yuanjie': '苏缘杰',
    'Guo Hao': '郭皓',
    'Fran Mérida': '梅里达',
    'Fang Jingqi': '方镜淇',
    'Wang Zhenghao': '王政豪',
    'Yu Yang': '于洋',
    'Zhao Yingjie': '赵英杰',
    'Xie Weijun': '谢维军',
    'Xuelong Sun': '孙学龙',
    'Gao Huaze': '高华泽',
    'Chang Feiya': '常飞亚',
    'Qian Yumiao': '钱宇淼',
    'Piao Taoyu': '朴韬宇',
    'Xu Jiamin': '徐嘉敏',
    'Wang Dalei': '王大雷',
    'Zheng Zheng': '郑铮',
    'Moisés Magalhães': '莫伊塞斯',
    'Liu Yang': '刘洋',
    'Liao Lisheng': '廖力生',
    'Liu Binbin': '刘彬彬',
    'Li Yuanyi': '李源一',
    'Marouane Fellaini': '费莱尼',
    'Shi Ke': '石柯',
    'Chen Pu': '陈蒲',
    'Ji Xiang': '吉翔',
    'Han Rongze': '韩镕泽',
    'Liu Shibo': '刘世博',
    'Tong Lei': '童磊',
    'Zhang Chi': '张弛',
    // 上海申花球员
    'Ma Zhen': '马镇',
    'Yan Xinli': '晏新力',
    'Jiang Shenglong': '蒋圣龙',
    'Zhu Chenjie': '朱辰杰',
    'Amadou': '阿马杜',
    'Xu Haoyang': '徐皓阳',
    'Liu Ruofan': '刘若钒',
    'Teixeira': '特谢拉',
    'Mala': '马莱莱',
    'Yang Zexiang': '杨泽翔',
    'Bassogog': '巴索戈',
    'Zhang Wei': '张威',
    'Yu Hanchao': '于汉超',
    'Cui Lin': '崔麟',
    'Jin Yangyang': '金洋洋',
    'Bai Jiajun': '柏佳骏',
    'Xu Yougang': '徐友刚',
    'Peng Xinli': '彭欣力',
    'Cao Yunding': '曹赟定',
    'Zhou Junchen': '周俊辰',
    'Bao Yaxiong': '鲍亚雄',
    'Xue Qinghao': '薛庆浩',
    'Eddy': '艾迪',
    'Wang Haijian': '汪海健',
    'Qi Long': '齐龙',
    'He Longhai': '何龙海',
    'Fernando': '费尔南多',
    // 北京国安球员
    'Han Jiaqi': '韩佳奇',
    'Jiang Xiangyou': '姜祥佑',
    'De Souza': '德索萨',
    'Ademi': '阿代米',
    'Ngadeu-Ngadjui': '恩加德乌',
    'Ademilson': '阿德本罗',
    'Yang Liyu': '杨立瑜',
    'Feng Boxuan': '冯博轩',
    'Fang Hao': '方昊',
    'Li Lei': '李磊',
    'Nu\'eraili': '努尔艾力',
    'Liang Shaowen': '梁少文',
    'Yan Yu': '闫雨',
    'He Xiaoqiang': '和晓强',
    'Ma Yujun': '马钰钧',
    'Gao Jian': '高健',
    'Yu Dabao': '于大宝',
    'Chen Yanpu': '陈彦朴',
    'Ruan Qilong': '阮奇龙',
    'Jiang Wenhao': '江文豪',
    'Duan Dezhi': '段徳智',
    'Wang Tong': '王彤',
    'Huang Zhengyu': '黄政宇',
    'Matheus Pato': '马特乌斯·帕托',
    'Hu Jinghang': '胡靖航',
    'Zhao Jianfei': '赵剑非',
    'Fernandinho': '费南多',
    'Jia Feifan': '贾非凡',
    'Song Long': '宋龙',
    'Zou Dehai': '邹德海',
    'Hou Sen': '侯森',
    'Zhang Xizhe': '张稀哲',
    'Gao Tianyi': '高天意',
    'Zhang Chengdong': '张呈栋',
    'Fabio': '法比奥',
    // 沧州雄狮球员
    'Sun Jianxiang': '孙健祥',
    'Li Peng': '栗鹏',
    'Zhao Honglue': '赵宏略',
    'Yan Zihao': '晏紫豪',
    'Yang Yun': '杨云',
    'Zang Yifeng': '臧一锋',
    'Lin Chuangyi': '林创益',
    'Jürgen Locadia': '洛卡迪亚',
    'Oscar': '奥斯卡',
    'Cai Mingmin': '蔡明民',
    'Sun Qinhang': '孙沁涵',
    'Shao Puliang': '邵镤亮',
    'Wang Peng': '王鹏',
    'Zheng Kaimu': '郑凯木',
    'Piao Shihao': '朴世豪',
    'Yao Xuchen': '么旭辰',
    'Serhiy Kuznetsov': '朱可夫',
    'Liu Xinyu': '刘鑫瑜',
    'Mato Škoro': '什科里奇',
    'Wu Wei': '吴畏',
    'He Youzu': '何友族',
    'Zhang Yue': '张越',
    'Guo Yunqi': '郭芸齐',
    'Ma Fuyu': '马辅渔',
    'Yang Xiaotian': '杨笑天',
    'Han Feng': '韩锋',
    'Liu Yang': '刘洋',
    'Deabeas Owusu-Sekyere': '奥乌苏',
    'Zhang Xiangshuo': '张祥硕',
    // 深圳队球员
    'Dong Chunyu': '董春雨',
    'Xu Haofeng': '徐浩峰',
    'Yuan Mincheng': '元敏诚',
    'Zhang Yuan': '张远',
    'Jiang Zhipeng': '姜至鹏',
    'Xu Yue': '徐越',
    'Huang Ruifeng': '黄锐烽',
    'Shahsat Hujahmat': '夏合扎提',
    'Will Donkin': '沈子贵',
    'Zheng Dalun': '郑达伦',
    'Frank Acheampong': '阿奇姆彭',
    'Wei Minzhe': '魏黾哲',
    'Pei Shuai': '裴帅',
    'Liao Lei': '廖磊',
    'Li Ning': '李宁',
    'Liu Yue': '刘越',
    'Zhang Yuan': '张源',
    'Wu Xingyu': '吴星宇',
    'Du Yuezheng': '杜月徴',
    'Lyu Jiaqiang': '吕佳强',
    'Chen Guoliang': '陈国良',
    'Wang Chengkuai': '王成快',
    'Mi Haolun': '糜昊伦'
  },

  // 教练名称翻译
  coaches: {
    'Javier Pereira': '哈维尔·佩雷拉',
    'Pedro Morilla': '佩德罗·莫里利亚',
    'Choi Kang-hee': '崔康熙',
    'Choi Kanghee': '崔康熙',
    'Slavoljub Muslin': '斯拉沃柳布·穆斯利恩',
    'Aleksandar Stanojevic': '亚历山大·斯坦诺耶维奇',
    'Rafa Benitez': '拉斐尔·贝尼特斯',
    'Chang Woe-ryong': '张外龙',
    'Dragan Skocic': '德拉甘·斯科契奇',
    'Zhou Jinli': '周金利',
    'Sretenovic': '斯特雷托维奇',
    'Juan Carlos Garrido': '胡安·卡洛斯·加里多',
    'Yao Junsheng': '姚俊生',
    'Chen Tao': '陈涛',
    'Yu Genwei': '于根伟',
    'Wu Jingui': '吴金贵',
    'Stanley Menzo': '斯坦利·门佐',
    'Ricardo Soares': '里卡多·苏亚雷斯',
    'Zhao Junzhe': '肇俊哲'
  },

  // 裁判名称翻译
  referees: {
    'Zhang Lei': '张雷',
    'Wang Dexin': '王德鑫',
    'Su Xiaofei': '苏晓飞',
    'Zhen Wei': '甄伟',
    'Jin Jingyuan': '金京元',
    'Ai Kun': '艾堃',
    'Shi Xiang': '石祥',
    'Xi Fei': '席飞',
    'Wang Wei': '王伟',
    'Fu Ming': '傅明',
    'Ma Ning': '马宁',
    'Li Haixin': '李海新',
    'Wang Zhe': '王哲',
    'Tang Shunqi': '唐顺齐',
    'Chen Gang': '陈钢',
    'Huang Yejun': '黄烨军',
    'Shi Zhenlu': '石祯禄',
    'Sun Kai': '孙凯',
    'Wang Xihong': '王喜红',
    'Shengyu Sun': '圣宇',
    'Jing Wang': '金京元',
    'Yige Dai': '戴一戈',
    'Cao Yi': '曹奕',
    'Niu Minghui': '牛明辉',
    'Zhang Long': '张龙',
    'Yingbin Li': '李英斌',
    'Zhang Xuechen': '张学晨',
    'Jia Zhiliang': '贾志亮',
    'Hu Chengjun': '胡成军',
    'Sun Jin': '孙晋',
    'Gu Chunhan': '顾春含',
    'Tang Chao': '唐超',
    'Luo Zheng': '罗政',
    'Shuran Gan': '舒然甘',
    'Du Jianxin': '杜建新',
    'Bo Jiang': '江波',
    'Yi Huang': '黄翼'
  },

  // 球场名称翻译
  venues: {
    'Wuhan Sports Center Stadium': '武汉体育中心体育场',
    'Shanghai Stadium': '上海体育场',
    'Pudong Football Stadium': '上汽浦东足球场',
    'SAIC Motor Pudong Arena': '上汽浦东足球场',
    'Shenzhen Universiade Sports Centre': '深圳大运中心',
    'Cangzhou Stadium': '沧州体育场',
    'Hongkou Football Stadium': '虹口足球场',
    'Tianjin Olympic Center': '天津奥林匹克中心',
    'Tianjin Olympic Center Stadium': '天津奥林匹克中心',
    'Qingdao Hainiu Stadium': '青岛海牛体育场',
    'Huzhou Olympic Sports Center': '湖州奥林匹克体育中心',
    'Meizhou Hakka Stadium': '梅州客家体育场',
    'Zhengzhou Hanghai Stadium': '郑州航海体育场',
    'Changchun Yatai Stadium': '长春亚泰体育场',
    'Changchun Stadium': '长春体育场',
    'Chengdu Phoenix Hill Football Stadium': '成都凤凰山足球场',
    'Chengdu Phoenix Hill Stadium': '成都凤凰山足球场',
    'Rugao Olympic Sports Center': '如皋奥林匹克体育中心',
    'Workers Stadium': '工人体育场',
    'Jinan Olympic Sports Center': '济南奥林匹克体育中心',
    'Jinan Olympic Sports Center Stadium': '济南奥林匹克体育中心',
    'Dalian Barracuda Bay': '大连梭鱼湾足球场',
    'Huitang Stadium': '惠堂体育场',
    'Guzhenkou University City Sports Center': '古镇口大学城体育中心',
    'Dalian Sports Center Stadium': '大连体育中心体育场'
  },

  // 赛事名称翻译
  competitions: {
    'Chinese Football Association Super League': '中国足球协会超级联赛',
    'Super League': '中超联赛'
  },

  // 事件描述翻译
  events: {
    'GOAL': '进球',
    'YELLOW CARD': '黄牌',
    'RED CARD': '红牌',
    'SUBSTITUTION': '换人'
  }
};

// 翻译函数
function translateValue(key, value) {
  if (typeof value !== 'string') return value;
  
  // 处理特殊空格字符
  const normalizedValue = value.replace(/\u00A0/g, ' ').trim();
  
  // 按优先级检查各个翻译表
  if (translations.players[normalizedValue]) {
    return translations.players[normalizedValue];
  }
  if (translations.teams[normalizedValue]) {
    return translations.teams[normalizedValue];
  }
  if (translations.coaches[normalizedValue]) {
    return translations.coaches[normalizedValue];
  }
  if (translations.referees[normalizedValue]) {
    return translations.referees[normalizedValue];
  }
  if (translations.venues[normalizedValue]) {
    return translations.venues[normalizedValue];
  }
  if (translations.competitions[normalizedValue]) {
    return translations.competitions[normalizedValue];
  }
  if (translations.events[normalizedValue]) {
    return translations.events[normalizedValue];
  }
  
  // 处理轮次格式转换
  if (normalizedValue.startsWith('Matchweek ')) {
    const roundNumber = normalizedValue.replace('Matchweek ', '');
    return `第${roundNumber}轮`;
  }
  
  return value;
}

// 递归翻译对象
function translateObject(obj) {
  if (Array.isArray(obj)) {
    return obj.map(item => translateObject(item));
  }
  
  if (obj !== null && typeof obj === 'object') {
    const translatedObj = {};
    
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        translatedObj[key] = translateObject(obj[key]);
      }
    }
    
    return translatedObj;
  }
  
  return translateValue('', obj);
}

// 处理单个文件
function processFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const data = JSON.parse(content);
    
    // 翻译数据
    const translatedData = translateObject(data);
    
    // 写回文件
    fs.writeFileSync(filePath, JSON.stringify(translatedData, null, 2), 'utf8');
    console.log(`已处理: ${filePath}`);
    return true;
  } catch (error) {
    console.error(`处理文件时出错: ${filePath}`, error);
    return false;
  }
}

// 主函数
function main() {
  const directory = path.join(__dirname, '../public/data/history/2023');
  
  try {
    const files = fs.readdirSync(directory);
    const jsonFiles = files.filter(file => file.endsWith('.json'));
    
    console.log(`开始处理2023赛季JSON文件，共 ${jsonFiles.length} 个文件...`);
    
    let successCount = 0;
    let totalCount = jsonFiles.length;
    
    jsonFiles.forEach(file => {
      const filePath = path.join(directory, file);
      if (processFile(filePath)) {
        successCount++;
      }
    });
    
    console.log(`处理完成！成功: ${successCount}, 失败: ${totalCount - successCount}`);
    
  } catch (error) {
    console.error('读取目录时出错:', error);
  }
}

// 运行脚本
main();
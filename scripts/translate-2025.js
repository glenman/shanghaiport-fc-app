const fs = require('fs');
const path = require('path');

// 翻译映射表
const translations = {
  // 球队名称翻译
  teams: {
    'Shanghai Port': '上海海港',
    'Wuhan Three Towns': '武汉三镇',
    'Shandong Taishan': '山东泰山',
    'Beijing Guoan': '北京国安',
    'Tianjin Jinmen Tiger': '天津津门虎',
    'Chengdu Rongcheng': '成都蓉城',
    'Qingdao Hainiu': '青岛海牛',
    'Henan Songshan Longmen': '河南嵩山龙门',
    'Shenzhen Peng City': '深圳新鹏城',
    'Dalian Professional': '大连人',
    'Changchun Yatai': '长春亚泰',
    'Nantong Zhiyun': '南通支云',
    'Zhejiang': '浙江队',
    'Meizhou Hakka': '梅州客家',
    'Qingdao West Coast': '青岛西海岸',
    'Xiamen Egret': '厦门白鹭'
  },

  // 球员名称翻译（基于上海海港2025一线队大名单）
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
    'Gustavo': '古斯塔沃',
    'Matías Vargas': '巴尔加斯',
    'Lü Wenjun': '吕文君',
    'Chen Wei': '陈威',
    'Wei Zhen': '魏震',
    'Li Shenglong': '李圣龙',
    'Xu Xin': '徐新',
    'Will Donkin': '沈子贵',
    'Léo Cittadini': '莱奥·奇塔迪尼',
    'Wang Zhen\'ao': '王振澳',
    'Yang Shiyuan': '杨世元',
    'Chen Binbin': '陈彬彬',
    'Jussa': '马修斯·尤萨',
    'Fu Huan': '傅欢',
    'Du Jia': '杜佳',
    'Feng Jing': '冯劲',
    'He Guan': '贺惯',
    'Bao Shimeng': '鲍世蒙',
    'Li Shuai': '李帅',
    'Liu Zhurun': '刘祝润',
    'Chen Xuhuang': '陈序煌',
    'Li Deming': '黎德明',
    'Liang Kun': '梁锟',
    'Wang Yiwei': '王逸伟',
    'Liu Xiaolong': '刘小龙',
    'Meng Jingchao': '孟敬朝',
    'Li Zhiliang': '李智良',
    'Wang Yi Denny': '王逸',
    'Feierding Aisikaer': '艾菲尔丁·艾斯卡尔',
    
    // 其他球队球员（常见球员）
    'Edu García': '埃杜·加西亚',
    'Liu Dianzuo': '刘殿座',
    'Jiang Zhipeng': '姜至鹏',
    'Park Ji-soo': '朴志洙',
    'Pedro': '佩德罗',
    'Romário Baldé': '罗马里奥·巴尔德',
    'Zhang Xiaobin': '张晓彬',
    'He Chao': '何超',
    'Deng Hanwen': '邓涵文',
    'Darlan Mendes': '达兰·门德斯',
    'Wumitijiang Yusupu': '吾米提江·玉苏普',
    'Wei Minzhe': '魏敏哲',
    'Tao Qianglong': '陶强龙',
    'Liu Ruofan': '刘若钒',
    'Xiaokaitijiang Taiyer': '肖开提江·塔依尔',
    'Zhang Hui': '张辉',
    'Chen Yuhao': '陈宇浩',
    'Liu Yiming': '刘一鸣',
    'Liu Yue': '刘越',
    'Ren Hang': '任航',
    'He Tongshuai': '何统帅'
  },

  // 教练名称翻译
  coaches: {
    'Kevin Muscat': '凯文·穆斯卡特',
    'Choi Kang-hee': '崔康熙',
    'Slavoljub Muslin': '斯拉沃柳布·穆斯利恩',
    'Javier Pereira': '哈维尔·佩雷拉',
    'Aleksandar Stanojevic': '亚历山大·斯坦诺耶维奇',
    'Rafa Benitez': '拉斐尔·贝尼特斯',
    'Chang Woe-ryong': '张外龙',
    'Dragan Skocic': '德拉甘·斯科契奇',
    'Zhou Jinli': '周金利',
    'Sretenovic': '斯特雷托维奇',
    'Juan Carlos Garrido': '胡安·卡洛斯·加里多',
    'Yao Junsheng': '姚俊生'
  },

  // 裁判名称翻译
  referees: {
    'Ai Kun': '艾堃',
    'Shi Xiang': '石祥',
    'Xi Fei': '席飞',
    'Zhen Wei': '甄伟',
    'Wang Wei': '王伟',
    'Zhang Lei': '张雷',
    'Fu Ming': '傅明',
    'Ma Ning': '马宁',
    'Li Haixin': '李海新',
    'Jin Jingyuan': '金京元',
    'Wang Zhe': '王哲',
    'Tang Shunqi': '唐顺齐',
    'Chen Gang': '陈钢',
    'Huang Yejun': '黄烨军'
  },

  // 球场名称翻译
  venues: {
    'Shanghai Stadium': '上海体育场',
    'Pudong Football Stadium': '上汽浦东足球场',
    'SAIC Motor Pudong Arena': '上汽浦东足球场',
    'Wuhan Three Towns Stadium': '武汉三镇体育场',
    'Wuhan Sports Center Stadium': '武汉体育中心体育场',
    'Jinan Olympic Sports Center': '济南奥林匹克体育中心',
    'Jinan Olympic Sports Center Stadium': '济南奥林匹克体育中心',
    'Workers Stadium': '工人体育场',
    'Tianjin Olympic Center': '天津奥林匹克中心',
    'Tianjin Olympic Center Stadium': '天津奥林匹克中心',
    'Chengdu Phoenix Hill Football Stadium': '成都凤凰山足球场',
    'Chengdu Phoenix Hill Stadium': '成都凤凰山足球场',
    'Qingdao Hainiu Stadium': '青岛海牛体育场',
    'Zhengzhou Hanghai Stadium': '郑州航海体育场',
    'Shenzhen Universiade Sports Centre': '深圳大运中心',
    'Dalian Barracuda Bay': '大连梭鱼湾足球场',
    'Changchun Yatai Stadium': '长春亚泰体育场',
    'Changchun Stadium': '长春体育场',
    'Rugao Olympic Sports Center': '如皋奥林匹克体育中心',
    'Huzhou Olympic Sports Center': '湖州奥林匹克体育中心',
    'Meizhou Hakka Stadium': '梅州客家体育场',
    'Qingdao West Coast Stadium': '青岛西海岸体育场',
    'Xiamen Egret Stadium': '厦门白鹭体育场',
    'Cangzhou Stadium': '沧州体育场',
    'Huitang Stadium': '惠堂体育场',
    'Guzhenkou University City Sports Center': '古镇口大学城体育中心',
    'Dalian Sports Center Stadium': '大连体育中心体育场'
  },

  // 赛事名称翻译
  competitions: {
    'Chinese Super League': '中国足球协会超级联赛',
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
  const directory = path.join(__dirname, '../public/data/history/2025');
  
  try {
    const files = fs.readdirSync(directory);
    const jsonFiles = files.filter(file => file.endsWith('.json'));
    
    console.log(`开始处理2025赛季JSON文件，共 ${jsonFiles.length} 个文件...`);
    
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
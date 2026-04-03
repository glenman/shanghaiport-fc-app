const fs = require('fs');
const path = require('path');

// 翻译映射表
const translations = {
  // 球员英文名 -> 中文名
  'Nemanja Čović': '内马尼亚·科维奇',
  'Bruno Nazário': '布鲁诺·纳扎里奥',
  'Feng Boyuan': '冯伯元',
  'Huang Ruifeng': '黄锐烽',
  'Wang Shangyuan': '王上源',
  'Xu Haofeng': '徐浩峰',
  'Frank Acheampong': '弗兰克·阿奇姆彭',
  'Andrea Compagno': '安德烈亚·孔帕尼奥',
  'Xie Weijun': '谢维军',
  'Qian Yumiao': '钱宇淼',
  'Ming Tian': '明天',
  'Su Yuanjie': '苏缘杰',
  'Yang Zihao': '杨梓豪',
  'Guo Hao': '郭皓',
  'Mile Škorić': '米莱·斯科里奇',
  'Shi Yan': '史岩',
  'Ba Dun': '巴顿',
  'Li Shuai': '李帅',
  'Yan Zihao': '闫梓豪',
  'Zheng Dalun': '郑大伦',
  'Georgy Zhukov': '格奥尔基·朱可夫',
  'Léo Cittadini': '莱奥·奇塔迪尼',
  'Matías Vargas': '马蒂亚斯·巴尔加斯',
  'Wu Lei': '武磊',
  'Oscar': '奥斯卡',
  'Li Ang': '李昂',
  'Huang Zichang': '黄紫昌',
  'Zhang Linpeng': '张琳芃',
  'Xu Jiamin': '徐嘉敏',
  'Yixin Liu': '刘易鑫',
  'Đorđe Denić': '乔尔杰·德尼奇',
  'Wang Gang': '王刚',
  'Wang Peng': '王鹏',
  'Chen Zhechao': '陈哲超',
  'Zhang Yufeng': '张宇峰',
  'Shi Ke': '石柯',
  'Wang Shenchao': '王燊超',
  'Li Shenglong': '李圣龙',
  'Feng Jing': '冯劲',
  'Wei Zhen': '魏震',
  'Xu Xin': '徐新',
  'Lü Wenjun': '吕文君',
  'Liu Jiachen': '刘佳臣',
  'Chen Binbin': '陈彬彬',
  'Zhang Wei': '张卫',
  'Zhao Mingjian': '赵明剑',
  'Tan Long': '谭龙',
  'Jin Qiang': '金强',
  'Sun Guowen': '孙国文',
  'Wu Yake': '吴亚轲',
  'Liu Yiming': '刘奕鸣',
  'Jin Taiyan': '金泰延',
  'Yang Liyu': '杨立瑜',
  'Gao Tianyi': '高天意',
  'Zhang Xizhe': '张稀哲',
  'Yu Dabao': '于大宝',
  'Guo Quanbo': '郭全博',
  'Jiang Shenglong': '蒋圣龙',
  'Zhu Chenjie': '朱辰杰',
  'Peng Xinli': '彭欣力',
  'Wu Xi': '吴曦',
  'Zhang Yuning': '张玉宁',
  'Han Pengfei': '韩鹏飞',
  'Zhang Chengdong': '张呈栋',
  'He Chao': '何超',
  'Liu Binbin': '刘彬彬',
  'Chen Kerui': '陈克瑞',
  'Zhang Xinyu': '张新宇',
  'Zhang Yunqi': '张云祺',
  'Wang Jiajie': '王嘉杰',
  'Liu Yilong': '刘奕隆',
  'Tang Jin': '唐金',
  'Yang Shiyuan': '杨世元',
  'Gustavo': '古斯塔沃',
  'Wu Yufan': '吴宇帆',
  'Guo Tianyu': '郭田雨',
  'Zhao Xuri': '赵旭日',
  'Zhang Zhihao': '张治豪',
  'Zhang Yudong': '张煜东',
  'Hu Jinghang': '胡靖航',
  'Chen Tao': '陈涛',
  'Wang Chu': '王楚',
  'Liu Junshuai': '刘军帅',
  'Zhang Yan': '张岩',
  'Zhou Chenxu': '周晨旭',
  'Huang Jiajun': '黄佳军',
  'Zhang Wei': '张伟',
  'Liu Guobo': '刘博博',
  'Zhao Jianbo': '赵剑波',
  'Wang Jianan': '王建安',
  'Wang Ziming': '王梓铭',
  'Jiang Ning': '姜宁',
  'Li Zheyu': '李哲宇',
  'Wang Chen': '王晨',
  'Sun Yue': '孙越',
  'Liu Ruicheng': '刘瑞成',
  'Xadas': '哈达斯',
  'Nelson': '内尔森',
  'Serginho': '塞尔吉尼奥',
  'Thiago': '蒂亚戈',
  'Tiago': '蒂亚戈',
  'Fernandinho': '费尔南迪尼奥',
  'Rodrigo': '罗德里戈',
  'Crysan': '克里桑',
  'Leo': '莱奥',
  'Pedro': '佩德罗',
  'Elkeson': '埃尔克森',
  'Guilherme': '吉尔赫梅',
  'Jadson': '贾德森',
  'Henan': '河南队'
};

const dataDir = path.join(__dirname, '..', 'public', 'data', 'history', '2024');
const files = fs.readdirSync(dataDir).filter(f => f.endsWith('.json'));

let totalFiles = 0;
let totalTranslations = 0;

files.forEach(file => {
  const filePath = path.join(dataDir, file);
  const content = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(content);
  
  let fileModified = false;
  let translationCount = 0;
  
  // 翻译球员阵容
  if (data.teams) {
    ['home', 'away'].forEach(teamType => {
      if (data.teams[teamType]) {
        const team = data.teams[teamType];
        
        // 翻译球队名称
        if (team.name && translations[team.name]) {
          team.name = translations[team.name];
          fileModified = true;
          translationCount++;
        }
        if (team.full_name && translations[team.full_name]) {
          team.full_name = translations[team.full_name];
          fileModified = true;
          translationCount++;
        }
        
        // 翻译首发阵容
        if (team.lineup && Array.isArray(team.lineup)) {
          team.lineup.forEach(player => {
            if (player.name && translations[player.name]) {
              player.name = translations[player.name];
              fileModified = true;
              translationCount++;
            }
          });
        }
        
        // 翻译替补阵容
        if (team.substitutes && Array.isArray(team.substitutes)) {
          team.substitutes.forEach(player => {
            if (player.name && translations[player.name]) {
              player.name = translations[player.name];
              fileModified = true;
              translationCount++;
            }
          });
        }
        
        // 翻译换人信息
        if (team.substitutions && Array.isArray(team.substitutions)) {
          team.substitutions.forEach(sub => {
            if (sub.player_in && translations[sub.player_in]) {
              sub.player_in = translations[sub.player_in];
              fileModified = true;
              translationCount++;
            }
            if (sub.player_out && translations[sub.player_out]) {
              sub.player_out = translations[sub.player_out];
              fileModified = true;
              translationCount++;
            }
          });
        }
        
        // 翻译教练和队长
        if (team.coach && translations[team.coach]) {
          team.coach = translations[team.coach];
          fileModified = true;
          translationCount++;
        }
        if (team.captain && translations[team.captain]) {
          team.captain = translations[team.captain];
          fileModified = true;
          translationCount++;
        }
      }
    });
  }
  
  // 翻译比赛事件
  if (data.events && Array.isArray(data.events)) {
    data.events.forEach(event => {
      if (event.player && translations[event.player]) {
        event.player = translations[event.player];
        fileModified = true;
        translationCount++;
      }
      if (event.player2 && translations[event.player2]) {
        event.player2 = translations[event.player2];
        fileModified = true;
        translationCount++;
      }
      if (event.player_out && translations[event.player_out]) {
        event.player_out = translations[event.player_out];
        fileModified = true;
        translationCount++;
      }
      // 更新description
      if (event.type === 'goal') {
        if (event.player2 && event.player2 !== '') {
          event.description = `${event.player}进球，助攻球员：${event.player2}`;
        } else {
          event.description = `${event.player}进球`;
        }
      } else if (event.type === 'substitution' && event.player_out && event.player) {
        event.description = `${event.player_out}被换下，${event.player}替补登场`;
      }
    });
  }
  
  if (fileModified) {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf-8');
    console.log(`✓ ${file}: 翻译了 ${translationCount} 处`);
    totalFiles++;
    totalTranslations += translationCount;
  } else {
    console.log(`- ${file}: 无需翻译`);
  }
});

console.log(`\n总计: 处理了 ${totalFiles} 个文件，翻译了 ${totalTranslations} 处`);

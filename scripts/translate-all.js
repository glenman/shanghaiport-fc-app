const fs = require('fs');
const path = require('path');

// 球员中文名字映射
const playerTranslations = {
  // 上海海港球员
  'Zhang Linpeng': '张琳芃',
  'Zhang Wei': '张卫',
  'Luo Jing': '骆竞',
  'Wang Shenchao': '王燊超',
  'Oscar': '奥斯卡',
  'Balgas': '巴尔加斯',
  'Chen Binbin': '陈彬彬',
  'Yan Junling': '颜骏凌',
  'Li Shenglong': '李圣龙',
  'Jiang Guangtai': '蒋光太',
  'Yu Hai': '于海',
  'Lü Wenjun': '吕文君',
  'Sun Minghao': '孙铭浩',
  'Li Ang': '李昂',
  'Zhang Jiaqi': '张佳祺',
  'Guo Xueying': '郭学婴',
  'Yu Shaowen': '于绍文',
  'Liu Ruofan': '刘若钒',
  'Yang Shiyuan': '杨世元',
  'Wu Lei': '武磊',
  'Feng Jin': '冯劲',
  'Xu Xin': '徐新',
  'Chen Pu': '陈蒲',
  
  // 浙江队球员
  'Yue Xin': '岳鑫',
  'Wang Dongsheng': '王东升',
  'Li Tixiang': '李提香',
  'Gu Bin': '顾斌',
  'Zhang Jiaqi': '张佳祺',
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
  'Li Shuai': '李帅',
  'Hu Jingyang': '胡靖扬',
  'Zhang Yonghao': '张永浩',
  'Cai Haojing': '蔡浩京',
  'Shi Weiyuan': '史维元',
  'Chen Qi': '陈琪',
  'Liu Le': '刘乐',
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
  'Sun Ke': '孙可',
  'Zhao Chen': '赵辰',
  'Zhang Yuqing': '张玉清',
  'Wu Xi': '吴曦',
  'Li Xiaoming': '李晓明',
  'Liu Jialiang': '刘嘉良',
  'Jiang Shenglong': '蒋圣龙',
  'Zhu Chenjie': '朱辰杰',
  'Chen Binbin': '陈彬彬',
  'Wang Haijian': '王海港',
  'Jiang Shuyun': '蒋书云',
  'Chen Yuhao': '陈宇浩',
  'Wang Shun': '王顺',
  'Jiang Yifan': '蒋一帆',
  'Liu Ruofan': '刘若钒',
  'Zhang Yuning': '张玉宁',
  'Zhang Yufeng': '张玉峰',
  'Wang Yunlong': '王云龙',
  'Wu Lei': '武磊',
  'Zhang Li': '张磊',
  'Liu Yang': '刘洋',
  'Gao Tianyi': '高天意',
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
  'Zhang Xin': '张鑫',
  'Liu Le': '刘乐',
  'Zhang Yong': '张勇',
  'Li Zhichao': '李智超',
  'Zhang Li': '张磊',
  'Liu Yang': '刘洋',
  'Zhang Chenglin': '张呈栋',
  'Wang Gang': '王刚',
  'Zhang Jiaqi': '张佳祺',
  'Zhao Honglue': '赵宏略',
  'Zhang Chenglin': '张呈栋',
  'Wang Gang': '王刚',
  'Zhang Jiaqi': '张佳祺',
  'Zhao Honglue': '赵宏略',
  'Zhang Chenglin': '张呈栋',
  'Wang Gang': '王刚',
  'Zhang Jiaqi': '张佳祺',
  'Zhao Honglue': '赵宏略'
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
  'Changchun Yatai': '长春亚泰',
  'Qingdao West Coast': '青岛西海岸',
  'Chengdu Rongcheng': '成都蓉城',
  'Cangzhou Mighty Lions': '沧州雄狮',
  'Tianjin Jinmen Tiger': '天津津门虎',
  'Shanghai SIPG': '上海海港',
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

// 事件类型中文名称
const typeNames = {
  'goal': '进球',
  'yellow_card': '黄牌',
  'red_card': '红牌',
  'substitution': '换人'
};

const dataDir = path.join(__dirname, '..', 'public', 'data', 'history', '2024');
const files = fs.readdirSync(dataDir).filter(f => f.endsWith('.json'));

let totalFiles = 0;
let totalTranslations = 0;
let totalTeamUpdates = 0;

files.forEach(file => {
  const filePath = path.join(dataDir, file);
  const content = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(content);
  
  let fileModified = false;
  let translationCount = 0;
  let teamUpdateCount = 0;
  
  // 更新球队信息
  if (data.teams) {
    ['home', 'away'].forEach(teamType => {
      if (data.teams[teamType]) {
        const team = data.teams[teamType];
        
        // 更新球队名称
        if (team.name && teamTranslations[team.name]) {
          team.name = teamTranslations[team.name];
          fileModified = true;
          teamUpdateCount++;
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
        
        // 翻译首发球员
        if (team.lineup) {
          team.lineup.forEach(player => {
            if (player.name && playerTranslations[player.name]) {
              player.name = playerTranslations[player.name];
              fileModified = true;
              translationCount++;
            }
          });
        }
        
        // 翻译替补球员
        if (team.substitutes) {
          team.substitutes.forEach(player => {
            if (player.name && playerTranslations[player.name]) {
              player.name = playerTranslations[player.name];
              fileModified = true;
              translationCount++;
            }
          });
        }
        
        // 翻译换人信息
        if (team.substitutions) {
          team.substitutions.forEach(sub => {
            if (sub.player_out && playerTranslations[sub.player_out]) {
              sub.player_out = playerTranslations[sub.player_out];
              fileModified = true;
              translationCount++;
            }
            if (sub.player_in && playerTranslations[sub.player_in]) {
              sub.player_in = playerTranslations[sub.player_in];
              fileModified = true;
              translationCount++;
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
      
      // 翻译球员名字
      if (event.player && playerTranslations[event.player]) {
        event.player = playerTranslations[event.player];
        fileModified = true;
        translationCount++;
      }
      
      if (event.player2 && playerTranslations[event.player2]) {
        event.player2 = playerTranslations[event.player2];
        fileModified = true;
        translationCount++;
      }
      
      if (event.player_out && playerTranslations[event.player_out]) {
        event.player_out = playerTranslations[event.player_out];
        fileModified = true;
        translationCount++;
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
    console.log(`✓ ${file}: 翻译了 ${translationCount} 处球员名字，更新了 ${teamUpdateCount} 处球队信息`);
    totalFiles++;
    totalTranslations += translationCount;
    totalTeamUpdates += teamUpdateCount;
  } else {
    console.log(`- ${file}: 无需更新`);
  }
});

console.log(`\n总计: 处理了 ${totalFiles} 个文件，翻译了 ${totalTranslations} 处球员名字，更新了 ${totalTeamUpdates} 处球队信息`);

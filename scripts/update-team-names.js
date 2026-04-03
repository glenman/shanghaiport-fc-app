const fs = require('fs');
const path = require('path');

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
  
  // 更新球队名称
  if (data.teams) {
    ['home', 'away'].forEach(teamType => {
      if (data.teams[teamType]) {
        const team = data.teams[teamType];
        
        // 更新球队名称
        if (team.name && teamTranslations[team.name]) {
          team.name = teamTranslations[team.name];
          fileModified = true;
          translationCount++;
        }
        
        // 更新球队全名
        if (team.full_name && teamTranslations[team.full_name]) {
          team.full_name = teamTranslations[team.full_name];
          fileModified = true;
          translationCount++;
        }
      }
    });
  }
  
  if (fileModified) {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf-8');
    console.log(`✓ ${file}: 更新了 ${translationCount} 处球队名称`);
    totalFiles++;
    totalTranslations += translationCount;
  } else {
    console.log(`- ${file}: 无需更新球队名称`);
  }
});

console.log(`\n总计: 处理了 ${totalFiles} 个文件，更新了 ${totalTranslations} 处球队名称`);

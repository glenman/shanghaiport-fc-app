const fs = require('fs');
const path = require('path');

// 位置缩写映射
const positionMap = {
  'GK': '门将',
  'CB': '中后卫',
  'LB': '左后卫',
  'RB': '右后卫',
  'CM': '中前卫',
  'RW': '右前卫',
  'LW': '左前卫',
  'CF': '前锋',
  'AM': '前腰',
  'DM': '后腰',
  'DF': '后卫'
};

// 读取CSV文件
const csvPath = path.join(__dirname, '../datafile/上海海港2025一线队大名单.csv');
const csvContent = fs.readFileSync(csvPath, 'utf8');

// 解析CSV
const lines = csvContent.trim().split('\n');
const headers = lines[0].split(',').map(h =>h.trim());

const players = [];

for (let i = 1; i< lines.length; i++) {
  const values = lines[i].split(',');
  const player = {};
  
  headers.forEach((header, index) =>{
    let value = values[index] || '';
    value = value.trim();
    // 过滤掉空字段和换行符字段
    if (header && value && header !== '\r') {
      player[header] = value;
    }
  });
  
  // 添加中文位置
  if (player.位置) {
    player.中文位置 = positionMap[player.位置] || player.位置;
  }
  
  players.push(player);
}

// 创建按号码索引的对象
const playersByNumber = {};
players.forEach(player => {
  playersByNumber[player.号码] = player;
});

// 创建输出对象
const output = {
  players: players,
  playersByNumber: playersByNumber
};

// 写入JSON文件
const outputPath = path.join(__dirname, '../public/data/history/2025/players.json');
fs.writeFileSync(outputPath, JSON.stringify(output, null, 2), 'utf8');

console.log('球员数据JSON文件已生成:', outputPath);

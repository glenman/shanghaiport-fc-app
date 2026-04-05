const fs = require('fs');
const path = require('path');

const seasons = ['2023', '2024'];
const teams = new Set();

seasons.forEach(season => {
  const directory = path.join('public', 'data', 'history', season);
  const fullPath = path.join(__dirname, '..', directory);
  
  if (!fs.existsSync(fullPath)) {
    console.error(`目录不存在：${fullPath}`);
    return;
  }
  
  console.log(`开始提取${season}赛季球队信息...`);
  
  const files = fs.readdirSync(fullPath);
  
  files.forEach(file => {
    if (file.endsWith('.json') && file !== 'players.json') {
      const filePath = path.join(fullPath, file);
      
      try {
        const content = fs.readFileSync(filePath, 'utf8');
        const data = JSON.parse(content);
        
        if (data.teams && data.teams.home && data.teams.home.name) {
          teams.add(data.teams.home.name);
        }
        
        if (data.teams && data.teams.away && data.teams.away.name) {
          teams.add(data.teams.away.name);
        }
        
      } catch (error) {
        console.error(`处理文件时出错: ${file}`, error.message);
      }
    }
  });
});

console.log('\n提取完成！');
console.log(`共发现 ${teams.size} 支球队:`);
console.log([...teams].sort().join('\n'));

// 保存结果到文件
const resultPath = path.join(__dirname, '..', 'team-list.txt');
fs.writeFileSync(resultPath, [...teams].sort().join('\n'));
console.log(`\n结果已保存到: ${resultPath}`);
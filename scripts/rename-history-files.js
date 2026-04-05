const fs = require('fs');
const path = require('path');

// 获取命令行参数
const season = process.argv[2];

if (!season || !['2023', '2024', '2025'].includes(season)) {
  console.error('请指定赛季参数：2023、2024或2025');
  console.error('用法：node scripts/rename-history-files.js 2023');
  process.exit(1);
}

const directory = path.join('public', 'data', 'history', season);
const fullPath = path.join(__dirname, '..', directory);

// 检查目录是否存在
if (!fs.existsSync(fullPath)) {
  console.error(`目录不存在：${fullPath}`);
  process.exit(1);
}

console.log(`开始处理 ${season} 赛季JSON文件...`);

fs.readdir(fullPath, (err, files) => {
  if (err) {
    console.error('读取目录失败:', err);
    return;
  }

  let renamedCount = 0;
  let skippedCount = 0;
  let errorCount = 0;

  files.forEach(file => {
    if (file.endsWith('.json') && file !== 'players.json') {
      const filePath = path.join(fullPath, file);
      
      try {
        const content = fs.readFileSync(filePath, 'utf8');
        const data = JSON.parse(content);
        
        const date = data.match_info.date;
        const round = data.match_info.competition.round;
        
        // 构建新文件名
        const newFileName = `${date}-中超-${round}.json`;
        const newFilePath = path.join(fullPath, newFileName);
        
        if (file !== newFileName) {
          fs.renameSync(filePath, newFilePath);
          console.log(`重命名: ${file} -> ${newFileName}`);
          renamedCount++;
        } else {
          skippedCount++;
        }
        
      } catch (error) {
        console.error(`处理文件时出错: ${file}`, error.message);
        errorCount++;
      }
    }
  });

  console.log(`\n处理完成！`);
  console.log(`重命名: ${renamedCount}`);
  console.log(`跳过: ${skippedCount}`);
  console.log(`错误: ${errorCount}`);
});
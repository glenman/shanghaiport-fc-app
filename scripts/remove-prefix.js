const fs = require('fs');
const path = require('path');

const directory = path.join('public', 'data', 'history', '2023');
const fullPath = path.join(__dirname, '..', directory);

console.log('开始处理2023赛季文件名，去掉"2023-"前缀...');

fs.readdir(fullPath, (err, files) => {
  if (err) {
    console.error('读取目录失败:', err);
    return;
  }

  let renamedCount = 0;
  let skippedCount = 0;

  files.forEach(file => {
    if (file.includes('2023-') && file.endsWith('.json')) {
      const oldFilePath = path.join(fullPath, file);
      const newFileName = file.replace(/2023-/g, '');
      const newFilePath = path.join(fullPath, newFileName);
      
      fs.renameSync(oldFilePath, newFilePath);
      console.log(`重命名: ${file} -> ${newFileName}`);
      renamedCount++;
    } else {
      skippedCount++;
    }
  });

  console.log(`\n处理完成！`);
  console.log(`重命名: ${renamedCount}`);
  console.log(`跳过: ${skippedCount}`);
});
const fs = require('fs');
const path = require('path');

const directory = 'd:\\Workspace\\shanghaiport-fc-app\\public\\data\\history\\2024';

fs.readdir(directory, (err, files) => {
  if (err) {
    console.error('读取目录失败:', err);
    return;
  }

  let renamedCount = 0;
  let skippedCount = 0;

  files.forEach(file => {
    if (file.endsWith('.json')) {
      const filePath = path.join(directory, file);
      
      try {
        const content = fs.readFileSync(filePath, 'utf8');
        const data = JSON.parse(content);
        
        const date = data.match_info.date;
        const round = data.match_info.competition.round;
        const year = date.substring(0, 4);
        
        // 构建新文件名
        const newFileName = `${date}-中超-${round}.json`;
        const newFilePath = path.join(directory, newFileName);
        
        if (file !== newFileName) {
          fs.renameSync(filePath, newFilePath);
          console.log(`重命名: ${file} -> ${newFileName}`);
          renamedCount++;
        } else {
          skippedCount++;
        }
        
      } catch (error) {
        console.error(`处理文件时出错: ${file}`, error);
      }
    }
  });

  console.log(`处理完成！重命名: ${renamedCount}, 跳过: ${skippedCount}`);
});
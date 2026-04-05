const fs = require('fs');
const path = require('path');

const directory = 'd:\\Workspace\\shanghaiport-fc-app\\public\\data\\history\\2023';

fs.readdir(directory, (err, files) => {
  if (err) {
    console.error('读取目录失败:', err);
    return;
  }

  files.forEach(file => {
    if (file.startsWith('2023-') && file.endsWith('.json')) {
      const oldPath = path.join(directory, file);
      const newPath = path.join(directory, file.substring(5)); // 去掉前5个字符 "2023-"
      
      fs.rename(oldPath, newPath, (err) => {
        if (err) {
          console.error(`重命名失败 ${file}:`, err);
        } else {
          console.log(`已重命名: ${file} -> ${file.substring(5)}`);
        }
      });
    }
  });
});
const fs = require('fs');
const path = require('path');

const dataDir = path.join(__dirname, '..', 'public', 'data', 'history', '2024');
const files = fs.readdirSync(dataDir).filter(f => f.endsWith('.json'));

let totalProcessed = 0;
let totalEvents = 0;

const typeNames = {
  'yellow_card': '黄牌',
  'red_card': '红牌'
};

files.forEach(file => {
  const filePath = path.join(dataDir, file);
  const content = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(content);
  
  let fileModified = false;
  let eventCount = 0;
  
  if (data.events && Array.isArray(data.events)) {
    data.events.forEach(event => {
      const type = event.type;
      const player = event.player || '';
      const player2 = event.player2;
      
      let newDescription;
      
      if (type === 'goal') {
        if (player2 && player2 !== '') {
          newDescription = `${player}进球，助攻球员：${player2}`;
        } else {
          newDescription = `${player}进球`;
        }
      } else if (type === 'yellow_card' || type === 'red_card') {
        newDescription = `${player}获得${typeNames[type]}`;
      } else if (type === 'substitution') {
        const playerOut = event.player_out || '';
        if (playerOut && player) {
          newDescription = `${playerOut}被换下，${player}替补登场`;
        }
      }
      
      if (newDescription && event.description !== newDescription) {
        event.description = newDescription;
        fileModified = true;
        eventCount++;
      }
    });
  }
  
  if (fileModified) {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf-8');
    console.log(`✓ ${file}: 更新了 ${eventCount} 个事件`);
    totalEvents += eventCount;
    totalProcessed++;
  } else {
    console.log(`- ${file}: 无需修改`);
  }
});

console.log(`\n总计: 处理了 ${totalProcessed} 个文件，更新了 ${totalEvents} 个事件`);

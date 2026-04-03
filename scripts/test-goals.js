const fs = require('fs');
const path = require('path');

// 球员名字翻译映射表
const playerNameMap = {
  '马修斯·尤萨': '尤萨',
  '加布里埃尔·艾尔顿·德索萨': '加布里埃尔',
  '阿不都海米提·阿卜杜格尼': '阿不都海米提',
  '王建南': '王嘉楠'
};

// 读取CSV文件
const csvPath = path.join(__dirname, '../datafile/上海海港2025中超联赛对阵结果.csv');
const csvContent = fs.readFileSync(csvPath, 'utf8');

// 解析CSV数据
const csvLines = csvContent.trim().split('\n');
const csvHeaders = csvLines[0].split(',').map(header => header.replace(/\r/g, '').trim());

const csvMatches = [];
for (let i = 1; i< csvLines.length; i++) {
  const values = csvLines[i].split(',');
  const match = {};
  csvHeaders.forEach((header, index) =>{
    let value = values[index] || '';
    match[header] = value.trim();
  });
  csvMatches.push(match);
}

// 读取所有2025赛季的JSON文件
const historyDir = path.join(__dirname, '../public/data/history/2025');
const jsonFiles = fs.readdirSync(historyDir).filter(file =>file.endsWith('.json') && file !== 'players.json');

const testResults = [];

// 处理每个JSON文件
jsonFiles.forEach(file => {
  const filePath = path.join(historyDir, file);
  const jsonContent = fs.readFileSync(filePath, 'utf8');
  const matchData = JSON.parse(jsonContent);
  
  const matchDate = matchData.match_info.date;
  // 从中文轮次格式中提取数字
  const roundMatch = matchData.match_info.competition.round.match(/第(\d+)轮/);
  const round = roundMatch ? roundMatch[1] : '';
  
  // 找到对应的CSV数据
  let csvMatch = null;
  
  // 首先尝试按日期和轮次精确匹配
  csvMatch = csvMatches.find(m => {
    const csvDate = m['比赛时间'].replace(/\./g, '-');
    const csvRound = m['轮次'].replace('(补赛)', '');
    const isDateMatch = csvDate === matchDate;
    const isRoundMatch = csvRound === round;
    return isDateMatch && isRoundMatch;
  });
  
  // 如果精确匹配失败，尝试只按日期匹配
  if (!csvMatch) {
    csvMatch = csvMatches.find(m => {
      const csvDate = m['比赛时间'].replace(/\./g, '-');
      return csvDate === matchDate;
    });
  }
  
  if (!csvMatch) {
    testResults.push({
      file: file,
      status: 'ERROR',
      message: `未找到对应的CSV数据: ${matchDate}, 第${round}轮`
    });
    return;
  }
  
  // 获取JSON文件中的进球数据
  const goalEvents = matchData.events.filter(event => 
    event.type === 'goal' || event.type === 'own_goal'
  );
  
  // 提取上海海港的进球
  const shanghaiPortGoals = goalEvents.filter(event => {
    const teamName = event.team === 'home' ? matchData.teams.home.name : matchData.teams.away.name;
    return teamName === '上海海港';
  });
  
  const shanghaiPortGoalScorers = shanghaiPortGoals.map(event => {
    let scorer = event.player;
    // 应用翻译映射
    scorer = playerNameMap[scorer] || scorer;
    if (event.goal_type === 'penalty_goal') {
      scorer += '(PK)';
    } else if (event.goal_type === 'own_goal') {
      scorer += '(OG)';
    }
    return scorer;
  }).sort();
  
  // 提取CSV中的上海海港进球
  let csvGoals = '';
  
  // 获取CSV中的上海海港进球
  
  if (csvMatch && csvMatch['进球队员']) {
    if (csvMatch['主队'] === '上海海港') {
      csvGoals = csvMatch['进球队员'].split('/')[0] || '';
    } else {
      csvGoals = csvMatch['进球队员'].split('/')[1] || '';
    }
  }
  
  const csvGoalScorers = csvGoals ? csvGoals.split('，').map(g => g.trim()).filter(g => g).sort() : [];
  
  // 对比结果
  const isMatch = JSON.stringify(shanghaiPortGoalScorers) === JSON.stringify(csvGoalScorers);
  
  testResults.push({
    file: file,
    date: matchDate,
    round: round,
    homeTeam: matchData.teams.home.name,
    awayTeam: matchData.teams.away.name,
    status: isMatch ? 'PASS' : 'FAIL',
    jsonGoals: shanghaiPortGoalScorers.join('，'),
    csvGoals: csvGoalScorers.join('，')
  });
});

// 生成测试报告
console.log('=== 2025赛季赛事报告进球记录测试 ===');
console.log('');

let passCount = 0;
let failCount = 0;
let errorCount = 0;

testResults.forEach(result => {
  if (result.status === 'PASS') {
    passCount++;
    console.log(`✅ ${result.file} - ${result.date} - ${result.homeTeam} vs ${result.awayTeam} - 通过`);
  } else if (result.status === 'FAIL') {
    failCount++;
    console.log(`❌ ${result.file} - ${result.date} - ${result.homeTeam} vs ${result.awayTeam} - 失败`);
    console.log(`   JSON进球: ${result.jsonGoals}`);
    console.log(`   CSV进球: ${result.csvGoals}`);
  } else {
    errorCount++;
    console.log(`⚠️  ${result.file} - ${result.message}`);
  }
});

console.log('');
console.log('=== 测试统计 ===');
console.log(`总测试数: ${testResults.length}`);
console.log(`通过: ${passCount}`);
console.log(`失败: ${failCount}`);
console.log(`错误: ${errorCount}`);
console.log(`成功率: ${((passCount / testResults.length) * 100).toFixed(1)}%`);

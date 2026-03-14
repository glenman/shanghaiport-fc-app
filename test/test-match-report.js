// 模拟 match-report.html 的数据加载逻辑
const urlParams = new URLSearchParams('?date=2026-03-07&type=中超&round=第1轮');
const params = {};
for (const [key, value] of urlParams.entries()) {
  params[key] = value;
}

const { date, type, round, source } = params;
console.log('URL参数:', params);

if (!date || !type || !round) {
  console.log('缺少比赛信息参数');
} else {
  // 构建JSON文件路径
  let filePath;
  // 处理type参数，将"中超联赛"转换为"中超"
  const processedType = type.replace('联赛', '');
  if (source === 'h') {
    // 历史比赛，从history目录读取
    const year = date.substring(0, 4);
    const fileName = `${date}-${processedType}-${round}.json`;
    filePath = `data/history/${year}/${fileName}`;
  } else {
    // 当前赛季，从data目录读取
    const fileName = `${date}-${processedType}-${round}.json`;
    filePath = `data/${fileName}`;
  }

  console.log('文件路径:', filePath);

  // 模拟 fetch 请求
  const fs = require('fs');
  const path = require('path');
  const fullPath = path.join(__dirname, 'public', filePath);
  console.log('完整路径:', fullPath);

  try {
    const data = fs.readFileSync(fullPath, 'utf8');
    const jsonData = JSON.parse(data);
    console.log('成功加载数据:', jsonData.match.homeTeam, 'vs', jsonData.match.awayTeam);
    console.log('比赛结果:', jsonData.match.result);
  } catch (error) {
    console.error('加载数据失败:', error.message);
  }
}

// 热点数据更新脚本 - 猪小媒
// 用于合并各平台热点并生成TOP100

const fs = require('fs');
const path = require('path');

// ========== 知乎热榜数据 (50条) ==========
const zhihuData = [
  { title: "如何评价钉钉内网 7.5 万字长文《置身钉内》？反映出公司管理和开发哪些问题？", platform: "知乎", heat: 5370000, heatText: "537万热度" },
  { title: "日股跳水韩股熔断， SK 海力士跌超 8%，暴跌原因是什么？释放了哪些市场信号？", platform: "知乎", heat: 2360000, heatText: "236万热度" },
  { title: "饶毅称：「中国学术不端比例世界空前，但很少对学术不端有惩罚」，如何看待他的这一说法？", platform: "知乎", heat: 1430000, heatText: "143万热度" },
  { title: "广东化州多校有空调却不开，校方称去年被举报收费，今年决定不开也不收钱，学校开空调为啥这么难？", platform: "知乎", heat: 1350000, heatText: "135万热度" },
  { title: "一直有物种灭绝，怎么没见过有新的物种产生？", platform: "知乎", heat: 1230000, heatText: "123万热度" },
  { title: "怎么看待外媒报道美国公务员被强制安装白宫 App，可一键夸特朗普?", platform: "知乎", heat: 1200000, heatText: "120万热度" },
  { title: "如何看待大胃袋良子加入华哥百日彭于晏训练营，你觉得他能回到正常体重，减肥成功吗？", platform: "知乎", heat: 1170000, heatText: "117万热度" },
  { title: "美国如何一次性解决 36 万亿美债问题？", platform: "知乎", heat: 1130000, heatText: "113万热度" },
  { title: "TP-LINK 被曝强制全员转签，新合同暗含霸王条款，超 140 人离职，企业这种做法合法吗？", platform: "知乎", heat: 1070000, heatText: "107万热度" },
  { title: "腾讯姚顺雨称 AI 实用价值高于「刷榜」价值，如何看待这一观点？国产大模型该告别榜单内卷吗？", platform: "知乎", heat: 1060000, heatText: "106万热度" },
  { title: "印度人想把喜马拉雅山炸个口子，以解决高温问题，这个思路可行性如何？为什么换成印度人想炸喜马拉雅山了？", platform: "知乎", heat: 1030000, heatText: "103万热度" },
  { title: "如果柯南不能完结是因为太赚钱了，那为什么不能先放出主线结局然后再无限连载日常篇？", platform: "知乎", heat: 840000, heatText: "84万热度" },
  { title: "为何公司财务能接触这么多秘密，却地位这么低？", platform: "知乎", heat: 800000, heatText: "80万热度" },
  { title: "网友称遇王祖蓝被清场，官方否认，真实情况究竟如何？", platform: "知乎", heat: 770000, heatText: "77万热度" },
  { title: "《人民的名义》里赵立春怎样做才能「反杀」沙瑞金？", platform: "知乎", heat: 760000, heatText: "76万热度" },
  { title: "德国罕见落选联合国非常任理事国，原因何在？", platform: "知乎", heat: 750000, heatText: "75万热度" },
  { title: "《歌手 2026》第三期胡彦斌第一，齐豫、张碧晨、斯纳吉、周兴哲进入危险区，如何评价歌手们表现？", platform: "知乎", heat: 730000, heatText: "73万热度" },
  { title: "河南人高考竞争激烈为什么不把户口迁到东三省？", platform: "知乎", heat: 710000, heatText: "71万热度" },
  { title: "美国外卖机器人被当街暴打，该厂商曾称其要替代人工快递员，这一现象反映了哪些问题？", platform: "知乎", heat: 690000, heatText: "69万热度" },
  { title: "37 岁工程师猝死时工作群仍在派活，生前常加班至凌晨，这种「停不下来」的死循环，究竟是谁在按下加速键？", platform: "知乎", heat: 660000, heatText: "66万热度" },
  { title: "电影《特立独行》中白敬亭造型被戏称「国产版祖国人」 ，你觉得如何？算致敬吗？", platform: "知乎", heat: 630000, heatText: "63万热度" },
  { title: "为什么大多数人拿到精装房的第一步就是换地板？", platform: "知乎", heat: 590000, heatText: "59万热度" },
  { title: "耐克原价 899 元几个月后变 429 元，奥特莱斯货架上堆积如山，为什么中国消费者现在都不穿耐克了？", platform: "知乎", heat: 590000, heatText: "59万热度" },
  { title: "谷歌计划两年内释放 3200 万只蚊子，旨在减少蚊子数抑制疾病传播，放蚊为啥能灭蚊？背后是什么原理？", platform: "知乎", heat: 590000, heatText: "59万热度" },
  { title: "瑞幸回应咖啡去冰后仅半杯，称去冰不满杯属于正常操作，这合理吗？算是变相的缺斤短两吗？", platform: "知乎", heat: 590000, heatText: "59万热度" },
  { title: "网传苹果即将发布首款折叠屏手机，确认液态金属铰链方案，新技术有哪些优劣？会给国产折叠屏带来哪些冲击？", platform: "知乎", heat: 580000, heatText: "58万热度" },
  { title: "豆包首次推出订阅选项后，月活跃用户减少近 610 万，怎样看待这一影响？豆包的商业化尝试过早了吗？", platform: "知乎", heat: 580000, heatText: "58万热度" },
  { title: "在拨号上网时代下载一个游戏，是怎样的一种体验？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "《家业》中的徽墨、徽商在历史上影响力有多大？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "生活中人特别迟钝是怎样的体验？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "小时候看的剧中，有哪些人物的美，至今你还记忆犹新，觉得无可替代？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "如何评价中国男篮热身赛输给了塞尔维亚 KK FMP 俱乐部？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "同等体重下猫科动物是否无敌？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "如何看待名古屋亚运会《英雄联盟》项目未能参赛「市场行为应交给市场决定」与「领导英明去了也丢人」的讨论？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "为什么《崩坏：星穹铁道》里阿哈婴儿啼哭的故事会被认为好笑？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "潮汕文学里的海，为什么很少是浪漫的，反而常带着漂泊感和危险感？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "儿子喜欢篮球，走职业有前途吗？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "为什么那么多人很多年后才发现《黑猫警长》动画片只有五集？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "为什么哪怕不做什么事情，在工位上待着也会感觉到疲惫？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "《情深深雨濛濛》中，如萍真的爱杜飞吗？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "应届生第一份工作，选高薪小公司还是低薪大厂？职业起步到底该看重什么？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "挪威附近发现 18 世纪沉船，载有中国瓷器等珍贵文物，对历史研究有哪些价值？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "经常看书的人和不看书的人有什么区别？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "游戏史上有哪些「大家都以为是真的」，后来却被证实是假的经典谣言？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "有什么事是你去了瑞典才知道的？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "为什么最近潮汕文学被重新看见？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "《迪迦奥特曼》的人气为什么这么高？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "你对潮汕文学中的女性角色有什么印象？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "《连城诀》中狄云是否真能接受水笙？", platform: "知乎", heat: 560000, heatText: "56万热度" },
  { title: "为什么年轻人上班都不想化妆了?", platform: "知乎", heat: 560000, heatText: "56万热度" }
];

// ========== 抖音热点数据 (20条) ==========
const douyinData = [
  { title: "饭店的暑假工，八块钱餐位费合理吗？", platform: "抖音", heat: 44550267, heatText: "4455万播放" },
  { title: "中国少年叶梓渝，以0.39秒的惊人速度解出2×2魔方，将世界纪录收入囊中", platform: "抖音", heat: 27761519, heatText: "2776万播放" },
  { title: "“鬼火少年”深夜飙车炫技，还发视频挑衅警方：请你们来逮我", platform: "抖音", heat: 22292808, heatText: "2229万播放" },
  { title: "沉浸式体验明星保镖的一天，今天保护的艺人是赵露思", platform: "抖音", heat: 19765854, heatText: "1976万播放" },
  { title: "《言传身教》", platform: "抖音", heat: 18850252, heatText: "1885万播放" },
  { title: "世界武功 唯快不破 #我和我的狗", platform: "抖音", heat: 18634144, heatText: "1863万播放" },
  { title: "脱手“智驾”40秒，一家三口当场身亡！ 最新调查细节公布", platform: "抖音", heat: 18423302, heatText: "1842万播放" },
  { title: "老是会老的，童心还是未泯😄", platform: "抖音", heat: 17344065, heatText: "1734万播放" },
  { title: "警惕新型诈骗！接到陌生电话千万不要先出声，只需要5秒，Ai就能复制你的声音", platform: "抖音", heat: 17194376, heatText: "1719万播放" },
  { title: "冬瓜 防暑神器～是谁还没拥有？哈哈哈", platform: "抖音", heat: 14796610, heatText: "1480万播放" },
  { title: "贵州全校一起为高考的同学们跳一场舞！加油", platform: "抖音", heat: 13670983, heatText: "1367万播放" },
  { title: "住在50楼，这一次闪电真的把我吓到了……", platform: "抖音", heat: 13070967, heatText: "1307万播放" },
  { title: "看起来我们两个更想过儿童节？", platform: "抖音", heat: 13019309, heatText: "1302万播放" },
  { title: "当实习同学挤爆一袋三合一营养液……", platform: "抖音", heat: 12860162, heatText: "1286万播放" },
  { title: "居然说我黑", platform: "抖音", heat: 12232628, heatText: "1223万播放" },
  { title: "Oi 今天跟老舅针锋相对", platform: "抖音", heat: 12086404, heatText: "1209万播放" },
  { title: "外卖新规自6月1日起正式实施！无堂食商家须在主页位置显著设置“无堂食”标志", platform: "抖音", heat: 11799495, heatText: "1180万播放" },
  { title: "中央巡视工作领导小组办公室原主任黎晓宏被查", platform: "抖音", heat: 11798339, heatText: "1180万播放" },
  { title: "以为有故人之姿，没想到是故人本人啊", platform: "抖音", heat: 10820137, heatText: "1082万播放" },
  { title: "愿望愿望，请重新降临在手上👋", platform: "抖音", heat: 10707173, heatText: "1071万播放" }
];

// ========== 虎嗅热文数据 (15条) ==========
const huxiuData = [
  { title: "微信闷声赚麻了", platform: "虎嗅", heat: 758000, heatText: "75.8万阅读" },
  { title: "第一批赚到科技股钱的人，开始跑路了", platform: "虎嗅", heat: 623000, heatText: "62.3万阅读" },
  { title: "五年减少3900万，儿童节，越来越冷清了", platform: "虎嗅", heat: 533000, heatText: "53.3万阅读" },
  { title: "小红书这步棋，赌大了", platform: "虎嗅", heat: 532000, heatText: "53.2万阅读" },
  { title: "中国的第三次红利是什么？", platform: "虎嗅", heat: 506000, heatText: "50.6万阅读" },
  { title: "令人窒息，十几款旗舰SUV长成了一个样", platform: "虎嗅", heat: 491000, heatText: "49.1万阅读" },
  { title: "我们这代人正在经历的终极大脱钩", platform: "虎嗅", heat: 412000, heatText: "41.2万阅读" },
  { title: "从9.1狂跌到6.6，一代神剧烂尾了", platform: "虎嗅", heat: 396000, heatText: "39.6万阅读" },
  { title: "价格战已死，新能源车集体反水", platform: "虎嗅", heat: 379000, heatText: "37.9万阅读" },
  { title: "智元和宇树的“暗战”愈演愈烈", platform: "虎嗅", heat: 343000, heatText: "34.3万阅读" },
  { title: "出人意料的答案，今天的AI，就是1882年的电", platform: "虎嗅", heat: 339000, heatText: "33.9万阅读" },
  { title: "SpaceX浑身拧巴", platform: "虎嗅", heat: 332000, heatText: "33.2万阅读" },
  { title: "崩老头儿属于常规操作", platform: "虎嗅", heat: 292000, heatText: "29.2万阅读" },
  { title: "宗馥莉新动作，停摆一年又推新品，比烂尾更可怕的是，宏胜集团把自己印上了瓶身", platform: "虎嗅", heat: 282000, heatText: "28.2万阅读" },
  { title: "天涯六一归来，但互联网早已没了天真", platform: "虎嗅", heat: 236000, heatText: "23.6万阅读" }
];

// ========== 合并所有数据 ==========
const allData = [...zhihuData, ...douyinData, ...huxiuData];

// 按热度排序
allData.sort((a, b) => b.heat - a.heat);

// 取TOP100
const top100 = allData.slice(0, 100);

// ========== 生成HTML ==========
function generateHotlistHTML(data) {
  let html = '';
  data.forEach((item, index) => {
    const rank = String(index + 1).padStart(2, '0');
    const rankClass = index < 3 ? 'top3' : index < 10 ? 'top10' : '';
    html += `    <div class="hotlist-merged-item"><span class="hotlist-merged-rank ${rankClass}">${rank}</span><span class="hotlist-merged-title-text">${item.title}</span><span class="hotlist-merged-platform">${item.platform}</span><span class="hotlist-merged-heat">${item.heatText}</span></div>\n`;
  });
  return html;
}

// ========== 更新HTML文件 ==========
const htmlPath = path.join(__dirname, 'index.html');
let htmlContent = fs.readFileSync(htmlPath, 'utf-8');

// 生成新的热点列表HTML
const newHotlist = generateHotlistHTML(top100);

// 替换热点列表部分
const hotlistStart = '<div class="hotlist-merged-grid">';
const hotlistEnd = '    </div>\n</div></div>';

const startIndex = htmlContent.indexOf(hotlistStart);
const endIndex = htmlContent.indexOf(hotlistEnd, startIndex);

if (startIndex !== -1 && endIndex !== -1) {
  const before = htmlContent.substring(0, startIndex + hotlistStart.length);
  const after = htmlContent.substring(endIndex);
  const newContent = before + '\n' + newHotlist + '\n' + after;
  
  // 更新日期
  const today = new Date();
  const dateStr = `${today.getFullYear()}年${today.getMonth() + 1}月${today.getDate()}日`;
  const updatedContent = newContent.replace(/2026年6月\d+日/g, dateStr);
  
  // 写入文件
  fs.writeFileSync(htmlPath, updatedContent, 'utf-8');
  console.log('✅ 热点数据更新成功！');
  console.log(`📊 共更新 ${top100.length} 条热点`);
  console.log(`📅 更新日期：${dateStr}`);
  console.log(`📱 数据来源：知乎(${zhihuData.length}) + 抖音(${douyinData.length}) + 虎嗅(${huxiuData.length})`);
} else {
  console.log('❌ 未找到热点列表位置');
  process.exit(1);
}

// 解析已抓取的热点数据
const zhihuData = [
  { rank: 1, title: "如何评价钉钉内网 7.5 万字长文《置身钉内》？反映出公司管理和开发哪些问题？", platform: "知乎", heat: 5370000 },
  { rank: 2, title: "日股跳水韩股熔断， SK 海力士跌超 8%，暴跌原因是什么？释放了哪些市场信号？", platform: "知乎", heat: 2360000 },
  { rank: 3, title: "饶毅称：「中国学术不端比例世界空前，但很少对学术不端有惩罚」，如何看待他的这一说法？", platform: "知乎", heat: 1430000 },
  { rank: 4, title: "广东化州多校有空调却不开，校方称去年被举报收费，今年决定不开也不收钱，学校开空调为啥这么难？", platform: "知乎", heat: 1350000 },
  { rank: 5, title: "一直有物种灭绝，怎么没见过有新的物种产生？", platform: "知乎", heat: 1230000 }
];

const douyinData = [
  { rank: 1, title: "饭店的暑假工，八块钱餐位费合理吗？", platform: "抖音", heat: 44550267 },
  { rank: 2, title: "中国少年叶梓渝，以0.39秒的惊人速度解出2×2魔方，将世界纪录收入囊中", platform: "抖音", heat: 27761519 },
  { rank: 3, title: "“鬼火少年”深夜飙车炫技，还发视频挑衅警方：请你们来逮我", platform: "抖音", heat: 22292808 }
];

const huxiuData = [
  { rank: 1, title: "微信闷声赚麻了", platform: "虎嗅", heat: 758000 },
  { rank: 2, title: "第一批赚到科技股钱的人，开始跑路了", platform: "虎嗅", heat: 623000 },
  { rank: 3, title: "五年减少3900万，儿童节，越来越冷清了", platform: "虎嗅", heat: 533000 }
];

// 合并所有数据
const allData = [...zhihuData, ...douyinData, ...huxiuData];

// 按热度排序
allData.sort((a, b) => b.heat - a.heat);

// 取TOP100
const top100 = allData.slice(0, 100);

console.log(JSON.stringify(top100, null, 2));

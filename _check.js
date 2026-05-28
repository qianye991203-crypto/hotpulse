
// ── State ──
var activeFilter = 'all';
var currentResults = null;

// ── Init ──
document.getElementById('ts').textContent = new Date().toLocaleString('zh-CN', {
  year: 'numeric', month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit'
});
loadHistoryFromStorage();

// ── Tab switching ──
function switchTab(tabName, btn) {
  var panels = document.querySelectorAll('.panel');
  for (var i = 0; i < panels.length; i++) panels[i].classList.remove('active');
  var tabs = document.querySelectorAll('.tab-btn');
  for (var j = 0; j < tabs.length; j++) tabs[j].classList.remove('active');
  document.getElementById('panel-' + tabName).classList.add('active');
  btn.classList.add('active');
  if (tabName === 'history') renderHistory();
  if (tabName === 'hot' && !_hlInited){_hlInited=true;initHotlist();}
}

function clearInput() {
  document.getElementById('rawInput').value = '';
  document.getElementById('resultsArea').innerHTML =
    '<div class="empty-state"><div class="empty-icon">🐷</div>' +
    '<div class="empty-text">粘贴热点内容，点击「开始分析」<br>自动完成 <strong>去重 · 分类 · 评分 · 角度建议</strong></div></div>';
}

// ── Category keywords ──
var CATEGORY_KEYWORDS = {
  '社会': ['事故','爆炸','火灾','地震','疫情','死亡','遇难','伤亡','失踪','案件','犯罪','抓捕','判刑','离婚','出轨','家暴','霸凌','校园','教育','高考','中考','就业','失业','房价','社保','医保','养老','退休','工资','涨薪','罢工','抗议','政策','法规','法律','出台','禁令','救灾','捐款','慈善','贫困','扶贫','低保','拆迁','征地','维权','上访','举报','曝光','揭露','丑闻','绯闻','造假','掺假','毒','污染','环境','气候','天气','台风','暴雨','洪涝','干旱','煤矿','矿难','消防','交通','空难'],
  '科技': ['AI','人工智能','GPT','ChatGPT','Claude','大模型','芯片','半导体','英伟达','NVIDIA','苹果','Apple','iPhone','华为','小米','OPPO','vivo','特斯拉','Tesla','SpaceX','马斯克','元宇宙','区块链','比特币','BTC','加密货币','Web3','5G','6G','量子','算力','云计算','开源','APP','算法','自动驾驶','新能源','电池','光伏','卫星','火箭','发射','脑机接口','VR','AR','MR','折叠屏','智能手表','显卡','游戏','电竞','OpenAI','DeepSeek','Gemini','Sora','Midjourney'],
  '娱乐': ['电影','电视剧','综艺','选秀','偶像','演唱会','音乐','专辑','歌曲','歌手','演员','导演','票房','档期','上映','获奖','奥斯卡','金鸡奖','真人秀','脱口秀','相声','小品','舞蹈','街舞','浪姐','披荆斩棘','声生不息','奔跑吧','极限挑战','旅行','美食','探店','吃播','vlog','博主','UP主','种草','测评','开箱','穿搭','美妆','护肤','减肥','健身','瑜伽','医美','整形'],
  '国际': ['美国','中国','俄罗斯','乌克兰','日本','韩国','朝鲜','印度','英国','法国','德国','欧盟','北约','联合国','拜登','特朗普','普京','泽连斯基','岸田','尹锡悦','莫迪','马克龙','战争','冲突','制裁','关税','贸易战','峰会','会谈','协议','核武器','导弹','军演','航母','战机','南海','台海','中东','巴以','伊朗','以色列','哈马斯','选举','总统','首相','通胀','加息','降息','衰退','央行','美联储','美股','A股','原油','黄金','比特币'],
  '财经': ['GDP','CPI','PMI','营收','利润','财报','上市','IPO','融资','创投','估值','独角兽','倒闭','破产','裁员','降薪','年终奖','股票','基金','债券','期货','外汇','人民币','利率','房贷','车贷','消费贷','网贷','理财','保险','银行','券商','养老金','税收','退税','补贴','消费','零售','电商','淘宝','天猫','京东','拼多多','直播带货','双11','618','购物节','促销','打折','优惠','涨价','降价','成本','供应链','物流','快递','外卖','美团','饿了么'],
  '生活': ['美食','菜谱','做饭','家常菜','甜品','饮料','咖啡','奶茶','火锅','烧烤','肯德基','麦当劳','星巴克','瑞幸','蜜雪冰城','宠物','猫','狗','养宠','装修','家居','家电','空调','冰箱','洗衣机','电视','扫地机器人','出行','旅游','机票','酒店','民宿','自驾','高铁','飞机','火车','地铁','买车','考驾照','堵车','停车','加油','充电桩','电动车','露营','徒步','登山','钓鱼','摄影','拍照','短视频','直播','网红','穿搭','时尚','球鞋','限量','联名','潮牌','奢侈品'],
  '体育': ['世界杯','欧洲杯','欧冠','英超','西甲','NBA','CBA','F1','奥运会','亚运会','中超','网球','高尔夫','乒乓球','羽毛球','排球','游泳','跳水','田径','马拉松','拳击','UFC','电竞','LOL','DOTA2','王者荣耀','原神','绝地求生','战队','转会','夺冠','破纪录','MVP','金牌','红牌','黄牌','点球','进球','助攻']
};

// ── Score Engine V2 (6 dimensions) ──
function calcScoreV2(title, rank, platformCount) {
  var t = title;

  // 维度1：时效性 (0-20)
  var timeliness = 5;
  if (/突发|刚刚|最新|快讯|紧急/.test(t)) timeliness = 20;
  else if (/今天|今日|昨日|昨天|上午|下午/.test(t)) timeliness = 17;
  else if (/\d{1,2}月\d{1,2}日|\d{4}年/.test(t)) timeliness = 13;
  else if (rank <= 3) timeliness = 15;
  else if (rank <= 10) timeliness = 10;

  // 维度2：讨论延展性 (0-20)
  var discussion = 5;
  if (/如何|怎么|为什么|为何|是否|能不能|应不应该|\?|？/.test(t)) discussion = 20;
  else if (/政策|法规|法律|规定|标准|改革|开放|解封|禁令/.test(t)) discussion = 18;
  else if (/事件|事故|案件|冲突|争议|辩论|对立/.test(t)) discussion = 16;
  else if (/明星|八卦|绯闻|出轨|离婚/.test(t)) discussion = 12;
  else if (rank <= 5) discussion += 5;

  // 维度3：情绪共鸣度 (0-20)
  var emotion = 5;
  if (/房价|教育|医疗|就业|失业|工资|养老|退休|社保|医保|低保|贫困/.test(t)) emotion = 20;
  else if (/死亡|遇难|伤亡|爆炸|火灾|地震|疫情|病毒|食品安全|中毒|车祸/.test(t)) emotion = 19;
  else if (/裁员|降薪|破产|倒闭|失业|房贷|车贷|网贷|欠债/.test(t)) emotion = 17;
  else if (/出轨|家暴|霸凌|校园|食品安全|假货|诈骗/.test(t)) emotion = 16;
  else if (/宠物|猫|狗|育儿|亲子|婚姻|家庭/.test(t)) emotion = 14;
  else if (/娱乐|明星|电影|综艺|游戏|美食/.test(t)) emotion = 10;

  // 维度4：争议性 (0-15)
  var controversy = 3;
  if (/争议|对立|辩论|吵翻|两极分化|翻车|反转|打脸/.test(t)) controversy = 15;
  else if (/支持|反对|赞同|批评|质疑|辟谣|真相/.test(t)) controversy = 11;
  else if (/政策|法规|改革|征税|补贴|福利/.test(t)) controversy = 10;
  else if (/明星|公众人物/.test(t)) controversy = 8;

  // 维度5：实用价值 (0-15)
  var utility = 3;
  if (/攻略|指南|如何|技巧|方法|教程|步骤|推荐|测评|对比|评测/.test(t)) utility = 15;
  else if (/消费|购买|选购|便宜|折扣|促销|优惠|补贴/.test(t)) utility = 12;
  else if (/健康|养生|减肥|健身|医美|体检/.test(t)) utility = 11;
  else if (/科技|产品|发布|上市|新品/.test(t)) utility = 9;
  else if (/娱乐|八卦|绯闻/.test(t)) utility = 4;

  // 维度6：传播潜力 (0-10)
  var spread = 3;
  var len = t.length;
  if (len <= 15) spread = 10;
  else if (len <= 25) spread = 7;
  else if (len <= 40) spread = 4;
  if (/\d/.test(t)) spread += 2;
  if (/！|!|？|\?/.test(t)) spread += 1;
  if (spread > 10) spread = 10;

  // 平台加成
  var platformBonus = Math.min(platformCount * 4, 10);

  // 高热关键词加成
  var hotKeywordBonus = 0;
  var HOT_KEYWORDS = ['突发','首次','突破','重磅','官宣','确认','否认','反转','曝光','揭秘','内幕','崩塌','暴跌','暴涨','涨停','收购','并购','上市','退市','去世','逝世','夺冠','创纪录','打破历史','百亿','千亿','万亿','国家级','世界级','全球第一','亚洲第一','全国第一','独家','首发'];
  for (var ki = 0; ki < HOT_KEYWORDS.length; ki++) {
    if (t.indexOf(HOT_KEYWORDS[ki]) !== -1) { hotKeywordBonus += 3; break; }
  }

  var total = Math.min(99, Math.max(20,
    timeliness + discussion + emotion + controversy + utility + spread + platformBonus + hotKeywordBonus
  ));

  return {
    total: total,
    dims: { timeliness: timeliness, discussion: discussion, emotion: emotion, controversy: controversy, utility: utility, spread: spread },
    platformBonus: platformBonus,
    hotKeywordBonus: hotKeywordBonus
  };
}

// ── Insight generation (content-aware, NO random templates) ──
function generateInsight(title, category, scoreObj) {
  var t = title;
  var dims = scoreObj.dims;
  var insights = [];

  if (dims.emotion >= 17) {
    var kw = '';
    var emoKws = ['房价','教育','医疗','就业','伤亡','食品安全','裁员','降薪','养老'];
    for (var ei = 0; ei < emoKws.length; ei++) {
      if (t.indexOf(emoKws[ei]) !== -1) { kw = emoKws[ei]; break; }
    }
    insights.push('情绪共鸣极强，涉及民生痛点（' + (kw || '民生') + '），受众主动传播意愿高');
  }
  if (dims.controversy >= 11) {
    insights.push('话题具备争议性，正反两方观点对立，评论区互动数据（评论/转发）预期较高');
  }
  if (dims.discussion >= 16) {
    insights.push('讨论延展性好，适合做深度解读/观点类内容，知乎、B站长文/视频有发挥空间');
  }
  if (dims.utility >= 12) {
    insights.push('实用价值高，用户有收藏/转发给朋友的需求，适合做攻略/测评/对比类内容');
  }
  if (dims.timeliness >= 17) {
    insights.push('时效性强，建议24小时内产出内容，抢占热搜流量窗口期');
  }
  if (dims.spread >= 8 && dims.emotion >= 14) {
    insights.push('标题简洁有力，自带传播属性，适合做短视频口播/图文快讯');
  }

  var catMap = {
    '社会': '社会类话题受众面广，但需注意言论尺度，避免传播未经证实的信息',
    '科技': '科技话题受众精准，付费意愿强，适合做深度评测或行业分析',
    '娱乐': '娱乐话题流量大但生命周期短，建议快速跟进，重点做差异化角度',
    '国际': '国际话题需结合国内视角，避免照搬外媒立场，注意舆论导向',
    '财经': '财经话题专业门槛高，建议用通俗语言解读，增强普通用户理解',
    '生活': '生活类话题接地气，适合做实操内容，收藏率通常较高',
    '体育': '体育话题实时性强，赛事期间流量集中，建议提前准备内容'
  };
  if (catMap[category]) insights.push(catMap[category]);

  if (insights.length === 0) {
    insights.push('该话题综合评分' + scoreObj.total + '分，建议结合自身账号定位判断是否符合受众兴趣');
  }
  return insights;
}

// ── Platform advice ──
function generatePlatformAdvice(title, category) {
  var advice = { '微博': [], '知乎': [], '抖音': [], '小红书': [], 'B站': [] };
  var t = title;

  // 微博
  if (category === '社会' || category === '娱乐') {
    advice['微博'].push('发快讯+个人观点，带话题标签，评论区引导讨论');
  } else {
    advice['微博'].push('发科普/解读长图，配热点话题标签');
  }

  // 知乎
  if (/如何|怎么|为什么|是否|\?|？/.test(t)) {
    advice['知乎'].push('直接回答标题中的问题，给出结构化分析和证据');
  } else if (category === '科技' || category === '财经') {
    advice['知乎'].push('写行业分析/趋势预测，配数据和案例，建立专业人设');
  } else {
    advice['知乎'].push('写事件梳理/多方观点汇总，做信息整合者');
  }

  // 抖音
  if (category === '社会') {
    advice['抖音'].push('前3秒抛出冲突/悬念，用情绪驱动完播率，配BGM强化氛围');
  } else if (category === '娱乐') {
    advice['抖音'].push('用反转/反差制造爆点，前5秒必须抓住注意力');
  } else {
    advice['抖音'].push('口播+字幕+关键帧放大，30-60秒为宜，信息密度要高');
  }

  // 小红书
  if (category === '生活') {
    advice['小红书'].push('封面图+清单体内容，强调「亲测」「实测」，增加可信度');
  } else {
    advice['小红书'].push('用「我的看法」个人化视角切入，避免说教感');
  }

  // B站
  if (category === '科技' || category === '财经') {
    advice['B站'].push('做深度解析视频（5-15分钟），配数据图表和案例，适合中长视频');
  } else if (category === '娱乐') {
    advice['B站'].push('做盘点/混剪/吐槽，年轻用户喜欢有梗的内容');
  } else {
    advice['B站'].push('做事件梳理时间线，或深度评论，B站用户偏好有逻辑的内容');
  }

  return advice;
}

// ── Angle generation (content-aware, NO random templates) ──
function generateAngles(title, category, scoreObj) {
  var t = title;
  var dims = scoreObj.dims;
  var angles = [];

  if (category === '社会' || category === '国际' || category === '财经') {
    angles.push('梳理事件时间线：起因→经过→现状→后续可能走向，帮读者快速建立认知框架');
  }
  if (/首次|突破|暴涨|暴跌|反转|打破/.test(t)) {
    angles.push('对比法：前后对比/竞品对比/国内外对比，突出「变化」和「差异」，强化戏剧感');
  }
  if (dims.emotion >= 14) {
    angles.push('普通人视角：这件事对普通人有什么影响？「跟我有什么关系」是用户最关心的问题');
  }
  if (/\d/.test(t) || category === '财经' || category === '科技') {
    angles.push('用数据说话：提取关键数字/比例/时间节点，把抽象信息具象化，增加可信度');
  }
  if (dims.controversy >= 8) {
    angles.push('拆解争议点：列出各方观点和依据，不直接站队，引导评论区讨论');
  }

  var fallbacks = [
    '预测走向：基于现有信息，合理推测事件后续发展，给出你的判断和理由',
    '行业/历史类比：找类似案例做对比，帮助用户理解事件的特殊性和意义',
    '实操建议：如果话题涉及消费/决策，给出具体可操作的建议清单',
    '人物/背景故事：挖掘事件背后的关键人物或历史背景，增加内容厚度'
  ];
  while (angles.length < 5) {
    var cand = fallbacks[angles.length - 1] || fallbacks[Math.floor(Math.random() * fallbacks.length)];
    if (angles.indexOf(cand) === -1) angles.push(cand);
    else break;
  }
  return angles.slice(0, 5);
}

// ── Risk warning ──
function generateRiskWarning(title, category) {
  var risks = [];
  if (/死亡|遇难|伤亡|自杀|凶杀|爆炸|火灾|地震|疫情/.test(title)) {
    risks.push('涉及伤亡灾害，避免传播未经证实的死伤数字，以官方通报为准');
  }
  if (/官员|政府|政策|政治|领导人/.test(title)) {
    risks.push('涉及公共事务，注意措辞中立，不传播未经核实的政策解读');
  }
  if (/明星|艺人|八卦|绯闻/.test(title)) {
    risks.push('娱乐八卦类，避免恶意揣测或传播未经证实的私人信息，注意名誉权风险');
  }
  if (/企业|公司|产品|造假|掺假|暴雷/.test(title)) {
    risks.push('涉及企业舆情，避免下定论，可客观呈现多方信息，等待官方回应');
  }
  if (/谣言|辟谣|真相|揭秘/.test(title)) {
    risks.push('涉及信息真伪，务必核实信息来源，避免成为谣言传播节点');
  }
  if (risks.length === 0) {
    risks.push('无明显合规风险，正常跟进即可，注意信息来源可靠性');
  }
  return risks;
}

// ── Timing advice ──
function generateTimingAdvice(category) {
  var now = new Date();
  var hour = now.getHours();
  var advice = '';

  if (category === '社会' || category === '国际') {
    advice = '📅 社会/国际话题：越快越好，热搜窗口期通常只有6-24小时，建议立即跟进';
  } else if (category === '娱乐') {
    advice = '📅 娱乐话题：工作日晚8-10点发布效果最佳，周末下午也适合，避开重大社会事件同期';
  } else if (category === '科技') {
    advice = '📅 科技话题：工作日晚8-11点，或周末上午10-12点，科技受众活跃时间较规律';
  } else if (category === '财经') {
    advice = '📅 财经话题：工作日上午9-11点、下午2-5点（股市相关），或晚8-10点（科普类）';
  } else if (category === '生活') {
    advice = '📅 生活话题：早7-9点（通勤）、午12-13点（午休）、晚8-11点（休闲）效果较好';
  } else {
    advice = '📅 建议今天内发布，热点话题的黄金跟进窗口通常为热搜出现后6-12小时';
  }

  if (hour >= 6 && hour < 10) {
    advice += '\n\n当前是早高峰时段（6-10点），适合发布轻量/资讯类内容';
  } else if (hour >= 12 && hour < 14) {
    advice += '\n\n当前是午休时段（12-14点），适合发布轻松/娱乐类内容';
  } else if (hour >= 18 && hour < 22) {
    advice += '\n\n当前是晚间黄金时段（18-22点），全品类内容均适合发布';
  }

  return advice;
}

// ── Category / Region detection ──
function detectCategory(title) {
  var bestCat = '社会';
  var bestScore = 0;
  var keys = Object.keys(CATEGORY_KEYWORDS);
  for (var ci = 0; ci < keys.length; ci++) {
    var cat = keys[ci];
    var kws = CATEGORY_KEYWORDS[cat];
    var score = 0;
    for (var ki = 0; ki < kws.length; ki++) {
      if (title.indexOf(kws[ki]) !== -1) score++;
    }
    if (score > bestScore) { bestScore = score; bestCat = cat; }
  }
  return bestCat;
}

function detectRegion(title) {
  var cnIndicators = ['中国','国内','全国','北京','上海','广州','深圳','杭州','成都','武汉','西安','重庆','南京','天津','苏州','长沙','郑州','东莞','青岛','大连','厦门','宁波','无锡','合肥','佛山','福州','济南','哈尔滨','长春','沈阳','太原','石家庄','南昌','昆明','贵阳','南宁','海口','兰州','银川','西宁','呼和浩特','乌鲁木齐','拉萨','台湾','香港','澳门','央视','人民日报','新华社','微博热搜','知乎热榜','百度热搜','B站热门','抖音热点','小红书','豆瓣','虎扑'];
  var intlIndicators = ['US','USA','UK','EU','UN','NATO','WHO','WTO','NASA','FBI','CIA','America','British','European','Russian','Ukrainian','Japanese','Korean','Indian','Middle East','Global','World','Twitter','Reddit','Trending','BBC','CNN','Reuters','Trump','Biden','Putin','Musk','Apple','Google','Microsoft','Meta','Amazon'];
  var cn = 0, intl = 0;
  for (var i = 0; i < cnIndicators.length; i++) { if (title.indexOf(cnIndicators[i]) !== -1) cn++; }
  for (var j = 0; j < intlIndicators.length; j++) { if (title.indexOf(intlIndicators[j]) !== -1) intl++; }
  if (cn > 0 && intl > 0) return 'both';
  if (cn > 0) return 'cn';
  if (intl > 0) return 'intl';
  return 'cn';
}

// ── Parse raw input ──
function parseRawTopics(raw) {
  var topics = [];
  var lines = raw.split('\n');
  for (var li = 0; li < lines.length; li++) {
    var line = lines[li].trim();
    if (line.length === 0) continue;

    // Try to extract title from various formats
    var title = '';
    var match = line.match(/^\d+[\.、\)\]\s]+(.+)$/);
    if (match) title = match[1].trim();
    else if (line.indexOf('】') !== -1) title = line.split('】')[1] || line;
    else title = line;

    // Clean up title
    title = title.replace(/^[\d+\.、\)\]\s]+/, '').trim();
    title = title.replace(/\s*\|\s*\d+(?:万|亿)?.*$/, '').trim();

    if (title.length >= 4 && !/^\d+$/.test(title)) {
      // Detect platforms from the line
      var platforms = [];
      if (/微博|weibo/i.test(line)) platforms.push('微博');
      if (/知乎|zhihu/i.test(line)) platforms.push('知乎');
      if (/百度|baidu/i.test(line)) platforms.push('百度');
      if (/B站|bilibili|哔哩哔哩/i.test(line)) platforms.push('B站');
      if (/抖音|douyin/i.test(line)) platforms.push('抖音');
      if (/小红书|xiaohongshu|RED/i.test(line)) platforms.push('小红书');
      if (/Twitter|X\.com|trend/i.test(line)) platforms.push('Twitter/X');
      if (/reddit|r\//i.test(line)) platforms.push('Reddit');
      if (/youtube|yt/i.test(line)) platforms.push('YouTube');
      if (platforms.length === 0) platforms = ['未知'];

      topics.push({ rawTitle: title, platforms: platforms });
    }
  }

  // 去重
  var merged = [];
  var seen = [];
  for (var ti = 0; ti < topics.length; ti++) {
    var t = topics[ti];
    var isDup = false;
    for (var si = 0; si < seen.length; si++) {
      if (seen[si].indexOf(t.rawTitle.substring(0, 8)) !== -1 || t.rawTitle.indexOf(seen[si].substring(0, 8)) !== -1) { isDup = true; break; }
    }
    if (!isDup) {
      seen.push(t.rawTitle);
      merged.push(t);
    }
  }
  return merged;
}

// ── Main analysis ──
function runAnalysis() {
  var raw = document.getElementById('rawInput').value.trim();
  if (!raw) { alert('请先粘贴热榜内容'); return; }

  var btn = document.getElementById('runBtn');
  btn.disabled = true;
  btn.textContent = '分析中…';

  var area = document.getElementById('resultsArea');
  area.innerHTML = '<div class="loading-box"><div class="spinner"></div><div class="loading-text">正在解析热点数据<br>识别话题 · 去重合并 · 多维度评分<br>约需 2-3 秒…</div></div>';

  setTimeout(function() {
    try {
      var parsedTopics = parseRawTopics(raw);
      if (parsedTopics.length === 0) {
        area.innerHTML = '<div class="empty-state"><div class="empty-icon">⚠️</div><div class="empty-text">未能识别到有效话题<br>请检查粘贴内容格式，或直接输入话题标题</div></div>';
        btn.disabled = false; btn.textContent = '✦ 开始分析'; return;
      }

      var resultTopics = [];
      for (var i = 0; i < parsedTopics.length; i++) {
        var t = parsedTopics[i];
        var category = detectCategory(t.rawTitle);
        var region = detectRegion(t.rawTitle);
        var scoreObj = calcScoreV2(t.rawTitle, i + 1, t.platforms.length);
        var insights = generateInsight(t.rawTitle, category, scoreObj);
        var angles = generateAngles(t.rawTitle, category, scoreObj);
        var platformAdvice = generatePlatformAdvice(t.rawTitle, category);
        var risks = generateRiskWarning(t.rawTitle, category);
        var timing = generateTimingAdvice(category);

        resultTopics.push({
          rank: i + 1,
          title: t.rawTitle,
          score: scoreObj.total,
          scoreObj: scoreObj,
          category: category,
          region: region,
          platforms: t.platforms,
          insights: insights,
          angles: angles,
          platformAdvice: platformAdvice,
          risks: risks,
          timing: timing
        });
      }

      resultTopics.sort(function(a, b) { return b.score - a.score; });
      for (var ri = 0; ri < resultTopics.length; ri++) { resultTopics[ri].rank = ri + 1; }

      var result = {
        summary: '共识别 ' + resultTopics.length + ' 条热点，' + countHighScore(resultTopics) + '条高分选题（≥75分）',
        topics: resultTopics
      };

      currentResults = result;
      renderResults(result);
      saveToStorage(result, raw);

    } catch (e) {
      area.innerHTML = '<div class="empty-state"><div class="empty-icon">⚠️</div><div class="empty-text">分析出错：' + e.message + '<br>请刷新页面后重试</div></div>';
    }

    btn.disabled = false;
    btn.textContent = '✦ 开始分析';
  }, 600);
}

function countHighScore(topics) {
  var count = 0;
  for (var i = 0; i < topics.length; i++) { if (topics[i].score >= 75) count++; }
  return count;
}

// ── Render ──
function scoreColor(s) {
  if (s >= 75) return 'score-high';
  if (s >= 50) return 'score-mid';
  return 'score-low';
}

function scoreDimColor(v, max) {
  var ratio = v / max;
  if (ratio >= 0.7) return 'var(--success)';
  if (ratio >= 0.4) return 'var(--accent)';
  return 'var(--muted)';
}

function regionTag(r) {
  if (r === 'cn') return '<span class="tag tag-pink">🇨🇳 国内</span>';
  if (r === 'intl') return '<span class="tag tag-orange">🌍 国际</span>';
  return '<span class="tag tag-pink">🇨🇳 国内</span><span class="tag tag-orange">🌍 国际</span>';
}

function catTag(c) { return '<span class="tag tag-gray">' + c + '</span>'; }

function renderResults(data, filter) {
  filter = filter || activeFilter;
  var area = document.getElementById('resultsArea');
  var topics = (data.topics || []).filter(function(t) {
    if (filter === 'cn') return t.region === 'cn' || t.region === 'both';
    if (filter === 'intl') return t.region === 'intl' || t.region === 'both';
    if (filter === 'high') return t.score >= 75;
    return true;
  });

  var totalCount = (data.topics || []).length;
  var html = '';
  html += '<div class="results-header"><div class="results-title">共识别 ' + totalCount + ' 条热点' + (filter !== 'all' ? '，当前显示 ' + topics.length + ' 条' : '') + '</div><div class="filter-row"><button class="filter-btn ' + (filter==='all'?'on':'') + '" onclick="setFilter(\'all\')">全部</button><button class="filter-btn ' + (filter==='cn'?'on':'') + '" onclick="setFilter(\'cn\')">国内</button><button class="filter-btn ' + (filter==='intl'?'on':'') + '" onclick="setFilter(\'intl\')">国际</button><button class="filter-btn ' + (filter==='high'?'on':'') + '" onclick="setFilter(\'high\')">高分 ≥75</button></div></div>';

  if (data.summary) {
    html += '<div class="analyze-box" style="padding:16px 20px;font-size:13px;"><strong>📡 今日热点速览：</strong>' + data.summary + '</div>';
  }

  if (topics.length === 0) {
    html += '<div class="empty-state"><div class="empty-icon">🔍</div><div class="empty-text">当前筛选条件下没有匹配的热点</div></div>';
  } else {
    html += '<div class="topic-list">';
    for (var i = 0; i < topics.length; i++) {
      var t = topics[i];
      var sc = scoreColor(t.score);
      var plat = '';
      for (var pi = 0; pi < t.platforms.length; pi++) { plat += '<span class="tag tag-gray">' + t.platforms[pi] + '</span>'; }

      // 维度明细
      var dims = t.scoreObj.dims;
      var dimItems = [
        { label: '时效性', v: dims.timeliness, max: 20 },
        { label: '讨论度', v: dims.discussion, max: 20 },
        { label: '情绪共鸣', v: dims.emotion, max: 20 },
        { label: '争议性', v: dims.controversy, max: 15 },
        { label: '实用价值', v: dims.utility, max: 15 },
        { label: '传播潜力', v: dims.spread, max: 10 }
      ];
      var dimHtml = '';
      for (var di = 0; di < dimItems.length; di++) {
        var d = dimItems[di];
        var pct = Math.round(d.v / d.max * 100);
        var clr = scoreDimColor(d.v, d.max);
        dimHtml += '<div class="dim"><span class="dim-label">' + d.label + '</span><span class="dim-bar"><span class="dim-fill" style="width:' + pct + '%;background:' + clr + '"></span></span><span class="dim-score" style="color:' + clr + '">' + d.v + '</span></div>';
      }

      // 洞察
      var insightHtml = '';
      for (var ii = 0; ii < t.insights.length; ii++) { insightHtml += '<div class="insight">' + t.insights[ii] + '</div>'; }

      // 角度
      var angleHtml = '';
      for (var ai = 0; ai < t.angles.length; ai++) { angleHtml += '<div class="angle-item">' + t.angles[ai] + '</div>'; }

      // 平台建议
      var platformAdviceHtml = '';
      if (t.platformAdvice) {
        var pa = t.platformAdvice;
        var paKeys = ['微博','知乎','抖音','小红书','B站'];
        var paItems = '';
        for (var pai = 0; pai < paKeys.length; pai++) {
          var pk = paKeys[pai];
          if (pa[pk] && pa[pk].length > 0) {
            paItems += '<div style="margin-bottom:6px;"><strong style="color:var(--accent);font-size:12px;">' + pk + '：</strong><span style="font-size:12px;color:#555;">' + pa[pk][0] + '</span></div>';
          }
        }
        if (paItems) {
          platformAdviceHtml = '<div class="angle-section"><div class="angle-section-title">📱 平台适配建议</div>' + paItems + '</div>';
        }
      }

      // 风险
      var riskCls = t.scoreObj.dims.controversy >= 11 ? 'risk-high' : (t.scoreObj.dims.controversy >= 6 ? 'risk-mid' : 'risk-low');
      var riskHtml = '';
      for (var ri = 0; ri < t.risks.length; ri++) { riskHtml += '<div class="risk-box ' + riskCls + '">⚠️ 风险提示：' + t.risks[ri] + '</div>'; }

      // 时机
      var timingHtml = t.timing ? '<div class="timing-box">' + t.timing.replace(/\n/g, '<br>') + '</div>' : '';

      var rankClass = (i < 3) ? ' top' : '';
      html += '<div class="topic-card">' +
        '<div class="card-top">' +
          '<div class="card-left">' +
            '<div class="rank-num' + rankClass + '">' + String(t.rank).padStart(2, '0') + '</div>' +
            '<div class="topic-text">' + escapeHtml(t.title) + '</div>' +
          '</div>' +
          '<div class="card-score">' +
            '<div class="score-val ' + sc + '">' + t.score + '</div>' +
            '<div class="score-label">选题分</div>' +
            '<div class="score-bar"><div class="score-fill" style="width:' + t.score + '%"></div></div>' +
          '</div>' +
        '</div>' +
        '<div class="card-meta">' + regionTag(t.region) + catTag(t.category) + plat + '</div>' +
        '<div class="score-detail"><div style="font-weight:700;margin-bottom:8px;color:var(--accent);font-size:12px;">📊 评分维度明细</div>' + dimHtml + '<div style="margin-top:8px;font-size:11px;color:var(--muted);">平台加成 +' + t.scoreObj.platformBonus + ' · 关键词加成 +' + t.scoreObj.hotKeywordBonus + '</div></div>' +
        insightHtml +
        platformAdviceHtml +
        '<div class="angle-section"><div class="angle-section-title">✦ 内容角度建议（5个方向）</div>' + angleHtml + '</div>' +
        riskHtml +
        timingHtml +
        '</div>';
    }
    html += '</div>';
  }

  area.innerHTML = html;
}

function escapeHtml(str) {
  var div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

function setFilter(f) {
  activeFilter = f;
  if (currentResults) renderResults(currentResults, f);
}

// ── Storage ──
function saveToStorage(data, raw) {
  try {
    var history = getHistory();
    history.unshift({
      time: new Date().toLocaleString('zh-CN'),
      timestamp: Date.now(),
      summary: data.summary,
      count: (data.topics || []).length,
      raw: raw.substring(0, 500),
      data: data
    });
    if (history.length > 20) history.splice(20);
    localStorage.setItem('zhuxiaomei_history', JSON.stringify(history));
  } catch(e) {}
}

function getHistory() {
  try { return JSON.parse(localStorage.getItem('zhuxiaomei_history') || '[]'); }
  catch(e) { return []; }
}

function loadHistoryFromStorage() {}

function renderHistory() {
  var area = document.getElementById('historyArea');
  var history = getHistory();
  if (!history.length) {
    area.innerHTML = '<div class="empty-state"><div class="empty-icon">📁</div><div class="empty-text">暂无历史记录<br><span style="font-size:12px">每次分析自动保存，最多保留20条</span></div></div>';
    return;
  }
  var html = '';
  for (var i = 0; i < history.length; i++) {
    var h = history[i];
    html += '<div class="hist-card" onclick="loadHistory(' + i + ')"><div class="hist-count">' + h.count + '</div><div class="hist-info"><div class="hist-date">' + h.time + '</div><div class="hist-preview">' + (h.summary || '—') + '</div></div><div class="hist-tip">点击加载 →</div></div>';
  }
  area.innerHTML = html;
}

function loadHistory(idx) {
  var h = getHistory()[idx];
  if (!h) return;
  document.getElementById('rawInput').value = h.raw;
  currentResults = h.data;
  var panels = document.querySelectorAll('.panel');
  for (var i = 0; i < panels.length; i++) panels[i].classList.remove('active');
  var tabs = document.querySelectorAll('.tab-btn');
  for (var j = 0; j < tabs.length; j++) tabs[j].classList.remove('active');
  document.getElementById('panel-analyze').classList.add('active');
  var tabBtns = document.querySelectorAll('.tab-btn');
  if (tabBtns[1]) tabBtns[1].classList.add('active');
  renderResults(h.data, 'all');
}


// ── Hotlist (static data) ──
var _hlPlatform = 'weibo';
var _hlInited = false;
var _HL_DATA = {
weibo:{n:'微博热搜',i:'🐦',d:[
{r:1,t:'外交部回应美方涉华言论',h:'892万'},{r:2,t:'全国多地高温预警',h:'756万'},
{r:3,t:'嫦娥六号任务进展',h:'623万'},{r:4,t:'新能源汽车出口创新高',h:'512万'},
{r:5,t:'A股三大指数收涨',h:'489万'},{r:6,t:'教育部发布最新通知',h:'421万'},
{r:7,t:'知名演员去世',h:'398万'},{r:8,t:'某地突发地震',h:'356万'},
{r:9,t:'网红主播被罚',h:'312万'},{r:10,t:'新剧开播热度登顶',h:'287万'},
{r:11,t:'国际金价波动',h:'254万'},{r:12,t:'手机新品发布会',h:'231万'},
{r:13,t:'体育赛事精彩瞬间',h:'198万'},{r:14,t:'旅游旺季出行提醒',h:'176万'},
{r:15,t:'健康科普辟谣',h:'153万'}
]},
zhihu:{n:'知乎热榜',i:'📘',d:[
{r:1,t:'如何看待当前经济形势？',h:'2856万'},{r:2,t:'AI对就业市场的真实影响',h:'2134万'},
{r:3,t:'年轻人为什么不愿意结婚了？',h:'1876万'},{r:4,t:'有哪些值得一看的纪录片推荐？',h:'1523万'},
{r:5,t:'如何提高工作效率？',h:'1298万'},{r:6,t:'大城市vs小城市生活选择',h:'1156万'},
{r:7,t:'最近有什么好书推荐？',h:'987万'},{r:8,t:'职场新人避坑指南',h:'854万'},
{r:9,t:'健康生活方式分享',h:'723万'},{r:10,t:'科技行业发展趋势分析',h:'651万'}
]},
bilibili:{n:'B站热门',i:'📺',d:[
{r:1,t:'【年度盘点】2025最火视频合集',h:'1234万播放'},{r:2,t:'UP主实测新款手机',h:'987万播放'},
{r:3,t:'搞笑配音：当AI学会吐槽',h:'856万播放'},{r:4,t:'美食探店：隐藏在城市角落的神店',h:'723万播放'},
{r:5,t:'知识科普：宇宙的尽头是什么',h:'654万播放'},{r:6,t:'游戏实况：通关全流程',h:'543万播放'},
{r:7,t:'音乐翻唱：经典老歌新演绎',h:'432万播放'},{r:8,t:'手工DIY：从零开始做家具',h:'387万播放'},
{r:9,t:'旅行vlog：独自环游中国',h:'321万播放'},{r:10,t:'动画短片：治愈系故事',h:'276万播放'}
]},
douyin:{n:'抖音热点',i:'🎵',d:[
{r:1,t:'#外交部回应# 热议中',h:'987万'},{r:2,t:'挑战类视频又火了',h:'876万'},
{r:3,t:'明星同款穿搭分享',h:'765万'},{r:4,t:'美食制作教程走红',h:'654万'},
{r:5,t:'萌宠日常治愈无数人',h:'543万'},{r:6,t:'健身打卡激励视频',h:'432万'},
{r:7,t:'知识科普短视频爆火',h:'387万'},{r:8,t:'旅游攻略合集收藏',h:'321万'},
{r:9,t:'音乐舞蹈挑战赛',h:'276万'},{r:10,t:'情感语录引发共鸣',h:'234万'}
]},
xiaohongshu:{n:'小红书',i:'📕',d:[
{r:1,t:'夏日穿搭灵感｜这5套绝了！',h:'45.6万收藏'},{r:2,t:'平价好物分享｜学生党必看',h:'38.2万收藏'},
{r:3,t:'减脂餐食谱｜一周不重样',h:'32.1万收藏'},{r:4,t:'家居改造｜租房党也能拥有梦想家',h:'28.7万收藏'},
{r:5,t:'护肤干货｜敏感肌自救指南',h:'25.3万收藏'},{r:6,t:'旅行攻略｜小众目的地推荐',h:'21.8万收藏'},
{r:7,t:'学习笔记｜高效记忆法',h:'19.5万收藏'},{r:8,t:'健身教程｜居家塑形计划',h:'17.2万收藏'},
{r:9,t:'数码测评｜性价比之王',h:'15.4万收藏'},{r:10,t:'书单推荐｜本月最爱读',h:'13.1万收藏'}
]}
};
function _e(s){return s?s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'):''}
function _p(n){return n<10?'0'+n:''+n}
function initHotlist(){
var t=document.getElementById('hotlist-tabs');if(!t)return;
var ps=[{k:'weibo',n:'🐦 微博'},{k:'zhihu',n:'📘 知乎'},{k:'bilibili',n:'📺 B站'},{k:'douyin',n:'🎵 抖音'},{k:'xiaohongshu',n:'📕 小红书'}];
t.innerHTML=ps.map(function(p){return'<button class="hotlist-tab'+(p.k===_hlPlatform?' on':'')+'" onclick="_hlS(&apos;'+p.k+'&apos;)">'+p.n+'</button>';}).join('');
renderHotlist();
}
function _hlS(k){_hlPlatform=k;var ts=document.querySelectorAll('.hotlist-tab');for(var i=0;i<ts.length;i++)ts[i].classList.remove('on');var ks=['weibo','zhihu','bilibili','douyin','xiaohongshu'];for(var j=0;j<ks.length;j++){if(ks[j]===k){if(ts[j])ts[j].classList.add('on');break;}}renderHotlist();}
function renderHotlist(){
var el=document.getElementById('hotlist-content');if(!el)return;var p=_HL_DATA[_hlPlatform];if(!p||!p.d||!p.d.length){el.innerHTML='<div class="hotlist-error">暂无数据</div>';return;}
var h='<div class="hotlist-platform-name">'+p.i+' '+_e(p.n)+'</div><div class="hotlist-grid">';
for(var i=0;i<p.d.length;i++){var it=p.d[i];var rc=i<3?' top':'';var inner='<span class="hotlist-rank'+rc+'">'+_p(it.r)+'</span><span class="hotlist-title">'+_e(it.t)+'</span>'+(it.h?'<span class="hotlist-hot">'+_e(it.h)+'</span>':'');h+='<div class="hotlist-item">'+inner+'</div>';}
h+='</div><div style="margin-top:16px;text-align:center;"><a href="https://tophub.today" target="_blank" rel="noopener" style="font-size:12px;color:var(--accent);text-decoration:none;">🔗 前往今日热榜查看完整榜单 →</a></div>';
el.innerHTML=h;
}
async function refreshHotlist(){
var el=document.getElementById('hotlist-content');var sc=document.getElementById('hotlist-source');if(!el)return;
el.innerHTML='<div class="hotlist-loading">⏳ 正在刷新…</div>';
try{var r=await fetch('/api/hotlist?platform=all&_t='+Date.now(),{signal:AbortSignal.timeout(10000)});var j=await r.json();if(j.success&&j.data){var ks=Object.keys(j.data);for(var k=0;k<ks.length;k++){var kd=j.data[ks[k]];if(kd&&kd.d)_HL_DATA[ks[k]]={n:kd.n||ks[k],i:kd.i||'',d:kd.d};}if(sc)sc.textContent='实时 ('+new Date().toLocaleTimeString('zh-CN')+')';renderHotlist();return;}}catch(e){}
if(sc)sc.textContent='内置数据';renderHotlist();
}


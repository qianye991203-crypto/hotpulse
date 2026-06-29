const fs = require('fs');
const path = require('path');
const dir = 'C:\\Users\\VRPC01\\.qclaw\\workspace\\hotpulse';

// Weibo data (51 items)
const weibo = [
    ["法国紧急下单3万台空调",1164727],["韩剧编剧又升级了",953330],["行程万里不忘初心",939708],
    ["薇诺娜清透防晒乳5折只在拼多多",937693],["尽量少用玻璃吸管",935975],["NBA交易",747132],
    ["法拉利被4个孩子当滑梯玩",688202],["5万块的威力",681502],["恋与深空失控领地",543557],
    ["白宇摘下白玉兰送给杨幂",424359],["广州一高校通报网传禁止小米汽车入校",420900],
    ["47岁吴建豪再婚",420182],["女儿称是生父强奸所生拒付赡养费",415128],["杨紫飞奔拥抱胡歌",410201],
    ["赵今麦娇兰全球总裁LV太子妃合照",406202],["外网预言中国举办世界杯时间",404258],
    ["撒旦的腋窝是什么比喻",401840],["母亲获赔80万弟弟拿74万姐姐3万",395197],
    ["在家赤身裸体是否绝对自由",394973],["杨紫下沉市场口碑",391286],
    ["网约车司机转账1.5万后被乘客拉黑",387073],["韩国国脚每人获35.5万奖金",384015],
    ["尹恩惠自曝14年没谈过恋爱",382838],["日本前锋言论激怒巴西",370365],
    ["吴建豪老婆",360761],["世界杯超牛补水广告出现了",342941],
    ["12人以护剧为名敲诈剧组艺人被抓",339848],["孙怡告别浪姐千字文",325855],
    ["曝歌手第七期帮唱阵容",315218],["美的空调卡bug",294126],["iPhone18系列预计将大幅涨价",288687],
    ["龟梨和也田中美奈实结婚",286203],["光与夜之恋",279489],["葫芦岛居民楼爆炸致3失联8伤",278912],
    ["恋与深空遭抵制后仍置顶敖敖",276417],["papi酱回应毕业4年零收入",257047],
    ["陈靖可虞书欣领衔主演",247545],["四川宜宾地震",245666],["AG冠军五人组轮换",232054],
    ["巴黎两家殡仪馆爆满",220838],["王楚钦表演球擦网",217706],["阿娇瘦了10斤",215194],
    ["哈兰德之歌火到国外",201246],["毕业群都在出什么东西",197425],["恋与深空评分暴跌至1.8",191582],
    ["林昀儒止步美国大满贯首轮",179789],["内马尔能上场15分钟",169837],["曾沛慈夺冠后和姐妹齐聚庆功宴",169832],
    ["爸爸当家",169575],["三星与SK集团或将投资2000万亿韩元",169087],["智界V9成为高端圈层共同选择",168985]
];

// Baidu data (51 items) - already scaled down
const baidu = [
    ["永远保持对人民的赤子之心",7903993],["法国紧急下单3万台空调",7809466],
    ["韩国媒体破防：被中国球迷当笑柄",7713675],["上周末多领域成果密集“上新”",7616536],
    ["在自己家不穿衣服犯法吗",7521182],["巴西国脚说不出日本球员全场哄笑",7423738],
    ["韩国主帅辞职念完稿双手插兜离场",7333346],["宜宾地震食客避难后折返无人逃单",7234262],
    ["利率一再降“存款搬家”搬去哪",7135612],["法总统候选人：拒绝与中国激烈对抗",7048118],
    ["五粮液回应宜宾地震影响",6943777],["造谣县城满街都是小混混男子被拘",6855186],
    ["吴建豪宣布再婚",6759890],["欧洲人驾车200公里抢购中国空调",6662857],
    ["三甲医生提醒青蛙腹是最糟糕体型",6563758],["葫芦岛居民楼爆炸致3人失联8人轻微伤",6463337],
    ["空调两年没洗男子吹了三天双肺全白",6383233],["韩国队启程回国全员羞愧低头",6276906],
    ["中方将20家日本实体列入出口管制名单",6179181],["戴军否认1993年月入过万",6088706],
    ["FIFA回应佛得角队长被指控强奸",5989149],["韩国队差旅费亏麻了",5895479],
    ["日本主帅：对战胜巴西很有信心",5794956],["中国战机大片上新",5716480],
    ["法拉利被当滑梯玩出现多处划痕",5613832],["世界杯看台惊现一群“哈兰德”",5506809],
    ["赵露思爸爸拍vlog“翻车”",5430211],["央视曝光高价回收老物件骗局",5323788],
    ["欧洲多国激辩“装不装空调”",5240903],["教育部发布预警事关高招录取",5127207],
    ["德国连续三天刷新本国最高气温纪录",5047704],["韩国极端网友对主教练发出死亡威胁",4927664],
    ["周锡玮：做堂堂正正的中国人",4860878],["中方将20家日本实体列入关注名单",4738264],
    ["内马尔世界杯期间豪购百万美元腕表",4638115],["伊朗队员在酒店看球从狂喜到绝望",4554515],
    ["梅朗雄主张法国退出北约",4453529],["王楚钦欢迎晚宴上打台球",4371430],
    ["哈兰德这该死的胜负欲",4264738],["大疆7月15日起涨价？公司回应",4179713],
    ["拆快递不再“里三层外三层”",4081542],["欧洲极端高温美的“卡bug”空调卖爆",3992609],
    ["全国第三艘万车级汽车运输船交付",3897435],["中俄联合巡航阵容强大日本慌了？",3801246],
    ["王楚钦3-0周启豪晋级32强",3698965],["唐国强打卡贵阳孔学堂",3612942],
    ["林昀儒不敌17岁小将止步首轮",3512425],["未来5年全国能源体系将呈现这些特征",3422789],
    ["巴西发布对阵日本宣传片",3318170],["日本主帅：目标是冠军",3232069],
    ["日本在南鸟岛部署岸舰导弹发射装置",3127954]
];

// Normalize baidu scores (divide by ~10 to match weibo scale)
const baiduScaled = baidu.map(([w, s]) => [w, Math.round(s / 10)]);

// Merge with deduplication
const seen = new Set();
const merged = [];

// Normalize text for comparison
function norm(s) { return s.replace(/[^\u4e00-\u9fa5a-zA-Z0-9]/g, '').toLowerCase(); }

// Add weibo first (already higher quality)
for (const [word, hot] of weibo) {
    const k = norm(word);
    if (!seen.has(k)) {
        seen.add(k);
        merged.push([word, hot, '微博']);
    }
}
for (const [word, hot] of baiduScaled) {
    const k = norm(word);
    if (!seen.has(k)) {
        seen.add(k);
        merged.push([word, hot, '百度']);
    }
}

// Sort by hot score descending
merged.sort((a, b) => b[1] - a[1]);

const top100 = merged.slice(0, 100);

// Generate hotlist HTML
function esc(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

let html = `<div class="hotlist-merged">`;
top100.forEach(([word, hot, src], i) => {
    const rank = String(i+1).padStart(2,'0');
    const heat = hot >= 10000 ? (hot/10000).toFixed(1)+'亿' : hot+'万';
    html += `<div class="hot-item" data-rank="${rank}" onclick="showDetail('${esc(word)}','${src}')">
        <span class="rank">${rank}</span>
        <span class="title">${esc(word)}</span>
        <span class="heat">${heat}</span>
    </div>`;
});
html += `</div>`;

// Read current index.html and update
let index = fs.readFileSync(path.join(dir, 'index.html'), 'utf8');

// Update date
const today = '2026年06月29日';
const time = '13:59';
index = index.replace(/更新于\d{4}年\d{2}月\d{2}日 \d{2}:\d{2}/, `更新于${today} ${time}`);
index = index.replace(/更新时间：\d{4}年\d{2}月\d{2}日/, `更新时间：${today}`);
index = index.replace(/footer.*?update-time.*?(\d{2}:\d{2})/s, `footer update-time">${time}`);

// Replace hotlist content
index = index.replace(/<div class="hotlist-merged">[\s\S]*?<\/div>\s*<\/div>\s*<\/div>\s*<\/div>\s*<\/div>\s*<\/div>\s*<\/div>\s*<!--\s*平台Tab内容\s*-->/,
    html + `\n</div></div></div></div></div></div></div><!-- 平台Tab内容 -->`);

fs.writeFileSync(path.join(dir, 'index.html'), index, 'utf8');
console.log('Updated index.html with', top100.length, 'hot items, date:', today);

// Also update hotlist_100.json
const json100 = top100.map(([word, hot, src]) => [word, src, hot, 1000 - top100.indexOf([word,hot,src])]);
fs.writeFileSync(path.join(dir, 'hotlist_100.json'), JSON.stringify(json100, null, 2), 'utf8');
console.log('Updated hotlist_100.json');

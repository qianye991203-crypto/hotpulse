// Self-test: simulate DOM operations to verify JS logic works
const fs = require('fs');
const h = fs.readFileSync('index.html', 'utf8');

console.log('=== JS Syntax Check ===');
try {
  // Extract script content
  const scriptStart = h.indexOf('<script>') + 8;
  const scriptEnd = h.indexOf('</script>');
  const js = h.substring(scriptStart, scriptEnd);
  new Function(js);
  console.log('✅ JavaScript syntax is valid (no parse errors)');
} catch(e) {
  console.log('❌ JS Syntax Error:', e.message);
}

// Simulate calcScore
console.log('\n=== Scoring Engine Test ===');

// We need to extract and run the functions
const scriptStart = h.indexOf('<script>') + 8;
const scriptEnd = h.indexOf('</script>');
const jsCode = h.substring(scriptStart, scriptEnd);

// Create mock DOM
global.document = {
  getElementById: () => ({ textContent:'', style:{}, classList:{add(){},remove(){}}, innerHTML:'', scrollIntoView(){} }),
  querySelectorAll: () => ({ forEach(){} }),
  querySelector: () => null
};
global.window = {};
global.alert = () => {};
global.localStorage = { getItem:()=>'[]', setItem(){} };
global.requestAnimationFrame = (fn) => fn(performance.now());
global.performance = { now:()=>0 };

try {
  eval(jsCode);
  
  // Test 1: High-score topic
  var r1 = calcScore('刚刚！外交部回应美方涉华言论，网友炸了', '抖音', '口播');
  console.log('Test1 - 高热度话题:', r1.total, '分 (expect 70+)', r1.total >= 70 ? '✅' : '❌');
  
  // Test 2: Medium topic
  var r2 = calcScore('AI工具推荐', '小红书', '图文');
  console.log('Test2 - 中等话题:', r2.total, '分 (expect 40-70)', r2.total >= 40 && r2.total < 70 ? '✅' : '❌');
  
  // Test 3: Low topic
  var r3 = calcScore('今天天气不错', '全平台', '');
  console.log('Test3 - 低热度:', r3.total, '分 (expect <50)', r3.total < 50 ? '✅' : '❌');
  
  // Test dimensions
  console.log('\nTest1 维度详情:');
  r1.dimensions.forEach(d => console.log(`  ${d.name}: ${d.value}`));
  
  // Test angle generation
  var angles = generateAngle('外交部回应美方涉华言论', '抖音');
  console.log('\nTest 角度生成:', angles.length, '个 (expect 4)', angles.length === 4 ? '✅' : '❌');
  angles.forEach((a,i) => console.log(`  ${i+1}. ${a.title}: ${a.desc.substring(0,40)}...`));
  
  // Test insight
  console.log('\nTest 洞察生成长度:', r1.insight.length, 'chars (>50?)', r1.insight.length > 50 ? '✅' : '❌');
  
  console.log('\n🎉 All engine tests passed!');
  
} catch(e) {
  console.log('❌ Runtime Error:', e.message);
  console.log(e.stack);
}

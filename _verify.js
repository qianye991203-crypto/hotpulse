
const fs=require("fs");
const h=fs.readFileSync("index.html","utf8");
var ok=true;
var checks=[
  ["</html>","HTML close"],
  ["</script>","Script close"],
  ["</body>","Body close"],
  ['id="panel-hot"',"panel-hot"],
  ['id="panel-analyze"',"panel-analyze"],
  ['id="panel-content"',"panel-content"],
  ['id="panel-history"',"panel-history"],
  ["switchTab","switchTab fn"],
  ["runAnalyze","runAnalyze fn"],
  ["calcScore","calcScore fn"],
  ["hotlist-merged","hotlist-merged"],
  ["选题热度分析","analyze title"],
  ["爆款参考案例","content title"],
  ["analyze-input-area","analyze form"],
  ["content-grid","content cards"],
  ["btn-analyze","analyze button"]
];
checks.forEach(function(c){
  var pass=h.indexOf(c[0])!==-1;
  if(!pass)ok=false;
  console.log((pass?"✅":"❌")+" "+c[1]);
});
console.log(ok?"\n🎉 ALL CHECKS PASSED!":"\n⚠️ SOME CHECKS FAILED");

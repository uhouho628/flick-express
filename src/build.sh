#!/bin/zsh
# index.html      … claude.ai Artifact 用（文書の骨組みは公開時に付く）
# docs/index.html … GitHub Pages 用の完全なHTML文書
cd "$(dirname "$0")"
cat p1_style.html p2_style.html p3_markup.html p4_stations.html p5_kbd.html p6_game.html p6b_native.html p7_result.html > ../index.html
mkdir -p ../docs
{
  cat <<'HEAD'
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="寿司打のフリック入力版。全国の駅名をスマホのフリックで打ち切って電車に乗り、1日乗車券の元を取るタイピングゲーム。">
<meta property="og:type" content="website">
<meta property="og:title" content="フリック特急">
<meta property="og:description" content="全国の駅名をフリック入力で打つタイピングゲーム。電車が出る前に打ち切れば乗車、1日乗車券の元を取れるか。">
<meta property="og:url" content="https://uhouho628.github.io/flick-express/">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#1f7a3f">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect x='5' y='3' width='22' height='22' rx='6' fill='%231f7a3f'/%3E%3Crect x='9' y='7' width='14' height='8' rx='2' fill='%23e8f3ec'/%3E%3Ccircle cx='11' cy='20' r='2' fill='%23ffd34d'/%3E%3Ccircle cx='21' cy='20' r='2' fill='%23ffd34d'/%3E%3Cpath d='M9 30l3-5M23 30l-3-5' stroke='%231f7a3f' stroke-width='2.5' stroke-linecap='round'/%3E%3C/svg%3E">
<style>
:root{color-scheme:light}
html{box-sizing:border-box;padding-top:env(safe-area-inset-top,0px)}
body{margin:0;font-size:14px}
img{max-width:100%}
[hidden]{display:none!important}
</style>
HEAD
  cat p1_style.html p2_style.html
  echo '</head>'
  echo '<body>'
  cat p3_markup.html p4_stations.html p5_kbd.html p6_game.html p6b_native.html p7_result.html
  echo '</body>'
  echo '</html>'
} > ../docs/index.html
python3 - <<'PY'
import re
s=open('../index.html').read()
open('/tmp/flick-all.js','w').write("\n".join(re.findall(r'<script>(.*?)</script>',s,re.S)))
PY
node --check /tmp/flick-all.js && echo BUILD_OK

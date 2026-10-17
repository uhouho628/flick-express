#!/usr/bin/env python3
"""TrainLCD/StationAPI の CSV から p4_stations.html（駅データ）を作る。

使い方: python3 make_stations.py <CSVのあるフォルダ> [読みの修正JSON]
CSV: 1!companies.csv 2!lines.csv 3!stations.csv（MIT, https://github.com/TrainLCD/StationAPI）
修正JSON（検証で直した分）:
  {"readings": {"駅名|都道府県番号": "正しいよみ"},
   "rename":   {"旧駅名|都道府県番号": ["新駅名", "よみ"]},
   "drop":     ["駅名|都道府県番号"],            # 廃止済みなのに営業中扱いの駅
   "add":      [["駅名", "よみ", 都道府県番号, ["路線名"]]]}   # データにない新駅
"""
import csv, json, os, re, sys, collections

src = sys.argv[1]
fixes = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}
READ_FIX, RENAME = fixes.get('readings', {}), fixes.get('rename', {})
DROP, ADD = set(fixes.get('drop', [])), fixes.get('add', [])
used = set()

def rd(name):
    for cand in (name, name.replace('!', '_')):
        p = os.path.join(src, cand)
        if os.path.exists(p):
            return list(csv.DictReader(open(p, encoding='utf-8')))
    raise SystemExit('not found: ' + name)

companies = {r['company_cd']: r for r in rd('1!companies.csv')}
lines = {r['line_cd']: r for r in rd('2!lines.csv')}
stations = rd('3!stations.csv')

FW = str.maketrans({chr(0xFF10 + i): str(i) for i in range(10)} |
                   {chr(0xFF21 + i): chr(65 + i) for i in range(26)} |
                   {chr(0xFF41 + i): chr(97 + i) for i in range(26)})

def hira(k):
    return ''.join(chr(ord(c) - 0x60) if 0x30A1 <= ord(c) <= 0x30F6 else c for c in k)

# 表示名の整理：読みに含まれない副名称は表示からも外す。〈〉は（）にそろえる
DISPLAY = {
    'ジヤトコ前（ジヤトコ1地区前）': 'ジヤトコ前',
    'スタジアムシティサウス（宝町）': 'スタジアムシティサウス',
    'スタジアムシティノース（銭座町）': 'スタジアムシティノース',
    '成田空港（第1旅客ターミナル）': '成田空港',
    '空港第2ビル（第2旅客ターミナル）': '空港第2ビル',
    '粟島（大阪屋ショップ前）': '粟島',
    '鹿島サッカースタジアム（臨）': '鹿島サッカースタジアム',
    '押上〈スカイツリー前〉': '押上（スカイツリー前）',
    '明治神宮前〈原宿〉': '明治神宮前（原宿）',
    '獨協大学前〈草加松原〉': '獨協大学前（草加松原）',
}
TYPEABLE = set('あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんー'
               'がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽぁぃぅぇぉっゃゅょゎゔ')

def active(r):
    l = lines.get(r['line_cd'])
    return (r['e_status'] == '0' and l and l['e_status'] == '0'
            and companies.get(l['company_cd'], {}).get('e_status') == '0')

entries = collections.OrderedDict()
for r in stations:
    if not active(r):
        continue
    disp = r['station_name'].translate(FW)
    disp = DISPLAY.get(disp, disp)
    pref = int(r['pref_cd'])
    k = f'{disp}|{pref}'
    if k in DROP:
        used.add(k); continue
    read = hira(r['station_name_k'])
    if k in RENAME:
        used.add(k); disp, read = RENAME[k]; k = f'{disp}|{pref}'
    if k in READ_FIX:
        used.add(k); read = READ_FIX[k]
    read = re.sub(r'[\s　・（）()〈〉「」]', '', read)
    bad = set(read) - TYPEABLE
    if bad:
        raise SystemExit(f'打てない字 {bad}: {disp} {read}')
    key = (disp, read, pref)
    e = entries.setdefault(key, {'lines': []})
    name = lines[r['line_cd']]['line_name']
    if name not in e['lines']:
        e['lines'].append(name)

for disp, read, pref, lns in ADD:
    e = entries.setdefault((disp, read, pref), {'lines': []})
    e['lines'] += [n for n in lns if n not in e['lines']]
unused = (set(READ_FIX) | set(RENAME) | DROP) - used
if unused:
    print('使われなかった修正:', sorted(unused))

line_names = sorted({n for e in entries.values() for n in e['lines']})
line_idx = {n: i for i, n in enumerate(line_names)}
data = [[d, rdg, p, [line_idx[n] for n in e['lines']]] for (d, rdg, p), e in entries.items()]

PREFS = ('北海道 青森県 岩手県 宮城県 秋田県 山形県 福島県 茨城県 栃木県 群馬県 埼玉県 千葉県 東京都 神奈川県 '
         '新潟県 富山県 石川県 福井県 山梨県 長野県 岐阜県 静岡県 愛知県 三重県 滋賀県 京都府 大阪府 兵庫県 '
         '奈良県 和歌山県 鳥取県 島根県 岡山県 広島県 山口県 徳島県 香川県 愛媛県 高知県 福岡県 佐賀県 長崎県 '
         '熊本県 大分県 宮崎県 鹿児島県 沖縄県').split()
REGIONS = [
    {'id': 'all', 'name': '全国'},
    {'id': 'hokkaido', 'name': '北海道', 'p': [1]},
    {'id': 'tohoku', 'name': '東北', 'p': list(range(2, 8))},
    {'id': 'kanto', 'name': '関東', 'p': list(range(8, 15))},
    {'id': 'chubu', 'name': '中部', 'p': list(range(15, 24))},
    {'id': 'kinki', 'name': '近畿', 'p': list(range(24, 31))},
    {'id': 'chugoku', 'name': '中国', 'p': list(range(31, 36))},
    {'id': 'shikoku', 'name': '四国', 'p': list(range(36, 40))},
    {'id': 'kyushu', 'name': '九州・沖縄', 'p': list(range(40, 48))},
]

j = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':'))
out = f"""<script>
// 駅データ：TrainLCD/StationAPI（MIT）の営業中の駅 {len(data)} 駅。読みは Wikidata・Wikipedia と照合済み
// [表示名, よみ, 都道府県番号, [路線番号...]]
const PREFS = {j(PREFS)};
const REGIONS = {j(REGIONS)};
const LINES = {j(line_names)};
const STATIONS = {j(data)};
const COURSES = {{
  kaku:    {{id:"kaku",    name:"各停", label:"各停コース", price:3000,  time:60,  color:"var(--kaku)",    desc:"よみ4字まで",  min:1, max:4,  base:2.6, per:0.85}},
  kaisoku: {{id:"kaisoku", name:"快速", label:"快速コース", price:5000,  time:90,  color:"var(--kaisoku)", desc:"よみ5〜7字",   min:5, max:7,  base:2.4, per:0.7}},
  tokkyu:  {{id:"tokkyu",  name:"特急", label:"特急コース", price:10000, time:120, color:"var(--tokkyu)",  desc:"よみ8字以上", min:8, max:99, base:2.2, per:0.6}},
}};
</script>
"""
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'p4_stations.html'), 'w').write(out)
lens = collections.Counter(len(d[1]) for d in data)
print(len(data), 'stations,', len(line_names), 'lines')
print('各停', sum(v for k, v in lens.items() if k <= 4), '快速', sum(v for k, v in lens.items() if 5 <= k <= 7),
      '特急', sum(v for k, v in lens.items() if k >= 8), 'max', max(lens))

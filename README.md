# フリック特急

寿司打のフリック入力版。発車標に出た全国の駅名を、スマホのフリック入力で電車が出る前に打ち切ると乗車できます。乗った電車の運賃が1日乗車券の値段を超えたらおトク。

**遊ぶ:** https://uhouho628.github.io/flick-express/

- 行先は 2026年10月時点で営業中の全国 8,944 駅
- コースは読みの長さで3つ（各停：4字まで／快速：5〜7字／特急：8字以上）、地方でも絞り込める
- 濁点・半濁点・小さい字は「小゛゜」キー（タップで切り替え、左に払うと ゛、上で小さい字、右で ゜）。「ー」は「わ」キーを右に払う

## ファイル

| パス | 中身 |
| --- | --- |
| `docs/index.html` | GitHub Pages で配信しているページ（ビルド結果） |
| `src/p1_style.html` 〜 `src/p7_result.html` | ページの部品（見た目・画面・駅データ・キーボード・ゲーム・結果） |
| `src/build.sh` | 部品をつないで `docs/index.html` を作る |
| `src/make_stations.py` | 駅データの CSV から `src/p4_stations.html` を作る |
| `src/fixes.json` | 元データから直した読み・駅名の改称・廃止 |

駅データを作り直すとき：

```sh
# TrainLCD/StationAPI の data/1!companies.csv 2!lines.csv 3!stations.csv を1つのフォルダに置く
python3 src/make_stations.py path/to/csv src/fixes.json
src/build.sh
```

## 駅データ

[TrainLCD/StationAPI](https://github.com/TrainLCD/StationAPI) の駅データ（MIT License, Copyright (c) 2019 TinyKitten）をもとにしています。読みは Wikidata・日本語版 Wikipedia・各鉄道会社の駅案内と照合し、食い違った駅は `src/fixes.json` で直しています。

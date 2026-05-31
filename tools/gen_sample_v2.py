# -*- coding: utf-8 -*-
"""saketto / 銘柄詳細ページ V2 サンプル

社長指示: いったん1本作って判断 → 横展開
対象: haccoba「はなうたホップス」(haccoba-0.html を上書き)

V2の新セクション:
- 酒税法分類バッジ
- 大判 CORE SPECS (ABV / Volume / Price)
- RECIPE 詳細テーブル (米品種・精米歩合・酒母・麹菌・酵母・仕込水・容器・火入れ)
- HOW TO ENJOY (保存・温度・グラス・ペアリング)
- TASTING 3段 (香り / 含み香 / 余韻)
- FLAVOR PROFILE (4軸構造スケール SVG + 6軸レーダー SVG + タグ)
- STORY (コラボ・LAB背景)
- AWARDS (per銘柄)
- KURA + PURCHASE
- 関連 + 出典 + データ更新日 + 専門用語ミニ解説
"""

import math
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from breweries_master import by_slug
from moshimo_link import rakuten_search, amazon_search
from site_common import head_extra

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "brand" / "haccoba-0.html"

# アフィリエイト（もしも経由 楽天/Amazon）の表示制御
# サイト登録が完了したら True に戻すと購入ボタンが復活する
AFFILIATE_ENABLED = False


# ────────────── サンプル銘柄データ (はなうたホップス) ──────────────
# 一次ソース確認済み + 編集部初期値（要更新の項目は data_status で明示）

BRAND = {
    "brewery_slug": "haccoba",
    "name": "はなうたホップス",
    "kana": "ハナウタホップス",
    "category": "その他の醸造酒",
    "tagline": "「花酛」復刻 × クラフトビールのドライホッピング。haccobaが切り拓いた、クラフトサケのアイコン銘柄。",

    # CORE SPECS（2025BY No.1 基準）
    "abv": 13,
    "abv_note": "ロットにより11〜13%帯で変動。本ページは2025BY No.1基準",
    "volume_ml": 720,
    "price": 2420,
    "price_note": "参考価格・確認日 2026/05/30",

    # RECIPE（一次ソース確認済み・2025BY No.1基準）
    "sub_ingredients": ["ホップ", "唐花草（カラハナソウ）"],
    "sub_ingredients_detail": "Citra・Talus・Motueka・Galaxy等のアロマホップ（ロット別組合せ）+ 古来からの唐花草",
    "rice_variety": "天のつぶ（福島県産）",
    "rice_polish": 88,
    "shubo": "花酛（はなもと）",
    "shubo_note": "東北に伝わる幻のどぶろく製法。haccobaが復刻し、ドライホッピングと融合",
    "koji": "黄麹＋白麹（併用）",
    "yeast": "ロット別（2023BY No.4 は BRY-97 ビール酵母、他公式非開示）",
    "water": "公式非開示",
    "vessel": "公式非開示（発酵温度18〜22℃の高温発酵）",
    "pasteurized": False,  # 生酒
    "draft": None,

    # HOW TO ENJOY
    "preservation": "要冷蔵・クール便必須",
    "open_days": None,
    "serving_temp": "8℃推奨（公式）",
    "glass": "白ワイン用の小ぶりなワイングラス（編集部推奨）",
    "pairing": [
        "白身魚のカルパッチョ",
        "ナンプラー・パクチーのエスニック料理",
        "イタリアン（カプレーゼ等）",
        "山羊チーズ",
    ],

    # TASTING（IMADEYA + haccoba note より）
    "tasting_nose": "柑橘やマスカットなどの香りが広がるアロマホップ、グレープフルーツのようなシトラスのアロマ。",
    "tasting_palate": "グレープフルーツのような味わいが口いっぱいに広がり、お米とホップが調和した「セッション」。黄麹由来の米の甘みと白麹由来のレモンのような酸。",
    "tasting_finish": "熟成していくと全く表情が変わり、ライチなどの熟したフルーツのような印象に変化。",
    "tasting_source_name": "IMADEYA ONLINE STORE / haccoba note",
    "tasting_source_url": "https://imadeya.co.jp/products/8180977172645",

    # FLAVOR PROFILE（編集部初期値）
    "scale4": {
        "body":    0.35,
        "sweet":   0.42,
        "acid":    0.65,
        "clarity": 0.55,
    },
    "radar6": {
        "華やか":   5,
        "酸味":     4,
        "甘味":     3,
        "コク":     3,
        "米感":     4,
        "複雑性":   4,
    },
    # 香り・味の印象キーワードのみ（品種名Citra/Talusや製法用語は混ぜない）
    "flavor_tags": ["シトラス", "グレープフルーツ", "マスカット", "ホップ香", "ライチ（熟成）", "レモンのような酸"],

    # STORY（一次ソース確認済み）
    "story": (
        "haccoba は2021年2月、東日本大震災で一度ゴーストタウン化した福島県南相馬市小高区に、"
        "元IT職の佐藤太亮氏が立ち上げたクラフトサケ蔵。"
        "「金はないけど、熱はある」を合言葉に、清酒免許の制約を逃れる"
        "「その他の醸造酒」枠で表現の自由を確保した。"
        "看板銘柄「はなうたホップス」は、東北に伝わる幻のどぶろく製法「花酛（はなもと）」——"
        "古来カラハナソウを使った歴史をヒントに、黄麹で米の甘み、白麹でレモンのような酸を引き出し、"
        "クラフトビールのドライホッピング技法で Citra・Talus・Motueka・Galaxy 等のアロマホップを重ねた一本。"
        "Makuakeでの人気投票A案から2021年6月14日に商品化された。"
        "佐藤氏は「昔の酒づくりはもっと自由だった。これからも自由な方が良い」と語る。"
    ),
    "story_source_name": "PR TIMES／Diamond Online／haccoba note",
    "story_source_url": "https://prtimes.jp/main/html/rd/p/000000003.000061904.html",

    # AWARDS（per銘柄。受賞は蔵単位だが銘柄に紐づくものを記載）
    "awards": [
        {
            "year": 2023,
            "title": "ICC SAKE AWARD 準決勝進出",
            "where": "ICC KYOTO 2023",
            "source": "https://industry-co-creation.com/news/93891",
        },
    ],
    # 蔵全体としては「日本パッケージデザイン大賞2025 銀賞（水を編むシリーズ）」「東北アントレプレナー大賞2025」も
    # ただしはなうたホップス単独の受賞ではないので含めない（嘘ゼロ運用）

    # AVAILABILITY
    "availability": "online",
    "official_ec_url": "https://haccoba.com/products/hanauta-hops20",

    # META
    "data_updated": "2026/05/30",
    "sources_extra": [
        "https://haccoba.com/products/hanauta-hops23",
        "https://imadeya.co.jp/products/8180977172645",
        "https://note.com/haccoba/n/n22d0797a17cb",
        "https://note.com/haccoba/n/na8aae391dec3",
        "https://prtimes.jp/main/html/rd/p/000000003.000061904.html",
        "https://diamond.jp/articles/-/292641",
        "https://industry-co-creation.com/news/93891",
    ],

    # 専門用語（その銘柄に登場する用語のみ）
    "glossary": [
        ("花酛（はなもと）", "東北地方に伝わるどぶろくの古典製法。「東洋のホップ」と呼ばれる唐花草（カラハナソウ）を使って自然発酵させる。明治の自家醸造禁止で衰退していたものを haccoba が復刻。"),
        ("その他の醸造酒", "酒税法上、副原料を加えた米由来の醸造酒は「清酒」を名乗れず、この区分に分類される。クラフトサケの大半がこのカテゴリ。"),
        ("ドライホッピング", "発酵後にホップを漬け込み、香りを抽出するクラフトビールの技法。haccobaは日本酒製造にこれを応用。"),
    ],
}


# ────────────── SVG 生成ヘルパー ──────────────

def gen_scale4_svg(scale):
    """4軸構造スケール: 横長バー × 4 + 1-5目盛り + 位置ドット"""
    axes = [
        ("軽快", "濃醇", scale["body"]),
        ("甘口", "辛口", scale["sweet"]),
        ("酸控", "酸強", scale["acid"]),
        ("清澄", "にごり", scale["clarity"]),
    ]
    W, H = 480, 260
    rows = []
    bar_x = 80
    bar_w = 320
    n_ticks = 5  # 1-5 スケール
    for i, (left, right, val) in enumerate(axes):
        y = 35 + i * 56
        dot_x = bar_x + val * bar_w
        # 値の1-5換算
        score = 1 + val * (n_ticks - 1)

        # 目盛り（1-5の縦線＋数字）
        ticks_svg = []
        for t in range(n_ticks):
            tx = bar_x + (t / (n_ticks - 1)) * bar_w
            # 縦の目盛り線
            ticks_svg.append(
                f'<line x1="{tx:.1f}" y1="{y-5}" x2="{tx:.1f}" y2="{y+5}" '
                f'stroke="#C0B69E" stroke-width="1"/>'
            )
            # 数字ラベル（下）
            ticks_svg.append(
                f'<text x="{tx:.1f}" y="{y+19}" font-family="Cormorant Garamond" '
                f'font-style="italic" font-size="11" text-anchor="middle" fill="#635C57">{t+1}</text>'
            )
        ticks_html = ''.join(ticks_svg)

        rows.append(f"""
    <text x="{bar_x - 12}" y="{y+5}" font-family="Shippori Mincho" font-size="13"
          font-weight="500" text-anchor="end" fill="#3D3633">{left}</text>
    <line x1="{bar_x}" y1="{y}" x2="{bar_x+bar_w}" y2="{y}" stroke="#C0B69E" stroke-width="1"/>
    {ticks_html}
    <circle cx="{dot_x:.1f}" cy="{y}" r="8" fill="#A8351F"/>
    <circle cx="{dot_x:.1f}" cy="{y}" r="13" fill="none" stroke="#A8351F" stroke-width="1" opacity="0.35"/>
    <text x="{bar_x+bar_w+12}" y="{y+5}" font-family="Shippori Mincho" font-size="13"
          font-weight="500" fill="#3D3633">{right}</text>
    <text x="{dot_x:.1f}" y="{y-12}" font-family="Cormorant Garamond" font-style="italic"
          font-size="13" font-weight="500" text-anchor="middle" fill="#A8351F">{score:.1f}</text>""")
    return f"""<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" aria-label="4軸構造スケール">
{''.join(rows)}
</svg>"""


def gen_radar6_svg(values):
    """6軸レーダー: 1-5スケール、6カテゴリ"""
    cx, cy = 130, 130
    max_r = 90
    max_val = 5
    axes = ["華やか", "酸味", "甘味", "コク", "米感", "複雑性"]

    def point(angle_deg, r):
        rad = math.radians(angle_deg - 90)
        return (cx + r * math.cos(rad), cy + r * math.sin(rad))

    # 同心六角形（参照）
    rings_svg = ""
    for level in range(1, max_val + 1):
        r = max_r * level / max_val
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in [point(i*60, r) for i in range(6)])
        opacity = 0.18 if level == max_val else 0.10
        rings_svg += f'<polygon points="{pts}" fill="none" stroke="#C0B69E" stroke-width="0.7" opacity="{opacity}"/>\n    '

    # 軸線
    axis_svg = ""
    for i in range(6):
        x, y = point(i*60, max_r)
        axis_svg += f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#C0B69E" stroke-width="0.5" opacity="0.5"/>\n    '

    # データ多角形
    data_pts = []
    for i, name in enumerate(axes):
        v = values.get(name, 0)
        r = max_r * v / max_val
        x, y = point(i*60, r)
        data_pts.append(f"{x:.1f},{y:.1f}")
    data_poly = " ".join(data_pts)

    # データ頂点ドット
    dots_svg = ""
    for i, name in enumerate(axes):
        v = values.get(name, 0)
        r = max_r * v / max_val
        x, y = point(i*60, r)
        dots_svg += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="#A8351F"/>\n    '

    # 軸ラベル
    labels_svg = ""
    for i, name in enumerate(axes):
        lx, ly = point(i*60, max_r + 22)
        labels_svg += f'<text x="{lx:.1f}" y="{ly:.1f}" font-family="Shippori Mincho" font-size="13" font-weight="600" fill="#16100E" text-anchor="middle" dominant-baseline="middle">{name}</text>\n    '

    # 値ラベル
    value_labels = ""
    for i, name in enumerate(axes):
        v = values.get(name, 0)
        r = max_r * v / max_val
        x, y = point(i*60, r + 12)
        value_labels += f'<text x="{x:.1f}" y="{y:.1f}" font-family="Cormorant Garamond" font-style="italic" font-size="11" fill="#A8351F" text-anchor="middle">{v}</text>\n    '

    return f"""<svg viewBox="0 0 260 280" xmlns="http://www.w3.org/2000/svg" aria-label="6軸フレーバープロファイル">
    {rings_svg}{axis_svg}
    <polygon points="{data_poly}" fill="#A8351F" fill-opacity="0.18" stroke="#A8351F" stroke-width="1.5"/>
    {dots_svg}{labels_svg}{value_labels}
</svg>"""


# ────────────── HTMLテンプレート ──────────────

CSS = """
:root {
  --bg: #F5F0E7; --bg-alt: #EDE5D2; --paper: #FAF6ED;
  --ink: #16100E; --ink-soft: #3D3633; --ink-mute: #635C57;
  --accent: #A8351F; --accent-deep: #862719;
  --warm: #7A6447; --line: #C0B69E; --line-soft: #D6CCB3;
}
* { margin:0; padding:0; box-sizing:border-box; }
html { scroll-behavior:smooth; }
body {
  background:var(--bg); color:var(--ink);
  font-family:'Noto Sans JP', sans-serif; font-weight:400; line-height:1.8;
  -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility;
  overflow-x:hidden; font-size:16px;
}
main { position:relative; z-index:1; }

/* ===== マストヘッド ===== */
.masthead {
  border-bottom:1px solid var(--line); padding:1rem 2rem;
  display:flex; justify-content:space-between; align-items:center;
  font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:500;
  font-size:.8rem; letter-spacing:.12em; color:var(--ink-soft); text-transform:uppercase;
}
.masthead a { color:var(--ink-soft); text-decoration:none; transition:color .25s; }
.masthead a:hover { color:var(--accent); }
.masthead .accent-dot { width:5px; height:5px; background:var(--accent); border-radius:50%; display:inline-block; margin-right:.5rem; }
.masthead { flex-wrap:wrap; gap:.7rem 1.2rem; }
.masthead .left { display:flex; gap:1.2rem; align-items:center; flex-wrap:wrap; }
.masthead .brand-link { color:var(--ink); font-weight:700; }
.masthead-nav { display:flex; gap:1.2rem; align-items:center; flex-wrap:wrap; }
.masthead-nav a { color:var(--ink-mute); text-decoration:none; transition:color .25s; }
.masthead-nav a:hover { color:var(--accent); }
@media (max-width:640px){ .masthead-nav{ gap:.9rem; font-size:.72rem; } }
.masthead .right { font-family:'Cormorant Garamond', serif; font-style:italic; letter-spacing:.1em; }

/* ===== HERO ===== */
.hero {
  max-width:1100px; margin:0 auto; padding:4rem 2rem 2.5rem;
}
/* ===== 役割ラベルチップ（蔵／銘柄の区別） ===== */
.role-chip {
  display:inline-block; font-family:'Zen Kaku Gothic Antique', sans-serif;
  font-weight:700; font-size:.7rem; letter-spacing:.18em;
  padding:.16rem .55rem; margin-right:.65rem; vertical-align:middle;
  line-height:1;
}
.role-chip--kura { border:1px solid var(--warm); color:var(--warm); }
.role-chip--brand { background:var(--accent); color:#FAF6ED; border:1px solid var(--accent); }

.hero__brewery {
  font-family:'Shippori Mincho', serif; font-weight:500;
  font-size:1.1rem; color:var(--warm); letter-spacing:.04em; margin-bottom:1.1rem;
  display:flex; align-items:center; flex-wrap:wrap;
}
.hero__brewery a { color:var(--warm); text-decoration:none; border-bottom:1px dotted var(--warm); }
.hero__brewery a:hover { color:var(--accent); border-bottom-color:var(--accent); }
.hero__brewery-loc {
  font-family:'Noto Sans JP', sans-serif; font-weight:400;
  font-size:.82rem; color:var(--ink-mute); letter-spacing:.02em; margin-left:.5rem;
}
.hero__brandrow { margin-bottom:.5rem; }
.hero__name {
  font-family:'Shippori Mincho', serif; font-weight:700;
  font-size:clamp(2.2rem, 6vw, 4rem);
  letter-spacing:.01em; line-height:1.15; color:var(--ink); margin-bottom:1rem;
}
.hero__kana {
  font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:500;
  font-size:.88rem; letter-spacing:.2em; color:var(--ink-soft); margin-bottom:1.5rem;
}
.hero__tagline {
  font-family:'Shippori Mincho', serif; font-weight:500;
  font-size:1.15rem; color:var(--ink); line-height:1.75;
  max-width:780px; margin-bottom:2rem;
}
.hero__flavor {
  border-top:1px solid var(--line); border-bottom:1px solid var(--line);
  padding:1.1rem 0; margin-bottom:1.75rem; max-width:780px;
}
.hero__flavor-label {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.92rem; color:var(--accent); letter-spacing:.08em; margin-bottom:.7rem;
}
.hero__badges { display:flex; flex-wrap:wrap; gap:.55rem; margin-bottom:.5rem; }
.badge {
  font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:700;
  font-size:.75rem; letter-spacing:.12em; padding:.4rem .85rem;
  border:1px solid currentColor;
}
.badge--cat { color:var(--accent); }
.badge--avail { color:var(--warm); }
.badge--filled { color:#fff; background:var(--accent); border-color:var(--accent); }

/* ===== Spec Board (大判) ===== */
.spec-board {
  max-width:1100px; margin:0 auto; padding:0 2rem 2rem;
  display:grid; grid-template-columns:1fr; gap:0;
  border:1px solid var(--line); background:var(--paper);
}
@media (min-width:640px) { .spec-board { grid-template-columns:repeat(3, 1fr); } }
.spec-cell { padding:1.5rem 1.75rem; border-bottom:1px solid var(--line); display:flex; flex-direction:column; justify-content:center; }
@media (min-width:640px) {
  .spec-cell { border-bottom:none; border-right:1px solid var(--line); }
  .spec-cell:last-child { border-right:none; }
}
.spec-cell:last-child { border-bottom:none; }
.spec-cell__label {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.88rem; color:var(--accent); letter-spacing:.1em; margin-bottom:.5rem;
}
.spec-cell__value {
  font-family:'Shippori Mincho', serif; font-weight:700;
  font-size:2rem; color:var(--ink); letter-spacing:.02em; line-height:1.15;
}
.spec-cell__value small {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.55em; color:var(--ink-soft); font-weight:400; margin-left:.3rem;
}
.spec-cell__sub {
  font-family:'Noto Sans JP', sans-serif;
  font-size:.78rem; color:var(--ink-soft); margin-top:.5rem; line-height:1.5;
}

/* ===== Section common ===== */
.section { max-width:1100px; margin:0 auto; padding:0 2rem 4rem; }
.section-meta {
  display:flex; align-items:baseline; gap:1.25rem; margin-bottom:1.5rem;
}
.section-meta__num {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:1.15rem; color:var(--accent); letter-spacing:.05em;
}
.section-meta__label {
  font-family:'Zen Kaku Gothic Antique', sans-serif;
  font-size:.88rem; font-weight:700; letter-spacing:.18em; color:var(--ink);
  text-transform:uppercase;
}
.section-meta__rule { flex:1; height:1px; background:var(--line); }

/* ===== Recipe Table ===== */
.recipe {
  border:1px solid var(--line);
}
.recipe-row {
  display:grid; grid-template-columns:170px 1fr;
  border-bottom:1px solid var(--line); padding:1rem 1.5rem;
  background:var(--bg);
}
.recipe-row:last-child { border-bottom:none; }
.recipe-row:nth-child(even) { background:var(--paper); }
.recipe-row__label {
  font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:700;
  font-size:.82rem; letter-spacing:.12em; color:var(--accent);
  text-transform:uppercase; line-height:1.6;
}
.recipe-row__value {
  font-family:'Shippori Mincho', serif; font-weight:500;
  font-size:1rem; color:var(--ink); line-height:1.65;
}
.recipe-row__value small {
  display:block; font-family:'Noto Sans JP', sans-serif; font-weight:400;
  font-size:.82rem; color:var(--ink-soft); margin-top:.3rem; line-height:1.6;
}
.recipe-row__value.unknown { color:var(--ink-mute); font-style:italic; font-weight:400; }
@media (max-width:640px) {
  .recipe-row { grid-template-columns:1fr; gap:.4rem; }
}

/* ===== How To Enjoy ===== */
.enjoy {
  display:grid; grid-template-columns:1fr; gap:1px; background:var(--line);
  border:1px solid var(--line);
}
@media (min-width:760px) { .enjoy { grid-template-columns:repeat(2, 1fr); } }
.enjoy-cell { background:var(--bg); padding:1.5rem 1.75rem; }
.enjoy-cell__label {
  font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:700;
  font-size:.78rem; letter-spacing:.18em; color:var(--accent);
  text-transform:uppercase; margin-bottom:.5rem;
}
.enjoy-cell__value {
  font-family:'Shippori Mincho', serif; font-weight:500;
  font-size:1.1rem; color:var(--ink); line-height:1.7;
}
.enjoy-cell__value small {
  display:block; font-family:'Noto Sans JP', sans-serif; font-weight:400;
  font-size:.82rem; color:var(--ink-soft); margin-top:.4rem; line-height:1.65;
}

.pairing-list {
  display:flex; flex-wrap:wrap; gap:.5rem; margin-top:.65rem;
}
.pairing-chip {
  font-family:'Shippori Mincho', serif; font-weight:500;
  font-size:.95rem; padding:.4rem .85rem;
  background:var(--paper); border:1px solid var(--line);
  color:var(--ink); letter-spacing:.02em;
}

/* ===== TASTING 3段 ===== */
.tasting-3 {
  display:grid; grid-template-columns:1fr; gap:0;
  border:1px solid var(--line); border-left:4px solid var(--accent);
  background:var(--paper); margin-bottom:1rem;
}
.tasting-row {
  padding:1.4rem 1.75rem;
  border-bottom:1px solid var(--line);
}
.tasting-row:last-child { border-bottom:none; }
.tasting-row__label {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.95rem; color:var(--accent); letter-spacing:.1em; margin-bottom:.45rem;
}
.tasting-row__label strong {
  display:block; font-family:'Shippori Mincho', serif; font-style:normal;
  font-weight:700; font-size:1.05rem; color:var(--ink); letter-spacing:.05em;
}
.tasting-row__text {
  font-family:'Shippori Mincho', serif; font-weight:500;
  font-size:1.05rem; color:var(--ink); line-height:1.95;
}
.tasting-source {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.88rem; color:var(--ink-soft); padding-top:.75rem;
  border-top:1px dotted var(--line); margin-top:1rem;
}
.tasting-source a { color:var(--ink); border-bottom:1px dotted var(--line); text-decoration:none; }
.tasting-source a:hover { color:var(--accent); border-bottom-color:var(--accent); }

/* ===== Flavor Profile (4軸 + 6軸) ===== */
.flavor-wrap {
  display:grid; grid-template-columns:1fr; gap:2rem;
  margin-bottom:2rem;
}
@media (min-width:860px) { .flavor-wrap { grid-template-columns:1.3fr 1fr; } }
.flavor-box {
  background:var(--paper); border:1px solid var(--line);
  padding:1.5rem 1.5rem;
}
.flavor-box__title {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:1rem; color:var(--accent); letter-spacing:.1em; margin-bottom:1rem;
  display:flex; align-items:center; gap:.5rem;
}
.flavor-box__title strong {
  font-family:'Shippori Mincho', serif; font-weight:600;
  color:var(--ink); font-size:1.1rem; letter-spacing:.04em; font-style:normal;
}
.flavor-box svg { display:block; width:100%; height:auto; }
.flavor-box__cap {
  font-family:'Noto Sans JP', sans-serif; font-weight:400;
  font-size:.78rem; color:var(--ink-soft); margin-top:.75rem; line-height:1.6;
  border-top:1px dotted var(--line); padding-top:.75rem;
}
.flavor-tags { display:flex; flex-wrap:wrap; gap:.45rem; }
.flavor-tag {
  font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:500;
  font-size:.85rem; padding:.32rem .75rem; background:var(--bg);
  border:1px solid var(--line); color:var(--ink); letter-spacing:.02em;
}

/* ===== STORY ===== */
.story-block {
  background:var(--bg-alt); padding:2rem 2.25rem;
  border-left:3px solid var(--warm);
}
.story-text {
  font-family:'Shippori Mincho', serif; font-weight:500;
  font-size:1.05rem; color:var(--ink); line-height:1.95; margin-bottom:1rem;
}
.story-source {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.85rem; color:var(--ink-soft);
}
.story-source a { color:var(--ink); border-bottom:1px dotted var(--line); text-decoration:none; }

/* ===== AWARDS ===== */
.awards-list {
  display:flex; flex-direction:column; border:1px solid var(--line);
}
.award-card {
  display:grid; grid-template-columns:auto 1fr; gap:1.2rem;
  padding:1.25rem 1.5rem; border-bottom:1px solid var(--line);
  background:var(--bg); border-left:3px solid var(--accent);
}
.award-card:last-child { border-bottom:none; }
.award-year {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:1.4rem; color:var(--accent); letter-spacing:.05em; min-width:3.5em;
}
.award-title {
  font-family:'Shippori Mincho', serif; font-weight:700;
  font-size:1.05rem; color:var(--ink); line-height:1.5;
}
.award-where {
  font-family:'Noto Sans JP', sans-serif; font-weight:400;
  font-size:.85rem; color:var(--ink-soft); margin-top:.2rem;
}

/* ===== KURA + PURCHASE ===== */
.kura-purchase {
  display:grid; grid-template-columns:1fr; gap:1.5rem;
}
@media (min-width:760px) { .kura-purchase { grid-template-columns:2fr 1fr; } }
.kura-card {
  background:var(--bg-alt); padding:1.75rem 2rem; border:1px solid var(--line);
}
.kura-card__name {
  font-family:'Shippori Mincho', serif; font-weight:700;
  font-size:1.35rem; color:var(--ink); margin-bottom:.3rem;
}
.kura-card__meta {
  font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:500;
  font-size:.85rem; color:var(--ink-soft); letter-spacing:.05em; margin-bottom:1rem;
}
.kura-card__philo {
  font-size:.95rem; color:var(--ink); line-height:1.85; margin-bottom:1rem;
}
.kura-card__link {
  display:inline-block; font-family:'Zen Kaku Gothic Antique', sans-serif;
  font-weight:700; font-size:.85rem; color:var(--accent); letter-spacing:.1em;
  text-transform:uppercase; text-decoration:none;
  border-bottom:1px solid var(--accent); padding-bottom:.15rem;
}
.purchase-card {
  background:var(--ink); color:#F5F0E7; padding:1.75rem 2rem;
  display:flex; flex-direction:column; justify-content:space-between;
}
.purchase-card__label {
  font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:700;
  font-size:.78rem; letter-spacing:.18em; color:#A8351F; margin-bottom:.6rem;
  text-transform:uppercase;
}
.purchase-card__title {
  font-family:'Shippori Mincho', serif; font-weight:700;
  font-size:1.15rem; line-height:1.5; margin-bottom:1.25rem; color:#F5F0E7;
}
.purchase-card__btns {
  display:flex; flex-direction:column; gap:.6rem;
}
.purchase-card__btn {
  display:block; text-align:center; padding:.95rem 1.25rem;
  color:#F5F0E7; text-decoration:none;
  font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:700;
  font-size:.95rem; letter-spacing:.1em;
  transition:filter .25s, transform .15s;
  position:relative;
}
.purchase-card__btn:hover { filter:brightness(1.1); transform:translateY(-1px); }
.purchase-card__btn--rakuten {
  background:linear-gradient(135deg, #BF0000 0%, #C9242E 100%);
}
.purchase-card__btn--amazon {
  background:linear-gradient(135deg, #232F3E 0%, #FF9900 100%);
}
.purchase-card__btn--official {
  background:#16100E; border:1px solid #635C57;
}
.purchase-card__note {
  font-family:'Noto Sans JP', sans-serif; font-weight:400;
  font-size:.72rem; color:#C0B69E; margin-top:.85rem; letter-spacing:.05em;
  text-align:center;
}
.purchase-card__pending {
  font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:500;
  font-size:.92rem; color:#C0B69E; letter-spacing:.08em;
  text-align:center; padding:1.1rem 0; border:1px dashed #635C57;
}

/* ===== SOURCES ===== */
.sources {
  background:var(--bg-alt); padding:1.75rem 2rem;
  font-family:'Zen Kaku Gothic Antique', sans-serif;
}
.sources h4 {
  font-size:.85rem; letter-spacing:.18em; color:var(--ink); font-weight:700;
  margin-bottom:1rem; text-transform:uppercase;
}
.sources ul { list-style:none; display:flex; flex-direction:column; gap:.55rem; }
.sources a {
  font-size:.92rem; color:var(--ink); text-decoration:none; font-weight:500;
  border-bottom:1px dotted var(--line); padding-bottom:.15rem;
  word-break:break-all; transition:color .25s;
}
.sources a:hover { color:var(--accent); border-bottom-color:var(--accent); }
.sources__meta {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.82rem; color:var(--ink-soft); margin-top:1.25rem;
  padding-top:1rem; border-top:1px solid var(--line);
}

/* ===== Glossary ===== */
.glossary {
  border:1px solid var(--line); padding:1.5rem 1.75rem; background:var(--paper);
}
.glossary-item { padding:.9rem 0; border-bottom:1px dotted var(--line); }
.glossary-item:last-child { border-bottom:none; padding-bottom:0; }
.glossary-item dt {
  font-family:'Shippori Mincho', serif; font-weight:700;
  font-size:1rem; color:var(--accent); margin-bottom:.35rem;
}
.glossary-item dd {
  font-size:.92rem; color:var(--ink); line-height:1.75; font-weight:400;
}

/* ===== Divider ===== */
.divider {
  max-width:1100px; margin:3rem auto; padding:0 2rem;
  display:flex; align-items:center; gap:1rem;
}
.divider .rule { flex:1; height:1px; background:var(--line); }
.divider .ornament { width:8px; height:8px; background:var(--accent); transform:rotate(45deg); }
.divider .ornament.outer { width:4px; height:4px; background:var(--warm); }

/* ===== 公式サイト（最下部・控えめ） ===== */
.official-foot {
  max-width:1100px; margin:0 auto; padding:0 2rem 3rem; text-align:center;
}
.official-foot a {
  font-family:'Noto Sans JP', sans-serif; font-weight:400;
  font-size:.85rem; color:var(--ink-mute); letter-spacing:.04em;
  text-decoration:none; border-bottom:1px dotted var(--line); padding-bottom:.2rem;
  transition:color .25s;
}
.official-foot a:hover { color:var(--ink-soft); }

/* ===== Footer ===== */
footer { margin-top:4rem; border-top:1px solid var(--ink); }
.colophon {
  max-width:1100px; margin:0 auto; padding:2rem;
  display:grid; grid-template-columns:1fr; gap:1.5rem;
}
@media (min-width:700px) { .colophon { grid-template-columns:2fr 3fr; } }
.colophon__brand {
  font-family:'Shippori Mincho', serif; font-weight:700;
  font-size:1.5rem; letter-spacing:.02em;
}
.colophon__brand .dot { color:var(--accent); }
.colophon__brand a { color:var(--ink); text-decoration:none; }
.colophon__brand small {
  display:block; font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.8rem; color:var(--ink-soft); margin-top:.25rem;
  font-weight:400; letter-spacing:.08em;
}
.colophon__notes {
  font-family:'Noto Sans JP', sans-serif; font-weight:400;
  font-size:.88rem; color:var(--ink-soft); line-height:1.9; letter-spacing:.02em;
}
.colophon__notes strong { color:var(--accent); font-weight:500; }
.colophon__sep { color:var(--line); margin:0 .5rem; }
"""


def main():
    b = BRAND
    brewery = by_slug(b["brewery_slug"])

    scale4_svg = gen_scale4_svg(b["scale4"])
    radar6_svg = gen_radar6_svg(b["radar6"])

    # アフィリリンク（もしも経由・楽天/Amazon検索）
    rakuten_url = rakuten_search(b["name"])
    amazon_url = amazon_search(b["name"])

    # 購入ボックス（アフィリ未登録時はボタンを出さず「準備中」表示）
    if AFFILIATE_ENABLED:
        purchase_inner = f"""<div class="purchase-card__btns">
            <a class="purchase-card__btn purchase-card__btn--rakuten" href="{rakuten_url}" target="_blank" rel="noopener sponsored">楽天市場で探す →</a>
            <a class="purchase-card__btn purchase-card__btn--amazon" href="{amazon_url}" target="_blank" rel="noopener sponsored">Amazonで探す →</a>
          </div>
          <div class="purchase-card__note">PR ／ アフィリエイトリンクを含みます</div>"""
    else:
        purchase_inner = """<div class="purchase-card__pending">お取り扱い情報は準備中です</div>"""

    # Recipe rows
    recipe_rows = []
    def row(label, val, sub=None, unknown=False):
        cls = " unknown" if unknown else ""
        sub_html = f"<small>{sub}</small>" if sub else ""
        recipe_rows.append(f"""
        <div class="recipe-row">
          <div class="recipe-row__label">{label}</div>
          <div class="recipe-row__value{cls}">{val}{sub_html}</div>
        </div>""")

    row("品目（酒税法）", b["category"])
    row("副原料", "・".join(b["sub_ingredients"]), sub=b.get("sub_ingredients_detail"))
    row("米品種", b["rice_variety"] if b["rice_variety"] != "公式非開示" else "公式非開示", unknown=(b["rice_variety"] == "公式非開示"))
    row("精米歩合", f"{b['rice_polish']}%" if b["rice_polish"] else "公式非開示", unknown=(b["rice_polish"] is None))
    row("酒母", b["shubo"], sub=b.get("shubo_note"))
    row("麹菌", b["koji"] if b["koji"] != "公式非開示" else "公式非開示", unknown=(b["koji"] == "公式非開示"))
    row("酵母", b["yeast"] if b["yeast"] != "公式非開示" else "公式非開示", unknown=(b["yeast"] == "公式非開示"))
    row("仕込水", b["water"] if b["water"] != "公式非開示" else "公式非開示", unknown=(b["water"] == "公式非開示"))
    row("発酵容器", b["vessel"] if b["vessel"] != "公式非開示" else "公式非開示", unknown=(b["vessel"] == "公式非開示"))
    row("火入れ／生酒", "公式非開示" if b["pasteurized"] is None else ("火入れ" if b["pasteurized"] else "生酒"), unknown=(b["pasteurized"] is None))
    row("加水／原酒", "公式非開示" if b["draft"] is None else ("加水" if not b["draft"] else "原酒"), unknown=(b["draft"] is None))
    recipe_html = ''.join(recipe_rows)

    # Pairing chips
    pairing_chips = ''.join(f'<span class="pairing-chip">{p}</span>' for p in b["pairing"])

    # Flavor tags
    flavor_tags_html = ''.join(f'<span class="flavor-tag">{t}</span>' for t in b["flavor_tags"])

    # Awards
    awards_html = ''.join(f"""
        <div class="award-card">
          <div class="award-year">{a["year"]}</div>
          <div>
            <div class="award-title">{a["title"]}</div>
            <div class="award-where">{a["where"]}</div>
          </div>
        </div>""" for a in b["awards"]) if b["awards"] else '<p style="font-size:.92rem; color:var(--ink-soft); padding:.5rem 0">本銘柄単独の受賞情報は現時点で確認できず（蔵全体としての受賞は <a href="../brewery/haccoba.html" style="color:var(--accent)">蔵詳細</a> 参照）</p>'

    # Glossary
    glossary_html = ''.join(f"""
        <div class="glossary-item">
          <dt>{term}</dt>
          <dd>{desc}</dd>
        </div>""" for term, desc in b["glossary"])

    # Category badge
    cat_badge = f'<span class="badge badge--cat">— 酒税法分類：{b["category"]}</span>'
    avail_label = {"online": "通販可", "tokuyaku": "特約店", "rare": "極希少"}.get(b["availability"], "—")
    avail_badge = f'<span class="badge badge--avail">— 入手性：{avail_label}</span>'

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{b['name']} ／ {brewery['name']} — saketto.</title>
<meta name="description" content="{b['tagline'][:120]}">
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@300;400;500&family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<style>{CSS}</style>
{head_extra()}
</head>
<body>
<main>

  <!-- マストヘッド -->
  <div class="masthead">
    <div class="left">
      <a href="../index.html"><span class="accent-dot"></span>SAKETTO</a>
      <a href="../brewery/{b['brewery_slug']}.html">← {brewery['name']}</a>
    </div>
    <div class="right">BRAND SAMPLE V2 — {b['data_updated']}</div>
  </div>

  <!-- HERO -->
  <section class="hero">
    <div class="hero__brewery">
      <span class="role-chip role-chip--kura">蔵</span><a href="../brewery/{b['brewery_slug']}.html">{brewery['name']}</a><span class="hero__brewery-loc">（{brewery['prefecture']}）が醸造</span>
    </div>
    <div class="hero__brandrow"><span class="role-chip role-chip--brand">銘柄</span></div>
    <h1 class="hero__name">{b['name']}</h1>
    <div class="hero__kana">{b['kana']}</div>
    <p class="hero__tagline">{b['tagline']}</p>
    <div class="hero__flavor">
      <div class="hero__flavor-label">— AROMA &amp; FLAVOR ／ 香り・味の印象</div>
      <div class="flavor-tags">{flavor_tags_html}</div>
    </div>
    <div class="hero__badges">{cat_badge}{avail_badge}</div>
  </section>

  <!-- 大判 SPECS -->
  <div class="spec-board">
    <div class="spec-cell">
      <div class="spec-cell__label">— ABV</div>
      <div class="spec-cell__value">{b['abv']}<small>% ALC.</small></div>
      <div class="spec-cell__sub">{b['abv_note']}</div>
    </div>
    <div class="spec-cell">
      <div class="spec-cell__label">— VOLUME</div>
      <div class="spec-cell__value">{b['volume_ml']}<small>ml</small></div>
    </div>
    <div class="spec-cell">
      <div class="spec-cell__label">— PRICE</div>
      <div class="spec-cell__value">¥{b['price']:,}</div>
      <div class="spec-cell__sub">{b['price_note']}</div>
    </div>
  </div>

  <!-- RECIPE -->
  <section class="section" style="padding-top:3rem">
    <div class="section-meta">
      <span class="section-meta__num">No. 01</span>
      <span class="section-meta__label">RECIPE / 仕込み</span>
      <span class="section-meta__rule"></span>
    </div>
    <div class="recipe">{recipe_html}
    </div>
  </section>

  <!-- HOW TO ENJOY -->
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. 02</span>
      <span class="section-meta__label">HOW TO ENJOY / 楽しみ方</span>
      <span class="section-meta__rule"></span>
    </div>
    <div class="enjoy">
      <div class="enjoy-cell">
        <div class="enjoy-cell__label">— TEMPERATURE</div>
        <div class="enjoy-cell__value">{b['serving_temp'] or '公式推奨なし'}</div>
      </div>
      <div class="enjoy-cell">
        <div class="enjoy-cell__label">— GLASS</div>
        <div class="enjoy-cell__value">{b['glass'] or '公式推奨なし'}</div>
      </div>
      <div class="enjoy-cell">
        <div class="enjoy-cell__label">— PRESERVATION</div>
        <div class="enjoy-cell__value">{b['preservation']}<small>開封後の目安: {b['open_days'] or '公式非開示'}</small></div>
      </div>
      <div class="enjoy-cell">
        <div class="enjoy-cell__label">— PAIRING</div>
        <div class="enjoy-cell__value">編集部おすすめ料理
          <div class="pairing-list">{pairing_chips}</div>
        </div>
      </div>
    </div>
  </section>

  <!-- TASTING NOTES 3段 -->
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. 03</span>
      <span class="section-meta__label">TASTING NOTES / 香り・含み香・余韻</span>
      <span class="section-meta__rule"></span>
    </div>
    <div class="tasting-3">
      <div class="tasting-row">
        <div class="tasting-row__label">— NOSE　<strong>香り</strong></div>
        <div class="tasting-row__text">{b['tasting_nose']}</div>
      </div>
      <div class="tasting-row">
        <div class="tasting-row__label">— PALATE　<strong>含み香・味わい</strong></div>
        <div class="tasting-row__text">{b['tasting_palate']}</div>
      </div>
      <div class="tasting-row">
        <div class="tasting-row__label">— FINISH　<strong>余韻</strong></div>
        <div class="tasting-row__text">{b['tasting_finish']}</div>
      </div>
    </div>
  </section>

  <!-- FLAVOR PROFILE -->
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. 04</span>
      <span class="section-meta__label">FLAVOR PROFILE / 味わいの構造</span>
      <span class="section-meta__rule"></span>
    </div>
    <div class="flavor-wrap">
      <div class="flavor-box">
        <div class="flavor-box__title">— STRUCTURE　<strong>4軸構造スケール</strong></div>
        {scale4_svg}
        <div class="flavor-box__cap">蔵の設計意図を構造で示す。Vivino型の4軸。値は編集部初期値（公式テイスティング記述から推定）。社長承認後に各銘柄個別チューニング予定。</div>
      </div>
      <div class="flavor-box">
        <div class="flavor-box__title">— PROFILE　<strong>6軸レーダー</strong></div>
        {radar6_svg}
        <div class="flavor-box__cap">飲み手の印象を6軸で。さけのわ型のスタイル。値は編集部初期値。</div>
      </div>
    </div>
  </section>

  <div class="divider">
    <div class="rule"></div>
    <div class="ornament outer"></div>
    <div class="ornament"></div>
    <div class="ornament outer"></div>
    <div class="rule"></div>
  </div>

  <!-- STORY -->
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. 05</span>
      <span class="section-meta__label">STORY / この銘柄が生まれた背景</span>
      <span class="section-meta__rule"></span>
    </div>
    <div class="story-block">
      <p class="story-text">{b['story']}</p>
    </div>
  </section>

  <!-- AWARDS -->
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. 06</span>
      <span class="section-meta__label">ACCOLADES / 受賞</span>
      <span class="section-meta__rule"></span>
    </div>
    <div class="awards-list">{awards_html}</div>
  </section>

  <!-- KURA + PURCHASE -->
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. 07</span>
      <span class="section-meta__label">KURA & PURCHASE / 蔵元と入手</span>
      <span class="section-meta__rule"></span>
    </div>
    <div class="kura-purchase">
      <div class="kura-card">
        <div class="kura-card__name">{brewery['name']}</div>
        <div class="kura-card__meta">{brewery['prefecture']}・{brewery['city']}　／　創業 {brewery['founded']}</div>
        <p class="kura-card__philo">{brewery['philosophy']}</p>
        <a class="kura-card__link" href="../brewery/{b['brewery_slug']}.html">蔵の詳細を見る →</a>
      </div>
      <div class="purchase-card">
        <div>
          <div class="purchase-card__label">— PURCHASE</div>
          <div class="purchase-card__title">「{b['name']}」を探す</div>
        </div>
        <div>
          {purchase_inner}
        </div>
      </div>
    </div>
  </section>

  <!-- GLOSSARY -->
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. 08</span>
      <span class="section-meta__label">GLOSSARY / 専門用語ミニ解説</span>
      <span class="section-meta__rule"></span>
    </div>
    <dl class="glossary">{glossary_html}
    </dl>
  </section>

  <!-- 公式サイト（情報リンク・控えめ） -->
  <div class="official-foot">
    <a href="{b['official_ec_url']}" target="_blank" rel="noopener">{brewery['name']} 公式サイト（{b['official_ec_url'].split('//')[-1].split('/')[0]}）→</a>
  </div>

  <footer>
    <div class="colophon">
      <div class="colophon__brand">
        <a href="../index.html">saketto<span class="dot">.</span></a>
        <small>— クラフトサケの図鑑</small>
      </div>
      <div class="colophon__notes">
        <strong>準備中</strong><span class="colophon__sep">／</span>
        価格・度数は公式サイトでご確認ください<span class="colophon__sep">／</span>
        20歳未満の飲酒は法律で禁じられています<span class="colophon__sep">／</span>
        PR ／ アフィリエイトリンクを含みます<span class="colophon__sep">／</span>
        © 2026 saketto.
      </div>
    </div>
  </footer>

</main>
</body>
</html>
"""

    OUT.write_text(html, encoding="utf-8")
    print(f"✓ サンプル生成: {OUT}")


if __name__ == "__main__":
    main()

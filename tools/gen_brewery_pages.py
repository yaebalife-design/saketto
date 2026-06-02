# -*- coding: utf-8 -*-
"""saketto / 蔵詳細ページ生成スクリプト

実行:
    cd ツール/saketto_repo/tools && python gen_brewery_pages.py

出力:
    ../brewery/{slug}.html × 24
"""

import os
import sys
import json
import glob
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from breweries_master import BREWERIES
from breweries_brands import BRANDS
from awards import AWARDS
from tasting import TASTING
from brewery_about import about_of, founder_of
from site_common import head_extra, seo_head, breadcrumb, SITE_URL

# brand_data（一次ソース調査済み）を読み込み、製法特徴の抽出に使う
_DETAILS = {}
for _f in glob.glob(os.path.join(os.path.dirname(__file__), "brand_data", "*.json")):
    _d = json.load(open(_f, encoding="utf-8"))
    _DETAILS[_d["brewery"]] = list(_d["brands"].values())

# 製法・特徴キーワード → 表示ラベル
_METHOD_TAGS = [
    ("花酛", "花酛"), ("水もと", "水酛"), ("水酛", "水酛"), ("生酛", "生酛"),
    ("差酛", "差酛"), ("菩提酛", "菩提酛"), ("全麹", "全麹仕込み"), ("木桶", "木桶仕込み"),
    ("ドライホッピング", "ドライホッピング"), ("酵母無添加", "酵母無添加"),
    ("袋吊り", "袋吊り"), ("発芽玄米", "発芽玄米"), ("高温糖化", "高温糖化"),
    ("白麹", "白麹"), ("黄麹", "黄麹"),
]


def method_tags_for(slug):
    """その蔵のbrand_dataから製法・特徴タグを集約（出現順・重複なし）"""
    details = _DETAILS.get(slug, [])
    if not details:
        return []
    blob = ""
    for d in details:
        for k in ("shubo", "koji", "vessel", "flavor_basis", "sub_ingredients_detail", "story"):
            v = d.get(k)
            if v:
                blob += str(v) + " "
    tags = []
    for kw, label in _METHOD_TAGS:
        if kw in blob and label not in tags:
            tags.append(label)
    return tags

REGION_IMG = {
    "東北": "region_tohoku", "関東": "region_kanto", "中部": "region_chubu",
    "関西": "region_kansai", "九州": "region_kyushu", "沖縄": "region_okinawa",
}


REPO_ROOT = Path(__file__).resolve().parent.parent  # saketto_repo/
OUT_DIR = REPO_ROOT / "brewery"
OUT_DIR.mkdir(exist_ok=True)


# ────────────── HTML テンプレート ──────────────

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
  font-family:'Noto Sans JP', sans-serif;
  font-weight:400; line-height:1.8;
  -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility;
  overflow-x:hidden; font-size:16px;
}
body::before {
  content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
  background-image:
    radial-gradient(ellipse 1.5px 2.2px at 18% 22%, rgba(184,73,58,0.035) 60%, transparent 70%),
    radial-gradient(ellipse 1.2px 1.8px at 67% 38%, rgba(139,115,85,0.04) 60%, transparent 70%),
    radial-gradient(ellipse 1.5px 2.3px at 42% 71%, rgba(26,23,23,0.025) 60%, transparent 70%),
    radial-gradient(ellipse 1px 1.5px at 85% 14%, rgba(184,73,58,0.025) 60%, transparent 70%),
    radial-gradient(ellipse 1.2px 1.8px at 8% 88%, rgba(139,115,85,0.035) 60%, transparent 70%);
  background-size: 64px 64px, 96px 96px, 80px 80px, 72px 72px, 88px 88px;
}
main { position:relative; z-index:1; }

/* マストヘッド */
.masthead {
  border-bottom:1px solid var(--line);
  padding:1rem 2rem;
  display:flex; justify-content:space-between; align-items:center;
  font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:500;
  font-size:.8rem; letter-spacing:.12em; color:var(--ink-soft);
  text-transform:uppercase;
}
.masthead a { color:var(--ink-mute); text-decoration:none; transition:color .25s; }
.masthead a:hover { color:var(--accent); }
.masthead .accent-dot { width:5px; height:5px; background:var(--accent); border-radius:50%; display:inline-block; margin-right:.5rem; }
.masthead { flex-wrap:wrap; gap:.7rem 1.2rem; }
.masthead .left { display:flex; gap:1.2rem; align-items:center; flex-wrap:wrap; }
.masthead .brand-link { color:var(--ink); font-weight:700; }
.masthead-nav { display:flex; gap:1.2rem; align-items:center; flex-wrap:wrap; }
.masthead-nav a { color:var(--ink-mute); text-decoration:none; transition:color .25s; }
.masthead-nav a:hover { color:var(--accent); }
@media (max-width:640px){ .masthead-nav{ gap:.9rem; font-size:.72rem; } }

/* HERO */
.hero {
  max-width:1100px; margin:0 auto; padding:5rem 2rem 3rem;
}
/* 役割ラベルチップ（蔵／銘柄の区別） */
.role-chip {
  display:inline-block; font-family:'Zen Kaku Gothic Antique', sans-serif;
  font-weight:700; font-size:.72rem; letter-spacing:.18em;
  padding:.18rem .6rem; vertical-align:middle; line-height:1;
}
.role-chip--kura { border:1px solid var(--warm); color:var(--warm); }
.role-chip--brand { background:var(--accent); color:#FAF6ED; border:1px solid var(--accent); }
.hero__rolerow { display:flex; align-items:center; flex-wrap:wrap; gap:.75rem; margin-bottom:1.1rem; }
.hero__rolenote {
  font-family:'Noto Sans JP', sans-serif; font-weight:400;
  font-size:.85rem; color:var(--ink-mute); letter-spacing:.04em;
}
.hero__eyebrow {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.95rem; color:var(--accent); letter-spacing:.15em;
  margin-bottom:1rem;
}
.hero__name {
  font-family:'Shippori Mincho', serif; font-weight:700;
  font-size:clamp(2.5rem, 6.5vw, 4.5rem);
  letter-spacing:.02em; line-height:1.1; color:var(--ink);
  margin-bottom:.85rem;
}
.hero__kana {
  font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:500;
  font-size:.88rem; letter-spacing:.2em; color:var(--ink-soft);
  margin-bottom:2rem;
}
.hero__meta {
  display:flex; gap:1.75rem; flex-wrap:wrap;
  font-family:'Noto Sans JP', sans-serif; font-weight:500;
  font-size:.95rem; color:var(--ink);
  border-top:1px solid var(--line); border-bottom:1px solid var(--line);
  padding:1.1rem 0; margin-bottom:2.5rem;
}
.hero__meta dt {
  display:inline-block;
  font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:700;
  font-size:.78rem; letter-spacing:.15em; color:var(--accent);
  margin-right:.5rem;
}
.hero__meta dd { display:inline; color:var(--ink); }
.hero__meta a { color:inherit; text-decoration:underline; text-decoration-color:var(--line); text-underline-offset:3px; }
.hero__meta a:hover { text-decoration-color:var(--accent); color:var(--accent); }
.hero__meta .group { display:inline-flex; align-items:baseline; }
.hero__assoc {
  display:inline-block;
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.75rem; color:var(--accent); letter-spacing:.1em;
  border:1px solid var(--accent); padding:.15rem .6rem;
  vertical-align:middle;
}

/* セクション */
.section { max-width:1100px; margin:0 auto; padding:0 2rem 4rem; }
.section-meta {
  display:flex; align-items:baseline; gap:1.25rem; margin-bottom:2rem;
}
.section-meta__num {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:1.05rem; color:var(--accent); letter-spacing:.1em;
}
.section-meta__label {
  font-family:'Zen Kaku Gothic Antique', sans-serif;
  font-size:.7rem; font-weight:700; letter-spacing:.35em; color:var(--ink);
  text-transform:uppercase;
}
.section-meta__rule { flex:1; height:1px; background:var(--line); }

/* 哲学・特徴 */
.story {
  font-family:'Shippori Mincho', serif;
  font-size:1.2rem; font-weight:500; line-height:1.95; color:var(--ink);
  border-left:3px solid var(--accent); padding-left:1.5rem;
  margin-bottom:1.5rem;
}
.features {
  font-size:.95rem; color:var(--ink-mute); line-height:1.85;
  padding-left:1.5rem; font-weight:400; margin-top:1.5rem;
}
.features::before { content:"特徴 ─ "; color:var(--accent); font-family:'Zen Kaku Gothic Antique',sans-serif; font-weight:700; font-size:.82rem; letter-spacing:.08em; }
.about-body {
  font-family:'Shippori Mincho', serif; font-weight:400;
  font-size:1.06rem; color:var(--ink); line-height:2.0;
  margin-top:1.6rem;
}
/* 蔵のファクトシート */
.factsheet { border:1px solid var(--line); margin-top:1.9rem; }
.fact-row { display:grid; grid-template-columns:140px 1fr; border-bottom:1px solid var(--line); padding:.9rem 1.5rem; background:var(--bg); }
.fact-row:last-child { border-bottom:none; }
.fact-row:nth-child(even) { background:var(--paper); }
.fact-row__label { font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:700; font-size:.76rem; letter-spacing:.12em; color:var(--accent); text-transform:uppercase; line-height:1.9; }
.fact-row__value { font-family:'Shippori Mincho', serif; font-weight:500; font-size:1rem; color:var(--ink); line-height:1.7; }
.fact-row__value a { color:var(--accent); text-decoration:none; border-bottom:1px dotted var(--accent); }
.fact-row__value small { display:block; font-family:'Noto Sans JP',sans-serif; font-weight:400; font-size:.82rem; color:var(--ink-soft); margin-top:.2rem; }
.fact-tags { display:flex; flex-wrap:wrap; gap:.4rem; }
.fact-tag { font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:500; font-size:.8rem; color:var(--ink-soft); border:1px solid var(--line); background:var(--paper); padding:.22rem .65rem; letter-spacing:.02em; }
@media (max-width:600px) { .fact-row { grid-template-columns:1fr; gap:.35rem; } }

/* 銘柄カード */
.brands { display:flex; flex-direction:column; border:1px solid var(--line); }
.brand-card { background:var(--bg); padding:1.5rem 1.5rem; display:grid; grid-template-columns:1fr auto; gap:1rem 2rem; transition:background .4s, border-left-color .4s, padding-left .3s; border-bottom:1px solid var(--line); border-left:4px solid transparent; scroll-margin-top:60px; text-decoration:none; color:inherit; }
.brand-card:hover { background:var(--paper); padding-left:2rem; }
.brand-card:last-child { border-bottom:none; }
.brand-card:target {
  background:var(--paper);
  border-left:4px solid var(--accent);
  animation:highlight 2s ease-out;
}
@keyframes highlight {
  0% { background:rgba(168,53,31,.18); }
  100% { background:var(--paper); }
}
.brand-card:hover { background:var(--paper); }
@media (min-width:760px) { .brand-card { grid-template-columns:1.4fr 1fr auto; padding:1.5rem 2rem; } }

.brand-card__main h3 {
  font-family:'Shippori Mincho', serif; font-weight:700;
  font-size:1.25rem; letter-spacing:.02em; color:var(--ink);
  margin-bottom:.5rem; line-height:1.45;
}
.brand-card__chip {
  font-size:.6rem; letter-spacing:.14em; padding:.12rem .4rem;
  margin-right:.6rem; vertical-align:middle; position:relative; top:-2px;
}
.brand-card__note {
  font-size:.92rem; color:var(--ink-soft); line-height:1.75;
  font-weight:400;
}
.brand-card__specs {
  display:flex; gap:.45rem; flex-wrap:wrap; align-items:flex-start;
}
.spec-pill {
  font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:500;
  font-size:.82rem; letter-spacing:.02em; color:var(--ink-soft);
  background:var(--bg-alt); padding:.28rem .7rem; border-radius:0;
}
.spec-pill.accent { color:var(--accent); background:transparent; border:1px solid var(--accent); }
.spec-pill.warm { color:var(--warm); background:transparent; border:1px solid var(--warm); }
.brand-card__price {
  font-family:'Shippori Mincho', serif; font-weight:700;
  font-size:1.1rem; color:var(--ink); white-space:nowrap; align-self:flex-start;
}
.brand-card__price small {
  display:block; font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.78rem; color:var(--ink-soft); margin-top:.2rem; font-weight:400;
  letter-spacing:.03em;
}

.no-brands {
  font-family:'Shippori Mincho', serif;
  font-size:.95rem; color:var(--ink-soft); padding:2rem 0; text-align:center;
  border-top:1px solid var(--line); border-bottom:1px solid var(--line);
}

/* 出典 */
.sources {
  background:var(--bg-alt); padding:2rem; font-family:'Zen Kaku Gothic Antique', sans-serif;
}
.sources h4 {
  font-size:.85rem; letter-spacing:.18em; color:var(--ink); font-weight:700;
  margin-bottom:1rem; text-transform:uppercase;
}
.sources ul { list-style:none; display:flex; flex-direction:column; gap:.6rem; }
.sources a {
  font-size:.95rem; color:var(--ink); text-decoration:none; font-weight:500;
  border-bottom:1px dotted var(--line); padding-bottom:.2rem; transition:color .25s;
  word-break:break-all;
}
.sources a:hover { color:var(--accent); border-bottom-color:var(--accent); }

/* 区切り */
.divider {
  max-width:1100px; margin:4rem auto;
  padding:0 2rem; display:flex; align-items:center; gap:1rem;
}
.divider .rule { flex:1; height:1px; background:var(--line); }
.divider .ornament { width:8px; height:8px; background:var(--accent); transform:rotate(45deg); }
.divider .ornament.outer { width:4px; height:4px; background:var(--warm); }

/* ナビゲーション (前へ・次へ) */
.nav-prev-next {
  max-width:1100px; margin:0 auto; padding:2rem;
  display:flex; justify-content:space-between; gap:1rem;
  font-family:'Shippori Mincho', serif;
}
.nav-prev-next a {
  color:var(--ink); text-decoration:none; padding:1rem 0;
  border-top:1px solid var(--line);
  flex:1; max-width:48%; transition:color .25s, border-color .25s;
  position:relative;
}
.nav-prev-next a:hover { color:var(--accent); border-top-color:var(--accent); }
.nav-prev-next a small {
  display:block; font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.85rem; color:var(--ink-soft); letter-spacing:.05em; margin-bottom:.4rem;
}
.nav-prev-next .next { text-align:right; margin-left:auto; }

/* フッター */
footer { margin-top:5rem; border-top:1px solid var(--ink); position:relative; z-index:1; }
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
.colophon__notes a { color:var(--warm); text-decoration:none; }
.colophon__notes a:hover { color:var(--accent); }
.colophon__sep { color:var(--line); margin:0 .5rem; }

/* 地域バナー */
.region-banner {
  max-width:1100px; margin:0 auto; padding:1rem 2rem 0;
}
.region-banner__wrap {
  position:relative; overflow:hidden; border:1px solid var(--line);
}
.region-banner img {
  display:block; width:100%; height:auto; max-height:260px;
  object-fit:cover; filter:contrast(.98) saturate(.95);
}
.region-banner__cap {
  position:absolute; bottom:.5rem; right:.75rem;
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.78rem; color:rgba(255,255,255,0.94); letter-spacing:.08em;
  background:rgba(22,16,14,0.5); padding:.25rem .65rem;
}

/* 受賞・メディアセクション */
.acc-list {
  display:flex; flex-direction:column; border:1px solid var(--line);
  margin-bottom:1rem;
}
.acc-card {
  background:var(--bg); padding:1.25rem 1.5rem;
  display:grid; grid-template-columns:auto 1fr auto; gap:1rem;
  align-items:center;
  border-bottom:1px solid var(--line);
  transition:background .3s;
}
.acc-card:last-child { border-bottom:none; }
.acc-card:hover { background:var(--paper); }
.acc-card--award { border-left:3px solid var(--accent); }
.acc-card--global { border-left:3px solid var(--warm); }
.acc-card--media { border-left:3px solid var(--line); }
.acc-type {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.85rem; color:var(--accent); letter-spacing:.08em;
  min-width:5em;
}
.acc-type.warm { color:var(--warm); }
.acc-type.mute { color:var(--ink-soft); }
.acc-title {
  font-family:'Shippori Mincho', serif; font-weight:700;
  font-size:1.05rem; color:var(--ink); line-height:1.45;
}
.acc-brand {
  font-family:'Noto Sans JP', sans-serif; font-weight:400;
  font-size:.88rem; color:var(--ink-soft); margin-top:.25rem;
}
.acc-year {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:1.05rem; color:var(--ink-soft); letter-spacing:.05em;
}
@media (max-width:640px) {
  .acc-card { grid-template-columns:1fr; gap:.4rem; }
  .acc-year { text-align:left; }
}

/* テイスティングセクション */
.tasting-list {
  display:flex; flex-direction:column; border:1px solid var(--line);
}
.tasting-card {
  background:var(--bg); padding:1.5rem 1.75rem;
  border-bottom:1px solid var(--line);
}
.tasting-card:last-child { border-bottom:none; }
.tasting-brand {
  font-family:'Shippori Mincho', serif; font-weight:700;
  font-size:1.15rem; margin-bottom:.85rem; color:var(--ink);
  letter-spacing:.02em;
}
.tasting-notes {
  font-size:1rem; color:var(--ink); line-height:1.95; margin-bottom:1rem;
  font-weight:400;
}
.tasting-meta {
  display:flex; flex-wrap:wrap; gap:.4rem 1.2rem;
  font-size:.88rem; color:var(--ink-soft); margin-bottom:.6rem;
}
.tasting-meta__row { display:inline-flex; align-items:baseline; }
.tasting-meta strong {
  color:var(--accent); font-weight:700; margin-right:.5rem;
  font-family:'Zen Kaku Gothic Antique', sans-serif;
  font-size:.78rem; letter-spacing:.1em;
  text-transform:uppercase;
}
.tasting-source {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.85rem; color:var(--ink-mute); margin-top:.6rem;
  padding-top:.6rem; border-top:1px dotted var(--line);
}
.tasting-source a {
  color:var(--ink-soft); text-decoration:none;
  border-bottom:1px dotted var(--line);
}
.tasting-source a:hover { color:var(--accent); border-bottom-color:var(--accent); }
"""


HEAD = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} — saketto.</title>
<meta name="description" content="{name}（{prefecture}・{city}）。{philosophy_short}">
{seo}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@300;400;500&family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<style>{css}</style>
{head_extra}
</head>
<body>
<main>
"""


def render_brand_card(brand, idx=0, brewery_slug=""):
    specs = []
    if brand.get("abv") is not None:
        specs.append(f'<span class="spec-pill accent">ABV {brand["abv"]}%</span>')
    if brand.get("volume_ml") is not None:
        specs.append(f'<span class="spec-pill warm">{brand["volume_ml"]}ml</span>')
    for ing in brand.get("sub_ingredients") or []:
        specs.append(f'<span class="spec-pill">{ing}</span>')

    specs_html = ' '.join(specs) if specs else \
        '<span class="spec-pill">公式非開示</span>'

    if brand.get("price") is not None:
        price_html = f'<div class="brand-card__price">¥{brand["price"]:,}<small>参考 2026.05.30</small></div>'
    else:
        price_html = f'<div class="brand-card__price"><small>市場実勢</small></div>'

    note = brand.get("note", "")
    note_html = f'<p class="brand-card__note">{note}</p>' if note else ''

    href = f"../brand/{brewery_slug}-{idx}.html" if brewery_slug else "#"
    return f"""
      <a class="brand-card" href="{href}" id="b{idx}">
        <div class="brand-card__main">
          <h3><span class="role-chip role-chip--brand brand-card__chip">銘柄</span>{brand['name']}</h3>
          {note_html}
        </div>
        <div class="brand-card__specs">{specs_html}</div>
        {price_html}
      </a>"""


def render(brewery, index, prev_brewery, next_brewery):
    n = index + 1
    total = len(BREWERIES)
    brands = BRANDS.get(brewery["slug"], [])

    philosophy_short = brewery.get("philosophy", "")[:120].replace('"', "'")
    about_text = about_of(brewery["slug"]) or ""

    # ── ファクトシート（蔵のデータ） ──
    slug = brewery["slug"]
    fact_rows = []

    def fact(label, value):
        if value:
            fact_rows.append(f'<div class="fact-row"><div class="fact-row__label">{label}</div><div class="fact-row__value">{value}</div></div>')

    fact("所在地", f'{brewery["prefecture"]}・{brewery["city"]}')
    fact("創業", (f'{brewery["founded"]}年' if str(brewery.get("founded", "")).isdigit() else brewery.get("founded")) if brewery.get("founded") else None)
    fact("代表者", founder_of(slug))
    fact("協会", "クラフトサケ協会 加盟" if brewery.get("association") else "非加盟（独立系）")
    fact("収録銘柄", f'{len(brands)} 銘柄' if brands else None)

    subs = []
    for br in brands:
        for ing in (br.get("sub_ingredients") or []):
            base = ing.split("（")[0].strip()
            if base and base != "米のみ" and base not in subs:
                subs.append(base)
    if not subs and brands:
        subs = ["米のみ（副原料を使わない純米仕込み）"]
    fact("主な副原料", "・".join(subs[:8]) if subs else None)

    mtags = method_tags_for(slug)
    if mtags:
        tags_html = '<div class="fact-tags">' + "".join(f'<span class="fact-tag">{t}</span>' for t in mtags) + '</div>'
        fact("製法・特徴", tags_html)

    if brewery.get("official_url"):
        host = brewery["official_url"].split("//")[-1].split("/")[0]
        fact("公式サイト", f'<a href="{brewery["official_url"]}" target="_blank" rel="noopener">{host}</a>')

    factsheet_html = ('<div class="factsheet">' + "".join(fact_rows) + '</div>') if fact_rows else ''

    assoc_html = '<span class="hero__assoc">CRAFTSAKE ASSOC.</span>' \
        if brewery.get("association") else ''

    prev_html = ""
    if prev_brewery:
        prev_html = f'<a href="{prev_brewery["slug"]}.html"><small>← Prev. No. {(index):02d}</small>{prev_brewery["name"]}</a>'
    else:
        prev_html = '<span></span>'

    next_html = ""
    if next_brewery:
        next_html = f'<a class="next" href="{next_brewery["slug"]}.html"><small>Next No. {(index+2):02d} →</small>{next_brewery["name"]}</a>'
    else:
        next_html = '<span></span>'

    brand_cards_html = ''.join(render_brand_card(b, i, brewery["slug"]) for i, b in enumerate(brands))
    if not brands:
        brand_cards_html = '<div class="no-brands">銘柄情報は調査中です</div>'

    # 受賞・メディア
    brewery_awards = AWARDS.get(brewery["slug"], [])
    awards_cards = []
    extra_sources = []
    for it in brewery_awards:
        typ = it["type"]
        if typ == "media":
            continue  # メディア露出は掲載しない（キリがなく格が弱いため）
        label = {"award": "AWARD", "global": "GLOBAL"}.get(typ, "")
        cls = {"award": "award", "global": "global"}.get(typ, "")
        type_cls = {"award": "", "global": " warm"}.get(typ, "")
        year_html = f'<div class="acc-year">{it["year"]}</div>' if it.get("year") else '<div class="acc-year">—</div>'
        brand_html = f'<div class="acc-brand">{it["brand"]}</div>' if it.get("brand") else ''
        awards_cards.append(f"""
      <div class="acc-card acc-card--{cls}">
        <div class="acc-type{type_cls}">— {label}</div>
        <div><div class="acc-title">{it["title"]}</div>{brand_html}</div>
        {year_html}
      </div>""")
        if it.get("source"):
            extra_sources.append(it["source"])
    awards_html_block = '<div class="acc-list">' + ''.join(awards_cards) + '</div>' if awards_cards else ''

    # テイスティング
    brewery_tasting = TASTING.get(brewery["slug"], [])
    tasting_cards = []
    for t in brewery_tasting:
        meta_rows = []
        if t.get("temp"):
            meta_rows.append(f'<span class="tasting-meta__row"><strong>温度</strong>{t["temp"]}</span>')
        if t.get("pairing"):
            meta_rows.append(f'<span class="tasting-meta__row"><strong>ペアリング</strong>{t["pairing"]}</span>')
        meta_html = f'<div class="tasting-meta">{"".join(meta_rows)}</div>' if meta_rows else ''
        src_html = (
            f'<div class="tasting-source">出典：<a href="{t["source_url"]}" target="_blank" rel="noopener">{t.get("source_name","出典")}</a></div>'
            if t.get("source_url") else ''
        )
        tasting_cards.append(f"""
      <div class="tasting-card">
        <div class="tasting-brand">{t["brand"]}</div>
        <div class="tasting-notes">{t["notes"]}</div>
        {meta_html}
        {src_html}
      </div>""")
        if t.get("source_url"):
            extra_sources.append(t["source_url"])
    tasting_html_block = '<div class="tasting-list">' + ''.join(tasting_cards) + '</div>' if tasting_cards else ''

    # セクション番号の動的計算
    section_n = 3
    awards_section_num = None
    tasting_section_num = None
    if awards_html_block:
        awards_section_num = section_n
        section_n += 1
    if tasting_html_block:
        tasting_section_num = section_n
        section_n += 1
    sources_section_num = section_n

    # 地域バナー
    region_img_name = REGION_IMG.get(brewery["region"], "")
    region_banner = (
        f'<figure class="region-banner"><div class="region-banner__wrap">'
        f'<img src="../assets/images/{region_img_name}.png" alt="" loading="lazy">'
        f'<span class="region-banner__cap">{brewery["region"]}</span>'
        f'</div></figure>'
    ) if region_img_name else ''

    # 出典 - 公式 + 受賞/テイスティングの出典
    src_links = [f'<li><a href="{brewery["official_url"]}" target="_blank" rel="noopener">{brewery["official_url"]}</a></li>']
    seen = set([brewery["official_url"]])
    for u in extra_sources:
        if u and u not in seen:
            src_links.append(f'<li><a href="{u}" target="_blank" rel="noopener">{u}</a></li>')
            seen.add(u)
    sources_html = ''.join(src_links)

    awards_section = f"""
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. {awards_section_num:02d}</span>
      <span class="section-meta__label">ACCOLADES & GLOBAL</span>
      <span class="section-meta__rule"></span>
    </div>
    {awards_html_block}
  </section>""" if awards_section_num else ''

    tasting_section = f"""
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. {tasting_section_num:02d}</span>
      <span class="section-meta__label">TASTING NOTES / {len(brewery_tasting)} 銘柄</span>
      <span class="section-meta__rule"></span>
    </div>
    {tasting_html_block}
  </section>""" if tasting_section_num else ''

    _path = f"/brewery/{brewery['slug']}.html"
    _bdesc = f"{brewery['name']}（{brewery['prefecture']}・{brewery['city']}）。{philosophy_short}"
    _org = {"@context": "https://schema.org/", "@type": ["Brewery", "LocalBusiness"],
            "@id": SITE_URL + _path + "#brewery",
            "name": brewery["name"],
            "address": {"@type": "PostalAddress", "addressRegion": brewery["prefecture"],
                        "addressLocality": brewery["city"], "addressCountry": "JP"},
            "url": SITE_URL + _path,
            "description": philosophy_short}
    if brewery.get("official_url"):
        _org["sameAs"] = [brewery["official_url"]]
    seo = seo_head(_path, brewery["name"], _bdesc, og_type="website", jsonld=[
        _org,
        breadcrumb([("トップ", "/"), (brewery["name"], _path)]),
    ])
    html = HEAD.format(name=brewery["name"], prefecture=brewery["prefecture"],
                       city=brewery["city"], philosophy_short=philosophy_short,
                       css=CSS, head_extra=head_extra(), seo=seo)

    html += f"""
  <div class="masthead">
    <div class="left">
      <a class="brand-link" href="../index.html"><span class="accent-dot"></span>SAKETTO</a>
      <span>BREWERY No. {n:02d} / {total}</span>
    </div>
    <nav class="masthead-nav" aria-label="ナビ">
      <a href="../subingredients/">副原料</a>
      <a href="../index.html#breweries">蔵</a>
      <a href="../region/">地域</a>
      <a href="../genre/">ジャンル</a>
      <a href="../guide/">読みもの</a>
    </nav>
  </div>

  {region_banner}

  <section class="hero">
    <div class="hero__rolerow">
      <span class="role-chip role-chip--kura">蔵</span>
      <span class="hero__rolenote">BREWERY No. {n:02d} / {total} ・ {brewery["prefecture"]}の醸造所（造り手）</span>
    </div>
    <h1 class="hero__name">{brewery["name"]}</h1>
    <div class="hero__kana">{brewery["name_kana"]}</div>
    <dl class="hero__meta">
      <span class="group"><dt>所在</dt><dd>{brewery["prefecture"]}・{brewery["city"]}</dd></span>
      <span class="group"><dt>創業</dt><dd>{brewery["founded"]}</dd></span>
      <span class="group"><dt>地域</dt><dd>{brewery["region"]}</dd></span>
      <span class="group"><dt>公式</dt><dd><a href="{brewery["official_url"]}" target="_blank" rel="noopener">サイトを見る</a></dd></span>
      {('<span class="group">' + assoc_html + '</span>') if assoc_html else ''}
    </dl>
  </section>

  <section class="section" style="padding-top:3rem">
    <div class="section-meta">
      <span class="section-meta__num">No. 01</span>
      <span class="section-meta__label">ABOUT / この蔵について</span>
      <span class="section-meta__rule"></span>
    </div>
    <p class="story">{brewery["philosophy"]}</p>
    {(f'<p class="about-body">{about_text}</p>') if about_text else ''}
    {factsheet_html}
    <p class="features">{brewery["features"]}</p>
  </section>

  <div class="divider">
    <div class="rule"></div>
    <div class="ornament outer"></div>
    <div class="ornament"></div>
    <div class="ornament outer"></div>
    <div class="rule"></div>
  </div>

  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. 02</span>
      <span class="section-meta__label">BRANDS / {len(brands)} 銘柄</span>
      <span class="section-meta__rule"></span>
    </div>
    <div class="brands">{brand_cards_html}
    </div>
  </section>

  {awards_section}

  <nav class="nav-prev-next">
    {prev_html}
    {next_html}
  </nav>

  <footer>
    <div class="colophon">
      <div class="colophon__brand">
        <a href="../index.html">saketto<span class="dot">.</span></a>
        <small>— クラフトサケの図鑑</small>
      </div>
      <div class="colophon__notes">
        <a href="/about.html">運営者情報</a><span class="colophon__sep">／</span>
        <a href="/privacy.html">プライバシーポリシー</a><span class="colophon__sep">／</span>
        <a href="/disclaimer.html">免責事項・広告表記</a><span class="colophon__sep">／</span>
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
    return html


def main():
    count = 0
    for i, brewery in enumerate(BREWERIES):
        prev_b = BREWERIES[i - 1] if i > 0 else None
        next_b = BREWERIES[i + 1] if i < len(BREWERIES) - 1 else None
        html = render(brewery, i, prev_b, next_b)
        out_path = OUT_DIR / f'{brewery["slug"]}.html'
        out_path.write_text(html, encoding="utf-8")
        count += 1
        print(f"  {brewery['slug']:30s}  {brewery['name']}")
    print(f"\n✓ 生成完了: {count}件 ({OUT_DIR})")


if __name__ == "__main__":
    main()

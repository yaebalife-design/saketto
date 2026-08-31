# -*- coding: utf-8 -*-
"""saketto / 逆引きハブページ生成スクリプト

副原料軸・地域軸・ジャンル軸＋ふるさと納税・受賞の5ハブページを生成する。
実行: cd ツール/saketto_repo/tools && python gen_axes_pages.py
"""

import os
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from breweries_master import BREWERIES, REGIONS, by_slug
from breweries_brands import BRANDS
from awards import AWARDS
from urllib.parse import quote

from furusato_data import FURUSATO, PORTAL_NAMES
from moshimo_link import rakuten_url, rakuten_search
from site_common import head_extra, seo_head, breadcrumb, website_node, SITE_URL, pr_notice


REPO_ROOT = Path(__file__).resolve().parent.parent  # saketto_repo/


# ────────────── 共通CSS（簡易・蔵詳細と同系統） ──────────────

CSS = """
:root {
  --bg: #F5F0E7; --bg-alt: #EDE5D2; --paper: #FAF6ED;
  --ink: #16100E; --ink-soft: #3D3633; --ink-mute: #635C57;
  --accent: #A8351F; --accent-deep: #862719;
  --warm: #7A6447; --line: #C0B69E; --line-soft: #D6CCB3;
}
* { margin:0; padding:0; box-sizing:border-box; }
html { scroll-behavior:smooth; }
a:focus-visible, button:focus-visible { outline:2px solid var(--accent); outline-offset:2px; }
body {
  background:var(--bg); color:var(--ink);
  font-family:'Noto Sans JP', sans-serif; font-weight:400;
  line-height:1.8; -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility;
  overflow-x:hidden; font-size:16px;
}
body::before {
  content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
  background-image:
    radial-gradient(ellipse 1.5px 2.2px at 18% 22%, rgba(184,73,58,0.035) 60%, transparent 70%),
    radial-gradient(ellipse 1.2px 1.8px at 67% 38%, rgba(139,115,85,0.04) 60%, transparent 70%),
    radial-gradient(ellipse 1.5px 2.3px at 42% 71%, rgba(26,23,23,0.025) 60%, transparent 70%);
  background-size: 64px 64px, 96px 96px, 80px 80px;
}
main { position:relative; z-index:1; }

.masthead {
  border-bottom:1px solid var(--line); padding:1rem 2rem;
  display:flex; justify-content:space-between; align-items:center;
  font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:500;
  font-size:.8rem; letter-spacing:.12em; color:var(--ink-soft); text-transform:uppercase;
}
.masthead a { color:var(--ink-mute); text-decoration:none; transition:color .25s; }
.masthead a:hover { color:var(--accent); }
.masthead .accent-dot { width:5px; height:5px; background:var(--accent); border-radius:50%; display:inline-block; margin-right:.5rem; }
.masthead { flex-wrap:wrap; gap:.7rem 1.2rem; }
.masthead .left { display:flex; gap:1.2rem; align-items:center; flex-wrap:wrap; }
.masthead .brand-link { color:var(--ink); font-weight:700; }
.masthead-nav { display:flex; gap:1.2rem; align-items:center; flex-wrap:wrap; }
.masthead-nav a { color:var(--ink-mute); text-decoration:none; transition:color .25s; padding:.45rem .25rem; margin:-.45rem -.25rem; }
.masthead-nav a:hover { color:var(--accent); }
@media (max-width:640px){ .masthead-nav{ gap:.9rem; font-size:.72rem; } }

.hero {
  max-width:1100px; margin:0 auto; padding:5rem 2rem 3rem;
}
.hero__eyebrow {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.95rem; color:var(--accent); letter-spacing:.15em;
  margin-bottom:1rem;
}
.hero__title {
  font-family:'Shippori Mincho', serif; font-weight:700;
  font-size:clamp(2.5rem, 6vw, 4rem);
  letter-spacing:.02em; line-height:1.2; color:var(--ink);
  margin-bottom:1rem;
}
.hero__title .accent { color:var(--accent); }
.hero__lede {
  font-size:1.05rem; color:var(--ink-soft); max-width:680px;
  border-left:3px solid var(--accent); padding-left:1.5rem; line-height:1.9;
  font-weight:400;
}
.hero__guide {
  font-family:'Zen Kaku Gothic Antique', sans-serif;
  font-size:.92rem; color:var(--ink-mute); max-width:680px;
  margin-top:1.6rem; line-height:2.1; letter-spacing:.02em; font-weight:400;
}
.hero__guide a { color:var(--accent); text-decoration:none; border-bottom:1px solid var(--accent); padding-bottom:1px; }
.hero__guide a:hover { color:var(--accent-deep); border-color:var(--accent-deep); }

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
.section-meta__count {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:1rem; color:var(--ink-soft); letter-spacing:.05em;
}
.section-meta__rule { flex:1; height:1px; background:var(--line); }

.cat-title {
  font-family:'Shippori Mincho', serif; font-weight:700;
  font-size:1.65rem; letter-spacing:.02em; color:var(--ink);
  margin-bottom:.6rem;
}
.cat-title .accent { color:var(--accent); }
.cat-desc {
  font-size:.98rem; color:var(--ink-soft); margin-bottom:1.5rem; line-height:1.8;
  font-weight:400;
}

.entries {
  display:flex; flex-direction:column;
  border:1px solid var(--line);
  margin-bottom:3rem;
}
.entry {
  background:var(--bg); padding:1.1rem 1.5rem;
  display:grid; grid-template-columns:1fr; gap:.4rem;
  transition:background .3s;
  text-decoration:none; color:var(--ink);
  border-bottom:1px solid var(--line);
}
.entry:last-child { border-bottom:none; }
@media (min-width:760px) {
  .entry { grid-template-columns:1.5fr 1fr 1fr; align-items:center; gap:1rem; }
}
.entry:hover { background:var(--paper); }
.entry__brand {
  font-family:'Shippori Mincho', serif; font-weight: 700;
  font-size:1.08rem; color:var(--ink); line-height:1.5;
}
.entry__brewery {
  font-family:'Noto Sans JP', sans-serif; font-weight:400;
  font-size:.88rem; color:var(--ink-soft); letter-spacing:.02em;
  margin-top:.15rem;
}
.entry__brewery::before { content:"— "; color:var(--accent); }
.entry__specs { display:flex; gap:.4rem; flex-wrap:wrap; }
.spec-pill {
  font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:500;
  font-size:.78rem; letter-spacing:.02em; color:var(--ink-soft);
  background:var(--bg-alt); padding:.25rem .65rem;
}
.spec-pill.accent { color:var(--accent); background:transparent; border:1px solid var(--accent); }
.spec-pill.warm { color:var(--warm); background:transparent; border:1px solid var(--warm); }



/* ふるさと納税の行（行全体リンクをやめ、蔵名とポータルを個別リンクに） */
.entry--furusato { cursor:default; }
.entry--furusato:hover { background:var(--bg); }
.entry__brand a { color:var(--ink); text-decoration:none; border-bottom:1px solid transparent; }
.entry__brand a:hover { color:var(--accent); border-bottom-color:var(--accent); }
a.spec-pill.portal-link { text-decoration:none; display:inline-flex; align-items:center;
  min-height:36px; transition:background .2s,color .2s; }
a.spec-pill.portal-link:hover { background:var(--accent); color:var(--paper); border-color:var(--accent); }

.brewery-cell { display:flex; flex-direction:column; border-bottom:1px solid var(--line); }
@media (min-width:600px) {
  .brewery-cell { border-right:1px solid var(--line); }
  .brewery-cell:nth-child(2n) { border-right:none; }
}
.brewery-cell .brewery-card { border-bottom:none; border-right:none; flex:1; }
.card-picks { display:flex; flex-wrap:wrap; align-items:baseline; gap:.4rem .55rem;
  padding:0 1.5rem 1.1rem; }
.card-picks__label { font-family:'Cormorant Garamond',serif; font-style:italic;
  font-size:.72rem; color:var(--ink-mute); letter-spacing:.08em; }
.card-picks__item { font-family:'Zen Kaku Gothic Antique',sans-serif; font-size:.82rem;
  color:var(--ink); text-decoration:none; border-bottom:1px solid var(--line);
  padding-bottom:1px; }
.card-picks__item:hover { color:var(--accent); border-bottom-color:var(--accent); }
.card-picks__more { font-size:.78rem; color:var(--ink-mute); }
@media (max-width:640px){ .card-picks { padding:0 1.25rem 1rem; } }

.brewery-grid {
  display:grid; grid-template-columns:1fr; gap:0;
  border-top:1px solid var(--line);
}
@media (min-width:600px) { .brewery-grid { grid-template-columns:repeat(2, 1fr); } }
.brewery-card {
  padding:1.5rem; border-bottom:1px solid var(--line);
  background:var(--bg); text-decoration:none; color:var(--ink);
  display:flex; flex-direction:column; gap:.4rem;
  transition:background .3s, padding-left .3s;
}
@media (min-width:600px) {
  .brewery-card { border-right:1px solid var(--line); }
  .brewery-card:nth-child(2n) { border-right:none; }
}
.brewery-card:hover { background:var(--paper); padding-left:1.75rem; }
.brewery-card__num {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.85rem; color:var(--accent); letter-spacing:.05em;
}
.brewery-card__name {
  font-family:'Shippori Mincho', serif; font-weight:700;
  font-size:1.25rem; color:var(--ink); letter-spacing:.02em;
}
.brewery-card__meta {
  font-family:'Noto Sans JP', sans-serif; font-weight:400;
  font-size:.85rem; color:var(--ink-soft); letter-spacing:.02em;
}
.brewery-card__features {
  font-size:.9rem; color:var(--ink-soft); line-height:1.7; margin-top:.35rem;
  font-weight:400;
}

.empty-region {
  background:var(--bg-alt); padding:2rem; border-left:3px solid var(--warm);
  font-family:'Shippori Mincho', serif;
  color:var(--ink-soft); font-size:.95rem;
}
.empty-region em {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  color:var(--accent); letter-spacing:.05em;
}

.divider {
  max-width:1100px; margin:3rem auto; padding:0 2rem;
  display:flex; align-items:center; gap:1rem;
}
.divider .rule { flex:1; height:1px; background:var(--line); }
.divider .ornament { width:8px; height:8px; background:var(--accent); transform:rotate(45deg); }
.divider .ornament.outer { width:4px; height:4px; background:var(--warm); }

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

/* セクションヘッダー画像 (Vertex AI) */
.cat-image {
  margin: 0 0 2rem;
  overflow: hidden;
  border: 1px solid var(--line);
  position: relative;
}
.cat-image img {
  display: block;
  width: 100%;
  height: auto;
  max-height: 280px;
  object-fit: cover;
  filter: contrast(0.98) saturate(0.95);
}
.cat-image__cap {
  position: absolute;
  bottom: .5rem;
  right: .75rem;
  font-family: 'Cormorant Garamond', serif;
  font-style: italic;
  font-size: .65rem;
  color: rgba(255,255,255,0.92);
  letter-spacing: .12em;
  background: rgba(26,23,23,0.45);
  padding: .15rem .5rem;
}
"""


# ────────────── 副原料カテゴリ分類 ──────────────

INGREDIENT_CATEGORIES = [
    ("hop", "ホップ", "HOP", "クラフトサケと最も相性の良いビール由来の副原料。シトラ・Huell Melon・Hallertau Blancなど品種別の表現も。"),
    ("fruit", "果実", "FRUITS", "リンゴ・ブドウ・洋梨・イチゴ・メロン・桃・パイナップル等、地域の旬を醸す。"),
    ("tea-herb", "茶葉・ハーブ・スパイス", "TEA & HERBS", "ジャスミン茶・狭山茶・抹茶／山椒・黒文字・バジル・在来植物など、香りと余韻で表現する副原料。"),
    ("rice-koji", "米のみ・特殊麹", "RICE / SPECIAL KOJI", "副原料なしの純米どぶろく、全麹酒、発芽玄米、大麦麹・蕎麦麹・芋麹など、米と麹そのものを主役にした酒。"),
    ("special", "特殊副原料", "SPECIAL", "アガベシロップ・ハチミツ・トマト・小豆・黒豆・桜など、ジャンルを問わない自由な副原料。"),
]


def categorize_ingredient(ing):
    """副原料文字列を5カテゴリに分類"""
    if not ing:
        return None
    s = ing
    if "製法" in s:          # 「ベルギービール製法」等は副原料ではないので分類しない
        return None
    if "ホップ" in s:
        return "hop"
    if (any(k in s for k in ["リンゴ", "りんご", "ブドウ", "ぶどう", "洋梨", "洋ナシ",
                             "ル・レクチェ", "ル レクチエ", "メロン", "イチゴ",
                             "あまおう", "越後姫", "桃", "マンゴー", "パイナップル",
                             "パイン", "シークワーサー", "シークヮーサー", "アセロラ", "ミカン",
                             "黒イチジク", "レモン", "カボス", "果汁", "果物",
                             "柚子", "八朔", "ブルーベリー"])
            and "レモングラス" not in s and "レモネード" not in s):  # レモングラス/レモネードは茶ハーブ
        return "fruit"
    if "茶" in s and "焼酎" not in s:
        return "tea-herb"
    if any(k in s for k in ["山椒", "黒文字", "ハーブ", "ボタニカル",
                            "在来", "バジル", "ミント", "レモングラス",
                            "レモネード", "花酛"]):
        return "tea-herb"
    if "米" in s or "玄米" in s or ("麹" in s and "アガベ" not in s):
        return "rice-koji"
    # 残りは special
    return "special"


# ────────────── ジャンル分類（蔵単位） ──────────────

GENRES = [
    ("hop-sake", "ホップサケ", "HOP SAKE", "ホップを副原料に使う、ビールカルチャー寄りのクラフトサケ。"),
    ("fruit-sake", "果実サケ", "FRUIT SAKE", "果汁・果実を発酵に絡める、ワイン的なクラフトサケ。"),
    ("doburoku", "古典どぶろく", "CLASSIC DOBUROKU", "米と麹のみで醸した、伝統的どぶろくの系譜。"),
    ("full-koji", "全麹酒・米麹100%", "FULL KOJI", "米麹のみで造る、清酒規格を超えた濃密な酒。"),
    ("kioke", "木桶仕込み", "KIOKE FERMENTATION", "木桶を使った手仕事の発酵。"),
    ("foreign-koji", "異素材麹", "FOREIGN KOJI", "大麦・蕎麦・芋など米以外の麹で造る、新しい酒のかたち。"),
    ("tea-herb-sake", "茶葉・ハーブサケ", "TEA & HERB", "茶やハーブの香りを纏う、繊細な系統。"),
]


def _load_brand_details():
    """brand_data/*.json を slug -> [detail] (breweries_brands と同じ順序) で読む。
    銘柄名や note に現れない製法（木桶・全麹・酒母など）を判定に使うため。"""
    import glob
    import json
    out = {}
    for p in glob.glob(str(Path(__file__).resolve().parent / "brand_data" / "*.json")):
        d = json.load(open(p, encoding="utf-8"))
        out[d["brewery"]] = list(d["brands"].values())
    return out


BRAND_DETAILS = _load_brand_details()


def get_brewery_genres(brewery):
    """蔵を複数のジャンルに分類（重複OK）"""
    slug = brewery["slug"]
    brands = BRANDS.get(slug, [])
    features = brewery.get("features", "") + brewery.get("philosophy", "")
    genres = set()
    _details = BRAND_DETAILS.get(slug, [])

    for _i, b in enumerate(brands):
        ings = b.get("sub_ingredients") or []
        name = b.get("name", "")
        note = b.get("note", "")
        # brand_data の製法情報（発酵容器・酒母・麹）も判定材料に含める。
        # 例：やまね酒造は銘柄名にもnoteにも「木桶」が出ないが vessel は木桶。
        _d = _details[_i] if _i < len(_details) else {}
        _method = " ".join(str(_d.get(k) or "") for k in ("vessel", "shubo", "koji"))
        all_text = " ".join(ings) + " " + name + " " + note + " " + _method

        if "ホップ" in all_text:
            genres.add("hop-sake")
        if (any(k in all_text for k in ["リンゴ", "ブドウ", "洋梨", "メロン", "イチゴ",
                                        "あまおう", "桃", "マンゴー", "パイナップル",
                                        "シークワーサー", "シークヮーサー", "アセロラ", "黒イチジク",
                                        "レモン", "カボス", "果汁", "果物", "ル・レクチェ",
                                        "ル レクチエ", "ぶどう", "りんご", "八朔",
                                        "ブルーベリー", "ミカン"])
                and "レモングラス" not in all_text and "レモネード" not in all_text):
            genres.add("fruit-sake")
        if "どぶろく" in name or "ドブロク" in name or "ドブロク" in note:
            # 古典どぶろく＝副原料を使わない（米と麹のみ）もののみ。果実・ホップ入りは各ジャンルへ
            _subs = b.get("sub_ingredients") or []
            if not any(x and x != "米のみ" and "米" not in x for x in _subs):
                genres.add("doburoku")
        if "全麹" in all_text or "米麹100%" in all_text or "十割麹" in name:
            genres.add("full-koji")
        if "木桶" in all_text:
            genres.add("kioke")
        if "茶" in all_text or "山椒" in all_text or "黒文字" in all_text or \
           "在来" in all_text or "バジル" in all_text or "ハーブ" in all_text:
            genres.add("tea-herb-sake")

    # 特殊：LINNÉ は異素材麹
    if any(k in features for k in ["大麦麹", "蕎麦", "芋麹", "米以外の麹"]):
        genres.add("foreign-koji")
    if any("大麦" in (b.get("sub_ingredients") or [None])[0] or "" or "" for b in brands if b.get("sub_ingredients")):
        genres.add("foreign-koji")
    for b in brands:
        for ing in (b.get("sub_ingredients") or []):
            if "大麦" in ing or "蕎麦" in ing or "芋麹" in ing:
                genres.add("foreign-koji")

    # 純米のみ（米のみ系）→ どぶろく系として補足
    for b in brands:
        for ing in (b.get("sub_ingredients") or []):
            if "米のみ" in ing and "全麹" not in ing and "100%" not in ing:
                genres.add("doburoku")

    return genres


# ────────────── HTML テンプレート ──────────────

def page_head(title, description, path="/"):
    seo = seo_head(path, title, description, og_type="website", jsonld=[
        {"@context": "https://schema.org/", "@type": "CollectionPage",
         "name": f"{title} — saketto.", "description": description,
         "url": SITE_URL + path, "isPartOf": website_node()},
        breadcrumb([("トップ", "/"), (title, path)]),
    ])
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — saketto.</title>
<meta name="description" content="{description}">
{seo}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@400;500&family=Cormorant+Garamond:ital,wght@0,400;1,400&display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@400;500&family=Cormorant+Garamond:ital,wght@0,400;1,400&display=swap" media="print" onload="this.media=&#39;all&#39;">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@400;500&family=Cormorant+Garamond:ital,wght@0,400;1,400&display=swap"></noscript>
<style>{CSS}{JUMP_NAV_CSS}</style>
{head_extra()}
</head>
<body>
<main>
"""


def masthead(label, right_text=""):
    return f"""
  <div class="masthead">
    <div class="left">
      <a class="brand-link" href="../index.html"><span class="accent-dot"></span>SAKETTO</a>
      <span>{label}</span>
    </div>
    <nav class="masthead-nav" aria-label="ナビ">
      <a href="../subingredients/">副原料</a>
      <a href="../brewery/">蔵</a>
      <a href="../region/">地域</a>
      <a href="../genre/">ジャンル</a>
      <a href="../guide/">読みもの</a>
    </nav>
  </div>
"""


def hero(eyebrow, title_html, lede, guide="", divider=True):
    """divider=False にすると区切り線を出さない（目次を挟んでから区切る用）。"""
    guide_html = f'\n    <p class="hero__guide">{guide}</p>' if guide else ""
    rule = """
  <div class="divider">
    <div class="rule"></div>
    <div class="ornament outer"></div>
    <div class="ornament"></div>
    <div class="ornament outer"></div>
    <div class="rule"></div>
  </div>
""" if divider else ""
    return f"""
  <section class="hero">
    <div class="hero__eyebrow">{eyebrow}</div>
    <h1 class="hero__title">{title_html}</h1>
    <p class="hero__lede">{lede}</p>{guide_html}
  </section>
{rule}"""


def guide_block(text):
    """軸ページの長い解説。目次の下に置いて、選択肢を先に見せる。"""
    return f"""
  <section class="hero" style="padding-top:0;padding-bottom:2.5rem">
    <p class="hero__guide" style="margin-top:0">{text}</p>
  </section>

  <div class="divider">
    <div class="rule"></div>
    <div class="ornament outer"></div>
    <div class="ornament"></div>
    <div class="ornament outer"></div>
    <div class="rule"></div>
  </div>
"""


def footer():
    return f"""
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
        20歳未満の飲酒は法律で禁じられています<span class="colophon__sep">／</span>
        {pr_notice()}<span class="colophon__sep">／</span>
        © 2026 saketto.
      </div>
    </div>
  </footer>

</main>
</body>
</html>
"""


def render_entry(brewery_slug, brand, idx=0):
    """副原料カテゴリページ内の1エントリ(蔵×銘柄)を描画。
    idx は brewery_slug 蔵のbrands配列内インデックス → 蔵詳細ページのbN へジャンプ"""
    b = by_slug(brewery_slug)
    if not b:
        return ""
    specs = []
    if brand.get("abv") is not None:
        specs.append(f'<span class="spec-pill accent">ABV {brand["abv"]}%</span>')
    if brand.get("volume_ml") is not None:
        specs.append(f'<span class="spec-pill warm">{brand["volume_ml"]}ml</span>')
    for ing in (brand.get("sub_ingredients") or [])[:2]:
        specs.append(f'<span class="spec-pill">{ing}</span>')
    specs_html = ' '.join(specs)
    return f"""
        <a class="entry" href="../brand/{brewery_slug}-{idx}.html">
          <div>
            <div class="entry__brand">{brand['name']}</div>
            <div class="entry__brewery">{b['name']}</div>
          </div>
          <div class="entry__specs">{specs_html}</div>
          <div class="entry__brewery" style="text-align:right">{b['prefecture']}</div>
        </a>"""


def jump_nav(items, label="この中から探す"):
    """カテゴリ間を飛べる目次。軸ページは1ページが数千〜数万pxになるため、
    最初のスクリーンで全カテゴリを見せて目的地へ直行できるようにする。
    items: [(anchor_id, 表示名, 件数), ...]"""
    if not items:
        return ""
    links = "".join(
        f'<a class="jump-nav__item" href="#{aid}">{name}'
        f'<span class="jump-nav__num">{cnt}</span></a>'
        for aid, name, cnt in items)
    return f"""
  <nav class="jump-nav" aria-label="{label}">
    <div class="jump-nav__label">— {label}</div>
    <div class="jump-nav__items">{links}</div>
  </nav>"""


JUMP_NAV_CSS = """
.jump-nav { max-width:1100px; margin:0 auto 2.5rem; padding:0 2rem; }
.jump-nav__label { font-family:'Cormorant Garamond',serif; font-style:italic;
  font-size:.8rem; color:var(--ink-mute); letter-spacing:.12em; margin-bottom:.7rem; }
.jump-nav__items { display:flex; flex-wrap:wrap; gap:.55rem; }
.jump-nav__item { display:inline-flex; align-items:baseline; gap:.45rem;
  font-family:'Zen Kaku Gothic Antique',sans-serif; font-weight:500; font-size:.88rem;
  letter-spacing:.04em; color:var(--ink); text-decoration:none;
  border:1px solid var(--line); padding:.5rem .9rem;
  transition:border-color .25s, color .25s, background .25s; }
.jump-nav__item:hover { border-color:var(--accent); color:var(--accent); background:var(--paper); }
.jump-nav__num { font-family:'Cormorant Garamond',serif; font-size:.8rem; color:var(--ink-mute); }
.jump-nav__item:hover .jump-nav__num { color:var(--accent); }
/* アンカー移動時に見出しがマストヘッドへ潜らないよう余白を確保 */
.section[id] { scroll-margin-top: 1.5rem; }
@media (max-width:640px) {
  .jump-nav { padding:0 1.25rem; margin-bottom:2rem; }
  .jump-nav__item { font-size:.82rem; padding:.45rem .75rem; }
}
"""


def render_brewery_card(brewery, idx, picks=None):
    """蔵カード。picks=[(銘柄名, パス), ...] を渡すと該当銘柄へのリンクを併記する。

    ジャンル軸・地域軸は蔵カードだけを並べていたため、銘柄ページへ一切
    到達できなかった（副原料軸のみ142件リンク）。「なぜこの蔵がこの分類なのか」
    も分からないので、該当する銘柄名を実リンクで見せる。
    カード全体が <a> なので、銘柄リンクはカードの外側に別ブロックで置く。
    """
    picks_html = ""
    if picks:
        links = "".join(
            f'<a class="card-picks__item" href="{path}">{name}</a>' for name, path in picks[:4])
        more = ('<span class="card-picks__more">ほか</span>' if len(picks) > 4 else "")
        picks_html = f'<div class="card-picks"><span class="card-picks__label">該当銘柄</span>{links}{more}</div>'
    return f"""
      <div class="brewery-cell">
      <a class="brewery-card" href="../brewery/{brewery['slug']}.html">
        <div class="brewery-card__num">No. {idx:02d}</div>
        <div class="brewery-card__name">{brewery['name']}</div>
        <div class="brewery-card__meta">{brewery['prefecture']}・{brewery['city']}　/　創業 {brewery['founded']}</div>
        <div class="brewery-card__features">{brewery['features']}</div>
      </a>{picks_html}
      </div>"""


# ────────────── 各ハブ生成 ──────────────



def brand_picks(brewery, limit=3):
    """蔵の代表銘柄を [(名前, パス), ...] で返す。購入導線のあるものを優先。"""
    from moshimo_link import resolve_rakuten
    slug = brewery["slug"]
    buyable, others = [], []
    for i, b in enumerate(BRANDS.get(slug, [])):
        item = (b["name"], f"../brand/{slug}-{i}.html")
        (buyable if resolve_rakuten(slug, i, b["name"]) else others).append(item)
    return (buyable + others)[:limit]


def brands_in_genre(brewery, genre_key):
    """その蔵の銘柄のうち、指定ジャンルに該当するものを [(名前, パス), ...] で返す。
    判定は get_brewery_genres と同じ材料（副原料・銘柄名・note・brand_dataの製法）を使う。"""
    slug = brewery["slug"]
    dets = BRAND_DETAILS.get(slug, [])
    out = []
    for i, b in enumerate(BRANDS.get(slug, [])):
        ings = b.get("sub_ingredients") or []
        d = dets[i] if i < len(dets) else {}
        method = " ".join(str(d.get(k) or "") for k in ("vessel", "shubo", "koji"))
        t = " ".join(ings) + " " + b.get("name", "") + " " + (b.get("note") or "") + " " + method
        hit = False
        if genre_key == "hop-sake":
            hit = "ホップ" in t or "唐花草" in t
        elif genre_key == "fruit-sake":
            hit = any(k in t for k in ["リンゴ", "りんご", "ブドウ", "ぶどう", "洋梨", "洋ナシ", "メロン",
                                       "イチゴ", "いちご", "あまおう", "越後姫", "桃", "マンゴー",
                                       "パイナップル", "八朔", "レモン", "カボス", "ライチ", "果汁",
                                       "ブルーベリー", "ミカン", "みかん", "トマト"])
        elif genre_key == "doburoku":
            hit = ("どぶろく" in t or "ドブロク" in t) and not [x for x in ings if x and "米" not in x]
        elif genre_key == "full-koji":
            hit = "全麹" in t or "十割麹" in t or "米麹100%" in t
        elif genre_key == "kioke":
            hit = "木桶" in t
        elif genre_key == "foreign-koji":
            hit = any(k in t for k in ["大麦", "蕎麦", "そば", "芋麹", "黒米"])
        elif genre_key == "tea-herb-sake":
            hit = any(k in t for k in ["茶", "山椒", "黒文字", "在来", "バジル", "ハーブ",
                                       "ミント", "ハッカ", "薄荷", "紫蘇", "エルダーフラワー"])
        if hit:
            out.append((b["name"], f"../brand/{slug}-{i}.html"))
    return out


def gen_subingredients():
    """副原料逆引きハブ"""
    OUT = REPO_ROOT / "subingredients"
    OUT.mkdir(exist_ok=True)

    # カテゴリ別に銘柄を集計
    by_cat = defaultdict(list)  # cat -> [(brewery_slug, brand, brand_idx)]
    for brewery in BREWERIES:
        for idx, brand in enumerate(BRANDS.get(brewery["slug"], [])):
            ings = brand.get("sub_ingredients") or []
            cats_for_this = set()
            for ing in ings:
                cat = categorize_ingredient(ing)
                if cat:
                    cats_for_this.add(cat)
            for cat in cats_for_this:
                by_cat[cat].append((brewery["slug"], brand, idx))

    total_brands = sum(len(v) for v in by_cat.values())

    html = page_head("クラフトサケを副原料から探す", "クラフトサケを副原料（ホップ・果実・茶葉・ハーブ・米のみ・特殊副原料）から横断的に検索する逆引きデータベース。", "/subingredients/")
    html += masthead("AXIS 01 — SUB-INGREDIENTS", f"5 categories")
    html += hero(
        "— FIVE CATEGORIES",
        '副原料から、<span class="accent">探す</span>。',
        '何を入れた酒か。クラフトサケの自由さを最も雄弁に語るのが副原料。ホップから茶葉、ハーブ、果実、そして米と麹のみまで、5つのカテゴリで横断する。',
        divider=False
    )
    # カテゴリ目次（このページは全カテゴリを縦に並べるため数千pxになる）
    html += jump_nav([(f"cat-{k}", jp, len(by_cat.get(k, [])))
                      for k, jp, _en, _d in INGREDIENT_CATEGORIES], "5つのカテゴリから")
    html += guide_block('クラフトサケの味の輪郭は、米と麹に「何を重ねるか」で大きく変わる。ホップを選べば柑橘やハーブを思わせる香りが立つビール好きに馴染む一本に、果実を選べばワインのような酸と甘みの方向へ、茶葉やハーブなら和の余韻に近づく。逆に副原料を使わない「米と麹のみ」は、どぶろくや全麹といった製法の個性がそのまま顔を出す。はじめてなら、ふだん好きな飲み物——ビール、白ワイン、日本酒——に近いカテゴリから入るのが早道だ。気になる素材をひとつ選んで、そこから蔵へ、銘柄へと辿ってほしい。製法の背景は<a href="../guide/craftsake-towa.html">「クラフトサケとは」</a>でも読める。')
    html += '<div style="max-width:1100px; margin:0 auto; padding:0 2rem 2rem">'

    SUB_IMG_MAP = {"hop":"sub_hop", "fruit":"sub_fruit", "tea-herb":"sub_tea_herb",
                   "rice-koji":"sub_rice", "special":"sub_special"}
    for cat_key, cat_jp, cat_en, cat_desc in INGREDIENT_CATEGORIES:
        entries = by_cat.get(cat_key, [])
        img_name = SUB_IMG_MAP.get(cat_key, "")
        img_html = (
            f'<figure class="cat-image"><img src="../assets/images/{img_name}.webp" alt="" loading="lazy" width="1024" height="1024">'
            f'</figure>'
        ) if img_name else ''
        html += f"""
  <section class="section" id="cat-{cat_key}" style="padding-bottom:2rem">
    <div class="section-meta">
      <span class="section-meta__num">No. {INGREDIENT_CATEGORIES.index((cat_key, cat_jp, cat_en, cat_desc))+1:02d}</span>
      <h2 class="section-meta__label" style="margin:0">{cat_en}</h2>
      <span class="section-meta__count">/ {len(entries)} 銘柄</span>
      <span class="section-meta__rule"></span>
    </div>
    {img_html}
    <h2 class="cat-title">{cat_jp}</h2>
    <p class="cat-desc">{cat_desc}</p>
    <div class="entries">"""
        for slug, brand, idx in entries:
            html += render_entry(slug, brand, idx)
        html += """
    </div>
  </section>"""

    html += '</div>'
    html += footer()

    out_path = OUT / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"  subingredients/index.html  ({total_brands}件の副原料エントリ)")


REGION_SLUG = {
    "東北": "tohoku", "関東": "kanto", "中部": "chubu",
    "関西": "kansai", "九州": "kyushu", "沖縄": "okinawa",
    "北海道": "hokkaido", "中国": "chugoku", "四国": "shikoku",
}


def region_anchor(region):
    """地域ハブ内のアンカーID。蔵ページからここへ直接リンクする。"""
    return "r-" + REGION_SLUG.get(region, region)


def gen_regions():
    """地域逆引きハブ"""
    OUT = REPO_ROOT / "region"
    OUT.mkdir(exist_ok=True)

    by_region = defaultdict(list)
    for b in BREWERIES:
        by_region[b["region"]].append(b)

    populated = [r for r in REGIONS if by_region[r]]
    empty = [r for r in REGIONS if not by_region[r]]

    html = page_head("クラフトサケを地域から探す", f"全国のクラフトサケ醸造所{len(BREWERIES)}蔵を東北・関東・中部・関西・九州・沖縄の地域別に横断検索。震災復興の東北、駅ナカの都市型、南国素材の九州・沖縄まで、土地の物語から次の一本へ。", "/region/")
    html += masthead("AXIS 03 — REGION", f"{len(populated)} regions populated")
    html += hero(
        "— BY REGION",
        '地域から、<span class="accent">探す</span>。',
        f'クラフトサケは復興と再生の文脈と深く結びついている。福島・宮城・岩手といった東北、首都圏の都市型、関西の団地酒蔵、九州・沖縄の南国素材まで、{len(BREWERIES)}蔵が日本列島に散らばる。',
        'クラフトサケの蔵は、その土地の事情と切り離せない。震災からの再生を懸けて立ち上がった東北の蔵があり、駅ナカや街なかで醸す都市型の醸造所があり、南の島では地元の素材を仕込みに使う蔵が生まれている。同じ「米と麹の酒」でも、土地が変われば動機も素材も変わる——そこがこのジャンルの面白さだ。旅先や出身地、いつか行ってみたい町。縁のある地域から選べば、一本の酒がその地域の物語への入口になる。気に入った蔵が見つかったら、<a href="../furusato/">ふるさと納税</a>で応援するという選び方もある。'
    )

    html += '<div style="max-width:1100px; margin:0 auto; padding:0 2rem 2rem">'

    REGION_IMG_MAP = {
        "東北": "region_tohoku", "関東": "region_kanto", "中部": "region_chubu",
        "関西": "region_kansai", "九州": "region_kyushu", "沖縄": "region_okinawa",
    }
    # 他ハブと同じくアンカーを振る。蔵ページから「◯◯の蔵」へ直接送れるようにするため
    # （これが無いあいだ、蔵ページの導線は地域トップに落とすしかなかった）
    html += jump_nav([(region_anchor(r), r, len(by_region[r])) for r in populated],
                     label="地域から探す")
    for idx, region in enumerate(populated, 1):
        breweries = by_region[region]
        img_name = REGION_IMG_MAP.get(region, "")
        img_html = (
            f'<figure class="cat-image"><img src="../assets/images/{img_name}.webp" alt="" loading="lazy" width="1376" height="768">'
            f'</figure>'
        ) if img_name else ''
        html += f"""
  <section class="section" id="{region_anchor(region)}">
    <div class="section-meta">
      <span class="section-meta__num">No. {idx:02d}</span>
      <h2 class="section-meta__label">{region}</h2>
      <span class="section-meta__count">/ {len(breweries)} 蔵</span>
      <span class="section-meta__rule"></span>
    </div>
    {img_html}
    <div class="brewery-grid">"""
        for i, b in enumerate(breweries, 1):
            html += render_brewery_card(b, i, picks=brand_picks(b))
        html += """
    </div>
  </section>"""

    # 空地域
    if empty:
        html += f"""
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">— COMING</span>
      <span class="section-meta__label">EMPTY REGIONS</span>
      <span class="section-meta__rule"></span>
    </div>
    <div class="empty-region">
      <em>— 拡張予定</em><br>
      {' / '.join(empty)} は現時点で新興クラフトサケ醸造所の確認が取れていません。Phase 2 で発掘予定。
    </div>
  </section>"""

    html += '</div>'
    html += footer()

    out_path = OUT / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"  region/index.html  ({len(populated)}地域 / {sum(len(v) for v in by_region.values())}蔵)")


def gen_genres():
    """ジャンル逆引きハブ（saketto独自）"""
    OUT = REPO_ROOT / "genre"
    OUT.mkdir(exist_ok=True)

    by_genre = defaultdict(list)  # genre -> [brewery]
    for brewery in BREWERIES:
        genres = get_brewery_genres(brewery)
        for g in genres:
            by_genre[g].append(brewery)

    html = page_head("クラフトサケをジャンルから探す", "クラフトサケのジャンル（ホップサケ・果実サケ・古典どぶろく・全麹酒・木桶仕込み・異素材麹・茶葉ハーブサケ）から横断検索。saketto独自軸。", "/genre/")
    html += masthead("AXIS 04 — GENRE / SAKETTO独自", "7 genres")
    html += hero(
        "— SAKETTO ORIGINAL AXIS",
        'ジャンルから、<span class="accent">探す</span>。',
        '副原料の選び方、製法の系譜、麹の素材。クラフトサケの中にも明確な"系"がある。これはsaketto独自の分類軸。',
        divider=False
    )
    # ジャンル目次（銘柄が無いジャンルは出さない）
    html += jump_nav([(f"g-{k}", jp, len(by_genre.get(k, [])))
                      for k, jp, _en, _d in GENRES if by_genre.get(k)], "ジャンルから")
    html += guide_block('ジャンルは、sakettoが銘柄を読み解くために置いた独自のものさしだ。ホップを効かせた「ホップサケ」、果実を醸し込む「果実サケ」、伝統の製法に立ち返る「古典どぶろく」、麹の力だけで設計する「全麹酒」、木の香りをまとう「木桶仕込み」、麹の素材そのものを変える「異素材麹」——どの"系"に連なる一本かが分かると、初めての銘柄でも味の見当がつくようになる。蔵の数だけ解釈があるので、同じジャンルの中で蔵ごとの違いを飲み比べるのも、この軸ならではの楽しみ方だ。')
    html += '<div style="max-width:1100px; margin:0 auto; padding:0 2rem 2rem">'

    for idx, (g_key, g_jp, g_en, g_desc) in enumerate(GENRES, 1):
        breweries = by_genre.get(g_key, [])
        if not breweries:
            continue
        html += f"""
  <section class="section" id="g-{g_key}">
    <div class="section-meta">
      <span class="section-meta__num">No. {idx:02d}</span>
      <h2 class="section-meta__label" style="margin:0">{g_en}</h2>
      <span class="section-meta__count">/ {len(breweries)} 蔵</span>
      <span class="section-meta__rule"></span>
    </div>
    <h2 class="cat-title">{g_jp}</h2>
    <p class="cat-desc">{g_desc}</p>
    <div class="brewery-grid">"""
        for i, b in enumerate(breweries, 1):
            html += render_brewery_card(b, i, picks=brands_in_genre(b, g_key))
        html += """
    </div>
  </section>"""

    html += '</div>'
    html += footer()

    out_path = OUT / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"  genre/index.html  ({len([g for g in GENRES if by_genre.get(g[0])])}ジャンル)")


# ⚠️ このJSを f-string の中に直接書かないこと。
# JSの { } が置換フィールドとして解釈されて壊れる（GIN-DBで実際に事故った箇所）。
# 必ず定数のまま連結する。
FURUSATO_FILTER_JS = """<script>
(function () {
  var chips = document.querySelectorAll('.fchip');
  var cards = document.querySelectorAll('[data-portals]');
  var result = document.getElementById('fresult');
  if (!chips.length || !cards.length) return;

  function apply(key) {
    var shown = 0;
    cards.forEach(function (c) {
      var ok = !key || (' ' + c.getAttribute('data-portals') + ' ').indexOf(' ' + key + ' ') >= 0;
      c.hidden = !ok;
      if (ok) shown++;
    });
    chips.forEach(function (ch) {
      var on = (ch.dataset.portal || '') === key;
      ch.setAttribute('aria-current', on ? 'true' : 'false');
    });
    if (result) {
      var name = '';
      chips.forEach(function (ch) { if ((ch.dataset.portal || '') === key) name = ch.dataset.label || ''; });
      result.textContent = key ? (name + 'で寄附できる ' + shown + ' 蔵') : ('すべて表示中 ' + shown + ' 蔵');
    }
  }

  chips.forEach(function (ch) {
    ch.addEventListener('click', function (e) {
      e.preventDefault();
      var key = ch.dataset.portal || '';
      apply(key);
      history.replaceState(null, '', key ? ('#portal=' + key) : location.pathname);
    });
  });

  var m = /portal=([\\w-]+)/.exec(location.hash);
  apply(m ? m[1] : '');
})();
</script>"""


FURUSATO_FILTER_CSS = """<style>
.fchips { display:flex; flex-wrap:wrap; gap:.5rem; margin:0 0 .6rem; }
.fchip {
  display:inline-flex; align-items:center; gap:.4rem; min-height:44px;
  padding:.45rem .9rem; border:1px solid var(--line); background:var(--paper);
  font-family:'Zen Kaku Gothic Antique',sans-serif; font-size:.85rem;
  color:var(--ink-soft); text-decoration:none; cursor:pointer;
  transition:background .25s, border-color .25s, color .25s;
}
.fchip:hover { border-color:var(--accent); color:var(--accent); }
.fchip[aria-current="true"] { background:var(--accent); border-color:var(--accent); color:var(--paper); }
.fchip__n { font-family:'Cormorant Garamond',serif; font-style:italic; font-size:.82rem; opacity:.85; }
.fchips-note { font-family:'Zen Kaku Gothic Antique',sans-serif; font-size:.82rem;
  color:var(--ink-mute); margin:0 0 .4rem; }
#fresult { font-family:'Cormorant Garamond',serif; font-style:italic;
  font-size:.9rem; color:var(--accent); margin:0 0 1.6rem; display:block; }
.yen-note { font-size:.78rem; color:var(--ink-mute); margin-left:.3rem; }
/* 品切れ等の状態。押せるリンクと同じ見た目にすると誤解するので枠線だけにする */
.furusato-status {
  display:inline-flex; align-items:center; margin-left:.4rem; padding:.2rem .6rem;
  border:1px dashed var(--line); font-family:'Zen Kaku Gothic Antique',sans-serif;
  font-size:.78rem; color:var(--ink-mute);
}
.fallback-portals { display:flex; flex-wrap:wrap; gap:.6rem; margin-top:1rem; }
.fallback-portals a {
  display:inline-flex; align-items:center; min-height:44px; padding:.5rem 1rem;
  border:1px solid var(--line); background:var(--paper); text-decoration:none;
  font-family:'Zen Kaku Gothic Antique',sans-serif; font-size:.88rem; color:var(--ink);
  transition:background .25s, border-color .25s;
}
.fallback-portals a:hover { background:var(--bg-alt); border-color:var(--accent); color:var(--accent); }
</style>"""


def gen_furusato():
    """ふるさと納税逆引きハブ"""
    OUT = REPO_ROOT / "furusato"
    OUT.mkdir(exist_ok=True)

    confirmed = [b for b in BREWERIES if b["slug"] in FURUSATO]
    not_confirmed = [b for b in BREWERIES if b["slug"] not in FURUSATO]

    html = page_head("クラフトサケをふるさと納税から探す", f"クラフトサケのふるさと納税返礼品を一次ソース確認の上で横断検索。返礼品を確認できた{len(confirmed)}蔵を寄附額・ポータル別に掲載。寄附で蔵の地元を支えながら、限定流通の一本に出会う。", "/furusato/")
    html += masthead("EXTRA — FURUSATO TAX", f"{len(confirmed)} confirmed")
    html += hero(
        "— TAX-DEDUCTIBLE DISCOVERY",
        'ふるさと納税から、<span class="accent">支援する</span>。',
        f'クラフトサケのふるさと納税返礼品を一次ソース確認の上で集約。寄附で蔵を支えながら、地域の挑戦と希少な酒に出会える。確認できた {len(confirmed)} 蔵のみ掲載、残り {len(not_confirmed)} 蔵は今後の出品を追跡。',
        'ふるさと納税は、クラフトサケと出会うもうひとつの入口だ。小さな蔵の酒は流通量が少なく、ECでは売り切れていることも多いが、返礼品なら蔵の地元自治体への寄附を通じて手に入ることがある。しかも寄附はそのまま、蔵が根を張る町に届く——一本を受け取ることが地域の応援になる仕組みだ。このページに載せているのは、自治体やポータルでの出品を一次ソースで確認できた蔵だけ。返礼品は時期によって入れ替わるため、申し込む前にリンク先で最新の受付状況を確かめてほしい。'
    )
    html += '<div style="max-width:1100px; margin:0 auto; padding:0 2rem 2rem">'

    # ── 使うポータルで絞る ──
    # 「どのポータルでも良いから寄附したい」人はまずいない。普段使っている1つで
    # 扱いがあるかを知りたいので、そこだけ残せるようにする。
    _portal_count = {}
    for _b in confirmed:
        _d = FURUSATO[_b["slug"]]
        for _p in set(list(_d["portals"]) + list((_d.get("urls") or {}).keys())):
            _portal_count[_p] = _portal_count.get(_p, 0) + 1
    _chips = [f'<a class="fchip" href="#" data-portal="" data-label="" aria-current="true">'
              f'すべて<span class="fchip__n">{len(confirmed)}</span></a>']
    for _p, _n in sorted(_portal_count.items(), key=lambda x: -x[1]):
        _nm = PORTAL_NAMES.get(_p, _p)
        _chips.append(f'<a class="fchip" href="#portal={_p}" data-portal="{_p}" '
                      f'data-label="{_nm}" aria-current="false">{_nm}'
                      f'<span class="fchip__n">{_n}</span></a>')

    html += f"""
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. 01</span>
      <h2 class="section-meta__label">CONFIRMED LISTINGS</h2>
      <span class="section-meta__count">/ {len(confirmed)} 蔵</span>
      <span class="section-meta__rule"></span>
    </div>
    <p class="fchips-note">いつも使っているポータルを選ぶと、そこで扱いのある蔵だけになります。<br>
      ※「楽天ふるさと納税」のリンクはアフィリエイト広告（PR）です。寄附額に影響はありません。</p>
    <nav class="fchips" aria-label="ポータルで絞る">{''.join(_chips)}</nav>
    <span id="fresult">すべて表示中 {len(confirmed)} 蔵</span>
    <div class="entries">"""

    for b in confirmed:
        data = FURUSATO[b["slug"]]
        # ポータル名は「押せる」ことが期待される要素。URLがあるものは実リンクにする
        # （収益モデルにふるさと納税を掲げているのに、従来は span で出口が無かった）。
        _urls = data.get("urls") or {}

        def _portal_pill(code):
            """ポータル1つぶんのリンク。楽天は必ずもしも経由（社長ルール）。

            従来は楽天の商品URLを生で貼っており、ふるさと納税を収益の柱に
            掲げているのに楽天ぶんが1円も計上されない状態だった。
            pl_id=616 は任意URLを渡せる型なので、検索ではなく返礼品ページへ直接送る。
            """
            label = PORTAL_NAMES.get(code, code)
            u = _urls.get(code)
            if not u:
                return f'<span class="spec-pill accent">{label}</span>'
            # sponsored は「広告リンク」の意味。実際にアフィリを通しているのは
            # もしも経由の楽天だけなので、他ポータルに付けると表示が実態と食い違う。
            # （チョイス・ふるなび・さとふる等を収益化するにはA8の提携が要る）
            if code == "r":
                return (f'<a class="spec-pill accent portal-link" href="{rakuten_url(u)}" '
                        f'target="_blank" rel="nofollow sponsored noopener">{label} →</a>')
            return (f'<a class="spec-pill accent portal-link" href="{u}" target="_blank" '
                    f'rel="noopener">{label} →</a>')

        # **URLで裏の取れたポータルだけを出す。**
        # 以前は portals に書いてあるだけの（URLの無い）ポータルも
        # 押せないラベルとして並べていたが、それは「そこで寄附できる」という
        # 主張でありながら確認手段が無く、読者も何もできない。
        # ふるなび・さとふるは検索結果がJSレンダリングで機械確認ができず、
        # 実際に稲とアガベのふるなびは200を返しながら中身が空だった。
        # 確認できないものは並べず、下の「見つからないとき」から各ポータルへ逃がす。
        _seen = [p for p in list(data["portals"]) + list(_urls) if p in _urls]
        _seen = list(dict.fromkeys(_seen))
        portals_html = " ".join(_portal_pill(p) for p in _seen)
        _portal_key = " ".join(_seen)  # 絞り込み用（data-portals）
        _status = data.get("status")
        if _status:
            portals_html += f'<span class="furusato-status">{_status}</span>'
        # 寄附額はポータルごと・セット内容ごとに違う。単一の数字に「〜」を付けると
        # 「ここから始まる」と読めてしまい、実際の申込画面と食い違う（12,000円と
        # 表示して19,000円だった例がある）。確認した額であることを明示する。
        yen = (f'{data["donation_yen"]:,}円<span class="yen-note">（確認時点）</span>'
               if data.get("donation_yen") else '寄附額はポータルで確認')
        rep = data.get("rep_brand", "")
        html += f"""
      <div class="entry entry--furusato" data-portals="{_portal_key}">
        <div>
          <div class="entry__brand"><a href="../brewery/{b['slug']}.html">{b['name']}</a></div>
          <div class="entry__brewery">{data['city']}　/　{rep}</div>
        </div>
        <div class="entry__specs">{portals_html}</div>
        <div class="entry__brewery" style="text-align:right">{yen}</div>
      </div>"""

    html += """
    </div>
  </section>"""

    # ── 見つからなかったときの出口 ──
    # 返礼品は時期で入れ替わる。掲載が無い＝手に入らない、ではないので
    # 各ポータルの検索へ逃がす。楽天だけは必ずもしも経由にする。
    _fallback = [
        ("ふるさとチョイス", "https://www.furusato-tax.jp/search?header_search=1&q=" + quote("クラフトサケ"), False),
        ("楽天ふるさと納税", rakuten_search("クラフトサケ ふるさと納税"), True),
        ("ふるなび", "https://furunavi.jp/search?keyword=" + quote("どぶろく"), False),
        ("さとふる", "https://www.satofull.jp/search.php?q=" + quote("どぶろく"), False),
    ]
    _fb = "".join(
        f'<a href="{u}" target="_blank" '
        f'rel="{"nofollow sponsored noopener" if aff else "noopener"}">{n} で探す →</a>'
        for n, u, aff in _fallback)
    html += f"""
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. 02</span>
      <h2 class="section-meta__label">NOT FOUND ／ 見つからないとき</h2>
      <span class="section-meta__rule"></span>
    </div>
    <p class="cat-desc">
      返礼品の取扱いは時期によって入れ替わります。ここに載っていない蔵でも、
      ポータルで「クラフトサケ」「どぶろく」や銘柄名を直接検索すると
      新しい出品が見つかることがあります。上の一覧は
      各ポータルの商品ページで実際に確認できたものだけです。
    </p>
    <div class="fallback-portals">{_fb}</div>
  </section>"""

    html += f"""
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. 03</span>
      <h2 class="section-meta__label">PENDING / NOT YET LISTED</h2>
      <span class="section-meta__count">/ {len(not_confirmed)} 蔵</span>
      <span class="section-meta__rule"></span>
    </div>
    <p class="cat-desc">
      ふるさと納税ポータル(チョイス/楽天/ふるなび/さとふる)での出品を現時点では確認できていない蔵。
      新興・小規模・委託醸造の蔵が多く、今後の出品が期待される。各蔵の公式ECで購入可能。
    </p>
    <div class="brewery-grid">"""
    for i, b in enumerate(not_confirmed, 1):
        html += render_brewery_card(b, i)
    html += """
    </div>
  </section>"""

    html += '</div>'
    # CSSとJSは f-string の外で連結する（JSの { } が置換フィールドと解釈されるため）
    html += FURUSATO_FILTER_CSS
    html += FURUSATO_FILTER_JS
    html += footer()

    out = OUT / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"  furusato/index.html  ({len(confirmed)}社確認 / {len(not_confirmed)}社未確認)")


AWARDS_CSS = """
.awards-wrap { max-width:1100px; margin:0 auto; padding:0 2rem; }
.awards-sec { margin-bottom:3.5rem; }
.awards-sec__desc { color:var(--ink-soft); font-size:.97rem; line-height:1.85; max-width:680px; margin:-1rem 0 1.75rem; }

/* ICC 殿堂（墨バンド） */
.icc { background:var(--ink); position:relative; overflow:hidden; margin:1.5rem 0 3.5rem; }
.icc__inner { max-width:1100px; margin:0 auto; padding:3.75rem 2rem 4rem; position:relative; z-index:1; }
.icc__emblem { position:absolute; right:clamp(1rem,4vw,3.5rem); top:2.8rem;
  width:clamp(140px,16vw,200px); height:auto; opacity:.95; z-index:0; pointer-events:none; }
@media (max-width:760px) { .icc__emblem { position:static; display:block; margin:0 auto 1.75rem; width:150px; } }
.icc__eyebrow { font-family:'Cormorant Garamond',serif; font-style:italic; color:#D9694F; letter-spacing:.15em; font-size:.95rem; margin-bottom:.9rem; }
.icc-year { font-family:'Cormorant Garamond',serif; font-style:italic; font-size:1.55rem; color:#D9694F;
  letter-spacing:.05em; padding:1.7rem 0 .5rem; margin-top:.4rem; }
.icc-year:first-child { margin-top:0; }
.icc__title { font-family:'Shippori Mincho',serif; font-weight:700; color:#F5F0E7; font-size:clamp(1.9rem,4.2vw,2.9rem); line-height:1.2; margin-bottom:.8rem; }
.icc__desc { color:#C9BFAE; font-size:.95rem; line-height:1.9; max-width:660px; margin-bottom:2.4rem; }
.icc-list { display:flex; flex-direction:column; border-top:1px solid #463c36; }
.icc-row { display:grid; grid-template-columns:6.5em 1fr; gap:1.4rem; align-items:center;
  padding:1.3rem .25rem; border-bottom:1px solid #463c36; text-decoration:none; transition:padding-left .25s; }
.icc-row:hover { padding-left:.6rem; }
.icc-row__brewery { font-family:'Shippori Mincho',serif; font-weight:700; font-size:1.2rem; color:#F5F0E7; letter-spacing:.02em; transition:color .25s; }
.icc-row:hover .icc-row__brewery { color:#fff; }
.icc-row__brand { font-family:'Noto Sans JP',sans-serif; font-weight:400; font-size:.85rem; color:#A99C8C; margin-top:.25rem; line-height:1.5; }
.icc-row__year { font-family:'Cormorant Garamond',serif; font-style:italic; font-size:1.3rem; color:#8a7d6e; }
.rank-chip { font-family:'Zen Kaku Gothic Antique',sans-serif; font-weight:700; font-size:.8rem;
  letter-spacing:.08em; padding:.45rem .2rem; text-align:center; line-height:1; }
.rank-chip--win { background:var(--accent); color:#FAF6ED; }
.rank-chip--2nd { border:1px solid #D9694F; color:#E8917B; }
.rank-chip--3rd { border:1px solid #8a7d6e; color:#C9BFAE; }
.rank-chip--fin { border:1px solid #463c36; color:#8a7d6e; }

/* GLOBAL 行先（地域別・旅程インデックス） */
.dest-group { border-top:1px solid var(--line); padding:1.6rem 0 1.2rem; }
.dest-group:last-child { border-bottom:1px solid var(--line); }
.dest-head { display:flex; align-items:baseline; gap:1.1rem; margin-bottom:1.1rem; }
.dest-head__name { font-family:'Cormorant Garamond',serif; font-style:italic; font-weight:700;
  font-size:clamp(1.9rem,4.5vw,2.8rem); color:var(--accent); letter-spacing:.03em; line-height:1; white-space:nowrap; }
.dest-head__rule { flex:1; height:1px; background:var(--line); }
.dest-head__count { font-family:'Zen Kaku Gothic Antique',sans-serif; font-size:.76rem; letter-spacing:.12em; color:var(--ink-mute); white-space:nowrap; }
.dest-item { display:block; text-decoration:none; color:inherit; padding:.7rem 0 .7rem 1.3rem;
  border-left:3px solid var(--line-soft); margin-bottom:.7rem; transition:border-color .25s, padding-left .25s; }
.dest-item:last-child { margin-bottom:0; }
.dest-item:hover { border-left-color:var(--accent); padding-left:1.7rem; }
.dest-item__title { font-family:'Shippori Mincho',serif; font-weight:700; font-size:1.12rem; color:var(--ink); line-height:1.5; }
.dest-item__year { font-family:'Cormorant Garamond',serif; font-style:italic; font-size:.92rem; color:var(--accent); margin-left:.55rem; }
.dest-item__meta { font-family:'Zen Kaku Gothic Antique',sans-serif; font-weight:500; font-size:.84rem; color:var(--ink-soft); letter-spacing:.04em; margin-top:.3rem; }
.dest-item__note { font-size:.83rem; color:var(--ink-mute); line-height:1.75; margin-top:.3rem; }

/* その他受賞・メディア 行 */
.acc-row { display:grid; grid-template-columns:1fr auto; gap:1.1rem; align-items:start;
  padding:1.15rem 0; border-bottom:1px solid var(--line); text-decoration:none; color:inherit; transition:padding-left .25s; }
.acc-row:hover { padding-left:.5rem; }
.acc-row:last-child { border-bottom:none; }
.acc-row__title { font-family:'Shippori Mincho',serif; font-weight:700; font-size:1.02rem; color:var(--ink); line-height:1.55; }
.acc-row__brewery { font-size:.85rem; color:var(--ink-soft); margin-top:.3rem; }
.acc-row__right { text-align:right; white-space:nowrap; }
.acc-row__year { font-family:'Cormorant Garamond',serif; font-style:italic; font-size:1.05rem; color:var(--accent); }
.acc-row__pref { display:block; font-size:.8rem; color:var(--ink-mute); margin-top:.2rem; }
"""



# 受賞データの brand 名から銘柄ページを特定する。
# 部分一致だと「花風」が3銘柄に当たるなど誤リンクするため、確実なものだけ明示する。
AWARD_BRAND_INDEX = {
    ("ine-to-agave", "稲とアガベ OGAラベル"): 0,      # 通常版「稲とアガベ」
    ("haccoba", "水を編む シリーズ"): 4,
    ("linne", "800 大麦 樽熟成"): 0,
    ("dejima-hosendo", "芳扇 吟雲（九州初作付・初収穫の美山錦100%どぶろく）"): 2,
}


def award_brand_href(slug, brand_name):
    """受賞銘柄の個別ページがあればそのパスを返す。特定できなければ None。"""
    if not brand_name:
        return None
    i = AWARD_BRAND_INDEX.get((slug, brand_name))
    if i is None:
        return None
    return f"../brand/{slug}-{i}.html"


def gen_awards():
    """受賞・メディア・海外進出ハブ（殿堂デザイン）"""
    OUT = REPO_ROOT / "awards"
    OUT.mkdir(exist_ok=True)

    # 分類
    icc_entries = []      # (slug, it)  ICC SAKE AWARD
    other_awards = []     # (slug, it)  ICC以外の受賞
    global_entries = []   # (slug, it)
    media_entries = []    # (slug, it)
    for slug, items in AWARDS.items():
        for it in items:
            if it["type"] == "award":
                if "ICC SAKE AWARD" in it["title"]:
                    icc_entries.append((slug, it))
                else:
                    other_awards.append((slug, it))
            elif it["type"] == "global":
                global_entries.append((slug, it))
            elif it["type"] == "media":
                media_entries.append((slug, it))

    # ICC: ランク序列でソート
    def rank_meta(title):
        if "準優勝" in title:
            return (1, "準優勝", "2nd")
        if "優勝" in title:  # 優勝・初代優勝
            label = "初代優勝" if "初代" in title else "優勝"
            return (0, label, "win")
        if "第3位" in title:
            return (2, "第3位", "3rd")
        if "決勝進出" in title and "準決勝" not in title:
            return (3, "決勝進出", "fin")
        if "準決勝" in title:
            return (4, "準決勝", "fin")
        return (5, "出場", "fin")

    award_brewery_count = len(set(s for s, _ in icc_entries) | set(s for s, _ in other_awards))

    html = page_head("クラフトサケの受賞と海外進出", "ICC SAKE AWARD歴代の頂点、Disfrutar・Mugaritzでの提供、欧米アジア輸出 — クラフトサケと世界のつながり。", "/awards/")
    html += f"<style>{AWARDS_CSS}</style>"
    html += masthead("EXTRA — ACCOLADES & GLOBAL", f"{award_brewery_count} breweries awarded")
    html += hero(
        "— 実績で選ぶ ／ ACCOLADES & GLOBAL",
        '頂点と、<span class="accent">世界</span>から。',
        'まだ10年に満たない新ジャンルが、競技会で頂点を競い、世界のトップレストランに選ばれ、欧米アジアへ渡っていく。クラフトサケの"現在地"を、受賞と海外進出から見つける。',
        '評価の物差しがまだ固まっていない新ジャンルだからこそ、第三者の評価は銘柄選びの確かな手がかりになる。ここに載せているのは、コンテストの受賞歴や海外進出の実績を、蔵やコンテストの公式発表で確認できたものだけ。賞は「その年・その場での評価」であって絶対の序列ではないが、初めての一本を外したくないとき、贈り物で間違いたくないときの指針には十分役立つ。受賞銘柄から蔵のページへ進めば、同じ蔵の別の表現にも出会える。贈答用途なら<a href="../guide/gift.html">ギフトガイド</a>も合わせてどうぞ。'
    )
    html += '<div class="awards-wrap">'

    # ── No.01 ICC SAKE AWARD（墨の殿堂）──
    # 年別グルーピング（新しい年順）、各年内はランク序列
    by_year = defaultdict(list)
    for slug, it in icc_entries:
        by_year[it.get("year") or 0].append((slug, it))
    icc_rows = ""
    for y in sorted(by_year.keys(), reverse=True):
        ylabel = str(y) if y else "年不明"
        icc_rows += f'\n        <div class="icc-year">{ylabel}</div>'
        for slug, it in sorted(by_year[y], key=lambda x: rank_meta(x[1]["title"])[0]):
            b = by_slug(slug)
            if not b:
                continue
            _, label, variant = rank_meta(it["title"])
            brand_html = f'<div class="icc-row__brand">{it["brand"]}</div>' if it.get("brand") else ''
            _bh = award_brand_href(slug, it.get("brand"))
            _href = _bh or f"../brewery/{slug}.html"
            icc_rows += f"""
        <a class="icc-row" href="{_href}">
          <span class="rank-chip rank-chip--{variant}">{label}</span>
          <div><div class="icc-row__brewery">{b['name']}</div>{brand_html}</div>
        </a>"""
    html += f"""
  </div>
  <section class="icc">
    <svg class="icc__emblem" viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg" aria-label="ICC SAKE AWARD">
      <circle cx="110" cy="110" r="92" fill="none" stroke="#B33A2A" stroke-width="2.5"/>
      <circle cx="110" cy="110" r="83" fill="none" stroke="#B33A2A" stroke-width="1"/>
      <g fill="#B33A2A"><path d="M88 51l5 7-5 7-5-7z"/><path d="M110 49l5.5 8-5.5 8-5.5-8z"/><path d="M132 51l5 7-5 7-5-7z"/></g>
      <text x="110" y="120" text-anchor="middle" font-family="'Cormorant Garamond', serif" font-weight="700" font-size="58" letter-spacing="4" fill="#E8917B">ICC</text>
      <line x1="68" y1="134" x2="152" y2="134" stroke="#B33A2A" stroke-width="0.8" opacity="0.55"/>
      <text x="110" y="156" text-anchor="middle" font-family="'Zen Kaku Gothic Antique', sans-serif" font-weight="700" font-size="16" letter-spacing="6" fill="#D9694F">SAKE AWARD</text>
    </svg>
    <div class="icc__inner">
      <div class="icc__eyebrow">— No.01 ／ ICC SAKE AWARD</div>
      <h2 class="icc__title">クラフトサケ、<br>歴代の頂点。</h2>
      <p class="icc__desc">ICCサミットが主催するSAKEの品評会「ICC SAKE AWARD」。米×副原料の新ジャンルが、年に一度ここで頂点を競う。saketto収録の蔵が刻んだ戦績を、序列で並べた。</p>
      <div class="icc-list">{icc_rows}
      </div>
    </div>
  </section>
  <div class="awards-wrap">"""

    # ── No.02 GLOBAL ──
    def dest_label(it):
        t = it["title"]
        if "Disfrutar" in t or "Mugaritz" in t:
            return "SPAIN"
        if "欧米" in t:
            return "USA / EUROPE"
        if "アジア" in t:
            return "ASIA"
        if "イタリア" in t or "ITALY" in t:
            return "ITALY"
        return "GLOBAL"

    # 地域でグルーピング（物語順）。地名を主役にした旅程インデックス
    region_groups = defaultdict(list)
    for slug, it in global_entries:
        region_groups[dest_label(it)].append((slug, it))
    region_order = ["SPAIN", "USA / EUROPE", "ITALY", "ASIA", "GLOBAL"]
    ordered_regions = [r for r in region_order if r in region_groups] + \
                      [r for r in region_groups if r not in region_order]

    dest_html = ""
    for region in ordered_regions:
        items = region_groups[region]
        disp = region.replace(" / ", " · ")
        item_rows = ""
        for slug, it in items:
            b = by_slug(slug)
            if not b:
                continue
            yr = f'<span class="dest-item__year">{it["year"]}</span>' if it.get("year") else ''
            note = f'<div class="dest-item__note">{it["brand"]}</div>' if it.get("brand") else ''
            item_rows += f"""
        <a class="dest-item" href="../brewery/{slug}.html">
          <div class="dest-item__title">{it['title']}{yr}</div>
          <div class="dest-item__meta">{b['name']}（{b['prefecture']}）</div>{note}
        </a>"""
        dest_html += f"""
      <div class="dest-group">
        <div class="dest-head"><span class="dest-head__name">{disp}</span><span class="dest-head__rule"></span><span class="dest-head__count">{len(items)} 件</span></div>{item_rows}
      </div>"""
    html += f"""
  <section class="awards-sec">
    <div class="section-meta"><span class="section-meta__num">No. 02</span><span class="section-meta__label">GLOBAL EXPANSION</span><span class="section-meta__count">/ {len(set(s for s,_ in global_entries))} 蔵</span><span class="section-meta__rule"></span></div>
    <h2 class="cat-title">世界へ、渡っていく。</h2>
    <p class="awards-sec__desc">世界ベストレストラン2024年1位「Disfrutar」、旧3つ星「Mugaritz」が選んだ遠野のどぶろく。欧米・アジアへの輸出、海外法人の設立 — クラフトサケはもう国境を越えている。</p>
    {dest_html}
  </section>"""

    # ── No.03 その他の受賞 ──
    def acc_row(slug, it, show_pref=True):
        b = by_slug(slug)
        if not b:
            return ""
        brand_html = f'<div class="acc-row__brewery">{b["name"]}{("／" + it["brand"]) if it.get("brand") else ""}</div>'
        yr = f'<span class="acc-row__year">{it["year"]}</span>' if it.get("year") else ''
        pref = f'<span class="acc-row__pref">{b["prefecture"]}</span>' if show_pref else ''
        return f"""
      <a class="acc-row" href="../brewery/{slug}.html">
        <div><div class="acc-row__title">{it['title']}</div>{brand_html}</div>
        <div class="acc-row__right">{yr}{pref}</div>
      </a>"""

    other_rows = "".join(acc_row(s, it) for s, it in sorted(other_awards, key=lambda x: -(x[1].get("year") or 0)))
    html += f"""
  <section class="awards-sec">
    <div class="section-meta"><span class="section-meta__num">No. 03</span><span class="section-meta__label">OTHER ACCOLADES</span><span class="section-meta__count">/ {len(other_awards)} 件</span><span class="section-meta__rule"></span></div>
    <h2 class="cat-title">その他の受賞。</h2>
    <p class="awards-sec__desc">日本パッケージデザイン大賞、東北アントレプレナー大賞、Tokyo酒チャレンジ金賞 — 味だけでなく、デザイン・起業・品質でも評価される。</p>
    <div>{other_rows}
    </div>
  </section>"""

    html += '</div>'
    html += footer()

    out = OUT / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"  awards/index.html  (ICC{len(icc_entries)} / 海外{len(global_entries)} / 他受賞{len(other_awards)} ※メディア非掲載)")


def gen_breweries_hub():
    """蔵ハブ（4軸の「蔵」の受けページ。従来は index.html#breweries アンカーのみで非対称だった）"""
    OUT = REPO_ROOT / "brewery"
    OUT.mkdir(exist_ok=True)

    total = len(BREWERIES)
    assoc = sum(1 for b in BREWERIES if b.get("association"))
    indep = total - assoc

    html = page_head(
        "クラフトサケの蔵から探す",
        f"全国のクラフトサケ醸造所{total}蔵（協会加盟{assoc}＋独立系{indep}）を一覧で横断。所在地・創業・特徴・収録銘柄まで、公式サイトで一次確認した情報だけを収録した蔵の索引。",
        "/brewery/")
    html += masthead("AXIS 02 — BREWERIES", f"{total} breweries")
    html += hero(
        "— ALL BREWERIES",
        '蔵から、<span class="accent">探す</span>。',
        f'クラフトサケは、蔵の思想がそのまま味になる酒。震災復興の東北から、駅ナカの都市型、南国素材の蔵まで、{total}蔵の物語から次の一本を選ぶ。',
        'クラフトサケの蔵は、そのほとんどが2020年代に生まれたばかり。だからこそ、どの蔵にも「なぜ酒を造るのか」の物語が色濃く残っている。蔵のページでは、成り立ちと哲学、仕込みの特徴、収録銘柄までまとめて読める。土地から辿りたいなら<a href="../region/">地域から探す</a>、造りの系統で選びたいなら<a href="../genre/">ジャンルから探す</a>も合わせてどうぞ。'
    )
    html += '<div style="max-width:1100px; margin:0 auto; padding:0 2rem 2rem">'
    html += f"""
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. 01</span>
      <h2 class="section-meta__label">ALL BREWERIES</h2>
      <span class="section-meta__count">/ {total} 蔵</span>
      <span class="section-meta__rule"></span>
    </div>
    <div class="brewery-grid">"""
    for i, b in enumerate(BREWERIES, 1):
        html += render_brewery_card(b, i, picks=brand_picks(b))
    html += """
    </div>
  </section>"""
    html += '</div>'
    html += footer()

    out_path = OUT / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"  brewery/index.html  ({total}蔵の索引)")


def main():
    print("生成中...")
    gen_subingredients()
    gen_breweries_hub()
    gen_regions()
    gen_genres()
    gen_furusato()
    gen_awards()
    print("\n✓ 6ハブページ生成完了（副原料・蔵・地域・ジャンル・ふるさと納税・受賞）")


if __name__ == "__main__":
    main()

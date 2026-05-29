# -*- coding: utf-8 -*-
"""saketto / 逆引きハブページ生成スクリプト

副原料軸・地域軸・ジャンル軸・入手性軸の4ハブページを生成する。
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
from furusato_data import FURUSATO, PORTAL_NAMES


REPO_ROOT = Path(__file__).resolve().parent.parent  # saketto_repo/


# ────────────── 共通CSS（簡易・蔵詳細と同系統） ──────────────

CSS = """
:root {
  --bg: #F5F0E7; --bg-alt: #EDE5D2; --paper: #FAF6ED;
  --ink: #1A1717; --ink-soft: #4A4441; --ink-mute: #7A7470;
  --accent: #B33A2A; --accent-deep: #862719;
  --warm: #8B7355; --line: #C9BFA8; --line-soft: #DFD5BD;
}
* { margin:0; padding:0; box-sizing:border-box; }
html { scroll-behavior:smooth; }
body {
  background:var(--bg); color:var(--ink);
  font-family:'Noto Sans JP', sans-serif; font-weight:300;
  line-height:1.75; -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility;
  overflow-x:hidden;
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
  font-family:'Zen Kaku Gothic Antique', sans-serif;
  font-size:.7rem; letter-spacing:.2em; color:var(--ink-mute); text-transform:uppercase;
}
.masthead a { color:var(--ink-mute); text-decoration:none; transition:color .25s; }
.masthead a:hover { color:var(--accent); }
.masthead .accent-dot { width:5px; height:5px; background:var(--accent); border-radius:50%; display:inline-block; margin-right:.5rem; }
.masthead .left { display:flex; gap:1.5rem; align-items:center; }
.masthead .right { font-family:'Cormorant Garamond', serif; font-style:italic; letter-spacing:.1em; }

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
  font-size:.95rem; color:var(--ink-soft); max-width:680px;
  border-left:2px solid var(--accent); padding-left:1.5rem; line-height:1.95;
}

.section { max-width:1100px; margin:0 auto; padding:0 2rem 4rem; }
.section-meta {
  display:flex; align-items:baseline; gap:1.25rem; margin-bottom:1.5rem;
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
.section-meta__count {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.9rem; color:var(--ink-mute); letter-spacing:.1em;
}
.section-meta__rule { flex:1; height:1px; background:var(--line); }

.cat-title {
  font-family:'Shippori Mincho', serif; font-weight:600;
  font-size:1.5rem; letter-spacing:.02em; color:var(--ink);
  margin-bottom:.5rem;
}
.cat-title .accent { color:var(--accent); }
.cat-desc {
  font-size:.85rem; color:var(--ink-soft); margin-bottom:1.25rem; line-height:1.7;
}

.entries {
  display:flex; flex-direction:column; gap:.5px;
  background:var(--line); border:1px solid var(--line);
  margin-bottom:3rem;
}
.entry {
  background:var(--bg); padding:1.1rem 1.5rem;
  display:grid; grid-template-columns:1fr; gap:.4rem;
  transition:background .3s;
  text-decoration:none; color:var(--ink);
}
@media (min-width:760px) {
  .entry { grid-template-columns:1.5fr 1fr 1fr; align-items:center; gap:1rem; }
}
.entry:hover { background:var(--paper); }
.entry__brand {
  font-family:'Shippori Mincho', serif; font-weight:500;
  font-size:1rem; color:var(--ink);
}
.entry__brewery {
  font-family:'Zen Kaku Gothic Antique', sans-serif;
  font-size:.78rem; color:var(--ink-soft); letter-spacing:.04em;
}
.entry__brewery::before { content:"— "; color:var(--accent); }
.entry__specs { display:flex; gap:.35rem; flex-wrap:wrap; }
.spec-pill {
  font-family:'Zen Kaku Gothic Antique', sans-serif;
  font-size:.68rem; letter-spacing:.04em; color:var(--ink-soft);
  background:var(--bg-alt); padding:.2rem .55rem;
}
.spec-pill.accent { color:var(--accent); background:transparent; border:1px solid var(--accent); }
.spec-pill.warm { color:var(--warm); background:transparent; border:1px solid var(--warm); }

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
  font-size:.75rem; color:var(--accent); letter-spacing:.1em;
}
.brewery-card__name {
  font-family:'Shippori Mincho', serif; font-weight:600;
  font-size:1.15rem; color:var(--ink);
}
.brewery-card__meta {
  font-family:'Zen Kaku Gothic Antique', sans-serif;
  font-size:.72rem; color:var(--ink-soft); letter-spacing:.05em;
}
.brewery-card__features {
  font-size:.78rem; color:var(--ink-soft); line-height:1.6; margin-top:.25rem;
}

.empty-region {
  background:var(--bg-alt); padding:2rem; border-left:2px solid var(--warm);
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
  font-family:'Zen Kaku Gothic Antique', sans-serif;
  font-size:.75rem; color:var(--ink-soft); line-height:1.95; letter-spacing:.04em;
}
.colophon__notes strong { color:var(--accent); font-weight:500; }
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
    if "ホップ" in s:
        return "hop"
    if any(k in s for k in ["リンゴ", "りんご", "ブドウ", "ぶどう", "洋梨", "洋ナシ",
                            "ル・レクチェ", "ル レクチエ", "メロン", "イチゴ",
                            "あまおう", "越後姫", "桃", "マンゴー", "パイナップル",
                            "パイン", "シークワーサー", "アセロラ", "ミカン",
                            "黒イチジク", "ハニーレモン", "果汁", "果物",
                            "柚子", "八朔", "ブルーベリー"]):
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


def get_brewery_genres(brewery):
    """蔵を複数のジャンルに分類（重複OK）"""
    slug = brewery["slug"]
    brands = BRANDS.get(slug, [])
    features = brewery.get("features", "") + brewery.get("philosophy", "")
    genres = set()

    for b in brands:
        ings = b.get("sub_ingredients") or []
        name = b.get("name", "")
        note = b.get("note", "")
        all_text = " ".join(ings) + " " + name + " " + note

        if "ホップ" in all_text:
            genres.add("hop-sake")
        if any(k in all_text for k in ["リンゴ", "ブドウ", "洋梨", "メロン", "イチゴ",
                                        "あまおう", "桃", "マンゴー", "パイナップル",
                                        "シークワーサー", "アセロラ", "黒イチジク",
                                        "ハニーレモン", "果汁", "果物", "ル・レクチェ",
                                        "ル レクチエ", "ぶどう", "りんご", "八朔",
                                        "ブルーベリー", "ミカン"]):
            genres.add("fruit-sake")
        if "どぶろく" in name or "ドブロク" in name or "ドブロク" in note:
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


# ────────────── 入手性分類 ──────────────

AVAILABILITY = [
    ("online", "通販可", "ONLINE", "公式EC・酒販ECで誰でも入手可能な蔵。"),
    ("tokuyaku", "特約店中心", "TOKUYAKU ONLY", "特約店を通じた流通が中心。公式ECがない or 限定的。"),
    ("rare", "極希少・限定流通", "EXTREMELY RARE", "本数限定・抽選販売・現地限定など、入手が困難な銘柄を中心に持つ蔵。"),
]


def get_brewery_availability(brewery):
    """蔵の入手性カテゴリを判定"""
    slug = brewery["slug"]
    brands = BRANDS.get(slug, [])
    features = brewery.get("features", "")

    # 極希少：限定本数・限定数本・限定 等の記述
    rare_keywords = ["限定本数", "限定数本", "限定100本", "限定192本", "限定約100",
                     "100本限定", "192本限定", "抽選", "現地限定"]
    rare_count = sum(1 for b in brands for kw in rare_keywords
                     if kw in b.get("note", ""))
    if rare_count >= 2:
        return "rare"

    # 特約店中心：特約店扱い・公式EC不明
    tokuyaku_count = sum(1 for b in brands if "特約店" in b.get("note", ""))
    if tokuyaku_count >= 2 or "特約店" in features:
        return "tokuyaku"

    # それ以外は通販可（公式ECある前提）
    return "online"


# ────────────── HTML テンプレート ──────────────

def page_head(title, description):
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — saketto.</title>
<meta name="description" content="{description}">
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@300;400;500&family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<main>
"""


def masthead(label, right_text):
    return f"""
  <div class="masthead">
    <div class="left">
      <a href="../index.html"><span class="accent-dot"></span>SAKETTO</a>
      <span>{label}</span>
    </div>
    <div class="right">{right_text}</div>
  </div>
"""


def hero(eyebrow, title_html, lede):
    return f"""
  <section class="hero">
    <div class="hero__eyebrow">{eyebrow}</div>
    <h1 class="hero__title">{title_html}</h1>
    <p class="hero__lede">{lede}</p>
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
    return """
  <footer>
    <div class="colophon">
      <div class="colophon__brand">
        <a href="../index.html">saketto<span class="dot">.</span></a>
        <small>— クラフトサケの図鑑</small>
      </div>
      <div class="colophon__notes">
        <strong>準備中</strong><span class="colophon__sep">／</span>
        2026年夏、本サイト公開予定<span class="colophon__sep">／</span>
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


def render_entry(brewery_slug, brand):
    """副原料カテゴリページ内の1エントリ(蔵×銘柄)を描画"""
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
        <a class="entry" href="../brewery/{brewery_slug}.html">
          <div>
            <div class="entry__brand">{brand['name']}</div>
            <div class="entry__brewery">{b['name']}</div>
          </div>
          <div class="entry__specs">{specs_html}</div>
          <div class="entry__brewery" style="text-align:right">{b['prefecture']}</div>
        </a>"""


def render_brewery_card(brewery, idx):
    return f"""
      <a class="brewery-card" href="../brewery/{brewery['slug']}.html">
        <div class="brewery-card__num">No. {idx:02d}</div>
        <div class="brewery-card__name">{brewery['name']}</div>
        <div class="brewery-card__meta">{brewery['prefecture']}・{brewery['city']}　/　創業 {brewery['founded']}</div>
        <div class="brewery-card__features">{brewery['features']}</div>
      </a>"""


# ────────────── 各ハブ生成 ──────────────

def gen_subingredients():
    """副原料逆引きハブ"""
    OUT = REPO_ROOT / "subingredients"
    OUT.mkdir(exist_ok=True)

    # カテゴリ別に銘柄を集計
    by_cat = defaultdict(list)  # cat -> [(brewery_slug, brand)]
    for brewery in BREWERIES:
        for brand in BRANDS.get(brewery["slug"], []):
            ings = brand.get("sub_ingredients") or []
            cats_for_this = set()
            for ing in ings:
                cat = categorize_ingredient(ing)
                if cat:
                    cats_for_this.add(cat)
            for cat in cats_for_this:
                by_cat[cat].append((brewery["slug"], brand))

    total_brands = sum(len(v) for v in by_cat.values())

    html = page_head("副原料から探す", "クラフトサケを副原料（ホップ・果実・茶葉・ハーブ・米のみ・特殊副原料）から横断的に検索する逆引きデータベース。")
    html += masthead("AXIS 01 — SUB-INGREDIENTS", f"5 categories")
    html += hero(
        "— FIVE CATEGORIES",
        '副原料から、<span class="accent">探す</span>。',
        '何を入れた酒か。クラフトサケの自由さを最も雄弁に語るのが副原料。ホップから茶葉、ハーブ、果実、そして米と麹のみまで、5つのカテゴリで横断する。'
    )
    html += '<div style="max-width:1100px; margin:0 auto; padding:0 2rem 2rem">'

    SUB_IMG_MAP = {"hop":"sub_hop", "fruit":"sub_fruit", "tea-herb":"sub_tea_herb",
                   "rice-koji":"sub_rice", "special":"sub_special"}
    for cat_key, cat_jp, cat_en, cat_desc in INGREDIENT_CATEGORIES:
        entries = by_cat.get(cat_key, [])
        img_name = SUB_IMG_MAP.get(cat_key, "")
        img_html = (
            f'<figure class="cat-image"><img src="../assets/images/{img_name}.png" alt="" loading="lazy">'
            f'<span class="cat-image__cap">画像はイメージ</span></figure>'
        ) if img_name else ''
        html += f"""
  <section class="section" style="padding-bottom:2rem">
    <div class="section-meta">
      <span class="section-meta__num">No. {INGREDIENT_CATEGORIES.index((cat_key, cat_jp, cat_en, cat_desc))+1:02d}</span>
      <span class="section-meta__label">{cat_en}</span>
      <span class="section-meta__count">/ {len(entries)} 銘柄</span>
      <span class="section-meta__rule"></span>
    </div>
    {img_html}
    <h2 class="cat-title">{cat_jp}</h2>
    <p class="cat-desc">{cat_desc}</p>
    <div class="entries">"""
        for slug, brand in entries:
            html += render_entry(slug, brand)
        html += """
    </div>
  </section>"""

    html += '</div>'
    html += footer()

    out_path = OUT / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"  subingredients/index.html  ({total_brands}件の副原料エントリ)")


def gen_regions():
    """地域逆引きハブ"""
    OUT = REPO_ROOT / "region"
    OUT.mkdir(exist_ok=True)

    by_region = defaultdict(list)
    for b in BREWERIES:
        by_region[b["region"]].append(b)

    populated = [r for r in REGIONS if by_region[r]]
    empty = [r for r in REGIONS if not by_region[r]]

    html = page_head("地域から探す", "全国のクラフトサケ醸造所を9地域別に横断検索する逆引きデータベース。")
    html += masthead("AXIS 03 — REGION", f"{len(populated)} regions populated")
    html += hero(
        "— BY REGION",
        '地域から、<span class="accent">探す</span>。',
        f'クラフトサケは復興と再生の文脈と深く結びついている。福島・宮城・岩手といった東北、首都圏の都市型、関西の団地酒蔵、九州・沖縄の南国素材まで、{len(BREWERIES)}蔵が日本列島に散らばる。'
    )

    html += '<div style="max-width:1100px; margin:0 auto; padding:0 2rem 2rem">'

    REGION_IMG_MAP = {
        "東北": "region_tohoku", "関東": "region_kanto", "中部": "region_chubu",
        "関西": "region_kansai", "九州": "region_kyushu", "沖縄": "region_okinawa",
    }
    for idx, region in enumerate(populated, 1):
        breweries = by_region[region]
        img_name = REGION_IMG_MAP.get(region, "")
        img_html = (
            f'<figure class="cat-image"><img src="../assets/images/{img_name}.png" alt="" loading="lazy">'
            f'<span class="cat-image__cap">画像はイメージ</span></figure>'
        ) if img_name else ''
        html += f"""
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. {idx:02d}</span>
      <span class="section-meta__label">{region}</span>
      <span class="section-meta__count">/ {len(breweries)} 蔵</span>
      <span class="section-meta__rule"></span>
    </div>
    {img_html}
    <div class="brewery-grid">"""
        for i, b in enumerate(breweries, 1):
            html += render_brewery_card(b, i)
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

    html = page_head("ジャンルから探す", "クラフトサケのジャンル（ホップサケ・果実サケ・古典どぶろく・全麹酒・木桶仕込み・異素材麹・茶葉ハーブサケ）から横断検索。saketto独自軸。")
    html += masthead("AXIS 04 — GENRE / SAKETTO独自", "7 genres")
    html += hero(
        "— SAKETTO ORIGINAL AXIS",
        'ジャンルから、<span class="accent">探す</span>。',
        '副原料の選び方、製法の系譜、麹の素材。クラフトサケの中にも明確な"系"がある。これはsaketto独自の分類軸。'
    )
    html += '<div style="max-width:1100px; margin:0 auto; padding:0 2rem 2rem">'

    for idx, (g_key, g_jp, g_en, g_desc) in enumerate(GENRES, 1):
        breweries = by_genre.get(g_key, [])
        if not breweries:
            continue
        html += f"""
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. {idx:02d}</span>
      <span class="section-meta__label">{g_en}</span>
      <span class="section-meta__count">/ {len(breweries)} 蔵</span>
      <span class="section-meta__rule"></span>
    </div>
    <h2 class="cat-title">{g_jp}</h2>
    <p class="cat-desc">{g_desc}</p>
    <div class="brewery-grid">"""
        for i, b in enumerate(breweries, 1):
            html += render_brewery_card(b, i)
        html += """
    </div>
  </section>"""

    html += '</div>'
    html += footer()

    out_path = OUT / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"  genre/index.html  ({len([g for g in GENRES if by_genre.get(g[0])])}ジャンル)")


def gen_availability():
    """入手性逆引きハブ（saketto独自）"""
    OUT = REPO_ROOT / "availability"
    OUT.mkdir(exist_ok=True)

    by_avail = defaultdict(list)
    for brewery in BREWERIES:
        a = get_brewery_availability(brewery)
        by_avail[a].append(brewery)

    html = page_head("入手性から探す", "クラフトサケを入手性（通販可・特約店中心・極希少）から横断検索。saketto独自軸。")
    html += masthead("AXIS 05 — AVAILABILITY / SAKETTO独自", f"{len(BREWERIES)} breweries classified")
    html += hero(
        "— SAKETTO ORIGINAL AXIS",
        '入手性から、<span class="accent">探す</span>。',
        'クラフトサケは少量生産が前提。誰でもネットで買える蔵もあれば、特約店経由でしか買えない蔵、限定本数で即完売する蔵も。「いつでも飲める酒」と「狙い撃ちすべき酒」を分ける軸。'
    )
    html += '<div style="max-width:1100px; margin:0 auto; padding:0 2rem 2rem">'

    for idx, (a_key, a_jp, a_en, a_desc) in enumerate(AVAILABILITY, 1):
        breweries = by_avail.get(a_key, [])
        html += f"""
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. {idx:02d}</span>
      <span class="section-meta__label">{a_en}</span>
      <span class="section-meta__count">/ {len(breweries)} 蔵</span>
      <span class="section-meta__rule"></span>
    </div>
    <h2 class="cat-title">{a_jp}</h2>
    <p class="cat-desc">{a_desc}</p>
    <div class="brewery-grid">"""
        for i, b in enumerate(breweries, 1):
            html += render_brewery_card(b, i)
        html += """
    </div>
  </section>"""

    html += '</div>'
    html += footer()

    out_path = OUT / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"  availability/index.html  ({len(BREWERIES)}蔵分類)")


def gen_furusato():
    """ふるさと納税逆引きハブ"""
    OUT = REPO_ROOT / "furusato"
    OUT.mkdir(exist_ok=True)

    confirmed = [b for b in BREWERIES if b["slug"] in FURUSATO]
    not_confirmed = [b for b in BREWERIES if b["slug"] not in FURUSATO]

    html = page_head("ふるさと納税から探す", "クラフトサケのふるさと納税返礼品を一次ソース確認の上で横断検索。")
    html += masthead("EXTRA — FURUSATO TAX", f"{len(confirmed)} confirmed")
    html += hero(
        "— TAX-DEDUCTIBLE DISCOVERY",
        'ふるさと納税から、<span class="accent">支援する</span>。',
        f'クラフトサケのふるさと納税返礼品を一次ソース確認の上で集約。寄附で蔵を支えながら、地域の挑戦と希少な酒に出会える。確認できた {len(confirmed)} 蔵のみ掲載、残り {len(not_confirmed)} 蔵は今後の出品を追跡。'
    )
    html += '<div style="max-width:1100px; margin:0 auto; padding:0 2rem 2rem">'

    html += f"""
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. 01</span>
      <span class="section-meta__label">CONFIRMED LISTINGS</span>
      <span class="section-meta__count">/ {len(confirmed)} 蔵</span>
      <span class="section-meta__rule"></span>
    </div>
    <div class="entries">"""

    for b in confirmed:
        data = FURUSATO[b["slug"]]
        portals_html = ' '.join(
            f'<span class="spec-pill accent">{PORTAL_NAMES.get(p, p)}</span>'
            for p in data["portals"]
        )
        yen = f'¥{data["donation_yen"]:,}〜' if data.get("donation_yen") else '寄附額確認中'
        rep = data.get("rep_brand", "")
        html += f"""
      <a class="entry" href="../brewery/{b['slug']}.html">
        <div>
          <div class="entry__brand">{b['name']}</div>
          <div class="entry__brewery">{data['city']}　/　{rep}</div>
        </div>
        <div class="entry__specs">{portals_html}</div>
        <div class="entry__brewery" style="text-align:right">{yen}</div>
      </a>"""

    html += """
    </div>
  </section>"""

    html += f"""
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. 02</span>
      <span class="section-meta__label">PENDING / NOT YET LISTED</span>
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
    html += footer()

    out = OUT / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"  furusato/index.html  ({len(confirmed)}社確認 / {len(not_confirmed)}社未確認)")


def gen_awards():
    """受賞・メディア・海外進出ハブ"""
    OUT = REPO_ROOT / "awards"
    OUT.mkdir(exist_ok=True)

    awarded_slugs = []
    media_slugs = []
    global_slugs = []
    for slug, items in AWARDS.items():
        if any(it["type"] == "award" for it in items):
            awarded_slugs.append(slug)
        if any(it["type"] == "media" for it in items):
            media_slugs.append(slug)
        if any(it["type"] == "global" for it in items):
            global_slugs.append(slug)

    html = page_head("受賞・メディア・海外進出", "クラフトサケのICC SAKE AWARD等の受賞、業界メディア露出、海外進出を横断的に追跡。")
    html += masthead("EXTRA — ACCOLADES & MEDIA", f"{len(awarded_slugs)} awarded")
    html += hero(
        "— ACCOLADES & EXPOSURE",
        '受賞と<span class="accent">海外進出</span>から、見つける。',
        'ICC SAKE AWARD、Tokyo酒チャレンジ、日本パッケージデザイン大賞、Mugaritz・Disfrutarでの提供、欧米輸出開始 — クラフトサケと「世界」のつながりを一覧する。'
    )
    html += '<div style="max-width:1100px; margin:0 auto; padding:0 2rem 2rem">'

    def render_award_entry(slug, it):
        b = by_slug(slug)
        if not b:
            return ""
        year_html = f'<span class="spec-pill accent">{it["year"]}</span>' if it.get("year") else ''
        brand_part = f"（{it['brand']}）" if it.get('brand') else ''
        return f"""
      <a class="entry" href="../brewery/{slug}.html">
        <div>
          <div class="entry__brand">{it['title']}</div>
          <div class="entry__brewery">{b['name']}{brand_part}</div>
        </div>
        <div class="entry__specs">{year_html}</div>
        <div class="entry__brewery" style="text-align:right">{b['prefecture']}</div>
      </a>"""

    # AWARDS section
    html += f"""
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. 01</span>
      <span class="section-meta__label">AWARDS</span>
      <span class="section-meta__count">/ {len(awarded_slugs)} 蔵</span>
      <span class="section-meta__rule"></span>
    </div>
    <h2 class="cat-title">受賞</h2>
    <p class="cat-desc">ICC SAKE AWARD、Tokyo酒チャレンジ、日本パッケージデザイン大賞、東北アントレプレナー大賞ほか。</p>
    <div class="entries">"""
    for slug in awarded_slugs:
        for it in AWARDS[slug]:
            if it["type"] == "award":
                html += render_award_entry(slug, it)
    html += """
    </div>
  </section>"""

    # GLOBAL section
    html += f"""
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. 02</span>
      <span class="section-meta__label">GLOBAL EXPANSION</span>
      <span class="section-meta__count">/ {len(global_slugs)} 蔵</span>
      <span class="section-meta__rule"></span>
    </div>
    <h2 class="cat-title">海外進出・国際的提供</h2>
    <p class="cat-desc">輸出開始、海外法人設立、ミシュランレストランでの提供などクラフトサケの世界展開。</p>
    <div class="entries">"""
    for slug in global_slugs:
        for it in AWARDS[slug]:
            if it["type"] == "global":
                html += render_award_entry(slug, it)
    html += """
    </div>
  </section>"""

    # MEDIA section
    html += f"""
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. 03</span>
      <span class="section-meta__label">MEDIA SPOTLIGHTS</span>
      <span class="section-meta__count">/ {len(media_slugs)} 蔵</span>
      <span class="section-meta__rule"></span>
    </div>
    <h2 class="cat-title">メディア露出</h2>
    <p class="cat-desc">Forbes JAPAN、dancyu、日経新聞、Diamond、経済産業省METI Journal等での主要露出。</p>
    <div class="entries">"""
    for slug in media_slugs:
        for it in AWARDS[slug]:
            if it["type"] == "media":
                html += render_award_entry(slug, it)
    html += """
    </div>
  </section>"""

    html += '</div>'
    html += footer()

    out = OUT / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"  awards/index.html  (受賞{len(awarded_slugs)} / 海外{len(global_slugs)} / メディア{len(media_slugs)})")


def main():
    print("生成中...")
    gen_subingredients()
    gen_regions()
    gen_genres()
    gen_availability()
    gen_furusato()
    gen_awards()
    print("\n✓ 6ハブページ生成完了")


if __name__ == "__main__":
    main()

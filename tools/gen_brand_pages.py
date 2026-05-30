# -*- coding: utf-8 -*-
"""saketto / 銘柄詳細ページ生成

実行: cd ツール/saketto_repo/tools && python gen_brand_pages.py
出力: ../brand/{brewery_slug}-{idx}.html × 全銘柄
URL: /brand/ine-to-agave-0.html などのパターン
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from breweries_master import BREWERIES, by_slug
from breweries_brands import BRANDS
from tasting import TASTING

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "brand"
OUT_DIR.mkdir(exist_ok=True)


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
    radial-gradient(ellipse 1.5px 2.2px at 18% 22%, rgba(168,53,31,0.03) 60%, transparent 70%),
    radial-gradient(ellipse 1.2px 1.8px at 67% 38%, rgba(122,100,71,0.035) 60%, transparent 70%);
  background-size: 64px 64px, 96px 96px;
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
.masthead a { color:var(--ink-soft); text-decoration:none; transition:color .25s; }
.masthead a:hover { color:var(--accent); }
.masthead .accent-dot { width:5px; height:5px; background:var(--accent); border-radius:50%; display:inline-block; margin-right:.5rem; }
.masthead .left { display:flex; gap:1.5rem; align-items:center; }
.masthead .right { font-family:'Cormorant Garamond', serif; font-style:italic; letter-spacing:.1em; }

/* HERO */
.hero {
  max-width:1100px; margin:0 auto; padding:4rem 2rem 3rem;
}
.hero__brewery {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:1rem; color:var(--accent); letter-spacing:.1em;
  margin-bottom:.85rem;
}
.hero__brewery a {
  color:var(--accent); text-decoration:none;
  border-bottom:1px dotted var(--accent);
}
.hero__brewery a:hover { color:var(--accent-deep); }
.hero__name {
  font-family:'Shippori Mincho', serif; font-weight:700;
  font-size:clamp(2rem, 5.5vw, 3.6rem);
  letter-spacing:.01em; line-height:1.2; color:var(--ink);
  margin-bottom:1.2rem;
}
.hero__note {
  font-family:'Shippori Mincho', serif; font-weight:500;
  font-size:1.1rem; color:var(--ink-soft); line-height:1.75;
  margin-bottom:2.5rem; max-width:680px;
}

/* SPECS - 大判ディスプレイ */
.specs-board {
  display:grid; grid-template-columns:1fr; gap:0;
  border:1px solid var(--line); margin-bottom:3rem;
  background:var(--paper);
}
@media (min-width:640px) {
  .specs-board { grid-template-columns:repeat(3, 1fr); }
}
.spec-cell {
  padding:1.5rem 1.75rem;
  border-bottom:1px solid var(--line);
}
@media (min-width:640px) {
  .spec-cell { border-bottom:none; border-right:1px solid var(--line); }
  .spec-cell:last-child { border-right:none; }
}
.spec-cell:last-child { border-bottom:none; }
.spec-cell__label {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.85rem; color:var(--accent); letter-spacing:.1em;
  margin-bottom:.4rem;
}
.spec-cell__value {
  font-family:'Shippori Mincho', serif; font-weight:700;
  font-size:1.8rem; color:var(--ink); letter-spacing:.02em; line-height:1.2;
}
.spec-cell__value small {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.65em; color:var(--ink-soft); font-weight:400;
  margin-left:.25rem;
}
.spec-cell__unknown {
  font-family:'Shippori Mincho', serif; font-size:1.1rem;
  color:var(--ink-mute); font-weight:500;
}
.spec-cell__pills {
  display:flex; flex-wrap:wrap; gap:.4rem; margin-top:.3rem;
}
.pill {
  font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:500;
  font-size:.85rem; letter-spacing:.02em; color:var(--ink);
  background:var(--bg); padding:.3rem .7rem;
  border:1px solid var(--line);
}

/* PRICE */
.price-block {
  display:flex; justify-content:space-between; align-items:baseline;
  padding:1.5rem 0; border-top:1px solid var(--line); border-bottom:1px solid var(--line);
  margin-bottom:3rem; flex-wrap:wrap; gap:.5rem;
}
.price-block__label {
  font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:700;
  font-size:.85rem; letter-spacing:.18em; color:var(--ink);
  text-transform:uppercase;
}
.price-block__value {
  font-family:'Shippori Mincho', serif; font-weight:700;
  font-size:1.6rem; color:var(--ink);
}
.price-block__value small {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.65em; color:var(--ink-soft); font-weight:400;
  margin-left:.4rem;
}

/* SECTION */
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

/* TASTING */
.tasting-block {
  background:var(--paper); padding:2rem 2.25rem;
  border-left:3px solid var(--accent); margin-bottom:1rem;
}
.tasting-notes {
  font-family:'Shippori Mincho', serif; font-weight:500;
  font-size:1.1rem; color:var(--ink); line-height:1.95; margin-bottom:1.2rem;
}
.tasting-meta {
  display:flex; flex-wrap:wrap; gap:.5rem 1.5rem;
  font-size:.92rem; color:var(--ink-soft); margin-bottom:.8rem;
}
.tasting-meta__row { display:inline-flex; align-items:baseline; }
.tasting-meta strong {
  color:var(--accent); font-weight:700; margin-right:.5rem;
  font-family:'Zen Kaku Gothic Antique', sans-serif;
  font-size:.78rem; letter-spacing:.1em; text-transform:uppercase;
}
.tasting-source {
  font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.88rem; color:var(--ink-soft); padding-top:.85rem;
  border-top:1px dotted var(--line);
}
.tasting-source a { color:var(--ink); border-bottom:1px dotted var(--line); text-decoration:none; }
.tasting-source a:hover { color:var(--accent); border-bottom-color:var(--accent); }

/* KURA CONTEXT */
.kura-context {
  background:var(--bg-alt); padding:2rem 2.25rem; border:1px solid var(--line);
  margin-bottom:1rem;
}
.kura-context__name {
  font-family:'Shippori Mincho', serif; font-weight:700;
  font-size:1.35rem; color:var(--ink); margin-bottom:.4rem;
}
.kura-context__meta {
  font-family:'Zen Kaku Gothic Antique', sans-serif; font-weight:500;
  font-size:.85rem; color:var(--ink-soft); letter-spacing:.05em;
  margin-bottom:1rem;
}
.kura-context__philosophy {
  font-size:.95rem; color:var(--ink); line-height:1.85; margin-bottom:1rem;
}
.kura-context__link {
  display:inline-block; font-family:'Zen Kaku Gothic Antique', sans-serif;
  font-weight:700; font-size:.85rem; color:var(--accent); letter-spacing:.1em;
  text-transform:uppercase; text-decoration:none;
  border-bottom:1px solid var(--accent); padding-bottom:.15rem;
  transition:color .25s;
}
.kura-context__link:hover { color:var(--accent-deep); }

/* RELATED */
.related {
  display:grid; grid-template-columns:1fr; gap:0;
  border:1px solid var(--line);
}
@media (min-width:700px) { .related { grid-template-columns:repeat(2, 1fr); } }
.related-card {
  display:block; padding:1.1rem 1.4rem;
  background:var(--bg); color:var(--ink); text-decoration:none;
  border-bottom:1px solid var(--line);
  transition:background .3s, padding-left .3s;
}
@media (min-width:700px) {
  .related-card { border-right:1px solid var(--line); }
  .related-card:nth-child(2n) { border-right:none; }
}
.related-card:hover { background:var(--paper); padding-left:1.6rem; }
.related-card__name {
  font-family:'Shippori Mincho', serif; font-weight:600;
  font-size:1rem; color:var(--ink); margin-bottom:.2rem;
}
.related-card__sub {
  font-family:'Noto Sans JP', sans-serif; font-weight:400;
  font-size:.78rem; color:var(--ink-soft);
}

/* SOURCES */
.sources {
  background:var(--bg-alt); padding:1.75rem 2rem;
  font-family:'Zen Kaku Gothic Antique', sans-serif;
}
.sources h4 {
  font-size:.85rem; letter-spacing:.18em; color:var(--ink); font-weight:700;
  margin-bottom:1rem; text-transform:uppercase;
}
.sources ul { list-style:none; display:flex; flex-direction:column; gap:.6rem; }
.sources a {
  font-size:.95rem; color:var(--ink); text-decoration:none; font-weight:500;
  border-bottom:1px dotted var(--line); padding-bottom:.2rem;
  word-break:break-all; transition:color .25s;
}
.sources a:hover { color:var(--accent); border-bottom-color:var(--accent); }

/* NAV PREV/NEXT */
.nav-prev-next {
  max-width:1100px; margin:0 auto; padding:2rem;
  display:flex; justify-content:space-between; gap:1rem;
  font-family:'Shippori Mincho', serif;
}
.nav-prev-next a {
  color:var(--ink); text-decoration:none; padding:1rem 0;
  border-top:1px solid var(--line); flex:1; max-width:48%;
  transition:color .25s, border-color .25s;
}
.nav-prev-next a:hover { color:var(--accent); border-top-color:var(--accent); }
.nav-prev-next a small {
  display:block; font-family:'Cormorant Garamond', serif; font-style:italic;
  font-size:.85rem; color:var(--ink-soft); letter-spacing:.05em; margin-bottom:.4rem;
}
.nav-prev-next .next { text-align:right; margin-left:auto; }

/* DIVIDER */
.divider {
  max-width:1100px; margin:3rem auto; padding:0 2rem;
  display:flex; align-items:center; gap:1rem;
}
.divider .rule { flex:1; height:1px; background:var(--line); }
.divider .ornament { width:8px; height:8px; background:var(--accent); transform:rotate(45deg); }
.divider .ornament.outer { width:4px; height:4px; background:var(--warm); }

/* FOOTER */
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
  font-size:.8rem; color:var(--ink-soft); margin-top:.25rem; letter-spacing:.08em;
}
.colophon__notes {
  font-family:'Noto Sans JP', sans-serif; font-weight:400;
  font-size:.88rem; color:var(--ink-soft); line-height:1.9; letter-spacing:.02em;
}
.colophon__notes strong { color:var(--accent); font-weight:500; }
.colophon__sep { color:var(--line); margin:0 .5rem; }
"""


HEAD = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} ／ {brewery_name} — saketto.</title>
<meta name="description" content="{name}（{brewery_name}）。{note_short}">
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@300;400;500&family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<main>
"""


def find_tasting(brewery_slug, brand_name):
    """銘柄名で TASTING を引く（部分一致）"""
    notes = TASTING.get(brewery_slug, [])
    bn = brand_name.lower()
    for t in notes:
        tb = t["brand"].lower()
        # 銘柄名の主要部分が一致するか
        if bn in tb or tb in bn:
            return t
        # キーワード抜粋でも判定
        key_parts = bn.replace("（", " ").replace("）", " ").split()
        if any(p in tb for p in key_parts if len(p) > 1):
            return t
    return None


def render(brewery, brand, brand_idx, all_brands_count, prev_brand, next_brand):
    brewery_slug = brewery["slug"]
    brand_name = brand["name"]
    note = brand.get("note", "")
    note_short = note[:100].replace('"', "'")

    # SPEC cells
    abv_html = (
        f'<div class="spec-cell__value">{brand["abv"]}<small>% ABV</small></div>'
        if brand.get("abv") is not None
        else '<div class="spec-cell__unknown">公式非開示</div>'
    )
    vol_html = (
        f'<div class="spec-cell__value">{brand["volume_ml"]}<small>ml</small></div>'
        if brand.get("volume_ml") is not None
        else '<div class="spec-cell__unknown">公式非開示</div>'
    )
    ings = brand.get("sub_ingredients") or []
    if ings:
        ing_pills = ' '.join(f'<span class="pill">{i}</span>' for i in ings)
        ing_html = f'<div class="spec-cell__pills">{ing_pills}</div>'
    else:
        ing_html = '<div class="spec-cell__unknown">公式非開示</div>'

    # PRICE
    if brand.get("price") is not None:
        price_block = f"""
  <div class="price-block">
    <div class="price-block__label">PRICE</div>
    <div class="price-block__value">¥{brand["price"]:,}<small>参考 2026.05.30</small></div>
  </div>"""
    else:
        price_block = f"""
  <div class="price-block">
    <div class="price-block__label">PRICE</div>
    <div class="price-block__value" style="font-size:1.2rem; color:var(--ink-soft)">市場実勢／要公式確認</div>
  </div>"""

    # TASTING
    tasting = find_tasting(brewery_slug, brand_name)
    if tasting:
        meta_rows = []
        if tasting.get("temp"):
            meta_rows.append(f'<span class="tasting-meta__row"><strong>温度</strong>{tasting["temp"]}</span>')
        if tasting.get("pairing"):
            meta_rows.append(f'<span class="tasting-meta__row"><strong>ペアリング</strong>{tasting["pairing"]}</span>')
        meta_html = f'<div class="tasting-meta">{"".join(meta_rows)}</div>' if meta_rows else ''
        src_html = (
            f'<div class="tasting-source">出典：<a href="{tasting["source_url"]}" target="_blank" rel="noopener">{tasting.get("source_name","出典")}</a></div>'
            if tasting.get("source_url") else ''
        )
        tasting_section = f"""
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. 01</span>
      <span class="section-meta__label">TASTING NOTES</span>
      <span class="section-meta__rule"></span>
    </div>
    <div class="tasting-block">
      <div class="tasting-notes">{tasting["notes"]}</div>
      {meta_html}
      {src_html}
    </div>
  </section>"""
        kura_num = "02"
        related_num = "03"
        sources_num = "04"
    else:
        tasting_section = ''
        kura_num = "01"
        related_num = "02"
        sources_num = "03"

    # KURA context
    kura_section = f"""
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. {kura_num}</span>
      <span class="section-meta__label">KURA / 蔵について</span>
      <span class="section-meta__rule"></span>
    </div>
    <div class="kura-context">
      <div class="kura-context__name">{brewery["name"]}</div>
      <div class="kura-context__meta">{brewery["prefecture"]}・{brewery["city"]}　／　創業 {brewery["founded"]}</div>
      <p class="kura-context__philosophy">{brewery["philosophy"]}</p>
      <a class="kura-context__link" href="../brewery/{brewery_slug}.html">蔵の詳細を見る →</a>
    </div>
  </section>"""

    # RELATED — 同じ蔵の他銘柄（自分以外）
    related_brands = BRANDS.get(brewery_slug, [])
    related_cards = []
    for i, b in enumerate(related_brands):
        if i == brand_idx:
            continue
        sub_parts = []
        if b.get("abv") is not None:
            sub_parts.append(f'ABV {b["abv"]}%')
        if b.get("volume_ml") is not None:
            sub_parts.append(f'{b["volume_ml"]}ml')
        ings_str = "・".join((b.get("sub_ingredients") or [])[:2])
        if ings_str:
            sub_parts.append(ings_str)
        sub = "　／　".join(sub_parts) if sub_parts else "公式非開示"
        related_cards.append(f"""
      <a class="related-card" href="{brewery_slug}-{i}.html">
        <div class="related-card__name">{b['name']}</div>
        <div class="related-card__sub">{sub}</div>
      </a>""")

    if related_cards:
        related_section = f"""
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. {related_num}</span>
      <span class="section-meta__label">RELATED / 同じ蔵の他銘柄</span>
      <span class="section-meta__rule"></span>
    </div>
    <div class="related">{''.join(related_cards)}</div>
  </section>"""
    else:
        related_section = ''
        sources_num = related_num  # bump up

    # SOURCES
    src_links = [f'<li><a href="{brewery["official_url"]}" target="_blank" rel="noopener">{brewery["official_url"]}</a></li>']
    if tasting and tasting.get("source_url") and tasting["source_url"] != brewery["official_url"]:
        src_links.append(f'<li><a href="{tasting["source_url"]}" target="_blank" rel="noopener">{tasting["source_url"]}</a></li>')
    sources_html = ''.join(src_links)

    sources_section = f"""
  <section class="section">
    <div class="section-meta">
      <span class="section-meta__num">No. {sources_num}</span>
      <span class="section-meta__label">SOURCES / 一次ソース</span>
      <span class="section-meta__rule"></span>
    </div>
    <div class="sources">
      <h4>本ページのデータ出典</h4>
      <ul>{sources_html}</ul>
    </div>
  </section>"""

    # PREV/NEXT within brewery
    prev_html = (
        f'<a href="{brewery_slug}-{prev_brand["idx"]}.html"><small>← Prev</small>{prev_brand["name"]}</a>'
        if prev_brand else '<span></span>'
    )
    next_html = (
        f'<a class="next" href="{brewery_slug}-{next_brand["idx"]}.html"><small>Next →</small>{next_brand["name"]}</a>'
        if next_brand else '<span></span>'
    )

    html = HEAD.format(name=brand_name, brewery_name=brewery["name"],
                       note_short=note_short, css=CSS)

    html += f"""
  <div class="masthead">
    <div class="left">
      <a href="../index.html"><span class="accent-dot"></span>SAKETTO</a>
      <a href="../brewery/{brewery_slug}.html">← {brewery["name"]}</a>
    </div>
    <div class="right">BRAND {brand_idx+1:02d} / {all_brands_count}</div>
  </div>

  <section class="hero">
    <div class="hero__brewery"><a href="../brewery/{brewery_slug}.html">— {brewery["name"]}</a></div>
    <h1 class="hero__name">{brand_name}</h1>
    {('<p class="hero__note">' + note + '</p>') if note else ''}

    <div class="specs-board">
      <div class="spec-cell">
        <div class="spec-cell__label">— ABV</div>
        {abv_html}
      </div>
      <div class="spec-cell">
        <div class="spec-cell__label">— VOLUME</div>
        {vol_html}
      </div>
      <div class="spec-cell">
        <div class="spec-cell__label">— SUB-INGREDIENTS</div>
        {ing_html}
      </div>
    </div>

    {price_block}
  </section>

  <div class="divider">
    <div class="rule"></div>
    <div class="ornament outer"></div>
    <div class="ornament"></div>
    <div class="ornament outer"></div>
    <div class="rule"></div>
  </div>

  {tasting_section}
  {kura_section}
  {related_section}
  {sources_section}

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
    return html


def main():
    total = 0
    for brewery in BREWERIES:
        brands = BRANDS.get(brewery["slug"], [])
        for idx, brand in enumerate(brands):
            prev_brand = {"idx": idx - 1, "name": brands[idx - 1]["name"]} if idx > 0 else None
            next_brand = {"idx": idx + 1, "name": brands[idx + 1]["name"]} if idx < len(brands) - 1 else None
            html = render(brewery, brand, idx, len(brands), prev_brand, next_brand)
            out_path = OUT_DIR / f'{brewery["slug"]}-{idx}.html'
            out_path.write_text(html, encoding="utf-8")
            total += 1
        if brands:
            print(f"  {brewery['slug']:30s}  {len(brands)} 銘柄")
    print(f"\n✓ 生成完了: {total} 銘柄ページ ({OUT_DIR})")


if __name__ == "__main__":
    main()

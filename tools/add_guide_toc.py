# -*- coding: utf-8 -*-
"""読みもの記事に「目次」と「次に読む」を後付けする（生成後の後処理）

記事は1本4,600〜9,800字・節が8〜14あるのに目次が無く、モバイルでは
数百行のスクロールになる。また末尾に関連記事が無く、10本すべてが袋小路だった。

生成物から実際の節（section-meta__num / section-meta__label）を拾って作るので、
記事を書き換えても内容とズレない。gen_guides.py の後に実行する。

    cd ツール/saketto_repo && python tools/add_guide_toc.py
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDE = os.path.join(ROOT, "guide")

# 記事どうしの関連（同カテゴリ＋文脈の近さで手当て。行き止まりを作らない）
RELATED = {
    "craftsake-towa":  [("doburoku", "どぶろくとは"), ("nomikata", "飲み方・楽しみ方"), ("osusume", "おすすめ12選")],
    "doburoku":        [("hanamoto", "花酛とは"), ("zenkoji", "全麹酒とは"), ("craftsake-towa", "クラフトサケとは")],
    "nomikata":        [("osusume", "おすすめ12選"), ("doko-de-kaeru", "どこで買える？"), ("craftsake-towa", "クラフトサケとは")],
    "osusume":         [("doko-de-kaeru", "どこで買える？"), ("gift", "ギフトに贈る"), ("nomikata", "飲み方・楽しみ方")],
    "doko-de-kaeru":   [("osusume", "おすすめ12選"), ("gift", "ギフトに贈る"), ("new-breweries", "新しい蔵")],
    "gift":            [("osusume", "おすすめ12選"), ("doko-de-kaeru", "どこで買える？"), ("nomikata", "飲み方・楽しみ方")],
    "kioke":           [("zenkoji", "全麹酒とは"), ("hanamoto", "花酛とは"), ("doburoku", "どぶろくとは")],
    "hanamoto":        [("doburoku", "どぶろくとは"), ("kioke", "木桶仕込みとは"), ("craftsake-towa", "クラフトサケとは")],
    "zenkoji":         [("kioke", "木桶仕込みとは"), ("doburoku", "どぶろくとは"), ("craftsake-towa", "クラフトサケとは")],
    "new-breweries":   [("craftsake-towa", "クラフトサケとは"), ("doko-de-kaeru", "どこで買える？"), ("doburoku", "どぶろくとは")],
}

TOC_CSS = """<style>
.toc { max-width:760px; margin:0 auto 2.5rem; padding:1.4rem 1.6rem;
  border:1px solid var(--line); background:var(--paper); }
.toc__label { font-family:'Cormorant Garamond',serif; font-style:italic;
  font-size:.8rem; color:var(--ink-mute); letter-spacing:.12em; margin-bottom:.7rem; }
.toc ol { list-style:none; counter-reset:toc; display:grid; gap:.35rem; }
@media (min-width:700px){ .toc ol { grid-template-columns:1fr 1fr; column-gap:1.6rem; } }
.toc li { counter-increment:toc; }
.toc a { display:block; padding:.3rem 0; text-decoration:none; color:var(--ink);
  font-family:'Zen Kaku Gothic Antique',sans-serif; font-size:.9rem; line-height:1.7; }
.toc a::before { content:counter(toc,decimal-leading-zero); margin-right:.6rem;
  font-family:'Cormorant Garamond',serif; font-style:italic; color:var(--accent); font-size:.85rem; }
.toc a:hover { color:var(--accent); }
.article .section[id] { scroll-margin-top:1.5rem; }
.readnext { max-width:760px; margin:0 auto; padding:0 0 3rem; }
.readnext__label { font-family:'Cormorant Garamond',serif; font-style:italic;
  font-size:.8rem; color:var(--ink-mute); letter-spacing:.12em; margin-bottom:.8rem; }
.readnext__grid { display:grid; gap:.75rem; }
@media (min-width:700px){ .readnext__grid { grid-template-columns:repeat(3,1fr); } }
.readnext__card { display:block; padding:1rem 1.1rem; border:1px solid var(--line);
  background:var(--bg); text-decoration:none; color:var(--ink); transition:background .25s,border-color .25s; }
.readnext__card:hover { background:var(--paper); border-color:var(--accent); }
.readnext__k { display:block; font-family:'Cormorant Garamond',serif; font-style:italic;
  font-size:.72rem; color:var(--accent); letter-spacing:.1em; }
.readnext__t { display:block; font-family:'Shippori Mincho',serif; font-weight:700; font-size:1.02rem; margin-top:.2rem; }
@media (max-width:640px){ .toc, .readnext { padding-left:1.25rem; padding-right:1.25rem; } }
</style>"""

SEC_RE = re.compile(
    r'<section class="section">\s*<div class="section-meta">\s*'
    r'<span class="section-meta__num">No\. (\d+)</span>\s*'
    r'<span class="section-meta__label">([^<]+)</span>', re.S)


def build(path, slug):
    html = open(path, encoding="utf-8").read()
    if 'class="toc"' in html:
        return 0  # 二重付与を防ぐ

    secs = SEC_RE.findall(html)
    if not secs:
        return 0

    # 各節に id を振る
    def add_id(m):
        return m.group(0).replace('<section class="section">',
                                  f'<section class="section" id="s{m.group(1)}">', 1)
    html = SEC_RE.sub(add_id, html)

    items = "".join(
        f'<li><a href="#s{num}">{label.split(" / ")[-1].strip()}</a></li>' for num, label in secs)
    toc = (f'\n  <nav class="toc" aria-label="目次">\n'
           f'    <div class="toc__label">— 目次</div>\n'
           f'    <ol>{items}</ol>\n  </nav>\n')

    # ヒーロー直後の区切りの後ろに目次を差し込む
    marker = '</div>\n\n  <div class="article">'
    if marker in html:
        html = html.replace(marker, '</div>\n' + toc + '\n  <div class="article">', 1)
    else:
        html = html.replace('<div class="article">', toc + '\n  <div class="article">', 1)

    # 末尾に「次に読む」
    rel = RELATED.get(slug, [])
    if rel:
        cards = "".join(
            f'<a class="readnext__card" href="{u}"><span class="readnext__k">READ NEXT</span>'
            f'<span class="readnext__t">{t}</span></a>' for u, t in rel)
        block = (f'\n  <section class="readnext" aria-label="次に読む">\n'
                 f'    <div class="readnext__label">— 次に読む</div>\n'
                 f'    <div class="readnext__grid">{cards}</div>\n  </section>\n')
        html = html.replace("  <footer>", block + "\n  <footer>", 1)

    html = html.replace("</head>", TOC_CSS + "\n</head>", 1)
    open(path, "w", encoding="utf-8").write(html)
    return len(secs)


def main():
    total = 0
    for f in sorted(os.listdir(GUIDE)):
        if not f.endswith(".html") or f == "index.html":
            continue
        n = build(os.path.join(GUIDE, f), f[:-len(".html")])
        if n:
            total += 1
            print(f"  {f}: 目次{n}項目＋次に読む")
    print(f"読みもの {total} 本に目次と関連記事を付与")


if __name__ == "__main__":
    main()

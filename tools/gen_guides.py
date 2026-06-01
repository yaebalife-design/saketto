# -*- coding: utf-8 -*-
"""saketto / ガイド記事（読みもの）生成スクリプト

2本のガイド記事を生成する。
  guide/craftsake-towa.html … 「クラフトサケとは」
  guide/nomikata.html       … 「クラフトサケの飲み方・楽しみ方」

世界観CSSは gen_axes_pages.py から流用し、記事用タイポを追加。
嘘ゼロ: 事実は一次ソース（国税庁基本通達・酒税法／クラフトサケブリュワリー協会公式・
各蔵プレスリリース・日本酒造組合中央会・厚労省・月桂冠総合研究所 等）で確認したもののみ。
数値は出典明記のうえ概数で、温度・比率は「目安」、飲み方は「蔵推奨を優先」を明記。

実行: cd ツール/saketto_repo/tools && python gen_guides.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from gen_axes_pages import CSS as BASE_CSS  # 世界観CSSを流用
from site_common import head_extra
from breweries_brands import BRANDS          # おすすめ記事：スペックを一次ソースDBから直接引く
from breweries_master import by_slug
from moshimo_link import rakuten_search
from gen_sample_v2 import RAKUTEN_ENABLED

REPO_ROOT = Path(__file__).resolve().parent.parent  # saketto_repo/
OUT_DIR = REPO_ROOT / "guide"


# ────────────── 記事用 追加CSS ──────────────

EXTRA_CSS = """
.article { max-width:1100px; margin:0 auto; padding:0 2rem 2rem; }
.prose { max-width:760px; }
.prose p { font-size:1.02rem; color:var(--ink-soft); line-height:1.95; margin-bottom:1.4rem; }
.prose strong { color:var(--ink); font-weight:600; }
.prose a { color:var(--accent); text-decoration:none; border-bottom:1px solid var(--line-soft); transition:border-color .25s; }
.prose a:hover { border-bottom-color:var(--accent); }
.lead {
  font-family:'Shippori Mincho', serif; font-size:1.22rem; line-height:1.95;
  color:var(--ink); margin-bottom:1.8rem; font-weight:500;
}
.lead .accent { color:var(--accent); }

/* 用語・区分グリッド */
.term-grid { display:grid; grid-template-columns:1fr; border:1px solid var(--line); margin:1rem 0 2.5rem; max-width:860px; }
@media (min-width:680px){ .term-grid { grid-template-columns:1fr 1fr; } }
.term { padding:1.2rem 1.4rem; border-bottom:1px solid var(--line); background:var(--bg); }
@media (min-width:680px){ .term { border-right:1px solid var(--line); } .term:nth-child(2n){ border-right:none; } }
.term:last-child{ border-bottom:none; }
.term__name { font-family:'Shippori Mincho',serif; font-weight:700; font-size:1.12rem; color:var(--ink); margin-bottom:.4rem; }
.term__name .en { font-family:'Cormorant Garamond',serif; font-style:italic; font-size:.82rem; color:var(--accent); margin-left:.5rem; letter-spacing:.05em; }
.term__desc { font-size:.92rem; color:var(--ink-soft); line-height:1.8; }

/* 温度テーブル */
.temp-table { width:100%; max-width:760px; border-collapse:collapse; margin:1rem 0 1rem; font-size:.92rem; }
.temp-table th, .temp-table td { text-align:left; padding:.7rem 1rem; border-bottom:1px solid var(--line-soft); }
.temp-table thead th {
  font-family:'Zen Kaku Gothic Antique',sans-serif; font-weight:700; letter-spacing:.1em;
  font-size:.75rem; text-transform:uppercase; color:var(--ink); border-bottom:1px solid var(--line);
}
.temp-table td.t { font-family:'Zen Kaku Gothic Antique',sans-serif; font-weight:700; font-style:normal; color:var(--accent); white-space:nowrap; font-size:1rem; letter-spacing:.01em; }
.temp-table tr.grp td { background:var(--bg-alt); font-family:'Shippori Mincho',serif; font-weight:600; color:var(--ink); letter-spacing:.04em; }
.temp-note { font-size:.82rem; color:var(--ink-mute); margin:0 0 2.2rem; max-width:760px; line-height:1.7; }

/* 注意ボックス */
.callout { background:var(--bg-alt); border-left:3px solid var(--accent); padding:1.3rem 1.5rem; margin:1.6rem 0 2.2rem; max-width:760px; }
.callout__label {
  font-family:'Zen Kaku Gothic Antique',sans-serif; font-weight:700; letter-spacing:.12em;
  font-size:.74rem; color:var(--accent); text-transform:uppercase; margin-bottom:.5rem;
}
.callout p { font-size:.9rem; color:var(--ink-soft); line-height:1.85; margin:0; }
.callout a { color:var(--accent); text-decoration:none; border-bottom:1px solid var(--line-soft); }

/* ハブへのリンク行 */
.pill-links { display:flex; flex-wrap:wrap; gap:.6rem; margin:1rem 0 2.5rem; }
.pill-links a {
  font-family:'Zen Kaku Gothic Antique',sans-serif; font-weight:500; font-size:.9rem;
  letter-spacing:.03em; color:var(--ink); text-decoration:none;
  border:1px solid var(--line); padding:.55rem 1.1rem; transition:border-color .25s,color .25s;
}
.pill-links a:hover { border-color:var(--accent); color:var(--accent); }
.pill-links a .arr { color:var(--accent); margin-left:.45rem; }

/* 蔵リンクのインライン群 */
.kura-links { display:flex; flex-wrap:wrap; gap:.55rem 1rem; margin:.2rem 0 2rem; max-width:760px; }
.kura-links a { font-family:'Shippori Mincho',serif; font-size:.98rem; color:var(--ink); text-decoration:none; border-bottom:1px solid var(--line); padding-bottom:1px; transition:color .25s,border-color .25s; }
.kura-links a:hover { color:var(--accent); border-bottom-color:var(--accent); }

/* 次に読む */
.readmore { display:grid; grid-template-columns:1fr; gap:1rem; margin:1.5rem 0 0; max-width:860px; }
@media (min-width:680px){ .readmore { grid-template-columns:1fr 1fr; } }
.readmore a { display:block; border:1px solid var(--line); padding:1.4rem 1.5rem; text-decoration:none; background:var(--bg); transition:background .3s,padding-left .3s; }
.readmore a:hover { background:var(--paper); padding-left:1.75rem; }
.readmore__k { font-family:'Cormorant Garamond',serif; font-style:italic; font-size:.8rem; color:var(--accent); letter-spacing:.08em; }
.readmore__t { font-family:'Shippori Mincho',serif; font-weight:700; font-size:1.18rem; color:var(--ink); margin-top:.3rem; line-height:1.4; }

.sub-h { font-family:'Shippori Mincho',serif; font-weight:700; font-size:1.3rem; color:var(--ink); margin:.4rem 0 .9rem; letter-spacing:.02em; line-height:1.5; }
.sub-h.tight { margin-top:1.8rem; }
.sub-h .accent { color:var(--accent); }

/* 読みもの一覧（ガイドのハブ） */
.guide-list { border-top:1px solid var(--line); max-width:980px; margin:0 auto; }
.guide-card {
  display:grid; grid-template-columns:auto 1fr auto; gap:1.5rem; align-items:center;
  padding:1.9rem 1rem; border-bottom:1px solid var(--line);
  text-decoration:none; color:var(--ink); transition:background .3s,padding-left .3s;
}
.guide-card:hover { background:var(--paper); padding-left:1.5rem; }
.guide-card__mark { width:10px; height:10px; background:var(--line); transform:rotate(45deg); transition:background .3s; }
.guide-card:hover .guide-card__mark { background:var(--accent); }
.guide-card__eyebrow { font-family:'Zen Kaku Gothic Antique',sans-serif; font-size:.72rem; letter-spacing:.16em; text-transform:uppercase; color:var(--accent); margin-bottom:.4rem; }
.guide-card__title { font-family:'Shippori Mincho',serif; font-weight:700; font-size:1.5rem; color:var(--ink); margin-bottom:.5rem; line-height:1.4; }
.guide-card__sum { font-size:.92rem; color:var(--ink-soft); line-height:1.8; }
.guide-card__arr { font-family:'Cormorant Garamond',serif; font-style:italic; color:var(--accent); font-size:1rem; white-space:nowrap; letter-spacing:.08em; }
@media (max-width:680px){ .guide-card { grid-template-columns:auto 1fr; } .guide-card__arr{ display:none; } }
.cat-lead { max-width:760px; font-size:.95rem; color:var(--ink-soft); line-height:1.85; margin:-.4rem 0 1.2rem; }
.guide-foot { max-width:760px; margin:2.6rem auto 0; font-size:.95rem; color:var(--ink-soft); line-height:1.9; }
.guide-foot a { color:var(--accent); text-decoration:none; border-bottom:1px solid var(--line-soft); }

/* おすすめ（ランキング）カード */
.pick-group { font-family:'Shippori Mincho',serif; font-weight:700; font-size:1.18rem; color:var(--ink); max-width:820px; margin:2.6rem 0 1.1rem; padding-bottom:.5rem; border-bottom:1px solid var(--line); letter-spacing:.03em; }
.pick-group:first-of-type { margin-top:.6rem; }
.pick-group .en { font-family:'Cormorant Garamond',serif; font-style:italic; font-size:.8rem; color:var(--accent); margin-left:.6rem; letter-spacing:.06em; }
.pick { display:grid; grid-template-columns:auto 1fr; gap:1.1rem 1.3rem; max-width:820px; padding:1.5rem 0; border-bottom:1px solid var(--line-soft); }
.pick__no { font-family:'Cormorant Garamond',serif; font-style:italic; font-size:2rem; line-height:1; color:var(--line); padding-top:.1rem; }
.pick__head { display:flex; flex-wrap:wrap; align-items:baseline; gap:.5rem .9rem; margin-bottom:.5rem; }
.pick__kura { font-size:.82rem; color:var(--ink-mute); letter-spacing:.04em; }
.pick__kura a { color:var(--warm); text-decoration:none; border-bottom:1px solid var(--line-soft); }
.pick__kura a:hover { color:var(--accent); }
.pick__name { font-family:'Shippori Mincho',serif; font-weight:700; font-size:1.24rem; color:var(--ink); line-height:1.4; width:100%; }
.pick__tags { display:flex; flex-wrap:wrap; gap:.4rem; margin:.1rem 0 .55rem; }
.pick__tag { font-family:'Zen Kaku Gothic Antique',sans-serif; font-size:.72rem; letter-spacing:.04em; color:var(--ink-soft); border:1px solid var(--line); padding:.16rem .6rem; }
.pick__spec { font-size:.84rem; color:var(--ink-mute); letter-spacing:.02em; margin-bottom:.6rem; }
.pick__spec b { color:var(--ink-soft); font-weight:600; }
.pick__note { font-size:.95rem; color:var(--ink-soft); line-height:1.85; margin-bottom:.9rem; }
.pick__links { display:flex; flex-wrap:wrap; gap:.6rem .9rem; align-items:center; }
.pick__detail { font-family:'Shippori Mincho',serif; font-size:.92rem; color:var(--ink); text-decoration:none; border-bottom:1px solid var(--line); padding-bottom:1px; }
.pick__detail:hover { color:var(--accent); border-bottom-color:var(--accent); }
.pick__btn { font-family:'Zen Kaku Gothic Antique',sans-serif; font-weight:500; font-size:.9rem; letter-spacing:.03em; color:var(--paper); background:var(--accent); border:1px solid var(--accent); padding:.5rem 1.1rem; text-decoration:none; }
.pick__btn:hover { background:var(--accent-deep); border-color:var(--accent-deep); }
.pick__pr { font-size:.72rem; color:var(--ink-mute); letter-spacing:.04em; }
@media (max-width:600px){ .pick { grid-template-columns:1fr; gap:.2rem; } .pick__no { font-size:1.4rem; } }

/* スペック比較表 */
.cmp-wrap { max-width:820px; overflow-x:auto; margin:1rem 0 1rem; }
.cmp { width:100%; border-collapse:collapse; font-size:.84rem; white-space:nowrap; }
.cmp th, .cmp td { text-align:left; padding:.6rem .8rem; border-bottom:1px solid var(--line-soft); }
.cmp thead th { font-family:'Zen Kaku Gothic Antique',sans-serif; font-weight:700; letter-spacing:.06em; font-size:.72rem; color:var(--ink); border-bottom:1px solid var(--line); }
.cmp td.nm { font-family:'Shippori Mincho',serif; color:var(--ink); white-space:normal; min-width:11rem; }
.cmp td.p { font-family:'Zen Kaku Gothic Antique',sans-serif; color:var(--accent); font-weight:700; }
.cmp a { color:inherit; text-decoration:none; border-bottom:1px solid var(--line-soft); }
.cmp a:hover { color:var(--accent); }
"""


# ────────────── ページ骨格 ──────────────

def page_head(title, description):
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — saketto.</title>
<meta name="description" content="{description}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@300;400;500&family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<style>{BASE_CSS}{EXTRA_CSS}</style>
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
      <a href="../index.html#breweries">蔵</a>
      <a href="../region/">地域</a>
      <a href="../genre/">ジャンル</a>
      <a href="../guide/">読みもの</a>
    </nav>
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


def section_meta(num, label_en):
    return f"""    <div class="section-meta">
      <span class="section-meta__num">No. {num}</span>
      <span class="section-meta__label">{label_en}</span>
      <span class="section-meta__rule"></span>
    </div>"""


def divider():
    return """
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
        <a href="/about.html">運営者情報</a><span class="colophon__sep">／</span>
        <a href="/privacy.html">プライバシーポリシー</a><span class="colophon__sep">／</span>
        <a href="/disclaimer.html">免責事項・広告表記</a><span class="colophon__sep">／</span>
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


def term_grid(items):
    """items: list of (name, en, desc)"""
    return '<div class="term-grid">' + "".join(
        f'<div class="term"><div class="term__name">{n}<span class="en">{en}</span></div>'
        f'<div class="term__desc">{d}</div></div>' for n, en, d in items) + "</div>"


# 協会加盟蔵（saketto収録分・確認日2026-05-31）
KURA = {
    "konohanano": "木花之醸造所",
    "haccoba": "haccoba",
    "librom": "LIBROM",
    "ine-to-agave": "稲とアガベ",
    "lagoon": "LAGOON BREWERY",
    "happy-taro": "ハッピー太郎醸造所",
    "heiroku": "平六醸造",
    "pukupuku": "ぷくぷく醸造",
    "adachi-noujo": "足立農醸",
}


def kura_link(slug):
    return f'<a href="../brewery/{slug}.html">{KURA.get(slug, slug)}</a>'


# ────────────── 記事メタ（一覧の元データ。記事を増やすときはここに1件追加） ──────────────

# 分類（カテゴリ）。表示はこの順。記事の無いカテゴリは一覧に出さない。
CATEGORIES = [
    {"key": "know", "en": "KNOW", "ja": "基礎を知る",
     "desc": "クラフトサケを初めて知る人へ。まず読んでおきたい入門。"},
    {"key": "choose", "en": "CHOOSE", "ja": "選ぶ・探す",
     "desc": "副原料やふるさと納税から、自分にぴったりの一本を見つける。"},
    {"key": "deep", "en": "DEEP", "ja": "深く味わう",
     "desc": "製法や文化を掘り下げ、クラフトサケをもっと深く楽しむ。"},
]
CAT_BY_KEY = {c["key"]: c for c in CATEGORIES}

# 記事メタ（記事を増やすときはここに1件追加し、build関数を1つ書く）
ARTICLES = [
    {
        "slug": "craftsake-towa",
        "category": "know",
        "eyebrow_en": "WHAT IS CRAFT SAKE",
        "title": "クラフトサケとは",
        "summary": "米と副原料で醸す新ジャンルの酒「クラフトサケ」。その定義、日本酒・どぶろくとの区分の違い、新規参入の仕組み、協会、世界の潮流、醸造のことばまで、全体像をやさしく。",
    },
    {
        "slug": "nomikata",
        "category": "know",
        "eyebrow_en": "HOW TO ENJOY",
        "title": "クラフトサケの飲み方・楽しみ方",
        "summary": "温度で変わる味わい、生酒・にごりの保存、活性タイプの開け方、器の選び方、ソーダ割りなどのスタイル、料理とのペアリング、和らぎ水まで。自由な酒の楽しみ方。",
    },
    {
        "slug": "osusume",
        "category": "choose",
        "eyebrow_en": "EDITORS' PICKS",
        "title": "クラフトサケ おすすめ12選",
        "summary": "「はじめの一本」から通好みまで、saketto編集部がタイプ別に選んだ12本。稲とアガベ・haccoba・LAGOON・ぷくぷく醸造ほか、収録DBの確認済みスペックとともに紹介。各銘柄から探せます。",
    },
]


def article_meta(slug):
    """slug から (article, category) を返す。"""
    art = next(a for a in ARTICLES if a["slug"] == slug)
    return art, CAT_BY_KEY[art["category"]]


def article_eyebrow(slug):
    """記事ページのアイブロウ（分類 ／ 分類名）。番号は使わない。"""
    art, cat = article_meta(slug)
    return f'{cat["en"]} ／ {cat["ja"]}'


def article_masthead_label(slug):
    art, cat = article_meta(slug)
    return f'{cat["en"]} — {art["eyebrow_en"]}'


def build_index():
    blocks = ""
    for cat in CATEGORIES:
        arts = [a for a in ARTICLES if a["category"] == cat["key"]]
        if not arts:
            continue  # 記事の無い分類は出さない
        cards = ""
        for a in arts:
            cards += f"""        <a class="guide-card" href="{a['slug']}.html">
          <div class="guide-card__mark"></div>
          <div class="guide-card__body">
            <div class="guide-card__eyebrow">{a['eyebrow_en']}</div>
            <div class="guide-card__title">{a['title']}</div>
            <div class="guide-card__sum">{a['summary']}</div>
          </div>
          <div class="guide-card__arr">READ →</div>
        </a>
"""
        blocks += f"""
    <section class="section">
      <div class="section-meta">
        <span class="section-meta__num">{cat['en']}</span>
        <span class="section-meta__label">{cat['ja']}</span>
        <span class="section-meta__rule"></span>
      </div>
      <p class="cat-lead">{cat['desc']}</p>
      <div class="guide-list">
{cards}      </div>
    </section>
"""
    body = f"""
  <div class="article">
{blocks}    <p class="guide-foot">クラフトサケの世界を、知って・選んで・深く味わうための読みもの。これから少しずつ増えていきます。まず一本に出会いたい方は、<a href="../index.html">トップ</a>の4つの軸からどうぞ。</p>
  </div>
"""
    html = page_head("読みもの — クラフトサケのガイド",
                     "クラフトサケを知り、選び、楽しむためのガイド記事の一覧。基礎を知る・選ぶ・深く味わうの分類で、米から生まれた自由な酒を味わうための読みものをまとめています。")
    html += masthead("READING — 読みもの", "A Field Guide")
    html += hero(
        "READING — 読みもの",
        'クラフトサケを、<span class="accent">もっと知る</span>。',
        "そもそもクラフトサケとは何か。どう飲めば、もっとおいしいのか。基礎を知り、選び、深く味わう——saketto のガイド記事を、分類でまとめています。")
    html += body
    html += footer()
    return html


# ────────────── 記事①：クラフトサケとは ──────────────

def build_towa():
    members6 = "WAKAZE・木花之醸造所・haccoba・LIBROM・稲とアガベ・LAGOON BREWERY"
    kura_row = '<div class="kura-links">' + \
        "".join(kura_link(s) for s in
                ["konohanano", "haccoba", "librom", "ine-to-agave", "lagoon",
                 "happy-taro", "heiroku", "pukupuku", "adachi-noujo"]) + "</div>"

    classes = term_grid([
        ("清酒（日本酒）", "SEISHU", "米・米麹・水（と法定の副原料）を発酵させ、もろみを「こした」もの。加えてよい副原料は政令で決められた品目に限られ、その重量は米と米麹の合計の半分（50%）以内、アルコール分は22度未満。"),
        ("どぶろく", "DOBUROKU", "米・米麹・水を発酵させるが、もろみを「こさない」酒。こす工程がないため清酒の定義を外れ、酒税法上は「その他の醸造酒」に分類される。"),
        ("その他の醸造酒", "OTHER BREWED", "穀類や糖類などを発酵させた酒類で、清酒や果実酒などに当てはまらず、アルコール分20度未満・エキス分2度以上のもの。クラフトサケの多くがここに入る。"),
        ("リキュール", "LIQUEUR", "酒類に糖類などを加えた混成酒。副原料の使い方によっては、クラフトサケがこの区分で造られることもある。"),
        ("果実酒", "FRUIT WINE", "果実を主原料として発酵させた酒。果実を多く用いる設計では、こちらに区分される場合もある。"),
    ])

    terms = term_grid([
        ("花酛", "HANAMOTO", "東北地方に伝わる、幻とされるどぶろくの製法。ホップの近縁種「カラハナソウ（唐花草）」の煎じ汁で雑菌の繁殖を抑えながら醸す。現代に再現する蔵もある。"),
        ("水もと・菩提酛", "MIZUMOTO", "室町時代に奈良・正暦寺で生まれた、現存最古級の酒母づくり。生米を水に漬けて乳酸発酵させた酸性水「そやし水」を仕込みに使い、雑菌を抑える。"),
        ("生酛", "KIMOTO", "自然界の乳酸菌を取り込んで乳酸を生成させる、伝統的な酒母の育て方。手間はかかるが、力強く安定した発酵を生む。"),
        ("速醸", "SOKUJO", "明治末期に確立した比較的新しい製法。醸造用の乳酸を加えることで、短期間で安全に酒母を仕込める。"),
        ("白麹", "SHIRO-KOJI", "もとは焼酎づくりに使う麹。クエン酸を多く生み、レモンを思わせる爽やかな酸味とキレを酒に与える。"),
        ("全麹", "ZEN-KOJI", "蒸米を使わず、原料をすべて米麹で仕込む方法。泡盛に通じる手法で、甘みと旨みが濃密に引き出される。"),
        ("木桶仕込み", "KIOKE", "木桶を発酵の容器に用いる、伝統的な仕込み。蔵や桶ごとの個性が酒に映るとされる。"),
        ("ドライホッピング", "DRY HOPPING", "ビールづくり由来の技法。発酵の後半などにホップを加え、華やかな香りを引き出す。"),
        ("どぶろく", "DOBUROKU", "もろみを「こさない」酒。固液分離をしないため清酒の定義を外れ、その他の醸造酒に分類される。"),
    ])

    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "DEFINITION / 定義")}
      <div class="prose">
        <p class="lead">「クラフトサケ」とは、米と米麹を軸にしながら、ホップ・果実・ハーブといった<span class="accent">副原料</span>を自由に取り入れて醸す、新しいジャンルの酒。</p>
        <p>日本の酒税法では、「清酒（いわゆる日本酒）」は——米・米麹・水を原料として発酵させ、もろみを<strong>こした</strong>もの——と細かく定義されている。さらに、加えてよい副原料は政令で決められた品目に限られ、その重量は米と米麹の合計の<strong>半分（50%）を超えてはならない</strong>。アルコール分も22度未満。これらをすべて満たして、はじめて「清酒」を名乗れる。</p>
        <p>裏を返せば、ホップや果実、ハーブのような<strong>定義の外にある副原料</strong>を加えたり、もろみを<strong>こさずに</strong>仕上げたりすると、その酒はもう「清酒（日本酒）」ではなくなる。その多くは、酒税法上<strong>「その他の醸造酒」</strong>という区分に入る。</p>
        <p>つまりクラフトサケは、日本酒づくりの技術を土台にしながら、あえて「日本酒」という枠の<strong>外</strong>へ踏み出すことで生まれた酒。米と麹だけを濾さずに仕込む<strong>どぶろく</strong>も、ホップを効かせたホップサケも、果実を絡めた果実サケも、この同じ土俵の上にある。「日本酒ではない」ことが、むしろ自由の源泉になっている。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("02", "CLASSIFICATION / 区分の違い")}
      <div class="prose">
        <h2 class="sub-h">日本酒・どぶろく・<span class="accent">その他の醸造酒</span>。</h2>
        <p>似ているようで、酒税法上の区分は意外と入り組んでいる。クラフトサケがどこに立っているのか、おもな区分を並べてみる。</p>
      </div>
      {classes}
      <div class="prose">
        <p>同じ「米の酒」でも、もろみを<strong>こすか・こさないか</strong>、副原料を<strong>何をどれだけ</strong>加えるかで、区分は変わる。クラフトサケの多くは「その他の醸造酒」だが、果実や糖類の使い方によっては、リキュールや果実酒として届けられることもある。ラベルの分類表示を見比べてみるのも、この酒のおもしろさだ。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("03", "WHY NOW / なぜ今")}
      <div class="prose">
        <h2 class="sub-h">「日本酒の枠の外」に、<span class="accent">自由</span>があった。</h2>
        <p>なぜ造り手たちは、わざわざ「日本酒ではない酒」を造るのか。背景には、日本酒（清酒）の<strong>製造免許</strong>が、新規にはほとんど交付されないという事情がある。</p>
        <p>酒税法には、酒税収を守るために「需給の均衡を保つ必要があるときは免許を与えないことができる」という<strong>需給調整</strong>の仕組みがある。清酒はこの対象で、長らく新規の製造免許が原則として発行されていない。さらに、清酒を造るには年間<strong>60キロリットル</strong>（一升瓶でおよそ3万本超）という<strong>最低製造数量</strong>の基準もあり、小さく始めることも難しい。既存の蔵を守るこの仕組みが、結果として新規参入の高い壁になってきた。</p>
        <p>そこで近年の造り手は、比較的取得しやすい<strong>「その他の醸造酒」の製造免許</strong>で参入する道を選んだ。この免許なら、清酒の定義に縛られない発想——副原料を加える、すべてを麹で仕込む、もろみを濾さない——で自由に酒を醸せる。これがクラフトサケというムーブメントの源流になっている。</p>
        <p>「どぶろくなら特区で造れるのでは」と思うかもしれない。だが農家民宿などの<strong>どぶろく特区</strong>は、原則として<strong>自分の店で出す</strong>ぶんに限られ、瓶詰めして全国に売ることはできない。クラフトサケが取る「その他の醸造酒」の免許は、<strong>瓶に詰めて全国へ流通</strong>させられる点が決定的に違う。だからこそ、各地の蔵の個性が、いまや全国の食卓で楽しめる。</p>
        <p>その先駆けとされるのが、2021年に福島県南相馬市小高で立ち上がった {kura_link("haccoba")} や、秋田県男鹿の {kura_link("ine-to-agave")}。彼らが切り拓いた道を、いま全国の蔵が思い思いのかたちで歩んでいる。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("04", "THE ASSOCIATION / 協会")}
      <div class="prose">
        <h2 class="sub-h">合言葉は、<span class="accent">「自由を、醸そう。」</span></h2>
        <p>2022年6月27日、6つの醸造所が手を組み<strong>「クラフトサケブリュワリー協会」（JAPAN CRAFT SAKE BREWERIES ASSOCIATION）</strong>が発足した。掲げるコピーは<strong>「自由を、醸そう。」</strong>。</p>
        <p>設立の目的は、<strong>①クラフトサケの醸造所を増やす ②知名度を高める ③日本酒とクラフトサケが共存できる未来をつくる</strong>——の3つ。協会は、10年以内に全47都道府県へクラフトサケの醸造所をつくることも目標に掲げている。設立メンバーは {members6} の6蔵だった。</p>
        <p>その後、加盟は少しずつ広がっている。本記事の確認時点（2026年5月31日）で協会公式サイトに名を連ねる蔵のうち、saketto に収録しているのは次の蔵。日本酒の伝統と新しい自由が同居する、それぞれの物語は各蔵のページから辿れる。</p>
        {kura_row}
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("05", "GLOBAL / 世界の潮流")}
      <div class="prose">
        <h2 class="sub-h">世界が、<span class="accent">SAKE</span>に気づき始めた。</h2>
        <p>クラフトサケが生まれた背景には、世界的なSAKE人気の高まりもある。日本酒（清酒）の輸出額は伸び続け、日本酒造組合中央会の発表によれば、2023年には<strong>約410億円</strong>、輸出先は<strong>75の国と地域</strong>に達した。1リットルあたりの単価も過去最高を更新し、SAKEは「安く、たくさん」から「選んで、味わう」ものへと位置づけを変えつつある。</p>
        <p>2024年12月には、日本酒や焼酎などの<strong>「伝統的酒造り」がユネスコの無形文化遺産に登録</strong>された。麹を用いる日本の酒づくりの技術が、世界の宝として認められたのだ。海外でSAKEを醸す蔵も欧米を中心に増えており、米から生まれる酒は静かに国境を越えている。</p>
        <p>クラフトサケは、その大きな潮流の中で生まれた「これからの酒」。伝統に深く根ざしながら、まだ誰も見たことのない味へと向かっている。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("06", "VOCABULARY / 醸造のことば")}
      <div class="prose">
        <p>クラフトサケのラベルや解説には、聞き慣れない醸造用語が並ぶ。代表的なことばを知っておくと、ひと口の味わいの背景が、ぐっと立体的に見えてくる。</p>
      </div>
      {terms}
      <div class="prose">
        <p>こうした製法や副原料の個性は、saketto では<a href="../genre/">ジャンル</a>や<a href="../subingredients/">副原料</a>の軸からも辿れる。気になることばを入り口に、酒を探してみてほしい。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("07", "HOW TO EXPLORE / 探し方")}
      <div class="prose">
        <h2 class="sub-h">4つの軸から、<span class="accent">次の一本</span>へ。</h2>
        <p>クラフトサケの面白さは、その多様さにある。saketto では、25の蔵と120を超える銘柄を、4つの軸から横断的に探せる。気になる入り口から、次に出会う一本を見つけてほしい。</p>
        <div class="pill-links">
          <a href="../subingredients/">副原料から<span class="arr">→</span></a>
          <a href="../region/">地域から<span class="arr">→</span></a>
          <a href="../genre/">ジャンルから<span class="arr">→</span></a>
          <a href="../furusato/">ふるさと納税から<span class="arr">→</span></a>
        </div>
        <div class="readmore">
          <a href="nomikata.html">
            <div class="readmore__k">つづけて読む</div>
            <div class="readmore__t">クラフトサケの飲み方・楽しみ方</div>
          </a>
          <a href="index.html">
            <div class="readmore__k">INDEX</div>
            <div class="readmore__t">読みもの一覧へ</div>
          </a>
        </div>
      </div>
    </section>

  </div>
"""
    html = page_head("クラフトサケとは — 米から生まれた、自由な酒",
                     "クラフトサケとは何か。酒税法上の「その他の醸造酒」という位置づけ、日本酒・どぶろくとの区分の違い、新規参入の仕組み、クラフトサケブリュワリー協会、花酛・白麹・全麹などの醸造用語まで、その全体像をやさしく解説します。")
    html += masthead(article_masthead_label("craftsake-towa"), "A Field Guide")
    html += hero(
        article_eyebrow("craftsake-towa"),
        'クラフトサケとは。<br>米から生まれた、<span class="accent">自由な酒</span>。',
        "日本酒づくりの技術を土台に、あえて「日本酒」の枠の外へ。米と副原料で醸す新ジャンル「クラフトサケ」の成り立ちを、法律・歴史・世界の潮流・醸造のことばからひもときます。")
    html += body
    html += footer()
    return html


# ────────────── 記事②：飲み方・楽しみ方 ──────────────

def build_nomikata():
    temp_rows = [
        ("grp", "冷やして — COLD", ""),
        ("", "雪冷え", "5℃", "香りは控えめ、きりりと締まった口当たり"),
        ("", "花冷え", "10℃", "繊細な味わい、香りが少しずつ開く"),
        ("", "涼冷え", "15℃", "はっきりした冷たさに、華やかな香り"),
        ("grp", "常温で — ROOM", ""),
        ("", "冷や（常温）", "15-20℃", "「冷や」は本来この常温のこと。酒の素の表情が出る"),
        ("grp", "温めて — WARM", ""),
        ("", "人肌燗", "35℃", "米と麹の香り、さらりとやわらかく"),
        ("", "ぬる燗", "40℃", "香りがもっとも豊かにふくらむ"),
        ("", "あつ燗", "50℃", "シャープに引き締まり、キレのある辛口に"),
    ]
    trows = ""
    for r in temp_rows:
        if r[0] == "grp":
            trows += f'        <tr class="grp"><td colspan="3">{r[1]}</td></tr>\n'
        else:
            trows += f'        <tr><td>{r[1]}</td><td class="t">{r[2]}</td><td>{r[3]}</td></tr>\n'

    pair_html = term_grid([
        ("果実サケ", "FRUIT", "生ハム、フレッシュチーズ、サーモンの香草焼き、サラダ。華やかな香りと果実の甘酸っぱさが、前菜や軽い一皿に寄り添う。"),
        ("ホップサケ", "HOP", "揚げ物、スパイス料理、エスニック。ホップのほろ苦さと柑橘のような香りが、油やスパイスをすっきり受け止める。"),
        ("古典どぶろく", "DOBUROKU", "味噌・漬物などの発酵食品、鍋もの、焼き魚。米の濃い旨みと酸が、滋味深い和の食卓と響き合う。"),
        ("全麹・濃醇タイプ", "FULL-BODIED", "おでん、ぶり大根、熟成チーズ、グラタン。とろりと濃い甘旨味は、こっくりした料理やデザート感覚でも。"),
        ("白麹・酸の効いた酒", "ACIDIC", "揚げ物や脂ののった肉を、さっぱりと。クエン酸由来の爽やかな酸が、後味を軽やかに切り替える。"),
    ])

    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "TEMPERATURE / 温度")}
      <div class="prose">
        <p class="lead">クラフトサケは、低アルコールのものから濃厚な原酒まで、<span class="accent">味わいの幅</span>がとても広い。まずは「冷や」で、その個性を確かめるのがおすすめ。</p>
        <p>クラフトサケの多くは、加熱処理をしない<strong>生酒</strong>や、澱を残した<strong>にごり</strong>。発酵の余韻が生きた、繊細で変化に富む酒だ。だから保存も飲み方も、基本は日本酒の生酒に準じて考えるとうまくいく。</p>
        <h2 class="sub-h tight">温度で、酒の<span class="accent">表情</span>が変わる。</h2>
        <p>日本酒には、温度帯ごとに風流な呼び名がある。クラフトサケも基本は同じ。一般に、<strong>冷やすと</strong>酸味がはっきりして香りは控えめになり、きりっとシャープな印象に。<strong>温めると</strong>甘味と旨味、そして香りがふくらみ、口当たりがまろやかになる。同じ一本でも、温度しだいで驚くほど表情が変わる。</p>
      </div>
      <table class="temp-table">
        <thead><tr><th>呼び名</th><th>目安</th><th>表情</th></tr></thead>
        <tbody>
{trows}        </tbody>
      </table>
      <p class="temp-note">※ 温度帯の呼称は日本酒造組合中央会による。温度はおおよその目安です。最適な温度は銘柄ごとに異なるため、各蔵のおすすめがあればそれを優先してください。</p>
      <div class="prose">
        <p>ただし、温めすぎるとせっかくの香りが飛んでしまうことも。まずは冷やで個性を確かめ、そこから少しずつ温度を上げて、自分の好みの表情を探してみてほしい。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("02", "STORAGE / 保存")}
      <div class="prose">
        <h2 class="sub-h">生酒・にごりは、<span class="accent">冷蔵</span>が基本。</h2>
        <p>日本酒には、加熱処理（火入れ）を2回・1回・0回と行う段階があり、火入れが少ないほど酵母や酵素が生きていて、味が変わりやすい。クラフトサケに多い<strong>生酒（火入れなし）</strong>や<strong>にごり</strong>は、まさにその変わりやすいタイプ。<strong>約5℃以下の冷蔵</strong>を目安に保管したい。火入れされたものも、品質を保つなら冷暗所が安心だ。</p>
        <p>大敵は、高温・光・時間。温度が高いと「老香（ひねか）」と呼ばれる劣化した香りが出やすく、紫外線（日光や蛍光灯の光）に当たると「日光臭」というネギのような匂いがつくことがある。<strong>冷蔵庫の奥（温度の変わりやすいドアポケットは避ける）に、立てて、光を遮って</strong>保管するのがいい。</p>
        <p>開栓したあとは風味が変わりやすいので、<strong>遅くとも2週間ほど</strong>を目安に飲み切るのがおすすめ。これらはあくまで一般的な目安。ボトルに「要冷蔵」などの表示があれば、それが何よりのガイドになる。</p>
        <div class="callout">
          <div class="callout__label">ボトルの表示を確認</div>
          <p>「要冷蔵」「開栓注意」といった表示は、その酒の個性そのもの。ラベルや蔵の案内に従うのが、いちばんおいしく楽しむ近道です。</p>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("03", "NIGORI / 濁りと澱")}
      <div class="prose">
        <h2 class="sub-h">澱（おり）は、<span class="accent">味のうち</span>。</h2>
        <p>ひと口に「濁った酒」といっても、いくつか種類がある。もろみを搾らずそのまま味わうのが<strong>どぶろく</strong>、粗く漉して米の固形分を多めに残すのが<strong>にごり酒</strong>、搾ったあとの澱をあえて少し残したのが<strong>おりがらみ</strong>。濁りの濃さも、とろみも口当たりも、それぞれに違う。</p>
        <p>瓶の底に沈んだ澱は、二通りに楽しめる。立てたまま上澄みだけを注いで<strong>すっきりと飲み、後から濃い澱を味わう</strong>「分けて飲む」スタイル。もしくは、瓶をゆっくり傾けて<strong>澱を均一に混ぜ、クリーミーな口当たり</strong>を楽しむスタイル。ひと瓶で二度おいしい。</p>
        <h2 class="sub-h tight">活性タイプは、<span class="accent">ゆっくり</span>開ける。</h2>
        <p>火入れをしていない<strong>活性（発泡）にごり</strong>は、瓶の中で炭酸ガスが生きている。勢いよく開けると噴き出すので、手順が大切だ。まず<strong>冷蔵庫でよく冷やし、立てて</strong>落ち着かせる。栓は一気に開けず、<strong>少し開けてはガスを逃がし、また閉める</strong>——これを何度も繰り返す。落ち着くまで時間がかかることもあるので、こぼれてもいい場所で、あせらず、ゆっくりと。</p>
        <div class="callout">
          <div class="callout__label">開け方は商品の案内を優先</div>
          <p>活性タイプは、商品ごとに開栓の注意書きや専用の手順が指定されていることがあります。安全のため、まずはボトルの表示と蔵の案内を最優先にしてください。</p>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("04", "GLASS / 器")}
      <div class="prose">
        <h2 class="sub-h">器で、<span class="accent">香り</span>が立つ。</h2>
        <p>同じ酒でも、注ぐ器で印象が変わる。口の広い<strong>ワイングラス</strong>は、グラスの中で香りがふわりと広がり、フルーティーな果実サケや華やかなホップサケの魅力を引き出す。香りを楽しみたいなら、まずはワイングラスがおすすめだ。</p>
        <p>小ぶりな<strong>おちょこ</strong>は、温度が変わる前に飲み切れるので冷酒や燗に向く。少し深い<strong>ぐい呑み</strong>は、温度や香りの移ろいを味わえる。木の<strong>升</strong>は、木の香りが移って爽やかさが加わる。器を替えるだけで、一本の酒がいくつもの顔を見せてくれる。</p>
        <p>ちなみに、ワイングラスで香りが引き立つのには理由がある。ワインを対象にしたある研究では、グラスの中でアルコールの蒸気がリング状に分布し、中央では刺激が抑えられて香りだけを感じやすくなることが示された。口のすぼまった形が、立ちのぼる香りをやさしくまとめてくれるのだ。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("05", "STYLE / 割り方とアレンジ")}
      <div class="prose">
        <h2 class="sub-h">ロックも、<span class="accent">ソーダ割り</span>も。</h2>
        <p>クラフトサケは、自由な酒。味のしっかりした銘柄なら、ストレートだけでなくアレンジも楽しい。<strong>ソーダ割り</strong>は、まず<strong>酒1：炭酸1</strong>を基準に、好みで炭酸を増やして軽やかに。よく冷やして、冷えたグラスでつくるのがコツだ。</p>
        <p>度数の高い原酒は<strong>ロック</strong>で、冷やしながらゆっくりと。寒い日には<strong>お湯割り</strong>で、米の甘みをふっくらと。柑橘やミント、ジンジャーを添えれば、カクテルのようにも遊べる。低アルコールのタイプは、お酒に飲み慣れていない人の入り口にもなる。</p>
        <p>もっとも、どんな飲み方が合うかは、銘柄ごとに蔵がおすすめを示していることも多い。割って楽しんでほしい酒、そのまま味わってほしい酒——迷ったら、<strong>蔵の推奨に従う</strong>のがいちばんだ。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("06", "PAIRING / 料理と合わせる")}
      <div class="prose">
        <h2 class="sub-h">料理と、<span class="accent">響き合わせる</span>。</h2>
        <p>ペアリングの基本は、<strong>味の強さを合わせる</strong>こと。軽やかな酒には淡白な料理、濃厚な酒にはしっかりした味つけ。香りや酸味の方向性を料理と揃えると、互いに引き立て合う。脂の多い料理には、酸でさっぱり流すか、旨味で受け止めるか——その選び方も楽しい。下は、ジャンル別の相性の目安。あくまで出発点として、自由に組み合わせてみてほしい。</p>
      </div>
      {pair_html}
      <div class="prose">
        <p>こうしたジャンルは、saketto の<a href="../genre/">ジャンル</a>や<a href="../subingredients/">副原料</a>の軸から探せる。今夜の食卓に合わせて、一本を選んでみてほしい。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("07", "ENJOY WELL / 心地よく楽しむ")}
      <div class="prose">
        <h2 class="sub-h">水を飲みながら、<span class="accent">自分のペース</span>で。</h2>
        <p>おいしいお酒ほど、つい杯が進んでしまう。合間に飲む水「<strong>和らぎ水（やわらぎみず）</strong>」を用意しておくと、酔いがゆるやかになり、口の中もリフレッシュされて、次の一杯と料理がいっそう鮮やかに感じられる。お酒と同じくらいの量の水を飲むのを、目安に。</p>
        <p>厚生労働省は、節度ある適度な飲酒の目安を「1日あたり純アルコールで約20グラム程度」としている。日本酒なら、おおよそ1合（180ml）にあたる量だ（あくまで一般的な目安で、お酒の強さには個人差がある）。自分のペースを大切に、休む日もつくりながら、この自由な酒と長く付き合っていきたい。</p>
        <div class="callout">
          <div class="callout__label">楽しむ前に</div>
          <p><strong>20歳未満の飲酒は法律で禁じられています。</strong>　お酒を飲んだら運転はできません（飲酒運転は法律で禁止されています）。妊娠中・授乳期の飲酒は、おなかの赤ちゃんに影響することがあります。適量を守り、自分のペースで楽しんでください。</p>
        </div>
        <div class="readmore">
          <a href="craftsake-towa.html">
            <div class="readmore__k">あわせて読む</div>
            <div class="readmore__t">そもそもクラフトサケとは？</div>
          </a>
          <a href="index.html">
            <div class="readmore__k">INDEX</div>
            <div class="readmore__t">読みもの一覧へ</div>
          </a>
        </div>
      </div>
    </section>

  </div>
"""
    html = page_head("クラフトサケの飲み方・楽しみ方",
                     "クラフトサケをもっとおいしく。温度帯による味の変化、生酒・にごりの保存、活性タイプの開け方、ワイングラスやソーダ割りといったスタイル、料理とのペアリング、和らぎ水まで、自由な酒の楽しみ方を解説します。")
    html += masthead(article_masthead_label("nomikata"), "A Field Guide")
    html += hero(
        article_eyebrow("nomikata"),
        'クラフトサケの<span class="accent">飲み方</span>。<br>自由だから、おいしい。',
        "冷やでも燗でも、グラスでもソーダ割りでも。温度・保存・濁りの扱い・器・ペアリングのちょっとしたコツで、クラフトサケはもっと豊かに楽しめます。")
    html += body
    html += footer()
    return html


# ────────────── 記事③：おすすめ12選（編集部セレクト） ──────────────

# 編集部セレクト。番号は人気・売上順ではなく、タイプ別に並べた見取り図。
# スペックは BRANDS[slug][idx] から直接引くため転記ミス（＝嘘）が出ない。
OSUSUME_PICKS = [
    ("はじめの一本に", "FIRST BOTTLE", "ine-to-agave", 0,
     "クラフトサケの代名詞ともいえる一本。白ブドウや白桃を思わせる柔らかな香りで、「日本酒ともワインとも違う」第一印象をくれる。まず一本選ぶなら、ここから。"),
    ("はじめの一本に", "FIRST BOTTLE", "haccoba", 0,
     "クラフトサケというムーブメントを切り拓いた蔵の看板。東北の古い製法「花酛」にビール由来のドライホッピングを掛け合わせた、爽やかで親しみやすい味わい。"),
    ("はじめの一本に", "FIRST BOTTLE", "konohanano", 0,
     "本格純米のにごりに、シュワッとした微発泡。価格も手に取りやすく、にごり酒の心地よさを知る入り口にうってつけ。"),
    ("ホップサケ — ビール好きに", "HOP SAKE", "lagoon", 0,
     "「シトラ」というホップ由来の柑橘香と、米の旨みが同居する一本。クラフトビール好きが「サケ」へ踏み出す、ちょうどいい橋渡し。"),
    ("ホップサケ — ビール好きに", "HOP SAKE", "librom", 4,
     "福岡のブルワリー的アプローチ。ホップ品種をはっきり打ち出した、香り重視の設計。米の酒の概念がやわらかくほどける。"),
    ("果実サケ — 華やかに", "FRUIT SAKE", "librom", 3,
     "福岡県産いちご「あまおう」を絡めた、甘酸っぱく華やかな果実サケ。ワインやナチュールが好きな人への一本に。"),
    ("果実サケ — 華やかに", "FRUIT SAKE", "lagoon", 2,
     "新潟のブランド洋梨ル・レクチェを使った季節銘柄。果実のみずみずしい香りと、純米の旨みが静かに重なる。"),
    ("古典どぶろく・純米 — 米の旨み", "DOBUROKU", "happy-taro", 0,
     "米だけで醸す、定番のどぶろく。濃い米の旨みと優しい甘み。味噌や漬物などの発酵食品、和の食卓と響き合う、日々に寄り添う一本。"),
    ("古典どぶろく・純米 — 米の旨み", "DOBUROKU", "nondo", 5,
     "岩手・遠野の、水もと仕込み・無添加の生どぶろく。乳酸由来の綺麗な酸が、米の旨みをきりりと引き締める。"),
    ("通好み・受賞・特別な一本", "CONNOISSEUR", "pukupuku", 4,
     "蔵付き酵母を使い、木桶で醸したどぶろく。ICC SAKE AWARD 2025で頂点に立った、いま最も注目される造りのひとつ。"),
    ("通好み・受賞・特別な一本", "CONNOISSEUR", "nondo", 0,
     "水もと × 木桶 × 150日超の長期発酵。米糠まで活かし、柑橘を思わせる香りと軽やかな甘みをまとう。贈り物にもふさわしい。"),
    ("通好み・受賞・特別な一本", "CONNOISSEUR", "adachi-noujo", 0,
     "焼酎用の白麹で仕込んだ、スッキリとした綺麗さと心地よい酸。クラフトサケの「酸」の表現を味わいたい人に。"),
]


def _osusume_spec(b):
    parts = []
    parts.append(f"度数 <b>{b['abv']}%</b>" if b.get("abv") is not None else "度数 <b>非公開</b>")
    parts.append(f"容量 <b>{b['volume_ml']}ml</b>" if b.get("volume_ml") else "容量 <b>—</b>")
    parts.append(f"参考価格 <b>¥{b['price']:,}</b>" if b.get("price") else "価格 <b>公式非開示</b>")
    return " ／ ".join(parts)


def _osusume_tags(b):
    subs = b.get("sub_ingredients") or []
    if not subs:
        return '<span class="pick__tag">副原料 非開示</span>'
    return "".join(f'<span class="pick__tag">{s}</span>' for s in subs)


def build_osusume():
    cards = ""
    cur_group = None
    for i, (group, group_en, slug, idx, comment) in enumerate(OSUSUME_PICKS, start=1):
        if group != cur_group:
            cur_group = group
            cards += f'    <div class="pick-group">{group}<span class="en">{group_en}</span></div>\n'
        kura = by_slug(slug)
        b = BRANDS[slug][idx]
        btn = (f'<a class="pick__btn" href="{rakuten_search(b["name"])}" target="_blank" rel="noopener sponsored">楽天市場で探す →</a>'
               '<span class="pick__pr">PR</span>') if RAKUTEN_ENABLED else ""
        cards += f"""    <div class="pick">
      <div class="pick__no">{i:02d}</div>
      <div class="pick__body">
        <div class="pick__head">
          <span class="pick__kura"><a href="../brewery/{slug}.html">{kura['name']}</a>　{kura['prefecture']}</span>
          <span class="pick__name">{b['name']}</span>
        </div>
        <div class="pick__tags">{_osusume_tags(b)}</div>
        <div class="pick__spec">{_osusume_spec(b)}</div>
        <p class="pick__note">{comment}</p>
        <div class="pick__links">
          <a class="pick__detail" href="../brand/{slug}-{idx}.html">銘柄の詳細を見る →</a>
          {btn}
        </div>
      </div>
    </div>
"""

    # スペック比較表
    rows = ""
    for i, (group, group_en, slug, idx, comment) in enumerate(OSUSUME_PICKS, start=1):
        kura = by_slug(slug)
        b = BRANDS[slug][idx]
        subs = b.get("sub_ingredients") or []
        typ = subs[0] if subs else "—"
        abv = f"{b['abv']}%" if b.get("abv") is not None else "—"
        vol = f"{b['volume_ml']}ml" if b.get("volume_ml") else "—"
        price = f"¥{b['price']:,}" if b.get("price") else "—"
        rows += (f'<tr><td class="nm"><a href="../brand/{slug}-{idx}.html">{b["name"]}</a></td>'
                 f'<td>{kura["name"]}</td><td>{typ}</td><td>{abv}</td><td>{vol}</td>'
                 f'<td class="p">{price}</td></tr>\n')

    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "EDITORS' PICKS / 選び方の地図")}
      <div class="prose">
        <p class="lead">クラフトサケは、<span class="accent">自由</span>な酒。ホップ、果実、ハーブ、米だけの濃いどぶろく——幅が広いぶん、最初の一本に迷う。そこで saketto 編集部が、収録する25の蔵・120を超える銘柄から、<span class="accent">タイプ別に12本</span>を選びました。</p>
        <p>「日本酒は知っているけれど、クラフトサケは初めて」という人も、「もう何本か飲んだから、次の一本を」という人も。下のグループを入り口に、自分に合いそうな一本を見つけてください。各銘柄のスペックは、saketto が一次ソース（各蔵の公式情報）で確認したものです。</p>
        <div class="callout">
          <div class="callout__label">この12選について</div>
          <p>このリストは、収録銘柄の中から「タイプの代表性・はじめての入りやすさ・話題性・入手のしやすさ」を目安に編集部が選んだものです。<strong>番号は人気や売上の順位ではなく</strong>、タイプ別に読みやすく並べた見取り図です。価格・度数などは2026年5月時点の確認値で、ロットや時期によって変わります。最新の価格・在庫は各リンク先でご確認ください。</p>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("02", "THE 12 / 12本")}
      <div class="prose">
        <p>気になった一本は、銘柄ページから味わいの詳細や蔵の物語を辿れます。「楽天市場で探す」では、その銘柄名で楽天市場の検索結果へ移動します（在庫・価格は時期により変動します）。</p>
      </div>
{cards}    </section>
{divider()}
    <section class="section">
{section_meta("03", "COMPARISON / スペック比較")}
      <div class="prose">
        <h2 class="sub-h">12本を、<span class="accent">ひと目</span>で。</h2>
        <p>度数・容量・参考価格を一覧で。「—」は公式に非開示、またはロットで変動するものです。</p>
      </div>
      <div class="cmp-wrap">
        <table class="cmp">
          <thead><tr><th>銘柄</th><th>蔵</th><th>タイプ</th><th>度数</th><th>容量</th><th>参考価格</th></tr></thead>
          <tbody>
{rows}          </tbody>
        </table>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("04", "HOW TO CHOOSE / 選び方")}
      <div class="prose">
        <h2 class="sub-h">迷ったら、<span class="accent">入り口</span>を決める。</h2>
        <p>選び方に正解はありませんが、目安はあります。<strong>ビールやクラフトビールが好き</strong>なら、ホップサケから。<strong>ワインやナチュールが好き</strong>なら、果実サケや酸の効いた一本へ。<strong>日本酒の旨みが好き</strong>なら、米だけで醸す古典どぶろくへ。迷ったら、まず「はじめの一本に」の3本から始めるのがおすすめです。</p>
        <p>もっと自由に探したいときは、saketto の4つの軸が役立ちます。香りの素材から辿る<a href="../subingredients/">副原料</a>、造りや個性で選ぶ<a href="../genre/">ジャンル</a>、旅するように探す<a href="../region/">地域</a>、お得に試す<a href="../furusato/">ふるさと納税</a>。</p>
        <div class="pill-links">
          <a href="../subingredients/">副原料から<span class="arr">→</span></a>
          <a href="../genre/">ジャンルから<span class="arr">→</span></a>
          <a href="../region/">地域から<span class="arr">→</span></a>
          <a href="../furusato/">ふるさと納税から<span class="arr">→</span></a>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("05", "FAQ / よくある質問")}
      <div class="prose">
        <h2 class="sub-h tight">クラフトサケは、どこで買えますか。</h2>
        <p>多くは各蔵の公式オンラインショップや取扱酒販店、楽天市場などのECで手に入ります。少量生産・限定流通の銘柄も多く、季節や入荷のタイミングで在庫は変わります。気になる一本は、見かけたときが買いどきです。</p>
        <h2 class="sub-h tight">日本酒とどう違うのですか。</h2>
        <p>ざっくり言えば、クラフトサケは「日本酒（清酒）の定義の<strong>外</strong>」で自由に醸された米の酒。副原料を加えたり、もろみを濾さなかったりするため、酒税法上は多くが「その他の醸造酒」に分類されます。詳しくは<a href="craftsake-towa.html">クラフトサケとは</a>をご覧ください。</p>
        <h2 class="sub-h tight">どう飲むのがおいしいですか。</h2>
        <p>まずは冷やして、その個性を確かめるのがおすすめ。温度・保存・濁りの扱い・器・割り方のコツは<a href="nomikata.html">飲み方・楽しみ方</a>でまとめています。</p>
        <div class="callout">
          <div class="callout__label">楽しむ前に</div>
          <p><strong>20歳未満の飲酒は法律で禁じられています。</strong>　飲酒運転は法律で禁止されています。妊娠中・授乳期の飲酒はお控えください。適量を守り、自分のペースでお楽しみください。</p>
        </div>
        <div class="readmore">
          <a href="craftsake-towa.html">
            <div class="readmore__k">あわせて読む</div>
            <div class="readmore__t">そもそもクラフトサケとは？</div>
          </a>
          <a href="index.html">
            <div class="readmore__k">INDEX</div>
            <div class="readmore__t">読みもの一覧へ</div>
          </a>
        </div>
      </div>
    </section>

  </div>
"""
    html = page_head("クラフトサケ おすすめ12選 — はじめの一本から通好みまで【編集部セレクト】",
                     "クラフトサケのおすすめを、saketto編集部がタイプ別に12本厳選。稲とアガベ・haccoba・LAGOON・ぷくぷく醸造など、収録DBの確認済みスペック（度数・容量・参考価格）とともに、はじめての一本から通好みの受賞銘柄までを紹介します。")
    html += masthead(article_masthead_label("osusume"), "A Field Guide")
    html += hero(
        article_eyebrow("osusume"),
        'クラフトサケ、<br><span class="accent">最初の12本</span>。',
        "ホップ、果実、米だけの濃いどぶろく——自由な酒だから、入り口も自由。編集部がタイプ別に選んだ12本を、確認済みのスペックとともに。")
    html += body
    html += footer()
    return html


# ────────────── 実行 ──────────────

def main():
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "index.html").write_text(build_index(), encoding="utf-8")
    (OUT_DIR / "craftsake-towa.html").write_text(build_towa(), encoding="utf-8")
    (OUT_DIR / "nomikata.html").write_text(build_nomikata(), encoding="utf-8")
    (OUT_DIR / "osusume.html").write_text(build_osusume(), encoding="utf-8")
    print(f"OK ガイド生成: guide/index.html（一覧）＋ 記事{len(ARTICLES)}本")


if __name__ == "__main__":
    main()

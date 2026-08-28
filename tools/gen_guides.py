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
from site_common import head_extra, seo_head, breadcrumb, website_node, SITE_URL
from breweries_brands import BRANDS          # おすすめ記事：スペックを一次ソースDBから直接引く
from breweries_master import by_slug
from moshimo_link import resolve_rakuten, resolve_amazon
from gen_sample_v2 import RAKUTEN_ENABLED, AMAZON_ENABLED

REPO_ROOT = Path(__file__).resolve().parent.parent  # saketto_repo/
OUT_DIR = REPO_ROOT / "guide"

# 読みものの構造化データ用 日付（ISO8601）。内容を大きく更新したら dateModified を更新する。
ARTICLE_PUBLISHED = "2026-05-31"
ARTICLE_MODIFIED = "2026-06-03"

# 記事ごとの公開日の上書き（あとから追加した記事はここに入れる）。
# 全記事で同じ日付を配信すると、新しい記事も旧日付で公開されたとGoogleに伝わるため。
ARTICLE_DATES = {
    "/guide/doburoku.html": ("2026-08-10", "2026-08-10"),
    "/guide/doko-de-kaeru.html": ("2026-08-10", "2026-08-10"),
    "/guide/zenkoji.html": ("2026-08-10", "2026-08-10"),
    "/guide/new-breweries.html": ("2026-08-10", "2026-08-10"),
}


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
.pick__btn--amazon { color:var(--accent); background:transparent; border:1px solid var(--accent); margin-left:.5rem; }
.pick__btn--amazon:hover { color:var(--paper); background:var(--accent); }
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

def page_head(title, description, path="/guide/", og_type="website"):
    short = title.split(" — ")[0].split("【")[0].strip()  # パンくず/headline用の短縮名
    published, modified = ARTICLE_DATES.get(path, (ARTICLE_PUBLISHED, ARTICLE_MODIFIED))
    if og_type == "article":
        jsonld = [
            {"@context": "https://schema.org/", "@type": "Article",
             "headline": short, "description": description, "inLanguage": "ja",
             "datePublished": published, "dateModified": modified,
             "author": {"@type": "Organization", "name": "saketto 編集部"},
             "publisher": {"@type": "Organization", "name": "saketto", "url": SITE_URL + "/",
                           "logo": {"@type": "ImageObject", "url": SITE_URL + "/apple-touch-icon.png"}},
             "image": SITE_URL + "/assets/images/og.png",
             "mainEntityOfPage": SITE_URL + path},
            breadcrumb([("トップ", "/"), ("読みもの", "/guide/"), (short, path)]),
        ]
    else:
        crumb = [("トップ", "/")] + ([] if path == "/guide/" else [("読みもの", "/guide/")]) + [("読みもの" if path == "/guide/" else short, path)]
        jsonld = [
            {"@context": "https://schema.org/", "@type": "CollectionPage",
             "name": f"{title} — saketto.", "description": description,
             "url": SITE_URL + path, "isPartOf": website_node()},
            breadcrumb(crumb),
        ]
    seo = seo_head(path, title, description, og_type=og_type, jsonld=jsonld)
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
      <a href="../brewery/">蔵</a>
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
        PR ／ 当サイトはアフィリエイト広告（Amazonアソシエイト含む）を掲載しています<span class="colophon__sep">／</span>
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
    {
        "slug": "kioke",
        "category": "deep",
        "eyebrow_en": "KIOKE BREWING",
        "title": "木桶仕込みとは",
        "summary": "なぜ木の桶で醸すのか。江戸期に主流だった木桶がホーロー・ステンレスに置き換わった歴史、桶に棲む蔵付き微生物、木桶職人復活プロジェクト、そしてクラフトサケが木桶に回帰する理由を深掘り。",
    },
    {
        "slug": "gift",
        "category": "choose",
        "eyebrow_en": "GIFT GUIDE",
        "title": "ギフトに贈るクラフトサケ",
        "summary": "手土産・誕生日・お祝い・自分へのご褒美。シーンと予算別に、贈って喜ばれるクラフトサケを編集部が厳選。話題性や華やかさ、物語のある一本を、確認済みスペックと贈るときの注意点とともに。",
    },
    {
        "slug": "hanamoto",
        "category": "deep",
        "eyebrow_en": "HANAMOTO",
        "title": "花酛（はなもと）とは",
        "summary": "東北に伝わる“幻のどぶろく製法”、花酛。東洋のホップ「唐花草」を使い、ビールのように醸す。なぜ幻になり、haccobaがどう甦らせ、それがなぜクラフトサケの原点なのかを深掘り。",
    },
    {
        "slug": "doburoku",
        "category": "know",
        "eyebrow_en": "WHAT IS DOBUROKU",
        "title": "どぶろくとは",
        "summary": "白く濁った米の酒、どぶろく。にごり酒・清酒との違いはどこにあるのか。「こす／こさない」という一線が酒の呼び名を分ける仕組みから、家庭の酒だった歴史、いまクラフトサケの主役になった理由まで。",
    },
    {
        "slug": "doko-de-kaeru",
        "category": "choose",
        "eyebrow_en": "WHERE TO BUY",
        "title": "クラフトサケはどこで買える？",
        "summary": "少量生産のクラフトサケは、探し方にコツがいる。蔵の公式オンラインショップ、通販モール、ふるさと納税、店頭限定——4つの入口の違いと、要冷蔵・季節限定という壁の越え方を、収録蔵の公式情報をもとに。",
    },
    {
        "slug": "zenkoji",
        "category": "deep",
        "eyebrow_en": "FULL KOJI",
        "title": "全麹酒とは",
        "summary": "米をすべて麹にして醸す、全麹（ぜんこうじ）。掛米を使わないという一点で、酒は清酒の枠を外れ、濃密な甘みと酸をまとう。なぜ手間をかけてまで麹だけで造るのか、その設計思想を掘り下げる。",
    },
    {
        "slug": "new-breweries",
        "category": "deep",
        "eyebrow_en": "NEW BREWERIES",
        "title": "いま生まれている、新しい蔵",
        "summary": "駅のホーム、商店街のアーケード、島、団地の一角。2024年以降に生まれたクラフトサケの蔵は、これまで酒蔵がなかった場所に立つ。saketto収録25蔵の開業年から、いま何が起きているのかを読む。",
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
{blocks}    <p class="guide-foot">クラフトサケの世界を、知って・選んで・深く味わうための読みもの。基礎から製法まで10本を揃えています。まず一本に出会いたい方は、<a href="../index.html">トップ</a>の4つの軸からどうぞ。</p>
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
        <p>とりわけ奥が深い<a href="hanamoto.html">花酛（はなもと）</a>と<a href="kioke.html">木桶仕込み</a>は、それぞれ一本の読みものとして掘り下げている。こうした製法や副原料の個性は、saketto では<a href="../genre/">ジャンル</a>や<a href="../subingredients/">副原料</a>の軸からも辿れる。気になることばを入り口に、酒を探してみてほしい。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("07", "MAKING / どうやって造るのか")}
      <div class="prose">
        <h2 class="sub-h">米が酒になるまでの、<span class="accent">四つの仕事</span>。</h2>
        <p>クラフトサケの造りは、基本のところで日本酒と変わらない。<strong>米を蒸し、麹をつくり、酵母を育て、発酵させる</strong>——この四つの仕事の積み重ねだ。違いが出るのは、その先の一手にある。</p>
        <p>まず<strong>製麹（せいきく）</strong>。蒸した米に麹菌を植えつけ、温度と湿度を管理しながら育てる。麹がつくる酵素が、米のデンプンを糖へ変える。ここでどの麹菌を選ぶかが、味の方向を大きく決める。黄麹なら穏やかな甘み、白麹ならクエン酸由来のはっきりした酸——同じ米から、まるで違う酒が生まれる。</p>
        <p>次に<strong>酒母（しゅぼ）</strong>づくり。酵母を安全に増やすための、いわば種の仕込みだ。乳酸を添加して雑菌を抑える速醸、乳酸菌の力を借りる生酛・山廃、そして<a href="hanamoto.html">花酛</a>のように植物の力を借りる古い手法もある。</p>
        <p>そして<strong>もろみの発酵</strong>。ここでクラフトサケは大きく分岐する。副原料——ホップ、果実、茶葉、ボタニカル——を、どの段階で、どれだけ入れるか。仕込みの最初から一緒に発酵させれば果実味が酒に溶け込み、発酵の後半に加えれば香りが立つ。ビールのドライホッピングを応用した造り手もいる。</p>
        <p>最後が<strong>搾るか、搾らないか</strong>。搾れば澄んだ酒に、搾らなければ<a href="doburoku.html">どぶろく</a>になる。この一手が、法律上の区分までも決めてしまう。<strong>同じ四つの仕事を経ながら、最後の選択で酒の名前が変わる</strong>——クラフトサケの自由は、この工程の一つひとつに宿っている。</p>
        <p>加えて、<strong>火入れするかどうか</strong>という選択もある。加熱して酵母の働きを止めれば味が安定し、常温での流通もできる。止めなければ瓶の中で発酵が続き、届いたあとも味が動いていく。<strong>安定を取るか、変化を取るか</strong>——ここにも造り手の考えが出る。要冷蔵の生酒が多いのは、多くのクラフトサケが後者を選んでいるからだ。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("08", "PRICE / 値段の理由")}
      <div class="prose">
        <h2 class="sub-h">なぜ、<span class="accent">この価格</span>なのか。</h2>
        <p>クラフトサケを手に取ると、四合瓶で2,000円台が中心、造りに手をかけた一本は5,000円を超えることもある。スーパーの棚に並ぶ酒に慣れていると、少し高く感じるかもしれない。その理由は、造りの構造そのものにある。</p>
        <p>ひとつは<strong>仕込みの規模</strong>だ。大手の蔵が一度に大きなタンクで仕込むのに対し、クラフトサケの多くは小さな仕込みを重ねる。同じ手間をかけても、生まれる本数がまるで違う。一本あたりが背負うコストは、どうしても大きくなる。</p>
        <p>ふたつめは<strong>副原料</strong>。ホップ、果実、茶葉、ハーブ——米以外の原料は、それ自体に相応の価格がある。しかも農産物である以上、その年の出来に左右される。地元の農家と組んで少量を仕入れる造りなら、なおさらだ。</p>
        <p>みっつめは<strong>流通の形</strong>。要冷蔵の生酒はクール便が前提になる。輸送にも保管にもコストがかかり、そのぶん価格に乗る。<strong>ラベルの数字は、そのまま造りの選択の記録</strong>だと思うと、見え方が変わってくる。買える場所ごとの違いは<a href="doko-de-kaeru.html">どこで買える？</a>にまとめている。</p>
        <div class="callout">
          <div class="callout__label">saketto の価格表示について</div>
          <p>本サイトに掲載している価格は、各蔵の公式サイト・公式オンラインショップで確認した時点のものです。<strong>確認日を併記しています</strong>が、ロットや年度で改定されることがあります。購入時は各販売ページで最新の価格をご確認ください。</p>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("09", "BY THE NUMBERS / 数字で見る")}
      <div class="prose">
        <h2 class="sub-h">143本を並べて、<span class="accent">見えたこと</span>。</h2>
        <p>クラフトサケは「自由な酒」と語られる。だが自由とは具体的に何を指すのか。saketto が収録する143銘柄を実際に集計してみると、その輪郭が数字になって現れる。</p>
        <p>まず<strong>副原料の表記は76通り</strong>。ホップ、果実、茶葉、ボタニカル、出汁、ホエー、カカオ——143本のなかに、76通りの「米以外」が記録されている。<strong>およそ2本に1種類の割合で新しい素材が登場している</strong>計算だ。日本酒が米・米麹・水という三つの原料で千年以上の表現を積み上げてきたことを思えば、この散らばり方は異様ですらある。</p>
        <p>分類してみると、<strong>米と麹だけで醸すものが47銘柄</strong>ともっとも多い。次いで<strong>果実が28、ホップが19、アガベ・蜂蜜・出汁などの特殊な副原料が16、茶葉・ハーブが15、大麦麹・蕎麦麹・発芽玄米といった穀物や特殊な麹が10</strong>と続く（副原料を複数使う銘柄は主たるものに寄せて分類。副原料が公式非開示の8銘柄は除く）。<strong>「自由な酒」の三分の一近くが、じつは何も足していない</strong>——この事実は、クラフトサケが副原料の物珍しさだけで成り立っているわけではないことを示している。搾らないという選択そのものが、すでに表現になっているのだ。</p>
        <p>価格は<strong>中央値2,750円</strong>。判明している101銘柄のうち<strong>54銘柄が2,000円台</strong>に集まり、3,000〜4,999円が27銘柄。5,000円を超えるものは9銘柄しかない。<strong>大半は、日常の食卓に届く価格帯</strong>にある。度数は、ノンアルコールの甘酒を除くと4度から17度まで幅があり、中央値は13度。容量は720mlが49銘柄、500mlが30銘柄で、四合瓶と、その少し小さいサイズが主流だ。</p>
        <p>これらの数字が語るのは、<strong>クラフトサケが「珍しい実験酒」から「選べる日常の酒」へ移りつつある</strong>ということだろう。76通りの素材という振れ幅を持ちながら、価格と容量はきわめて現実的な範囲に収まっている。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("10", "FAQ / よくある質問")}
      <div class="prose">
        <h2 class="sub-h tight">クラフトサケと日本酒は、<span class="accent">何が違う</span>のですか？</h2>
        <p>原料も造りも近いのですが、酒税法上の区分が違います。日本酒（清酒）は「米・米こうじ・水などを原料として発酵させ、<strong>こしたもの</strong>」と定められており、この定義から外れる酒は「その他の醸造酒」などに分類されます。もろみをこさない、あるいは米以外の副原料を使う——クラフトサケの多くはこの枠で造られています。味の優劣ではなく、あくまで制度上の線引きです。</p>
        <h2 class="sub-h tight">「クラフトサケ」は<span class="accent">誰が決めた</span>呼び名ですか？</h2>
        <p>造り手たち自身です。2022年に発足したクラフトサケブリュワリー協会が、この呼称を掲げました。法律上の用語ではないため、蔵によっては別の言い方をすることもあります。<a href="new-breweries.html">新しい蔵</a>の記事では、この呼び名が生まれた背景にも触れています。</p>
        <h2 class="sub-h tight">度数は<span class="accent">どのくらい</span>ですか？</h2>
        <p>銘柄によって幅が大きく、saketto に収録している範囲では4度前後から17度程度まであります。低アルコールを狙って設計されたものから、原酒に近い濃厚なタイプまでさまざまです。ラベルの表示を確認してください。</p>
        <h2 class="sub-h tight">クラフトサケは<span class="accent">どこで買える</span>のですか？</h2>
        <p>蔵の公式オンラインショップ、通販モール、ふるさと納税、醸造所併設の店舗——大きく4つの入口があります。少量生産のため、スーパーや一般的な酒販店では見かけないことが多いです。詳しくは<a href="doko-de-kaeru.html">どこで買える？</a>にまとめました。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("11", "HOW TO EXPLORE / 探し方")}
      <div class="prose">
        <h2 class="sub-h">4つの軸から、<span class="accent">次の一本</span>へ。</h2>
        <p>クラフトサケの面白さは、その多様さにある。saketto では、25の蔵と140を超える銘柄を、4つの軸から横断的に探せる。気になる入り口から、次に出会う一本を見つけてほしい。</p>
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
                     "クラフトサケとは何か。酒税法上の「その他の醸造酒」という位置づけ、日本酒・どぶろくとの区分の違い、新規参入の仕組み、クラフトサケブリュワリー協会、花酛・白麹・全麹などの醸造用語まで、その全体像をやさしく解説します。",
                     "/guide/craftsake-towa.html", "article")
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
        <p>開栓したあとは風味が変わりやすい。<strong>生酒・にごりは数日から一週間、火入れしたものはもう少し長く</strong>を目安に。これらはあくまで一般的な目安で、ボトルに「要冷蔵」などの表示があれば、それが何よりのガイドになる。</p>
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
{section_meta("07", "SEASON / 季節で楽しむ")}
      <div class="prose">
        <h2 class="sub-h">一年を、<span class="accent">四つの顔</span>で。</h2>
        <p>クラフトサケは季節限定の銘柄が多い（その理由は<a href="doko-de-kaeru.html">どこで買える？</a>で扱っている）。ここで見たいのは、季節ごとにどう<strong>飲む</strong>かだ。</p>
        <p><strong>春</strong>は苺や柑橘を使った果実サケが並ぶ時期。搾りたての生酒も出まわる。よく冷やして、ワイングラスで香りごと楽しみたい。<strong>夏</strong>は炭酸の効いた活性タイプやホップサケの季節。キンと冷やしてソーダで割れば、ビールのような感覚で飲める。低アルコールのタイプも夏向きだ。</p>
        <p><strong>秋</strong>は新米の季節。その年に穫れた米で仕込んだ酒が出はじめ、ひやおろしのように少し落ち着いた味わいが楽しめる。ぶどうや梨を使った果実サケもこの時期だ。<strong>冬</strong>は燗が似合う。どぶろくをぬるめに温めれば甘みがふくらみ、<a href="zenkoji.html">全麹酒</a>のような濃密なタイプは体を温める一杯になる。柑橘の季節でもあるので、八朔やレモンを使った銘柄も出てくる。</p>
        <p><strong>同じ蔵の酒を季節ごとに追う</strong>のは、クラフトサケならではの楽しみ方だ。造り手が何を考え、どこへ向かっているのかが、一年の流れのなかに見えてくる。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("08", "LEFTOVER / 飲み切れなかったら")}
      <div class="prose">
        <h2 class="sub-h">残った酒は、<span class="accent">育てる</span>。</h2>
        <p>四合瓶（720ml）を一度で飲み切るのは、なかなか難しい。だがクラフトサケの場合、<strong>残すことが必ずしもマイナスではない</strong>。とくに生タイプは、日が経つにつれて味が動いていく。</p>
        <p>保管の基本は前の節のとおりだが、飲み残しでとくに効くのは<strong>栓をしっかり閉めて、立てたまま冷蔵庫へ</strong>という一点だ。横に寝かせると、キャップの内側から風味が抜けやすくなる。</p>
        <p>おもしろいのは<strong>味の変化</strong>だ。開けた直後はガスが強く尖って感じられた酒が、二日目には落ち着いて甘みが出てくる。三日目には酸が前に出る——そんなふうに表情が変わっていく。<strong>「変わってしまった」ではなく「変わっていく」と捉える</strong>と、一本を数日かけて飲む楽しみが生まれる。</p>
        <p>それでも余ってしまったら、料理に使う手もある。米と麹の甘みは、煮物やドレッシング、肉を漬け込む下ごしらえによく合う。加熱すればアルコールは飛ぶ。<strong>捨てるくらいなら、台所へ</strong>。もともと米からできた調味料のような存在なのだから、相性が悪いはずがない。</p>
        <p>もうひとつ、<strong>凍らせる</strong>という手もある。度数が低めのものなら、製氷皿に注いで凍らせておけば、次に同じ酒を飲むときの氷になる。溶けても薄まらないので、ロックで飲むときに重宝する。シャーベット状にしてデザート代わりにするのも、度数の低いにごりタイプなら楽しい。<strong>一本を最後まで使い切る工夫は、そのまま楽しみ方の幅になる</strong>。</p>
        <p>ただし、どの方法にも共通する前提がひとつ。<strong>その酒がいま「おいしい」かどうかは、自分の舌で確かめる</strong>ということだ。目安の日数を過ぎていても良い状態のこともあれば、その逆もある。香りに違和感があれば無理をしない——それだけ守れば、あとは自由に楽しんでいい。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("09", "MAKER'S NOTE / 造り手の推奨に従う")}
      <div class="prose">
        <h2 class="sub-h">迷ったら、<span class="accent">蔵の言葉</span>を読む。</h2>
        <p>ここまで温度や器の話をしてきたが、じつはもっと確実な指針がある。<strong>造り手自身が示している飲み方</strong>だ。saketto が収録する銘柄のうち、<strong>50件で蔵の推奨する温度帯が公開されている</strong>。</p>
        <p>並べてみると、いちばん多いのは<strong>「冷やして」</strong>。生酒や果実を使った銘柄が多いクラフトサケでは、これが基本になる。だが注目したいのは、<strong>「冷酒から燗まで」「常温15度から42度のお燗酒まで」「ひやからぬる燗」</strong>といった、<strong>幅で示す蔵が少なくない</strong>ことだ。</p>
        <p>幅で示すというのは、<strong>どこで飲んでも成立するように設計している</strong>という宣言でもある。温度を変えて何度も表情を確かめてほしい——そういう意図が読み取れる。逆に「50〜60度」と狭く指定する銘柄もあり、これは燗酒専用として設計された一本だ。ここを外すと、造り手が意図した味に届かない。</p>
        <p>ラベルや商品ページに書かれた一行は、<strong>その酒を誰よりも知っている人が残した最短の攻略法</strong>である。ネットで見つけた一般論より、まずそちらを試したい。saketto の各銘柄ページにも、公式で確認できた推奨温度を掲載している。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("10", "FAQ / よくある質問")}
      <div class="prose">
        <h2 class="sub-h tight">グラスは<span class="accent">何を</span>使えばいいですか？</h2>
        <p>迷ったらワイングラスです。口が広く上がすぼまった形は香りをまとめてくれるので、果実サケやホップサケの華やかさがよく出ます。冷酒や燗を少しずつ飲むならおちょこ、温度の移ろいまで味わうならぐい呑み——器を替えるだけで同じ酒が違う顔を見せます。詳しくは本文の「器」の節をご覧ください。</p>
        <h2 class="sub-h tight">どぶろくを<span class="accent">温めても</span>いいですか？</h2>
        <p>問題ありません。ぬるめ（40度前後）に温めると甘みがふくらみ、冷やしたときとは別の表情になります。ただし急激に高温にすると香りが飛びやすいので、湯煎でゆっくり温めるのがおすすめです。活性タイプは加熱で吹きこぼれることがあるため、ガスが落ち着いてからにしてください。</p>
        <h2 class="sub-h tight">開けたら<span class="accent">吹き出して</span>しまいました。</h2>
        <p>瓶内で発酵が続く活性タイプによくあることです。次回は<strong>しっかり冷やし、瓶を立てたまま、栓を少し開けてはガスを逃がす</strong>のを数回くり返してください。シンクの上で、ボウルにグラスを置いて開けると安心です。振ってしまった場合は、半日ほど冷蔵庫で落ち着かせてから開けます。</p>
        <h2 class="sub-h tight">お酒が<span class="accent">強くない</span>のですが、楽しめますか？</h2>
        <p>低アルコールに設計された銘柄や、ソーダで割って飲めるタイプがあります。度数5〜8度ほどのものはビールに近い感覚で飲めます。無理のない量で、水（和らぎ水）を挟みながらお楽しみください。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("11", "ENJOY WELL / 心地よく楽しむ")}
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
                     "クラフトサケをもっとおいしく。温度帯による味の変化、生酒・にごりの保存、活性タイプの開け方、ワイングラスやソーダ割りといったスタイル、料理とのペアリング、和らぎ水まで、自由な酒の楽しみ方を解説します。",
                     "/guide/nomikata.html", "article")
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
# コメントの事実部分（蔵の哲学・特徴・製法・受賞）は breweries_master / breweries_brands /
# awards の確認済みデータに基づく。味の表現・「こんな人に」は編集部の評価。
GROUP_INTROS = {
    "はじめの一本に":
        "クラフトサケが初めてなら、まずは“代表格”から。ジャンルを切り拓いた蔵の看板銘柄は、奇をてらわずに「日本酒とは違う」と一口でわかる。アルコール度数も穏やかなものが多く、入門にいちばん向いている。",
    "ホップサケ — ビール好きに":
        "ビールの香りづけに使うホップを、米の酒に効かせた一群。柑橘や白い花を思わせる華やかなアロマとほろ苦さが特徴で、クラフトビール好きが「サケ」へ踏み出す入り口になりやすい。よく冷やして、できれば香りの立つグラスで。",
    "果実サケ — 華やかに":
        "果実を絡めて醸す、華やかなグループ。甘酸っぱく香り高い味わいは、ワインやナチュールが好きな人と相性がいい。食前酒として、あるいは軽い前菜と合わせて楽しみたい。",
    "古典どぶろく・純米 — 米の旨み":
        "副原料を使わず、米と米麹だけで醸す原点の酒。とろりと濃い米の旨みと、製法ごとに表情を変える酸が魅力だ。味噌や漬物などの発酵食品、和の食卓と深く響き合う、滋味のある一群。",
    "通好み・受賞・特別な一本":
        "もう何本か飲んだ人へ。受賞銘柄や、木桶仕込み・長期発酵といった手間のかかる造りから、特別な一本を選んだ。自分へのご褒美にも、贈り物にも。",
}

OSUSUME_PICKS = [
    ("はじめの一本に", "FIRST BOTTLE", "ine-to-agave", 0,
     "クラフトサケというジャンルそのものを切り拓いた、秋田・男鹿の稲とアガベ醸造所。その代名詞がこのCRAFTシリーズだ。テキーラの原料として知られるアガベのシロップを副原料に用い、白ブドウや白桃を思わせる柔らかな香りをまとう。全量を無肥料・無農薬の自然栽培米で仕込み、精米歩合は90%に統一——米をあえて削りすぎず、その個性をふくよかな旨みとして残す思想が貫かれている。「日本酒ともワインとも違う」第一印象を確かめる、まさに最初の一本。"),
    ("はじめの一本に", "FIRST BOTTLE", "haccoba", 0,
     "「自由を、醸そう。」を体現する先駆者、福島・小高のhaccoba。看板の“はなうたホップス”は、東北に伝わる幻のどぶろく製法「花酛（はなもと）」に、クラフトビールのドライホッピングを掛け合わせた一本だ。ホップ由来の華やかな香りと、米のやさしい甘みが軽やかに溶け合う。アルコールはロットにより11〜13%と程よく、するすると飲めてしまう親しみやすさ。クラフトサケの“はじまりの味”を知るなら、外せない蔵の代表作。"),
    ("はじめの一本に", "FIRST BOTTLE", "konohanano", 0,
     "浅草・駒形でどぶろくを醸す木花之醸造所の看板が、この“ハナグモリ”。本格純米のにごりに、瓶の中で生まれたシュワッとした微発泡が心地よく弾ける。米だけで仕込むやさしい甘酸っぱさは、にごり酒が初めての人にもすっと入っていく。バーを併設し、若い蔵人の“新しい修行の場”としても知られる蔵の顔。価格も手に取りやすく、微発泡のにごりから始めたい人にうってつけだ。"),
    ("ホップサケ — ビール好きに", "HOP SAKE", "lagoon", 0,
     "新潟・福島潟のほとりで、極小規模と持続可能性にこだわって醸すLAGOON BREWERY。ブランド名は「翔空（しょうくう）」。この“HOP SAKE ほっぺ”は、ホップ品種シトラ由来の柑橘香と、米の旨みが同居する爽快な一本だ。果実からトマト＋バジルまで副原料の幅が驚くほど広い蔵だが、その分かりやすい入り口がこのホップサケ。クラフトビール党が「サケ」に踏み出す、最初の一杯にちょうどいい。"),
    ("ホップサケ — ビール好きに", "HOP SAKE", "librom", 4,
     "「自由な醸造にロマンを」を掲げる福岡・LIBROM（社名はLIBERTA〔自由〕＋ROMANZO〔ロマン〕）。バーを併設する醸造所が放つこの一本は、ホップ品種“Hallertau Blanc”をはっきり打ち出した香り重視の設計だ。白ワインを思わせる華やかなアロマで、「米の酒」という先入観がやわらかくほどけていく。九州の素材で自由に遊ぶ蔵の個性が、香りに素直に表れている。"),
    ("果実サケ — 華やかに", "FRUIT SAKE", "librom", 3,
     "福岡が誇るブランドいちご「あまおう」を絡めた、LIBROMの果実サケ。いちごの甘酸っぱさと香りがそのまま立ち上がり、グラスの中まで華やかだ。日本酒が得意でない人や、ふだんワインを好む人への一本としても喜ばれる。地元・福岡の果実を主役に据えるところに、九州の蔵らしい土地への眼差しがある。記念日や手土産にも映える、贈って嬉しい一本。"),
    ("果実サケ — 華やかに", "FRUIT SAKE", "lagoon", 2,
     "新潟のブランド洋梨「ル・レクチェ」を使った、LAGOONの季節銘柄。洋梨のみずみずしく、とろりとした香りと、純米の旨みが静かに重なり合う。槽（ふね）でやさしく搾った生酒で、フレッシュさそのものが身上だ。地域の旬の果実を映すこの蔵らしく、季節限定で巡ってくる——見かけたら逃したくない、出会いの一本。"),
    ("古典どぶろく・純米 — 米の旨み", "DOBUROKU", "happy-taro", 0,
     "滋賀・長浜の糀屋（発酵食品店）が営む、ハッピー太郎醸造所の定番どぶろく。完熟糀ならではの旨みを生かし、伊吹山の伏流水で醸す。米だけの濃い旨みとやさしい甘みは、味噌や漬物などの発酵食品、和の食卓にぴたりと寄り添う。「醗酵でつなぐ、しあわせ」を掲げる発酵のプロが造る、毎日に寄り添う一本。480mlで手頃な価格も、普段づかいに嬉しい。"),
    ("古典どぶろく・純米 — 米の旨み", "DOBUROKU", "nondo", 5,
     "岩手・遠野で、自然栽培米「遠野1号」を醸すnondo。この一本は、室町期に生まれた古い酒母づくり「水もと」で、酵母も加えずに仕込んだ生のどぶろくだ。乳酸由来のきれいな酸が、米の濃い旨みをきりりと引き締める。四代目が長年取り組んできた遠野の風土の酒で、要冷蔵で味わう生きた発酵の余韻は格別。古典製法の奥行きを知りたい人に。"),
    ("通好み・受賞・特別な一本", "CONNOISSEUR", "pukupuku", 4,
     "haccobaで醸造責任者を務めた造り手が独立して立ち上げた、福島・小高のぷくぷく醸造。全量“酵母無添加”の自然発酵に、ビールの技法を掛け合わせる蔵だ。この“#ODAKA”は、蔵に棲みつく蔵付き酵母を使い、木桶で醸したどぶろく。クラフトサケの国際コンペ、ICC SAKE AWARD 2025で頂点に立った注目の造りで、発酵そのものの力強さを味わえる、通好みの一杯。"),
    ("通好み・受賞・特別な一本", "CONNOISSEUR", "nondo", 0,
     "nondoの上級シリーズ「権化（ごんげ）」。水もと × 木桶 × 150日を超える長期発酵という、手間を惜しまない造りで生まれる。米糠まで活かし、柑橘を思わせる香りと軽やかな甘みをまとった、複雑で奥行きのある味わい。一本一本に蔵の思想が宿る、特別な酒だ。じっくり時間をかけて向き合いたい、贈り物にもふさわしい一本。"),
    ("通好み・受賞・特別な一本", "CONNOISSEUR", "adachi-noujo", 0,
     "大阪・高槻、団地の一角で醸す日本初の「団地酒蔵」、足立農醸の第一弾がこのKOYOI。焼酎づくりに使う白麹で仕込み、スッキリとした綺麗さと、クエン酸由来の心地よい酸を生む。「世界が驚く、唯一の日本酒を造りたい」という気概が、酸の効いたモダンな味わいに表れている。クラフトサケならではの“酸”の表現を確かめたい人に、ぜひ。"),
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
            cards += f'    <p class="cat-lead" style="max-width:820px;">{GROUP_INTROS[group]}</p>\n'
        kura = by_slug(slug)
        b = BRANDS[slug][idx]
        btn = ""
        _rk = resolve_rakuten(slug, idx, b["name"]) if RAKUTEN_ENABLED else None
        _az = resolve_amazon(slug, idx, b["name"]) if AMAZON_ENABLED else None
        if _rk:
            btn += f'<a class="pick__btn" href="{_rk}" target="_blank" rel="noopener sponsored">楽天市場で探す →</a>'
        if _az:
            btn += f'<a class="pick__btn pick__btn--amazon" href="{_az}" target="_blank" rel="noopener sponsored">Amazonで探す →</a>'
        if btn:
            btn += '<span class="pick__pr">PR</span>'
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

    # 「好きなお酒から逆算する」選び方の早見表
    choose_grid = term_grid([
        ("ビール・クラフトビールが好き", "HOP", "ホップサケから。柑橘や白い花のような華やかな香りと、心地よいほろ苦さ。〈はなうたホップス／翔空 HOP SAKE ほっぺ〉"),
        ("ワイン・ナチュールが好き", "FRUIT", "果実サケや、酸の効いた一本へ。甘酸っぱく華やかで、食前にも。〈あまおうのおさけ／翔空 酔いどれ洋梨／KOYOI〉"),
        ("日本酒の旨みが好き", "DOBUROKU", "米だけで醸す古典どぶろく・純米へ。とろりと濃い旨みと、製法ごとの酸。〈ハッピーどぶろく／とおの どぶろく〉"),
        ("お酒が強くない・初めて", "LIGHT", "度数が穏やかで、微発泡のにごりから。口当たりがやさしい。〈ハナグモリ〉。低アルコールの銘柄も多い。"),
        ("贈り物・特別な日に", "GIFT", "受賞銘柄や、木桶・長期発酵の上級銘柄を。物語のある一本は記憶に残る。〈#ODAKA（ICC優勝）／権化〉"),
        ("とにかく自由に開拓したい", "EXPLORE", "saketto の4軸（副原料・蔵・地域・ジャンル）から横断検索。気になった入り口から辿るのがいちばん。"),
    ])

    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "EDITORS' PICKS / 選び方の地図")}
      <div class="prose">
        <p class="lead">クラフトサケは、<span class="accent">自由</span>な酒。ホップ、果実、ハーブ、米だけの濃いどぶろく——幅が広いぶん、最初の一本に迷う。そこで saketto 編集部が、収録する25の蔵・140を超える銘柄から、<span class="accent">タイプ別に12本</span>を選びました。</p>
        <p>「日本酒は知っているけれど、クラフトサケは初めて」という人も、「もう何本か飲んだから、次の一本を」という人も。下のグループを入り口に、自分に合いそうな一本を見つけてください。各銘柄のスペックは、saketto が一次ソース（各蔵の公式情報）で確認したものです。</p>
        <div class="callout">
          <div class="callout__label">この12選について</div>
          <p>このリストは、収録銘柄の中から「タイプの代表性・はじめての入りやすさ・話題性・入手のしやすさ」を目安に編集部が選んだものです。<strong>番号は人気や売上の順位ではなく</strong>、タイプ別に読みやすく並べた見取り図です。価格・度数などは2026年8月時点の確認値で、ロットや時期によって変わります。最新の価格・在庫は各リンク先でご確認ください。</p>
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
        <h2 class="sub-h">迷ったら、<span class="accent">好きなお酒</span>から逆算する。</h2>
        <p>クラフトサケ選びに正解はありません。でも、迷ったときの目安はあります。いちばん簡単なのは、<strong>ふだん好きなお酒</strong>から逆算すること。下の早見表を入り口に、自分に近いタイプから試してみてください。</p>
      </div>
      {choose_grid}
      <div class="prose">
        <p>もうひとつ知っておきたいのが、クラフトサケは<strong>少量生産・限定流通</strong>のものが多いということ。同じ銘柄でも<strong>仕込み（ロット）ごとに度数や味わいが少しずつ変わる</strong>のも、この酒ならではの面白さです。だからこそ「定番の一本」を決めるより、<strong>巡り合った一本を、その時々で楽しむ</strong>のがいちばん。気になる銘柄は、見かけたときが買いどきです。</p>
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
{section_meta("05", "FIRST BOTTLE / はじめの一本の選び方")}
      <div class="prose">
        <h2 class="sub-h">最初の一本は、<span class="accent">失敗しない</span>ように。</h2>
        <p>12本を眺めても決めきれない——そんなときのために、もう少し実際的な指針を置いておきます。<strong>はじめの一本は「冒険しない」のがコツ</strong>です。クラフトサケの幅広さは魅力ですが、いきなり尖った一本に当たると「自分には合わない酒」という印象で終わってしまいます。</p>
        <p>おすすめの入り方は<strong>ホップサケか、果実サケ</strong>。どちらも普段ビールやワイン、チューハイを飲む人にとって、味の想像がつきやすいカテゴリです。ホップサケなら柑橘やハーブを思わせる香り、果実サケなら素材そのものの甘みと酸——<strong>飲む前に味が予想できることが、最初の一本ではとても大事</strong>です。</p>
        <p>容量は<strong>500mlか、それ以下</strong>を選ぶと気楽です。四合瓶（720ml）は飲み切るのに数日かかるので、まずは小さいサイズで数種類を試すほうが、自分の好みの方向をつかみやすくなります。</p>
        <p>そしてもう一つ。<strong>火入れしてある（要冷蔵でない）銘柄</strong>から入ると、保管や配送で気を使う場面が減ります。生酒は確かにおいしいのですが、クール便の受け取りや開栓後の管理という手間がついてきます。慣れてから進むので十分です。</p>
        <div class="callout">
          <div class="callout__label">2本目からの広げ方</div>
          <p>1本目が気に入ったら、<strong>同じ蔵の別銘柄</strong>へ進むのがおすすめです。造り手の考え方が一貫しているので、好みに当たる確率が高くなります。逆に「違う方向を試したい」なら、<strong>同じ副原料で別の蔵</strong>へ。同じホップでも蔵によって解釈がまるで違うことに驚くはずです。</p>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("06", "BEYOND THE 12 / 12本の、その先へ")}
      <div class="prose">
        <h2 class="sub-h">選ばれなかった<span class="accent">130本あまり</span>のほうへ。</h2>
        <p>ここで挙げた12本は、あくまで入り口です。saketto が収録している銘柄は<strong>140を超えます</strong>。編集部が12本に絞った時点で、その大半は選から漏れているわけですが、それは「劣る」という意味ではまったくありません。<strong>入手しやすさや、はじめての人にとっての分かりやすさを優先した結果</strong>にすぎません。</p>
        <p>むしろ面白いのは、選ばれなかったほうにあります。年に一度しか仕込まれない酒、蔵の店舗でしか出さない酒、地震で被災した蔵と共同で醸した酒、地元の農家や農園と組んで生まれた酒——<strong>数字に表れない背景を持つ銘柄が、まだいくつも眠っています</strong>。</p>
        <p>そうした一本にたどり着くには、リストを追うより<strong>軸で掘る</strong>ほうが早い。ホップが好きだと分かったなら副原料の軸から、造りの物語に惹かれるならジャンルの軸から、旅の予定に合わせるなら地域の軸から。<strong>12本はあくまで地図の入り口で、その先の道はご自身で選んでほしい</strong>——それが saketto の考える楽しみ方です。</p>
        <div class="pill-links">
          <a href="../subingredients/">副原料から掘る<span class="arr">→</span></a>
          <a href="../genre/">ジャンルから掘る<span class="arr">→</span></a>
          <a href="../brewery/">25の蔵を見る<span class="arr">→</span></a>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("07", "AWARDED / 外から評価された一本")}
      <div class="prose">
        <h2 class="sub-h">好みの前に、<span class="accent">実績</span>で選ぶ。</h2>
        <p>「編集部が選んだ」と言われても、どこまで信用していいか分からない——そう感じる方には、<strong>第三者の評価という物差し</strong>があります。クラフトサケにも、審査を経て賞を受けた銘柄があります。</p>
        <p>代表的なのが<strong>ICC SAKE AWARD</strong>です。2023年の初代優勝は<a href="../brewery/ine-to-agave.html">稲とアガベ</a>の「稲とアガベ OGAラベル」。2024年には同蔵の「花風」が第3位に入りました。2025年の優勝は<a href="../brewery/pukupuku.html">ぷくぷく醸造</a>の木桶どぶろく「#ODAKA」、準優勝は京都の<a href="../brewery/linne.html">LINNÉ</a>「800 大麦 樽熟成」です。ぷくぷく醸造は2024年にも決勝へ進んでおり、<strong>連続して評価されている蔵</strong>と言えます。</p>
        <p>ほかにも、長崎の<a href="../brewery/dejima-hosendo.html">でじま芳扇堂</a>「芳扇 吟雲」が2025年のTokyo酒チャレンジで金賞を受賞。九州で初めて作付け・収穫された美山錦を100%使ったどぶろくです。<a href="../brewery/haccoba.html">haccoba</a>は2025年、日本パッケージデザイン大賞の銀賞（酒類カテゴリ）を「水を編む」シリーズで受賞しました。<strong>味だけでなく、瓶に立つ姿まで評価されている</strong>という点で、贈りものを探す方には見逃せない一本です。</p>
        <p>視点を海外に移すと、評価はさらに鮮明です。岩手・遠野の<a href="../brewery/nondo.html">nondo</a>は、世界ベストレストラン2024年1位に選ばれたバルセロナの「Disfrutar」と、スペインの旧3つ星「Mugaritz」で提供されました。<strong>世界最高峰の料理人が、日本のどぶろくを自分たちの皿に合わせている</strong>——これ以上の評価はそうありません。</p>
        <div class="callout">
          <div class="callout__label">賞との付き合い方</div>
          <p>受賞歴は選ぶときの手がかりになりますが、<strong>賞を取っていない銘柄が劣るわけではありません</strong>。少量生産で出品自体をしない蔵も多く、コンテストに出る・出ないは造り手の方針です。迷ったときの入り口として使うのが、いちばん健全な向き合い方だと思います。</p>
        </div>
        <div class="pill-links">
          <a href="../awards/">受賞から探す<span class="arr">→</span></a>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("08", "BY SCENE / 場面で使い分ける")}
      <div class="prose">
        <h2 class="sub-h">誰と飲むかで、<span class="accent">正解は変わる</span>。</h2>
        <p>同じ12本でも、飲む場面によって向き不向きがあります。味の好みとは別の軸で、実際に選ぶときの目安をまとめておきます。</p>
        <p><strong>ひとりで、じっくり</strong>味わうなら、濃度の高いタイプが向きます。<a href="zenkoji.html">全麹酒</a>や熟成させた銘柄は、少量をゆっくり飲むほど表情が変わっていきます。500ml以下の小さめの瓶を選べば、数日かけて変化を追えます。</p>
        <p><strong>誰かと分けあう</strong>なら、四合瓶（720ml）でホップサケや果実サケを。香りが華やかな銘柄は、開けた瞬間に場の空気が変わります。飲み慣れていない人がいるときは、度数が低めのものやソーダで割れるタイプを選ぶと、全員が楽しめます。</p>
        <p><strong>食事に合わせる</strong>なら、酸のしっかりしたタイプが便利です。白麹由来の酸は料理の脂を切ってくれるので、和食に限らず洋食や中華にも寄り添います。逆に甘みの強い銘柄は、食中よりも食前・食後に単体で楽しむほうが持ち味が出ます。</p>
        <p><strong>贈りものにする</strong>なら、味の良さと同じくらい「話せる背景があるか」が効きます。被災した蔵との共同醸造、地元の農家と組んだ副原料、途絶えかけた製法の復活——<strong>一本の後ろにある物語は、そのまま贈る言葉になります</strong>。選び方は<a href="gift.html">ギフトガイド</a>で詳しく扱っています。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("09", "KEEP / 届いてからのこと")}
      <div class="prose">
        <h2 class="sub-h">買ったあとが、<span class="accent">半分</span>。</h2>
        <p>せっかく選んだ一本も、扱いを誤ると本来の味に届きません。とくにクラフトサケは生タイプが多く、<strong>届いてからの数時間で印象が変わる</strong>ことがあります。</p>
        <p>まず<strong>受け取ったらすぐ冷蔵庫へ</strong>。クール便で届いた瓶を、玄関に置いたまま数時間——これがいちばんもったいない扱いです。立てて、光を避けて保管します（詳しい保管方法は<a href="nomikata.html">飲み方・楽しみ方</a>に）。</p>
        <p>そして<strong>飲む直前に、瓶をゆっくり回してください</strong>。にごりタイプは澱が底に沈んでいるので、静かに転がすように混ぜると全体が均一になります。激しく振ると、活性タイプでは吹き出しの原因になるので禁物です。温度帯や器の選び方は<a href="nomikata.html">飲み方・楽しみ方</a>で詳しく扱っています。</p>
        <p>飲み比べをするなら、<strong>順番にもコツ</strong>があります。基本は<strong>軽いものから重いものへ</strong>。度数の低いもの、酸のきれいなものから始めて、甘みや旨みの濃いものへ進むと、それぞれの個性が分かりやすくなります。逆に濃厚な一本から入ると、そのあとの繊細な酒がぼやけて感じられてしまいます。</p>
        <p>グラスは、できれば<strong>銘柄ごとに替える</strong>のが理想です。難しければ、間に水を挟んで軽くすすぐだけでも違います。そして<strong>和らぎ水</strong>——酒と同量くらいの水を交互に飲むことは、体への負担を減らすだけでなく、舌をリセットして次の一杯を正しく味わうためにも効きます。</p>
        <p>もうひとつ、<strong>メモを取ること</strong>をおすすめします。銘柄名と、ひと言の感想だけで十分です。「甘い」「酸っぱい」でもいい。数本ためると、自分がどの方向を好むのかが見えてきます。<strong>好みが言語化できると、次の一本を選ぶのが格段に楽になります</strong>。saketto の各銘柄ページには副原料や造りの情報をまとめてあるので、感想と照らし合わせてみてください。</p>
        <p>そして、<strong>合わなかった一本も記録しておく</strong>価値があります。「自分には甘すぎた」「酸が強すぎた」——それは失敗ではなく、好みの輪郭が一本ぶんはっきりしたということです。クラフトサケは幅が広いぶん、全部が好みに合うほうがおかしいくらいです。<strong>合わないものを知ることは、合うものを探す作業の半分</strong>を占めています。</p>
        <p>もし一本目でうまく出会えなくても、それだけで見切らないでください。同じ「クラフトサケ」の三文字でも、蔵が変われば別の飲みものと言っていいほど違います。<strong>方向を変えてもう一本</strong>——ホップが強すぎたなら果実へ、甘すぎたならすっきりした古典どぶろくへ。棚の広さは、そのまま可能性の広さです。</p>
        <p>そして忘れがちなのが、<strong>体調と場所</strong>の影響です。同じ酒でも、疲れているとき、暑い部屋、急いで飲んだとき——条件が違えば印象は変わります。「あのとき苦手だった一本」が、季節を変えて飲んだら好きになった、ということは珍しくありません。<strong>一度の評価を固定しない</strong>ほうが、この酒とは長く付き合えます。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("10", "FAQ / よくある質問")}
      <div class="prose">
        <h2 class="sub-h tight">クラフトサケは、どこで買えますか。</h2>
        <p>多くは各蔵の公式オンラインショップや取扱酒販店、楽天市場などのECで手に入ります。少量生産・限定流通の銘柄も多く、季節や入荷のタイミングで在庫は変わります。気になる一本は、見かけたときが買いどきです。チャネルごとの違いは<a href="doko-de-kaeru.html">どこで買える？</a>で詳しく扱っています。</p>
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
                     "クラフトサケのおすすめを、saketto編集部がタイプ別に12本厳選。稲とアガベ・haccoba・LAGOON・ぷくぷく醸造など、収録DBの確認済みスペック（度数・容量・参考価格）とともに、はじめての一本から通好みの受賞銘柄までを紹介します。",
                     "/guide/osusume.html", "article")
    html += masthead(article_masthead_label("osusume"), "A Field Guide")
    html += hero(
        article_eyebrow("osusume"),
        'クラフトサケ、<br><span class="accent">最初の12本</span>。',
        "ホップ、果実、米だけの濃いどぶろく——自由な酒だから、入り口も自由。編集部がタイプ別に選んだ12本を、確認済みのスペックとともに。")
    html += body
    html += footer()
    return html


# ────────────── 記事④：木桶仕込みとは（DEEP） ──────────────

def build_kioke():
    # 木桶 と 金属タンクの比較
    compare_grid = term_grid([
        ("木桶", "KIOKE", "呼吸する木。蔵付きの微生物が棲みつき、桶ごとに表情が変わる。まろやかさ・複雑さ・やわらかな酸といった“ゆらぎ”の方向へ。一方で手間がかかり、欠減も多い。"),
        ("ステンレス・ホーロー", "METAL TANK", "洗いやすく衛生を保ちやすい。温度を狙いどおりに管理でき、欠減も少ない。クリアでまっすぐ、再現性の高い味わいに向く。近代の酒造りを支えてきた器。"),
    ])

    # 木桶にまつわることば
    kioke_terms = term_grid([
        ("木桶 / 大桶", "KIOKE", "杉などの木材を、竹や金属の「箍（たが）」で締めて作る発酵容器。酒蔵で使う大型のものは「大桶」とも。数十年から、手入れ次第で100年以上使われることもある。"),
        ("箍（たが）", "TAGA", "桶の側板（がわいた）を外周から締め、固定する輪。かつては真竹が使われた。緩むと桶がばらける——「たがが外れる」の語源でもある。"),
        ("蔵付き酵母・乳酸菌", "HOUSE MICROBES", "蔵や木桶に棲みつき、その蔵だけの発酵をもたらす微生物たち。木桶の細かな隙間は、彼らの棲み家になりやすいとされる。"),
        ("欠減（けつげん）", "LOSS", "醸造中に蒸発や漏れで中身が減ること。木桶はホーロー・ステンレスより欠減が大きく、これも近代化で敬遠された一因。"),
    ])

    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "WHAT IS / 木桶仕込みとは")}
      <div class="prose">
        <p class="lead">木桶仕込みとは、ステンレスやホーローのタンクではなく、<span class="accent">木の桶</span>で酒を発酵させること。いま、クラフトサケの造り手たちが、あえてこの“古くて新しい”容器へ回帰している。</p>
        <p>木桶は、杉などの板を「箍（たが）」で締めてつくる発酵の器。かつては日本中の酒蔵・醤油蔵・味噌蔵で当たり前に使われていた。だが20世紀のあいだに、その姿はほとんど消えてしまう。</p>
        <p>そして今、消えたはずの木桶が静かに戻ってきている。しかもそれは、単なる懐古趣味ではない。<strong>効率を最優先にしてきた酒造りへの、ひとつの問い直し</strong>——「速さや均一さの代わりに、私たちは何を手放してきたのか」。木桶という一つの器をめぐる物語は、クラフトサケが大切にする思想そのものを映している。なぜ消え、なぜ今、選び直されているのか。順に見ていこう。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("02", "HISTORY / なぜ木桶は消えたか")}
      <div class="prose">
        <h2 class="sub-h">江戸の主役は、<span class="accent">百年</span>で姿を消した。</h2>
        <p>木の仕込み桶は、江戸時代を通じて酒造りの主役だった。桶を組み上げる「結桶（ゆいおけ）」の技は全国の桶屋が担い、酒だけでなく醤油・味噌・漬物まで——日本の発酵文化は、まるごと木桶の上に成り立っていたと言っていい。大きな酒どころでは、何十本もの大桶が立ち並ぶ蔵の風景が当たり前だった。</p>
        <p>ところが近代になると、木桶は「隙間に雑菌が棲むかもしれない、不衛生だ」と見なされるようになる。大正期に登場したのが、鉄の表面にガラス質を焼き付けた<strong>ホーロー（琺瑯）タンク</strong>。やがてステンレスタンクも広まった。</p>
        <p>これらの金属タンクは、洗って清潔を保ちやすく、発酵中の温度を冷やしやすく、そして<strong>欠減（けつげん＝蒸発や漏れによる目減り）が少ない</strong>。仕込みの数値を狙いどおりに、安定して再現できる。管理のしやすさは圧倒的で、行政もその普及を後押しした。こうして木の大桶は急速に置き換わり、<strong>1960年頃までに、酒蔵の現場からほとんど姿を消した</strong>とされる。大量に、安定して、安く——効率を求める時代に、手のかかる木桶は割に合わなくなったのだ。</p>
        <p>木桶が使われなくなれば、桶を結う仕事も消えていく。やがて、<strong>大桶を新しくつくれる職人・製桶所は、全国でごくわずか</strong>にまで減ってしまった。器だけでなく、それを生み出す技術そのものが、静かに失われようとしていた。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("03", "HOW MADE / 木桶のつくり")}
      <div class="prose">
        <h2 class="sub-h">釘を使わず、<span class="accent">竹</span>で締める。</h2>
        <p>木桶は、驚くほど“原始的”で、同時に精巧な器だ。主な材料は<strong>杉</strong>。木の赤身（中心に近い部分）と白身（外側）の境目が一枚の板に入るように製材し、わずかに角度をつけて削る。それを並べて組むと、ぴたりと円形になる。<strong>接着剤も鉄の釘も使わず、側板（がわいた）どうしは竹の釘でつなぎ、外周を竹の「箍（たが）」で締め上げる</strong>。金属を使わないのは、錆びが酒や微生物に触れないためでもある。</p>
        <p>大きさもさまざまだ。酒の仕込みに使う木桶は<strong>3,000リットル前後</strong>のものが多く、総米1トン程度かそれ以下の「小仕込み」に向く。大型になると<strong>6,500リットル</strong>級のものもあり、醤油では「20石桶（約3,600リットル）」と呼ばれる大桶も使われてきた。一本の桶に、一度の仕込みの命運が託される。</p>
        <p>木は生きものだから、同じ寸法に削っても一本一本くせがある。それを水の力で膨らませ、たがの締め方で漏れないように仕上げていく——これはまさに職人の手わざ。だからこそ、つくれる人が減ることは、味の選択肢そのものが減ることを意味していた。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("04", "WHY / 木桶が宿す力")}
      <div class="prose">
        <h2 class="sub-h">木桶は、<span class="accent">呼吸</span>する。</h2>
        <p>では、なぜ造り手は木桶に戻るのか。鍵は、木という素材そのものにある。木桶は金属タンクと違って、<strong>わずかに「呼吸する」</strong>といわれる。天然の木材がもつ細かな隙間や繊維が空気をゆるやかに通し、発酵に繊細な揺らぎをもたらす——そう考えられている。</p>
        <p>そしてその隙間は、<strong>微生物の棲み家</strong>になる。長年使い込まれた木桶には、酵母や乳酸菌といった<strong>「蔵付き」の微生物</strong>が棲みつき、その蔵・その桶でしか出せない発酵を生む。無機質なステンレスでは再現しにくい、桶ごとの“個性”がそこに宿るとされる。同じレシピでも、桶が変われば酒の表情が変わる——木桶仕込みの面白さは、この<strong>不均一さ・予測しきれなさ</strong>にある。</p>
        <p>では、味わいはどう変わるのか。木桶で醸した酒は、しばしば<strong>角の取れたまろやかさ</strong>や、いくつもの香りが折り重なる<strong>複雑さ</strong>、そして蔵付き乳酸菌に由来するともいわれる<strong>やわらかな酸</strong>をまとう、と語られる。ステンレスのクリアでまっすぐな味わいに対して、木桶は“ゆらぎ”や“ふくらみ”の方向——そんなふうにイメージすると分かりやすい。もちろん、レシピや蔵の設計しだいで表情は大きく変わるので、あくまで傾向の話だ。</p>
        <h2 class="sub-h tight">木桶と金属タンク、<span class="accent">何が違う</span>。</h2>
        <p>どちらが上、という話ではない。狙う味と造りの思想によって、選ばれる器が違うだけだ。それぞれの“得意”を並べてみる。</p>
      </div>
      {compare_grid}
      <div class="prose">
        <div class="callout">
          <div class="callout__label">編集部より</div>
          <p>木桶の発酵が「呼吸」「蔵付き微生物」によるとする説明は、造り手や専門メディアで広く語られる見方です。科学的な機序には諸説あり、ここでは一般的な考え方として紹介しています。味わいの感じ方には個人差があります。</p>
        </div>
      </div>
      {kioke_terms}
    </section>
{divider()}
    <section class="section">
{section_meta("05", "REVIVAL / 木桶を、未来へ")}
      <div class="prose">
        <h2 class="sub-h">桶を“つくれる人”を、<span class="accent">つくる</span>。</h2>
        <p>消えかけた木桶文化に、ひとりの作り手が抗った。香川・小豆島の醤油蔵<strong>ヤマロク醤油</strong>の五代目・山本康夫さんだ。2011年から2012年にかけて、同級生の大工たちとともに<strong>「木桶職人復活プロジェクト」</strong>を立ち上げ、数少ない桶屋に弟子入りする。約2年の試行錯誤の末、<strong>2013年、奈良の吉野杉と真竹の箍で新しい大桶を完成</strong>させた。</p>
        <p>このプロジェクトの面白さは、技術を一人占めしないところにある。<strong>毎年1月、小豆島には全国から木桶仕込みのメーカー・飲食店・流通関係者が集まり、みんなで新桶を組み上げる</strong>。学んだ人がまた各地で桶をつくれるように——「つくれる人」ごと増やしていく発想だ。その輪は醤油から、酒・味噌など発酵食品の作り手へと広がった。2025年には「木桶による発酵文化サミット」も開かれ、木桶を軸にした作り手たちのつながりは、年々太くなっている。</p>
        <p>効率を捨ててでも残したいものがある——その静かな意志が、消えかけた技術を未来へつないでいる。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("06", "SUSTAINABILITY / 百年の器")}
      <div class="prose">
        <h2 class="sub-h">手入れすれば、<span class="accent">百年</span>使える。</h2>
        <p>木桶は、一度つくれば長く生きる器でもある。箍を締め直し、手入れをしながら使えば、<strong>数十年、ときに100年以上</strong>現役で働く。しかも、その一生は一つの蔵だけで終わらない。<strong>酒蔵で役目を終えた大桶が、醤油蔵や味噌蔵へ“second life”として引き継がれる</strong>——そんなリレーが、いまも各地で続いている。木という再生可能な素材を、世代をまたいで、用途をまたいで使い切る。</p>
        <p>大量生産・使い捨てとは正反対のこの在り方は、いまの<strong>サステナビリティ</strong>の感覚とも自然に響き合う。手間がかかり、欠減もある。効率だけを見れば不利な器を、それでも選ぶ。そこには「<strong>その土地の、その蔵の、その桶でしか出せない味</strong>」を信じる造り手の覚悟がある。クラフトサケが木桶へ向かうのは、自由な発想で“らしさ”を突き詰める、この酒の精神そのものだ。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("07", "MATERIAL / 木という素材")}
      <div class="prose">
        <h2 class="sub-h">なぜ、<span class="accent">杉</span>なのか。</h2>
        <p>酒や醤油の木桶に使われてきたのは、主に<strong>杉</strong>だ。数ある木のなかから杉が選ばれてきたのには、いくつもの理由が重なっている。</p>
        <p>まず<strong>手に入りやすさ</strong>。杉は日本の山にもっとも多く植えられてきた木で、まっすぐ育ち、大きな板が取れる。次に<strong>加工のしやすさ</strong>。柔らかく、割れにくく、曲げの加工にも耐える。そして<strong>香り</strong>。杉に含まれる成分が、酒にかすかな清涼感を与える。新しい桶ほど木香が強く出るため、蔵によっては最初の数年を「桶を慣らす期間」と考える。</p>
        <p>木桶を締めているのは、竹を編んだ<strong>箍（たが）</strong>だ。金属の輪ではなく竹を使うのは、木の呼吸に合わせてわずかに伸縮するから。<strong>木も竹も、生きていたころの性質を残したまま器になっている</strong>。「たがが外れる」という言い回しは、この箍が緩んで桶がばらけることから来ている。</p>
        <p>そしてこの器は、時間とともに変わっていく。使い込むほど木の内部に微生物が棲みつき、<strong>その蔵にしかいない菌の集まり</strong>が育つ。ステンレスやホーローが「洗って元に戻せる」器だとすれば、木桶は<strong>元に戻らないことに価値がある</strong>器だ。同じ設計図で作った桶が、置かれた蔵によって別々の性格を持つようになる。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("08", "BEYOND SAKE / 醤油と味噌の木桶")}
      <div class="prose">
        <h2 class="sub-h">日本の味は、<span class="accent">桶の中</span>で育った。</h2>
        <p>木桶を使ってきたのは、酒だけではない。<strong>醤油、味噌、酢、漬物</strong>——日本の発酵食品の多くが、木桶とともに育ってきた。むしろ量としては、醤油の桶のほうがずっと多かった時代もある。</p>
        <p>そして木桶の危機も、業界を越えて共通していた。効率を求めてタンクへの置き換えが進み、桶を作る職人が減り、新しい桶が手に入らなくなる。<strong>桶がなくなれば、桶の味も消える</strong>——この危機感から、醤油の造り手たちのあいだで木桶を自分たちで作ろうという動きが起こった。職人のもとへ学びに行き、道具を揃え、桶を組む。その活動が、いま酒の世界にも波及している。</p>
        <p>おもしろいのは、<strong>発酵食品どうしで桶が行き来する</strong>ことだ。役目を終えた醤油の桶が酒蔵に渡り、酒を仕込む器として第二の人生を送る。逆に酒の桶が味噌に使われることもある。<strong>桶に棲みついた微生物ごと、別の発酵へ引き継がれていく</strong>——百年使える器だからこそ成立する循環だ。</p>
        <p>クラフトサケの造り手が木桶を選ぶとき、彼らは酒の歴史だけでなく、この<strong>発酵文化そのものの流れ</strong>に足を踏み入れている。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("09", "IN CRAFT SAKE / 木桶を選んだ蔵")}
      <div class="prose">
        <h2 class="sub-h">saketto で出会える、<span class="accent">木桶の酒</span>。</h2>
        <p>木桶への回帰は、クラフトサケだけの話ではない。寺田本家・今代司・人気酒造といった<strong>伝統的な日本酒蔵でも、あえて木桶仕込みに取り組む例が増えている</strong>。「木桶でしか出せない味がある」「自然の力を生かしたい」——ナチュラル志向の高まりも追い風に、古い器がいま静かに見直されているのだ。</p>
        <p>そして、自由を信条とするクラフトサケの造り手たちは、その先頭を走るひとり。saketto の収録銘柄で発酵容器を確認できたもののうち、<strong>木桶を使っているのは13銘柄・4蔵</strong>。数としては多くないが、その中身は蔵ごとにまるで違う。</p>
        <p><a href="../brewery/nondo.html">nondo（岩手・遠野）</a>は、上級シリーズ「権化」5銘柄すべてを木桶で醸す。<strong>水もと × 木桶 × 長期発酵</strong>という組み合わせで、なかでも「権化 Rafters」は<strong>200年前の古民家の男柱とはね木、江戸期の槽を再生</strong>して搾るという徹底ぶりだ。<a href="../brewery/pukupuku.html">ぷくぷく醸造（福島・小高）</a>は<strong>福島県産の杉と竹で組んだ木桶</strong>を使い、蔵付き酵母の「#ODAKA」で<strong>ICC SAKE AWARD 2025の頂点</strong>に立った。木桶仕込みの全麹酒も手がけている。</p>
        <p><a href="../brewery/yamane.html">やまね酒造（埼玉・飯能）</a>は、地元・西川材でつくった道具と木桶で醸す。<strong>器そのものに土地を宿す</strong>試みだ。そして福岡の<a href="../brewery/cultiva.html">Cultiva糸島醸造所</a>は、「米のテロワール」を掲げ<strong>収録3銘柄すべてを生酛×木桶</strong>で仕込む。長野産三系錦、福岡産ヒノヒカリ、福岡産山田錦——米の産地と品種を前面に出し、器と製法を固定して<strong>米の違いだけを浮かび上がらせる</strong>設計になっている。</p>
        <p>興味深いのは、この13銘柄のほとんどが<strong>酒母も古典に戻っている</strong>ことだ。水もと、生酛——木桶を選ぶ蔵は、酵母や乳酸を足さずに微生物に委ねる造りへ向かう傾向がある。<strong>器の選択と製法の選択は、切り離せない</strong>のかもしれない。</p>
        <div class="pill-links">
          <a href="../genre/">ジャンル「木桶仕込み」から探す<span class="arr">→</span></a>
          <a href="../subingredients/">副原料から<span class="arr">→</span></a>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("10", "HOW TO TASTE / 木桶の酒を味わう")}
      <div class="prose">
        <h2 class="sub-h">桶の仕事を、<span class="accent">舌で探す</span>。</h2>
        <p>木桶で仕込んだ酒を手に入れたら、どこを味わえばいいのか。ステンレス仕込みとの違いは、慣れないうちは分かりにくいかもしれない。目のつけどころをいくつか挙げておく。</p>
        <p>ひとつは<strong>味の層</strong>だ。木桶の酒は、ひと口目からすべてが出てくるというより、<strong>飲み進めるほど後ろから別の要素が立ち上がってくる</strong>ことが多い。桶に棲む多様な微生物が関わったぶん、単一の酵母では出ない複雑さが生まれる。ひと口で判断せず、二口目、三口目と追ってほしい。</p>
        <p>ふたつめは<strong>温度による変化</strong>。冷やした状態では硬く感じた酒が、常温に近づくにつれてほどけていく——木桶の酒にはこの振れ幅が大きいものがある。冷蔵庫から出してすぐと、30分置いてからで、別の酒のように感じられることも珍しくない。<strong>意図的に温度を動かしながら飲む</strong>と、その日いちばんおいしい温度帯が見つかる。</p>
        <p>みっつめは<strong>木の香り</strong>。新しい桶で仕込んだ酒には、杉のかすかな清涼感が乗ることがある。これを個性と取るか雑味と取るかは好みだが、<strong>器の記憶がそのまま酒に移っている</strong>と思えば、味わい方が変わってくる。器の選び方や温度帯の詳細は<a href="nomikata.html">飲み方・楽しみ方</a>にまとめている。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("11", "CARE / 桶を守る仕事")}
      <div class="prose">
        <h2 class="sub-h">使うことが、<span class="accent">手入れ</span>になる。</h2>
        <p>木桶は、置いておくだけでは保たない。<strong>使い続けることそのものが手入れ</strong>だという点で、金属のタンクとは性格がまるで違う。</p>
        <p>まず<strong>乾燥は大敵</strong>だ。長く使わずに放置すると木が縮み、板と板のあいだに隙間ができて水が漏れる。だから使わない時期にも水を張って湿らせておく。<strong>桶は、酒を仕込んでいないときにも世話を必要とする</strong>。</p>
        <p>洗浄も難しい。木は表面に細かな凹凸があり、内部に微生物が棲みついている。<strong>強い薬剤で完全に殺菌してしまえば、木桶の意味がなくなる</strong>。かといって汚れを残せば、望まない菌が優勢になり酒が傷む。求められるのは、消毒ではなく<strong>菌の集まりを望ましい状態に保つこと</strong>——効率化とは正反対の、経験と観察に頼る仕事だ。</p>
        <p>そして箍（たが）の締め直しがある。竹の箍は年月とともに緩み、傷む。定期的に締め直し、必要なら組み替える。この作業ができる職人が減ったことが、木桶の危機の一因でもあった。</p>
        <p><strong>百年使える器とは、百年手入れし続けられる器のこと</strong>だ。木桶を選ぶということは、その手間を引き受けるという意思表示にほかならない。</p>
        <p>そしてこの手間は、一世代では完結しない。桶を仕込んだ人がその桶の最後を看取るとは限らず、次の代へ引き継がれていく。<strong>自分が使い終えたあとも誰かが使い続ける前提で、器を育てる</strong>——木桶を巡る仕事には、そういう時間感覚が織り込まれている。</p>
        <p>効率を基準にすれば、この選択は合理的ではない。洗いやすく、温度も管理しやすく、壊れれば買い替えられるタンクのほうが、経営としては正しい。それでも木桶を選ぶ蔵があるのは、<strong>この器でしか出せない味がある</strong>という一点による。手間の総量ではなく、その先にある一杯で判断している。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("12", "VESSELS / 桶だけではない、器の話")}
      <div class="prose">
        <h2 class="sub-h">7リットルの<span class="accent">鍋</span>から、木桶まで。</h2>
        <p>木桶を語ってきたが、視野を広げると、クラフトサケの発酵容器はきわめて多様だ。saketto の収録銘柄で発酵容器が公開されているのは<strong>29銘柄</strong>。木桶、試し桶、タンク、オーク樽、そして数リットルの小型容器——<strong>大きく5つの系統</strong>に分かれる。</p>
        <p>最多はもちろん<strong>木桶</strong>だが、そのすぐ隣に驚く記述が並ぶ。<strong>「7〜8リットルの小型容器（店頭仕込み）」「小型タンク（8L）」「7L容器（カレー鍋大）」</strong>——数リットル規模で仕込まれている銘柄が、実際に存在する。</p>
        <p>これは駅ナカや商店街に立つ<a href="new-breweries.html">新しい蔵</a>の造りだ。大きなタンクを置く場所がないから、小さな容器で少量ずつ仕込む。<strong>一回の仕込みが数十本にしかならない</strong>かわりに、毎回レシピを変えられる。木桶が「時間をかけて器を育てる」方向の極致だとすれば、こちらは<strong>「回数を重ねて試す」方向の極致</strong>である。</p>
        <p>おもしろいのは、この両極が同じジャンルの中に共存していることだ。百年使う器と、カレー鍋ほどの容器。<strong>どちらもクラフトサケであり、どちらも「その器でしか出せない酒」を目指している</strong>。器の選択そのものが、造り手の思想を映す鏡になっている。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("13", "FAQ / よくある質問")}
      <div class="prose">
        <h2 class="sub-h tight">木桶仕込みのお酒は、やっぱり<span class="accent">高い</span>の？</h2>
        <p>手間と希少性から、比較的高価になりやすい傾向はあります。長期発酵や少量生産が重なると、一本で数千円、上級銘柄では一万円を超えるものも。ただ、すべてが高価というわけではなく、手の届く一本もあります。価格には、職人がつくった器と、時間と、人の手わざが含まれている——そう考えると、見え方が変わるかもしれません。</p>
        <h2 class="sub-h tight">“木桶仕込み”って、どう<span class="accent">見分ける</span>の？</h2>
        <p>多くの場合、ラベルや蔵の商品説明に「木桶仕込み」「木桶発酵」と明記されています。saketto では<a href="../genre/">ジャンル「木桶仕込み」</a>から、収録銘柄を横断的に辿れます。</p>
        <h2 class="sub-h tight">木桶のお酒は、どう<span class="accent">楽しむ</span>といい？</h2>
        <p>まずはよく冷やして、できれば香りの立つグラスで。桶由来のまろやかさや、折り重なる複雑な香りを味わってみてください。温度を少しずつ上げて表情の変化を探るのもおすすめです。詳しいコツは<a href="nomikata.html">飲み方・楽しみ方</a>でまとめています。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("14", "READ ON / もっと味わう")}
      <div class="prose">
        <p>木桶は、クラフトサケの造りを彩る技法のひとつ。花酛・水もと・生酛・全麹といったほかの製法のことばは、入門記事でまとめて紹介している。製法を知れば、ひと口の背景がぐっと立体的になる。</p>
        <div class="callout">
          <div class="callout__label">楽しむ前に</div>
          <p><strong>20歳未満の飲酒は法律で禁じられています。</strong>　飲酒運転は法律で禁止されています。妊娠中・授乳期の飲酒はお控えください。適量を守り、自分のペースでお楽しみください。</p>
        </div>
        <div class="readmore">
          <a href="craftsake-towa.html">
            <div class="readmore__k">あわせて読む</div>
            <div class="readmore__t">クラフトサケとは（製法のことば）</div>
          </a>
          <a href="osusume.html">
            <div class="readmore__k">CHOOSE</div>
            <div class="readmore__t">おすすめ12選から探す</div>
          </a>
        </div>
      </div>
    </section>

  </div>
"""
    html = page_head("木桶仕込みとは — 木の桶が醸す、時間と微生物の酒",
                     "木桶仕込みとは何か。江戸期に主流だった木桶がホーロー・ステンレスタンクに置き換わった歴史、木桶に棲む蔵付き微生物の働き、木桶職人復活プロジェクト、そしてクラフトサケが木桶へ回帰する理由を、一次情報をもとに深掘りします。",
                     "/guide/kioke.html", "article")
    html += masthead(article_masthead_label("kioke"), "A Field Guide")
    html += hero(
        article_eyebrow("kioke"),
        '木桶仕込みとは。<br>木が醸す、<span class="accent">時間の酒</span>。',
        "効率を求めて消えた木の桶に、クラフトサケはなぜ戻るのか。歴史・微生物・職人の技から、木桶仕込みの奥行きをひもときます。")
    html += body
    html += footer()
    return html


# ────────────── 記事⑤：ギフトに贈るクラフトサケ（CHOOSE） ──────────────

GIFT_SCENE_INTROS = {
    "手土産・ちょっとしたお礼に":
        "気負わず渡せて、それでいて「お、いいね」と思わせる。2,000〜2,500円ほどの、ちょっとした手土産やお礼にちょうどいい一群。話題性や見た目の華やかさで選ぶと喜ばれる。",
    "誕生日・記念日に":
        "大切な人の特別な日に。香りや見た目が華やかで、食卓を彩る一本を。お酒が得意でない相手にも、果実やお茶の香りの一本なら喜ばれやすい。",
    "お祝い・改まった贈り物に":
        "昇進・結婚・長寿のお祝いなど、改まった贈り物に。受賞歴や手間のかかる造り、特別仕込みなど“物語”のある一本は記憶に残る。熨斗や化粧箱の対応は各蔵に確認を。",
    "自分へのご褒美に":
        "誰かにではなく、自分に。頑張った日の夜、特別な一本をゆっくりと。受賞銘柄や最高峰の仕込みで、クラフトサケの奥深さを心ゆくまで味わいたい。",
}

# シーン別ギフトセレクト。スペックは BRANDS から直接引く。コメントの事実部分は
# breweries_master / breweries_brands / awards の確認済データに基づく（味/贈答の所感は編集部）。
GIFT_PICKS = [
    ("手土産・ちょっとしたお礼に", "CASUAL", "konohanano", 0,
     "微発泡のにごりは、開けた瞬間の華やぎで場を和ませる。浅草・木花之醸造所の看板で、2,000円を切る手頃さも気軽な手土産にぴったり。日本酒好きにも、にごり初心者にも喜ばれる、外さない一本。"),
    ("手土産・ちょっとしたお礼に", "CASUAL", "haccoba", 0,
     "「クラフトサケって何？」から会話が弾む、話題性のある一本。ジャンルを切り拓いたhaccobaの看板で、ホップの華やかな香りは贈った相手の記憶に残る。物語ごと渡せるのが、ギフトとして嬉しい。"),
    ("手土産・ちょっとしたお礼に", "CASUAL", "lagoon", 4,
     "新潟産いちご「越後姫」をたっぷり使った、見た目も味も華やかな果実サケ。LAGOONの季節仕込みで、フルーツ好きへの手土産や、お酒が得意でない人へのプレゼントにも向く。"),
    ("誕生日・記念日に", "BIRTHDAY", "ine-to-agave", 0,
     "迷ったらこれ、という安心感。クラフトサケの代名詞で、白ブドウや白桃を思わせる上品な香りは誕生日の食卓に映える。「いま話題のクラフトサケ」を贈りたいときの、王道の一本。"),
    ("誕生日・記念日に", "BIRTHDAY", "librom", 3,
     "福岡の高級いちご「あまおう」の甘酸っぱさが華やかに香る、記念日にふさわしい一本。ワインのように楽しめるので、お祝いの乾杯にも。LIBROMの遊び心が、贈り物に彩りを添える。"),
    ("誕生日・記念日に", "BIRTHDAY", "ine-to-agave", 3,
     "麹の糖と白麹の酸に、青森・奥入瀬のトチの蜂蜜を融合させた実験的な一本。蜂蜜酒（ミード）とも日本酒とも違う複雑な甘み。少し背伸びした誕生日プレゼントや、甘口好きへの贈り物に。クラフトサケの先駆者・稲とアガベが見せる“特別な顔”。"),
    ("お祝い・改まった贈り物に", "CELEBRATION", "nondo", 0,
     "水もと × 木桶 × 150日超の長期発酵という、手間の結晶。一本に蔵の思想が宿る物語性は、昇進祝いや大切な節目の贈り物にふさわしい。じっくり味わう時間ごと、贈りたい一本。"),
    ("お祝い・改まった贈り物に", "CELEBRATION", "ine-to-agave", 4,
     "稲とアガベが特別な機会に放つ、スペシャルエディション。りんごを纏わせた贅沢な果実表現で、ハレの日の贈り物に。価格帯にも、改まった贈答にふさわしい特別感がある。"),
    ("お祝い・改まった贈り物に", "CELEBRATION", "pukupuku", 5,
     "木桶仕込み × 全麹という、クラフトサケの技を凝縮したぷくぷく醸造のハイエンド。甘みと旨みが濃密で、酒通へのとっておきの贈り物に。一万円を超える、まさに特別な一本。"),
    ("お祝い・改まった贈り物に", "CELEBRATION", "heiroku", 2,
     "「百年の眠りから目覚めた酵母」で醸す平六醸造の最高峰。発芽玄米ベースの奥行きある味わいは、忘れられない記念の贈り物に。古民家を改装した蔵から生まれる、物語のある一本。"),
    ("自分へのご褒美に", "FOR YOURSELF", "pukupuku", 4,
     "ICC SAKE AWARD 2025の頂点に立った、いま最も語られる一本。頑張った自分へのご褒美に、受賞の味を確かめてみては。蔵付き酵母と木桶が生む、発酵の力を存分に味わえる。"),
    ("自分へのご褒美に", "FOR YOURSELF", "nondo", 2,
     "nondoが水もと・木桶で醸す、権化シリーズの無濾過生原酒。米糠まで活かした濃密で複雑な味わいは、特別な夜にゆっくり向き合いたい。誰かにではなく、頑張った自分へ贈る一本。"),
]


def build_gift():
    cards = ""
    cur = None
    for i, (scene, scene_en, slug, idx, comment) in enumerate(GIFT_PICKS, start=1):
        if scene != cur:
            cur = scene
            cards += f'    <div class="pick-group">{scene}<span class="en">{scene_en}</span></div>\n'
            cards += f'    <p class="cat-lead" style="max-width:820px;">{GIFT_SCENE_INTROS[scene]}</p>\n'
        kura = by_slug(slug)
        b = BRANDS[slug][idx]
        btn = ""
        _rk = resolve_rakuten(slug, idx, b["name"]) if RAKUTEN_ENABLED else None
        _az = resolve_amazon(slug, idx, b["name"]) if AMAZON_ENABLED else None
        if _rk:
            btn += f'<a class="pick__btn" href="{_rk}" target="_blank" rel="noopener sponsored">楽天市場で探す →</a>'
        if _az:
            btn += f'<a class="pick__btn pick__btn--amazon" href="{_az}" target="_blank" rel="noopener sponsored">Amazonで探す →</a>'
        if btn:
            btn += '<span class="pick__pr">PR</span>'
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

    # 予算で並べた比較表
    rows = ""
    ordered = sorted(GIFT_PICKS, key=lambda p: (BRANDS[p[2]][p[3]].get("price") or 10**9))
    for scene, scene_en, slug, idx, comment in ordered:
        kura = by_slug(slug)
        b = BRANDS[slug][idx]
        price = f"¥{b['price']:,}" if b.get("price") else "—"
        vol = f"{b['volume_ml']}ml" if b.get("volume_ml") else "—"
        rows += (f'<tr><td class="p">{price}</td>'
                 f'<td class="nm"><a href="../brand/{slug}-{idx}.html">{b["name"]}</a></td>'
                 f'<td>{kura["name"]}</td><td>{vol}</td><td>{scene}</td></tr>\n')

    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "GIFT GUIDE / 贈りものに")}
      <div class="prose">
        <p class="lead">米と副原料で醸す、<span class="accent">自由</span>な酒。話題性があって、見た目も華やか、しかも“物語”がついてくる——クラフトサケは、実は<span class="accent">贈りもの</span>にとても向いている。</p>
        <p>少量生産で、ほかではなかなか手に入らない特別感。蔵ごとの背景や、ホップ・果実・木桶といった造りのストーリー。渡しながら「これはね」と一言添えられるのが、クラフトサケのギフトの楽しさだ。この記事では、saketto 編集部が<strong>シーンと予算</strong>に分けて、贈って喜ばれる一本を選びました。スペックは、すべて一次ソースで確認した値です。</p>
        <div class="callout">
          <div class="callout__label">この選びかたについて</div>
          <p>収録銘柄の中から「贈り物としての華やかさ・話題性・物語性・予算帯のバランス」を目安に編集部が選びました。<strong>番号は順位ではなく、シーン別の並び</strong>です。価格は2026年8月時点の確認値で、ロットや時期により変わります。最新の価格・在庫・ギフト対応は各リンク先でご確認ください。</p>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("02", "BY SCENE / シーンで選ぶ")}
      <div class="prose">
        <p>気になった一本は、銘柄ページから味わいや蔵の物語を辿れます。「楽天市場で探す」では、その銘柄名で楽天市場の検索結果へ移動します（在庫・価格・ギフト対応は時期や販売店により異なります）。</p>
      </div>
{cards}    </section>
{divider()}
    <section class="section">
{section_meta("03", "BY BUDGET / 予算で選ぶ")}
      <div class="prose">
        <h2 class="sub-h">予算から、<span class="accent">ひと目</span>で。</h2>
        <p>手頃な手土産から、改まったお祝いまで。価格の安い順に並べました。「—」は公式に非開示、またはロットで変動するものです。</p>
      </div>
      <div class="cmp-wrap">
        <table class="cmp">
          <thead><tr><th>参考価格</th><th>銘柄</th><th>蔵</th><th>容量</th><th>シーン</th></tr></thead>
          <tbody>
{rows}          </tbody>
        </table>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("04", "BEFORE YOU SEND / 贈るときに")}
      <div class="prose">
        <h2 class="sub-h">贈る前に、<span class="accent">確認したいこと</span>。</h2>
        <p>クラフトサケをギフトに選ぶときは、いくつか気をつけたい点があります。せっかくの贈り物を、いちばんいい状態で届けるために。</p>
        <ul>
          <li><strong>年齢の確認を</strong>　酒類は、20歳未満の方へ贈ることはできません。贈る相手が20歳以上かどうか、必ず確認してください。</li>
          <li><strong>多くは「要冷蔵」</strong>　クラフトサケは火入れをしない生酒・にごりが多く、冷蔵保管が基本です。配送はクール便で、相手が受け取れるタイミングに合わせて。手渡しのときも保冷を心がけて。</li>
          <li><strong>熨斗・ラッピングは要確認</strong>　熨斗・化粧箱・ギフト包装に対応しているかは、蔵や販売店によって異なります。注文の前に、各蔵の公式サイトや販売ページで確認しておくと安心です。</li>
          <li><strong>早めの手配を</strong>　少量生産・限定流通のものが多く、人気銘柄や季節限定品は売り切れることもあります。余裕をもって用意するのがおすすめです。</li>
        </ul>
        <div class="callout">
          <div class="callout__label">活性タイプはとくに注意</div>
          <p>発泡する「活性にごり」は、輸送・開栓に注意が必要な場合があります。贈る相手に開け方を一言添えるか、商品ページの案内を確認しておくと親切です。</p>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("05", "HOW TO PRESENT / 渡し方と、添えることば")}
      <div class="prose">
        <h2 class="sub-h">酒より先に、<span class="accent">物語</span>を渡す。</h2>
        <p>クラフトサケが贈りものとして強いのは、味だけが理由ではありません。<strong>一本ごとに、話せる背景がある</strong>からです。ここを伝えるかどうかで、同じ酒でも受け取られ方がまるで変わります。</p>
        <p>たとえば、震災後に立ち上がった蔵の酒。地震で被災した蔵と共同で醸した一本。途絶えかけた製法を復活させた酒。地元の農家が作った果実を使った酒。<strong>「なぜこの一本を選んだのか」を一言添えるだけで、贈りものは記念になります</strong>。長い説明は要りません。「この蔵、駅の構内で醸してるらしいよ」——それだけで会話が生まれます。</p>
        <p>添えるカードに書くなら、<strong>味の説明より、選んだ理由</strong>を。「甘口です」より「あなたが好きなグレープフルーツの香りがすると思って」のほうが届きます。saketto の各銘柄ページには、蔵の背景や副原料の由来をまとめてあるので、書くことに困ったら覗いてみてください。</p>
        <p><strong>手渡しできるなら、それがいちばん</strong>です。要冷蔵の生酒は特に、受け取り手が家にいるかどうかが品質に直結します。配送する場合は、相手の在宅時間を確認するか、日時指定ができる販売ページを選ぶと安心です。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("06", "CAUTION / 避けたほうがいいこと")}
      <div class="prose">
        <h2 class="sub-h">よかれと思って、<span class="accent">外す</span>前に。</h2>
        <p>お酒の贈りものには、気をつけたい場面があります。相手を思っての一本が、かえって負担になってしまうことは避けたいところです。</p>
        <p>まず<strong>相手が飲めるかどうか</strong>。体質的にお酒を受けつけない人、健康上の理由で控えている人、妊娠中・授乳期の方、信仰上飲まない方——確信が持てないときは、お酒以外を選ぶか、事前にそれとなく確かめるのが安全です。</p>
        <p>次に<strong>保管の負担</strong>。要冷蔵の生酒は、受け取った側が冷蔵庫の場所を空けなければなりません。四合瓶が何本も届けば、それだけで一苦労です。ひとり暮らしの方や冷蔵庫が小さい家庭には、<strong>常温保存できる火入れタイプか、500ml以下の小さめ</strong>を選ぶ配慮が効きます。</p>
        <p>そして<strong>開け方の難しい酒</strong>。慣れていない相手には、落ち着いたタイプを選ぶほうが安心です。</p>
        <p>最後に、<strong>相手の好みを外した「通好み」</strong>。珍しさや希少性で選んだ一本が、飲み慣れない相手には難解に映ることがあります。贈りものは自分の趣味を伝える場ではなく、相手が心地よく飲める一本を届ける場——<strong>迷ったら、分かりやすくおいしいものを</strong>。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("07", "PACKAGING / 見た目という贈りもの")}
      <div class="prose">
        <h2 class="sub-h">瓶とラベルも、<span class="accent">贈りもの</span>のうち。</h2>
        <p>贈りものでは、味と同じくらい<strong>見た目が働きます</strong>。手渡した瞬間に相手が受け取るのは、まずラベルの印象だからです。</p>
        <p>クラフトサケは、この点でかなり強いお酒です。<strong>新しい造り手たちはラベルのデザインに力を入れており</strong>、日本酒の伝統的な意匠とは違う、モダンで洗練されたものが多く並びます。ワインボトルに近い形の瓶を使う蔵もあり、食卓に置いたときの佇まいが華やかです。お酒に詳しくない相手ほど、この第一印象が効きます。</p>
        <p>ただし注意したいのが<strong>化粧箱の有無</strong>です。少量生産の蔵では、箱を用意していない銘柄も少なくありません。フォーマルな場面で贈るなら、購入前に<strong>箱・熨斗・ラッピングに対応しているか</strong>を確認してください。対応していない場合でも、酒販店によっては別途包装を受けてくれることがあります。</p>
        <p>複数本を贈るなら、<strong>色や表情の違う銘柄を組み合わせる</strong>と喜ばれます。にごりの白、果実の淡い桃色、澄んだ琥珀——並べたときに絵になるセットは、開ける前から楽しめます。飲み比べの話題にもなります。</p>
        <p>季節感を意識するのも効きます。<strong>いま贈るからこの一本</strong>という理由があると、贈りものの意味がひとつ増えます。相手にとっても、季節の記憶と結びついて残りやすくなります。</p>
        <p>逆に、<strong>あえて定番を選ぶ</strong>という判断もあります。限定品は確かに希少ですが、相手が気に入ったときに二本目が手に入りません。<strong>「また飲みたい」と思ってもらえたときに買える一本</strong>のほうが、長い目で見れば喜ばれることもあります。贈る相手との関係や、その後の会話まで想像して選んでみてください。</p>
        <p>最後に、<strong>自分でも一本買っておく</strong>ことをすすめます。同じ銘柄を手元に置いておけば、相手が飲んだときに話が通じます。「あの酸っぱさ、驚いたでしょう」——贈ったあとに会話が生まれるかどうかで、贈りものの価値はずいぶん変わります。<strong>味を共有できる相手がいることが、酒のいちばんの贅沢</strong>かもしれません。</p>
        <p>配送で贈るなら、<strong>届く日を相手と合わせておく</strong>のが親切です。要冷蔵の生酒は、受け取りが遅れるほど状態が変わります。とくに夏場の再配達は避けたいところ。日時指定ができる販売ページを選ぶか、事前に「この日に届くよ」と一言伝えておくだけで、贈りものの状態がまるで変わります。</p>
        <p>のしを付けるなら、<strong>表書きは場面に合わせて</strong>。お祝いなら「御祝」、手土産や日頃の感謝なら「御礼」が無難です。クラフトサケは新しいジャンルなので形式にこだわりすぎる必要はありませんが、フォーマルな場面ではここを外すと惜しい。対応の可否は購入前に確認してください。</p>
        <p>なお、<strong>お酒を贈れない相手</strong>のことも頭の隅に置いておいてください。飲まない人、飲めない人にとっては、どんな名酒も置き場所に困る品物になります。そういうときは、同じ蔵が出している甘酒やノンアルコールの発酵飲料という選択肢もあります。<strong>「その蔵の物語を贈る」と考えれば、中身がお酒である必要は必ずしもありません</strong>。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("08", "FURUSATO / ふるさと納税という選択肢")}
      <div class="prose">
        <h2 class="sub-h">自分への<span class="accent">贈りもの</span>なら。</h2>
        <p>人に贈る話を続けてきましたが、<strong>自分へのご褒美</strong>という用途なら、ふるさと納税という手があります。蔵のある自治体に寄附すると、返礼品としてクラフトサケが届く仕組みです。</p>
        <p>saketto が公式に確認できた範囲では、<strong>6つの蔵</strong>が出品しています。秋田県男鹿市の<a href="../brewery/ine-to-agave.html">稲とアガベ</a>（寄附額10,500円・CRAFT 稲とアガベ OGAラベル 500mlと発酵マヨのセット）、福島県南相馬市の<a href="../brewery/haccoba.html">haccoba</a>（12,000円・はなうたホップス 720ml×2本）、福岡県福智町の<a href="../brewery/amanosato.html">天郷醸造所</a>（13,000円・在る 緒奏 720ml）、大阪府高槻市の<a href="../brewery/adachi-noujo.html">足立農醸</a>（15,000円・KOYOI 720ml）、岩手県紫波町の<a href="../brewery/heiroku.html">平六醸造</a>（40,000円・Re:vive Origin アカツキ 720ml）、沖縄県沖縄市の<a href="../brewery/nomu.html">NOMU醸造所</a>（56,000円・SHISHIKAMU 720ml×6本）です。</p>
        <p>注意したいのは、<strong>ふるさと納税は「割引」ではない</strong>ということ。寄附に対する税の控除であり、手続きも必要です。ただ<strong>通販モールには出ていない銘柄が、ここでだけ手に入る</strong>ことがあります。返礼品の内容は変わることがあるので、寄附の前に各ポータルで最新の情報を確認してください。</p>
        <div class="pill-links">
          <a href="../furusato/">ふるさと納税で探す<span class="arr">→</span></a>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("09", "FAQ / よくある質問")}
      <div class="prose">
        <h2 class="sub-h tight">予算は、どのくらいが<span class="accent">目安</span>？</h2>
        <p>ちょっとした手土産なら2,000円前後、誕生日・記念日は2,500〜3,500円ほど、改まったお祝いには5,000円から一万円を超えるものまで。相手との関係性やシーンに合わせて選べます。上の「予算で選ぶ」表も参考にしてください。</p>
        <h2 class="sub-h tight">お酒が強くない人へは？</h2>
        <p>果実やお茶の香りの一本、度数が穏やかなものや、微発泡のにごりが喜ばれやすいです。ジュース感覚で楽しめる果実サケや、低アルコールの銘柄も多くあります。</p>
        <h2 class="sub-h tight">どこで買えますか？</h2>
        <p>各蔵の公式オンラインショップ・取扱酒販店・楽天市場などで購入できます。ギフト対応や在庫の有無は、各販売ページでご確認ください。</p>
        <div class="callout">
          <div class="callout__label">贈る前に</div>
          <p><strong>20歳未満の方への酒類の贈与はできません。</strong>　飲酒運転は法律で禁止されています。妊娠中・授乳期の飲酒はお控えください。贈る相手にも、適量で楽しんでもらえますように。</p>
        </div>
        <div class="readmore">
          <a href="osusume.html">
            <div class="readmore__k">あわせて読む</div>
            <div class="readmore__t">クラフトサケ おすすめ12選</div>
          </a>
          <a href="nomikata.html">
            <div class="readmore__k">KNOW</div>
            <div class="readmore__t">飲み方・楽しみ方</div>
          </a>
        </div>
      </div>
    </section>

  </div>
"""
    html = page_head("ギフトに贈るクラフトサケ — シーンと予算で選ぶ贈りもの【編集部セレクト】",
                     "クラフトサケのギフト・贈り物を、saketto編集部がシーンと予算別に厳選。手土産・誕生日・お祝い・自分へのご褒美まで、稲とアガベ・haccoba・権化ほか話題の銘柄を、確認済みスペックと贈るときの注意点（年齢確認・要冷蔵・熨斗対応）とともに紹介します。",
                     "/guide/gift.html", "article")
    html += masthead(article_masthead_label("gift"), "A Field Guide")
    html += hero(
        article_eyebrow("gift"),
        'クラフトサケを、<br><span class="accent">贈る</span>。',
        "話題性も、華やかさも、物語も。シーンと予算で選ぶ、贈って喜ばれるクラフトサケ。贈るときに気をつけたいことまで。")
    html += body
    html += footer()
    return html


# ────────────── 記事⑥：花酛（はなもと）とは（DEEP） ──────────────

def build_hanamoto():
    hana_terms = term_grid([
        ("花酛 / 華もと", "HANAMOTO", "東北地方に伝わるとされる、幻のどぶろく製法。唐花草（からはなそう）を用い、まるでビールのように醸す。文献『諸国ドブロク宝典』に記録が残る。"),
        ("唐花草", "KARAHANASOU", "「東洋のホップ」と呼ばれる、ホップの近縁種。東北の山奥などに自生する。ビールに使うホップの和名は「セイヨウカラハナソウ」。"),
        ("どぶろく", "DOBUROKU", "もろみを「こさない」米の酒。固液を分けないため清酒の定義を外れ、酒税法上は「その他の醸造酒」に分類される。"),
        ("ドライホッピング", "DRY HOPPING", "ビールづくり由来の技法。発酵の後半などにホップを加え、華やかな香りを引き出す。haccobaは花酛にこれを掛け合わせる。"),
    ])

    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "WHAT IS / 花酛とは")}
      <div class="prose">
        <p class="lead">花酛（はなもと）とは、東北地方に伝わるとされる<span class="accent">“幻のどぶろく製法”</span>。「東洋のホップ」と呼ばれる植物<span class="accent">唐花草（からはなそう）</span>を使い、まるでビールのように醸す——米の酒とホップが、ずっと昔に出会っていた証のような造りだ。</p>
        <p>クラフトサケといえば「ホップを使った日本酒」のイメージを持つ人も多い。その源流をたどると、現代の発明ではなく、<strong>日本の家庭に伝わっていた古い製法</strong>にたどり着く。それが花酛。いまやほとんど忘れられたこの製法を、福島の小さな蔵が甦らせたことから、クラフトサケのひとつの潮流が生まれた。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("02", "KARAHANASOU / 東洋のホップ")}
      <div class="prose">
        <h2 class="sub-h">ホップは、<span class="accent">日本</span>にも生えていた。</h2>
        <p>花酛の鍵をにぎるのが、<strong>唐花草（からはなそう）</strong>という植物だ。ビールの苦味と香りをつくるホップ。その<strong>近縁種</strong>にあたり、東北の山奥などに<strong>自生</strong>している。だから「東洋のホップ」とも呼ばれる。じつは、ビールに使われるあのホップの和名は<strong>「セイヨウカラハナソウ」</strong>——つまり、日本の唐花草と西洋のホップは、植物として親戚どうしなのだ。</p>
        <p>かつての人々は、身近な山に生えるこの唐花草を摘み、酒づくりに使った。その煎じ汁には、雑菌の繁殖をやわらげる働きがあるとされ、ホップがビールの保存性を高めるのと同じ知恵が、米の酒にも生きていた。日本の山里に、ホップを効かせた酒が——その事実が、ビールと日本酒をへだてる壁を、軽やかに飛び越えていく。</p>
      </div>
      {hana_terms}
    </section>
{divider()}
    <section class="section">
{section_meta("03", "WHY PHANTOM / なぜ“幻”になったか")}
      <div class="prose">
        <h2 class="sub-h">家庭の酒が、<span class="accent">消えた</span>とき。</h2>
        <p>花酛は、<strong>かつて各家庭でどぶろくづくりを楽しんでいた時代に行われていた</strong>とされる製法だ。専門の蔵だけでなく、ふつうの家の台所で、その土地の植物を使って米を醸す——そんな暮らしの酒の一つだった。記録は、各地の自家醸造を集めた文献『諸国ドブロク宝典』などにわずかに残る。</p>
        <p>しかし、家庭での酒づくりがやがて姿を消していくなかで、花酛もまた忘れられていった。受け継ぐ人がいなくなれば、製法は途絶える。山の唐花草で醸す酒は、いつしか「幻」と呼ばれるようになった。木桶仕込みがそうであったように、効率や制度の流れのなかで、手のかかる小さな知恵が静かに失われていったのだ。</p>
        <div class="callout">
          <div class="callout__label">編集部より</div>
          <p>花酛の歴史や来歴は、文献や伝承に基づく部分が多く、細部には諸説あります。本記事は、再現に取り組む蔵（haccoba）の公式情報と『諸国ドブロク宝典』等の記述をもとに、一般的に語られる内容を紹介しています。</p>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("04", "REVIVAL / 小高から、もう一度")}
      <div class="prose">
        <h2 class="sub-h">「自由を、醸そう。」<span class="accent">はじまりの一本</span>。</h2>
        <p>その幻の製法に光を当てたのが、<a href="../brewery/haccoba.html">haccoba</a>。2021年、福島県南相馬市小高区で立ち上がったクラフトサケの先駆けだ。この蔵が花酛を再現してつくった「<strong>はなうたドロップス</strong>」は、唐花草の軽やかな苦味で、お米と麹のやさしい味わいを際立たせたどぶろく。失われた製法を、現代の蔵がもう一度かたちにした。</p>
        <p>さらに haccoba は、この古い花酛に、<strong>ビールの「ドライホッピング」技法を掛け合わせる</strong>。発酵の後半にホップを加えて香りを開かせる、クラフトビールの自由な発想だ。こうして生まれた看板銘柄が「<a href="../brand/haccoba-0.html">はなうたホップス</a>」。米のクリアな甘みと、華やかなホップの香りが同居する一本は、いまのクラフトサケを象徴する味になった。「花酛」の名を冠した復刻版「<a href="../brand/haccoba-4.html">水を編む</a>」もある。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("05", "MEANING / 「枠の外」の原点")}
      <div class="prose">
        <h2 class="sub-h">米の酒とホップは、<span class="accent">敵じゃない</span>。</h2>
        <p>花酛がクラフトサケにとって特別なのは、それが単なる懐古ではないからだ。「日本酒にホップなんて邪道だ」——そんな声に対して、花酛は静かにこう答える。<strong>米の酒とホップは、もともと日本で出会っていた</strong>、と。</p>
        <p>この「もともとあった」という一点は、思いのほか重い。新しいことを始めるとき、人はしばしば伝統と対立させられる。だが花酛の存在は、<strong>その対立そのものが思い込みだった</strong>と示している。伝統とは固定された一つの形ではなく、失われたものも含めた幅のことだ——そう考えられるようになると、造り手の選択肢は一気に広がる。</p>
        <p>だから花酛は、いまも参照され続けている。復刻そのものを目指す造りだけでなく、<strong>「昔の人はこう考えたのか」という発想の種</strong>として。山の草を使う、身近な素材で保存性を高める、ビールのような手つきで米を醸す——ひとつひとつは古い知恵だが、組み合わせ直せば新しい酒になる。<strong>過去は、いちばん手つかずのアイデアの宝庫でもある</strong>。</p>
        <p>失われた製法は、おそらく花酛だけではない。各地の家庭で醸されていた酒には、記録に残らないまま消えた工夫がいくつもあったはずだ。<strong>いま残っている文献は、その氷山の一角</strong>にすぎない。花酛が甦ったことは、まだ他にも掘り起こせるものがあるという合図でもある。</p>
        <p>クラフトサケは、清酒（日本酒）の定義の<strong>外</strong>で自由に醸される米の酒。ホップや果実を使い、もろみを濾さない。一見すると「新しすぎる」その造りは、じつは古い知恵の再発見でもある。花酛という原点があるからこそ、造り手たちは胸を張ってホップを使い、自由に副原料を選べる。伝統に根ざしながら、誰も見たことのない味へ——その精神の出発点に、花酛は立っている。クラフトサケの成り立ちそのものは、<a href="craftsake-towa.html">クラフトサケとは</a>でも詳しく紹介している。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("06", "BOTANY / 唐花草という植物")}
      <div class="prose">
        <h2 class="sub-h">山に生える、<span class="accent">つる草</span>。</h2>
        <p>唐花草（カラハナソウ）は、アサ科のつる性植物だ。夏から秋にかけて、松かさのような形の毬花（きゅうか）をつける。この毬花こそが、酒に苦味と香りをもたらす部分——ビールのホップとまったく同じ仕組みだ。</p>
        <p>ホップと唐花草の関係は、名前を並べるとはっきりする。ビールに使うホップの和名は<strong>セイヨウカラハナソウ</strong>。つまり「西洋の唐花草」であり、日本に自生するカラハナソウは、その変種とされる近縁の植物にあたる。<strong>植物としては、どちらもホップの仲間</strong>だ。</p>
        <p>毬花のなかには<strong>ルプリン</strong>と呼ばれる黄色い粒がある。ここに苦味と香りのもとが詰まっていて、指でつぶすと独特の香りが立つ。ビール醸造では、この成分を煮出して苦味を取り出す。花酛の造りでは、唐花草を煎じた汁を仕込みに使ったとされる。<strong>使う植物も、狙う効果も、ビールとほとんど変わらない</strong>。</p>
        <p>もうひとつ知られているのが<strong>抗菌の働き</strong>だ。ホップに含まれる成分には雑菌の繁殖を抑える作用があり、ビールの保存性を高めてきた。冷蔵設備のない時代、山の草がその役目を果たしていた——花酛が生まれた背景には、こうした経験の蓄積があったと考えられる。</p>
        <div class="callout">
          <div class="callout__label">編集部より</div>
          <p>唐花草の分類や成分については一般に知られている範囲を記しています。花酛での具体的な使用法は文献・伝承に基づく部分が多く、細部には諸説あります。</p>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("07", "NOW / ホップサケの現在地")}
      <div class="prose">
        <h2 class="sub-h">古い製法が、<span class="accent">いちばん新しい</span>棚をつくった。</h2>
        <p>花酛の再現から始まったホップの酒は、いまクラフトサケの主要なジャンルのひとつになっている。saketto がジャンル軸で「ホップサケ」に分類するのは10蔵。米と麹だけの古典どぶろく（16蔵）、果実サケ（12蔵）に次ぐ規模だ。<strong>最大勢力ではないが、この酒が「日本酒の外」へ出るとき最初に開いた扉がここだった</strong>。</p>
        <p>おもしろいのは、<strong>蔵ごとにホップの使い方がまるで違う</strong>ことだ。仕込みの最初から入れて苦味を酒に溶かし込む造り、発酵の後半に加えて香りだけを立たせる造り、品種を明示して個性を打ち出す造り。ビール由来の技法を、それぞれが自分なりに翻訳している。</p>
        <p>ホップの品種名がラベルに載ることも増えた。シトラは柑橘を思わせる香り、ネルソンソーヴィンは白ワインのような風味、ハラタウブランは白ワインを思わせる華やかなアロマ——<strong>ビール好きなら馴染みのある名前が、米の酒のラベルに並ぶ</strong>。これは十年前には考えにくかった光景だ。</p>
        <p>花酛という原点がなければ、ここまで堂々とホップを使えただろうか。「日本酒にホップは邪道」という声に対して、<strong>「もともと日本にあった」と答えられる根拠</strong>があることの意味は大きい。古い製法が、いちばん新しい棚をつくっている。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("08", "SPREAD / 数字で見る、ホップの広がり")}
      <div class="prose">
        <h2 class="sub-h">143本のうち、<span class="accent">19本</span>。</h2>
        <p>花酛から始まったホップの酒は、いまどれくらいの規模になっているのか。saketto の収録143銘柄を副原料で分類すると、<strong>ホップを使った銘柄は19</strong>。米と麹だけの47銘柄、果実系の28銘柄に次ぐ規模で、アガベ・蜂蜜・出汁などの特殊副原料（16銘柄）と並ぶ主要な一角だ。蔵の数でいえば10蔵が手がけている。</p>
        <p>副原料そのものは<strong>全体で76通り</strong>を数えるが、そのなかで<strong>ホップは単独の素材として突出して多い</strong>。果実は苺・ぶどう・柑橘などに分かれるため、「ひとつの素材」として見ればホップが最大勢力といっていい。<strong>幻の製法だったものが、いまジャンルの背骨のひとつになっている</strong>。</p>
        <p>使われ方も一様ではない。品種名まで公開している銘柄があり、シトラを使ったものだけで複数確認できる。ハラタウブランやネルソンソーヴィンといった、クラフトビールで名の通った品種も登場する。<strong>ビールの語彙が、そのまま米の酒のラベルに移植されている</strong>。</p>
        <p>唐花草を煎じて雑菌を抑えた昔の造りと、品種を選んで香りを設計する現在の造り。<strong>技術の精度はまるで違うが、「米の酒にホップを使う」という一点は同じ</strong>だ。19という数字は、その連続性が現実の棚の上で確かめられるところまで来たことを示している。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("09", "IN SAKETTO / ホップの酒を探す")}
      <div class="prose">
        <h2 class="sub-h">花酛から、<span class="accent">いまの一本</span>へ。</h2>
        <p>花酛を起点に生まれた「ホップサケ」は、いまや各地の蔵が手がけるジャンルになった。先駆者 <a href="../brewery/haccoba.html">haccoba</a> の<a href="../brand/haccoba-0.html">はなうたホップス</a>や、花酛の名を冠した復刻版<a href="../brand/haccoba-4.html">水を編む</a>はもちろん、収録する蔵にもホップの造り手は多い。</p>
        <p>たとえば、新潟・福島潟のほとりで醸す<a href="../brewery/lagoon.html">LAGOON BREWERY</a>の「翔空 HOP SAKE」、ホップ品種を打ち出す福岡の<a href="../brewery/librom.html">LIBROM</a>、低アルコールのホップサケも手がける福島・小高の<a href="../brewery/pukupuku.html">ぷくぷく醸造</a>、糀屋ならではのホップどぶろくを醸す滋賀の<a href="../brewery/happy-taro.html">ハッピー太郎醸造所</a>、そして「花風」でホップ（唐花草）を使う<a href="../brewery/ine-to-agave.html">稲とアガベ</a>。それぞれの解釈で、米とホップの出会いを描いている。唐花草・ホップを使った酒は、saketto の各軸からたどれる。</p>
        <div class="pill-links">
          <a href="../subingredients/">副原料「ホップ」から<span class="arr">→</span></a>
          <a href="../genre/">ジャンル「ホップサケ」から<span class="arr">→</span></a>
          <a href="../brewery/haccoba.html">haccoba の銘柄<span class="arr">→</span></a>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("10", "FAQ / よくある質問")}
      <div class="prose">
        <h2 class="sub-h tight">花酛のお酒は、どんな<span class="accent">味</span>？</h2>
        <p>唐花草やホップ由来の軽やかな苦味と華やかな香りに、米と麹のやさしい甘みが重なります。ビールほど苦くなく、日本酒ほど甘くない——その中間のような心地よさ、とイメージするとわかりやすいでしょう。よく冷やして、香りの立つグラスで楽しむのがおすすめです。</p>
        <h2 class="sub-h tight">唐花草とビールのホップは、<span class="accent">同じもの</span>？</h2>
        <p>近縁の“別種”です。ビールに使うホップの和名は「セイヨウカラハナソウ」、日本の山に自生するのが「カラハナソウ（唐花草）」。いわば親戚どうしで、どちらも酒に苦味と香りをもたらします。だから、唐花草で醸す花酛は「日本に昔からあったホップの酒」とも言えるのです。</p>
        <h2 class="sub-h tight">花酛のお酒は、<span class="accent">どこで買える</span>？</h2>
        <p>haccobaの公式オンラインショップや取扱酒販店、楽天市場などで手に入ります。少量生産で、季節やロットによって入荷が変わるため、気になる一本は見かけたときが買いどきです。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("11", "READ ON / もっと味わう")}
      <div class="prose">
        <p>花酛は、クラフトサケの自由を支える原点のひとつ。木桶仕込みや全麹など、ほかの造りのことばも知れば、ひと口の背景がさらに立体的になる。</p>
        <div class="callout">
          <div class="callout__label">楽しむ前に</div>
          <p><strong>20歳未満の飲酒は法律で禁じられています。</strong>　飲酒運転は法律で禁止されています。妊娠中・授乳期の飲酒はお控えください。適量を守り、自分のペースでお楽しみください。</p>
        </div>
        <div class="readmore">
          <a href="kioke.html">
            <div class="readmore__k">あわせて読む</div>
            <div class="readmore__t">木桶仕込みとは</div>
          </a>
          <a href="osusume.html">
            <div class="readmore__k">CHOOSE</div>
            <div class="readmore__t">おすすめ12選から探す</div>
          </a>
        </div>
      </div>
    </section>

  </div>
"""
    html = page_head("花酛（はなもと）とは — 東洋のホップで醸す、幻のどぶろく",
                     "花酛（はなもと）とは何か。東北に伝わる幻のどぶろく製法で、「東洋のホップ」唐花草を使いビールのように醸す。なぜ幻になり、haccobaがどう甦らせ、それがなぜクラフトサケの原点なのかを、一次情報をもとに深掘りします。",
                     "/guide/hanamoto.html", "article")
    html += masthead(article_masthead_label("hanamoto"), "A Field Guide")
    html += hero(
        article_eyebrow("hanamoto"),
        '花酛とは。<br>米とホップの、<span class="accent">古い約束</span>。',
        "東北に伝わる幻のどぶろく製法、花酛。東洋のホップ「唐花草」で醸すその酒に、クラフトサケの自由の原点がある。")
    html += body
    html += footer()
    return html


def build_doburoku():
    dobu_terms = term_grid([
        ("どぶろく", "DOBUROKU", "もろみを「こさない」米の酒。米・米麹・水を発酵させたまま、固形分ごと味わう。酒税法上は清酒ではなく「その他の醸造酒」にあたる。"),
        ("にごり酒", "NIGORIZAKE", "清酒として搾ったあと、澱（おり）をあえて戻したもの。工程としては清酒の側にいる。見た目は似ていても区分が違う。"),
        ("清酒", "SEISHU", "米・米麹・水などを原料に発酵させ、「こしたもの」。この「こす」という一語が、日本酒とどぶろくを分ける法律上の境界線になっている。"),
        ("もろみ", "MOROMI", "米・米麹・水が発酵している最中の、どろりとした状態。これをこせば清酒に、こさなければどぶろくになる。"),
    ])

    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "WHAT IS / どぶろくとは")}
      <div class="prose">
        <p class="lead">どぶろくとは、発酵したもろみを<span class="accent">こさずに</span>仕上げる米の酒。米粒や麹が溶け残ったまま、白く濁っている。日本でいちばん古い酒のかたちでありながら、いまクラフトサケのもっとも新しい表現でもある——それが、どぶろくという酒だ。</p>
        <p>甘酒のようにとろりとしたもの、ヨーグルトを思わせる酸味のあるもの、しゅわしゅわと発泡するもの。ひとくちに「どぶろく」といっても味の幅は驚くほど広い。<strong>その振れ幅の大きさこそが、いま造り手たちを惹きつけている理由</strong>でもある。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("02", "THE LINE / 「こす」という一線")}
      <div class="prose">
        <h2 class="sub-h">日本酒とどぶろくを分けるのは、<span class="accent">たった一工程</span>。</h2>
        <p>どぶろくと日本酒（清酒）の違いは、原料でも味でもない。<strong>「こす」かどうか</strong>、ただそれだけだ。酒税法が清酒を「米、米こうじ、水などを原料として発酵させて<strong>こしたもの</strong>」と定めているため、この一工程を経ない酒は、どれだけ丁寧に醸しても清酒とは呼ばれない。分類は「<strong>その他の醸造酒</strong>」になる。</p>
        <p>ここで多くの人がつまずくのが、<strong>にごり酒との違い</strong>だ。にごり酒も白く濁っているが、あちらは目の粗い布などで<strong>一度こしたうえで</strong>、澱をあえて残している。つまり工程としては清酒の側にいる。見た目がそっくりでも、法律上はまったく別の区分——この境界線を知っておくと、ラベルの「品目」表記の意味が急にはっきり見えてくる。</p>
      </div>
      {dobu_terms}
    </section>
{divider()}
    <section class="section">
{section_meta("03", "HISTORY / 家の酒だったころ")}
      <div class="prose">
        <h2 class="sub-h">かつて、酒は<span class="accent">台所</span>で生まれた。</h2>
        <p>どぶろくは、もともと<strong>家庭で造られる酒</strong>だった。収穫した米と麹を仕込み、その家、その土地の味に育てる。全国各地の自家醸造を記録した文献『諸国ドブロク宝典』には、地域ごとに驚くほど多様な造りが残されている。神社の神事として奉納されるどぶろくは、いまも各地に受け継がれている。</p>
        <p>しかし、酒造りが免許制になり、家庭での醸造が姿を消していくなかで、どぶろくは日常から遠ざかった。造り手が減れば、レシピも技も途絶える。<a href="hanamoto.html">花酛（はなもと）</a>のように、いちど「幻」と呼ばれるまで忘れられた製法もある。<strong>どぶろくが再び表舞台に戻ってくるまでには、長い空白があった</strong>。</p>
        <div class="callout">
          <div class="callout__label">編集部より</div>
          <p>どぶろくの歴史や地域の慣習には、文献・伝承にもとづく部分が多く、細部には諸説あります。本記事は一般に語られている内容と、収録蔵の公式情報をもとに構成しています。酒類の製造には免許が必要です。</p>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("04", "REVIVAL / なぜ、いま増えているのか")}
      <div class="prose">
        <h2 class="sub-h">「こさない」ことが、<span class="accent">自由</span>になった。</h2>
        <p>日本酒（清酒）の製造免許は、新規に取得することがきわめて難しい。だが「その他の醸造酒」であれば、条件を満たせば新たに免許を得る道がある。<strong>つまり、こさない酒を選ぶことは、新しい造り手が世に出るための現実的な入口だった</strong>。</p>
        <p>そしてこの枠には、もうひとつの自由がついてくる。清酒の定義から外れる以上、<strong>米と米麹以外のものを使ってもかまわない</strong>。ホップ、果実、茶葉、ハーブ、スパイス——副原料を自由に選べる。制度上の制約から始まったはずの選択が、結果として表現の幅を一気に押し広げた。いまクラフトサケと呼ばれる酒のほとんどが、この地点から生まれている。成り立ちの全体像は<a href="craftsake-towa.html">クラフトサケとは</a>で詳しく紹介している。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("05", "TASTE / 味わいの振れ幅")}
      <div class="prose">
        <h2 class="sub-h">甘い、酸っぱい、<span class="accent">しゅわしゅわ</span>。</h2>
        <p>どぶろくの味を決めるのは、主に<strong>発酵をどこで止めるか</strong>だ。糖が残っているうちに瓶詰めすれば甘口に、発酵を進めればすっきりと辛口に寄る。白麹や乳酸を使えばヨーグルトのような酸が立ち、火入れをしない生タイプなら瓶の中で発酵が続き、開けたときに気泡が上がってくる。</p>
        <p>米粒の溶け具合も口当たりを大きく変える。ざらりとした粒感を残すもの、なめらかに均一なもの、ムースのように空気を含むもの。<strong>同じ「どぶろく」の三文字でも、蔵によってまるで別の飲みものになる</strong>——飲み比べがこれほど楽しいジャンルはそうない。温度や器の選び方は<a href="nomikata.html">飲み方・楽しみ方</a>にまとめている。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("06", "HOW MADE / どうつくられるか")}
      <div class="prose">
        <h2 class="sub-h">工程は、<span class="accent">日本酒とほぼ同じ</span>。</h2>
        <p>どぶろくと聞くと素朴な酒を想像するかもしれないが、造りの工程そのものは清酒とほとんど変わらない。<strong>米を洗って蒸し、麹をつくり、酒母を立て、もろみを発酵させる</strong>。違うのは最後、搾らないという一点だけだ。</p>
        <p>ただし「搾らない」ことは、造り手にとって<strong>逃げ場がなくなる</strong>ことでもある。清酒なら搾りの工程で澱や雑味を分けられるが、どぶろくは仕込んだものがそのまま製品になる。米の溶け具合、麹の出来、発酵の進み方——すべてが飲み口に直結する。<strong>ごまかしのきかない造り</strong>だと言われるゆえんだ。</p>
        <p>味を決める分かれ道はいくつもある。<strong>麹の選択</strong>ひとつで甘みにも酸にも振れる（麹そのものについては<a href="zenkoji.html">全麹酒とは</a>で詳しく扱っている）。<strong>米の溶かし方</strong>では、粒を残せばざらりとした食感に、溶かし込めばなめらかになる。<strong>発酵をどこで止めるか</strong>で甘辛が決まり、火入れするかしないかで、瓶の中での変化の有無が決まる。</p>
        <p>火入れをしない生タイプは、瓶詰め後も酵母が生きている。<strong>出荷されたあとも発酵が続き、店頭で、冷蔵庫で、少しずつ変わっていく</strong>。開けたときにガスが上がるのはそのためだ。造り手の手を離れてなお動き続ける——どぶろくが「生きている酒」と呼ばれるのは、比喩ではない。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("07", "WORLD / 世界の、濁った酒")}
      <div class="prose">
        <h2 class="sub-h">こさない酒は、<span class="accent">日本だけ</span>じゃない。</h2>
        <p>穀物を発酵させて、濾さずに飲む——この形の酒は、世界のあちこちにある。<strong>穀物が採れる土地には、たいてい濁った酒がある</strong>と言っていい。</p>
        <p>いちばん身近なのは韓国の<strong>マッコリ</strong>だろう。米と、ヌルクと呼ばれる麹の一種を発酵させた、白く濁った酒。日本のどぶろくと発想はよく似ている。中国にも米を醸した濁り酒があり、東南アジアには米から造る地酒が各地に伝わる。</p>
        <p>穀物が米でなくてもいい。アフリカにはモロコシやキビを発酵させた濁った酒があり、中南米にはトウモロコシを使った伝統的な酒がある。ヨーロッパでも、濾過していない濁ったビールは珍しくない。<strong>「澄んだ酒」のほうが、むしろ技術と手間をかけた特殊な形</strong>なのだ。</p>
        <p>そう考えると、どぶろくは遅れた酒でも粗野な酒でもない。<strong>人が穀物から酒を得るときの、もっとも自然な帰結</strong>である。日本ではそこから清酒という精緻な形が生まれ、いまクラフトサケがまた「こさない」ほうへ戻ってきた。往復のなかに、この国の酒の歴史がある。</p>
        <p>ただし「戻ってきた」といっても、単純な復古ではない。かつてのどぶろくが<strong>限られた材料と設備で造られた酒</strong>だったのに対し、いまのどぶろくは<strong>選べる時代の、あえての選択</strong>だ。温度管理も、麹菌の種類も、酵母も選べる。そのうえで搾らないことを選んでいる。<strong>同じ「こさない」でも、意味がまるで違う</strong>。</p>
        <p>その違いは、味にもはっきり出る。かつてのどぶろくが「そうなった」酒だとすれば、いまのどぶろくは<strong>「そう造った」酒</strong>だ。米の溶け具合も、酸の量も、ガスの強さも設計されている。素朴な見た目のまま、中身はかなり緻密——このギャップこそが、いまのどぶろくのおもしろさだと言っていい。</p>
        <p>飲み手の側も変わった。かつては安価な酒の代名詞でもあったどぶろくが、いまは数百円台のものから、造りにこだわった数千円の一本まで幅広く並ぶ。<strong>価格帯そのものが大きく広がった</strong>ことが、このジャンルの現在地をよく表している。</p>
        <div class="callout">
          <div class="callout__label">編集部より</div>
          <p>各国の伝統酒については、一般に知られている範囲での紹介です。製法や分類は地域・時代によって幅があり、細部は異なる場合があります。</p>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("08", "SHUBO / 酒母という分岐点")}
      <div class="prose">
        <h2 class="sub-h">同じどぶろくでも、<span class="accent">出発点</span>が違う。</h2>
        <p>どぶろくの味を左右する要素のうち、飲み手にいちばん見えにくいのが<strong>酒母（しゅぼ）</strong>だ。酵母を安全に増やすための最初の仕込みで、ここで何を使うかによって、酒の酸の出方も香りの方向も変わる。</p>
        <p>saketto の収録銘柄で酒母が公開されているのは<strong>40銘柄</strong>。表記をそのまま数えれば24通り、書き方の違いをまとめると<strong>9つの系統</strong>になる。もっとも多いのは<strong>高温糖化・生酛系・水もと（水酛）系</strong>で、いずれも7銘柄ずつ。<strong>短期間で安全に立てられる現代的な高温糖化と、手間のかかる古典的な酒母が、ほぼ同じ数だけ並んでいる</strong>。</p>
        <p>菩提酛や水酛は、室町期の寺院で行われていたとされる古い手法だ。生米を水に漬けて乳酸発酵させ、その酸っぱい水を仕込みに使う。<strong>雑菌を寄せつけない環境を、微生物の力だけでつくる</strong>——冷蔵も薬剤もない時代の知恵である。それが令和のどぶろくで現役で使われている。</p>
        <p>さらに<a href="hanamoto.html">花酛</a>のように、植物の力を借りる手法もある。<strong>「こさない」という一点で括られるどぶろくの内側に、これだけ違う出発点が並んでいる</strong>——ラベルに酒母の表記があったら、そこは読み飛ばさないでほしい。その一語が、味の設計図を教えてくれる。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("09", "IN SAKETTO / どぶろくを探す")}
      <div class="prose">
        <h2 class="sub-h">米と麹だけの、<span class="accent">まっすぐな一杯</span>。</h2>
        <p>saketto では、副原料を使わず米と麹だけで醸したものを「<strong>古典どぶろく</strong>」として分類している。ここには、東京駅のエキナカで醸す<a href="../brewery/tokyo-station.html">東京駅酒造場</a>、大阪の<a href="../brewery/heiwa-namba.html">平和どぶろく難波醸造所</a>と日本橋の<a href="../brewery/heiwa-kabutocho.html">兜町醸造所</a>、岩手・遠野の<a href="../brewery/nondo.html">nondo</a>、福島・小高の<a href="../brewery/pukupuku.html">ぷくぷく醸造</a>、滋賀の糀屋<a href="../brewery/happy-taro.html">ハッピー太郎醸造所</a>などが並ぶ。</p>
        <p>いっぽうで、ホップを効かせたどぶろく、果実を仕込んだどぶろくも数多い。<a href="../brewery/ine-to-agave.html">稲とアガベ</a>の「DOBUROKU ホップ」、<a href="../brewery/lagoon.html">LAGOON BREWERY</a>の果実を漬け込んだシリーズなどがその代表だ。<strong>「こさない」という一点だけを共有して、あとは自由</strong>——どぶろくというジャンルの広さが、そのまま棚に並んでいる。</p>
        <div class="pill-links">
          <a href="../genre/">ジャンル「古典どぶろく」から<span class="arr">→</span></a>
          <a href="../subingredients/">副原料から探す<span class="arr">→</span></a>
          <a href="../brewery/">蔵から探す<span class="arr">→</span></a>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("10", "FAQ / よくある質問")}
      <div class="prose">
        <h2 class="sub-h tight">どぶろくと甘酒は、<span class="accent">違うもの</span>？</h2>
        <p>別のものです。甘酒は米と麹の糖化だけでつくる、アルコールをほとんど含まない飲みもの（酒粕を溶いたタイプは微量に含みます）。どぶろくは酵母による発酵を経た<strong>お酒</strong>で、度数はおおむね5〜17度と幅があります。見た目が似ているので混同されやすいところです。</p>
        <h2 class="sub-h tight">どぶろくは<span class="accent">日本酒</span>ですか？</h2>
        <p>酒税法上は日本酒（清酒）ではなく「その他の醸造酒」に分類されます。原料も造りも清酒とほぼ同じですが、「こす」工程を経ていないためです。味わいの近さと法律上の区分は別のもの、と考えるとすっきりします。</p>
        <h2 class="sub-h tight">開けるときに<span class="accent">吹きこぼれ</span>ませんか？</h2>
        <p>生タイプや活性タイプは瓶内で発酵が続いているため、勢いよく噴き出すことがあります。<strong>よく冷やし、瓶を立てたまま、栓を少しずつ開けてはガスを逃がす</strong>——これを数回くり返すのが基本です。シンクの上で開けると安心です。詳しくは<a href="nomikata.html">飲み方・楽しみ方</a>へ。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("11", "READ ON / もっと味わう")}
      <div class="prose">
        <p>「こさない」という選択から、クラフトサケの自由は始まった。その原点にある製法や、麹だけで醸すという極端な設計も知れば、一杯の奥行きがさらに増す。</p>
        <div class="callout">
          <div class="callout__label">楽しむ前に</div>
          <p><strong>20歳未満の飲酒は法律で禁じられています。</strong>　飲酒運転は法律で禁止されています。妊娠中・授乳期の飲酒はお控えください。適量を守り、自分のペースでお楽しみください。</p>
        </div>
        <div class="readmore">
          <a href="hanamoto.html">
            <div class="readmore__k">あわせて読む</div>
            <div class="readmore__t">花酛（はなもと）とは</div>
          </a>
          <a href="zenkoji.html">
            <div class="readmore__k">DEEP</div>
            <div class="readmore__t">全麹酒とは</div>
          </a>
        </div>
      </div>
    </section>

  </div>
"""
    html = page_head("どぶろくとは — にごり酒・清酒との違いと、いま増えている理由",
                     "どぶろくとは何か。もろみを「こさない」米の酒で、酒税法上は清酒ではなく「その他の醸造酒」。にごり酒との違い、家庭の酒だった歴史、そしていまクラフトサケの主役になった理由を、収録蔵の実例とともに解説します。",
                     "/guide/doburoku.html", "article")
    html += masthead(article_masthead_label("doburoku"), "A Field Guide")
    html += hero(
        article_eyebrow("doburoku"),
        'どぶろくとは。<br><span class="accent">こさない</span>という選択。',
        "白く濁った、いちばん古い米の酒。その「こさない」一工程が、いまいちばん新しい自由を生んでいる。")
    html += body
    html += footer()
    return html


def build_doko_de_kaeru():
    ch_terms = term_grid([
        ("蔵の公式オンラインショップ", "OFFICIAL EC", "いちばん確実で、品揃えも最新。Shopify・BASE・STORES などで蔵が直接運営する。限定品はここにしか出ないことが多い。"),
        ("通販モール", "ONLINE MALL", "楽天市場などに出店する酒販店経由。ポイントが使え、まとめ買いしやすい。ただし取扱いは蔵によって大きく差がある。"),
        ("ふるさと納税", "FURUSATO", "蔵のある自治体への寄附の返礼品。実質負担を抑えて手に入る。数量限定・季節限定が多く、通年で出ているとは限らない。"),
        ("店頭・蔵併設", "IN STORE", "醸造所併設のタップルームや酒販店。搾りたての生など、輸送に向かない酒はここでしか飲めない・買えない。"),
    ])

    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "THE PROBLEM / なぜ見つからないのか")}
      <div class="prose">
        <p class="lead">クラフトサケは、<span class="accent">探し方にコツがいる</span>。多くの蔵は大量生産を前提としない小さな仕込みを重ね、要冷蔵の生酒が主流で、季節限定も多い。<strong>全国のスーパーに並べるための酒ではない</strong>のだ。</p>
        <p>だから、経路ごとの性格を知っているかどうかで、目当ての一本に届く確率がはっきり変わる。どこを見れば出会えて、どこには最初から並ばないのか——その地図さえ持っていれば、探すこと自体が楽しくなる。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("02", "FOUR CHANNELS / 4つの入口")}
      <div class="prose">
        <h2 class="sub-h">買える場所は、<span class="accent">大きく4つ</span>。</h2>
        <p>クラフトサケの入手経路は、性格の違う4つに整理できる。どれが優れているという話ではなく、<strong>探しているものによって正解が変わる</strong>。</p>
      </div>
      {ch_terms}
      <div class="prose">
        <p>ざっくり言えば、<strong>確実さと品揃えなら公式ショップ、手軽さとポイントなら通販モール、お得さならふるさと納税、そこでしか出会えない一杯なら店頭</strong>。以下、それぞれの使いどころを見ていく。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("03", "OFFICIAL / 蔵の公式ショップ")}
      <div class="prose">
        <h2 class="sub-h">迷ったら、<span class="accent">蔵に直接</span>。</h2>
        <p>もっとも確実なのが、蔵が自分で運営するオンラインショップだ。<strong>新商品・限定ロットは真っ先にここへ出る</strong>。造り手が書いた原材料や仕込みの説明を読めるのも、公式ならではの価値だ。</p>
        <p>saketto が収録25蔵の全銘柄を実際に検索して調べたところ、<strong>通販モールでの取扱いを確認できなかった蔵が11あった</strong>。福岡の<a href="../brewery/librom.html">LIBROM</a>、仙台駅構内の<a href="../brewery/fermenteria.html">Fermenteria</a>、佐渡の<a href="../brewery/sakenova.html">SAKENOVA BREWERY</a>、長崎の<a href="../brewery/dejima-hosendo.html">でじま芳扇堂</a>、埼玉の<a href="../brewery/yamane.html">やまね酒造</a>などがそうだ。<strong>「モールで見つからない＝手に入らない」ではない</strong>。蔵の名前で公式サイトを開くのが近道になる。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("04", "MALL / 通販モールという近道")}
      <div class="prose">
        <h2 class="sub-h">出ている蔵は、<span class="accent">かなり出ている</span>。</h2>
        <p>楽天市場などのモールには、クラフトサケを積極的に扱う酒販店がいる。ポイントが使え、他の買いものとまとめられるのが利点だ。ただし<strong>取扱いの濃淡が激しい</strong>。<a href="../brewery/ine-to-agave.html">稲とアガベ</a>や<a href="../brewery/lagoon.html">LAGOON BREWERY</a>、<a href="../brewery/haccoba.html">haccoba</a>のように多数の銘柄が並ぶ蔵がある一方、1本も出ていない蔵も珍しくない。</p>
        <p>検索でつまずきやすいのが<strong>商品名の表記ゆれ</strong>だ。蔵の公式名と販売店のつけ方が違うことがよくある。語順や英字・かなが入れ替わっていたり、醸造年度やロット番号が足されていたりする。<strong>銘柄名だけで出てこないときは、蔵の名前と組み合わせて検索し直す</strong>——これだけで見つかることが多い。</p>
        <div class="callout">
          <div class="callout__label">saketto の使い方</div>
          <p>収録している各銘柄のページには、実際に購入できることを確認できたものだけ購入リンクを置いています。<strong>買えない銘柄にボタンは出しません</strong>。リンクが無い銘柄は、公式ショップか店頭を当たるのが確実です。</p>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("05", "FURUSATO / ふるさと納税で手に入れる")}
      <div class="prose">
        <h2 class="sub-h">寄附という、<span class="accent">もうひとつの買い方</span>。</h2>
        <p>意外と知られていないのが、ふるさと納税の返礼品にクラフトサケが並んでいることだ。蔵のある自治体に寄附すると、返礼品として届く。<strong>新しい蔵ほど地域と結びついて立ち上がっているため、この経路と相性がいい</strong>。</p>
        <p>saketto が公式に確認できた範囲では、秋田県男鹿市の<a href="../brewery/ine-to-agave.html">稲とアガベ</a>、福島県南相馬市の<a href="../brewery/haccoba.html">haccoba</a>、岩手県紫波町の<a href="../brewery/heiroku.html">平六醸造</a>、大阪府高槻市の<a href="../brewery/adachi-noujo.html">足立農醸</a>、福岡県福智町の<a href="../brewery/amanosato.html">天郷醸造所</a>、沖縄県沖縄市の<a href="../brewery/nomu.html">NOMU醸造所</a>が出品を確認できている。<strong>通販モールには出ていないのに、ふるさと納税でだけ買える銘柄もある</strong>ので、見落とさないでほしい。</p>
        <div class="pill-links">
          <a href="../furusato/">ふるさと納税で探す<span class="arr">→</span></a>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("06", "IN STORE / そこでしか飲めない酒")}
      <div class="prose">
        <h2 class="sub-h">運ばない、という<span class="accent">選択</span>。</h2>
        <p>クラフトサケには、<strong>意図的に流通させない酒</strong>がある。搾ったばかりの生、瓶内で発酵が進む活性タイプ——輸送や保管で品質が変わってしまうものは、醸造所併設の店やタップルームでしか出さない蔵がある。</p>
        <p>たとえば東京駅のエキナカで醸す<a href="../brewery/tokyo-station.html">東京駅酒造場</a>、大阪タカシマヤ地下の<a href="../brewery/heiwa-namba.html">平和どぶろく難波醸造所</a>と日本橋兜町の<a href="../brewery/heiwa-kabutocho.html">兜町醸造所</a>、仙台駅構内の約3.4坪で醸す<a href="../brewery/fermenteria.html">Fermenteria</a>。神戸の<a href="../brewery/hakutsuru-sakecraft.html">HAKUTSURU SAKE CRAFT</a>は、ナンバリングされたシリーズの多くが資料館限定で、一部の特別銘柄だけが公式オンラインに出る。<strong>「買えない」のではなく、「その場所へ行って出会う酒」として設計されている</strong>。旅の目的地にする価値がある。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("07", "TIMING / 出会うタイミング")}
      <div class="prose">
        <h2 class="sub-h">買える場所より、<span class="accent">買える時期</span>。</h2>
        <p>チャネルを押さえても、まだ半分だ。クラフトサケには<strong>「いつ出るか」という軸</strong>がある。ここを知らないと、目当ての銘柄をいつまでも追いかけることになる。</p>
        <p>多くの蔵は<strong>年に一度だけ仕込む銘柄</strong>を持っている。副原料が農産物である以上、原料が採れる時期にしか造れないからだ。苺の酒は春、ぶどうや梨の酒は秋、柑橘の酒は冬——旬を外すと、次は一年後になる。「売り切れ」の表示は、その年の分が終わったという意味であることが多い。</p>
        <p>そして<strong>発売の告知は、たいてい蔵のSNSが最速</strong>だ。オンラインショップに並ぶ前に予告が出て、公開と同時に売り切れる銘柄もある。人気の蔵ほどこの傾向が強い。<strong>気になる蔵ができたら、まずSNSと入荷通知の登録</strong>——これが遠回りに見えていちばん近い。</p>
        <p>逆に、<strong>通年で手に入る定番銘柄</strong>もある。蔵が年間を通して仕込む看板の一本は、比較的いつでも買える。まずは定番で蔵の味を知り、限定品はタイミングが合ったときに——という付き合い方なら、追いかける気疲れがない。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("08", "SHOPS / 街の酒屋という近道")}
      <div class="prose">
        <h2 class="sub-h">くわしい<span class="accent">一軒</span>を見つける。</h2>
        <p>オンラインの話が続いたが、<strong>街の酒販店</strong>という入口を忘れてはいけない。むしろ慣れてくるほど、この経路の価値がわかってくる。</p>
        <p>クラフトサケを扱うのは、たいてい<strong>地酒やクラフトビールに強い個人経営の酒屋</strong>だ。大型店やスーパーではまず見かけない。こうした店は蔵と直接つながっていることが多く、<strong>限定ロットが少量だけ入る</strong>ことがある。オンラインに出る前に店頭で売り切れる銘柄も珍しくない。</p>
        <p>実店舗の最大の利点は<strong>相談できること</strong>だ。「ビールが好きなんですが」「甘くないものを」——そう伝えれば、棚から一本選んでくれる。ラベルの情報だけでは分からない、開けたときの印象や飲み頃を教えてもらえる。<strong>好みを覚えてもらえれば、入荷時に声をかけてもらえる</strong>こともある。</p>
        <p>探し方は単純で、<strong>蔵の公式サイトの「取扱店」ページを見る</strong>のが確実だ。蔵によっては取扱店の一覧を公開している。自分の生活圏に一軒あるかどうかで、クラフトサケとの付き合い方はかなり変わる。</p>
        <p>もうひとつの入口が<strong>飲食店</strong>だ。クラフトサケを置く居酒屋やバー、レストランが少しずつ増えている。買う前に飲んで確かめられるのは大きな利点で、しかも一杯単位なら気軽に何種類も試せる。<strong>店で気に入った銘柄を、あとから瓶で買う</strong>——この順番なら失敗がない。醸造所に併設された店なら、その場でしか出さない搾りたてに出会えることもある。</p>
        <p>イベントという手もある。クラフトサケの造り手が集まる催しが各地で開かれており、<strong>複数の蔵を一度に飲み比べられる</strong>。造り手本人が注いでくれることも多く、その場で疑問を聞ける。「どの蔵から入ればいいか分からない」という段階の人にとって、これ以上効率のいい入口はない。開催情報は各蔵や協会の告知で流れる。</p>
        <p>結局のところ、探し方に唯一の正解はない。大事なのは、見つからなかったときに「売っていない」と結論しないことだ。<strong>経路を変えれば、たいていの酒はどこかで買える</strong>。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("09", "REALITY / 実際に、どれだけ買えるのか")}
      <div class="prose">
        <h2 class="sub-h">143銘柄を、<span class="accent">全部検索</span>してみた。</h2>
        <p>「クラフトサケは手に入りにくい」とよく言われる。では実際どれくらいなのか。saketto では収録している<strong>143銘柄すべてを通販モールで実際に検索し、購入できる出品があるかを一件ずつ確認</strong>している。</p>
        <p>結果は、<strong>購入リンクを出せたのが58銘柄</strong>。全体の約4割である。残る85銘柄については、確認した時点で取扱いが見つからなかった。<strong>収録の半分以上は、通販モールでは買えない</strong>——これがこのジャンルの現実だ。</p>
        <p>蔵の単位で見ると、さらにはっきりする。<strong>25蔵のうち11蔵は、通販モールでの取扱いを一件も確認できなかった</strong>。自社ECと店頭だけで売る方針の蔵、要冷蔵の生酒しか造っていない蔵、そもそも醸造所併設の店でしか出さない蔵。<strong>買えないのではなく、売り方がそういう設計になっている</strong>のだ。</p>
        <p>だからこそ、この記事で挙げた入口を使い分ける意味がある。<strong>モールで見つからないことは、その酒が手に入らないことを意味しない</strong>。公式ショップへ回り、ふるさと納税を調べ、取扱店を探す。経路を変えれば道は開ける。</p>
        <div class="callout">
          <div class="callout__label">saketto の方針</div>
          <p>各銘柄ページには、<strong>実際に購入できる出品を確認できたものだけ</strong>購入リンクを置いています。「たぶん買えるだろう」で表示することはしません。リンクのない銘柄は、公式ショップか店頭を当たってください。調査は定期的にやり直しており、出品が復活すればリンクも戻ります。</p>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("10", "TIPS / 買うときの注意点")}
      <div class="prose">
        <h2 class="sub-h tight">要冷蔵かどうかを、<span class="accent">必ず確認</span>する。</h2>
        <p>生タイプはクール便が前提です。常温便しか選べない販売ページでは、火入れ版かどうかを確かめてください。届いたらすぐ冷蔵庫へ。夏場の再配達は品質にひびきます。</p>
        <h2 class="sub-h tight">「売り切れ」は<span class="accent">終わり</span>ではない。</h2>
        <p>少量生産なので、公式ショップが品切れでも次のロットが仕込まれていることがよくあります。季節限定は翌年また登場します。入荷通知の登録や、蔵のSNSを追うのがいちばん早い方法です。</p>
        <h2 class="sub-h tight">見つけたときが、<span class="accent">買いどき</span>。</h2>
        <p>同じ銘柄でも醸造年度やロットで中身が変わります。「次でいいか」と思った一本が、次はもう別の設計になっていることも。気になったら、その場で確保するのが後悔しないコツです。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("11", "READ ON / 次の一本へ")}
      <div class="prose">
        <p>買い方がわかったら、あとは選ぶだけ。タイプ別のおすすめや、贈りものとしての選び方もあわせてどうぞ。</p>
        <div class="callout">
          <div class="callout__label">楽しむ前に</div>
          <p><strong>20歳未満の飲酒は法律で禁じられています。</strong>　飲酒運転は法律で禁止されています。妊娠中・授乳期の飲酒はお控えください。適量を守り、自分のペースでお楽しみください。</p>
        </div>
        <div class="readmore">
          <a href="osusume.html">
            <div class="readmore__k">あわせて読む</div>
            <div class="readmore__t">おすすめ12選</div>
          </a>
          <a href="gift.html">
            <div class="readmore__k">CHOOSE</div>
            <div class="readmore__t">ギフトに贈るクラフトサケ</div>
          </a>
        </div>
      </div>
    </section>

  </div>
"""
    html = page_head("クラフトサケはどこで買える？ — 公式EC・通販・ふるさと納税・店頭の探し方",
                     "少量生産のクラフトサケを確実に手に入れるには。蔵の公式オンラインショップ、通販モール、ふるさと納税、店頭限定という4つの入口の違いと、要冷蔵・表記ゆれ・季節限定という壁の越え方を、収録蔵の公式情報をもとに解説します。",
                     "/guide/doko-de-kaeru.html", "article")
    html += masthead(article_masthead_label("doko-de-kaeru"), "A Field Guide")
    html += hero(
        article_eyebrow("doko-de-kaeru"),
        'どこで買える？<br><span class="accent">4つの入口</span>を知る。',
        "近所の酒屋で見かけないのは、人気がないからではない。流通の量と経路が、そもそも違うからだ。")
    html += body
    html += footer()
    return html


def build_zenkoji():
    koji_terms = term_grid([
        ("全麹（全麹仕込み）", "FULL KOJI", "仕込みに使う米を、すべて麹にして醸す造り。掛米を使わないため、麹由来の甘みと酸がまっすぐ出る。「十割麹」とも呼ばれる。"),
        ("掛米", "KAKEMAI", "通常の仕込みで、麹にせず蒸したまま加える米。一般的な清酒では原料米の約8割を占める。全麹ではこれを使わない。"),
        ("麹", "KOJI", "蒸した米に麹菌を繁殖させたもの。デンプンを糖に変える酵素をつくる、酒造りの心臓部。"),
        ("その他の醸造酒", "OTHER BREWED", "酒税法上の分類。清酒の定義を外れた米の酒はここに入る。クラフトサケの多くがこの区分にあたる。"),
    ])

    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "WHAT IS / 全麹とは")}
      <div class="prose">
        <p class="lead">全麹（ぜんこうじ）とは、仕込みに使う米を<span class="accent">すべて麹にして</span>醸す造り。ふつうの酒なら8割ほどを占める「掛米」を、いっさい使わない。極端で、手間がかかり、そして<strong>ほかでは出せない濃密さ</strong>にたどり着く設計だ。</p>
        <p>ひとくち含むと、まず甘みが来る。次に、その甘さを引き締める酸。とろりとした質感が舌に残り、余韻が長い。<strong>日本酒ともワインとも違う、麹という素材そのものの味</strong>——それが全麹酒の正体だ。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("02", "THE STRUCTURE / なぜ濃くなるのか")}
      <div class="prose">
        <h2 class="sub-h">酒造りの<span class="accent">比率</span>を、壊す。</h2>
        <p>一般的な清酒づくりでは、原料米のうち<strong>約2割を麹にし、残り8割は蒸した掛米として加える</strong>。麹がつくる酵素が掛米のデンプンを糖に変え、その糖を酵母がアルコールに変える——この分業で酒ができあがる。</p>
        <p>全麹は、この比率を根本から変えてしまう。<strong>米を10割すべて麹にする</strong>のだ。酵素も、麹由来の旨み成分も、通常の何倍もの密度で仕込みに入る。結果として、糖化の力が強く働き、<strong>発酵で消費しきれない糖が残る</strong>。だから甘い。同時に麹由来のアミノ酸や有機酸も濃く出るため、ただ甘いだけでは終わらない、厚みのある味になる。</p>
      </div>
      {koji_terms}
    </section>
{divider()}
    <section class="section">
{section_meta("03", "THE COST / 手間という代償")}
      <div class="prose">
        <h2 class="sub-h">麹をつくるのは、<span class="accent">いちばん重い仕事</span>。</h2>
        <p>製麹（せいきく）——蒸した米に麹菌を植え、温度と湿度を管理しながら二昼夜ほどかけて育てる工程は、酒造りのなかでもっとも神経を使う作業とされる。夜通し数時間おきに手入れをすることもある。</p>
        <p>全麹とは、その重い工程を背負う量が跳ね上がるということだ。通常2割の米を麹にするところを10割にするのだから、<strong>製麹する米の量は単純計算で5倍</strong>になる。同じ量の酒を仕込むのに、麹室（こうじむろ）の稼働も、人手も、時間も跳ね上がる。<strong>それでも造る蔵があるのは、そこにしかない味があるから</strong>にほかならない。生産量が限られ、価格も高めになりがちなのは、この構造ゆえだ。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("04", "THE LINE / 清酒の枠を外れる")}
      <div class="prose">
        <h2 class="sub-h">蒸米を使わない、<span class="accent">米の酒</span>。</h2>
        <p>興味深いのは、全麹という選択が<strong>法律上の区分にも影響しうる</strong>ことだ。酒税法が定める清酒の原料は「米、米こうじ、水」。全麹では蒸米（掛米）を加えず米麹だけで仕込むため、この原料構成から外れ、<strong>「その他の醸造酒」として造られる</strong>ケースがある。</p>
        <p>収録銘柄でいえば、新潟・柏崎の<a href="../brewery/iyasaka.html">弥栄醸造</a>が醸す「<a href="../brand/iyasaka-0.html">ITTEKI（一擲）十割麹酒</a>」は、米麹のみで仕込むため清酒規格の外にある一本だ。<strong>米だけで造っているのに、制度上は日本酒と呼べない</strong>——この逆説が、クラフトサケという領域のおもしろさをよく表している。区分の考え方は<a href="doburoku.html">どぶろくとは</a>でも整理している。</p>
        <div class="callout">
          <div class="callout__label">編集部より</div>
          <p>酒類の分類は原料と製法の組み合わせで決まり、個々の商品がどの品目にあたるかは製造者の届出によります。本記事は一般的な仕組みの説明で、特定商品の区分については各蔵の表示をご確認ください。</p>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("05", "IN SAKETTO / 全麹の一本を探す")}
      <div class="prose">
        <h2 class="sub-h">濃密さを、<span class="accent">飲みくらべる</span>。</h2>
        <p>全麹はまだ数の少ない造りだが、それぞれの蔵がまったく違う解釈を見せている。</p>
        <p>福島・小高の<a href="../brewery/pukupuku.html">ぷくぷく醸造</a>が醸す「<a href="../brand/pukupuku-5.html">木桶発酵 全麹酒 雫取り</a>」は、全麹に<a href="kioke.html">木桶仕込み</a>を掛け合わせた最上位の一本。麹の濃密さに、木桶がもたらす微生物の複雑さが重なる。いっぽう<a href="../brewery/iyasaka.html">弥栄醸造</a>の「<a href="../brand/iyasaka-0.html">ITTEKI（一擲）</a>」は、柏崎市宮之下の米で醸すことを蔵の方針として掲げる一本だ（この銘柄個別の公式表記は「新潟県産米」）。</p>
        <p><strong>同じ「全麹」でも、木桶と組めば複雑に、単一品種と組めば澄んだ輪郭に</strong>。麹という土台が強いぶん、そこに何を重ねるかで表情が大きく変わる。</p>
        <div class="pill-links">
          <a href="../genre/">ジャンル「全麹酒」から<span class="arr">→</span></a>
          <a href="../brewery/pukupuku.html">ぷくぷく醸造の銘柄<span class="arr">→</span></a>
          <a href="../brewery/iyasaka.html">弥栄醸造の銘柄<span class="arr">→</span></a>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("06", "KOJI TYPES / 麹という素材")}
      <div class="prose">
        <h2 class="sub-h">黄・白・黒、<span class="accent">三つの麹</span>。</h2>
        <p>全麹酒の味を決めるのは、量だけではない。<strong>どの麹菌を使うか</strong>が、同じくらい効いてくる。米をすべて麹にするということは、麹菌の性格がそのまま酒の性格になるということでもある。</p>
        <p><strong>黄麹</strong>は、日本酒づくりで長く使われてきた麹だ。穏やかな甘みと、なめらかな旨みを生む。全麹で使えば、麹本来の甘さがまっすぐ出る。<strong>白麹</strong>は焼酎づくりに由来し、発酵の過程で<strong>クエン酸</strong>をつくる。この酸が甘みを引き締めるため、全麹の濃厚さと組み合わせると、甘酸っぱく厚みのある味に仕上がる。クラフトサケで白麹が好まれるのは、この設計のしやすさが理由のひとつだ。</p>
        <p><strong>黒麹</strong>もまたクエン酸を出すが、白麹より力強く、味に骨太な輪郭を与える。泡盛づくりに使われてきた麹で、南国の高温多湿な環境でも腐敗を防げる強さを持つ。</p>
        <p>つまり全麹酒とは、<strong>麹菌という素材の個性を、隠すもののない状態で差し出す造り</strong>だ。掛米という緩衝材がないぶん、選んだ菌の性格が容赦なく出る。造り手にとっては勝負であり、飲み手にとっては<strong>麹そのものを味わえる稀な機会</strong>になる。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("07", "BEYOND SAKE / 麹という日本の技")}
      <div class="prose">
        <h2 class="sub-h">味噌も醤油も、<span class="accent">麹から</span>。</h2>
        <p>麹は酒だけのものではない。<strong>味噌、醤油、酢、みりん、甘酒</strong>——日本の食卓を支える調味料の多くが、麹の働きから生まれている。米や大豆のデンプンとタンパク質を、麹の酵素が糖とうまみに変える。この仕組みが、和食の土台をつくってきた。</p>
        <p>そう考えると、全麹酒という造りの位置づけが見えてくる。<strong>酒を、もっとも調味料に近い側から造っている</strong>のだ。甘みが強く、酸があり、旨みが濃い——全麹酒の味の輪郭は、みりんや甘酒といった麹由来の食品と地続きにある。</p>
        <p>実際、クラフトサケの造り手には<strong>糀屋（こうじや）を営みながら酒を醸す</strong>例もある。麹を売る仕事と、麹で酒を造る仕事は、彼らのなかで切れていない。<strong>麹という一つの素材から、食べるものと飲むものが同じ手つきで生まれてくる</strong>。</p>
        <p>全麹酒を飲むとき、日本酒の一種として捉えるより、<strong>「麹という素材の、ひとつの現れ方」</strong>と考えたほうが腑に落ちるかもしれない。だから食べものとの相性もよく、料理に使ってもおいしい。もとが同じところから来ているのだから、当然といえば当然なのだ。</p>
        <p>ちなみに麹菌（ニホンコウジカビ）は、2006年に日本醸造学会によって<strong>「国菌」</strong>に認定されている。国を代表する菌という位置づけだ。味噌汁の一杯から、醤油のひとさじ、そして全麹酒の一口まで——<strong>同じ菌の仕事が、食卓のあちこちに顔を出している</strong>。そう思って飲むと、濃密な甘みの奥に、見慣れた味の記憶が重なって見えてくる。</p>
        <p>全麹という造りが近年になって増えてきたのも、この文脈で見ると自然だ。<strong>発酵という営みそのものへの関心が高まり</strong>、麹を主役に据える発想が受け入れられやすくなった。酒を「米の酒」としてではなく「麹の酒」として差し出す——その視点の転換が、この濃密な一杯を生んでいる。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("08", "POLISH / 削らないという選択")}
      <div class="prose">
        <h2 class="sub-h">磨くほど良い、<span class="accent">とは限らない</span>。</h2>
        <p>日本酒の世界では長く、<strong>米を磨くほど上等</strong>とされてきた。精米歩合50%以下を大吟醸と呼び、外側を削るほど雑味が減り、香りが澄んでいく——その価値観は、いまも根強い。</p>
        <p>ところがクラフトサケの数字を並べると、別の景色が見える。saketto の収録銘柄で精米歩合が公開されている76件を集計すると、<strong>もっとも多いのは90%</strong>だ。次いで92%。<strong>ほとんど削っていない</strong>ということである。もちろん50%や60%まで磨いた銘柄もあるが、分布の重心は明らかに「削らない」側にある。</p>
        <p>これは手抜きではなく、<strong>設計思想の違い</strong>だ。米の外側には、雑味のもとになると同時に旨みのもとにもなる成分がある。削れば澄むが、その分だけ米の個性も落ちる。<strong>ホップや果実と渡り合うには、澄んだ酒よりも骨格のある酒のほうが向く</strong>——副原料を使う造りだからこそ、米を残す選択に意味が出てくる。</p>
        <p>全麹酒の場合は事情がもうひとつ重なる。麹にする米は磨きすぎると麹菌が繁殖しにくくなるとされる。<strong>削らないことが、全麹という造りと相性がいい</strong>。精米歩合90%という数字は、粗い酒の証ではなく、麹の力を引き出すための条件なのだ。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("09", "HOW TO DRINK / 飲み方")}
      <div class="prose">
        <h2 class="sub-h">濃いから、<span class="accent">小さく</span>注ぐ。</h2>
        <p>全麹酒は甘みと酸がしっかりしているぶん、<strong>少量をゆっくり</strong>が似合う。ワイングラスなど口の広い器で香りを開かせ、冷やしすぎない温度（10〜15度）から始めると、甘みと酸のバランスが取りやすい。</p>
        <p>料理を合わせるなら、<strong>甘さに拮抗する塩気や発酵食品</strong>が好相性だ。熟成チーズ、生ハム、味噌を使った料理、レバーパテなど。デザートワインのように、食後に単体で楽しむのもいい。ロックにして薄めながら飲むと、濃度の変化を追えて面白い。詳しくは<a href="nomikata.html">飲み方・楽しみ方</a>へ。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("10", "FAQ / よくある質問")}
      <div class="prose">
        <h2 class="sub-h tight">全麹酒は<span class="accent">甘口</span>ばかりですか？</h2>
        <p>甘みが出やすい造りではありますが、発酵の進め方や酸の設計で辛口寄りに仕上げることもできます。ただ共通して言えるのは<strong>「味が濃い」</strong>こと。甘辛よりも、密度の高さが全麹らしさです。</p>
        <h2 class="sub-h tight">甘酒と<span class="accent">似ています</span>か？</h2>
        <p>麹の甘みという点では近い印象を受けるかもしれません（甘酒との違いは<a href="doburoku.html">どぶろくとは</a>で整理しています）。全麹酒はそこに<strong>麹由来の酸と厚み</strong>が乗るぶん、甘酒よりずっと輪郭がはっきりしています。</p>
        <h2 class="sub-h tight">「十割麹」と<span class="accent">同じ</span>ものですか？</h2>
        <p>基本的に同じ造りを指す言い方です。米をすべて麹にすることから「全麹」「十割麹」と呼ばれます。蔵によって表記の好みが分かれます。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("11", "READ ON / もっと味わう")}
      <div class="prose">
        <p>麹の力を極端まで押し進めたのが全麹なら、容器の力を借りるのが木桶仕込み。造りのことばを知るほど、一本の設計が読めるようになる。</p>
        <div class="callout">
          <div class="callout__label">楽しむ前に</div>
          <p><strong>20歳未満の飲酒は法律で禁じられています。</strong>　飲酒運転は法律で禁止されています。妊娠中・授乳期の飲酒はお控えください。適量を守り、自分のペースでお楽しみください。</p>
        </div>
        <div class="readmore">
          <a href="kioke.html">
            <div class="readmore__k">あわせて読む</div>
            <div class="readmore__t">木桶仕込みとは</div>
          </a>
          <a href="doburoku.html">
            <div class="readmore__k">KNOW</div>
            <div class="readmore__t">どぶろくとは</div>
          </a>
        </div>
      </div>
    </section>

  </div>
"""
    html = page_head("全麹酒とは — 米をすべて麹にして醸す、濃密な米の酒",
                     "全麹（ぜんこうじ）とは何か。仕込む米をすべて麹にし、掛米を使わない造り。なぜ濃密な甘みと酸が生まれるのか、なぜ清酒の枠を外れるのか、そして手間をかけてまで造る理由を、収録銘柄の実例とともに解説します。",
                     "/guide/zenkoji.html", "article")
    html += masthead(article_masthead_label("zenkoji"), "A Field Guide")
    html += hero(
        article_eyebrow("zenkoji"),
        '全麹酒とは。<br>米を、<span class="accent">すべて麹に</span>。',
        "掛米を使わないという一点。麹にする米は5倍、味は濃密。麹そのものを飲むような一杯がある。")
    html += body
    html += footer()
    return html


def build_new_breweries():
    nb_terms = term_grid([
        ("その他の醸造酒免許", "OTHER BREWED LICENSE", "清酒の製造免許は新規取得がきわめて困難だが、こちらは条件を満たせば新設の道がある。新しい蔵の多くがこの免許で立ち上がる。"),
        ("マイクロ醸造所", "MICRO BREWERY", "小さな仕込みを重ねる醸造所。設備がコンパクトなぶん、街なかや駅構内にも設置できる。"),
        ("委託醸造", "CONTRACT BREWING", "自前の設備を持つ前に、既存の蔵に委託して醸す方式。ブランドを先に立ち上げ、のちに自社醸造へ移る蔵もある。"),
        ("クラフトサケブリュワリー協会", "ASSOCIATION", "2022年に発足した造り手の団体。「クラフトサケ」という呼称そのものを、造り手たちが定義した。"),
    ])

    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "NOW / いま、何が起きているか")}
      <div class="prose">
        <p class="lead"><span class="accent">酒蔵が立つはずのなかった場所</span>に、いま次々と醸造所が生まれている。saketto が収録する蔵の開業年をならべると、その速さがはっきり見えてくる。</p>
        <p>収録25蔵のうち、<strong>2024年以降に立ち上がった蔵が11、さらに開業準備中が1</strong>。ほぼ半数が、ここ2〜3年に集中している計算になる。2024年に5蔵、2025年に5蔵、そして2026年にもすでに新しい名前が加わった。<strong>これは一過性のブームというより、酒づくりの入口が構造的に変わったということだ</strong>。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("02", "WHY / なぜ増えているのか")}
      <div class="prose">
        <h2 class="sub-h">閉じた扉の、<span class="accent">横にあった扉</span>。</h2>
        <p>理由の中心にあるのは免許制度だ。清酒の新規免許がほぼ下りない一方、<strong>「その他の醸造酒」には新設の道が残されている</strong>——この一点の差が、参入の地図を書き換えた。制度の詳しい仕組みは<a href="craftsake-towa.html">クラフトサケとは</a>、こさない造りについては<a href="doburoku.html">どぶろくとは</a>で扱っている。</p>
        <p>ここで見たいのは、その扉をくぐった蔵が<strong>どこに立ったか</strong>だ。清酒の枠を出るという選択は、造りの自由と引き換えに、既存の酒蔵が積み上げてきた前提——広い敷地、大きなタンク、長い歴史——からも自由になることを意味した。<strong>身軽になった蔵は、これまで酒が生まれるはずのなかった場所へ降りていく</strong>。</p>
      </div>
      {nb_terms}
    </section>
{divider()}
    <section class="section">
{section_meta("03", "PLACE / 蔵が立つ場所が変わった")}
      <div class="prose">
        <h2 class="sub-h">酒蔵は、<span class="accent">街の中</span>へ。</h2>
        <p>設備が小さくて済むということは、立地の自由度が上がるということでもある。新しい蔵のリストを見ると、<strong>従来の酒蔵の常識からすると意外な場所</strong>が並ぶ。</p>
        <p>宮城の<a href="../brewery/fermenteria.html">Fermenteria</a>は仙台駅のエキナカで、東京の<a href="../brewery/tokyo-station.html">東京駅酒造場</a>は東京駅のエキナカで醸す。沖縄の<a href="../brewery/nomu.html">NOMU醸造所</a>はコザ一番街の商店街に、大阪の<a href="../brewery/adachi-noujo.html">足立農醸</a>は高槻の団地内に立つ。<a href="../brewery/heiwa-namba.html">平和どぶろく難波醸造所</a>が構えるのは、大阪タカシマヤの地下だ。<strong>造る場所と飲む場所が同じ</strong>——搾りたてをその場で出すという、これまでできなかった体験が成立している。</p>
        <p>いっぽうで、地域に根ざす動きも強い。福岡県福智町の<a href="../brewery/amanosato.html">天郷醸造所</a>は町のクラフトサケ醸造者募集をきっかけに生まれ、佐渡島の<a href="../brewery/sakenova.html">SAKENOVA BREWERY</a>、新潟県柏崎市の集落に立つ<a href="../brewery/iyasaka.html">弥栄醸造</a>のように、<strong>土地の米と風景を前提にした蔵</strong>も続々と現れている。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("04", "TIMELINE / 開業年で読む")}
      <div class="prose">
        <h2 class="sub-h">2020年からの、<span class="accent">5年間</span>。</h2>
        <p>ここからは、生まれた順に並べ直してみる。世代の輪郭がはっきりする。滋賀の<a href="../brewery/happy-taro.html">ハッピー太郎醸造所</a>（2017年）や埼玉の<a href="../brewery/yamane.html">やまね酒造</a>（2019年）のような先行例はあるものの、収録蔵の多くは2020年以降に集まっている。なかでも<strong>2020〜2021年</strong>には、いまジャンルを牽引する蔵が集中して生まれた。福島・小高の<a href="../brewery/haccoba.html">haccoba</a>、秋田・男鹿の<a href="../brewery/ine-to-agave.html">稲とアガベ</a>、新潟・福島潟の<a href="../brewery/lagoon.html">LAGOON BREWERY</a>、福岡の<a href="../brewery/librom.html">LIBROM</a>、東京・浅草の<a href="../brewery/konohanano.html">木花之醸造所</a>——第一世代というべき蔵たちだ。</p>
        <p><strong>2022〜2023年</strong>は、その背中を追う世代。<a href="../brewery/pukupuku.html">ぷくぷく醸造</a>、岩手・遠野の<a href="../brewery/nondo.html">nondo</a>、岩手・紫波の<a href="../brewery/heiroku.html">平六醸造</a>、長崎・出島の<a href="../brewery/dejima-hosendo.html">でじま芳扇堂</a>。そして<strong>2024年以降</strong>になると、大手の参入（神戸の<a href="../brewery/hakutsuru-sakecraft.html">HAKUTSURU SAKE CRAFT</a>）や、駅・商店街・離島といった新しい立地が一気に増える。</p>
        <p>この5年で、<strong>クラフトサケは「一部の先進的な蔵の試み」から「毎年新しい蔵が生まれる領域」へ変わった</strong>。saketto が横断検索のデータベースをつくっているのも、追いかけきれない速さで銘柄が増えているからにほかならない。</p>
        <div class="pill-links">
          <a href="../brewery/">収録25蔵を一覧で見る<span class="arr">→</span></a>
          <a href="../region/">地域から探す<span class="arr">→</span></a>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("05", "MAP / 地図で見る")}
      <div class="prose">
        <h2 class="sub-h">16の都道府県に、<span class="accent">散らばっている</span>。</h2>
        <p>saketto 収録の25蔵（開業準備中の1蔵を含む）を地域で数えると、分布に特徴が見えてくる。<strong>東北6、関東6、関西5、九州4、中部3、沖縄1</strong>。日本酒どころに偏るでもなく、都市に集まるでもなく、<strong>全国に薄く広がっている</strong>のがクラフトサケの特徴だ。</p>
        <p>複数の蔵がある都道府県は6つ。<strong>新潟・福岡・東京が各3蔵、福島・岩手・大阪が各2蔵</strong>で、残りは1県1蔵。全体で16の都道府県にまたがっている計算になる。<strong>まだ空白の県のほうが多い</strong>ということでもあり、この地図はこれから埋まっていく余地が大きい。</p>
        <p>興味深いのは、既存の日本酒の勢力図とずれていることだ。酒どころとして知られる新潟に3蔵あるのは順当だが、<strong>東京に3蔵</strong>というのは従来の酒蔵の分布では考えにくい。駅ナカや商店街に置ける小さな設備だからこそ、都心にも蔵が立つ。<strong>沖縄にクラフトサケの蔵がある</strong>のも、泡盛の島という前提を思えば新しい動きだ。</p>
        <p>そして福島に2蔵。どちらも震災の被害を受けた南相馬市小高区にある。<strong>地域の再生と酒づくりが結びついた例</strong>で、ここから始まった蔵がジャンル全体を牽引してきた。地図の上の点は、それぞれに理由を持って打たれている。</p>
        <div class="pill-links">
          <a href="../region/">地域から蔵を探す<span class="arr">→</span></a>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("06", "ASSOCIATION / 造り手たちの協会")}
      <div class="prose">
        <h2 class="sub-h">ばらばらではなく、<span class="accent">ジャンルとして</span>。</h2>
        <p>個々の蔵が別々に試行錯誤していた段階から、ひとつのジャンルとして名乗る段階へ——その転換点になったのが<strong>クラフトサケブリュワリー協会</strong>の発足だ。「クラフトサケ」という呼び名そのものが、造り手たち自身の手で定義されたことに意味がある。</p>
        <p>saketto が収録する25蔵のうち、協会に加盟しているのは9蔵。<strong>加盟していない蔵のほうが多い</strong>のは、この領域がまだ広がり続けている証拠でもある。大手酒造の実験的ブランドから、地域おこしとして始まった蔵、駅のエキナカに立つ小さな醸造所まで——出自も規模も動機もばらばらな造り手が、「米で自由に醸す」という一点でゆるやかにつながっている。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("07", "PROCESS / 蔵ができるまで")}
      <div class="prose">
        <h2 class="sub-h">思い立ってから、<span class="accent">一本目</span>まで。</h2>
        <p>新しい蔵はどうやって生まれるのか。収録蔵の歩みをたどると、いくつか共通する道筋が見えてくる。</p>
        <p>多くの造り手は、まず<strong>どこかで酒造りを学ぶ</strong>。既存の酒蔵で働く人もいれば、醸造を学べる学校に通う人、先行するクラフトサケの蔵で修業する人もいる。実際、先発の蔵で経験を積んだ人が独立して次の蔵を立ち上げる——という連鎖が、この数年で起きている。<strong>ジャンルそのものが人を育てはじめている</strong>ということだ。</p>
        <p>次が<strong>免許と場所</strong>。「その他の醸造酒」の免許を取り、設備を置ける物件を探す。ここで自治体が関わる例もある。福岡県福智町のように<strong>醸造者を公募した町</strong>があり、ふるさと納税の返礼品として販路が用意される例もある。<strong>酒蔵の誘致を地域おこしに結びつける動きが出てきている</strong>。</p>
        <p>設備が整うまでのあいだ、<strong>既存の蔵に委託して醸す</strong>造り手もいる。京都の<a href="../brewery/linne.html">LINNÉ</a>は複数の蔵に委託して銘柄を世に出し、新潟の<a href="../brewery/iyasaka.html">弥栄醸造</a>も阿部酒造への委託から始まった。大阪の<a href="../brewery/adachi-noujo.html">足立農醸</a>の「KOYOI」も委託醸造だ。<strong>回り道に見えて、資金と経験の両方を確保できる現実的な進め方</strong>である。</p>
        <p>そして一本目が出る。多くの場合、それは<strong>蔵の店頭と公式オンラインショップだけ</strong>で売られる。ここから評判が広がり、取扱う酒販店が増え、やがて通販モールにも並ぶようになる。<strong>saketto に載っている蔵は、みなこの道を通ってきた</strong>。</p>
        <p>この道のりを知っていると、<strong>新しい蔵の酒が「どこにも売っていない」理由</strong>も腑に落ちる。まだ流通に乗る段階まで来ていないだけで、隠しているわけでも品薄商法でもない。公式サイトを直接訪ねれば、たいてい買える。<strong>できたばかりの蔵ほど、造り手との距離が近い</strong>——それは新しさの不便ではなく、この時期にしか味わえない特権かもしれない。</p>
        <p>そしてこの近さは、長くは続かない。蔵が育ち、流通が広がれば、造り手は忙しくなる。いま公式サイトのメッセージに直接返信をくれる造り手も、数年後には同じようにはいかないだろう。<strong>ジャンルが立ち上がっていく途中に居合わせている</strong>——飲み手にとって、それ自体がひとつの体験だと言っていい。</p>
        <p>もっとも、すべての蔵が続くとは限らない。小さな醸造所の経営は楽ではなく、設備投資も人手も重くのしかかる。<strong>いま飲める一本が、来年も同じように買えるとは限らない</strong>。だからこそ、気になる蔵があるなら早めに一本。飲むことが、いちばん直接的な応援になる。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("08", "OUTBOUND / 国境を越えはじめた")}
      <div class="prose">
        <h2 class="sub-h">日本で生まれて、<span class="accent">世界へ</span>。</h2>
        <p>新しい蔵の動きは、国内だけにとどまっていない。<strong>立ち上がってまだ数年の蔵が、すでに海を渡っている</strong>。これは従来の酒蔵の歩みからすると、異例の速さだ。</p>
        <p>福島・小高の<a href="../brewery/haccoba.html">haccoba</a>は2025年に欧米への進出を開始した。米国ポートランドの「Sunflower Sake」、アムステルダムの「Restaurant Flore」、そしてベルリンの「Enter Sake Berlin」——アジア圏でもタイ、香港、シンガポール、台湾へ輸出している。<strong>創業2021年の蔵が、四年ほどで欧米の食卓に並んでいる</strong>。</p>
        <p>福岡の<a href="../brewery/librom.html">LIBROM</a>はさらに踏み込んだ。2023年にイタリア法人「LIBROM ITALY」を設立し、バルバレスコ地区で<strong>現地の米を使ったテスト醸造</strong>に取り組んでいる。日本の酒を輸出するのではなく、<strong>その土地の米でその土地の酒を醸す</strong>——ワインの産地でクラフトサケを造るという発想は、この酒が「日本の酒」という枠すら越えはじめていることを示している。</p>
        <p>岩手・遠野の<a href="../brewery/nondo.html">nondo</a>のように、世界最高峰のレストランに採用される例もある。そして新潟・佐渡の<a href="../brewery/sakenova.html">SAKENOVA BREWERY</a>は2025年、日本アカデミー賞のアフターパーティーで唯一の日本酒ブランドとして提供された。約500名が口にした計算になる。</p>
        <p><strong>なぜこれほど早く外へ出られるのか</strong>。ひとつには、クラフトサケが「日本酒」という既存カテゴリの外にあるからだろう。海外の飲み手にとって、これは比較対象のない新しい飲みものだ。ホップや果実を使った造りは、ワインやクラフトビールに親しんだ舌にも入りやすい。<strong>国内で「規格外」だったことが、国外では「新しい」に変わる</strong>——制度の外に出た酒が、そのまま国境の外へ出ていく構図になっている。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("09", "NEXT / これから")}
      <div class="prose">
        <h2 class="sub-h">まだ、<span class="accent">増えつづける</span>。</h2>
        <p>2026年に入っても新しい蔵の名前は増えている。茨城の<a href="../brewery/tsuchiura.html">土浦醸造</a>のように準備段階の蔵もあり、<strong>この記事が古びるのは速い</strong>。saketto はそのつど一次ソースを確認して収録を更新している。</p>
        <p>新しい蔵の酒は、<strong>まず蔵の公式オンラインショップや店頭に出る</strong>ことが多い。通販モールに並ぶのは、そのあとになる。気になる蔵ができたら、公式サイトとSNSを直接追うのがいちばん早い。買い方のコツは<a href="doko-de-kaeru.html">どこで買える？</a>にまとめている。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("10", "FAQ / よくある質問")}
      <div class="prose">
        <h2 class="sub-h tight">クラフトサケの蔵は、全国に<span class="accent">いくつ</span>ありますか？</h2>
        <p>明確な統計はありません。協会加盟蔵のほか、加盟せずに醸す蔵、大手酒造の実験ブランド、準備中の蔵まで含めると、線の引き方で数が変わるためです。saketto では一次ソースで確認できた蔵を収録しており、現在25蔵を掲載しています。</p>
        <h2 class="sub-h tight">新しい蔵の酒は、<span class="accent">品質</span>が心配ではないですか？</h2>
        <p>多くの造り手は、既存の酒蔵での修業歴や醸造の専門教育を経て独立しています。また設備が小さいぶん一仕込みごとに細かく設計を変えられるため、むしろ攻めた造りに挑戦しやすいという利点があります。</p>
        <h2 class="sub-h tight">どの蔵から<span class="accent">飲めば</span>いいですか？</h2>
        <p>まずは入手しやすい第一世代の定番から入り、気に入った方向性（ホップ系・果実系・どぶろく系）を決めてから新しい蔵へ広げるのがおすすめです。タイプ別の入口は<a href="osusume.html">おすすめ12選</a>にまとめています。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("11", "READ ON / もっと知る")}
      <div class="prose">
        <p>新しい蔵が生まれる背景を知ると、一本の酒の後ろにある選択が見えてくる。ジャンルの成り立ちそのものも、あわせてどうぞ。</p>
        <div class="callout">
          <div class="callout__label">楽しむ前に</div>
          <p><strong>20歳未満の飲酒は法律で禁じられています。</strong>　飲酒運転は法律で禁止されています。妊娠中・授乳期の飲酒はお控えください。適量を守り、自分のペースでお楽しみください。</p>
        </div>
        <div class="readmore">
          <a href="craftsake-towa.html">
            <div class="readmore__k">あわせて読む</div>
            <div class="readmore__t">クラフトサケとは</div>
          </a>
          <a href="doko-de-kaeru.html">
            <div class="readmore__k">CHOOSE</div>
            <div class="readmore__t">どこで買える？</div>
          </a>
        </div>
      </div>
    </section>

  </div>
"""
    html = page_head("いま生まれている、新しい蔵 — クラフトサケ醸造所が増えている理由",
                     "駅構内、商店街、団地、離島。これまで酒蔵がなかった場所にクラフトサケの醸造所が次々と生まれている。saketto収録25蔵の開業年から、免許制度・立地・協会という3つの視点でいま何が起きているのかを読み解きます。",
                     "/guide/new-breweries.html", "article")
    html += masthead(article_masthead_label("new-breweries"), "A Field Guide")
    html += hero(
        article_eyebrow("new-breweries"),
        '新しい蔵が、<br><span class="accent">街の中</span>に立つ。',
        "駅のエキナカ、商店街のアーケード、団地の一角。酒蔵の常識が、この5年で書き換わった。")
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
    (OUT_DIR / "kioke.html").write_text(build_kioke(), encoding="utf-8")
    (OUT_DIR / "gift.html").write_text(build_gift(), encoding="utf-8")
    (OUT_DIR / "hanamoto.html").write_text(build_hanamoto(), encoding="utf-8")
    (OUT_DIR / "doburoku.html").write_text(build_doburoku(), encoding="utf-8")
    (OUT_DIR / "doko-de-kaeru.html").write_text(build_doko_de_kaeru(), encoding="utf-8")
    (OUT_DIR / "zenkoji.html").write_text(build_zenkoji(), encoding="utf-8")
    (OUT_DIR / "new-breweries.html").write_text(build_new_breweries(), encoding="utf-8")
    print(f"OK ガイド生成: guide/index.html（一覧）＋ 記事{len(ARTICLES)}本")


if __name__ == "__main__":
    main()

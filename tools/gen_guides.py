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
from site_common import head_extra, seo_head, breadcrumb, website_node, SITE_URL, pr_notice
from breweries_brands import BRANDS          # おすすめ記事：スペックを一次ソースDBから直接引く
from breweries_master import by_slug
from bottle_images import thumb_tag
from moshimo_link import resolve_rakuten, resolve_amazon
from gen_sample_v2 import RAKUTEN_ENABLED, AMAZON_ENABLED

REPO_ROOT = Path(__file__).resolve().parent.parent  # saketto_repo/
OUT_DIR = REPO_ROOT / "guide"

# 読みものの構造化データ用 日付（ISO8601）。内容を大きく更新したら dateModified を更新する。
# 記事中の統計値。直書きすると銘柄追加のたびに実データとズレるので必ずここから引く
from site_stats import STATS as S, buy_stats
import furusato_data as FD

B = buy_stats() or {"buyable": 0, "not_buyable": 0, "breweries_without_shop": 0}


def _brewery_link(slug, with_pref=False):
    import breweries_master as _bm
    import re as _re
    b = _bm.by_slug(slug)
    pref = _re.sub(r"[都府県]$", "", b["prefecture"]) + "の" if with_pref else ""
    return f'{pref}<a href="../brewery/{slug}.html">{b["name"]}</a>'


def _no_shop_examples(n=5):
    """通販モールで取扱いを確認できなかった蔵（購入ボタンが1つも無い蔵）を生成済みページから挙げる"""
    import breweries_master as _bm
    order = [b["slug"] for b in _bm.BREWERIES]
    slugs = sorted(B.get("without_shop_slugs") or [], key=order.index)[:n]
    return "、".join(_brewery_link(s, True) for s in slugs)


def _furusato_gift_summary():
    """ギフト記事のふるさと納税の段落。furusato_data から、いま申し込める返礼品のある蔵と最少額を出す。
    （以前は本文に直書きで、終了した返礼品や古い寄附額が残っていた。2026-10-11）"""
    import breweries_master as _bm
    from furusato_data import FURUSATO as _F
    rows = []
    for b in _bm.BREWERIES:
        d = _F.get(b["slug"])
        if not d:
            continue
        live = [i for i in d["items"] if i.get("accepting", True) and i.get("yen")]
        if not live:
            continue
        lo = min(live, key=lambda i: i["yen"])
        rows.append(f'<a href="../brewery/{b["slug"]}.html">{b["name"]}</a>'
                    f'（{d.get("city", "")}・{lo["yen"]:,}円から・{lo["brand"]}）')
    return (f"saketto が各ポータルの返礼品ページで確認した範囲では、いま申し込める返礼品があるのは"
            f"<strong>{len(rows)}蔵</strong>です。" + "、".join(rows) + "。")


def _many_shop_examples(n=3):
    """購入ボタンのある銘柄が多い蔵の上位"""
    cnt = B.get("buyable_by_brewery") or {}
    top = sorted(cnt, key=lambda s: -cnt[s])[:n]
    links = [_brewery_link(s) for s in top]
    if len(links) < 2:
        return "".join(links)
    return links[0] + "や" + "、".join(links[1:])
if not B["buyable"]:
    raise SystemExit(
        "銘柄ページが未生成のため購入導線の統計を計算できません。\n"
        "  先に python tools/gen_brand_pages_v2.py を実行してください。")

ARTICLE_PUBLISHED = "2026-05-31"
ARTICLE_MODIFIED = "2026-06-03"

# 記事ごとの公開日の上書き（あとから追加した記事はここに入れる）。
# 全記事で同じ日付を配信すると、新しい記事も旧日付で公開されたとGoogleに伝わるため。
ARTICLE_DATES = {
    "/guide/furusato.html": ("2026-09-02", "2026-09-02"),
    "/guide/craftsake-towa.html": ("2026-05-31", "2026-10-29"),
    "/guide/doburoku.html": ("2026-08-10", "2026-10-29"),
    "/guide/doko-de-kaeru.html": ("2026-08-10", "2026-08-10"),
    "/guide/zenkoji.html": ("2026-08-10", "2026-10-29"),
    "/guide/kioke.html": ("2026-05-31", "2026-10-29"),
    "/guide/new-breweries.html": ("2026-08-10", "2026-08-10"),
    "/guide/nomeru-kura.html": ("2026-10-28", "2026-10-28"),  # 10-28 夜に解説型へ全面改稿
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
.temp-table tr.grp td { background:var(--bg-alt); font-family:'Shippori Mincho',serif; font-weight: 700; color:var(--ink); letter-spacing:.04em; }
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
.pick { display:grid; grid-template-columns:auto 1fr 96px; gap:1.1rem 1.3rem; max-width:820px; padding:1.5rem 0; border-bottom:1px solid var(--line-soft); }
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
/* 銘柄のボトル（画像の無い銘柄は同じ大きさの線画） */
.pick__fig { display:block; align-self:start; }
.pick__thumb { display:block; width:96px; height:206px; background:var(--bg-alt); }
.pick__thumb img { display:block; width:100%; height:100%; object-fit:cover; }
.pick__thumb--none { background:var(--bg-alt) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 90' fill='none' stroke='%23D9CDB8' stroke-width='1.6' stroke-linejoin='round'%3E%3Cpath d='M16 4h8v5h-8z'/%3E%3Cpath d='M16.5 9v13c0 4-8.5 8-8.5 16v44a4 4 0 0 0 4 4h16a4 4 0 0 0 4-4V38c0-8-8.5-12-8.5-16V9'/%3E%3C/svg%3E") center/34px auto no-repeat; }
.pick-imgnote { font-family:'Zen Kaku Gothic Antique',sans-serif; font-size:.78rem; color:var(--ink-mute); max-width:820px; margin:.2rem 0 0; }
@media (max-width:600px){ .pick { grid-template-columns:1fr 64px; gap:.2rem .9rem; } .pick__no { font-size:1.4rem; grid-column:1/-1; }
  .pick__thumb { width:64px; height:137px; } .pick__thumb--none { background-size:24px auto; } }

/* スペック比較表 */
.cmp-wrap { max-width:820px; overflow-x:auto; margin:1rem 0 1rem; }
.cmp.cmp--compare td { white-space:normal; min-width:8rem; line-height:1.7; vertical-align:top; }
.cmp.cmp--compare td.nm { min-width:6.5rem; font-weight:700; }
.answer-list { list-style:none; padding:0; margin:.8rem 0 0; max-width:720px; }
.answer-list li { padding:.6rem 0; border-top:1px solid var(--line-soft); line-height:1.85; }
.answer-list li:last-child { border-bottom:1px solid var(--line-soft); }
.answer-list strong { color:var(--accent); margin-right:.4rem; }
@media (max-width:600px){ .cmp.cmp--compare thead { display:none; } .cmp.cmp--compare, .cmp.cmp--compare tbody, .cmp.cmp--compare tr, .cmp.cmp--compare td { display:block; width:100%; } .cmp.cmp--compare tr { border-bottom:1px solid var(--line-soft); padding:.7rem 0; } .cmp.cmp--compare td { border:0; padding:.15rem 0; min-width:0; } .cmp.cmp--compare td.nm { font-size:1rem; padding-bottom:.3rem; } .cmp.cmp--compare td[data-label]::before { content:attr(data-label); display:inline-block; width:6.5em; font-family:'Zen Kaku Gothic Antique',sans-serif; font-size:.72rem; font-weight:700; letter-spacing:.04em; color:var(--accent); } }
.cmp { width:100%; border-collapse:collapse; font-size:.84rem; white-space:nowrap; }
.cmp th, .cmp td { text-align:left; padding:.6rem .8rem; border-bottom:1px solid var(--line-soft); }
.cmp thead th { font-family:'Zen Kaku Gothic Antique',sans-serif; font-weight:700; letter-spacing:.06em; font-size:.72rem; color:var(--ink); border-bottom:1px solid var(--line); }
.cmp td.nm { font-family:'Shippori Mincho',serif; color:var(--ink); white-space:normal; min-width:11rem; }
.cmp td.p { font-family:'Zen Kaku Gothic Antique',sans-serif; color:var(--accent); font-weight:700; }
.cmp a { color:inherit; text-decoration:none; border-bottom:1px solid var(--line-soft); }
/* 飲める醸造所：蔵ごとのカード（全カード同じ枠線） */
.vcard { max-width:820px; border:1px solid var(--line); background:var(--bg); padding:1.3rem 1.5rem 1.1rem; margin:0 0 1.1rem; }
.vcard__head { display:flex; flex-wrap:wrap; align-items:baseline; gap:.3rem .9rem; margin-bottom:.8rem; }
.vcard__name { font-family:'Shippori Mincho',serif; font-weight:700; font-size:1.2rem; color:var(--ink); text-decoration:none; }
.vcard__name:hover { color:var(--accent); }
.vcard__h { margin:0; font-size:inherit; font-weight:inherit; }
.vcard__story p { margin:0 0 .8rem; font-size:.95rem; line-height:1.95; color:var(--ink-soft); }
.vcard__story { margin-bottom:.4rem; }
.vcard dl { border-top:1px solid var(--line-soft); padding-top:.75rem; }
h3.sub-h { font-size:1.08rem; }
.vcard__pref { font-family:'Zen Kaku Gothic Antique',sans-serif; font-size:.8rem; color:var(--ink-mute); letter-spacing:.04em; }
.vcard dl { display:grid; grid-template-columns:7.5em 1fr; gap:.45rem 1rem; margin:0; }
.vcard dt { font-family:'Zen Kaku Gothic Antique',sans-serif; font-weight:700; font-size:.74rem; letter-spacing:.08em; color:var(--accent); padding-top:.2rem; }
.vcard dd { margin:0; font-size:.93rem; color:var(--ink-soft); line-height:1.8; }
.vcard__links { display:flex; flex-wrap:wrap; gap:.4rem 1.2rem; margin-top:.8rem; font-size:.86rem; }
.vcard__links a { color:var(--accent); text-decoration:none; border-bottom:1px solid var(--line-soft); }
@media (max-width:600px){ .cmp--visit .pf { display:none; } .cmp--visit th, .cmp--visit td { padding:.55rem .45rem; } .cmp--visit td.nm { min-width:0; } .cmp--visit th:not(:first-child), .cmp--visit td:not(.nm) { white-space:nowrap; font-size:.78rem; } .vcard { padding:1.1rem 1.1rem 1rem; } .vcard dl { grid-template-columns:1fr; gap:.1rem; } .vcard dd { margin-bottom:.5rem; } }
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
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@400;500&family=Cormorant+Garamond:ital,wght@0,400;1,400&display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@400;500&family=Cormorant+Garamond:ital,wght@0,400;1,400&display=swap" media="print" onload="this.media=&#39;all&#39;">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@400;500&family=Cormorant+Garamond:ital,wght@0,400;1,400&display=swap"></noscript>
<style>{BASE_CSS}{EXTRA_CSS}</style>
{head_extra()}
</head>
<body>
<main>
"""


def article_crumbs(slug):
    """現在地パンくず。brand/breweryページの .crumbs と同じ見た目・区切り（／）で統一。"""
    a, _ = article_meta(slug)
    return f"""
  <nav class="crumbs" aria-label="現在地">
    <a href="../index.html">トップ</a><span class="crumbs__sep">／</span>
    <a href="../guide/">読みもの</a><span class="crumbs__sep">／</span>
    <span aria-current="page">{a["title"]}</span>
  </nav>"""


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
      <a href="../furusato/">ふるさと納税</a>
      <a href="../awards/">受賞</a>
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
        <a href="/contact.html">お問い合わせ</a><span class="colophon__sep">／</span>
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


def term_grid(items):
    """items: list of (name, en, desc)"""
    return '<div class="term-grid">' + "".join(
        f'<div class="term"><div class="term__name">{n}<span class="en">{en}</span></div>'
        f'<div class="term__desc">{d}</div></div>' for n, en, d in items) + "</div>"


# 協会加盟蔵（saketto収録分）。直書きすると加盟蔵の追加時に記事が古いまま残るので
# breweries_master の association フラグ（一次ソース確認済み）から導出する
from breweries_master import BREWERIES as _BREWERIES
KURA = {b["slug"]: b["name"] for b in _BREWERIES if b.get("association")}


def kura_link(slug):
    return f'<a href="../brewery/{slug}.html">{KURA.get(slug) or by_slug(slug)["name"]}</a>'


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
        "summary": "日本酒の技術で米を醸しながら、日本酒には使えない副原料や工程を取り入れた新しいジャンルの酒。日本酒との違いを表で整理し、ラベルの見分け方、7つの種類、なぜ増えているのかまで。",
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
        "summary": "金属のタンクではなく、杉の木桶で発酵させる造り。タンクとの違い、樽酒との違い、昭和に消えかけて戻ってきた歴史、木桶に棲む微生物の話、saketto で買える木桶の酒まで。",
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
        "summary": "白く濁った米の酒、どぶろく。にごり酒・甘酒・マッコリとはどう違うのか。酒税法や公的資料をもとに表で整理し、ラベルの見分け方、味わい、造り方、選び方・飲み方まで。",
    },
    {
        "slug": "doko-de-kaeru",
        "category": "choose",
        "eyebrow_en": "WHERE TO BUY",
        "title": "クラフトサケはどこで買える？",
        "summary": "少量生産のクラフトサケは、探し方にコツがいる。蔵の公式オンラインショップ、通販モール、ふるさと納税、店頭限定——4つの入口の違いと、要冷蔵・季節限定という壁の越え方を、収録蔵の公式情報をもとに。",
    },
    {
        "slug": "furusato",
        "category": "choose",
        "eyebrow_en": "FURUSATO TAX",
        "title": "ふるさと納税でクラフトサケを手に入れる",
        "summary": f"寄附で蔵の地元を応援しながら、返礼品としてクラフトサケを受け取る。制度のきほんと申し込みの流れ、saketto が一次ソースで確認した{len(FD.all_confirmed_slugs())}蔵の返礼品、品切れ・要冷蔵の注意点まで。",
    },
    {
        "slug": "zenkoji",
        "category": "deep",
        "eyebrow_en": "FULL KOJI",
        "title": "全麹仕込み（全麹酒）とは",
        "summary": "仕込む米をすべて麹にする、全麹仕込み。ふつうの日本酒との違いを表で整理し、麹99%なら日本酒、100%なら「その他の醸造酒」になる理由、味、泡盛との関係まで。",
    },
    {
        "slug": "nomeru-kura",
        "category": "choose",
        "eyebrow_en": "VISIT THE BREWERY",
        "title": "クラフトサケが飲める醸造所",
        "summary": "醸造所で飲むと何が違うのか。搾りたての生の酒、そこでしか買えない一本、ガラス越しの発酵。併設バーやパブ、見学ができる蔵を、目的別の選び方と地域ごとの紹介で。一人・子ども連れ・車で行くときの注意も、各蔵の公式情報をもとに。",
    },
    {
        "slug": "new-breweries",
        "category": "deep",
        "eyebrow_en": "NEW BREWERIES",
        "title": "いま生まれている、新しい蔵",
        "summary": f"駅のホーム、商店街のアーケード、島、団地の一角。2024年以降に生まれたクラフトサケの蔵は、これまで酒蔵がなかった場所に立つ。saketto収録{S['breweries']}蔵の開業年から、いま何が起きているのかを読む。",
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
        <h2 class="section-meta__label" style="margin:0">{cat['ja']}</h2>
        <span class="section-meta__rule"></span>
      </div>
      <p class="cat-lead">{cat['desc']}</p>
      <div class="guide-list">
{cards}      </div>
    </section>
"""
    body = f"""
  <div class="article">
{blocks}    <p class="guide-foot">クラフトサケの世界を、知って・選んで・深く味わうための読みもの。基礎から製法まで{len(ARTICLES)}本を揃えています。まず一本に出会いたい方は、<a href="../index.html">トップ</a>の4つの軸からどうぞ。</p>
  </div>
"""
    html = page_head("読みもの — クラフトサケのガイド",
                     "クラフトサケを知り、選び、楽しむためのガイド記事の一覧。基礎を知る・選ぶ・深く味わうの分類で、米から生まれた自由な酒を味わうための読みものをまとめています。")
    html += masthead("READING — 読みもの", "A Field Guide")
    html += """
  <nav class="crumbs" aria-label="現在地">
    <a href="../index.html">トップ</a><span class="crumbs__sep">／</span>
    <span aria-current="page">読みもの</span>
  </nav>"""
    html += hero(
        "READING — 読みもの",
        'クラフトサケを、<span class="accent">もっと知る</span>。',
        "そもそもクラフトサケとは何か。どう飲めば、もっとおいしいのか。基礎を知り、選び、深く味わう——saketto のガイド記事を、分類でまとめています。")
    html += body
    html += footer()
    return html


# ────────────── 記事①：クラフトサケとは ──────────────

def build_towa():
    # 🔴 嘘ゼロ：定義・制度は一次資料から（2026-10-29 確認）
    #   協会の定義・設立日・目的・会員一覧・商標の注記：https://craftsakebreweries.com/
    #   設立メンバー6社・「自由を、醸そう。」：協会の Makuake https://www.makuake.com/project/craft_sake_breweries/
    #   酒税法 第3条第7号（清酒）・第19号（その他の醸造酒）・第7条第2項（最低製造数量）・第10条第11号（需給調整）
    #     https://laws.e-gov.go.jp/law/328AC0000000006
    #   品目表示の義務：酒類業組合法 第86条の5 ／「日本酒」は地理的表示を満たす清酒の例外表示：
    #     国税庁「酒類の表示に関する説明事項」https://www.nta.go.jp/taxes/sake/qa/11/pdf/012.pdf
    #   清酒は「長年、新規参入が制限されている」・輸出用清酒製造免許（令和3年4月1日から申請受付）：
    #     税務大学校論叢107号 https://www.nta.go.jp/about/organization/ntc/kenkyu/ronsou/107/01/index.htm
    #   どぶろく特区：構造改革特別区域法 第25条 https://laws.e-gov.go.jp/law/414AC0000000189
    #   需給調整の対象は清酒・合成清酒・焼酎・みりん等で、その他の醸造酒は対象外：国税庁 法令解釈通達 第10条第11号関係 https://www.nta.go.jp/law/tsutatsu/kihon/sake/2-08.htm
    #   SAKENOVA の輸出用清酒＋その他の醸造酒：日本経済新聞 https://www.nikkei.com/article/DGXZQOCC232GM0T21C24A0000000/
    #   800 米＝品目 清酒・800 蕎麦＝品目 雑酒：SAKETIMES 掲載の公式リリース https://jp.sake-times.com/special/press/p_202504_linne-sales-start
    #   「クラフト日本酒」：協会・国税庁・日本酒造組合中央会のどれにも定義なし（書かない）
    #   書かないこと：協会の「10年で47都道府県」目標（公式の文言が見つからない）／「クラフトサケは生酒が多い」の一般論（DBの数字だけ）
    from gen_axes_pages import GENRES as _GENRES, brands_in_genre as _in_genre, BRAND_DETAILS as _DET
    from breweries_brands import BRANDS as _BR, is_alias as _is_alias

    def _ratio_ja(n, d):  # 統計は曖昧化して書く（○割ほど）
        t = round(n / d * 10)
        return "およそ半数" if t == 5 else ("ほぼすべて" if t >= 10 else f"{t}割ほど")

    # ジャンル別の銘柄数（ジャンル一覧ページと同じ判定）
    g_n = {}
    for k, *_ in _GENRES:
        g_n[k] = sum(len(_in_genre(b, k)) for b in _BREWERIES)

    # 火入れの有無を公開している銘柄のうち、火入れしていない（生）の割合
    _past = [(_DET.get(s) or [{}] * len(bs))[i].get("pasteurized") if i < len(_DET.get(s) or []) else None
             for s, bs in _BR.items() for i, _b in enumerate(bs) if not _is_alias(s, i)]
    _known = [p for p in _past if p is not None]
    nama_ja = _ratio_ja(sum(1 for p in _known if p is False), len(_known))

    rice_only_ja = _ratio_ja(S["rice_only"], S["brands"] - S["undisclosed"])
    n_1800 = sum(1 for s, bs in _BR.items() for i, b in enumerate(bs) if not _is_alias(s, i) and b.get("volume_ml") == 1800)
    new_ja = "半数を超える" if S["since2024"] * 2 > S["breweries"] else _ratio_ja(S["since2024"], S["breweries"]) + "を占める"
    members = [b for b in _BREWERIES if b.get("association")]
    kura_row = '<div class="kura-links">' + "".join(kura_link(b["slug"]) for b in members) + "</div>"

    cmp_rows = [
        ("原料", "米・米麹・水。加えてよい副原料は政令で決められたものだけで、重さは米の半分まで", "米・米麹・水に、ホップ・果実・ハーブなどを<strong>自由に</strong>加えられる（何も加えない銘柄もある）"),
        ("こすか", "<strong>必ずこす</strong>", "こすものも、<strong>こさないもの</strong>（どぶろく）もある"),
        ("ラベルの品目", "清酒（条件を満たせば「日本酒」）", "多くは<strong>「その他の醸造酒」</strong>。造りによってはリキュール・発泡酒・雑酒など"),
        ("度数", "22度未満", f"その他の醸造酒は20度未満（saketto 収録の銘柄で{S['abv_min']:g}〜{S['abv_max']:g}度ほど）"),
        ("製造免許", "新規の免許はほとんど出ない。最低でも年<strong>60kL</strong>造る必要がある", "「その他の醸造酒」の免許で造る。最低製造数量は年<strong>6kL</strong>"),
    ]
    cmp_html = "".join(f'            <tr><td class="nm">{a}</td><td data-label="日本酒（清酒）">{b}</td><td data-label="クラフトサケ">{c}</td></tr>\n'
                       for a, b, c in cmp_rows)

    type_rows = [
        ("hop-sake", "ホップサケ", "ビールの香りづけに使うホップを加える", "柑橘やハーブを思わせる香りと、軽い苦み"),
        ("fruit-sake", "果実サケ", "いちご・洋梨・りんごなどの果実や果汁を一緒に醸す", "果実の香りと甘酸っぱさ。ワインに近い印象のものも"),
        ("doburoku", "古典どぶろく", "副原料を使わず、米と米麹だけで、こさずに仕上げる", "米の甘みと旨み、乳酸のような酸。とろりと濃い"),
        ("tea-herb-sake", "茶葉・ハーブサケ", "茶葉、山椒、黒文字、紫蘇などを加える", "お茶やハーブ、スパイスの香り"),
        ("full-koji", "全麹酒", "仕込む米をすべて麹にする", "酸や旨みの濃い濃醇な味になりやすいとされる。軽やかなものもある"),
        ("kioke", "木桶仕込み", "金属のタンクではなく、木の桶で発酵させる", "蔵ごとに個性が分かれる。saketto 収録では生酛・水もとと組む銘柄が多い"),
        ("foreign-koji", "異素材麹", "大麦・蕎麦・芋など、米以外の麹を使う", "麹の素材によって、香ばしさや穀物の風味が出る"),
    ]
    types_html = "".join(
        f'            <tr><td class="nm"><a href="../genre/#g-{k}">{jp}</a></td><td data-label="どんな酒か">{what}</td>'
        f'<td data-label="味の方向">{taste}</td><td data-label="収録">{g_n.get(k, 0)}銘柄</td></tr>\n'
        for k, jp, what, taste in type_rows if g_n.get(k))

    terms = term_grid([
        ("酒母（しゅぼ）", "SHUBO", "酵母を増やすための、いわば酒の種。乳酸を加えて造る速醸のほか、生酛・山廃・水もと（菩提酛）・花酛など、自然の乳酸菌や植物の力を借りる古い造りがある。"),
        ("花酛（はなもと）", "HANAMOTO", "ホップと同じ仲間のカラハナソウ（唐花草）の煎じ汁を使う、東北に伝わったどぶろくの酒母。haccoba が現代に再現した。"),
        ("水もと・菩提酛", "MIZUMOTO", "生米を水に漬けて乳酸発酵させた「そやし水」を仕込みに使う酒母。室町時代に奈良の正暦寺で生まれたとされる。"),
        ("生酛（きもと）", "KIMOTO", "自然界の乳酸菌を取り込んで乳酸をつくらせる、伝統的な酒母の造り方。手間と日数がかかる。"),
        ("白麹", "SHIRO-KOJI", "主に焼酎づくりに使われる麹。クエン酸を多くつくるので、酒にレモンのような酸味が出る。"),
        ("全麹", "ZEN-KOJI", "仕込みに使う米を、すべて（またはほぼすべて）麹にして醸す造り。麹100%だと清酒にはならず「その他の醸造酒」になる。"),
        ("木桶仕込み", "KIOKE", "木の桶を発酵の容器に使う、昔ながらの仕込み。"),
        ("ドライホッピング", "DRY HOPPING", "ビールづくりの技法。発酵の後半や発酵後にホップを加え、苦みより香りを引き出す。"),
    ])

    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "WHAT IS / クラフトサケとは")}
      <div class="prose">
        <p class="lead">クラフトサケとは、<span class="accent">日本酒の造り方</span>をもとに米で醸しながら、日本酒には法律上使えない副原料や工程を取り入れた、新しいジャンルの酒。ホップや果実を加えた酒も、もろみをこさない<a href="doburoku.html">どぶろく</a>も含まれる。</p>
        <p>この呼び名を掲げるクラフトサケブリュワリー協会は、クラフトサケを「日本酒（清酒）の製造技術をベースとして、お米を原料としながら従来の『日本酒』では法的に採用できないプロセスを取り入れた、新しいジャンルのお酒」と定義し、「例えば、『どぶろく』もクラフトサケのひとつ」と書いている。つまり<strong>米の酒であることは日本酒と同じで、日本酒のルールの外で造っているところが違う</strong>。</p>
        <p>はじめて聞いた人がまず気になりそうなことに、先に答えておく。</p>
        <ul class="answer-list">
          <li><strong>日本酒なの？</strong>　法律上は日本酒（清酒）ではない。ラベルの品目は多くが「その他の醸造酒」になる。</li>
          <li><strong>どんな味？</strong>　加える素材しだいで、ビールのような香りのものから、ワインのような甘酸っぱいもの、米だけの濃いどぶろくまで幅が広い。</li>
          <li><strong>なぜ日本酒にしない？</strong>　日本酒の製造免許は新しく取るのがとても難しく、「その他の醸造酒」の免許なら小さな規模でも始められる。そこで日本酒の外で造る道を選んだ造り手たちが、2022年に協会をつくった。</li>
        </ul>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("02", "COMPARE / 日本酒との違い")}
      <div class="prose">
        <h2 class="sub-h">日本酒とクラフトサケの<span class="accent">違い</span>を表で。</h2>
        <p>原料も造り方の土台もほぼ同じで、違うのは<strong>「何を加えてよいか」「こすかどうか」</strong>と、その結果として決まる法律上の区分だ。味の上下ではない。</p>
      </div>
      <div class="cmp-wrap">
        <table class="cmp cmp--compare">
          <thead><tr><th>項目</th><th>日本酒（清酒）</th><th>クラフトサケ</th></tr></thead>
          <tbody>
{cmp_html}          </tbody>
        </table>
      </div>
      <p class="pick-imgnote">出典：酒税法 第3条・第7条・第10条、国税庁「酒類の表示に関する説明事項」、クラフトサケブリュワリー協会 公式サイト。</p>
      <div class="prose">
        <p>酒税法は清酒を「米、米こうじ及び水を原料として発酵させて、こしたもの」などと定め、アルコール分は22度未満としている。副原料を加えるときも、使える品目と量（米の重さの半分まで）が決まっている。<strong>ホップや果実を加える、もろみをこさない</strong>——どちらか一つでもすれば清酒の定義から外れ、多くは「その他の醸造酒」の区分に入る。</p>
      </div>
    </section>
{divider()}
    <section class="section" id="label">
{section_meta("03", "LABEL / ラベルで見分ける")}
      <div class="prose">
        <h2 class="sub-h">迷ったら、ラベルの<span class="accent">「品目」</span>を見る。</h2>
        <p>お酒のラベルには、酒税法の区分である<strong>「品目」</strong>を書くことが法律で義務づけられている（酒類業組合法 第86条の5）。見た目では区別しにくくても、ここを見ればどの区分の酒かがわかる。</p>
        <ul class="answer-list">
          <li><strong>清酒・日本酒</strong>　日本酒。国税庁の説明では、「日本酒」と書けるのは、地理的表示「日本酒」の条件を満たした清酒だけだ。</li>
          <li><strong>その他の醸造酒</strong>　クラフトサケの多くはここ。どぶろくもこの品目になる。</li>
          <li><strong>リキュール・発泡酒・雑酒 など</strong>　副原料の使い方や発泡性などによっては、別の品目になる。LINNÉ の「800 蕎麦」は、公式発表で品目が「雑酒」だ。</li>
        </ul>
        <p>店頭やネットでは「クラフト日本酒」という言葉も見かけるが、協会や国税庁、日本酒造組合中央会に、この言葉の定義は見当たらない。<strong>品目が「清酒」なら日本酒、「その他の醸造酒」ならクラフトサケやどぶろくの仲間</strong>と覚えておくと迷わない。</p>
      </div>
    </section>
{divider()}
    <section class="section" id="types">
{section_meta("04", "TYPES / どんな種類がある？")}
      <div class="prose">
        <h2 class="sub-h">加える素材と造り方で、<span class="accent">7つ</span>に分けてみる。</h2>
        <p>クラフトサケに公式の分類はない。saketto では、収録する{S['brands']}銘柄を「何を加えたか」「どう造ったか」で、次のジャンルに分けている。1つの銘柄が2つのジャンルに入ることもある（ホップを使った木桶仕込み、など）。</p>
      </div>
      <div class="cmp-wrap">
        <table class="cmp cmp--compare">
          <thead><tr><th>ジャンル</th><th>どんな酒か</th><th>味の方向</th><th>収録</th></tr></thead>
          <tbody>
{types_html}          </tbody>
        </table>
      </div>
      <div class="prose">
        <p>味の方向は、ジャンルの大まかな傾向にすぎない。同じジャンルでも蔵や銘柄によってかなり違うので、気になったら銘柄ページの公式の説明も読んでほしい。副原料ひとつから探したいときは<a href="../subingredients/">副原料から探す</a>が便利だ。</p>
        <p>なお、木桶仕込みや生酛は日本酒でも使われる造りで、それだけで日本酒の枠を外れるわけではない。saketto に収録した木桶仕込みの銘柄も、どれもこさないどぶろくや、副原料・麹だけで造る酒だ。</p>
        <p>副原料を使わない、米と米麹だけの銘柄も<strong>{rice_only_ja}</strong>ある（{S['rice_only']}銘柄）。その多くは、こさずに仕上げたどぶろくや、麹だけで造った酒で、<strong>造り方の違いで日本酒の定義から外れている</strong>。ただし saketto は蔵ごとに銘柄を収録しているので、白鶴 SAKE CRAFT の純米大吟醸や LINNÉ の「800 米」のように、品目が清酒（日本酒）の銘柄も一部含んでいる。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("05", "WHY / なぜ日本酒の外で造るのか")}
      <div class="prose">
        <h2 class="sub-h">日本酒の免許は、<span class="accent">新しくはほぼ取れない</span>。</h2>
        <p>造り手たちがわざわざ「日本酒ではない酒」を造る大きな理由は、<strong>製造免許</strong>にある。酒税法には、酒税を守るために需給の均衡を保つ必要があるときは製造免許を与えないことができる、という決まりがある（第10条第11号）。国税庁の税務大学校の論文も、清酒は「長年、新規参入が制限されている」と書いている。</p>
        <p>そのうえ清酒の免許には、年に<strong>60キロリットル</strong>以上造るという最低製造数量の基準がある。一升瓶（1.8リットル）にすると3万本を超える量で、小さく始めたい人にはまず届かない。いっぽう<strong>「その他の醸造酒」</strong>は需給調整の対象ではなく、最低製造数量も年<strong>6キロリットル</strong>だ。この免許なら、小さな醸造所でも酒造りを始められる。</p>
        <p>ほかの道もある。2021年4月からは<strong>輸出用の清酒</strong>に限って新しい製造免許の申請ができるようになったが、造った酒は国内では売れない。日本経済新聞によると、saketto 収録の{kura_link("sakenova")}は、この輸出用清酒の免許と「その他の醸造酒」の免許を組み合わせている。また<a href="doburoku.html#faq">どぶろく特区</a>は、特区内で農家民宿などを営む農業者が、自ら育てた米などを原料にこさない酒（濁酒）を造る場合に、最低製造数量の基準を外す特例だ（構造改革特別区域法 第25条）。原料は米・米こうじ・水と、麦など財務省令で決められたものに限られる。</p>
        <p>こうして「その他の醸造酒」の免許を取った造り手たちは、日本酒では使えない素材や工程を、逆に<strong>自分たちの個性</strong>として打ち出した。収録する{S['breweries']}蔵を見ても、創業（開業）が2024年以降の蔵が{new_ja}。まだ生まれて間もないジャンルだ。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("06", "THE ASSOCIATION / 協会と名前")}
      <div class="prose">
        <h2 class="sub-h">合言葉は、<span class="accent">「自由を、醸そう。」</span></h2>
        <p>2022年6月27日、6つの醸造所——WAKAZE・木花之醸造所・haccoba・LIBROM・稲とアガベ・LAGOON BREWERY——が<strong>クラフトサケブリュワリー協会</strong>を立ち上げた。テーマに掲げたのは「自由を、醸そう。」。公式サイトは目的を「クラフトサケの醸造所を増やす」「クラフトサケの知名度を高める」「日本酒とクラフトサケが共存できる未来をつくる」の3つとしている。<strong>日本酒と競うのではなく、並んで広がっていく</strong>ことを目指す団体だ。</p>
        <p>じつは<strong>「クラフトサケ」という名前は、株式会社モトックスの商標</strong>だ。協会の会員は同社の許諾を得てこの名前を使っていて、協会は、会員以外が名乗る「クラフトサケ」とは無関係だとしている。</p>
        <p>saketto は、協会の定義にあたる酒——日本酒の技術をもとに米で醸し、日本酒では使えない素材や工程を取り入れた酒——を、加盟しているかどうかにかかわらず、ひとつのジャンルとして集めている。各蔵のページには加盟・非加盟を明記した。収録蔵のうち、協会の会員一覧に載っているのは次の{len(members)}蔵だ。</p>
        {kura_row}
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("07", "BY THE NUMBERS / 数字で見る")}
      <div class="prose">
        <h2 class="sub-h">値段・度数・容量の<span class="accent">目安</span>。</h2>
        <p>収録する{S['brands']}銘柄の公式情報から、買う前に気になる数字をまとめた。</p>
        <ul class="answer-list">
          <li><strong>値段</strong>　価格がわかる{S['price_known']}銘柄の中央値は{S['price_median']:,}円。2,000円台がいちばん多く、5,000円を超えるものは一部だ。</li>
          <li><strong>度数</strong>　ノンアルコールの甘酒を除くと{S['abv_min']:g}〜{S['abv_max']:g}度で、真ん中は{S['abv_median']:g}度ほど。</li>
          <li><strong>容量</strong>　500mlと720ml（四合瓶）が中心。{'saketto の収録には一升瓶の銘柄はない' if n_1800 == 0 else '一升瓶は一部だけ'}。</li>
          <li><strong>火入れ</strong>　火入れの有無を公開している銘柄のうち、{nama_ja}が火入れをしていない生の酒だ。</li>
        </ul>
        <p>どこで買えるか、送料などを含めた買い方の違いは<a href="doko-de-kaeru.html">どこで買える？</a>にまとめている。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("08", "FIRST BOTTLE / 最初の一本")}
      <div class="prose">
        <h2 class="sub-h">ふだん好きなお酒から、<span class="accent">入り口</span>を選ぶ。</h2>
        <p>幅が広いぶん、最初の一本は「味の想像がつくもの」を選ぶと外しにくい。</p>
        <ul class="answer-list">
          <li><strong>ビールが好き</strong>　ホップサケから。香りの方向がビールに近い。</li>
          <li><strong>ワインが好き</strong>　果実サケや、酸のきいた銘柄から。</li>
          <li><strong>日本酒が好き</strong>　副原料を使わない古典どぶろくや全麹酒から。米の旨みの違いがわかりやすい。</li>
          <li><strong>お酒に強くない</strong>　度数が10度未満の銘柄を。ラベルや銘柄ページの度数を確かめてから選ぶといい。</li>
        </ul>
        <p>具体的な銘柄は<a href="osusume.html">おすすめ12選</a>で、タイプ別に選んでいる。生の酒が多いので、<strong>ラベルに「要冷蔵」とあれば、届いたらすぐ冷蔵庫へ</strong>。温度や割り方は<a href="nomikata.html">飲み方・楽しみ方</a>に詳しく書いた。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("09", "VOCABULARY / 醸造のことば")}
      <div class="prose">
        <p>クラフトサケのラベルや蔵の説明によく出てくることばをまとめた。造りの背景がわかると、同じ一杯でも見え方が変わる。</p>
      </div>
      {terms}
      <div class="prose">
        <p>とくに奥が深い<a href="hanamoto.html">花酛</a>・<a href="kioke.html">木桶仕込み</a>・<a href="zenkoji.html">全麹</a>は、それぞれ一本の記事で掘り下げている。</p>
      </div>
    </section>
{divider()}
    <section class="section" id="faq">
{section_meta("10", "FAQ / よくある質問")}
      <div class="prose">
        <h3 class="sub-h tight">クラフトサケは日本酒の一種ですか？</h3>
        <p>造り方の土台は日本酒と同じですが、法律上は日本酒（清酒）ではありません。副原料を加えたり、もろみをこさなかったりして清酒の定義から外れるため、多くは「その他の醸造酒」になります。ラベルの品目で確かめられます。</p>
        <h3 class="sub-h tight">「クラフト日本酒」とは違うのですか？</h3>
        <p>「クラフト日本酒」には、協会や国税庁などの公式な定義が見当たりません。品目が「清酒」の酒なら、どう呼ばれていても日本酒です。クラフトサケは、清酒の定義の外で造る米の酒を指します。</p>
        <h3 class="sub-h tight">「クラフトサケ」という名前は、誰でも使えるのですか？</h3>
        <p>「クラフトサケ」は株式会社モトックスの商標で、クラフトサケブリュワリー協会の会員は同社の許諾を得て使っています。協会は、会員以外が名乗る「クラフトサケ」とは無関係だとしています。</p>
        <h3 class="sub-h tight">甘いお酒ですか？</h3>
        <p>銘柄によります。甘いものもあれば、白麹のクエン酸で酸をきかせたものや、ホップの苦みが効いたものもあります。銘柄ページで公式の味の説明を確かめてください。</p>
        <h3 class="sub-h tight">度数はどのくらいですか？</h3>
        <p>saketto に収録している範囲では{S['abv_min']:g}〜{S['abv_max']:g}度ほどで、真ん中は{S['abv_median']:g}度前後です。「その他の醸造酒」は法律上20度未満と決まっています。</p>
        <h3 class="sub-h tight">保存は冷蔵庫ですか？</h3>
        <p>火入れをしていない生の酒が多いので、ラベルに「要冷蔵」とあれば冷蔵庫で立てて保存します。活性にごりなど発泡するものは、開けるときに吹き出すことがあるので、冷やしてからゆっくり開けてください。</p>
        <h3 class="sub-h tight">どこで買えますか？</h3>
        <p>蔵の公式オンラインショップ、通販モール、ふるさと納税、醸造所に併設した店が主な入口です。詳しくは<a href="doko-de-kaeru.html">どこで買える？</a>に、蔵で飲める場所は<a href="nomeru-kura.html">飲める醸造所</a>にまとめました。</p>
        <h3 class="sub-h tight">自分で造ってもいいですか？</h3>
        <p>できません。酒税法では、アルコール分1度以上の酒を免許なしで造ることは禁じられていて、罰則もあります。詳しくは<a href="doburoku.html#faq">どぶろくとは</a>のよくある質問で説明しています。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("11", "READ ON / 次に読む")}
      <div class="prose">
        <p>saketto では、{S['breweries']}の蔵と{S['brands']}の銘柄を、副原料・蔵・地域・ジャンルの4つの軸から探せる。</p>
        <div class="pill-links">
          <a href="../subingredients/">副原料から<span class="arr">→</span></a>
          <a href="../region/">地域から<span class="arr">→</span></a>
          <a href="../genre/">ジャンルから<span class="arr">→</span></a>
          <a href="../furusato/">ふるさと納税から<span class="arr">→</span></a>
        </div>
        <div class="callout">
          <div class="callout__label">楽しむ前に</div>
          <p><strong>20歳未満の飲酒は法律で禁じられています。</strong>　飲酒運転は法律で禁止されています。妊娠中・授乳期の飲酒はお控えください。適量を守り、自分のペースでお楽しみください。</p>
        </div>
        <div class="readmore">
          <a href="osusume.html">
            <div class="readmore__k">つづけて読む</div>
            <div class="readmore__t">クラフトサケ おすすめ12選</div>
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
    html = page_head("クラフトサケとは？日本酒との違い・種類・ラベルの見分け方",
                     "クラフトサケとは、日本酒の技術で米を醸しながら、日本酒には使えない副原料や工程を取り入れた新しいジャンルの酒。日本酒との違いを表で整理し、ラベルの「品目」での見分け方、7つの種類、なぜ増えているのか、値段・度数の目安まで解説します。",
                     "/guide/craftsake-towa.html", "article")
    html += masthead(article_masthead_label("craftsake-towa"), "A Field Guide")
    html += article_crumbs("craftsake-towa")
    html += hero(
        article_eyebrow("craftsake-towa"),
        'クラフトサケとは。<br>米から生まれた、<span class="accent">自由な酒</span>。',
        "日本酒の技術を土台に、あえて日本酒の枠の外へ。日本酒との違い、種類、ラベルの見分け方、なぜ増えているのかを、法律と公式情報からわかりやすく。")
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
        <p>収録銘柄にも、蔵自身が燗を勧める酒がある。足立農醸の<a href="../brand/adachi-noujo-3.html">MIYOI 燗酒専用酒</a>は、その名のとおり50〜60度の燗のために設計された一本。天郷醸造所の<a href="../brand/amanosato-2.html">在る 寒夜</a>や、でじま芳扇堂の<a href="../brand/dejima-hosendo-7.html">芳扇 友</a>も、冷酒から燗まで幅広い温度で楽しむことを蔵が勧めている。</p>
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
        <p>もっとも、どんな飲み方が合うかは、銘柄ごとに蔵がおすすめを示していることも多い。収録銘柄では、<a href="../brand/heiwa-kabutocho-3.html">平和どぶろく ホップ</a>が「しっかり冷やしてそのまま、またはロック」、ハッピー太郎醸造所の<a href="../brand/happy-taro-12.html">やまのかみさん 大原の赤紫蘇</a>が「ロック・ソーダ割りも可」、ぷくぷく醸造の<a href="../brand/pukupuku-2.html">KiKiKi Hopped Sour</a>が「キンキンに冷やして。ロックも可」と、蔵自身がアレンジを勧めている。割って楽しんでほしい酒、そのまま味わってほしい酒——迷ったら、<strong>蔵の推奨に従う</strong>のがいちばんだ。</p>
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
    html += article_crumbs("nomikata")
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
    "通好み・受賞蔵・特別な一本":
        "もう何本か飲んだ人へ。受賞した蔵の酒や、木桶仕込み・長期発酵といった手間のかかる造りから、特別な一本を選んだ。自分へのご褒美にも、贈り物にも。",
}

OSUSUME_PICKS = [
    ("はじめの一本に", "FIRST BOTTLE", "ine-to-agave", 0,
     "クラフトサケというジャンルそのものを切り拓いた、秋田・男鹿の稲とアガベ醸造所。その代名詞がこのCRAFTシリーズだ。テキーラの原料として知られるアガベのシロップを副原料に用い、白ブドウや白桃を思わせる柔らかな香りをまとう。全量を無肥料・無農薬の自然栽培米で仕込み、精米歩合は90%に統一——米をあえて削りすぎず、その個性をふくよかな旨みとして残す思想が貫かれている。「日本酒ともワインとも違う」第一印象を確かめる、まさに最初の一本。"),
    ("はじめの一本に", "FIRST BOTTLE", "haccoba", 0,
     "「自由を、醸そう。」を体現する先駆者、福島・小高のhaccoba。看板の“はなうたホップス”は、東北に伝わる幻のどぶろく製法「花酛（はなもと）」に、クラフトビールのドライホッピングを掛け合わせた一本だ。ホップ由来の華やかな香りと、米のやさしい甘みが軽やかに溶け合う。アルコールはロットにより11〜13%と程よく、するすると飲めてしまう親しみやすさ。クラフトサケの“はじまりの味”を知るなら、外せない蔵の代表作。"),
    ("はじめの一本に", "FIRST BOTTLE", "konohanano", 0,
     "浅草でどぶろくを醸す木花之醸造所の看板が、この“ハナグモリ”。本格純米のにごりに、瓶の中で生まれたシュワッとした微発泡が心地よく弾ける。米だけで仕込むやさしい甘酸っぱさは、にごり酒が初めての人にもすっと入っていく。バーを併設し、若い蔵人の“新しい修行の場”としても知られる蔵の顔。価格も手に取りやすく、微発泡のにごりから始めたい人にうってつけだ。"),
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
    ("通好み・受賞蔵・特別な一本", "CONNOISSEUR", "pukupuku", 4,
     "haccobaで醸造責任者を務めた造り手が独立して立ち上げた、福島・小高のぷくぷく醸造。全量“酵母無添加”の自然発酵に、ビールの技法を掛け合わせる蔵だ。この“#ODAKA”は、蔵に棲みつく蔵付き酵母を使い、木桶で醸したどぶろく。ICC SAKE AWARD 2025で蔵が優勝したとき、決勝で出したのがこの酒。発酵そのものの力強さを味わえる、通好みの一杯。"),
    ("通好み・受賞蔵・特別な一本", "CONNOISSEUR", "nondo", 0,
     "nondoの上級シリーズ「権化（ごんげ）」。水もと × 木桶 × 150日を超える長期発酵という、手間を惜しまない造りで生まれる。米糠まで活かし、柑橘を思わせる香りと軽やかな甘みをまとった、複雑で奥行きのある味わい。一本一本に蔵の思想が宿る、特別な酒だ。じっくり時間をかけて向き合いたい、贈り物にもふさわしい一本。"),
    ("通好み・受賞蔵・特別な一本", "CONNOISSEUR", "adachi-noujo", 0,
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


# おすすめ・ギフトの銘柄カードに添えるボトル画像の注記（ページに1回）
PICK_IMGNOTE = ('    <p class="pick-imgnote">ボトルの画像は、商品写真をもとに作り直したイメージです'
                '（線画は画像の無い銘柄）。</p>\n')


def build_osusume():
    cards = PICK_IMGNOTE
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
      <a class="pick__fig" href="../brand/{slug}-{idx}.html" tabindex="-1" aria-hidden="true">{thumb_tag(slug, idx, cls="pick__thumb")}</a>
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
        ("贈り物・特別な日に", "GIFT", "受賞した蔵の酒や、木桶・長期発酵の上級銘柄を。物語のある一本は記憶に残る。〈#ODAKA（ICC優勝蔵の決勝出品酒）／権化〉"),
        ("とにかく自由に開拓したい", "EXPLORE", "saketto の4軸（副原料・蔵・地域・ジャンル）から横断検索。気になった入り口から辿るのがいちばん。"),
    ])

    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "EDITORS' PICKS / 選び方の地図")}
      <div class="prose">
        <p class="lead">クラフトサケは、<span class="accent">自由</span>な酒。ホップ、果実、ハーブ、米だけの濃いどぶろく——幅が広いぶん、最初の一本に迷う。そこで saketto 編集部が、収録する{S['breweries']}の蔵・{S['brands']}の銘柄から、<span class="accent">タイプ別に12本</span>を選びました。</p>
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
        <p>気になった一本は、銘柄ページから味わいの詳細や蔵の物語を辿れます。購入ボタンは、その銘柄の取扱いを実際に確認できたモールにだけ表示しています（在庫・価格は時期により変動します）。</p>
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
        <h2 class="sub-h">選ばれなかった<span class="accent">{S['brands'] - 12}本</span>のほうへ。</h2>
        <p>ここで挙げた12本は、あくまで入り口です。saketto が収録している銘柄は<strong>{S['brands']}にのぼります</strong>。編集部が12本に絞った時点で、その大半は選から漏れているわけですが、それは「劣る」という意味ではまったくありません。<strong>入手しやすさや、はじめての人にとっての分かりやすさを優先した結果</strong>にすぎません。</p>
        <p>むしろ面白いのは、選ばれなかったほうにあります。年に一度しか仕込まれない酒、蔵の店舗でしか出さない酒、地震で被災した蔵と共同で醸した酒、地元の農家や農園と組んで生まれた酒——<strong>数字に表れない背景を持つ銘柄が、まだいくつも眠っています</strong>。</p>
        <p>そうした一本にたどり着くには、リストを追うより<strong>軸で掘る</strong>ほうが早い。ホップが好きだと分かったなら副原料の軸から、造りの物語に惹かれるならジャンルの軸から、旅の予定に合わせるなら地域の軸から。<strong>12本はあくまで地図の入り口で、その先の道はご自身で選んでほしい</strong>——それが saketto の考える楽しみ方です。</p>
        <div class="pill-links">
          <a href="../subingredients/">副原料から掘る<span class="arr">→</span></a>
          <a href="../genre/">ジャンルから掘る<span class="arr">→</span></a>
          <a href="../brewery/">{S['breweries']}の蔵を見る<span class="arr">→</span></a>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("07", "AWARDED / 外から評価された一本")}
      <div class="prose">
        <h2 class="sub-h">好みの前に、<span class="accent">実績</span>で選ぶ。</h2>
        <p>「編集部が選んだ」と言われても、どこまで信用していいか分からない——そう感じる方には、<strong>第三者の評価という物差し</strong>があります。クラフトサケにも、審査を経て評価された蔵と酒があります。</p>
        <p>代表的なのが<strong>ICC SAKE AWARD</strong>です。順位は<strong>蔵（酒造）に贈られ</strong>、勝ち抜き戦では試合ごとに酒を替えて出します。2023年の初代優勝は<a href="../brewery/ine-to-agave.html">稲とアガベ</a>（決勝で出したのは「稲とアガベ OGAラベル」）。2024年は同蔵が第3位（3位決定戦は「花風」）。2025年の優勝は<a href="../brewery/pukupuku.html">ぷくぷく醸造</a>で、決勝に出したのが木桶どぶろく「#ODAKA」。準優勝は京都の<a href="../brewery/linne.html">LINNÉ</a>（決勝は「800 大麦 樽熟成」）です。ぷくぷく醸造は2024年にも決勝トーナメント（予選を抜けた6社）に進んでおり、<strong>連続して評価されている蔵</strong>と言えます。</p>
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
                     "クラフトサケのおすすめを、saketto編集部がタイプ別に12本厳選。稲とアガベ・haccoba・LAGOON・ぷくぷく醸造など、収録DBの確認済みスペック（度数・容量・参考価格）とともに、はじめての一本から、受賞した蔵の通好みの一本までを紹介します。",
                     "/guide/osusume.html", "article")
    html += masthead(article_masthead_label("osusume"), "A Field Guide")
    html += article_crumbs("osusume")
    html += hero(
        article_eyebrow("osusume"),
        'クラフトサケ、<br><span class="accent">最初の12本</span>。',
        "ホップ、果実、米だけの濃いどぶろく——自由な酒だから、入り口も自由。編集部がタイプ別に選んだ12本を、確認済みのスペックとともに。")
    html += body
    html += footer()
    return html


# ────────────── 記事④：木桶仕込みとは（DEEP） ──────────────

def build_kioke():
    # 🔴 嘘ゼロ（2026-10-29 確認・別Agentで照合）
    #   古くから醸造に木桶・2018年時点で大桶を造れるのは大阪の1社：林野庁 近畿中国森林管理局 https://www.rinya.maff.go.jp/kinki/press/kiaku/attach/pdf/181015_3-1.pdf
    #   昭和初期にホーローのタンクが登場：国税庁 租税史料 https://www.nta.go.jp/about/organization/ntc/sozei/tokubetsu/h22shiryoukan/04.htm
    #   戦後タンクへ・2023年2月に山武杉の新桶・桶は醤油や味噌の蔵へ譲られる：寺田本家 https://www.teradahonke.co.jp/products/kioke/
    #   寿命100〜150年・木桶職人復活プロジェクト（2011年秋〜／2012年1月弟子入り／2013年9月新桶）：ヤマロク醤油 https://yama-roku.net/kioke
    #   甲付：白鹿記念酒造博物館 https://sake-museum.jp/saketalk/1101/ ／竹釘・釘も接着剤も使わない・20石桶 約3600L：職人醤油 https://s-shoyu.com/kioke-knowledge/kioke-tsukuru/
    #   人気酒造「全てが、木桶造り。」・7尺桶6500L：https://www.ninki.co.jp/ ／今代司 平成22年に約60年ぶり復活（蔵の Makuake）
    #   半切桶に乳酸菌：菊正宗 https://www.kikumasamune.co.jp/rd/special/vol02.html ／生酛蔵の設備表面に乳酸菌・酵母：Bokulich ほか 2014 https://pmc.ncbi.nlm.nih.gov/articles/PMC4136118
    #   樽酒＝木製の樽で貯蔵し木香のついた清酒：国税庁 清酒の製法品質表示基準 https://www.nta.go.jp/taxes/sake/hyoji/seishu/gaiyo/02.htm
    #   書かないこと：東北森林管理局の「木材に棲みつく微生物が…」（原文未確認）／権化生酛の木桶（公式ページ404で再確認できず）／「大正期」「1960年頃」「行政が後押し」「欠減が大きい」「呼吸する」「竹の箍は呼吸に合わせて伸縮」「新しい桶ほど木香」「3,000L前後が多い」（いずれも出典なし）
    from gen_axes_pages import brands_in_genre as _in_genre, BRAND_DETAILS as _DET
    from breweries_brands import BRANDS as _BR
    import re as _re
    import statistics as _st

    rows, prices, classic = [], [], 0
    for b in _BREWERIES:
        for nm, href in _in_genre(b, "kioke"):
            i = int(href.rsplit("-", 1)[1].split(".")[0])
            d = (_DET.get(b["slug"]) or [])[i] if i < len(_DET.get(b["slug"]) or []) else {}
            br = _BR[b["slug"]][i]
            shubo = d.get("shubo") or ""
            if _re.search("生酛|水もと|水酛|菩提|花酛", shubo):
                classic += 1
            if br.get("price"):
                prices.append(br["price"])
            shubo_ja = "生酛" if "生酛" in shubo else ("水もと" if _re.search("水もと|水酛", shubo) else "—")
            rows.append(f'            <tr><td class="nm"><a href="{href}">{nm}</a></td><td data-label="蔵"><a href="../brewery/{b["slug"]}.html">{b["name"]}</a></td>'
                        f'<td data-label="酒母">{shubo_ja}</td><td data-label="参考価格">{"¥{:,}".format(br["price"]) if br.get("price") else "—"}</td></tr>\n')
    n_kioke = len(rows)
    n_kura = len({r.split("../brewery/")[1].split(".html")[0] for r in rows})
    _t = round(classic / n_kioke * 10)
    classic_ja = "およそ半数" if _t == 5 else f"{_t}割ほど"
    kioke_median = int(_st.median(prices)) if prices else 0

    cmp_rows = [
        ("素材", "杉の板を竹の釘でつなぎ、竹の箍（たが）で締める。金属の釘も接着剤も使わない", "鉄にガラス質を焼き付けたホーロー、ステンレス"),
        ("管理", "木に棲みつく微生物ごと使う、と蔵元は説明する", "温度や微生物を<strong>管理しやすい</strong>"),
        ("使われ方", "昔から醸造に使われてきた。大きな桶を造れる製造所は、2018年時点で大阪の1社", "昭和初期に登場し、戦後、酒蔵で使われるようになった"),
    ]
    cmp_html = "".join(f'            <tr><td class="nm">{a}</td><td data-label="木桶">{b}</td><td data-label="金属のタンク">{c}</td></tr>\n'
                       for a, b, c in cmp_rows)

    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "WHAT IS / 木桶仕込みとは")}
      <div class="prose">
        <p class="lead">木桶仕込みとは、ステンレスやホーローの金属タンクではなく、<span class="accent">杉の木桶</span>で酒を発酵させる（仕込む）こと。昔から醸造に使われてきた器で、いま一部の日本酒蔵とクラフトサケの蔵が、あえてこの器に戻っている。</p>
        <p>木桶は、杉の板を並べて竹の「箍（たが）」で締めた大きな桶だ。林野庁の資料も「日本では昔から、味噌や醤油、酒などの醸造に木桶が使われてきました」と書いている。それが昭和に入ると金属のタンクに取って代わられ、木桶の需要は減っていった。</p>
        <p>まず、よく聞かれる3つの疑問に短く答えておく。</p>
        <ul class="answer-list">
          <li><strong>何が違う？</strong>　発酵させる器の素材。木に棲みつく微生物が発酵や風味に関わる、と蔵元は説明している。</li>
          <li><strong>なぜ減った？</strong>　昭和初期に温度や微生物を管理しやすいホーローのタンクが登場し、戦後は酒蔵で扱いの簡単なタンクが使われるようになったからだ。</li>
          <li><strong>樽酒と同じ？</strong>　違う。樽酒は木の樽で<strong>貯蔵</strong>して木の香りをつけた酒。木桶仕込みは木の桶で<strong>発酵</strong>させた酒だ。</li>
        </ul>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("02", "COMPARE / 金属タンクとの違い")}
      <div class="prose">
        <h2 class="sub-h">木桶と金属タンクの<span class="accent">違い</span>。</h2>
        <p>どちらが上という話ではない。管理のしやすさを取るか、木と微生物にまかせる部分を残すか——造り手の考え方で器が選ばれている。</p>
      </div>
      <div class="cmp-wrap">
        <table class="cmp cmp--compare">
          <thead><tr><th>項目</th><th>木桶</th><th>金属のタンク</th></tr></thead>
          <tbody>
{cmp_html}          </tbody>
        </table>
      </div>
      <p class="pick-imgnote">出典：国税庁 租税史料、林野庁 近畿中国森林管理局、寺田本家、職人醤油。</p>
    </section>
{divider()}
    <section class="section">
{section_meta("03", "MICROBES / 木桶の中で起きていること")}
      <div class="prose">
        <h2 class="sub-h">木に、<span class="accent">微生物</span>が棲みつく。</h2>
        <p>木桶で造る理由として、蔵元がまず挙げるのが微生物だ。木の表面や細かな隙間に酵母や乳酸菌が棲みつき、毎年の仕込みに加わる——蔵元はそう説明している。</p>
        <p>関連する調べもある。菊正宗酒造の研究所は、生酛づくりの乳酸菌を探して酒造りの道具を調べ、<strong>酛（もと）づくりに使う「半切桶」に菌が潜んでいた</strong>ことを紹介している。北米の生酛造りの蔵1か所を調べた研究（Bokulich ほか、2014年）でも、乳酸菌や酵母が設備の表面から見つかった。ただ、仕込み用の大桶の内側に絞った研究は saketto では確認できておらず、<strong>木桶がどれだけ味を変えるかは、はっきりしていない</strong>。</p>
        <h3 class="sub-h tight">では、木桶の酒は<span class="accent">どんな味</span>？</h3>
        <p>saketto に収録した木桶の銘柄について、蔵や販売店の味の説明を並べると、多くに<strong>「酸」</strong>ということばが出てくる。「心地よい酸味」「引き締まった酸」「酸度が高く」といった具合だ。ただ、これらの多くは生酛や水もとの酒母で造られていて、その酸が木桶によるものかどうかはわからない。<strong>木桶の酒の味は、米・麹・酒母・蔵の微生物の組み合わせで決まる</strong>と考えたほうがいい。銘柄ごとの説明は、下の「saketto で出会える木桶の酒」で紹介している。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("04", "HISTORY / なぜ消え、なぜ戻ってきたか")}
      <div class="prose">
        <h2 class="sub-h">消えかけた桶と、<span class="accent">桶を造る人</span>。</h2>
        <p>国税庁の租税史料によると、<strong>昭和初期</strong>に、旧来の木製の容器に替わって、温度管理・微生物管理に優れるホーローのタンクが登場した。千葉の寺田本家も、戦後、酒蔵では扱いが簡単なホーローなどのタンクを使うようになったと書いている。林野庁の資料も、木桶は鉄製やステンレス製の容器に取って代わられ、需要が減ったとしている。</p>
        <p>需要が減れば、桶を造る仕事も減る。林野庁の2018年の資料では、<strong>大きな木桶を造れる製造所は大阪の1社</strong>だけになっていた。</p>
        <p>この流れに抗ったのが、醤油の造り手だ。香川・小豆島のヤマロク醤油は2011年秋に「木桶職人復活プロジェクト」を始め、同級生の大工たちと最後の桶屋に弟子入りして、2013年に新しい桶を完成させた。いまは毎年1月に小豆島で新しい桶を組んでいる。造れる人ごと増やしていく取り組みだ。</p>
        <p>酒蔵にも、木桶に戻る動きがある。寺田本家は2023年2月に山武杉の新しい桶を完成させて仕込みに使い、福島・二本松の人気酒造は「全てが、木桶造り。」を掲げる（日本酒のみ。鑑評会への出品酒を除く）。新潟の今代司は、蔵の Makuake ページで、平成22年（2010年）に木桶仕込みの純米酒を約60年ぶりに復活させたと説明している。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("05", "HOW MADE / 木桶のつくり")}
      <div class="prose">
        <h2 class="sub-h">杉の板を、<span class="accent">竹</span>で締める。</h2>
        <p>木桶の材料は主に杉だ。樽の材について、白鹿記念酒造博物館は、杉の白い部分（白味）と赤い部分（赤味）の両方を含む部位がもっとも好まれ、「甲付（こうつき）」と呼ばれると説明している。</p>
        <p>醤油の木桶を紹介する「職人醤油」によると、桶には<strong>金属の釘も接着剤も使わず</strong>、板と板を<strong>竹の釘</strong>でつなぐ。外側を竹で編んだ箍で締めて形を保つ。</p>
        <p>大きさはさまざまで、人気酒造は蔵によると日本最大級の7尺桶（6,500リットル）を使っている。醤油の世界では「20石桶」と呼ばれる約3,600リットルの桶が使われてきた。ヤマロク醤油は「一般的に木桶の寿命は100～150年くらいと言われています」と書き、寺田本家によると、酒蔵で使い終えた桶を醤油屋や味噌屋が譲り受けることもある。</p>
      </div>
    </section>
{divider()}
    <section class="section" id="in-saketto">
{section_meta("06", "IN SAKETTO / saketto で出会える木桶の酒")}
      <div class="prose">
        <h2 class="sub-h">{n_kura}蔵・{n_kioke}銘柄の<span class="accent">木桶の酒</span>。</h2>
        <p>saketto に収録した銘柄のうち、公式情報などで木桶仕込みと確認できたのは{n_kioke}銘柄。目立つのは、<strong>{classic_ja}が生酛や水もとといった古い酒母で造られている</strong>ことだ。とくに{kura_link("nondo")}と{kura_link("cultiva")}は、乳酸を加えない古い酒母と木桶を組み合わせている。</p>
      </div>
      <div class="cmp-wrap">
        <table class="cmp cmp--compare">
          <thead><tr><th>銘柄</th><th>蔵</th><th>酒母</th><th>参考価格</th></tr></thead>
          <tbody>
{"".join(rows)}          </tbody>
        </table>
      </div>
      <p class="pick-imgnote">酒母の「—」は、公式情報に記載がないもの。</p>
      <div class="prose">
        <p>岩手・遠野の{kura_link("nondo")}は、「権化」シリーズを水もとと木桶で醸してきた。公式の説明では、「権化 Rafters」は「お米由来の軽やかな甘みと心地よい酸味。グレープフルーツや柑橘系の香りも感じられる味わいです。」。福岡の{kura_link("cultiva")}は生酛と木桶で仕込み、福岡産ヒノヒカリについて「製法は山田錦のときと変わらず、生酛造りと木桶での仕込み」と説明している。味は、ヒノヒカリが「酸度が高く、全体としてすっきりとした印象」、山田錦が「とろみのあるテクスチャーとともに濃厚な甘味」だという。</p>
        <p>福島・小高の{kura_link("pukupuku")}は、福島県産の杉と竹で組んだ木桶を使う。ICC SAKE AWARD 2025 で蔵が優勝したとき、決勝で出したのは蔵付き酵母で造る木桶どぶろく「#ODAKA」だった。埼玉・飯能の{kura_link("yamane")}は、地元・西川材の道具と木桶で仕込んでいる。</p>
        <div class="pill-links">
          <a href="../genre/#g-kioke">ジャンル「木桶仕込み」から探す<span class="arr">→</span></a>
          <a href="zenkoji.html">全麹仕込みとは<span class="arr">→</span></a>
        </div>
      </div>
    </section>
{divider()}
    <section class="section" id="faq">
{section_meta("07", "FAQ / よくある質問")}
      <div class="prose">
        <h3 class="sub-h tight">木桶仕込みと樽酒は、どう違いますか？</h3>
        <p>使う段階が違います。国税庁の表示基準では、樽酒は「木製の樽で貯蔵し、木香の付いた清酒」です。木桶仕込みは、木の桶で<strong>発酵</strong>させること。木桶仕込みの酒が、必ずしも木の香りがするわけではありません。</p>
        <h3 class="sub-h tight">木桶仕込みのお酒は、味が違いますか？</h3>
        <p>蔵や販売店の説明には「酸」に触れたものが多いですが、生酛や水もとで造った銘柄が多いため、木桶だけの効果かはわかりません。銘柄ごとの公式の説明を参考にしてください。</p>
        <h3 class="sub-h tight">木桶で仕込めば、クラフトサケになりますか？</h3>
        <p>なりません。木桶は日本酒でも使う器で、法律上の区分は原料と「こすかどうか」で決まります。寺田本家や人気酒造のように、木桶で仕込む日本酒蔵もあります。区分の違いは<a href="craftsake-towa.html">クラフトサケとは</a>で説明しています。</p>
        <h3 class="sub-h tight">木桶仕込みのお酒は高いですか？</h3>
        <p>saketto に収録した木桶仕込みの銘柄は、価格がわかるものの中央値が{round(kioke_median, -2):,}円ほどで、収録全体の中央値（{S['price_median']:,}円）より{"高め" if kioke_median > S['price_median'] else "低め"}です。2,000円を切るものから、1万円を超えるものまであります。</p>
        <h3 class="sub-h tight">どうやって見分けますか？</h3>
        <p>ラベルや蔵の商品説明に「木桶仕込み」「木桶発酵」と書かれていることが多いです。saketto では<a href="../genre/#g-kioke">ジャンル「木桶仕込み」</a>からまとめて探せます。</p>
        <h3 class="sub-h tight">木桶は何年くらい使えるのですか？</h3>
        <p>ヤマロク醤油は「一般的に木桶の寿命は100～150年くらいと言われています」と書いています。箍の締め直しなどの手入れをしながら、長く使い続ける器です。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("08", "READ ON / もっと味わう")}
      <div class="prose">
        <p>木桶は、クラフトサケの造りを彩る技法のひとつ。花酛・水もと・生酛・全麹といったほかの造りのことばは、<a href="craftsake-towa.html">クラフトサケとは</a>でまとめて紹介している。</p>
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
            <div class="readmore__t">全麹仕込みとは</div>
          </a>
        </div>
      </div>
    </section>

  </div>
"""
    html = page_head("木桶仕込みとは？金属タンクとの違い・樽酒との違い・味を解説",
                     "木桶仕込みとは、ステンレスやホーローのタンクではなく杉の木桶で酒を発酵させること。金属タンクとの違いを表で整理し、樽酒との違い、木桶が消えて戻ってきた歴史、木桶に棲む微生物の話、saketto で買える木桶仕込みの酒まで解説します。",
                     "/guide/kioke.html", "article")
    html += masthead(article_masthead_label("kioke"), "A Field Guide")
    html += article_crumbs("kioke")
    html += hero(
        article_eyebrow("kioke"),
        '木桶仕込みとは。<br>木が醸す、<span class="accent">時間の酒</span>。',
        "金属のタンクではなく、杉の桶で発酵させる。昭和に消えかけた木桶に、なぜ造り手は戻るのか。違い・歴史・微生物・銘柄を、公式情報から。")
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
        "誰かにではなく、自分に。頑張った日の夜、特別な一本をゆっくりと。受賞した蔵の酒や最高峰の仕込みで、クラフトサケの奥深さを心ゆくまで味わいたい。",
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
     "ICC SAKE AWARD 2025で優勝したぷくぷく醸造が、決勝の舞台に選んだ一本。頑張った自分へのご褒美に、頂点を決めた味を確かめてみては。蔵付き酵母と木桶が生む、発酵の力を存分に味わえる。"),
    ("自分へのご褒美に", "FOR YOURSELF", "nondo", 2,
     "nondoが水もと・木桶で醸す、権化シリーズの無濾過生原酒。米糠まで活かした濃密で複雑な味わいは、特別な夜にゆっくり向き合いたい。誰かにではなく、頑張った自分へ贈る一本。"),
]


def build_gift():
    cards = PICK_IMGNOTE
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
      <a class="pick__fig" href="../brand/{slug}-{idx}.html" tabindex="-1" aria-hidden="true">{thumb_tag(slug, idx, cls="pick__thumb")}</a>
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
        <p>気になった一本は、銘柄ページから味わいや蔵の物語を辿れます。購入ボタンは、その銘柄の取扱いを実際に確認できたモールにだけ表示しています（在庫・価格・ギフト対応は時期や販売店により異なります）。</p>
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
        <p>{_furusato_gift_summary()}</p>
        <p>注意したいのは、<strong>ふるさと納税は「割引」ではない</strong>ということ。寄附に対する税の控除であり、手続きも必要です。ただ<strong>通販モールには出ていない銘柄が、ここでだけ手に入る</strong>ことがあります。返礼品の内容は変わることがあるので、寄附の前に各ポータルで最新の情報を確認してください。仕組みと流れは<a href="furusato.html">ふるさと納税の解説記事</a>で詳しく読めます。</p>
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
    html += article_crumbs("gift")
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
        <h2 class="sub-h">{S['brands']}本のうち、<span class="accent">{S['hop_any']}本</span>。</h2>
        <p>花酛から始まったホップの酒は、いまどれくらいの規模になっているのか。saketto の収録{S['brands']}銘柄を副原料で分類すると、<strong>ホップを使った銘柄は{S['hop_any']}</strong>。米と麹だけの{S['rice_only']}銘柄、果実系の{S['fruit']}銘柄、アガベ・蜂蜜・出汁などの特殊副原料（{S['special']}銘柄）に次ぐ規模で、茶葉・ハーブ（{S['tea_herb']}銘柄）を上回る一角だ。蔵の数でいえば{S['hop_any_breweries']}蔵が手がけている。</p>
        <p>副原料そのものは<strong>全体で{S['ingredient_variants']}通り</strong>を数えるが、そのなかで<strong>ホップは単独の素材として突出して多い</strong>。果実は苺・ぶどう・柑橘などに分かれるため、「ひとつの素材」として見ればホップが最大勢力といっていい。<strong>幻の製法だったものが、いまジャンルの背骨のひとつになっている</strong>。</p>
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
    html += article_crumbs("hanamoto")
    html += hero(
        article_eyebrow("hanamoto"),
        '花酛とは。<br>米とホップの、<span class="accent">古い約束</span>。',
        "東北に伝わる幻のどぶろく製法、花酛。東洋のホップ「唐花草」で醸すその酒に、クラフトサケの自由の原点がある。")
    html += body
    html += footer()
    return html


def build_doburoku():
    # 🔴 嘘ゼロ：法律・定義は一次資料から（2026-10-29 確認・別Agent 2体で照合済み）
    #   酒税法 第2条（酒類＝1度以上）・第3条第7号（清酒＝こしたもの・22度未満）・第19号（その他の醸造酒＝20度未満）・
    #     第7条（最低製造数量 清酒60kL／その他の醸造酒6kL／輸出用清酒の例外）・第10条第11号（需給調整）・第54条（無免許製造）
    #     https://laws.e-gov.go.jp/law/328AC0000000006
    #   「こす」の解釈：国税庁 法令解釈通達 第3条 共通事項11 https://www.nta.go.jp/law/tsutatsu/kihon/sake/2-02.htm
    #   上澄みの取り分けも「こす」：国税庁 特区の手引 https://www.nta.go.jp/taxes/sake/menkyo/tebiki/menkyo2.pdf
    #   どぶろく＝その他の醸造酒・こす工程が無い：国税庁 酒類販売管理研修モデルテキスト https://www.nta.go.jp/taxes/sake/hambai/moderutekisuto/pdf/r04_04_07.pdf
    #   にごり酒・活性清酒・並行複発酵：日本酒造組合中央会 用語集 https://japansake.or.jp/sake/about-sake/glossary-of-sake/
    #   「にごり」は表示基準の用語ではない：https://www.nta.go.jp/taxes/sake/hyoji/seishu/kokuji891122/03.htm
    #   甘酒・白酒：農林水産省 https://www.maff.go.jp/j/heya/sodan/1201/a02.html ／森永製菓 FAQ https://www.morinaga.co.jp/faq/faq_detail.html?id=4249
    #     酒かすのアルコール 8.2g/100g：日本食品標準成分表（八訂）増補2023 17053 https://fooddb.mext.go.jp/details/details.pl?ITEM_NO=17_17053_7
    #   マッコリ：韓国 주세법 별표 2.가（탁주）https://www.law.go.kr/법령/주세법 ／韓国民族文化大百科「탁주」E0058756「막걸리 빚기」E0079922「누룩」E0013237
    #     JINRO マッコリ https://www.jinro.co.jp/goods/makkori/ ／東京税関 事前教示 https://www.customs.go.jp/tetsuzuki_search/bunrui/J1/23/J12301186.htm ・J12301297.htm
    #   餅こうじ（小泉武夫氏の述として）・1899年の自家醸造禁止（監修者論評）・沖縄の一部は大正期まで：国税庁 https://www.nta.go.jp/taxes/sake/koujikin/pdf/0021012-102_01.pdf
    #   自家醸造・梅酒の例外：国税庁 Q&A https://www.nta.go.jp/taxes/sake/qa/06/32.htm ・35.htm ／どぶろく特区：構造改革特別区域法 第25条 https://laws.e-gov.go.jp/law/414AC0000000189
    import re as _re
    from breweries_brands import BRANDS as _BR, is_alias as _is_alias
    # 度数の幅：名前に「どぶろく・ドブロク・濁酒・DOBUROKU」が入る銘柄だけで数える（メモに濁酒とあるだけの澄んだ酒を拾わない）
    _abv = sorted(b["abv"] for s, bs in _BR.items() for i, b in enumerate(bs)
                  if not _is_alias(s, i) and isinstance(b.get("abv"), (int, float))
                  and _re.search("どぶろく|ドブロク|濁酒|DOBUROKU", b["name"]))
    abv_lo, abv_hi = _abv[0], _abv[-1]
    n_under10 = sum(1 for a in _abv if a < 10)
    _tenths = round(n_under10 / len(_abv) * 10)  # 統計は曖昧化して書く（○割ほど）
    under10_ja = "およそ半数" if _tenths == 5 else f"{_tenths}割ほど"

    cmp_rows = [
        ("どぶろく", "米・米麹・水", "<strong>こさない</strong>", f"あり（saketto 収録の銘柄で{abv_lo}〜{abv_hi}度ほど）", "その他の醸造酒"),
        ("にごり酒", "米・米麹・水", "目の粗い網や布で<strong>粗くこす</strong>", "あり（清酒なので22度未満）", "清酒（日本酒）"),
        ("清酒（日本酒）", "米・米麹・水 など", "<strong>こす</strong>", "あり（22度未満）", "清酒"),
        ("甘酒（米麹）", "米・米麹", "—", "ほぼ無い（<strong>1%未満</strong>）", "お酒ではない"),
        ("甘酒（酒粕）", "酒粕・砂糖 など", "—", "酒粕のアルコールが残ることがある", "1%未満の市販品は清涼飲料水"),
        ("マッコリ", "穀物・麹（ヌルクなど）・水", "ふるいで<strong>粗くこし</strong>、水で割るのが伝統的", "販売品は6〜8%ほどが一般的", "日本では「リキュール」として売られる例がある"),
    ]
    cmp_html = "".join(f'            <tr><td class="nm">{a}</td><td data-label="主な原料">{b}</td><td data-label="こすか">{c}</td><td data-label="度数">{d}</td><td data-label="日本での区分">{e}</td></tr>\n'
                       for a, b, c, d, e in cmp_rows)

    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "WHAT IS / どぶろくとは")}
      <div class="prose">
        <p class="lead">どぶろくとは、米・米麹・水を発酵させたもろみを、<span class="accent">こさずに</span>そのまま仕上げた酒。米粒や麹が溶け残って白く濁り、とろりとした口当たりになる。漢字では「濁酒」と書き、酒税法では日本酒（清酒）ではなく<strong>「その他の醸造酒」</strong>にあたる。</p>
        <p>国税庁の研修用テキストも、どぶろくを「その他の醸造酒」の例に挙げ、「清酒と同様に米、米麹、水を原料として発酵させて造りますが、清酒と異なり『こす』工程がありません」と説明している。<strong>原料も造りも日本酒とほとんど同じで、大きな違いは最後に「こす」かどうか</strong>だ。味は甘口から、ヨーグルトのような酸味のあるもの、しゅわしゅわと発泡するものまで幅広く、度数も{abv_lo}〜{abv_hi}度ほどとさまざまだ。</p>
        <p>見た目が似ているせいで、どぶろくはよく、にごり酒・甘酒・マッコリと混同される。先に答えを書いておく。</p>
        <ul class="answer-list">
          <li><strong>にごり酒</strong>　粗くこした日本酒。一度もこさないどぶろくとは、法律上の区分が違う。</li>
          <li><strong>甘酒（米麹）</strong>　アルコール発酵をしていない、お酒ではない飲みもの。</li>
          <li><strong>マッコリ</strong>　韓国の濁り酒。麹の種類、こし方、日本での区分が違う。</li>
        </ul>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("02", "COMPARE / 違いが一目でわかる表")}
      <div class="prose">
        <h2 class="sub-h">どぶろく・にごり酒・甘酒・マッコリの<span class="accent">違い</span>。</h2>
        <p>分かれ目は、<strong>こすかどうか</strong>と、<strong>アルコール発酵をしているかどうか</strong>の2つだ。酒税法でいう「度」は、％と同じ意味で使っている。</p>
      </div>
      <div class="cmp-wrap">
        <table class="cmp cmp--compare">
          <thead><tr><th>種類</th><th>主な原料</th><th>こすか</th><th>アルコール度数</th><th>日本での区分</th></tr></thead>
          <tbody>
{cmp_html}          </tbody>
        </table>
      </div>
      <p class="pick-imgnote">出典：酒税法（第2条・第3条）、国税庁「酒類販売管理研修モデルテキスト」、日本酒造組合中央会「日本酒用語集」、農林水産省「消費者の部屋」、森永製菓 よくある質問、韓国・酒税法（주세법）別表、韓国民族文化大百科事典、JINRO マッコリ公式ページ。度数は商品によって異なります。</p>
    </section>
{divider()}
    <section class="section" id="nigori">
{section_meta("03", "VS NIGORI / にごり酒との違い")}
      <div class="prose">
        <h2 class="sub-h">にごり酒は、粗くこした<span class="accent">日本酒</span>。</h2>
        <p>違いは、<strong>こしているかどうか</strong>。にごり酒は一度こした日本酒で、どぶろくは一度もこさない。日本酒造組合中央会の用語集は、にごり酒を「清酒醪を上槽するときに、ある程度目の粗い網あるいは布などで濾過した白濁した清酒」と説明している。目の粗い布を通すので、細かな米や麹の粒が液に残って濁る。こしてあり、清酒の原料と度数の条件も満たすので、<strong>にごり酒は法律上も清酒、つまり日本酒の仲間</strong>だ。</p>
        <p>ここで知っておきたいのは、法律でいう「こす」の範囲がとても広いことだ。国税庁の通達は、「こす」を「その方法のいかんを問わず酒類のもろみを液状部分とかす部分とに分離する全ての行為」としている。どぶろく特区の手引には、<strong>上澄みを別の容器に取り分けるだけでも「こす」にあたる</strong>とまで書かれている。どぶろくは、もろみを少しも分けずに、まるごと瓶に詰めた酒なのだ。</p>
        <p>だから口当たりも違ってくる。どぶろくは、溶け残った米粒のざらりとした感触や、もったりとした重さを楽しめるものが多い。にごり酒は布を通したぶん、どぶろくよりさらりとしたものが多い。もっとも、どちらも造り方しだいで幅がある。</p>
        <h3 class="sub-h tight">見分けるなら、ラベルの<span class="accent">「品目」</span></h3>
        <p>店頭で迷ったら、ラベルの<strong>品目</strong>を見るのが確実だ。白く濁った米の酒で、<strong>品目が「清酒」ならにごり酒</strong>（粗くこした日本酒）、<strong>「その他の醸造酒」ならどぶろく</strong>か、副原料を使ったクラフトサケである。「にごり」という言葉は、国税庁の清酒の表示基準で定められた用語ではないので、商品名よりも品目のほうが頼りになる。</p>
        <h3 class="sub-h tight">活性にごり・おりがらみとは</h3>
        <p><strong>活性にごり</strong>（活性清酒）は、清酒のもろみを粗くこした濁ったままの酒で、微弱な発酵が続いてガスを含むことからこの名が付いた。ただし、酒質を安定させるために火入れしたものが多い（日本酒造組合中央会）。火入れをせず、瓶の中で酵母が生きているものもある。<strong>おりがらみ</strong>には公的な定義がなく、搾った酒に沈む白い滓（おり）を少し絡ませて出すものを、蔵ごとにそう呼んでいる。どちらも、品目が「清酒」なら日本酒の側の酒だ。</p>
      </div>
    </section>
{divider()}
    <section class="section" id="amazake">
{section_meta("04", "VS AMAZAKE / 甘酒との違い")}
      <div class="prose">
        <h2 class="sub-h">米麹の甘酒は、<span class="accent">お酒ではない</span>。</h2>
        <p>甘酒とどぶろくを分けるのは、<strong>アルコール発酵をしているかどうか</strong>だ。米麹の甘酒は、麹の酵素が米のでんぷんを糖に変えただけの飲みもので、酵母によるアルコール発酵をしていない。農林水産省は、米麹の甘酒のアルコール度数を1%未満としている。酒税法でいう「酒類」はアルコール分1度以上の飲料なので、<strong>米麹の甘酒はお酒ではない</strong>。</p>
        <p>どぶろくは、その先まで進んだ酒だ。米麹が米を糖に変えるのと同時に、酵母がその糖をアルコールに変えていく。日本酒と同じこの<strong>並行複発酵</strong>を経ているので、甘口のどぶろくでも、れっきとしたお酒である。<strong>甘くて甘酒のように見えても、子どもや運転する人は飲めない</strong>。</p>
        <h3 class="sub-h tight">酒粕の甘酒は、<span class="accent">少し別もの</span></h3>
        <p>酒粕を溶いて作る甘酒もある。酒粕は日本酒を搾ったあとの粕で、アルコールが残っている（日本食品標準成分表では、酒かす100gあたり8.2g）。市販の甘酒には、アルコールが1%未満含まれるものもある。森永製菓は、同社の「甘酒」にはアルコールが1%未満含まれ、法律上は清涼飲料水だとしたうえで、子どもに飲ませるかは保護者の判断としている。家で酒粕を溶いて作るときは、加熱の具合や酒粕の量でアルコールの残り方が変わる。<strong>アルコールを避けたいときは、原材料に酒粕を含まない米麹の甘酒を選ぶ</strong>のが安心だ。</p>
        <p>なお、ひな祭りの<strong>白酒</strong>は甘酒とは別もので、アルコール度数は10%前後ある（農林水産省）。</p>
      </div>
    </section>
{divider()}
    <section class="section" id="makgeolli">
{section_meta("05", "VS MAKGEOLLI / マッコリとの違い")}
      <div class="prose">
        <h2 class="sub-h">マッコリは、<span class="accent">韓国の濁り酒</span>。似ているが、同じではない。</h2>
        <p>マッコリは、韓国の酒税法で<strong>탁주（濁酒）</strong>にあたる酒だ。法律は「でん粉を含む材料（発芽させた穀類を除く）、麹（국）及び水を原料として発酵させたもろみを、濾過せずに濁った状態に仕上げたもの」と定めている（糖分や果物・野菜を加えたものなども탁주に含まれる）。穀物と麹と水を発酵させ、濁ったまま飲む——発想はどぶろくとよく似ている。違いは3つある。</p>
        <h3 class="sub-h tight">違い1　<span class="accent">麹</span>がちがう</h3>
        <p>日本の麹は、蒸した米などに麹菌を生やした、粒がばらばらの「散（ばら）こうじ」。韓国の伝統的な麹<strong>ヌルク（누룩）</strong>は、小麦・米・大麦などの穀物にカビを繁殖させたもので、主に餅状に固めたものが使われてきた（韓国民族文化大百科事典）。国税庁の調査報告でも、発酵学者の小泉武夫氏が、日本以外の国々では穀物を練り固めた「餅こうじ」が使われると述べている。もっとも、いまの韓国の醸造所では、白麹菌で作った粒の麹が主に使われているという（同事典）。</p>
        <h3 class="sub-h tight">違い2　<span class="accent">こし方と度数</span>がちがう</h3>
        <p>マッコリは、もろみをふるいで<strong>粗くこし</strong>、水を加えて、<strong>アルコール度数6〜8%ほどに整える</strong>のが一般的だ（同事典）。名前も「粗く（あるいは、たった今）こした酒」という意味から来たとされる。韓国の法律は「濾過せずに」と書くが、日本の酒税法では、こうした粗い分離も「こす」にあたる。<strong>同じ「濁った酒」でも、両国で「こす」という言葉の範囲は同じではない</strong>。どぶろくは、もろみをまったく分けずに瓶に詰める。水で割って仕上げるぶん、マッコリには軽く飲みやすいものが多い。</p>
        <h3 class="sub-h tight">違い3　日本での<span class="accent">区分</span>がちがう</h3>
        <p>日本で売られている韓国のマッコリには、<strong>「リキュール」として売られているもの</strong>がある。たとえば JINRO のマッコリは、公式ページで区分をリキュール、アルコール度数を6%としている。東京税関の事前教示回答（2023年）でも、異性化糖や甘味料を加えたマッコリは、酒税の区分がリキュールとされている。どぶろくは「その他の醸造酒」なので、ここでも分類が分かれる。</p>
        <p>まとめると、マッコリは<strong>麹の種類、こし方（と販売時の加水）、日本での区分</strong>で、どぶろくとは別の酒になる。どちらも「穀物を濁ったまま楽しむ酒」という、同じ根っこを持つ親戚のような関係だ。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("06", "TASTE &amp; MAKING / 味わいと造り")}
      <div class="prose">
        <h2 class="sub-h">甘い、酸っぱい、<span class="accent">しゅわしゅわ</span>。</h2>
        <p>どぶろくの造りの工程は、清酒とほとんど変わらない。<strong>米を洗って蒸し、麹をつくり、酒母を立て、もろみを発酵させる</strong>。そして最後に、こさずに瓶へ詰める。清酒なら搾りの工程で粕を分けられるが、どぶろくは仕込んだものがそのまま製品になる。米の溶け具合、麹の出来、発酵の進み方——すべてが飲み口に直結する。</p>
        <p>味を大きく分けるのは、<strong>発酵をどこで止めるか</strong>だ。糖が残っているうちに瓶詰めすれば甘口に、発酵を進めればすっきりと辛口に寄る。白麹を使えば柑橘のようなクエン酸の酸が、乳酸系の酒母ならヨーグルトを思わせる酸が立つ。<strong>米の溶かし方</strong>でも口当たりは変わり、粒を残せばざらりと、溶かし込めばなめらかに、ムースのように空気を含むものもある。</p>
        <p>火入れをしない生タイプは、瓶詰め後も酵母が生きていて、瓶の中で発酵が続くことがある。<strong>店頭で、冷蔵庫で、少しずつ味が変わっていく</strong>。開けたときにガスが上がるのはそのためだ。どぶろくが「生きている酒」と呼ばれるゆえんである。</p>
        <h3 class="sub-h tight">酒母という、<span class="accent">見えない出発点</span></h3>
        <p>飲み手にいちばん見えにくいのが<strong>酒母（しゅぼ）</strong>だ。酵母を安全に増やすための最初の仕込みで、ここで何を使うかで、酸の出方も香りの方向も変わる。saketto の収録銘柄では、単独でいちばん多い表記は現代的な高温糖化だが、生酛・水酛・菩提酛・<a href="hanamoto.html">花酛</a>といった古典的な酒母を合わせると、それを上回る。生米を水に漬けて乳酸発酵させ、その酸っぱい水を仕込みに使う水酛のように、<strong>雑菌を寄せつけない環境を微生物の力だけでつくる</strong>古い知恵が、いまのどぶろくで現役で使われている。ラベルに酒母の表記があったら、読み飛ばさないでほしい。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("07", "HOW TO ENJOY / 選び方・飲み方・保存")}
      <div class="prose">
        <h2 class="sub-h">初めての一本は、<span class="accent">ラベル</span>で選ぶ。</h2>
        <p>どぶろくを選ぶときに見ておきたいのは、3つの表示だ。<strong>ひとつめは「要冷蔵」</strong>。要冷蔵の表示があるものは、生タイプなど味が動きやすいものが多く、買ったらすぐ冷蔵庫へ入れる。<strong>ふたつめは「活性」「発泡」「開栓注意」</strong>といった表示。瓶の中でガスが生きているので、開け方に気をつけたい。<strong>みっつめは度数</strong>。どぶろくは{abv_lo}度ほどの軽いものから、日本酒並みの度数のものまである。</p>
        <p>米と麹だけの味を知りたいなら、副原料を使わない<a href="../genre/">「古典どぶろく」</a>から。慣れてきたら、ホップや果実を使ったものに進むと、違いがよくわかる。</p>
        <h3 class="sub-h tight">飲む前に、<span class="accent">そっと混ぜる</span></h3>
        <p>どぶろくは、瓶の底に米や麹の粒が沈んでいることが多い。飲む前に<strong>瓶をゆっくり回すように傾けて</strong>、全体をなじませる。上澄みだけをまず飲んで、あとから混ぜて味の変化を楽しむ人もいる。活性タイプは振ると噴き出すので、混ぜるときもやさしく。よく冷やして飲むのが基本だが、ぬる燗にすると甘みがふくらむものもある。</p>
        <h3 class="sub-h tight">保存は、<span class="accent">冷蔵・立てて・早めに</span></h3>
        <p>生タイプは冷蔵庫で、瓶を立てて保存する。開けたあとも冷蔵し、なるべく早く飲みきりたい。ボトルの表示や蔵の案内があれば、それがいちばんのガイドになる。温度や器の選び方、保存のコツは<a href="nomikata.html">飲み方・楽しみ方</a>にくわしく書いた。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("08", "HISTORY / 家の酒から、新しい蔵の酒へ")}
      <div class="prose">
        <h2 class="sub-h">かつて、酒は<span class="accent">台所</span>で生まれた。</h2>
        <p>どぶろくは、古くは家々で造られる酒だった。収穫した米と麹を仕込み、その家、その土地の味に育てる。神事として酒造りを伝える神社は、いまも50数社あるとされる（国税庁の調査報告）。</p>
        <p>しかし1899年（明治32年）に自家用の酒造りが原則として禁じられると（国税庁の調査報告所収の論評による。沖縄の一部では大正期まで認められていたとされる）、どぶろくは日常から遠ざかった。造り手が減れば、レシピも技も途絶える。<a href="hanamoto.html">花酛（はなもと）</a>のように、長く忘れられていた製法もある。</p>
        <h3 class="sub-h tight">なぜ、いま<span class="accent">増えている</span>のか</h3>
        <p>国内向けの清酒の新しい製造免許は、需給調整の規定（酒税法第10条第11号）があるため、取得がきわめて難しいとされる（輸出用に限った清酒の製造免許は別にある）。清酒には年60キロリットルという最低製造数量の基準もある。いっぽう「その他の醸造酒」の最低製造数量は年6キロリットル（酒税法第7条）で、条件を満たせば新しく免許を得る道がある。<strong>「その他の醸造酒」の免許を取ることが、新しい造り手の現実的な入口だった</strong>。こさないどぶろくも、副原料を使って清酒の定義から外れる酒も、ここに入る。</p>
        <p>そしてこの枠には、もうひとつの自由がついてくる。清酒の定義から外れる以上、<strong>米と米麹以外のものを使ってもかまわない</strong>。ホップ、果実、茶葉、ハーブ、スパイス——副原料を自由に選べる。制度上の制約から始まった選択が、結果として表現の幅を一気に押し広げた。成り立ちの全体像は<a href="craftsake-towa.html">クラフトサケとは</a>で紹介している。農家民宿などの「どぶろく特区」については、下のよくある質問で触れる。</p>
        <div class="callout">
          <div class="callout__label">編集部より</div>
          <p>どぶろくの歴史や地域の慣習には、文献・伝承にもとづく部分が多く、細部には諸説あります。本記事は公的資料と、収録蔵の公式情報をもとに構成しています。</p>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("09", "IN SAKETTO / どぶろくを探す")}
      <div class="prose">
        <h2 class="sub-h">米と麹だけの、<span class="accent">まっすぐな一杯</span>。</h2>
        <p>saketto では、副原料を使わず米と麹だけで醸したものを「<strong>古典どぶろく</strong>」として分類している。ここには、東京駅のエキナカで醸す<a href="../brewery/tokyo-station.html">東京駅酒造場</a>、大阪の<a href="../brewery/heiwa-namba.html">平和どぶろく難波醸造所</a>と日本橋の<a href="../brewery/heiwa-kabutocho.html">兜町醸造所</a>、岩手・遠野の<a href="../brewery/nondo.html">nondo</a>、福島・小高の<a href="../brewery/pukupuku.html">ぷくぷく醸造</a>、滋賀の糀屋<a href="../brewery/happy-taro.html">ハッピー太郎醸造所</a>などが並ぶ。</p>
        <p>いっぽうで、ホップや果実を使ったどぶろくも数多い。<a href="../brewery/ine-to-agave.html">稲とアガベ</a>の「DOBUROKU ホップ」、<a href="../brewery/lagoon.html">LAGOON BREWERY</a>の「酔いどれメロン ドブロク」などがその例だ。<strong>こさないことだけが共通で、あとは自由</strong>——どぶろくというジャンルの広さが、そのまま棚に並んでいる。買える場所は<a href="doko-de-kaeru.html">どこで買える？</a>に、造っている蔵で飲める店は<a href="nomeru-kura.html">クラフトサケが飲める醸造所</a>にまとめている。</p>
        <div class="pill-links">
          <a href="../genre/">ジャンル「古典どぶろく」から<span class="arr">→</span></a>
          <a href="../subingredients/">副原料から探す<span class="arr">→</span></a>
          <a href="../brewery/">蔵から探す<span class="arr">→</span></a>
        </div>
      </div>
    </section>
{divider()}
    <section class="section" id="faq">
{section_meta("10", "FAQ / よくある質問")}
      <div class="prose">
        <h3 class="sub-h tight">どぶろくとにごり酒、<span class="accent">日本酒</span>なのはどっち？</h3>
        <p>にごり酒です。にごり酒はもろみを目の粗い布などで粗くこした清酒（日本酒）で、どぶろくはこす工程が無いため、酒税法上は「その他の醸造酒」に分類されます。ラベルの品目で見分けられます。くわしくは<a href="#nigori">にごり酒との違い</a>へ。</p>
        <h3 class="sub-h tight">どぶろくと甘酒は、<span class="accent">違うもの</span>？</h3>
        <p>別のものです。米麹の甘酒は、麹で米を糖化しただけでアルコール度数1%未満（農林水産省）の飲みもの。どぶろくは酵母がアルコール発酵まで進めたお酒です。酒粕の甘酒には、酒粕のアルコールが残ることがあります。くわしくは<a href="#amazake">甘酒との違い</a>へ。</p>
        <h3 class="sub-h tight">どぶろくとマッコリは、<span class="accent">同じ</span>？</h3>
        <p>似ていますが、同じではありません。マッコリは韓国の濁り酒で、麹（ヌルクなど）の種類、もろみを粗くこして水で割る造り、日本での区分（リキュールとして売られるものがある）が、どぶろくと違います。くわしくは<a href="#makgeolli">マッコリとの違い</a>へ。</p>
        <h3 class="sub-h tight">どぶろくは、日本酒より<span class="accent">強い</span>？</h3>
        <p>商品によります。saketto に収録しているどぶろくでは、{under10_ja}が10度未満の軽めのもの。日本酒に近い度数のものもあり、いちばん高いもので{abv_hi}度です。なお「その他の醸造酒」は、酒税法上アルコール分20度未満と決められています。</p>
        <h3 class="sub-h tight">どんな<span class="accent">味</span>がする？</h3>
        <p>甘酒のような甘口から、ヨーグルトのような酸味のあるもの、発泡するものまでさまざまです。米粒が残る、とろりとした口当たりが共通点です。くわしくは上の「味わいと造り」へ。</p>
        <h3 class="sub-h tight">どぶろくを<span class="accent">家で造って</span>もいい？</h3>
        <p>いいえ。家庭で造ることは法律で禁じられています。製造免許を受けずに、アルコール分1度以上の酒や、酒母・もろみを造ると、酒税法違反になります（10年以下の拘禁刑または100万円以下の罰金）。梅酒づくりのような例外は、自分で飲むために、課税済みのアルコール分20度以上の酒に梅などを漬ける場合に限られます。米・麦などの穀類やそのこうじ、ぶどうなどは混ぜられず、漬けたあとに発酵させることも、販売することもできません（国税庁）。</p>
        <h3 class="sub-h tight">どぶろく特区とは？</h3>
        <p>構造改革特別区域法の特例です。国の認定を受けた特区の中で、農家民宿などを営む農業者が、自ら生産した米（これに準ずるものを含む）でこさない濁酒を自分の製造場で造る場合に、年6キロリットルの最低製造数量が適用されません。製造免許は必要です。</p>
        <h3 class="sub-h tight">開けるときに<span class="accent">吹きこぼれ</span>ませんか？</h3>
        <p>生タイプや活性タイプは瓶内で発酵が続いていることがあり、勢いよく噴き出すことがあります。<strong>よく冷やし、瓶を立てたまま、栓を少しずつ開けてはガスを逃がす</strong>——これを数回くり返すのが基本です。シンクの上で開けると安心です。商品に開け方の案内があれば、それに従ってください。</p>
        <h3 class="sub-h tight">どこで<span class="accent">買え</span>ますか？</h3>
        <p>酒販店、蔵の直売所や公式の通販、ネット通販、ふるさと納税などで買えます。入口ごとの違いは<a href="doko-de-kaeru.html">クラフトサケはどこで買える？</a>にまとめています。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("11", "READ ON / もっと味わう")}
      <div class="prose">
        <p>どぶろくの原点にある製法や、麹だけで醸す酒、クラフトサケという枠組みそのものも知れば、一杯の奥行きがさらに増す。</p>
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
          <a href="craftsake-towa.html">
            <div class="readmore__k">KNOW</div>
            <div class="readmore__t">クラフトサケとは</div>
          </a>
        </div>
      </div>
    </section>

  </div>
"""
    html = page_head("どぶろくとは？にごり酒・甘酒・マッコリとの違いを表で解説",
                     "どぶろくは、もろみをこさずに仕上げた米の酒（酒税法上は「その他の醸造酒」）。にごり酒は粗くこした日本酒、米麹の甘酒はアルコール1%未満でお酒ではなく、マッコリは韓国の濁り酒。違いを比較表とラベルの見分け方で解説します。",
                     "/guide/doburoku.html", "article")
    html += masthead(article_masthead_label("doburoku"), "A Field Guide")
    html += article_crumbs("doburoku")
    html += hero(
        article_eyebrow("doburoku"),
        'どぶろくとは。<br><span class="accent">こさない</span>という選択。',
        "白く濁った米の酒。にごり酒や甘酒、マッコリとはどう違う？「こさない」一工程から、味わい、造り方、飲み方まで。")
    html += body
    html += footer()
    return html


def build_doko_de_kaeru():
    # ふるさと納税の確認済み蔵。直書きすると furusato_data の更新から取り残されるので導出する
    import furusato_data
    _fur_slugs = furusato_data.all_confirmed_slugs()
    _fur_links = "、".join(
        f'{by_slug(s)["prefecture"]}{by_slug(s)["city"]}の<a href="../brewery/{s}.html">{by_slug(s)["name"]}</a>'
        for s in _fur_slugs[:5])
    _fur_n = len(_fur_slugs)

    ch_terms = term_grid([
        ("蔵の公式オンラインショップ", "OFFICIAL EC", "いちばん確実で、品揃えも最新。Shopify・BASE・STORES などで蔵が直接運営する。限定品はここにしか出ないことが多い。"),
        ("通販モール", "ONLINE MALL", "楽天市場やYahoo!ショッピング、Amazonに出店する酒販店経由。ポイントが使え、まとめ買いしやすい。ただし取扱いは蔵によって大きく差があり、同じ銘柄でもモールによって扱いが違う。"),
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
        <p>saketto が収録{S['breweries']}蔵の全銘柄を実際に検索して調べたところ、<strong>通販モールでの取扱いを確認できなかった蔵が{B['breweries_without_shop']}あった</strong>。{_no_shop_examples()}などがそうだ。<strong>「モールで見つからない＝手に入らない」ではない</strong>。蔵の名前で公式サイトを開くのが近道になる。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("04", "MALL / 通販モールという近道")}
      <div class="prose">
        <h2 class="sub-h">出ている蔵は、<span class="accent">かなり出ている</span>。</h2>
        <p>楽天市場などのモールには、クラフトサケを積極的に扱う酒販店がいる。ポイントが使え、他の買いものとまとめられるのが利点だ。ただし<strong>取扱いの濃淡が激しい</strong>。{_many_shop_examples()}のように多数の銘柄が並ぶ蔵がある一方、1本も出ていない蔵も珍しくない。</p>
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
        <p>saketto が公式に確認できた範囲では、{_fur_links}をはじめ、<strong>計{_fur_n}蔵</strong>の返礼品の出品を確認できている。<strong>通販モールには出ていないのに、ふるさと納税でだけ買える銘柄もある</strong>ので、見落とさないでほしい。制度のきほんや申し込みの流れは<a href="furusato.html">ふるさと納税の解説記事</a>にまとめた。</p>
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
        <p>たとえば東京駅のエキナカで醸す<a href="../brewery/tokyo-station.html">東京駅酒造場</a>、大阪タカシマヤ地下の<a href="../brewery/heiwa-namba.html">平和どぶろく難波醸造所</a>と日本橋兜町の<a href="../brewery/heiwa-kabutocho.html">兜町醸造所</a>、仙台駅構内の約3.4坪で、8Lタンクの超小仕込みを毎日重ねる<a href="../brewery/fermenteria.html">Fermenteria</a>。神戸の<a href="../brewery/hakutsuru-sakecraft.html">HAKUTSURU SAKE CRAFT</a>は、ナンバリングされたシリーズが各回本数限定で、公式の発表では白鶴酒造資料館で販売される。<strong>「買えない」のではなく、「その場所へ行って出会う酒」として設計されている</strong>。旅の目的地にする価値がある。訪ねて飲める蔵の一覧は<a href="nomeru-kura.html">クラフトサケが飲める醸造所</a>へ。</p>
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
        <h2 class="sub-h">{S['brands']}銘柄を、<span class="accent">全部検索</span>してみた。</h2>
        <p>「クラフトサケは手に入りにくい」とよく言われる。では実際どれくらいなのか。saketto では収録している<strong>{S['brands']}銘柄すべてを楽天市場・Yahoo!ショッピング・Amazonで実際に検索し、購入できる出品があるかを一件ずつ確認</strong>している。銘柄名だけでなく蔵名でも検索し、その蔵の出品を一覧して突き合わせる方法をとっている。</p>
        <p>結果は、<strong>購入リンクを出せたのが{B['buyable']}銘柄</strong>。全体の約{B['buyable'] * 10 // S['brands']}割である。残る{B['not_buyable']}銘柄については、確認した時点で取扱いが見つからなかった。<strong>収録の半分以上は、通販モールでは買えない</strong>——これがこのジャンルの現実だ。</p>
        <p>蔵の単位で見ると、さらにはっきりする。<strong>{S['breweries']}蔵のうち{B['breweries_without_shop']}蔵は、通販モールでの取扱いを一件も確認できなかった</strong>。自社ECと店頭だけで売る方針の蔵、要冷蔵の生酒しか造っていない蔵、そもそも醸造所併設の店でしか出さない蔵。<strong>買えないのではなく、売り方がそういう設計になっている</strong>のだ。</p>
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
    html += article_crumbs("doko-de-kaeru")
    html += hero(
        article_eyebrow("doko-de-kaeru"),
        'どこで買える？<br><span class="accent">4つの入口</span>を知る。',
        "近所の酒屋で見かけないのは、人気がないからではない。流通の量と経路が、そもそも違うからだ。")
    html += body
    html += footer()
    return html


def build_furusato_guide():
    """ふるさと納税×クラフトサケの解説記事。
    蔵の一覧・件数・寄附額はすべて furusato_data から導出する（直書きしない）。
    制度の説明は総務省の公表基準に基づく一般的な内容に留め、詳細は公的情報の確認を促す。"""
    slugs = FD.all_confirmed_slugs()
    n_kura = len(slugs)
    items_all = [i for s in slugs for i in FD.items_of(s)]
    live = [i for i in items_all if i.get("accepting", True)]
    yens = sorted(y for i in live if (y := i.get("yen")))
    yen_min, yen_max = (yens[0], yens[-1]) if yens else (0, 0)
    n_under20k = sum(1 for y in yens if y < 20000)

    # ポータル別の取扱蔵数（受付中のみ）
    portal_rows = ""
    for p in FD.PORTAL_ORDER:
        cnt = sum(1 for s in slugs if p in FD.portals_of(s))
        if cnt:
            portal_rows += (f'<tr><td class="nm">{FD.PORTAL_NAMES[p]}</td>'
                            f'<td class="p">{cnt}蔵</td></tr>\n')

    # 蔵ごとの一覧（受付中の額帯・ポータル数・状況）
    kura_rows = ""
    for s in slugs:
        b = by_slug(s)
        band = FD.price_range(s)
        band_txt = (f"{band[0]:,}円" if band and band[0] == band[1]
                    else f"{band[0]:,}〜{band[1]:,}円" if band else "—")
        n_portal = len(FD.portals_of(s))
        status = "受付中" if FD.is_accepting(s) else "品切れ中"
        kura_rows += (
            f'<tr><td class="nm"><a href="../brewery/{s}.html">{b["name"]}</a></td>'
            f'<td>{FD.FURUSATO[s].get("city") or b["prefecture"]}</td>'
            f'<td class="p">{band_txt}</td>'
            f'<td>{n_portal}ポータル</td><td>{status}</td></tr>\n')

    ch_terms = term_grid([
        ("控除の仕組み", "TAX CREDIT", "寄附額のうち2,000円を超える部分が、収入や家族構成に応じた上限の範囲内で所得税・住民税から控除される制度。上限は総務省や各ポータルの目安表・シミュレーションで確認できる。"),
        ("ワンストップ特例", "ONE-STOP", "もともと確定申告が不要な給与所得者などで、1年の寄附先が5自治体以内なら、申請書の提出だけで確定申告なしに控除を受けられる仕組み。"),
        ("返礼品の基準", "STANDARD", "返礼品は「調達費が寄附額の3割以下」「地場産品」という総務省の基準の下で提供される。蔵の地元自治体だからこそ、その蔵の酒が返礼品に並ぶ。"),
        ("受付の変動", "AVAILABILITY", "クラフトサケは少量生産のため、返礼品も数量限定・季節限定が多い。品切れと再開がひんぱんに入れ替わる。"),
    ])

    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "WHY / 寄附という買い方")}
      <div class="prose">
        <p class="lead">通販モールに出ていない酒が、<span class="accent">ふるさと納税</span>でだけ手に入ることがある。クラフトサケの蔵の多くは地域と結びついて立ち上がっており、蔵の地元自治体の返礼品にその酒が並ぶからだ。</p>
        <p>saketto が収録{S['breweries']}蔵の返礼品を一次ソースで確認したところ、<strong>{n_kura}蔵</strong>で返礼品の出品を確認できた。寄附額の目安は<strong>{yen_min:,}円から{yen_max:,}円</strong>。寄附は蔵の地元への直接の応援にもなる——飲み手にとっても造り手にとっても、うれしい買い方だ。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("02", "SYSTEM / 制度のきほん")}
      <div class="prose">
        <h2 class="sub-h">2,000円の自己負担で、<span class="accent">地元の酒</span>が届く。</h2>
        <p>ふるさと納税は、応援したい自治体に寄附をすると、<strong>寄附額のうち2,000円を超える部分が所得税・住民税から控除される</strong>制度だ（収入・家族構成に応じた上限あり）。返礼品として地場産品を受け取れるため、上限の範囲内なら実質2,000円の負担で蔵の酒が手に入る計算になる。</p>
        <p>大切なのは<strong>自分の控除上限を先に知っておく</strong>こと。上限を超えた分は純粋な寄附（自己負担）になる。上限額は総務省のふるさと納税ポータルサイトや、各ポータルのシミュレーションで確認できる。</p>
      </div>
      {ch_terms}
      <div class="prose">
        <div class="callout">
          <div class="callout__label">制度の詳細は公的情報で</div>
          <p>ここに書いた仕組みは2026年9月時点の一般的な説明です。控除の条件・手続き・期限の詳細は、総務省のふるさと納税ポータルサイトと各自治体の案内を必ずご確認ください。</p>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("03", "HOW / 申し込みの流れ")}
      <div class="prose">
        <h2 class="sub-h">流れは、<span class="accent">4ステップ</span>。</h2>
        <p><strong>① 控除上限を確認する</strong>——シミュレーションで自分の目安額を知る。<strong>② ポータルで申し込む</strong>——蔵のページから辿るか、ポータルで蔵名・銘柄名を検索して寄附する。<strong>③ 控除の手続き</strong>——ワンストップ特例の申請書を出すか、確定申告で寄附金控除を申告する。<strong>④ 返礼品を受け取る</strong>——クラフトサケは要冷蔵の生酒が多いので、受け取れる時期に申し込むのがコツだ。</p>
        <p>なお、<strong>酒類の返礼品は20歳以上のみ</strong>申し込める。ポータルの申込画面でも確認される。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("04", "DATA / 確認できている蔵")}
      <div class="prose">
        <h2 class="sub-h">一次ソース確認済み、<span class="accent">{n_kura}蔵</span>。</h2>
        <p>saketto では、返礼品ページのURLまで実際に開いて確認できたものだけを掲載している。現在確認できているのは次の{n_kura}蔵。寄附額{yen_min:,}円台からの返礼品もあり、{n_under20k}件は2万円未満で申し込める（額・受付状況は確認時点のもの。変動が早いので、最新はリンク先で確認してほしい）。</p>
      </div>
      <div style="overflow-x:auto">
      <table class="cmp">
        <thead><tr><th>蔵</th><th>出品自治体</th><th>寄附額の目安</th><th>取扱</th><th>状況</th></tr></thead>
        <tbody>
{kura_rows}        </tbody>
      </table>
      </div>
      <div class="prose">
        <div class="pill-links">
          <a href="../furusato/">ふるさと納税の返礼品を一覧で見る<span class="arr">→</span></a>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("05", "PORTAL / どのポータルで探すか")}
      <div class="prose">
        <h2 class="sub-h">同じ返礼品でも、<span class="accent">入口</span>はいくつもある。</h2>
        <p>ふるさと納税のポータルは複数あり、<strong>同じ蔵の返礼品が複数のポータルに並んでいる</strong>ことも多い。普段使うポイント経済圏や、使い慣れた画面で選べばいい。saketto が確認できた取扱は次のとおり。</p>
      </div>
      <div style="overflow-x:auto">
      <table class="cmp">
        <thead><tr><th>ポータル</th><th>取扱を確認できた蔵</th></tr></thead>
        <tbody>
{portal_rows}        </tbody>
      </table>
      </div>
      <div class="prose">
        <p>どのポータルにどの返礼品があるかは、<a href="../furusato/">ふるさと納税ハブ</a>で蔵ごとにまとめている。ポータルを横断して見比べてから申し込むのが確実だ。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("06", "CAUTION / つまずきやすいところ")}
      <div class="prose">
        <h2 class="sub-h">品切れは、<span class="accent">ひんぱんに動く</span>。</h2>
        <p>クラフトサケの返礼品でいちばん多いつまずきは<strong>品切れ</strong>だ。少量生産ゆえに数量限定が基本で、受付と品切れが短いサイクルで入れ替わる。品切れでも受付が戻ることは珍しくないので、気になる蔵はときどき見に行ってほしい。</p>
        <p>もうひとつは<strong>受け取りのタイミング</strong>。多くが要冷蔵の生酒で、長期の不在にはあわせにくい。発送時期の記載を確認し、受け取れる時期に申し込むこと。年末は控除の締切（その年の12月31日まで）に向けて申し込みが集中し、品切れも起きやすい。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("07", "FAQ / よくある質問")}
      <div class="prose">
        <h2 class="sub-h tight">実質2,000円って、<span class="accent">本当</span>ですか？</h2>
        <p>控除上限の範囲内で寄附した場合、自己負担は2,000円になります。ただし上限は収入や家族構成で大きく変わるため、先にシミュレーションで確認するのが前提です。上限を超えた分は控除されません。</p>
        <h2 class="sub-h tight">返礼品はどれくらいで<span class="accent">届き</span>ますか？</h2>
        <p>自治体・返礼品によってさまざまです。数量限定の酒は仕込みや瓶詰めのタイミングに合わせた発送になることもあります。各返礼品ページの発送時期の記載を確認してください。</p>
        <h2 class="sub-h tight">品切れの返礼品は、<span class="accent">もう買えない</span>のですか？</h2>
        <p>受付が再開されることは珍しくありません。saketto では品切れ中の返礼品も「品切れ中」と明記して掲載を続けています。再開を待つ間に、<a href="doko-de-kaeru.html">ほかの入手経路</a>を当たるのも手です。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("08", "NEXT / 次に読む")}
      <div class="prose">
        <h2 class="sub-h">寄附の先に、<span class="accent">蔵の物語</span>がある。</h2>
        <p>ふるさと納税は、蔵の地元とのつながりをいちばん感じられる買い方だ。寄附した蔵のページで、その土地でなぜ酒を醸すのかを読んでから開栓すると、一杯の味わいが変わってくる。</p>
        <div class="pill-links">
          <a href="../furusato/">返礼品の一覧を見る<span class="arr">→</span></a>
          <a href="../brewery/">蔵の物語を読む<span class="arr">→</span></a>
          <a href="doko-de-kaeru.html">ほかの買い方を知る<span class="arr">→</span></a>
        </div>
      </div>
    </section>

  </div>
"""
    html = page_head("ふるさと納税でクラフトサケを手に入れる — 確認済みの蔵と申し込みの流れ",
                     f"ふるさと納税の返礼品としてクラフトサケを受け取る方法。制度のきほん・申し込みの流れから、saketto が一次ソースで確認した{n_kura}蔵の返礼品、ポータル別の取扱、品切れ・要冷蔵の注意点まで。",
                     "/guide/furusato.html", "article")
    html += masthead(article_masthead_label("furusato"), "A Field Guide")
    html += article_crumbs("furusato")
    html += hero(
        article_eyebrow("furusato"),
        '寄附して、<br><span class="accent">蔵の地元</span>から届く。',
        f"通販モールに出ていない酒が、ふるさと納税でだけ手に入ることがある。saketto が一次ソースで確認できた{n_kura}蔵の返礼品と、制度のきほんをまとめた。")
    html += body
    html += footer()
    return html


def build_zenkoji():
    # 🔴 嘘ゼロ（2026-10-29 確認）
    #   酒税法 第3条第7号（清酒＝米、米こうじ及び水…こしたもの）https://laws.e-gov.go.jp/law/328AC0000000006
    #   麹100%だと日本酒と認められない・一般的な麹割合は約20%前後・「麴99%」：土田酒造 公式 https://tsuchidasake.jp/news/kouji992026/
    #   清酒の全麹は蒸米をほんの少量使う・麹歩合を上げると発酵が旺盛で酸が高く糖化が進みやすい：SAKE Street（専門メディア）
    #     https://sakestreet.com/ja/media/how-does-the-amount-of-rice-koji-and-water-affect-flavor-of-sake
    #   「十割麹」の呼び名・米麹だけの酒は「その他の醸造酒」の免許で造る（弥栄醸造 代表）：SAKE Street
    #     https://sakestreet.com/ja/media/pioneers-iyasaka-brewery-niigata ／代表の note https://note.com/ikko2535/n/n1c7b3b38e1e9
    #   特定名称の清酒は こうじ米の使用割合15%以上（上限の定めは見当たらない）：国税庁 https://www.nta.go.jp/taxes/sake/hyoji/seishu/gaiyo/02.htm
    #   泡盛は黒麹の全麹仕込み：JETRO https://www.jetro.go.jp/agriportal/pickup/awamori.html ／国税庁「酒類の表示に関する説明事項」（泡盛＝米こうじ〔黒こうじ菌〕及び水）
    #   国菌（2006年10月 日本醸造学会）：https://www.jozo.or.jp/gakkai/kokkin20/
    #   書かないこと：「磨きすぎると麹菌が繁殖しにくい」（出典なし）／精米歩合の件数の直書き／「全量麹仕込み」が全麹と同義という断定
    from gen_axes_pages import brands_in_genre as _in_genre
    fk = [(b, nm, href) for b in _BREWERIES for nm, href in _in_genre(b, "full-koji")]
    fk_html = "".join(f'<li><a href="{href}">{nm}</a>（<a href="../brewery/{b["slug"]}.html">{b["name"]}</a>・{b["prefecture"]}）</li>'
                      for b, nm, href in fk)

    cmp_rows = [
        ("ふつうの日本酒", "約2割前後", "使う（米の大半）", "清酒（日本酒）"),
        ("全麹仕込みの日本酒", "ほぼすべて（例：99%）", "<strong>ほんの少し使う</strong>", "清酒（日本酒）"),
        ("全麹酒・十割麹酒", "<strong>100%</strong>", "使わない", "その他の醸造酒"),
    ]
    cmp_html = "".join(f'            <tr><td class="nm">{a}</td><td data-label="麹の割合">{b}</td><td data-label="麹にしない米（掛米）">{c}</td><td data-label="ラベルの品目">{d}</td></tr>\n'
                       for a, b, c, d in cmp_rows)

    koji_terms = term_grid([
        ("麹（こうじ）", "KOJI", "蒸した米に麹菌を生やしたもの。米のでんぷんを糖に変える酵素をつくる。"),
        ("掛米（かけまい）", "KAKEMAI", "麹にせず、蒸しただけで仕込みに加える米。ふつうの日本酒では米の大半がこれ。"),
        ("麹歩合（こうじぶあい）", "KOJI RATIO", "使う米のうち、麹にした米の割合。ふつうの日本酒は約2割前後。"),
        ("全麹・十割麹", "FULL KOJI", "麹歩合をほぼ、または完全に100%にする造り。弥栄醸造は十割そばにならって「十割麹」と呼ぶ。"),
    ])

    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "WHAT IS / 全麹仕込みとは")}
      <div class="prose">
        <p class="lead">全麹仕込み（ぜんこうじじこみ）とは、酒の仕込みに使う米を、<span class="accent">すべて、またはほぼすべて麹にして</span>醸す造り方。ふつうの日本酒では麹にする米は全体の2割前後で、残りは蒸しただけの「掛米」だ。全麹では、この掛米をほとんど、あるいはまったく使わない。</p>
        <p>麹は、米のでんぷんを糖に変える酵素をつくる、酒造りの要だ。それを何倍も使うのだから、できる酒の性格も大きく変わる。専門メディアの SAKE Street は、麹の割合を増やすと発酵が旺盛になり、酸が高く、糖化も進みやすくなると解説している。<strong>酸や旨みの濃い、濃醇な酒になりやすい</strong>造りだ。</p>
        <p>よく聞かれることに、先に答えておく。</p>
        <ul class="answer-list">
          <li><strong>日本酒なの？</strong>　麹が<strong>100%</strong>だと日本酒（清酒）にはならず、「その他の醸造酒」になる。日本酒として売られている全麹仕込みは、掛米をほんの少しだけ使っている。</li>
          <li><strong>十割麹とは違う？</strong>　十割麹は、麹100%をはっきり示す呼び方。新潟の弥栄醸造が「十割そば」にならって使っている。「全麹」は、99%のように掛米をわずかに使うものにも使われる、少し広い言葉だ。</li>
          <li><strong>どんな味？</strong>　酸や旨みの濃い、濃醇な味になりやすいとされる。ただし軽やかに仕上げた銘柄もある。</li>
        </ul>
      </div>
      {koji_terms}
    </section>
{divider()}
    <section class="section">
{section_meta("02", "COMPARE / ふつうの日本酒との違い")}
      <div class="prose">
        <h2 class="sub-h">麹の割合で、<span class="accent">3つ</span>に分かれる。</h2>
        <p>同じ「全麹」でも、麹が99%か100%かで、法律上の区分が変わる。ふつうの日本酒と並べるとわかりやすい。</p>
      </div>
      <div class="cmp-wrap">
        <table class="cmp cmp--compare">
          <thead><tr><th>種類</th><th>麹の割合</th><th>麹にしない米（掛米）</th><th>ラベルの品目</th></tr></thead>
          <tbody>
{cmp_html}          </tbody>
        </table>
      </div>
      <p class="pick-imgnote">出典：酒税法 第3条第7号、土田酒造 公式ニュース（2026年10月16日）、SAKE Street。麹の割合は蔵や銘柄によって違います。</p>
    </section>
{divider()}
    <section class="section" id="seishu">
{section_meta("03", "THE LINE / なぜ100%だと日本酒にならない？")}
      <div class="prose">
        <h2 class="sub-h">99%なら日本酒、100%なら<span class="accent">その他の醸造酒</span>。</h2>
        <p>酒税法は清酒を「米、米こうじ及び水を原料として発酵させて、こしたもの」と定めている。<strong>「米」と「米こうじ」が別々の原料として並んでいる</strong>のがポイントだ。麹ももとは米だが、蔵や専門メディアは、麹にしない米を使わず麹だけで造った酒は、この定義にあたらないと説明している。</p>
        <p>たとえば群馬の土田酒造は、麹の割合を99%にした「Tsuchida 麴99%」について、公式サイトで「なぜ100％使わず99％に留めるのかというと、麹を100％にすると酒税法上の規制により日本酒として認められなくなるためです」と書いている。SAKE Street も、清酒と表示するには米を原料に含める必要があるため、全麹仕込みでも麹ではない蒸米を少しだけ使う、と解説している。</p>
        <p>逆に、麹100%を選んだ蔵は、日本酒ではなく<strong>「その他の醸造酒」</strong>の免許で造る。新潟・柏崎の{kura_link("iyasaka")}の代表は、米麹だけの酒は日本酒（清酒）を名乗れない代わりに「その他の醸造酒」の免許で造ることができる、と話している（SAKE Street）。日本酒の免許との関係は<a href="craftsake-towa.html">クラフトサケとは</a>で説明している。</p>
        <h3 class="sub-h tight">純米酒の条件にも、麹の<span class="accent">上限はない</span></h3>
        <p>国税庁の表示基準では、純米酒や吟醸酒などの「特定名称」を名乗るには、麹にした米の割合が<strong>15%以上</strong>であることが条件だ。上限は定められていない。麹を増やすこと自体は日本酒の造りの範囲で、ぶつかるのは「米を原料に含める」という定義のほうだ。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("04", "TASTE / 味と、手間")}
      <div class="prose">
        <h2 class="sub-h">濃くなりやすいが、<span class="accent">重いとは限らない</span>。</h2>
        <p>麹の割合を増やすと、酵素や麹由来の成分がそれだけ多く仕込みに入る。弥栄醸造を紹介した SAKE Street の記事は、麹の割合が多いと酸味や旨みの強い濃醇な酒になると書いている。土田酒造も「麴99%」の味を「麹由来の旨味ある甘酸っぱさ」と説明している。</p>
        <p>ただ、全部が重い酒というわけではない。弥栄醸造の「ITTEKI」について、販売店の長谷川屋は「十割麹酒というと、重たく濃醇な酒を連想する方も多いかと思われますが、むしろ味わいには軽めの印象を受けます。」と紹介している。<strong>麹の割合は味の方向を決める要素のひとつで、仕上がりは蔵の設計しだい</strong>だ。</p>
        <h3 class="sub-h tight">麹づくりの量が、<span class="accent">5倍</span>になる</h3>
        <p>麹づくり（製麹）は、蒸した米に麹菌を生やし、温度と湿度を細かく見ながら育てる、手のかかる工程だ。ふつうの日本酒が米の2割ほどを麹にするところを全量麹にすれば、<strong>麹にする米は単純に計算して5倍</strong>になる。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("05", "AWAMORI / 泡盛も全麹")}
      <div class="prose">
        <h2 class="sub-h">沖縄の泡盛は、昔から<span class="accent">全麹仕込み</span>。</h2>
        <p>全麹は新しい発明ではない。沖縄の<strong>泡盛</strong>は、黒麹菌でつくった米麹と水だけで仕込み、蒸留する酒で、JETRO も泡盛の製法を「全麹仕込み」と説明している。国税庁の表示の資料でも、泡盛は「米こうじ（黒こうじ菌を用いたものに限る。）及び水を原料として」造るものとされている。</p>
        <p>麹菌には、日本酒によく使う<strong>黄麹</strong>、焼酎に多い<strong>白麹</strong>、泡盛の<strong>黒麹</strong>がある。白麹と黒麹はクエン酸を多くつくるので、酒に酸味が出る。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("06", "IN SAKETTO / 全麹の一本を探す")}
      <div class="prose">
        <h2 class="sub-h">saketto で出会える、<span class="accent">麹だけの酒</span>。</h2>
        <p>saketto に収録しているクラフトサケのうち、全麹・十割麹の銘柄は{len(fk)}本。どれも日本酒ではなく「その他の醸造酒」として造られている。</p>
        <ul class="answer-list">
          {fk_html}
        </ul>
        <p>{kura_link("iyasaka")}の「ITTEKI」は、代表の坂本さんが阿部酒造で委託醸造した最初の酒で、白米を使わず米麹だけで造っている（代表の note より）。{kura_link("pukupuku")}の「木桶発酵 全麹酒 雫取り」は、全麹に<a href="kioke.html">木桶仕込み</a>を重ねた高価格帯の一本だ（販売店の表示では品目は「その他醸造酒」）。滋賀の{kura_link("happy-taro")}は、公式に「全糀仕込み」と書く「やまのかみさん 大原の赤紫蘇」のほか、原材料が米麹と副原料だけのどぶろくを造っている。日本酒として造られた全麹仕込みなら、土田酒造の「Tsuchida 麴99%」のような例もある（saketto には未収録）。</p>
        <div class="pill-links">
          <a href="../genre/#g-full-koji">ジャンル「全麹酒」から<span class="arr">→</span></a>
          <a href="../brewery/iyasaka.html">弥栄醸造の銘柄<span class="arr">→</span></a>
          <a href="../brewery/pukupuku.html">ぷくぷく醸造の銘柄<span class="arr">→</span></a>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("07", "HOW TO DRINK / 飲み方")}
      <div class="prose">
        <h2 class="sub-h">濃いから、<span class="accent">少しずつ</span>。</h2>
        <p>甘みと酸の強い全麹の酒は、小さめのグラスで少しずつ飲むと味の変化を追いやすい。冷やして飲みはじめ、グラスの中で温度が上がるにつれて甘みや香りがどう開くかを見るのもいい。生の酒は要冷蔵のものが多いので、ラベルの保存方法を確かめておこう。温度や器の選び方は<a href="nomikata.html">飲み方・楽しみ方</a>にまとめている。</p>
      </div>
    </section>
{divider()}
    <section class="section" id="faq">
{section_meta("08", "FAQ / よくある質問")}
      <div class="prose">
        <h3 class="sub-h tight">全麹仕込みのお酒は、日本酒ですか？</h3>
        <p>ラベルの品目が「清酒」なら日本酒です。麹を100%にすると清酒の定義にあたらず「その他の醸造酒」になるため、日本酒として売られている全麹仕込みは、掛米をほんの少し使っています（例：土田酒造「Tsuchida 麴99%」）。</p>
        <h3 class="sub-h tight">全麹・十割麹・麹100%は同じ意味ですか？</h3>
        <p>ほぼ同じ造りを指しますが、「全麹」は99%のように掛米をわずかに使う日本酒にも使われます。「十割麹」「麹100%」は、掛米をまったく使わないことをはっきり示す言い方です。100%かどうかは、ラベルの品目や蔵の説明で確かめてください。</p>
        <h3 class="sub-h tight">甘酒とは違うのですか？</h3>
        <p>違います。米麹の甘酒は、麹の酵素ででんぷんを糖に変えただけの飲みもので、アルコール発酵をしていません。全麹の酒は、麹でつくった糖を酵母がアルコールに変えたお酒です。詳しくは<a href="doburoku.html#amazake">どぶろくと甘酒の違い</a>で説明しています。</p>
        <h3 class="sub-h tight">全麹の酒は甘口ばかりですか？</h3>
        <p>麹の割合が多いと酸や旨みの濃い、濃醇な酒になりやすいとされますが、軽やかに仕上げた銘柄もあります。銘柄ページの公式の味の説明を参考にしてください。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("09", "READ ON / もっと味わう")}
      <div class="prose">
        <p>麹の力を突き詰めたのが全麹なら、器の力を借りるのが木桶仕込み、植物の力を借りるのが花酛だ。造りのことばを知るほど、一本の設計が読めるようになる。</p>
        <div class="callout">
          <div class="callout__label">楽しむ前に</div>
          <p><strong>20歳未満の飲酒は法律で禁じられています。</strong>　飲酒運転は法律で禁止されています。妊娠中・授乳期の飲酒はお控えください。適量を守り、自分のペースでお楽しみください。</p>
        </div>
        <div class="readmore">
          <a href="kioke.html">
            <div class="readmore__k">あわせて読む</div>
            <div class="readmore__t">木桶仕込みとは</div>
          </a>
          <a href="craftsake-towa.html">
            <div class="readmore__k">KNOW</div>
            <div class="readmore__t">クラフトサケとは</div>
          </a>
        </div>
      </div>
    </section>

  </div>
"""
    html = page_head("全麹仕込みとは？日本酒との違い・麹100%が清酒にならない理由",
                     "全麹仕込みとは、仕込みに使う米をすべて（またはほぼすべて）麹にして醸す造り。ふつうの日本酒（麹は2割前後）との違いを表で整理し、麹100%だと日本酒にならない理由、味の特徴、泡盛との関係、saketto で買える全麹酒まで解説します。",
                     "/guide/zenkoji.html", "article")
    html += masthead(article_masthead_label("zenkoji"), "A Field Guide")
    html += article_crumbs("zenkoji")
    html += hero(
        article_eyebrow("zenkoji"),
        '全麹仕込みとは。<br>米を、<span class="accent">すべて麹に</span>。',
        "ふつうの日本酒なら2割ほどの麹を、ほぼ全量に。99%なら日本酒、100%なら「その他の醸造酒」。麹だけで醸す酒の仕組みと味を、公式情報から。")
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
        <p>収録{S['breweries']}蔵のうち、<strong>2024年以降に立ち上がった蔵が{S['since2024']}</strong>{('（うち開業準備中が' + str(S['pending_breweries']) + '）') if S['pending_breweries'] else ''}。半数以上が、ここ2〜3年に集中している計算になる。<strong>これは一過性のブームというより、酒づくりの入口が構造的に変わったということだ</strong>。</p>
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
        <p>宮城の<a href="../brewery/fermenteria.html">Fermenteria</a>は仙台駅のエキナカで、東京の<a href="../brewery/tokyo-station.html">東京駅酒造場</a>は東京駅のエキナカで醸す。沖縄の<a href="../brewery/nomu.html">NOMU醸造所</a>はコザ一番街の商店街に、大阪の<a href="../brewery/adachi-noujo.html">足立農醸</a>は高槻の団地内に立つ。<a href="../brewery/heiwa-namba.html">平和どぶろく難波醸造所</a>が構えるのは、大阪タカシマヤの地下だ。<strong>造る場所と飲む場所が同じ</strong>——搾りたてをその場で出すという、これまでできなかった体験が成立している。訪ねて飲める蔵は<a href="nomeru-kura.html">クラフトサケが飲める醸造所</a>にまとめた。</p>
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
          <a href="../brewery/">収録{S['breweries']}蔵を一覧で見る<span class="arr">→</span></a>
          <a href="../region/">地域から探す<span class="arr">→</span></a>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("05", "MAP / 地図で見る")}
      <div class="prose">
        <h2 class="sub-h">{S['prefectures']}の都道府県に、<span class="accent">散らばっている</span>。</h2>
        <p>saketto 収録の{S['breweries']}蔵{('（開業準備中の' + str(S['pending_breweries']) + '蔵を含む）') if S['pending_breweries'] else ''}を地域で数えると、分布に特徴が見えてくる。<strong>{S['region_breakdown']}</strong>。日本酒どころに偏るでもなく、都市に集まるでもなく、<strong>全国に薄く広がっている</strong>のがクラフトサケの特徴だ。</p>
        <p>複数の蔵がある都道府県は{S['multi_prefectures']}つ。<strong>{S['multi_pref_breakdown']}</strong>で、残りは1県1蔵。全体で{S['prefectures']}の都道府県にまたがっている計算になる。<strong>まだ空白の県のほうが多い</strong>ということでもあり、この地図はこれから埋まっていく余地が大きい。</p>
        <p>興味深いのは、既存の日本酒の勢力図とずれていることだ。酒どころとして知られる新潟に{S['pref_counts'].get('新潟県', 0)}蔵あるのは順当だが、<strong>東京に{S['pref_counts'].get('東京都', 0)}蔵</strong>というのは従来の酒蔵の分布では考えにくい。駅ナカや商店街に置ける小さな設備だからこそ、都心にも蔵が立つ。<strong>沖縄にクラフトサケの蔵がある</strong>のも、泡盛の島という前提を思えば新しい動きだ。</p>
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
        <p>saketto が収録する{S['breweries']}蔵のうち、協会に加盟しているのは{S['assoc_breweries']}蔵。<strong>加盟していない蔵のほうが多い</strong>のは、この領域がまだ広がり続けている証拠でもある。大手酒造の実験的ブランドから、地域おこしとして始まった蔵、駅のエキナカに立つ小さな醸造所まで——出自も規模も動機もばらばらな造り手が、「米で自由に醸す」という一点でゆるやかにつながっている。</p>
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
        <p>明確な統計はありません。協会加盟蔵のほか、加盟せずに醸す蔵、大手酒造の実験ブランド、準備中の蔵まで含めると、線の引き方で数が変わるためです。saketto では一次ソースで確認できた蔵を収録しており、現在{S['breweries']}蔵を掲載しています。</p>
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
                     f"駅構内、商店街、団地、離島。これまで酒蔵がなかった場所にクラフトサケの醸造所が次々と生まれている。saketto収録{S['breweries']}蔵の開業年から、免許制度・立地・協会という3つの視点でいま何が起きているのかを読み解きます。",
                     "/guide/new-breweries.html", "article")
    html += masthead(article_masthead_label("new-breweries"), "A Field Guide")
    html += article_crumbs("new-breweries")
    html += hero(
        article_eyebrow("new-breweries"),
        '新しい蔵が、<br><span class="accent">街の中</span>に立つ。',
        "駅のエキナカ、商店街のアーケード、団地の一角。酒蔵の常識が、この5年で書き換わった。")
    html += body
    html += footer()
    return html


# ────────────── 記事：クラフトサケが飲める醸造所 ──────────────
# 🔴 嘘ゼロ：本文の事実は visit_info（2026-10-28 に出典と突き合わせ済み）・breweries_master・breweries_brands にあるものだけ。
#    蔵の情報を直したら、visit_info と下の NOMERU_STORY の両方を見直すこと。

# 早見表の「場所」の列（どんな場所にあるか）
NOMERU_PLACE = {
    "konohanano": "浅草", "heiwa-kabutocho": "日本橋兜町", "tokyo-station": "東京駅 改札内",
    "ubu": "新橋 ニュー新橋ビル地下", "heiwa-namba": "大阪高島屋 地下1階", "adachi-noujo": "高槻 富田団地",
    "hakutsuru-sakecraft": "神戸 白鶴酒造資料館", "happy-taro": "長浜 湖のスコーレ",
    "haccoba": "南相馬 小高", "pukupuku": "南相馬 小高", "heiroku": "紫波 日詰平井邸",
    "mingura": "大船渡", "fermenteria": "仙台駅 1階", "ine-to-agave": "男鹿",
    "tsuchiura": "土浦駅そば", "yamane": "飯能 赤沢", "lagoon": "新潟 福島潟", "iyasaka": "柏崎",
    "librom": "福岡 高砂", "dejima-hosendo": "長崎 出島", "amanosato": "福智町",
}

# 蔵ごとの紹介文（所在地・アクセスはカードの下に別に出すので、ここには書かない）
NOMERU_STORY = {
    "konohanano": [
        "浅草で「国内外に誇れる名物の酒」を造ろうと、2020年に開いたどぶろく醸造所。若い醸造家が独立に向けて腕を磨く<strong>「新しい修行の場」</strong>という顔も持ち、3代目醸造長の「LAB」シリーズや、醸造スタッフの名を冠した「ねねRock」シリーズのように、造り手の個性がそのまま酒になっている。",
        "醸造所に併設した店「ALL (W)RIGHT -sake place-」では、自家醸造の酒のほか、<strong>100種以上の日本酒を和の肴と</strong>楽しめる。看板は米だけで醸す「ハナグモリ」。ホップとハーブの「HAZY SAKE」、鰹節の出汁で仕込む「出汁パンチ」など、ほかでは見ない酒が多いのもこの蔵らしさだ（店に並ぶ酒は時期で変わる）。どぶろくは店で常時売っていて（売り切れの日もある）、<strong>営業時間内ならガラス越しに醸造の様子をいつでも眺められる</strong>。造りの話を聞きたいときは、醸造長が不在のこともあるので事前に問い合わせを。",
    ],
    "heiwa-kabutocho": [
        "和歌山で「紀土」を醸す平和酒造が、2022年に日本橋兜町に開いたどぶろくのブルワリーパブ。<strong>造り手がその場で、できたてのどぶろくを出してくれる</strong>。米だけのプレーンに、小豆・黒豆・ホップ、そして日替わりの「本日のどぶろく」。",
        "母体の「紀土」なども飲めるので、<strong>同じ蔵元のどぶろくと日本酒を飲み比べられる</strong>のがおもしろい。こした日本酒と、こさないどぶろくの違いを、舌で確かめられる。店内では物販もある。支払いはキャッシュレスのみで、現金は使えない。",
    ],
    "tokyo-station": [
        "2020年、JR東京駅の改札内・地下1階に生まれた蔵。公式は「世界でも例を見ないエキナカにある酒蔵」と紹介している。運営ははせがわ酒店で、醸造所とテイスティングバーを併設した「はせがわ酒店 グランスタ東京店」の中にある。",
        "ここでは<strong>完成から1週間ほどの時期に、生どぶろくを少量出している</strong>。瓶詰めの商品も同じ店で買える。マンゴーやリンゴ、桃といった季節のフルーツどぶろくは季節限定で、時期が変われば並ぶ味も変わる。見学ツアーの案内はないが、コンコース側からガラス越しにタンクが、広場側の小窓からは甑（こしき）が見える。改札の内側なので、<strong>駅を利用しないときは入場券が要る</strong>。",
    ],
    "ubu": [
        "ニュー新橋ビルの地下、カウンター7席の店に併設された小さな醸造所（2025年）。公式は「新橋初の『その他の醸造酒』酒造免許を取得したマイクロブルワリー」と名乗る。店で醸した<strong>できたてのどぶろく・クラフトサケに、鮨や肴のおまかせを合わせる</strong>のがこの店のスタイルだ。",
        "使い方は二通りある。<strong>食事の時間帯は前日23時までの完全予約制</strong>で、<strong>後半のバーの時間帯は予約なしで入れる</strong>。じっくり食事と合わせる日と、仕事帰りに一杯だけの日で、使い分けられる。",
    ],
    "heiwa-namba": [
        "平和酒造のどぶろくブルワリーパブの2号店として、2025年に大阪高島屋の地下1階・西ゾーンに開いた。自社栽培の山田錦に季節の副原料を合わせ、プレーンや小豆・黒豆・ホップ・白麹のほか、桜・抹茶・柚子といった季節のどぶろくも造っている。",
        "兜町と同じく、母体の「紀土」なども飲める。<strong>百貨店での買い物のついでに、できたてのどぶろくを一杯</strong>という寄り方ができる。飲食とは別に、店内で物販の時間も設けられている。定休日は高島屋に準じる。",
    ],
    "adachi-noujo": [
        "高槻市の富田団地の1階にある、「日本初の団地酒蔵」を掲げる蔵（2024年）。高槻産の米で醸し、大阪の農産物を発酵の途中で加える。ライチ果汁の「MIYOI -ライチ-」、かつお節と昆布の出汁を使う燗酒専用の「MIYOI -旨すぎて御燗弁。-」と、発想の幅が広い。発酵させたノンアルコールの飲みものも造っている。",
        "雑誌のWeb版「@DIME」（2025年6月14日）は、醸造所と立ち飲みバーがひとつになった「酒蔵Bar」で飲めると紹介している。公式サイトには店の案内が見当たらないので、訪ねる前に問い合わせを。",
    ],
    "hakutsuru-sakecraft": [
        "大手酒造の白鶴酒造が、神戸・住吉の白鶴酒造資料館の中に置いたマイクロブルワリー（2024年）。No.1、No.2……と番号を振ったシリーズで、<strong>各回本数限定、同じ酒質は二度と造らない</strong>。ホップを使ったNo.4、神戸産いちご「あきひめ」を使ったNo.6のように、毎回が一度きりの酒だ。",
        "公式の発表では、できた酒は<strong>資料館でだけ販売</strong>される。資料館は入館無料の自由見学で、ガラス越しに醸造設備や発酵中の醪（もろみ）が見られる。その場で飲める案内は見当たらないので、<strong>ここは「見て、買いに行く」蔵</strong>と考えたい。限定本数なので売り切れることもある。10名以上の団体は、資料館のオンライン予約が要る。",
    ],
    "happy-taro": [
        "滋賀・長浜で2017年から醸す、糀屋（こうじや）でもある蔵。糀屋ならではの完熟糀と伊吹山の伏流水で、顔の見える生産者の素材を醸す。茶葉や八朔、ホップを使う「something happy」シリーズなど、副原料の幅も広い。",
        "醸造所は「湖のスコーレ」の中にあり、店舗には試飲スペース「HAKKO SALON」がある。<strong>店でしか買えないクラフトどぶろく</strong>も扱っている。醸造所見学は完全予約制で、2〜8名・約90分。<strong>1人でも、2名分の料金で受け付けている</strong>。専用駐車場はないので、電車で行くのがいい。臨時の営業・休業はSNSで告知される。",
    ],
    "haccoba": [
        "かつての民俗的なドブロクづくりを、クラフトビールの自由なカルチャーで編み直す——クラフトサケの先駆けのひとつ（2021年、福島・南相馬市小高区）。東北の一部に伝わるドブロク製法「花酛（はなもと）」の復刻や、ホップ、ベルギービールの製法まで試してきた。",
        "醸造所とパブが一体の「haccoba 小高醸造所 &KITCHEN」では、<strong>酒蔵を眺めながら酒と料理を楽しめる</strong>。ただしブリューパブは<strong>金・土・日の夜だけ、予約制（公式のフォームかメール）、8席</strong>。同じ建物のショップは別の時間帯に開いていて、小高駅舎の中の「haccoba 小高駅舎醸造所&PUBLIC MARKET」も公式の販売先として案内されている。",
    ],
    "pukupuku": [
        "haccoba の醸造責任者だった立川氏が独立し、同じ小高で、古民家を改装して2024年秋に開いた蔵。<strong>酵母を加えない自然発酵</strong>とビールの技法を掛け合わせ、ホップサケや、木桶で仕込む全麹酒を醸す。",
        "酒蔵に併設した角打ちで飲めて、ボトルも買える（自社のオンラインストアは置いていない）。<strong>haccoba と同じ小高区なので、2蔵をめぐる旅</strong>もできる。番地と営業の案内は公式に無いので、出かける前に公式SNSを見ておくのが確実だ。",
    ],
    "heiroku": [
        "岩手・紫波町で、国の重要文化財「日詰平井邸」に醸造所を構える蔵（2023年）。「百年の眠りから目覚めた酵母で醸す」をうたい、発芽玄米を使う「Re:vive」と、果汁を重ねる「layer」の2つのシリーズを造る。",
        "古民家のカフェ「喫茶喫酒」で<strong>グラス単位の有料試飲</strong>ができ、<strong>醸造所限定の酒</strong>も含めてボトルを買える。醸造家が案内する有料の見学（約60分・試飲付き）は要予約。<strong>見学ツアー以外では、醸造所の付近には入れない</strong>（公式）。見学の前日からは、納豆・漬物・ヨーグルトなどの発酵食品を控えるよう案内がある。",
    ],
    "mingura": [
        "岩手・大船渡で、「誰もが杜氏になれる」醸造所を目指す蔵（2025年）。陶芸体験のように<strong>自分のお酒をつくる「素人醸造体験」</strong>を提供するとしている（日程や申し込み方法の案内はまだない）。",
        "公式note（2026年9月25日）は、ここをお酒を飲めて、どぶろくも買える場所と紹介している。営業日・時間の案内は見当たらないので、訪ねる前に公式LINEか問い合わせフォームで聞いておくのが確実だ。",
    ],
    "fermenteria": [
        "JR仙台駅の1階、「tekute dining」の中の約3.4坪で醸すマイクロ醸造所（2024年）。<strong>透明なタンクで発酵する様子が、店頭からガラス越しに見える</strong>。",
        "店頭では無料試飲ができ、造りたての生のクラフトサケ「サケベイビー」を<strong>店頭限定でカップで出している</strong>（持ち帰りもできる）。日持ちする火入れのボトルや、ノンアルコールの麹ドリンクも売っているので、<strong>お酒を飲まない人へのおみやげも選べる</strong>。8Lから頼めるオリジナルの酒造りプランもある（事前相談）。店頭限定の新作は入れ替わりが早い。",
    ],
    "ine-to-agave": [
        "秋田・男鹿で、旧駅舎を改装して2021年に開いた醸造所。自然栽培米をすべて精米歩合90%で使い、米と麹をフルーツやハーブと一緒に発酵させる。看板の「稲とアガベ」は、その名のとおりアガベシロップを副原料にしている。",
        "公式の案内で飲めると確かめられたのは、醸造所とは別の<strong>直営のラーメン店「RAMEN おがや」</strong>（男鹿市内）。ここでは<strong>ラーメン専用の「稲とアガベ」とのペアリング</strong>を出している。醸造所に併設した「土と風」は、公式サイト内でカフェ営業・完全予約制のレストランと書き方が分かれているので、行く前に確認を。定期的な見学の案内はないが、創業祭（2025年11月の4周年「OṃOn」）などのイベントを開いていて、告知は公式のnote・SNSに出る。",
    ],
    "tsuchiura": [
        "1948年創業の土浦の地酒店「佐藤酒店」が、新しく立ち上げた蔵（2026年）。茨城各地の素材を使う「ツチブル」シリーズで、規格外の果実も積極的に使い、茨城県産の酵母と掛け合わせる。メロンやいちご、ホップのどぶろくなどがある。",
        "飲食の案内はないが、醸造所（日下部ビル1階）で直売していて、<strong>醸造工程の見学から試飲までの60〜90分のプログラム</strong>（要予約）がある。営業時間は予告なく変わる場合がある（公式）。",
    ],
    "yamane": [
        "埼玉・飯能の赤沢で、西川材の杉の木桶を使って醸す蔵。埼玉県産米に、飯能産の茶葉や蜂蜜、発芽玄米を合わせる。",
        "「やまね酒造り学校」として、<strong>蔵見学や仕込み体験</strong>を案内している（メールで予約）。直売店は不定期営業で、営業日は公式サイトとXで告知される。体験には20歳未満は参加できず、中学生以下と妊娠中の人は入場できない。酒造りの状況によって予約を受けられないこともあり、案内ページは2022年に載せたものなので、最新の受付状況は公式で確認を。",
    ],
    "lagoon": [
        "新潟・福島潟のほとりにある蔵（2021年）。ブランドは「翔空（しょうくう）」。新潟の洋梨ル・レクチェや苺の越後姫、ホップ、さらにはトマトとバジルまで、副原料の幅がとても広い。",
        "併設の「LAGOON BREWERY Shop & Cafe」で<strong>自社醸造のSAKEをテイスティングでき</strong>、ボトルやグッズを買える（しっかりした食事の提供はない）。<strong>窓から発酵室を眺めるのは予約不要</strong>。蔵の中に入る見学（テイスティング付き・約1時間）は、約1週間前までにメールで相談する予約制だ。内部見学の当日は、来る前に発酵食品や柑橘類をとらないよう案内がある（歯みがき・シャワー・着替えの後ならよい）。酒造りの都合で営業が急に変わることもある。",
    ],
    "iyasaka": [
        "新潟・柏崎で、2026年1月に「その他の醸造酒」の免許を取ったばかりの蔵。副原料は使わず、米麹だけで醸す「十割麹酒」を造る。",
        "田植えや稲刈り（収穫祭）といったイベントを開いていて、2026年9月12日の収穫祭では、希望者向けの蔵見学も予定に組まれていた（申し込み制・代表のnote）。醸造所内の直売所とテイスティングスペースは、2026年8月時点で完成間近と報告されている（CAMPFIREの活動報告）。開店後はまずボトルの販売から始め、テイスティングは準備が整い次第とのこと。開業したかは公式で確認できていないので、訪ねる前に問い合わせを。",
    ],
    "librom": [
        "福岡市の高砂で、2020年から醸す蔵。社名は「LIBERTA（自由）」と「ROMANZO（ロマン）」を合わせた造語。米を主原料に、あまおうやトマト、ハーブ、スパイスなど、福岡・九州の素材を副原料にする。",
        "醸造所に併設したパブでは、<strong>搾りたての酒と、麹や酒粕を使った料理</strong>を出していて、<strong>酒造りの様子を目の前に見ながら</strong>飲める。予約は電話かInstagramのDMで受け付けている（公式）。",
    ],
    "dejima-hosendo": [
        "長崎・出島町で、「九州初の都市型どぶろく醸造所」をうたう蔵（2023年）。醸造所と、さけのバー、うつわのギャラリーをひとつにした場所だ。雲仙市産の黒米を使う「芳扇 紫雲」のように、長崎の米の酒もある。",
        "醸造所に隣接したカウンター6席の「でじま芳扇堂 BAR」で、<strong>出島で醸したどぶろくを、長崎の季節の肴と</strong>楽しめる。席が少ないので予約がすすめられている。時間帯によっては紹介制の貸切営業があり、<strong>未成年連れ・食事だけの利用はできない</strong>。酒造期は短縮営業や臨時休業がある。となりで醸造しているため、強い香水は控えるよう求めている。",
    ],
    "amanosato": [
        "福岡・福智町で2025年に生まれた蔵。福岡県産の山田錦、合鴨農法のヒノヒカリ、町でとれた無農薬の果物やハーブで、「在る」シリーズなどを醸す。",
        "ふだんの来訪・試飲の案内は公式に無いが、2025年に初めての蔵開きを開き、<strong>第2回を2026年11月1日に開く</strong>（入場無料）。催しは公式の催しページで告知されるので、<strong>門が開く日を狙って訪ねたい</strong>。",
    ],
}

NOMERU_INTRO = {
    "tokyo": "東京の4蔵は、浅草、日本橋兜町、東京駅の改札内、新橋の地下と、どれも都心の街なかにある。観光の途中や仕事帰りに、できたてのどぶろくを飲みに立ち寄れるのが、都市の醸造所のいいところだ。",
    "kansai": "関西の4蔵は、楽しみ方がそれぞれ違う。大阪で一杯なら、高島屋の地下か、高槻の団地の1階へ。神戸の白鶴酒造資料館は、造りを眺めて、ここでしか売らない酒を買いに行く場所。滋賀・長浜では、試飲と予約制の見学ができる。",
    "tohoku": "東北には、旅の目的地になる蔵が多い。福島・小高の2蔵、重要文化財の古民家にある紫波の蔵、旧駅舎を改装した男鹿の蔵、そして仙台駅の中の蔵。<strong>金・土・日の夜だけ・予約制の店や、営業の案内が公式に無い蔵もある</strong>ので、出かける前の確認が欠かせない。",
    "kanto": "茨城・埼玉・新潟の4蔵は、飲むより「見る・学ぶ・買う」が中心だ。予約して蔵の中まで入れる見学や、仕込みの体験、窓越しに発酵を眺められる蔵がある。",
    "kyushu": "九州で飲めるのは、福岡・高砂のパブと、長崎・出島の6席のバー。どちらも醸造の現場のすぐそばで飲める。福智町の天郷醸造所は、蔵開きの日に門を開く。",
}


def build_nomeru_kura():
    import visit_info as VI
    from breweries_master import by_slug as _bs, BREWERIES as _ALL
    y, m, d = (int(x) for x in VI.CHECKED.split("-"))
    checked_ja = f"{y}年{m}月{d}日"
    in_regions = [s for _k, _j, _e, slugs in VI.REGIONS_VISIT for s in slugs]
    assert set(in_regions) <= set(NOMERU_STORY) and set(in_regions) <= set(NOMERU_PLACE), "紹介文・場所の無い蔵がある"
    n_kura = len(in_regions)
    n_drink = sum(1 for s in in_regions if VI.VISIT[s].get("drink"))
    n_buy = sum(1 for s in in_regions if VI.VISIT[s].get("buy"))
    n_tour = sum(1 for s in in_regions if VI.VISIT[s].get("tour") and VI.VISIT[s].get("tour_kind") not in ("glass", "plan"))
    n_glass = sum(1 for s in in_regions if VI.VISIT[s].get("tour_kind") == "glass")
    n_event = sum(1 for s in in_regions if VI.VISIT[s].get("tour") and VI.VISIT[s].get("tour_kind") == "event")

    def k(slug):
        return f'<a href="../brewery/{slug}.html">{_bs(slug)["name"]}</a>'

    def official(slug):
        v = VI.VISIT[slug]
        return v.get("official", _bs(slug).get("official_url"))

    def mark(v, key):
        if not v.get(key):
            return "—"
        if key == "tour":
            return {"event": "イベント時", "glass": "ガラス越し", "plan": "予定"}.get(v.get("tour_kind"), "あり")
        return "あり"

    # 早見表
    rows = ""
    for s in in_regions:
        v, b = VI.VISIT[s], _bs(s)
        rows += (f'            <tr><td class="nm"><a href="../brewery/{s}.html">{b["name"]}</a></td>'
                 f'<td class="pf">{NOMERU_PLACE[s]}</td><td>{mark(v, "drink")}</td><td>{mark(v, "buy")}</td><td>{mark(v, "tour")}</td></tr>\n')

    def card(s):
        v, b = VI.VISIT[s], _bs(s)
        story = "".join(f"<p>{p}</p>" for p in NOMERU_STORY[s])
        dl = "".join(f"<dt>{lab}</dt><dd>{v[key]}</dd>" for lab, key in
                     (("所在地", "address"), ("アクセス", "access")) if v.get(key))
        if not v.get("address"):
            dl = f"<dt>所在地</dt><dd>{b['prefecture']}{b['city']}（番地は公式に記載なし）</dd>" + dl
        off = official(s)
        links = f'<a href="../brewery/{s}.html">{b["name"]}の蔵と銘柄を見る&nbsp;→</a>'
        if off:
            links += f'<a href="{off}" target="_blank" rel="noopener">公式サイトで最新の営業を見る&nbsp;→</a>'
        return f"""      <div class="vcard">
        <div class="vcard__head"><h3 class="vcard__h"><a class="vcard__name" href="../brewery/{s}.html">{b["name"]}</a></h3><span class="vcard__pref">{b["prefecture"]}・{NOMERU_PLACE[s]}</span></div>
        <div class="vcard__story">{story}</div>
        <dl>{dl}</dl>
        <div class="vcard__links">{links}</div>
      </div>
"""

    region_html = ""
    for i, (rk, ja, en, slugs) in enumerate(VI.REGIONS_VISIT):
        cards = "".join(card(s) for s in slugs)
        region_html += f"""{divider()}
    <section class="section" id="v-{rk}">
{section_meta(f"{i + 4:02d}", f"{en} / {ja}で飲む・訪ねる")}
      <div class="prose">
        <h2 class="sub-h">{ja}で、<span class="accent">クラフトサケの蔵</span>を訪ねる。</h2>
        <p>{NOMERU_INTRO[rk]}</p>
      </div>
{cards}    </section>
"""
    no_info = "、".join(k(s) for s in VI.NO_INFO)
    n_reg = len(VI.REGIONS_VISIT)
    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "WHY GO / 醸造所で飲むということ")}
      <div class="prose">
        <h2 class="sub-h">「醸造所で飲む」と、<span class="accent">何が違う</span>のか。</h2>
        <p class="lead">クラフトサケやどぶろくは、<span class="accent">造っている蔵で飲める</span>。東京なら浅草・日本橋兜町・東京駅の改札内・新橋の4か所に、醸造所と一体のバーやパブがある。saketto に載せている{len(_ALL)}蔵を公式情報などで調べると、<strong>蔵の店や直営店で飲めるのは{n_drink}蔵</strong>。直売は{n_buy}蔵、見学や体験の案内は{n_tour}蔵（うち{n_event}蔵はイベントのときだけ）、ガラス越しなどに造りを見られる蔵が{n_glass}あった（{checked_ja}時点）。</p>
        <p>では、わざわざ造る場所まで行くと、何がいいのか。理由は3つある。</p>
        <p>ひとつめは、<strong>生まれたての酒が飲める</strong>こと。クラフトサケには、火入れ（加熱処理）をしない生酒や、生のにごりが多い。火入れしない酒は酵素が（にごりなら酵母も）働いていて味が動くため、冷蔵が欠かせず、遠くへ運ぶほど手間がかかる。造った場所で飲めば、その心配がない。{k("tokyo-station")}は完成から1週間ほどの生どぶろくを少量出し、{k("fermenteria")}は造りたての生の酒を店頭限定でカップに注ぐ。{k("librom")}のパブで出すのは搾りたての酒だ。</p>
        <p>ふたつめは、<strong>そこでしか買えない酒</strong>があること。{k("hakutsuru-sakecraft")}は毎回本数限定で同じ酒質を二度と造らず、公式の発表では、できた酒は資料館でだけ販売される。{k("heiroku")}には醸造所限定の酒があり、{k("happy-taro")}の店には店でしか買えないどぶろくが並ぶ。</p>
        <p>みっつめは、<strong>造っている現場が見える</strong>こと。ガラス越しや窓越しに造りの様子を見られる蔵や、予約すれば蔵の中まで案内してもらえる蔵がある。グラスの中の酒が、どんな場所で、どんな人の手で生まれたのかがわかると、同じ一杯でも味わいが変わってくる。</p>
        <p>そもそも、なぜ駅の中や百貨店の地下、団地にまで醸造所があるのか。日本酒（清酒）の製造免許は、新規にはほとんど交付されない。だがクラフトサケの蔵の多くが取る「その他の醸造酒」の免許なら、小さな設備で新しく始める道がある。仙台駅の Fermenteria は、わずか約3.4坪だ。背景は<a href="new-breweries.html">いま生まれている、新しい蔵</a>と<a href="craftsake-towa.html">クラフトサケとは</a>にくわしく書いた。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("02", "AT A GLANCE / 早見表")}
      <div class="prose">
        <h2 class="sub-h">まず、<span class="accent">{n_kura}蔵</span>を一覧で。</h2>
        <p>訪ねる手がかりが公式などで見つかった{n_kura}蔵を、地域の順に並べた。蔵の名前から、蔵と銘柄のページへ進める。</p>
      </div>
      <div class="cmp-wrap">
        <table class="cmp cmp--visit">
          <thead><tr><th>蔵</th><th class="pf">場所</th><th>飲める</th><th>買える</th><th>見学・体験</th></tr></thead>
          <tbody>
{rows}          </tbody>
        </table>
      </div>
      <p class="pick-imgnote">「あり」は公式の案内などで確かめられたもの。「ガラス越し」は、見学の案内は無いものの、予約なしでガラス越しなどに造りの様子が見えるもの。「予定」は提供するとしているが日程の案内がまだ無いもの。「—」は案内が見つからなかったもので、できないという意味ではありません。営業日・時間・料金は変わりやすいため、この記事には載せていません。</p>
    </section>
{divider()}
    <section class="section">
{section_meta("03", "BY PURPOSE / 目的で選ぶ")}
      <div class="prose">
        <h2 class="sub-h">目的から、<span class="accent">行き先</span>を選ぶ。</h2>
        <p>同じ「飲める醸造所」でも、ふらっと一杯寄る店、料理とじっくり合わせる店、造りを学びに行く蔵と、性格はかなり違う。何をしたいかで選ぶと、行き先が絞りやすい。過ごし方の目安でいえば、駅や百貨店の中の蔵は一杯だけ立ち寄る使い方、料理を出す店は腰を据えて、見学は予約した時間（どの蔵もおよそ60〜90分）、地方の蔵は半日がかりの旅になる。</p>
        <h3 class="sub-h tight">乗り換えや仕事帰りに、<span class="accent">さっと一杯</span></h3>
        <p>旅の行き帰りに寄れるのは、東京駅の改札内にある{k("tokyo-station")}（はせがわ酒店 グランスタ東京店）と、仙台駅1階の{k("fermenteria")}。新橋の{k("ubu")}は、後半のバーの時間帯なら予約なしで入れる。大阪なら高島屋の地下にある{k("heiwa-namba")}、東京・日本橋なら{k("heiwa-kabutocho")}が、街なかのブルワリーパブだ。</p>
        <h3 class="sub-h tight">料理と合わせて、<span class="accent">ゆっくり</span></h3>
        <p>料理とじっくり合わせるなら、鮨と肴のおまかせを出す新橋の ubu（食事の時間帯は前日23時までの予約制）が代表格だ。浅草の木花之醸造所の店では和の肴と、福岡の{k("librom")}では麹や酒粕を使った料理と、長崎の{k("dejima-hosendo")}では長崎の季節の肴と合わせられる。福島・小高の{k("haccoba")}のブリューパブも、酒蔵を眺めながら料理と楽しむ店だ。変わったところでは、{k("ine-to-agave")}が直営のラーメン店で、<strong>ラーメン専用の酒とのペアリング</strong>を出している。</p>
        <h3 class="sub-h tight">造りを<span class="accent">見て、学ぶ</span></h3>
        <p>予約すれば蔵の中まで案内してもらえるのは、{k("heiroku")}（約60分・試飲付き）、{k("tsuchiura")}（見学から試飲まで60〜90分）、{k("happy-taro")}（約90分）、{k("lagoon")}（約1時間・テイスティング付き）。仕込みまで体験したいなら、{k("yamane")}の「やまね酒造り学校」がある。予約なしで気軽に眺めるなら、ガラス越しや窓越しに造りの様子が見られる木花之醸造所、東京駅酒造場、Fermenteria、白鶴酒造資料館（{k("hakutsuru-sakecraft")}）、LAGOON BREWERY へ。</p>
        <h3 class="sub-h tight">旅の<span class="accent">目的地</span>にする</h3>
        <p>蔵そのものが目的地になる場所もある。国の重要文化財の古民家にある平六醸造、旧駅舎を改装した男鹿の稲とアガベ、福島潟のほとりの LAGOON BREWERY、出島のでじま芳扇堂。福島・小高では、haccoba と、そこから独立した醸造家の{k("pukupuku")}の2蔵を一緒にめぐれる。</p>
        <h3 class="sub-h tight">そこでしか買えない一本を、<span class="accent">おみやげに</span></h3>
        <p>神戸の白鶴酒造資料館では、本数限定の HAKUTSURU SAKE CRAFT を資料館でだけ売っている。紫波の平六醸造には醸造所限定の酒があり、長浜のハッピー太郎醸造所の店には、店でしか買えないどぶろくが並ぶ。仙台駅の Fermenteria なら、店頭限定の造りたての「サケベイビー」をカップで持ち帰れる。</p>
      </div>
    </section>
{region_html}{divider()}
    <section class="section" id="v-notyet">
{section_meta(f"{n_reg + 4:02d}", "NOT YET / 訪ねる拠点がまだ無い蔵")}
      <div class="prose">
        <h2 class="sub-h">いまは、<span class="accent">瓶で出会う</span>蔵。</h2>
        <p>自前の醸造所を持たずに醸す蔵もある。京都の{k("linne")}はほかの蔵の設備を借りて醸すファントムブリュワリーで、公式ニュース（2026年9月25日）で、2027年春に京都の清水・五条坂エリアへ自社醸造所とレストランを開く予定と発表している。いまは京都の飲食店などで、要予約のペアリングイベントを開いている。千葉の{k("salmon-brewery")}も近くの酒蔵の協力で醸していて、訪ねられる施設は今のところ無い。</p>
        <p>また、{no_info}は、来訪の案内が公式に見つからなかった。こうした蔵の酒は、公式オンラインショップや取扱店で手に入る。買い方の入口は<a href="doko-de-kaeru.html">クラフトサケはどこで買える？</a>にまとめている。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta(f"{n_reg + 5:02d}", "FIRST VISIT / 初めて訪ねる前に")}
      <div class="prose">
        <h2 class="sub-h">小さな蔵ほど、<span class="accent">事前の確認</span>を。</h2>
        <p>初めて醸造所を訪ねるときに、知っておくと困らないことをまとめておく。</p>
        <h3 class="sub-h tight">その日の営業を、<span class="accent">公式で</span>確かめる</h3>
        <p>小さな醸造所の店は、営業が変わりやすい。酒造りの都合で営業が急に変わることや、酒造期の短縮営業・臨時休業を、公式で断っている蔵も多い（LAGOON BREWERY、でじま芳扇堂、土浦醸造など）。<strong>出かける前に、公式サイトかSNSでその日の営業を見ておくのがいちばん確実</strong>だ。</p>
        <h3 class="sub-h tight">席が少ない店は、<span class="accent">予約</span>を</h3>
        <p>新橋の ubu は7席、でじま芳扇堂の BAR は6席、haccoba のブリューパブは8席。金・土・日の夜だけ・予約制の店（haccoba）や、食事の時間帯が完全予約制の店（ubu）もある。蔵の中に入る見学は、どの蔵も予約制だ。</p>
        <h3 class="sub-h tight">支払いと<span class="accent">入場券</span></h3>
        <p>平和どぶろく兜町醸造所は<strong>現金が使えない</strong>（キャッシュレスのみ）。東京駅酒造場は改札の内側にあるので、<strong>駅を利用しないときは入場券が要る</strong>。</p>
        <h3 class="sub-h tight">見学の前は、<span class="accent">発酵食品</span>を控える</h3>
        <p>酒造りは微生物の仕事なので、外から菌を持ち込まないよう求める蔵がある。平六醸造は見学の前日から納豆・漬物・ヨーグルトなどの発酵食品を、LAGOON BREWERY は内部見学の当日に発酵食品や柑橘類を（歯みがき・シャワー・着替えの後ならよい）、やまね酒造は酒造り学校の前日と当日に納豆・柑橘系・キムチなどを控えるよう案内している。でじま芳扇堂の BAR は、となりで醸造しているため強い香水を控えるよう求めている。</p>
        <h3 class="sub-h tight">生の酒を買ったら、<span class="accent">冷やして</span>持ち帰る</h3>
        <p>蔵で買える酒には、火入れをしない要冷蔵の生酒や、生のにごりが多い。遠出のときは保冷バッグを用意して、寄り道は少なめに。発泡する活性タイプは、瓶を立てて、振らないように運ぶ。帰ったらすぐ冷蔵庫へ。保管と開け方のコツは<a href="nomikata.html">クラフトサケの飲み方・楽しみ方</a>にくわしく書いた。いちばん確かなのは、ボトルの表示と蔵の案内に従うことだ。</p>
        <div class="callout">
          <div class="callout__label">飲む前に</div>
          <p><strong>20歳未満の飲酒は法律で禁じられています。</strong>　試飲を含め、飲んだら運転はしないでください。妊娠中・授乳期の飲酒はお控えください。</p>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta(f"{n_reg + 6:02d}", "FAQ / よくある質問")}
      <div class="prose">
        <h2 class="sub-h tight">どぶろくとクラフトサケは、<span class="accent">何が違う</span>？</h2>
        <p>どぶろくは、もろみを搾らず（こさず）に残した、白く濁った米の酒です。クラフトサケは、日本酒の技術をもとに、果物やホップなどの副原料を加えたり、こさずに仕上げたりして「日本酒」の枠の外で醸す酒のことで、どぶろくもその仲間として語られます。この記事の蔵の多くは、どぶろくも、副原料を使ったクラフトサケも造っています。くわしくは<a href="craftsake-towa.html">クラフトサケとは</a>と<a href="doburoku.html">どぶろくとは</a>へ。</p>
        <h2 class="sub-h tight">東京でクラフトサケを<span class="accent">飲める</span>醸造所は？</h2>
        <p>浅草の{k("konohanano")}（併設の店 ALL (W)RIGHT -sake place-）、日本橋兜町の{k("heiwa-kabutocho")}、東京駅改札内の{k("tokyo-station")}（はせがわ酒店 グランスタ東京店）、新橋の{k("ubu")}があります。くわしくは<a href="#v-tokyo">東京の醸造所</a>へ。</p>
        <h2 class="sub-h tight">大阪でクラフトサケを<span class="accent">飲める</span>醸造所は？</h2>
        <p>大阪高島屋の地下にある{k("heiwa-namba")}と、高槻・富田団地の{k("adachi-noujo")}があります（足立農醸の店は報道による情報です）。近くでは、神戸の白鶴酒造資料館で HAKUTSURU SAKE CRAFT を見て買えます。くわしくは<a href="#v-kansai">関西の醸造所</a>へ。</p>
        <h2 class="sub-h tight">初めてでも楽しめる？<span class="accent">何を頼めば</span>いい？</h2>
        <p>迷ったら、まず米だけで醸したプレーンを一杯。そのあとで、果物やホップなど副原料を使った酒に進むと、違いがわかりやすくなります。造り手がその場で出してくれる店なら、味の好みを伝えて選んでもらうのも手です。飲み方の基本は<a href="nomikata.html">クラフトサケの飲み方・楽しみ方</a>に。</p>
        <h2 class="sub-h tight">予約なしで<span class="accent">入れ</span>ますか？</h2>
        <p>蔵によって違います。ubu はバーの時間帯なら予約なしで入れますが、食事の時間帯は前日23時までの予約制です。haccoba のブリューパブは予約制で、でじま芳扇堂の BAR も予約がすすめられています。蔵の中に入る見学は、どこも予約制です。LAGOON BREWERY の窓から発酵室を眺めるのは、予約なしでできます。</p>
        <h2 class="sub-h tight">日本酒も<span class="accent">飲め</span>ますか？</h2>
        <p>クラフトサケは法律上「清酒（日本酒）」ではありませんが、日本酒も一緒に飲める店があります。木花之醸造所の ALL (W)RIGHT には100種以上の日本酒があり、平和どぶろくの兜町・難波では、母体の平和酒造の「紀土」なども飲めます。</p>
        <h2 class="sub-h tight">一人でも<span class="accent">行けます</span>か？</h2>
        <p>ubu（7席）やでじま芳扇堂の BAR（6席）はカウンターの店で、東京駅酒造場や Fermenteria は駅の中で一杯だけ飲める蔵です。一人でも立ち寄りやすい形の店といえます。見学では、ハッピー太郎醸造所が2名からの受付ですが、1人でも2名分の料金で受け付けています。</p>
        <h2 class="sub-h tight">子ども連れでも<span class="accent">行けます</span>か？</h2>
        <p>蔵によります。でじま芳扇堂の BAR は未成年連れの利用ができず、やまね酒造の酒造り学校は中学生以下と妊娠中の人は入場できません。ほかの蔵も、家族で行くときは事前に問い合わせておくと安心です。</p>
        <h2 class="sub-h tight">車で行っても<span class="accent">いい</span>ですか？</h2>
        <p>試飲を含め、飲んだら運転はできません。運転する人は飲まない前提で計画してください。ハッピー太郎醸造所は専用駐車場がなく、白鶴酒造資料館は工事のため駐車場の一部が使えません（公式）。東京駅酒造場、Fermenteria（仙台駅）、ubu（新橋駅から徒歩1分）、土浦醸造（土浦駅西口から徒歩2分）、でじま芳扇堂（出島電停から徒歩1分）のように、駅や電停のすぐそばの蔵も多くあります。</p>
        <h2 class="sub-h tight">お酒を飲まない人と一緒でも<span class="accent">楽しめ</span>ますか？</h2>
        <p>見学や、ガラス越しに発酵を眺めるのは、飲まなくても楽しめます。Fermenteria はノンアルコールの麹ドリンクを売っています。木花之醸造所の店 ALL (W)RIGHT や ubu、LIBROM、でじま芳扇堂のように肴や料理を出す店もありますが、でじま芳扇堂の BAR は食事だけの利用はできません。</p>
        <h2 class="sub-h tight">醸造の様子を<span class="accent">見学</span>できる蔵は？</h2>
        <p>予約して蔵の中まで入れる蔵と、予約なしでガラス越しに見られる蔵があります。一覧は<a href="#s03">目的で選ぶ</a>の「造りを見て、学ぶ」へ。</p>
        <h2 class="sub-h tight">営業時間は<span class="accent">載っていない</span>のですか？</h2>
        <p>小さな醸造所の営業日・時間は変わりやすく、古い情報を載せると現地で困らせてしまうため、あえて載せていません。各蔵の「公式サイトで最新の営業を見る」から、蔵の案内をご覧ください。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta(f"{n_reg + 7:02d}", "READ ON / もっと知る")}
      <div class="prose">
        <p>訪ねる前に、飲み方の基本や、蔵が生まれている背景も読んでおくと、現地での一杯がもっと楽しめる。</p>
        <div class="readmore">
          <a href="new-breweries.html">
            <div class="readmore__k">DEEP</div>
            <div class="readmore__t">いま生まれている、新しい蔵</div>
          </a>
          <a href="nomikata.html">
            <div class="readmore__k">あわせて読む</div>
            <div class="readmore__t">クラフトサケの飲み方・楽しみ方</div>
          </a>
        </div>
      </div>
    </section>

  </div>
"""
    html = page_head(f"クラフトサケ・どぶろくが飲める醸造所 — 東京・大阪ほか{n_drink}蔵と、見学できる蔵",
                     f"東京なら浅草・日本橋兜町・東京駅改札内・新橋の4か所。醸造所に併設したバーやパブでクラフトサケ・どぶろくを飲める蔵を、全国{n_drink}蔵、公式情報などで確かめて紹介。目的別の選び方、予約・支払い・見学前の注意点も。",
                     "/guide/nomeru-kura.html", "article")
    html += masthead(article_masthead_label("nomeru-kura"), "A Field Guide")
    html += article_crumbs("nomeru-kura")
    html += hero(
        article_eyebrow("nomeru-kura"),
        '造る場所で、<br><span class="accent">その一杯を</span>。',
        "搾りたての生の酒、そこでしか買えない一本、ガラスの向こうの発酵。クラフトサケの醸造所を訪ねる楽しみと、目的に合った蔵の選び方、出かける前に知っておきたいことを案内する。")
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
    (OUT_DIR / "furusato.html").write_text(build_furusato_guide(), encoding="utf-8")
    (OUT_DIR / "zenkoji.html").write_text(build_zenkoji(), encoding="utf-8")
    (OUT_DIR / "new-breweries.html").write_text(build_new_breweries(), encoding="utf-8")
    (OUT_DIR / "nomeru-kura.html").write_text(build_nomeru_kura(), encoding="utf-8")
    print(f"OK ガイド生成: guide/index.html（一覧）＋ 記事{len(ARTICLES)}本")


if __name__ == "__main__":
    main()

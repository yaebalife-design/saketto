# -*- coding: utf-8 -*-
"""収録データから記事中の統計値を計算する。

読みもの記事に「143銘柄」「副原料は76通り」のような数字を直接書いていたため、
銘柄を追加するたびに本文が実データとズレた（そして気づけなかった）。
数字は必ずここで計算し、記事側は STATS[...] を埋め込むだけにする。

    python tools/site_stats.py   # 現在値を一覧表示（検算用）
"""
import collections
import re
import sys

from breweries_brands import BRANDS
from breweries_master import BREWERIES
from gen_axes_pages import categorize_ingredient

# 副原料の主分類の優先順（1銘柄が複数の副原料を持つとき、どれに寄せるか）
_PRIORITY = ["hop", "fruit", "tea-herb", "rice-koji", "special"]


def _num(v):
    return v if isinstance(v, (int, float)) else None


def compute():
    brands = [(s, b) for s, bs in BRANDS.items() for b in bs]
    total = len(brands)

    # ── 副原料の表記バリエーション（「米のみ」系は素材ではないので除く） ──
    variants = {i.strip() for _, b in brands
                for i in (b.get("sub_ingredients") or []) if i and "米のみ" not in i}

    # ── 主分類（排他。1銘柄1カテゴリ） ──
    cat_n = collections.Counter()
    cat_breweries = collections.defaultdict(set)
    rice_only = 0
    rice_breweries = set()
    undisclosed = 0
    for s, b in brands:
        ings = [i for i in (b.get("sub_ingredients") or []) if i]
        if not ings:
            undisclosed += 1
            continue
        if all("米のみ" in i for i in ings):
            rice_only += 1
            rice_breweries.add(s)
            continue
        cats = [c for c in (categorize_ingredient(i) for i in ings) if c]
        if not cats:
            undisclosed += 1
            continue
        pick = next(c for c in _PRIORITY if c in cats)
        cat_n[pick] += 1
        cat_breweries[pick].add(s)

    prices = sorted(p for _, b in brands if (p := _num(b.get("price"))))
    abvs = sorted(a for _, b in brands if (a := _num(b.get("abv"))) is not None)
    abv_alc = [a for a in abvs if a > 0]
    vols = collections.Counter(v for _, b in brands if (v := _num(b.get("volume_ml"))))

    hop_brands = [(s, b) for s, b in brands
                  if any("ホップ" in (i or "") for i in (b.get("sub_ingredients") or []))]

    # ── 蔵の統計（記事に「25蔵」「東北6…」と直書きされていて古くなっていた） ──
    region_n = collections.Counter(b["region"] for b in BREWERIES)
    years = collections.Counter()
    for b in BREWERIES:
        m = re.match(r"(\d{4})", str(b.get("founded", "")))
        if m:
            years[int(m.group(1))] += 1
    pending = [b for b in BREWERIES if "予定" in str(b.get("founded", ""))]
    region_text = "、".join(f"{r}{n}" for r, n in region_n.most_common())

    pref_n = collections.Counter(b["prefecture"] for b in BREWERIES)
    multi = [(p, n) for p, n in pref_n.most_common() if n >= 2]
    # 「新潟・福岡・東京が各3蔵、福島・岩手・大阪が各2蔵」のような並びを作る
    by_count = collections.defaultdict(list)
    for p, n in multi:
        by_count[n].append(p)
    multi_text = "、".join(
        f"{'・'.join(ps)}が各{n}蔵" for n, ps in sorted(by_count.items(), reverse=True))

    return {
        "brands": total,
        "breweries": len(BREWERIES),
        "assoc_breweries": sum(1 for b in BREWERIES if b.get("association")),
        "pending_breweries": len(pending),
        "since2024": sum(n for y, n in years.items() if y >= 2024),
        "region_breakdown": region_text,
        "multi_prefectures": len(multi),
        "multi_pref_breakdown": multi_text,
        "prefectures": len(pref_n),
        "pref_counts": dict(pref_n),
        "ingredient_variants": len(variants),
        "rice_only": rice_only,
        "rice_only_breweries": len(rice_breweries),
        "undisclosed": undisclosed,
        "hop": cat_n["hop"],
        "hop_breweries": len(cat_breweries["hop"]),
        "fruit": cat_n["fruit"],
        "tea_herb": cat_n["tea-herb"],
        "rice_koji": cat_n["rice-koji"],
        "special": cat_n["special"],
        "hop_any": len(hop_brands),
        "hop_any_breweries": len({s for s, _ in hop_brands}),
        "price_known": len(prices),
        "price_median": prices[len(prices) // 2] if prices else 0,
        "price_under2000": sum(1 for p in prices if p < 2000),
        "price_2000s": sum(1 for p in prices if 2000 <= p < 3000),
        "price_3000_4999": sum(1 for p in prices if 3000 <= p < 5000),
        "price_5000up": sum(1 for p in prices if p >= 5000),
        "abv_known": len(abvs),
        "abv_min": min(abv_alc) if abv_alc else 0,
        "abv_max": max(abv_alc) if abv_alc else 0,
        "abv_median": sorted(abv_alc)[len(abv_alc) // 2] if abv_alc else 0,
        "vol_720": vols.get(720, 0),
        "vol_500": vols.get(500, 0),
    }


def buy_stats():
    """購入導線の集計。生成済みの銘柄ページを数えるのが唯一の正解
    （affiliate_overrides と RAKUTEN_ENABLED / AMAZON_ENABLED の両方で決まるため）。
    ページ未生成なら None を返す。"""
    import glob
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = glob.glob(os.path.join(root, "brand", "*.html"))
    if not files:
        return None
    slug_of = {}
    for s, bs in BRANDS.items():
        for i, _ in enumerate(bs):
            slug_of[f"{s}-{i}"] = s
    buyable = 0
    with_shop = set()
    for f in files:
        html = open(f, encoding="utf-8").read()
        if ("楽天市場で探す" in html or "Yahoo!ショッピングで探す" in html
                or "Amazonで探す" in html):
            buyable += 1
            with_shop.add(slug_of.get(os.path.basename(f)[:-5], "?"))
    total = len(files)
    # 銘柄をまだ1件も収録していない蔵は「探したが無かった」のではないので、
    # 取扱いなしの蔵として数えない（収録直後の蔵を混ぜると実態より多く見える）
    with_brands = {s for s, bs in BRANDS.items() if bs}
    return {
        "buyable": buyable,
        "not_buyable": total - buyable,
        "breweries_without_shop": len(with_brands - with_shop),
        "breweries_with_brands": len(with_brands),
    }


STATS = compute()

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for k, v in STATS.items():
        print(f"  {k:26} {v}")
    b = buy_stats()
    print("  ── 購入導線（生成済みページから） ──" if b else "  （銘柄ページ未生成）")
    if b:
        for k, v in b.items():
            print(f"  {k:26} {v}")
    s = STATS
    assert s["rice_only"] + s["hop"] + s["fruit"] + s["tea_herb"] + s["rice_koji"] \
        + s["special"] + s["undisclosed"] == s["brands"], "分類の合計が総銘柄数と一致しない"
    print("\n  ✓ 分類の合計 = 総銘柄数")

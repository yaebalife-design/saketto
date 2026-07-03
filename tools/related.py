# -*- coding: utf-8 -*-
"""saketto / 「次に出会う」関連銘柄の選出・HTML生成（銘柄ページ共通）

サイトコンセプト「次に出会う」を銘柄ページの回遊導線として実装する。
選出はデータ（副原料カテゴリ・蔵）に基づく機械選出のみ。嘘ゼロ（主観の推薦文は書かない）。

- 優先1: 同じ副原料カテゴリ × 別の蔵（横断DBならではの出会い）
- 優先2: 同じ蔵の別銘柄
- 端数はもう一方のプールから補充

gen_brand_pages_v2.py / gen_sample_v2.py の両方から import される。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from breweries_master import by_slug
from breweries_brands import BRANDS
from gen_axes_pages import categorize_ingredient, INGREDIENT_CATEGORIES

CAT_JP = {k: jp for k, jp, _en, _d in INGREDIENT_CATEGORIES}


def _cats(brand):
    cats = set()
    for ing in (brand.get("sub_ingredients") or []):
        c = categorize_ingredient(ing)
        if c:
            cats.add(c)
    return cats


def _all_entries():
    """(brewery_slug, idx, brand, cats) を BRANDS の定義順で列挙。"""
    out = []
    for slug, brands in BRANDS.items():
        for i, b in enumerate(brands):
            out.append((slug, i, b, _cats(b)))
    return out


def pick_related(slug, idx, limit=3):
    """関連銘柄を機械選出。[(slug, idx, brand, reason_html), ...] を返す。"""
    my_brands = BRANDS.get(slug, [])
    if idx >= len(my_brands):
        return []
    me = my_brands[idx]
    my_cats = _cats(me)

    same_cat = []   # 同カテゴリ×別蔵
    for bslug, i, b, cats in _all_entries():
        if bslug == slug:
            continue
        shared = my_cats & cats
        if shared:
            # 表示用は共有カテゴリのうち定義順で最初のもの
            jp = next(CAT_JP[k] for k, *_ in INGREDIENT_CATEGORIES if k in shared)
            same_cat.append((bslug, i, b, f"同じ系統 — {jp}"))

    brewery = by_slug(slug)
    same_kura = [(slug, i, b, f"同じ蔵 — {brewery['name']}")
                 for i, b in enumerate(my_brands) if i != idx]

    # 決定的だがページごとに開始位置をずらす（毎回同じ顔ぶれを避ける）
    seed = (sum(ord(c) for c in slug) + idx * 7)
    if same_cat:
        off = seed % len(same_cat)
        same_cat = same_cat[off:] + same_cat[:off]
        # 同一蔵が並ばないよう蔵で間引き
        seen_kura, dedup = set(), []
        for e in same_cat:
            if e[0] not in seen_kura:
                dedup.append(e)
                seen_kura.add(e[0])
        same_cat = dedup
    if same_kura:
        off2 = idx % len(same_kura)
        same_kura = same_kura[off2:] + same_kura[:off2]

    picked = same_cat[:2] + same_kura[:1]
    for pool in (same_cat[2:], same_kura[1:]):
        for e in pool:
            if len(picked) >= limit:
                break
            if not any(p[0] == e[0] and p[1] == e[1] for p in picked):
                picked.append(e)
    return picked[:limit]


def next_section_html(slug, idx, num_str="No. 08"):
    """「NEXT / 次に出会う」セクションのHTML。関連が無ければ空文字。"""
    rel = pick_related(slug, idx)
    if not rel:
        return ""
    cards = ""
    for bslug, i, b, reason in rel:
        brw = by_slug(bslug)
        subs = [s for s in (b.get("sub_ingredients") or []) if s and "米のみ" not in s]
        sub_txt = "・".join(subs[:2]) if subs else "米と米麹のみ"
        cards += f"""
      <a class="next-card" href="../brand/{bslug}-{i}.html">
        <div class="next-card__kicker">{reason}</div>
        <div class="next-card__name">{b['name']}</div>
        <div class="next-card__meta">{brw['name']}（{brw['prefecture']}）　／　{sub_txt}</div>
      </a>"""
    return f"""
  <section class="section">
    <div class="section-meta"><span class="section-meta__num">{num_str}</span><h2 class="section-meta__label">NEXT / 次に出会う</h2><span class="section-meta__rule"></span></div>
    <p class="next-note">副原料の系統と蔵のつながりから、データベースが機械的に選んだ「次の一本」。</p>
    <div class="next-grid">{cards}
    </div>
  </section>"""

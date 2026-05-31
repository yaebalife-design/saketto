# -*- coding: utf-8 -*-
"""saketto / 銘柄詳細ページ V2 量産ジェネレータ（伸縮テンプレ）

brand_data/*.json（一次ソース調査済み）を breweries_brands.py の銘柄リストにマージし、
取れた項目だけ表示する伸縮テンプレで全銘柄を生成する。
フレーバー4軸/6軸は調査済み flavor_basis・テイスティング・成分値から編集部評価として導出。

- gen_sample_v2.py の CSS / SVG関数 / AFFILIATE_ENABLED を再利用
- haccoba は showcase の haccoba-0.html を維持するため対象外（brand_data無し）
- アフィリ購入ボタンは AFFILIATE_ENABLED に従う（現在False=準備中表示）

実行: cd ツール/saketto_repo/tools && python gen_brand_pages_v2.py
"""

import json
import glob
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from breweries_master import by_slug, BREWERIES
from breweries_brands import BRANDS
from moshimo_link import rakuten_search, amazon_search
from gen_sample_v2 import CSS, gen_scale4_svg, gen_radar6_svg, AFFILIATE_ENABLED

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "brand"
DATA_DIR = Path(__file__).resolve().parent / "brand_data"

# ────────────── brand_data 読み込み ──────────────
DETAILS = {}  # slug -> list[detail dict]（JSON挿入順＝breweries_brands順）
for f in sorted(glob.glob(str(DATA_DIR / "*.json"))):
    d = json.load(open(f, encoding="utf-8"))
    DETAILS[d["brewery"]] = list(d["brands"].values())


# ────────────── フレーバー導出（調査済み事実から編集部評価） ──────────────

def _has(text, *kws):
    return any(k in text for k in kws)


def derive_flavor(detail, brand):
    """flavor_basis・テイスティング・成分値から4軸/6軸/タグを導出。
    根拠は調査済みテキスト。値は『公式テイスティング・成分値に基づくsaketto編集部評価』。"""
    parts = [detail.get("flavor_basis"), detail.get("tasting_nose"),
             detail.get("tasting_palate"), detail.get("tasting_finish"),
             detail.get("sub_ingredients_detail"), detail.get("story")]
    text = " ".join(p for p in parts if p)

    abv = detail.get("abv") if isinstance(detail.get("abv"), (int, float)) else brand.get("abv")

    # ── 4軸（0=左, 1=右）──
    # body: 軽快(0) ↔ 濃醇(1)
    if _has(text, "濃醇", "濃厚", "リッチ", "フルボディ", "とろみ", "とろとろ", "ムース", "コク", "膨らみ", "ボリューム", "旨味が強", "旨みを強"):
        body = 0.72
    elif _has(text, "淡麗", "軽快", "さらり", "ライト", "すっきり", "クリア", "クリーン", "スイスイ", "ドリンカブル"):
        body = 0.32
    else:
        body = 0.5
    if isinstance(abv, (int, float)):
        if abv >= 16:
            body = min(1.0, body + 0.1)
        elif abv <= 8:
            body = max(0.0, body - 0.1)

    # sweet: 甘口(0) ↔ 辛口(1)
    nihonshudo = detail.get("flavor_basis", "")
    sweet = 0.5
    if _has(text, "ドライ", "辛口", "キレ", "シャープ"):
        sweet = 0.68
    if _has(text, "甘味", "甘み", "甘さ", "甘酸", "甘旨", "やさしい甘", "優しい甘", "濃厚な甘"):
        sweet = 0.35 if sweet == 0.5 else 0.5
    # 日本酒度の数値があれば優先（-で甘、+で辛）
    import re
    m = re.search(r"日本酒度[-−]?\s*([+\-]?\d+(?:\.\d+)?)", text)
    if m:
        try:
            v = float(m.group(1).replace("−", "-"))
            # -15..+10 を 0.15..0.8 に（負=甘=低）
            sweet = max(0.12, min(0.85, 0.5 - v / 30.0))
        except ValueError:
            pass

    # acid: 酸控(0) ↔ 酸強(1)
    if _has(text, "高酸", "鋭い酸", "鋭角な酸", "サワー", "クエン酸", "しっかりした酸", "強い酸", "強めの酸", "酸でキレ", "爽快感MAX"):
        acid = 0.78
    elif _has(text, "酸味", "酸が", "爽やかな酸", "心地よい酸", "柔らかな酸", "乳酸"):
        acid = 0.6
    elif _has(text, "酸控", "酸は穏やか", "まろやか"):
        acid = 0.35
    else:
        acid = 0.45
    ms = re.search(r"酸度\s*([0-9]+(?:\.\d+)?)", text)
    if ms:
        try:
            a = float(ms.group(1))
            acid = max(0.2, min(0.95, (a - 1.0) / 5.0 + 0.3))
        except ValueError:
            pass

    # clarity: 清澄(0) ↔ にごり(1)
    if _has(text, "どぶろく", "ドブロク", "にごり", "ニゴリ", "濁酒", "おりがらみ", "うす濁", "薄にごり", "白濁", "霞色"):
        clarity = 0.82
    elif _has(text, "清澄", "クリア", "透明", "澄んだ", "クリーン"):
        clarity = 0.25
    else:
        clarity = 0.5

    scale4 = {"body": round(body, 2), "sweet": round(sweet, 2),
              "acid": round(acid, 2), "clarity": round(clarity, 2)}

    # ── 6軸（1..5）──
    def lvl(base, *kw_high, bonus=0):
        return base + (1 if _has(text, *kw_high) else 0) + bonus if kw_high else base

    hanayaka = 3
    if _has(text, "華やか", "フルーティ", "フルーツ", "果実", "吟醸香", "トロピカル", "パイナップル", "メロン", "白桃", "マスカット", "ライチ", "柑橘", "香り高"):
        hanayaka = 5 if _has(text, "華やか", "トロピカル", "吟醸香") else 4
    sanmi = 1 + round(acid * 4)
    amami = 1 + round((1 - sweet) * 4)
    koku = 1 + round(body * 4)
    komekan = 4 if _has(text, "米の旨味", "米の旨み", "米由来", "旨味", "旨み", "米感", "お米") else 3
    fukuzatsu = 3
    if _has(text, "複雑", "層をなす", "奥行き", "余韻", "変化", "熟成"):
        fukuzatsu = 4
    radar6 = {"華やか": max(1, min(5, hanayaka)), "酸味": max(1, min(5, sanmi)),
              "甘味": max(1, min(5, amami)), "コク": max(1, min(5, koku)),
              "米感": max(1, min(5, komekan)), "複雑性": max(1, min(5, fukuzatsu))}

    # ── タグ（香り・味の印象。テキストに実在する語のみ）──
    VOCAB = ["シトラス", "グレープフルーツ", "柑橘", "マスカット", "白ぶどう", "白葡萄", "ライチ", "洋梨", "りんご", "リンゴ",
             "メロン", "白桃", "パイナップル", "いちご", "イチゴ", "八朔", "ゆず", "柚子", "レモン", "オレンジ",
             "蜂蜜", "ハチミツ", "ヨーグルト", "乳酸", "ミント", "ハーブ", "トロピカル", "バニラ", "シェリー",
             "緑茶", "ジャスミン", "ホップ", "クリーミー", "ミルキー", "香ばし", "ドライ", "甘酸っぱ"]
    seen = []
    for w in VOCAB:
        if w in text and w not in seen:
            seen.append(w)
        if len(seen) >= 6:
            break
    tags = seen
    return scale4, radar6, tags


# ────────────── HTML 構築（伸縮） ──────────────

def esc(s):
    return str(s) if s is not None else ""


def build_html(brand, detail, brewery, idx):
    b = brand
    d = detail or {}
    slug = brewery["slug"]
    name = b["name"]
    kana = b.get("kana", "")

    # 値の解決（detail優先、なければbreweries_brands）
    abv = d.get("abv") if d.get("abv") not in (None, "") else b.get("abv")
    volume = d.get("volume_ml") if d.get("volume_ml") not in (None, "") else b.get("volume_ml")
    price = d.get("price") if d.get("price") not in (None, "") else b.get("price")
    price_note = d.get("price_note") or ("参考価格・確認日 2026/05/31" if price else "")
    subs = b.get("sub_ingredients") or []
    sub_detail = d.get("sub_ingredients_detail")
    category = "その他の醸造酒"

    scale4, radar6, tags = derive_flavor(d, b)

    rakuten_url = rakuten_search(name)
    amazon_url = amazon_search(name)

    # ── HERO タグ（香り・味の印象）──
    flavor_tags_html = ""
    if tags:
        chips = "".join(f'<span class="flavor-tag">{t}</span>' for t in tags)
        flavor_tags_html = f"""
    <div class="hero__flavor">
      <div class="hero__flavor-label">— AROMA &amp; FLAVOR ／ 香り・味の印象</div>
      <div class="flavor-tags">{chips}</div>
    </div>"""

    avail_label = {"online": "通販可", "tokuyaku": "特約店", "rare": "極希少"}.get(b.get("availability", "online"), "通販可")

    # ── SPEC BOARD（取れたものだけ）──
    specs = []
    if abv not in (None, ""):
        av = f"{abv}" if not isinstance(abv, str) else abv
        sub = f'<div class="spec-cell__sub">{esc(d.get("abv_note"))}</div>' if d.get("abv_note") else ""
        specs.append(f'<div class="spec-cell"><div class="spec-cell__label">— ABV</div><div class="spec-cell__value">{av}<small>% ALC.</small></div>{sub}</div>')
    if volume not in (None, ""):
        specs.append(f'<div class="spec-cell"><div class="spec-cell__label">— VOLUME</div><div class="spec-cell__value">{volume}<small>ml</small></div></div>')
    if price not in (None, ""):
        pn = f'<div class="spec-cell__sub">{esc(price_note)}</div>' if price_note else ""
        specs.append(f'<div class="spec-cell"><div class="spec-cell__label">— PRICE</div><div class="spec-cell__value">¥{int(price):,}</div>{pn}</div>')
    spec_board = ('<div class="spec-board">' + "".join(specs) + "</div>") if specs else ""

    # ── RECIPE（値があるものだけ行表示）──
    rows = []

    def row(label, val, sub=None):
        if val in (None, "", []):
            return
        sub_html = f"<small>{esc(sub)}</small>" if sub else ""
        rows.append(f'<div class="recipe-row"><div class="recipe-row__label">{label}</div><div class="recipe-row__value">{esc(val)}{sub_html}</div></div>')

    row("品目（酒税法）", category)
    if subs:
        row("副原料", "・".join(subs), sub=sub_detail)
    elif sub_detail:
        row("副原料", sub_detail)
    row("米品種", d.get("rice_variety"))
    rp = d.get("rice_polish")
    if isinstance(rp, (int, float)):
        row("精米歩合", f"{rp}%")
    elif isinstance(rp, str) and rp:
        row("精米歩合", rp)
    row("酒母", d.get("shubo"), sub=d.get("shubo_note"))
    row("麹", d.get("koji"))
    row("酵母", d.get("yeast"))
    row("仕込水", d.get("water"))
    row("発酵容器", d.get("vessel"))
    if d.get("pasteurized") is True:
        row("火入れ／生酒", "火入れ")
    elif d.get("pasteurized") is False:
        row("火入れ／生酒", "生酒")
    if d.get("draft") is True:
        row("加水／原酒", "原酒")
    elif d.get("draft") is False:
        row("加水／原酒", "加水")

    recipe_section = ""
    if rows:
        recipe_section = f"""
  <section class="section" style="padding-top:3rem">
    <div class="section-meta"><span class="section-meta__num">No. 01</span><span class="section-meta__label">RECIPE / 仕込み</span><span class="section-meta__rule"></span></div>
    <div class="recipe">{''.join(rows)}</div>
  </section>"""

    # ── HOW TO ENJOY（取れたものだけ）──
    enjoy_cells = []
    if d.get("serving_temp"):
        enjoy_cells.append(f'<div class="enjoy-cell"><div class="enjoy-cell__label">— TEMPERATURE</div><div class="enjoy-cell__value">{esc(d["serving_temp"])}</div></div>')
    if d.get("glass"):
        enjoy_cells.append(f'<div class="enjoy-cell"><div class="enjoy-cell__label">— GLASS</div><div class="enjoy-cell__value">{esc(d["glass"])}</div></div>')
    if d.get("preservation"):
        enjoy_cells.append(f'<div class="enjoy-cell"><div class="enjoy-cell__label">— PRESERVATION</div><div class="enjoy-cell__value">{esc(d["preservation"])}</div></div>')
    pairing = d.get("pairing")
    if pairing:
        chips = "".join(f'<span class="pairing-chip">{esc(p)}</span>' for p in pairing)
        enjoy_cells.append(f'<div class="enjoy-cell"><div class="enjoy-cell__label">— PAIRING</div><div class="enjoy-cell__value">公式・取扱店より<div class="pairing-list">{chips}</div></div></div>')
    enjoy_section = ""
    if enjoy_cells:
        enjoy_section = f"""
  <section class="section">
    <div class="section-meta"><span class="section-meta__num">No. 02</span><span class="section-meta__label">HOW TO ENJOY / 楽しみ方</span><span class="section-meta__rule"></span></div>
    <div class="enjoy">{''.join(enjoy_cells)}</div>
  </section>"""

    # ── TASTING（取れた段だけ）──
    t_rows = []
    if d.get("tasting_nose"):
        t_rows.append(f'<div class="tasting-row"><div class="tasting-row__label">— NOSE　<strong>香り</strong></div><div class="tasting-row__text">{esc(d["tasting_nose"])}</div></div>')
    if d.get("tasting_palate"):
        t_rows.append(f'<div class="tasting-row"><div class="tasting-row__label">— PALATE　<strong>含み香・味わい</strong></div><div class="tasting-row__text">{esc(d["tasting_palate"])}</div></div>')
    if d.get("tasting_finish"):
        t_rows.append(f'<div class="tasting-row"><div class="tasting-row__label">— FINISH　<strong>余韻</strong></div><div class="tasting-row__text">{esc(d["tasting_finish"])}</div></div>')
    tasting_section = ""
    if t_rows:
        tasting_section = f"""
  <section class="section">
    <div class="section-meta"><span class="section-meta__num">No. 03</span><span class="section-meta__label">TASTING NOTES / 香り・味わい・余韻</span><span class="section-meta__rule"></span></div>
    <div class="tasting-3">{''.join(t_rows)}</div>
  </section>"""

    # ── FLAVOR PROFILE（常時・導出値）──
    scale4_svg = gen_scale4_svg(scale4)
    radar6_svg = gen_radar6_svg(radar6)
    flavor_section = f"""
  <section class="section">
    <div class="section-meta"><span class="section-meta__num">No. 04</span><span class="section-meta__label">FLAVOR PROFILE / 味わいの構造</span><span class="section-meta__rule"></span></div>
    <div class="flavor-wrap">
      <div class="flavor-box"><div class="flavor-box__title">— STRUCTURE　<strong>4軸構造スケール</strong></div>{scale4_svg}<div class="flavor-box__cap">公式テイスティング記述・成分値に基づく saketto 編集部評価。</div></div>
      <div class="flavor-box"><div class="flavor-box__title">— PROFILE　<strong>6軸レーダー</strong></div>{radar6_svg}<div class="flavor-box__cap">同上。飲み手の印象を6軸で。</div></div>
    </div>
  </section>"""

    # ── STORY（あれば）──
    story_section = ""
    if d.get("story"):
        story_section = f"""
  <div class="divider"><div class="rule"></div><div class="ornament outer"></div><div class="ornament"></div><div class="ornament outer"></div><div class="rule"></div></div>
  <section class="section">
    <div class="section-meta"><span class="section-meta__num">No. 05</span><span class="section-meta__label">STORY / この銘柄が生まれた背景</span><span class="section-meta__rule"></span></div>
    <div class="story-block"><p class="story-text">{esc(d["story"])}</p></div>
  </section>"""

    # ── AWARDS（あれば）──
    awards = d.get("awards") or []
    awards_section = ""
    if awards:
        cards = "".join(
            f'<div class="award-card"><div class="award-year">{esc(a.get("year",""))}</div><div><div class="award-title">{esc(a.get("title",""))}</div><div class="award-where">{esc(a.get("where",""))}</div></div></div>'
            for a in awards)
        awards_section = f"""
  <section class="section">
    <div class="section-meta"><span class="section-meta__num">No. 06</span><span class="section-meta__label">ACCOLADES / 受賞</span><span class="section-meta__rule"></span></div>
    <div class="awards-list">{cards}</div>
  </section>"""

    # ── KURA & PURCHASE ──
    if AFFILIATE_ENABLED:
        purchase_inner = f"""<div class="purchase-card__btns">
            <a class="purchase-card__btn purchase-card__btn--rakuten" href="{rakuten_url}" target="_blank" rel="noopener sponsored">楽天市場で探す →</a>
            <a class="purchase-card__btn purchase-card__btn--amazon" href="{amazon_url}" target="_blank" rel="noopener sponsored">Amazonで探す →</a>
          </div>
          <div class="purchase-card__note">PR ／ アフィリエイトリンクを含みます</div>"""
    else:
        purchase_inner = '<div class="purchase-card__pending">お取り扱い情報は準備中です</div>'

    kura_section = f"""
  <section class="section">
    <div class="section-meta"><span class="section-meta__num">No. 07</span><span class="section-meta__label">KURA &amp; PURCHASE / 蔵元と入手</span><span class="section-meta__rule"></span></div>
    <div class="kura-purchase">
      <div class="kura-card">
        <div class="kura-card__name">{brewery['name']}</div>
        <div class="kura-card__meta">{brewery['prefecture']}・{brewery['city']}　／　創業 {brewery['founded']}</div>
        <p class="kura-card__philo">{esc(brewery.get('philosophy',''))}</p>
        <a class="kura-card__link" href="../brewery/{slug}.html">蔵の詳細を見る →</a>
      </div>
      <div class="purchase-card">
        <div><div class="purchase-card__label">— PURCHASE</div><div class="purchase-card__title">「{name}」を探す</div></div>
        <div>{purchase_inner}</div>
      </div>
    </div>
  </section>"""

    # ── 公式サイト（最下部・控えめ）──
    official_url = brewery.get("official_url", "")
    official_foot = ""
    if official_url:
        host = official_url.split("//")[-1].split("/")[0]
        official_foot = f'<div class="official-foot"><a href="{official_url}" target="_blank" rel="noopener">{brewery["name"]} 公式サイト（{host}）→</a></div>'

    # ── HERO 役割チップ ──
    hero = f"""
  <section class="hero">
    <div class="hero__brewery">
      <span class="role-chip role-chip--kura">蔵</span><a href="../brewery/{slug}.html">{brewery['name']}</a><span class="hero__brewery-loc">（{brewery['prefecture']}）が醸造</span>
    </div>
    <div class="hero__brandrow"><span class="role-chip role-chip--brand">銘柄</span></div>
    <h1 class="hero__name">{name}</h1>
    {f'<div class="hero__kana">{kana}</div>' if kana else ''}
    <p class="hero__tagline">{esc(b.get('note',''))}</p>{flavor_tags_html}
  </section>"""

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} ／ {brewery['name']} — saketto.</title>
<meta name="description" content="{esc(b.get('note',''))[:120]}">
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@300;400;500&family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<main>
  <div class="masthead">
    <div class="left"><a href="../index.html"><span class="accent-dot"></span>SAKETTO</a><a href="../brewery/{slug}.html">← {brewery['name']}</a></div>
    <div class="right">BRAND — 2026/05/31</div>
  </div>
{hero}
{spec_board}
{recipe_section}
{enjoy_section}
{tasting_section}
{flavor_section}
{story_section}
{awards_section}
{kura_section}
{official_foot}
  <footer>
    <div class="colophon">
      <div class="colophon__brand"><a href="../index.html">saketto<span class="dot">.</span></a><small>— クラフトサケの図鑑</small></div>
      <div class="colophon__notes"><strong>準備中</strong><span class="colophon__sep">／</span>価格・度数は公式サイトでご確認ください<span class="colophon__sep">／</span>20歳未満の飲酒は法律で禁じられています<span class="colophon__sep">／</span>PR ／ アフィリエイトリンクを含みます<span class="colophon__sep">／</span>© 2026 saketto.</div>
    </div>
  </footer>
</main>
</body>
</html>
"""
    return html


def main():
    OUT_DIR.mkdir(exist_ok=True)
    count = 0
    skipped_haccoba = 0
    for brewery in BREWERIES:
        slug = brewery["slug"]
        brands = BRANDS.get(slug, [])
        if not brands:
            continue
        if slug == "haccoba":
            skipped_haccoba = len(brands)
            continue  # showcase の haccoba-0.html を維持
        details = DETAILS.get(slug, [])
        for i, brand in enumerate(brands):
            detail = details[i] if i < len(details) else {}
            html = build_html(brand, detail, brewery, i)
            (OUT_DIR / f"{slug}-{i}.html").write_text(html, encoding="utf-8")
            count += 1
    print(f"OK 生成: {count}件 / haccoba {skipped_haccoba}件は据え置き")


if __name__ == "__main__":
    main()

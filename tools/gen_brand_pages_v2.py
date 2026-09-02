# -*- coding: utf-8 -*-
"""saketto / 銘柄詳細ページ V2 量産ジェネレータ（伸縮テンプレ）

brand_data/*.json（一次ソース調査済み）を breweries_brands.py の銘柄リストにマージし、
取れた項目だけ表示する伸縮テンプレで全銘柄を生成する。
フレーバー4軸/6軸は調査済み flavor_basis・テイスティング・成分値から編集部評価として導出。

- gen_sample_v2.py の CSS / SVG関数 / AFFILIATE_ENABLED を再利用
- haccoba も含めて全銘柄を生成する（gen_sample_v2.py はデザイン見本で、公開ページは作らない）
- アフィリ購入ボタンは AFFILIATE_ENABLED に従う（現在False=準備中表示）

実行: cd ツール/saketto_repo/tools && python gen_brand_pages_v2.py
"""

import json
import glob
import math
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from breweries_master import by_slug, BREWERIES
from breweries_brands import BRANDS
from moshimo_link import (
    resolve_rakuten, resolve_amazon, resolve_yahoo, yahoo_impression_tag,
)
from gen_sample_v2 import (
    CSS as _BASE_CSS, gen_scale4_svg, gen_radar6_svg,
    RAKUTEN_ENABLED, AMAZON_ENABLED, YAHOO_ENABLED,
)
from furusato_block import render as furusato_render, CSS as _FURUSATO_CSS

CSS = _BASE_CSS + _FURUSATO_CSS
from story_overrides import story_override
from site_common import head_extra, seo_head, breadcrumb, SITE_URL, pr_notice
from related import next_section_html
# 副原料のカテゴリ判定はハブと同じロジックを使う（分類がズレると導線が壊れるため）
from gen_axes_pages import categorize_ingredient

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


def structural_signals(detail, brand):
    """味の記述が無くても、**造りのスペックから味の方向は読める**。

    従来は公式のテイスティング記述に強く依存していたため、記述の無い銘柄は
    4軸が初期値(0.5)のまま張り付いていた（濃淡で52%、甘辛で45%が該当）。
    「特徴が無い」のではなく「情報が無い」だけなのに、平坦な図はそう見える。

    そこで、酒母・麹・精米歩合・火入れ・推奨温度といった**公表されている造りの事実**から
    味の方向を推定する。ここは機械的な転記ではなく編集判断なので、
    根拠にできる関係が明確なものだけに絞る（下のコメントが各推定の根拠）。

    戻り値は各軸への増減 (body, sweet, acid, clarity) と、根拠の説明リスト。
    """
    d = detail
    why = []
    dbody = dsweet = dacid = dclar = 0.0

    shubo = str(d.get("shubo") or "")
    koji = str(d.get("koji") or "")
    temp = str(d.get("serving_temp") or "")
    polish = d.get("rice_polish")

    # 白麹はクエン酸を出す。焼酎用の麹を清酒系の造りに使う狙いは基本的に「酸」
    if "白麹" in koji or "白麹" in shubo:
        dacid += 0.18
        why.append("白麹（クエン酸由来の酸）")
    # 生酛・水酛・菩提酛は乳酸を自前で作る造り。速醸より酸が乗りやすい
    if any(k in shubo for k in ("生酛", "生もと", "水酛", "水もと", "菩提酛", "菩提もと", "花酛")):
        dacid += 0.12
        dbody += 0.08
        why.append("乳酸を自前で育てる酒母（生酛・水酛・菩提酛系）")
    # 高温糖化は短期間で糖を出す造り。甘みが残りやすい
    if "高温糖化" in shubo:
        dsweet -= 0.10
        why.append("高温糖化酛（糖が残りやすい）")
    # 全麹＝掛米を使わず米麹だけ。糖度も旨味も濃くなる
    blob = " ".join(str(d.get(k) or "") for k in
                    ("flavor_basis", "story", "sub_ingredients_detail", "koji"))
    if "全麹" in blob or "全糀" in blob:
        dbody += 0.18
        dsweet -= 0.12
        why.append("全麹仕込み（米麹のみ。糖と旨味が濃い）")
    # 精米歩合が高い＝あまり磨かない＝米の成分が多く残る
    if isinstance(polish, (int, float)) and polish >= 88:
        dbody += 0.10
        why.append(f"精米歩合{polish:.0f}%（磨かず米の成分を残す）")
    elif isinstance(polish, (int, float)) and polish <= 55:
        dbody -= 0.08
        why.append(f"精米歩合{polish:.0f}%（よく磨いた淡麗方向）")
    # 燗を勧める酒は、冷やして飲む酒より厚みのある設計であることが多い
    if any(k in temp for k in ("燗", "熱燗", "ぬる燗")):
        dbody += 0.10
        why.append("燗を勧める設計")
    # 果実の副原料は甘さと華やかさに寄る
    subs = " ".join(str(x) for x in (brand.get("sub_ingredients") or []))
    if categorize_ingredient(subs) == "fruit" or _has(subs, "ピューレ", "果汁"):
        dsweet -= 0.08
        why.append("果実を副原料に使う")
    # 搾るか搾らないかは、**その銘柄自身**の情報だけで判断する。
    # story には「どぶろくの製法をヒントに」のような蔵の説明が入るため、
    # ここを根拠にすると搾った酒まで濁りと判定してしまう（実際、
    # story を含めていたときは172銘柄の中央値が最大値0.93に張り付いた）。
    own = brand.get("name", "") + " " + str(d.get("flavor_basis") or "")
    if _has(own, "どぶろく", "ドブロク", "濁酒", "にごり", "ニゴリ", "おりがらみ", "薄にごり"):
        dclar += 0.22
        dbody += 0.08
        why.append("搾らない造り（どぶろく・濁酒）")
    elif _has(own, "澄み酒", "槽搾り", "槽絞り", "袋吊り", "清澄", "上槽"):
        dclar -= 0.18
        why.append("搾った酒（槽搾り・袋吊り等）")
    return (dbody, dsweet, dacid, dclar), why


# ────────────── 品目（酒税法上の区分） ──────────────
# 全銘柄を「その他の醸造酒」と決め打ちしていたが、実際は違う酒がある。
# 副原料を使わず搾った酒は「清酒」、発泡性を付けたものは「発泡酒」など。
# 推測はせず、**公式・蔵の記述で品目が確認できた銘柄だけ**をここに置く。
# 未確認の銘柄はクラフトサケの大半が該当する「その他の醸造酒」を既定値にする。
CATEGORY_OVERRIDE = {
    # 公式が品目を明記
    ("lagoon", 7): "発泡酒",            # 「蔵初の品目【発泡酒】製品」
    ("konohanano", 0): "濁酒",          # 「品目は『濁酒』」
    # 副原料を使わず搾った純米酒＝清酒（公式が純米大吟醸／純米と表記）
    ("hakutsuru-sakecraft", 0): "清酒",
    ("hakutsuru-sakecraft", 1): "清酒",
    ("hakutsuru-sakecraft", 2): "清酒",
    ("hakutsuru-sakecraft", 8): "清酒",
    ("ine-to-agave", 14): "清酒",        # 土田酒造での生酛・純米。副原料なし
    ("adachi-noujo", 0): "清酒",         # 公式表記「清酒(純米)」
    ("adachi-noujo", 1): "清酒",         # 公式表記「清酒・生原酒(直汲み)」
}


# ────────────── GLOSSARY（そのページに出てくる用語だけ出す） ──────────────
# クラフトサケは造りの用語が多く、初見の読者はそこで止まる。
# ただし全用語を並べると本文より長くなるため、**そのページの本文に実際に
# 現れた語だけ**を拾って出す。読みもの記事があるものはそこへ繋ぐ。
GLOSSARY_TERMS = [
    # (見出し語, 本文でこれが出たら拾う語, 解説, 読みもの記事)
    ("その他の醸造酒", ("その他の醸造酒",),
     "酒税法上の区分。米に副原料を加えて醸すと「清酒」を名乗れず、この区分になる。クラフトサケの多くがここに入る。",
     "../guide/craftsake-towa"),
    ("どぶろく（濁酒）", ("どぶろく", "ドブロク", "濁酒", "DOBUROKU", "Doburoku"),
     "もろみを搾らずにそのまま瓶詰めした酒。米の粒や澱が残り、とろりとした口当たりになる。",
     "../guide/doburoku"),
    ("にごり・おりがらみ", ("おりがらみ", "にごり", "ニゴリ", "うすにごり", "薄にごり", "澱", "オリ"),
     "搾った酒に澱（おり）をあえて残したもの。うっすら濁り、米の旨みが乗る。", None),
    ("花酛", ("花酛", "花もと", "はなもと"),
     "東北に伝わるどぶろくの古典製法。「東洋のホップ」と呼ばれる唐花草（カラハナソウ）で発酵させる。明治の自家醸造禁止で途絶えていたものを haccoba が復刻した。",
     "../guide/hanamoto"),
    ("木桶仕込み", ("木桶",),
     "ステンレスやホーローではなく木の桶で仕込む方法。桶に棲む微生物が発酵に関わり、蔵ごとの個性が出やすいとされる。",
     "../guide/kioke"),
    ("全麹仕込み", ("全麹", "全糀"),
     "仕込みに使う米を全量、麹にする造り。糖とアミノ酸が多くなり、濃厚で甘酸っぱい酒になりやすい。",
     "../guide/zenkoji"),
    ("生酛", ("生酛", "生もと", "きもと"),
     "乳酸菌を人為的に添加せず、蔵付きの乳酸菌に酸を作らせて酒母を育てる伝統製法。手間がかかるが、酸に厚みが出る。", None),
    ("水酛・菩提酛", ("水酛", "水もと", "菩提酛", "菩提もと", "ぼだいもと"),
     "室町期に寺で確立した酒母の造り方。生米を水に漬けて乳酸を得るため、独特の酸が出る。奈良・正暦寺由来のものを菩提酛と呼ぶ。", None),
    ("白麹", ("白麹", "白糀"),
     "焼酎造りに使われる麹。クエン酸を多く出すため、もろみが腐りにくく、酒に柑橘のような酸が乗る。", None),
    ("黄麹", ("黄麹", "黄糀"),
     "日本酒に古くから使われる麹。白麹ほど酸を出さず、穏やかな旨みと香りになる。", None),
    ("高温糖化酛", ("高温糖化",),
     "仕込み前に高温で米を糖化させてから酒母を立てる方法。短期間で安全に酒母ができ、糖が残りやすい。", None),
    ("速醸酛", ("速醸",),
     "醸造用乳酸を添加して酒母を立てる、明治期に確立した現代の標準的な方法。", None),
    ("ドライホッピング", ("ドライホッピング", "ドライホップ"),
     "発酵の後にホップを漬け込んで香りだけを移すクラフトビールの技法。クラフトサケでも香りづけに使われる。", None),
    ("上槽・袋吊り", ("上槽", "槽搾り", "槽絞り", "袋吊り", "雫取り"),
     "もろみを搾って酒と酒粕に分ける工程。圧をかけずに落ちる雫だけを集める袋吊りは、量は取れないが澄んだ味になる。", None),
    ("貴醸酒", ("貴醸酒",),
     "仕込み水の一部を酒に置き換えて仕込む方法。糖が残りやすく、とろりと甘い酒になる。", None),
    ("精米歩合", ("精米歩合",),
     "米を磨いて残った割合。90%なら1割だけ削った状態で、米の成分が多く残る。", None),
    ("日本酒度", ("日本酒度",),
     "酒の比重を示す数値。マイナスほど糖が多く甘口、プラスほど辛口の目安になる。", None),
    ("酸度", ("酸度",),
     "酒に含まれる有機酸の量の目安。数値が大きいほど酸を強く感じやすい。", None),
]


def glossary_section_html(page_text, num_str="§NUM§"):
    """本文に出てきた用語だけを拾って解説を付ける。最大6件。"""
    hits = [(term, desc, link) for term, trig, desc, link in GLOSSARY_TERMS
            if any(t in page_text for t in trig)]
    if not hits:
        return ""
    hits = hits[:6]
    items = "".join(
        f'<div class="glossary-item"><dt>{esc(t)}</dt>'
        f'<dd>{esc(d)}{f" <a href=\"{l}\">くわしく →</a>" if l else ""}</dd></div>'
        for t, d, l in hits)
    return f"""
  <section class="section">
    <div class="section-meta"><span class="section-meta__num">{num_str}</span><h2 class="section-meta__label">GLOSSARY / 専門用語ミニ解説</h2><span class="section-meta__rule"></span></div>
    <dl class="glossary">{items}</dl>
  </section>
"""


def derive_flavor(detail, brand):
    """flavor_basis・テイスティング・成分値・造りのスペックから4軸/6軸/タグを導出。
    値は『公式の記述と造りの情報に基づくsaketto編集部評価』。"""
    parts = [detail.get("flavor_basis"), detail.get("tasting_nose"),
             detail.get("tasting_palate"), detail.get("tasting_finish"),
             detail.get("sub_ingredients_detail"), detail.get("story"),
             # brand の note は一次ソース確認済みの短文。ここを読んでいなかったため、
             # 「うすにごり」「搾った」と明記されている酒まで判定不能になっていた。
             brand.get("note")]
    text = " ".join(p for p in parts if p)

    abv = detail.get("abv") if isinstance(detail.get("abv"), (int, float)) else brand.get("abv")

    # どの軸が「記述から決まったか」を値と別に持つ。
    # 0.5 は『根拠が無い初期値』でもあり『根拠があって中庸』でもあるため、
    # 値だけを見ると両者を区別できない（甘・辛が両方書かれた酒で実際に混同していた）。
    decided = set()

    # ── 4軸（0=左, 1=右）──
    # body: 軽快(0) ↔ 濃醇(1)
    if _has(text, "濃醇", "濃厚", "リッチ", "フルボディ", "とろみ", "とろとろ", "ムース", "コク", "膨らみ", "ボリューム", "旨味が強", "旨みを強", "完全発酵", "食い切", "長期発酵", "全麹", "濃密", "凝縮"):
        body = 0.72
        decided.add("body")
    elif _has(text, "淡麗", "軽快", "さらり", "ライト", "すっきり", "クリア", "クリーン", "スイスイ", "ドリンカブル"):
        body = 0.32
        decided.add("body")
    else:
        body = 0.5
    if isinstance(abv, (int, float)):
        if abv >= 16:
            body = min(1.0, body + 0.1)
        elif abv <= 8:
            body = max(0.0, body - 0.1)

    # sweet: 甘口(0) ↔ 辛口(1)
    sweet = 0.5
    if _has(text, "ドライ", "辛口", "キレ", "シャープ", "完全発酵", "食い切", "切れ味"):
        sweet = 0.68
        decided.add("sweet")
    # 「甘みはほとんど感じない」「甘ったるくない」のような否定表現を先に処理する。
    # これを見ないと、否定文の中の「甘み」に反応して辛口判定と相殺され、
    # 実際は甘みの無い酒が中央に落ちてしまう（nondo 水もとで実際に起きていた）。
    _dry_negation = _has(
        text, "甘みは殆ど", "甘みはほとんど", "甘味は殆ど", "甘味はほとんど",
        "甘ったるくな", "甘くな", "甘さ控えめ", "甘さを抑え", "甘みを抑え",
        "甘みが少な", "残糖感がな")
    if _dry_negation:
        sweet = 0.72
        decided.add("sweet")
    elif _has(text, "甘口", "甘味", "甘み", "甘さ", "甘酸", "甘旨", "やさしい甘", "優しい甘", "濃厚な甘", "しっかりした甘", "甘やか"):
        # 甘辛どちらの語もあるなら、それは「情報が無い」のではなく「中庸」。
        sweet = 0.5 if "sweet" in decided else 0.35
        decided.add("sweet")
    # 日本酒度の数値があれば優先（-で甘、+で辛）
    import re
    m = re.search(r"日本酒度[-−]?\s*([+\-]?\d+(?:\.\d+)?)", text)
    if m:
        try:
            v = float(m.group(1).replace("−", "-"))
            # -15..+10 を 0.15..0.8 に（負=甘=低）
            sweet = max(0.12, min(0.85, 0.5 - v / 30.0))
            decided.add("sweet")
        except ValueError:
            pass

    # acid: 酸控(0) ↔ 酸強(1)
    if _has(text, "高酸", "鋭い酸", "鋭角な酸", "サワー", "クエン酸", "しっかりした酸", "強い酸", "強めの酸", "酸でキレ", "爽快感MAX"):
        acid = 0.78
        decided.add("acid")
    # 「甘酸っぱい」「酸っぱい」は酸の記述として一般的だが、
    # 「酸味」という語を含まないため以前は拾えていなかった。
    elif _has(text, "酸味", "酸が", "爽やかな酸", "心地よい酸", "柔らかな酸", "乳酸",
              "甘酸っぱ", "酸っぱ", "酸を", "酸の立"):
        acid = 0.6
        decided.add("acid")
    elif _has(text, "酸控", "酸は穏やか", "まろやか"):
        acid = 0.35
        decided.add("acid")
    else:
        acid = 0.45
    ms = re.search(r"酸度\s*([0-9]+(?:\.\d+)?)", text)
    if ms:
        try:
            a = float(ms.group(1))
            acid = max(0.2, min(0.95, (a - 1.0) / 5.0 + 0.3))
            decided.add("acid")
        except ValueError:
            pass

    # clarity: 清澄(0) ↔ にごり(1)
    # **銘柄名と flavor_basis を最優先**。story には「どぶろくタイプを搾った澄み酒版」
    # のように、その酒自身とは逆の語が入ることがあり、そこを根拠にすると
    # 搾った酒を濁り判定してしまう（実際に「槽絞り生」「澄み酒タイプ」で誤判定していた）。
    _own = " ".join((brand.get("name", ""), str(detail.get("flavor_basis") or ""),
                     str(brand.get("note") or "")))
    if _has(_own, "澄み酒", "槽搾り", "槽絞り", "袋吊り", "上槽", "清澄"):
        clarity = 0.25
        decided.add("clarity")
    elif _has(_own, "どぶろく", "ドブロク", "にごり", "ニゴリ", "濁酒", "おりがらみ", "うす濁", "薄にごり", "白濁"):
        clarity = 0.82
        decided.add("clarity")
    elif _has(text, "どぶろく", "ドブロク", "にごり", "ニゴリ", "濁酒", "おりがらみ", "うす濁", "薄にごり", "白濁", "霞色"):
        clarity = 0.82
        decided.add("clarity")
    elif _has(text, "清澄", "クリア", "透明", "澄んだ", "クリーン"):
        clarity = 0.25
        decided.add("clarity")
    else:
        clarity = 0.5

    # ── 造りのスペックからの補正 ──
    # 味の記述で決まった軸はそのまま尊重し、**記述で決まらなかった軸ほど強く効かせる**。
    # （記述があるならそれが一次情報。造りからの推定はあくまで補助）
    (db, ds, da, dc), why = structural_signals(detail, brand)
    def _apply(cur, delta, decided):
        if delta == 0:
            return cur
        w = 0.45 if decided else 1.0   # 記述で決まっている軸は控えめに動かす
        return max(0.05, min(0.95, cur + delta * w))
    body = _apply(body, db, "body" in decided)
    sweet = _apply(sweet, ds, "sweet" in decided)
    acid = _apply(acid, da, "acid" in decided)
    clarity = _apply(clarity, dc, "clarity" in decided)
    for _ax, _dl in (("body", db), ("sweet", ds), ("acid", da), ("clarity", dc)):
        if _dl:
            decided.add(_ax)   # 造りのスペックも根拠のうち

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
    return scale4, radar6, tags, decided


# ────────────── HTML 構築（伸縮） ──────────────

def esc(s):
    return str(s) if s is not None else ""


# 読者に出してはいけない内部調査メモの語。これらを含む注記/括弧は表示時に除去する。
_CAVEAT_WORDS = ["要再確認", "未確認", "要確認", "Wikipedia", "ウィキペディア", "検索集約",
                 "閲覧不可", "テンプレ", "独立SKU", "推測", "暫定", "確認できず", "null",
                 "誤記", "残存", "準一次"]
_CAVEAT_PAREN = re.compile(r"[（(][^（()）]*(?:%s)[^（()）]*[)）]" % "|".join(_CAVEAT_WORDS))


def clean_note(s):
    """表示用に内部メモを除去。括弧内メモを削り、文全体がメモなら空にする。"""
    if not s:
        return s
    s = _CAVEAT_PAREN.sub("", str(s)).strip("　 、。/／").strip()
    if any(w in s for w in _CAVEAT_WORDS):  # 括弧外で残ったメモ語＝丸ごと内部メモ
        return ""
    return s



# 副原料カテゴリ → イメージ画像。銘柄固有の写真は無断使用NGのため、
# 既存の副原料イメージ（Vertex AI生成）をカテゴリ単位で流用する。
# 「画像はイメージ」表記を必ず添える（CLAUDE.md の画像方針）。
CAT_IMAGE = {
    "hop": ("sub_hop", "ホップ"),
    "fruit": ("sub_fruit", "果実"),
    "tea-herb": ("sub_tea_herb", "茶葉・ハーブ"),
    "rice-koji": ("sub_rice", "米と麹"),
    "special": ("sub_special", "副原料"),
}


def brand_image(brand):
    """銘柄の副原料からイメージ画像を選ぶ。(ファイル名, カテゴリ表示名) を返す。"""
    subs = [x for x in (brand.get("sub_ingredients") or []) if x]
    for x in subs:
        cat = categorize_ingredient(x)
        if cat:
            return CAT_IMAGE.get(cat, CAT_IMAGE["special"])
    # 「米のみ」系、および副原料が公式非開示のものは米と麹のイメージ
    return CAT_IMAGE["rice-koji"]


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
    price_note = clean_note(d.get("price_note")) or ("参考価格・確認日 2026/05/31" if price else "")
    subs = b.get("sub_ingredients") or []
    sub_detail = clean_note(d.get("sub_ingredients_detail"))
    category = CATEGORY_OVERRIDE.get((slug, idx), "その他の醸造酒")

    scale4, radar6, tags, _decided = derive_flavor(d, b)

    rakuten_url = resolve_rakuten(slug, idx, name)  # 実購入できない銘柄はNone（非表示）
    amazon_url = resolve_amazon(slug, idx, name)
    # Yahoo!は未調査なら None（検索へのフォールバックをしない）。
    # 「全銘柄を実際に検索して確認している」と記事に書いているため。
    yahoo_href = resolve_yahoo(slug, idx, name)
    has_buy = bool((RAKUTEN_ENABLED and rakuten_url) or (AMAZON_ENABLED and amazon_url))

    # ── HERO タグ（香り・味の印象）──
    flavor_tags_html = ""
    if tags:
        chips = "".join(f'<span class="flavor-tag">{t}</span>' for t in tags)
        flavor_tags_html = f"""
    <div class="hero__flavor">
      <div class="hero__flavor-label">— AROMA &amp; FLAVOR ／ 香り・味の印象</div>
      <div class="flavor-tags">{chips}</div>
    </div>"""

    # ── SPEC BOARD（取れたものだけ）──
    specs = []
    if abv not in (None, ""):
        av = f"{abv}" if not isinstance(abv, str) else abv
        _an = clean_note(d.get("abv_note"))
        sub = f'<div class="spec-cell__sub">{esc(_an)}</div>' if _an else ""
        specs.append(f'<div class="spec-cell"><div class="spec-cell__label">— ABV</div><div class="spec-cell__value">{av}<small>% ALC.</small></div>{sub}</div>')
    if volume not in (None, ""):
        specs.append(f'<div class="spec-cell"><div class="spec-cell__label">— VOLUME</div><div class="spec-cell__value">{volume}<small>ml</small></div></div>')
    if price not in (None, ""):
        pn = f'<div class="spec-cell__sub">{esc(price_note)}</div>' if price_note else ""
        gb = '<a class="spec-cell__gobuy" href="#purchase">購入リンクへ ↓</a>' if has_buy else ""
        specs.append(f'<div class="spec-cell"><div class="spec-cell__label">— PRICE</div><div class="spec-cell__value">¥{int(price):,}</div>{pn}{gb}</div>')
    spec_board = ('<div class="spec-board">' + "".join(specs) + "</div>") if specs else ""

    # ── RECIPE（値があるものだけ行表示）──
    rows = []

    def row(label, val, sub=None):
        if isinstance(val, str):
            val = clean_note(val)
        if isinstance(sub, str):
            sub = clean_note(sub)
        if val in (None, "", []):
            return
        sub_html = f"<small>{esc(sub)}</small>" if sub else ""
        rows.append(f'<div class="recipe-row"><div class="recipe-row__label">{label}</div><div class="recipe-row__value">{esc(val)}{sub_html}</div></div>')

    row("品目（酒税法）", category)
    # 副原料：「米のみ」系は副原料行を出さず「原料」行に。自己矛盾（副原料: 米のみ／なし）を解消
    non_rice = [s for s in subs if s and "米のみ" not in s]
    if non_rice:
        _sd = sub_detail
        if _sd and ("・".join(non_rice) in _sd or _sd in "・".join(non_rice)):
            _sd = None  # 副原料名と重複する詳細は省く
        # 副原料はハブの該当カテゴリへ直接飛ばす（ここが同系統の酒への入口になる）
        _linked = []
        for _s in non_rice:
            _cat = categorize_ingredient(_s)
            _linked.append(f'<a href="../subingredients/#cat-{_cat}">{esc(_s)}</a>' if _cat else esc(_s))
        _sub_html = f"<small>{esc(_sd)}</small>" if _sd else ""
        rows.append('<div class="recipe-row"><div class="recipe-row__label">副原料</div>'
                    f'<div class="recipe-row__value">{"・".join(_linked)}{_sub_html}</div></div>')
    elif subs:  # 米のみ系のみ
        rows.append('<div class="recipe-row"><div class="recipe-row__label">原料</div>'
                    '<div class="recipe-row__value">米・米麹のみ'
                    '<small><a href="../subingredients/#cat-rice-koji">同じ「米と麹だけ」の酒を見る →</a></small>'
                    '</div></div>')
    elif sub_detail:
        row("副原料", sub_detail)
    row("米品種", d.get("rice_variety"))
    rp = d.get("rice_polish")
    if isinstance(rp, (int, float)):
        row("精米歩合", f"{rp}%")
    elif isinstance(rp, str) and rp:
        row("精米歩合", rp)
    row("酒母", d.get("shubo"), sub=clean_note(d.get("shubo_note")))
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
    <div class="section-meta"><span class="section-meta__num">§NUM§</span><h2 class="section-meta__label">RECIPE / 仕込み</h2><span class="section-meta__rule"></span></div>
    <div class="recipe">{''.join(rows)}</div>
  </section>"""

    # ── HOW TO ENJOY（取れたものだけ）──
    enjoy_cells = []
    if d.get("serving_temp"):
        enjoy_cells.append(f'<div class="enjoy-cell"><div class="enjoy-cell__label">— TEMPERATURE</div><div class="enjoy-cell__value">{esc(d["serving_temp"])}</div></div>')
    if d.get("glass") and str(d["glass"]).strip() not in ("グラス", "グラス全般", "—", "ガラス"):
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
    <div class="section-meta"><span class="section-meta__num">§NUM§</span><h2 class="section-meta__label">HOW TO ENJOY / 楽しみ方</h2><span class="section-meta__rule"></span></div>
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
        _t_parts = [lbl for lbl, ok in (("香り", d.get("tasting_nose")),
                                         ("味わい", d.get("tasting_palate")),
                                         ("余韻", d.get("tasting_finish"))) if ok]
        tasting_section = f"""
  <section class="section">
    <div class="section-meta"><span class="section-meta__num">§NUM§</span><h2 class="section-meta__label">TASTING NOTES / {'・'.join(_t_parts)}</h2><span class="section-meta__rule"></span></div>
    <div class="tasting-3">{''.join(t_rows)}</div>
  </section>"""

    # ── FLAVOR PROFILE（根拠＝公式テイスティング記述 or 成分値/製法情報がある銘柄のみ。
    #    根拠の無い平坦グラフは「特徴の無い酒」に見え誤解を招くため出さない）──
    has_tasting = bool(d.get("tasting_nose") or d.get("tasting_palate") or d.get("tasting_finish"))
    has_basis = bool(d.get("flavor_basis")) or has_tasting
    flat_radar = len(set(radar6.values())) == 1            # 6軸が全部同値＝導出できていない
    informative_scale = any(abs(v - 0.5) >= 0.12 for v in scale4.values())
    flavor_section = ""
    if has_basis and (informative_scale or not flat_radar):
        # 何を根拠にした図なのかを読者が判断できるようにする。
        # 造りからの推定（白麹＝酸、全麹＝濃醇 等）や、飲んだ人の記述（口コミ）を
        # 使っている場合は、その旨を明示する。出典の性質が違うため。
        _, _why = structural_signals(d, b)
        # 出典種別は「公式＋販売店」のように複合で入ることがある。
        # 完全一致で見ると複合分を全部「公式」と書いてしまい、
        # 蔵が書いていない記述まで公式扱いになるため、含有で判定する。
        _st = (d.get("tasting_source_type") or "").strip()
        _who = []
        if "公式" in _st or "プレスリリース" in _st:
            _who.append("蔵の公表情報")
        if "販売店" in _st:
            _who.append("取扱店の商品説明")
        if "メディア" in _st:
            _who.append("媒体記事")
        if any(w in _st for w in ("口コミ", "SNS", "ブログ", "イベントレポ")):
            _who.append("飲んだ人の記述")
        if _who:
            _base = "・".join(_who) + ("と成分値" if has_tasting else "")
        elif has_tasting:
            _base = "公表されたテイスティング記述・成分値"
        else:
            _base = "公表された製法・原料・成分の情報"
        _cap = f"{_base}に基づく saketto 編集部評価。"
        if _why:
            _cap += "造りからの読み取り（" + "／".join(w.split("（")[0] for w in _why[:3]) + "）を含みます。"
        boxes = f'<div class="flavor-box"><div class="flavor-box__title">— STRUCTURE　<strong>4軸構造スケール</strong></div>{gen_scale4_svg(scale4)}<div class="flavor-box__cap">{_cap}</div></div>'
        if not flat_radar:   # 平坦な6軸レーダーは「特徴の無い酒」に見えるため出さない
            boxes += f'<div class="flavor-box"><div class="flavor-box__title">— PROFILE　<strong>6軸レーダー</strong></div>{gen_radar6_svg(radar6)}<div class="flavor-box__cap">同上。飲み手の印象を6軸で。</div></div>'
        flavor_section = f"""
  <section class="section">
    <div class="section-meta"><span class="section-meta__num">§NUM§</span><h2 class="section-meta__label">FLAVOR PROFILE / 味わいの構造</h2><span class="section-meta__rule"></span></div>
    <div class="flavor-wrap">
      {boxes}
    </div>
  </section>"""

    # ── STORY（充実版上書き優先。薄い事実列挙は出さない）──
    story_txt = story_override(slug, name) or d.get("story") or ""
    story_section = ""
    if len(story_txt) >= 70:
        story_section = f"""
  <div class="divider"><div class="rule"></div><div class="ornament outer"></div><div class="ornament"></div><div class="ornament outer"></div><div class="rule"></div></div>
  <section class="section">
    <div class="section-meta"><span class="section-meta__num">§NUM§</span><h2 class="section-meta__label">STORY / この銘柄が生まれた背景</h2><span class="section-meta__rule"></span></div>
    <div class="story-block"><p class="story-text">{esc(story_txt)}</p></div>
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
    <div class="section-meta"><span class="section-meta__num">§NUM§</span><h2 class="section-meta__label">ACCOLADES / 受賞</h2><span class="section-meta__rule"></span></div>
    <div class="awards-list">{cards}</div>
  </section>"""

    # ── KURA & PURCHASE ──（提携済みのボタンのみ表示。無ければ「準備中」）
    _btns = []
    if RAKUTEN_ENABLED and rakuten_url:
        _btns.append(f'<a class="purchase-card__btn purchase-card__btn--rakuten" href="{rakuten_url}" target="_blank" rel="noopener sponsored">楽天市場で探す →</a>')
    if YAHOO_ENABLED and yahoo_href:
        _btns.append(f'<a class="purchase-card__btn purchase-card__btn--yahoo" href="{yahoo_href}" target="_blank" rel="nofollow sponsored noopener">Yahoo!ショッピングで探す →</a>')
    if AMAZON_ENABLED and amazon_url:
        _btns.append(f'<a class="purchase-card__btn purchase-card__btn--amazon" href="{amazon_url}" target="_blank" rel="noopener sponsored">Amazonで探す →</a>')
    if _btns:
        # Yahoo!のインプレッションタグは1ページ1回だけ（カードごとに出すと水増しになる）
        _imp = yahoo_impression_tag() if (YAHOO_ENABLED and yahoo_href) else ''
        purchase_inner = ('<div class="purchase-card__btns">' + "".join(_btns) + '</div>'
                          '<div class="purchase-card__note">PR ／ アフィリエイトリンクを含みます</div>'
                          + _imp)
    else:
        # 通販に無い銘柄（143中85）。ここが唯一の出口なので、テキストリンクではなく
        # ボタンとして公式サイトへ送る（未使用だった --official クラスを使用）。
        _ofs = brewery.get("official_url", "")
        _alt = []
        if _ofs:
            _alt.append(f'<a class="purchase-card__btn purchase-card__btn--official" href="{_ofs}" target="_blank" rel="noopener">蔵の公式サイトで探す →</a>')
        _alt.append('<a class="purchase-card__btn purchase-card__btn--official" href="/guide/doko-de-kaeru.html">買える場所の探し方 →</a>')
        purchase_inner = (
            '<div class="purchase-card__pending">通販モールでの取り扱いは確認できていません。'
            '少量生産のため、蔵の公式オンラインショップや醸造所併設の店舗での販売が中心です。</div>'
            '<div class="purchase-card__btns">' + "".join(_alt) + '</div>')

    kura_section = f"""
  <section class="section" id="purchase">
    <div class="section-meta"><span class="section-meta__num">§NUM§</span><h2 class="section-meta__label">KURA &amp; PURCHASE / 蔵元と入手</h2><span class="section-meta__rule"></span></div>
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

    # ── 出典（一次ソース主義を画面上でも検証できるようにする）──
    # about.html で「一次ソース主義」を掲げ、テイスティング欄も「公式記述に基づく」と
    # 書いているのに、読者はその出典を1件も確認できない状態だった。
    _src = []
    _seen_url = set()

    # 🔴 社長指示（2026/09/02）：未提携ポータルへの生リンクを出さない。
    # 出典がふるさと納税ポータルを指すことがある（NOMU醸造所の銘柄背景がANAの
    # 返礼品ページだった）。出典は残さないと一次ソース主義が成り立たないので、
    # **リンクにせずテキストで示す**。アフィリ経由にはしない——出典は広告ではなく
    # 根拠であり、成果リンクに変えると役割が混ざるため。
    _PORTAL_HOSTS = ("furusato-tax.jp", "furunavi.jp", "satofull.jp",
                     "furusato.ana.co.jp", "furusato.wowma.jp")

    def _add_src(url, label):
        if url and url not in _seen_url:
            _seen_url.add(url)
            host = url.split("//")[-1].split("/")[0]
            if any(h in host for h in _PORTAL_HOSTS):
                _src.append(f'<li><span class="src-plain">{label}（{host}）</span></li>')
            else:
                _src.append(f'<li><a href="{url}" target="_blank" rel="noopener">{label}（{host}）→</a></li>')

    if official_url_ := brewery.get("official_url", ""):
        _add_src(official_url_, f'{brewery["name"]} 公式サイト')
    _add_src(d.get("story_source_url"), "この銘柄の背景（記事・公式リリース）")
    _add_src(d.get("tasting_source_url"), clean_note(d.get("tasting_source_name")) or "テイスティング記述の出典")
    for _aw in (d.get("awards") or []):
        if isinstance(_aw, dict):
            _add_src(_aw.get("source"), _aw.get("title") or "受賞の公式発表")

    # 蔵に返礼品があれば、銘柄ページからも寄附できるようにする。
    # 銘柄と返礼品は1対1に対応しないので（furusato_block.py の冒頭を参照）、
    # 「この銘柄が返礼品」とは書かず、実際の返礼品名を3件まで挙げる。
    furusato_section = furusato_render(slug, brewery["name"], rel="../",
                                       limit=3, compact=True)

    sources_section = ""
    if _src:
        sources_section = f"""
  <section class="section">
    <div class="sources">
      <h4>SOURCES ／ 出典</h4>
      <ul>{"".join(_src)}</ul>
      <p class="sources__note">掲載内容は上記の一次ソースで確認しています。価格・在庫・度数はロットや時期で変わるため、購入時は各販売ページで最新の情報をご確認ください。</p>
    </div>
  </section>"""

    # ── 公式サイト（最下部・控えめ）──
    official_url = brewery.get("official_url", "")
    official_foot = ""
    if official_url:
        host = official_url.split("//")[-1].split("/")[0]
        official_foot = f'<div class="official-foot"><a href="{official_url}" target="_blank" rel="noopener">{brewery["name"]} 公式サイト（{host}）→</a></div>'

    # ── HERO タグライン ──
    # note が空の銘柄が7件、「第二弾」等の極端に短いものが44件あり、
    # 空の場合は margin だけ残った空段落になっていた。空なら要素ごと出さず、
    # 短い場合は確認済みの事実（副原料・製法）で補う。
    _tagline = clean_note(b.get("note", "")) or ""
    if len(_tagline) < 12:
        _facts = []
        _nr = [x for x in subs if x and "米のみ" not in x]
        if _nr:
            _facts.append("副原料に" + "・".join(_nr[:2]))
        elif subs:
            _facts.append("米と米麹のみで醸す")
        for _k, _lbl in (("shubo", ""), ("vessel", ""), ("koji", "")):
            _v = clean_note(d.get(_k))
            if _v and len(_facts) < 3:
                _facts.append(_v)
        if _facts:
            _extra = "。".join(_facts)
            _tagline = f"{_tagline}／{_extra}" if _tagline else _extra

    # ── HERO 役割チップ ──
    hero = f"""
  <section class="hero">
    <div class="hero__brewery">
      <span class="role-chip role-chip--kura">蔵</span><a href="../brewery/{slug}.html">{brewery['name']}</a><span class="hero__brewery-loc">（{brewery['prefecture']}）が醸造</span>
    </div>
    <div class="hero__brandrow"><span class="role-chip role-chip--brand">銘柄</span></div>
    <h1 class="hero__name">{name}</h1>
    {f'<div class="hero__kana">{kana}</div>' if kana else ''}
    {f'<p class="hero__tagline">{esc(_tagline)}</p>' if _tagline else ''}{flavor_tags_html}
  </section>"""

    # ── イメージ画像（副原料カテゴリ単位。銘柄固有の写真ではない）──
    _img_name, _img_label = brand_image(b)
    brand_image_html = (
        f'<figure class="brand-image">'
        f'<img src="../assets/images/{_img_name}.webp" alt="{_img_label}のイメージ" '
        f'loading="lazy" decoding="async" width="1024" height="1024">'
        f'<figcaption class="brand-image__cap">{_img_label}のイメージ ／ 画像はイメージです</figcaption>'
        f'</figure>')

    # ── meta description（蔵・銘柄・note・副原料を常に合成。noteだけだと10字前後になりCTRを落とすため）──
    _subs = [s for s in (b.get('sub_ingredients') or []) if s and s != "米のみ"]
    _sub_txt = ("副原料に" + "・".join(_subs) + "を使った") if _subs else "米と米麹で醸す"
    _note = esc(b.get('note', '')).strip()
    if _note and not _note.endswith("。"):
        _note += "。"
    _head = f"{brewery['name']}（{brewery['prefecture']}）のクラフトサケ「{name}」。"
    _tail = f"{_sub_txt}一本。味わい・参考価格・購入リンクをsaketto（クラフトサケの図鑑）で。"
    meta_desc = _head + _note + _tail
    # 155字を超えるときは note を文単位で後ろから削る。
    # [:155] の機械的な切断は文の途中でぶつ切りになり、SERPでの見え方が悪かった
    while len(meta_desc) > 155 and _note:
        _note = "。".join(_note.rstrip("。").split("。")[:-1])
        if _note:
            _note += "。"
        meta_desc = _head + _note + _tail

    _path = f"/brand/{slug}-{idx}.html"
    # title：主要KW「クラフトサケ」を全銘柄ページに。銘柄名が蔵名を含む場合は蔵名を省略（二重表記防止）
    if brewery["name"] in name:
        _title_core = f"{name}｜クラフトサケ"
    else:
        _title_core = f"{name}｜{brewery['name']}のクラフトサケ"
    # OG/Product画像：蔵の専用イメージがあれば使う（全銘柄共通og.pngのままにしない）
    _img_file = REPO_ROOT / "assets" / "images" / "brewery" / f"{slug}.webp"
    _img = (SITE_URL + f"/assets/images/brewery/{slug}.webp") if _img_file.exists() \
        else (SITE_URL + "/assets/images/og.png")
    _product = {"@context": "https://schema.org/", "@type": "Product", "name": name,
                "brand": {"@type": "Brand", "name": brewery["name"]},
                "manufacturer": {"@id": SITE_URL + f"/brewery/{slug}.html#brewery"},
                "category": "クラフトサケ（その他の醸造酒）", "description": meta_desc,
                "image": _img,
                "url": SITE_URL + _path}
    if price not in (None, ""):
        # ページ本文に表示している確認済み価格をそのまま構造化データへ（嘘ゼロ準拠）。
        # availability を省くと「在庫あり」と解釈されうるため、実際に購入導線がある
        # 銘柄だけ InStock とし、通販で取扱いを確認できないものは OutOfStock を明示する。
        # url も、購入できるなら購入先を指す（自ページを指すと購入導線と誤解される）。
        _buyable = bool((RAKUTEN_ENABLED and rakuten_url) or (AMAZON_ENABLED and amazon_url))
        _offer = {"@type": "Offer", "price": str(int(price)), "priceCurrency": "JPY",
                  "availability": "https://schema.org/InStock" if _buyable
                                  else "https://schema.org/OutOfStock",
                  "url": (rakuten_url if (RAKUTEN_ENABLED and rakuten_url) else SITE_URL + _path)}
        _product["offers"] = _offer
    _seo = seo_head(_path, _title_core, meta_desc, og_type="product", image=_img, jsonld=[
        _product,
        breadcrumb([("トップ", "/"), (brewery["name"], f"/brewery/{slug}.html"), (name, _path)]),
    ])

    # NEXT / 次に出会う（機械選出の関連銘柄・回遊導線）
    next_section = next_section_html(slug, idx, num_str="§NUM§")

    # GLOSSARY は**データ側の文字列**から拾う。組み上がったHTMLを見ると、
    # 4軸グラフの軸ラベル「にごり」や表の見出し「精米歩合」に反応してしまい、
    # その酒と関係のない用語まで解説してしまう（実際に全172ページで起きた）。
    glossary_section = glossary_section_html(" ".join(str(x) for x in (
        name, category, b.get("note") or "", " ".join(map(str, subs)),
        d.get("flavor_basis") or "", d.get("tasting_nose") or "",
        d.get("tasting_palate") or "", d.get("tasting_finish") or "",
        d.get("sub_ingredients_detail") or "", story_txt,
        d.get("shubo") or "", d.get("koji") or "", d.get("vessel") or "",
        # 数値スペックは、実際に値がある時だけ用語解説の対象にする
        "精米歩合" if d.get("rice_polish") else "",
    )))

    # セクション採番：存在するセクションだけを表示順に No.01.. と連番にする（欠番を出さない）
    _n = 0
    _numbered = []
    for _s in (recipe_section, enjoy_section, tasting_section, flavor_section,
               story_section, awards_section, kura_section, glossary_section,
               next_section):
        if _s:
            _n += 1
            _numbered.append(_s.replace("§NUM§", f"No. {_n:02d}"))
    body_sections = "".join(_numbered)

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_title_core} — saketto.</title>
<meta name="description" content="{meta_desc}">
{_seo}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@400;500&family=Cormorant+Garamond:ital,wght@0,400;1,400&display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@400;500&family=Cormorant+Garamond:ital,wght@0,400;1,400&display=swap" media="print" onload="this.media=&#39;all&#39;">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@400;500&family=Cormorant+Garamond:ital,wght@0,400;1,400&display=swap"></noscript>
<style>{CSS}</style>
{head_extra()}
</head>
<body>
<main>
  <div class="masthead">
    <div class="left"><a class="brand-link" href="../index.html"><span class="accent-dot"></span>SAKETTO</a><a href="../brewery/{slug}.html">← {brewery['name']}</a></div>
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
  <nav class="crumbs" aria-label="現在地">
    <a href="../index.html">トップ</a><span class="crumbs__sep">／</span>
    <a href="../brewery/">蔵</a><span class="crumbs__sep">／</span>
    <a href="../brewery/{slug}.html">{brewery['name']}</a><span class="crumbs__sep">／</span>
    <span aria-current="page">{name}</span>
  </nav>
{hero}
{brand_image_html}
{spec_board}
{body_sections}
{furusato_section}
{sources_section}
{official_foot}
  <footer>
    <div class="colophon">
      <div class="colophon__brand"><a href="../index.html">saketto<span class="dot">.</span></a><small>— クラフトサケの図鑑</small></div>
      <div class="colophon__notes"><a href="/about.html">運営者情報</a><span class="colophon__sep">／</span><a href="/privacy.html">プライバシーポリシー</a><span class="colophon__sep">／</span><a href="/disclaimer.html">免責事項・広告表記</a><span class="colophon__sep">／</span>価格・度数は公式サイトでご確認ください<span class="colophon__sep">／</span>20歳未満の飲酒は法律で禁じられています<span class="colophon__sep">／</span>{pr_notice()}<span class="colophon__sep">／</span>© 2026 saketto.</div>
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
    for brewery in BREWERIES:
        slug = brewery["slug"]
        brands = BRANDS.get(slug, [])
        if not brands:
            continue
        details = DETAILS.get(slug, [])
        for i, brand in enumerate(brands):
            detail = details[i] if i < len(details) else {}
            html = build_html(brand, detail, brewery, i)
            (OUT_DIR / f"{slug}-{i}.html").write_text(html, encoding="utf-8")
            count += 1
    print(f"OK 生成: {count}件")


if __name__ == "__main__":
    main()

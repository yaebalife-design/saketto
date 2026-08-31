# -*- coding: utf-8 -*-
"""saketto / サイト内検索の静的インデックス生成

各ページの検索ボックスが fetch する assets/search-index.json を生成する。

収録:
  - 蔵25 / 銘柄143（件数は増えるので目安）（名前・かな・蔵名・県・地方・副原料・製法・味の印象で引ける）
  - 読みもの10本＋一覧、6つのハブ、法的3ページ
    （「花酛」「木桶」「ふるさと納税」「飲み方」等のサイト内の看板語で
      自サイトが引けない状態だったため）

URLは Cloudflare Pages の実URL（拡張子なし）で出す。

実行: cd ツール/saketto_repo/tools && python gen_search_index.py
※ データを変えたら（銘柄追加等）これも再実行して JSON を更新すること。
"""

import glob
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from breweries_master import BREWERIES, REGIONS
from breweries_brands import BRANDS

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "assets" / "search-index.json"

# 県 → 地方（「東北」等の広い語でも引けるように）
PREF_TO_REGION = {}
for _r in REGIONS:
    _key = _r[0] if isinstance(_r, (list, tuple)) else _r
    _name = _r[1] if isinstance(_r, (list, tuple)) and len(_r) > 1 else _key
    for _b in BREWERIES:
        if _b.get("region") in (_key, _name):
            PREF_TO_REGION[_b["prefecture"]] = _name

# 読みもの（タイトル＋検索されそうな語）
GUIDES = [
    ("guide/craftsake-towa", "クラフトサケとは", "基礎を知る", "クラフトサケ 定義 その他の醸造酒 日本酒 違い 製法 免許 協会 価格 度数"),
    ("guide/doburoku", "どぶろくとは", "基礎を知る", "どぶろく ドブロク 濁酒 にごり酒 清酒 違い こす 酒母 生酛 菩提酛 水酛 マッコリ"),
    ("guide/nomikata", "クラフトサケの飲み方・楽しみ方", "基礎を知る", "飲み方 温度 燗 冷酒 保存 開栓 器 グラス ペアリング 料理 ソーダ割り 季節"),
    ("guide/osusume", "クラフトサケ おすすめ12選", "選ぶ・探す", "おすすめ 12選 人気 初心者 はじめて 選び方 受賞 ICC 飲み比べ"),
    ("guide/doko-de-kaeru", "クラフトサケはどこで買える？", "選ぶ・探す", "どこで買える 買い方 通販 公式 EC 楽天 ふるさと納税 酒屋 取扱店 入手"),
    ("guide/gift", "ギフトに贈るクラフトサケ", "選ぶ・探す", "ギフト 贈り物 プレゼント 手土産 お祝い 予算 のし 熨斗 ラッピング ふるさと納税"),
    ("guide/kioke", "木桶仕込みとは", "深く味わう", "木桶 きおけ 杉 竹 箍 たが 蔵付き 微生物 醤油 味噌 発酵 職人"),
    ("guide/hanamoto", "花酛（はなもと）とは", "深く味わう", "花酛 はなもと 唐花草 カラハナソウ ホップ 東洋のホップ haccoba 幻 復刻"),
    ("guide/zenkoji", "全麹酒とは", "深く味わう", "全麹 ぜんこうじ 十割麹 掛米 麹 黄麹 白麹 黒麹 精米歩合 国菌"),
    ("guide/new-breweries", "いま生まれている、新しい蔵", "深く味わう", "新しい蔵 新規参入 免許 開業 駅ナカ 商店街 団地 離島 海外 輸出 協会"),
]

# ハブ・静的ページ
PAGES = [
    ("subingredients/", "副原料から探す", "軸", "副原料 ホップ 果実 茶葉 ハーブ 米のみ 特殊副原料 逆引き"),
    ("brewery/", "蔵から探す", "軸", "蔵 醸造所 ブルワリー 一覧 全国"),
    ("region/", "地域から探す", "軸", "地域 都道府県 産地 東北 関東 中部 関西 九州 沖縄"),
    ("genre/", "ジャンルから探す", "軸", "ジャンル ホップサケ 果実サケ 古典どぶろく 全麹酒 木桶仕込み 異素材麹 茶葉ハーブ"),
    ("furusato/", "ふるさと納税から探す", "軸", "ふるさと納税 寄附 返礼品 楽天ふるさと納税 ふるさとチョイス ふるなび さとふる"),
    ("awards/", "受賞から探す", "軸", "受賞 賞 ICC SAKE AWARD 金賞 コンテスト 海外 評価"),
    ("guide/", "読みもの", "読みもの", "読みもの 記事 ガイド コラム 入門"),
    ("about", "運営者情報", "サイト情報", "運営者 about 編集方針 一次ソース 問い合わせ"),
    ("privacy", "プライバシーポリシー", "サイト情報", "プライバシー 個人情報 cookie アクセス解析"),
    ("disclaimer", "免責事項・広告表記", "サイト情報", "免責 広告 アフィリエイト PR 表記"),
]


def _brand_details():
    """brand_data から製法・味の語を拾って検索語に足す。"""
    out = {}
    for p in glob.glob(str(Path(__file__).resolve().parent / "brand_data" / "*.json")):
        d = json.load(open(p, encoding="utf-8"))
        out[d["brewery"]] = list(d["brands"].values())
    return out


DETAILS = _brand_details()


def main():
    entries = []
    for b in BREWERIES:
        slug = b["slug"]
        region = PREF_TO_REGION.get(b["prefecture"], "")
        entries.append({
            "u": f"brewery/{slug}",
            "n": b["name"],
            "m": f"蔵 ／ {b['prefecture']}・{b['city']}",
            "t": " ".join(filter(None, [b["name"], b.get("name_kana", ""), slug,
                                        b["prefecture"], b["city"], region,
                                        b.get("features", "")])).lower(),
        })
        dets = DETAILS.get(slug, [])
        for i, br in enumerate(BRANDS.get(slug, [])):
            subs = [s for s in (br.get("sub_ingredients") or []) if s]
            det = dets[i] if i < len(dets) else {}
            method = " ".join(str(det.get(k) or "") for k in
                              ("shubo", "koji", "vessel", "rice_variety", "flavor_basis"))
            meta = f"銘柄 ／ {b['name']}（{b['prefecture']}）"
            if subs:
                meta += "　／ " + "・".join(subs[:2])
            entries.append({
                "u": f"brand/{slug}-{i}",
                "n": br["name"],
                "m": meta,
                "t": " ".join(filter(None, [br["name"], br.get("kana", ""), b["name"],
                                            slug, b["prefecture"], region,
                                            br.get("note", ""), method] + subs)).lower(),
            })

    for u, n, cat, kw in GUIDES:
        entries.append({"u": u, "n": n, "m": f"読みもの ／ {cat}", "t": f"{n} {kw}".lower()})
    for u, n, cat, kw in PAGES:
        entries.append({"u": u, "n": n, "m": cat, "t": f"{n} {kw}".lower()})

    OUT.write_text(json.dumps(entries, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    print(f"OK search-index.json: {len(entries)}件 ({OUT.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main()

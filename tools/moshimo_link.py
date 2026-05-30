# -*- coding: utf-8 -*-
"""saketto / もしもアフィリエイト リンク生成

GIN-DB と同じ もしも ID を使用（社長確認済み・運用中）。
- 楽天: 検索URLのみ使用（商品個別URLは規約違反リスク）
- Amazon: 検索URL使用
"""
import urllib.parse

# 楽天プロモ
RAKUTEN_AID = "5538619"
RAKUTEN_PID = "54"
RAKUTEN_PC_ID = "54"
RAKUTEN_PL_ID = "616"

# Amazonプロモ
AMAZON_AID = "5538622"
AMAZON_PID = "170"
AMAZON_PC_ID = "185"
AMAZON_PL_ID = "4062"


def rakuten_search(query):
    """楽天市場の検索結果ページにもしも経由で誘導"""
    target = f"https://search.rakuten.co.jp/search/mall/{urllib.parse.quote(query)}/"
    return (
        f"https://af.moshimo.com/af/c/click?"
        f"a_id={RAKUTEN_AID}&p_id={RAKUTEN_PID}&pc_id={RAKUTEN_PC_ID}&pl_id={RAKUTEN_PL_ID}"
        f"&url={urllib.parse.quote(target, safe='')}"
    )


def amazon_search(query):
    """Amazon検索結果ページにもしも経由で誘導"""
    target = f"https://www.amazon.co.jp/s?k={urllib.parse.quote(query)}"
    return (
        f"https://af.moshimo.com/af/c/click?"
        f"a_id={AMAZON_AID}&p_id={AMAZON_PID}&pc_id={AMAZON_PC_ID}&pl_id={AMAZON_PL_ID}"
        f"&url={urllib.parse.quote(target, safe='')}"
    )

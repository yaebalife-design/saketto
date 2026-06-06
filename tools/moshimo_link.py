# -*- coding: utf-8 -*-
"""saketto / もしもアフィリエイト リンク生成

- 楽天: **saketto専用ID**（2026/05/31 社長がsaketto媒体で取得・提携済）。検索URLのみ使用（商品個別URLは規約違反リスク）
- Amazon: **saketto専用ID**（2026/06/05 社長がsaketto媒体でAmazon提携承認・ID取得を確認）。検索URLのみ使用（楽天と同方針）。
  → gen_sample_v2.py の AMAZON_ENABLED=True で表示。
"""
import urllib.parse
import json
import os

# 楽天プロモ（saketto専用 / a_id=5607459）
# pl_id=616 は &url= でリンク先を指定できる「商品リンク(MyLink)」型（社長提供リンクで確認）。
# 本DBは各銘柄名の楽天検索URLを &url= に渡すため、この型を使う。
RAKUTEN_AID = "5607459"
RAKUTEN_PID = "54"
RAKUTEN_PC_ID = "54"
RAKUTEN_PL_ID = "616"

# Amazonプロモ（saketto専用 / a_id=5609637 ／ 2026/06/05 提携承認確認）
AMAZON_AID = "5609637"
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
    return _amazon_wrap(target)


def amazon_product(url):
    """Amazon商品ページ(任意URL)にもしも経由で誘導"""
    return _amazon_wrap(url)


def _amazon_wrap(target):
    return (
        f"https://af.moshimo.com/af/c/click?"
        f"a_id={AMAZON_AID}&p_id={AMAZON_PID}&pc_id={AMAZON_PC_ID}&pl_id={AMAZON_PL_ID}"
        f"&url={urllib.parse.quote(target, safe='')}"
    )


# ── 実購入可否オーバーライド ─────────────────────────────────
# affiliate_overrides.json：銘柄ごとにAmazon/楽天で本当に買えるかをWeb調査して判定した結果。
# キー "slug:idx" → {"amazon":{"show":bool,"query":str|None,"product_url":str|None},
#                    "rakuten":{"show":bool,"query":str|None}}
# 調査スクリプト：ワークフロー saketto-affiliate-availability（2026/06/06）
_OVERRIDES = None


def _load_overrides():
    global _OVERRIDES
    if _OVERRIDES is None:
        path = os.path.join(os.path.dirname(__file__), "affiliate_overrides.json")
        try:
            with open(path, encoding="utf-8") as f:
                _OVERRIDES = json.load(f)
        except (OSError, ValueError):
            _OVERRIDES = {}
    return _OVERRIDES


def resolve_rakuten(slug, idx, name):
    """楽天リンクURLを返す。買えない判定ならNone（ボタン非表示）。未登録は名前検索にフォールバック。"""
    ov = _load_overrides().get(f"{slug}:{idx}")
    if ov is None:
        return rakuten_search(name)  # 未調査銘柄は従来どおり
    r = ov.get("rakuten") or {}
    if not r.get("show"):
        return None
    return rakuten_search(r.get("query") or name)


def resolve_amazon(slug, idx, name):
    """AmazonリンクURLを返す。買えない判定ならNone（ボタン非表示）。未登録は名前検索にフォールバック。"""
    ov = _load_overrides().get(f"{slug}:{idx}")
    if ov is None:
        return amazon_search(name)  # 未調査銘柄は従来どおり
    a = ov.get("amazon") or {}
    if not a.get("show"):
        return None
    if a.get("product_url"):
        return amazon_product(a["product_url"])
    return amazon_search(a.get("query") or name)

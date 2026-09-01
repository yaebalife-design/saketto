# -*- coding: utf-8 -*-
"""saketto / もしもアフィリエイト リンク生成

- 楽天: **saketto専用ID**。2026/06/14 もしもの登録媒体を作り直したため a_id を 5607459→5637367 へ更新（社長提供リンクで確認）。検索URLのみ使用。
- Amazon: ⚠️ 媒体作り直しで旧 a_id=5609637 は無効。新Amazon a_id 未受領のため AMAZON_ENABLED=False で一時停止中。
  → 新IDを受領したら AMAZON_AID を差し替え、gen_sample_v2.py の AMAZON_ENABLED=True に戻して全ページ再生成。
"""
import urllib.parse
import json
import os

# 楽天プロモ（saketto専用 / a_id=5637367 ／ 2026/06/14 媒体作り直しで更新）
# pl_id=616 は &url= でリンク先を指定できる「商品リンク(MyLink)」型（社長提供リンクで確認）。
# 本DBは各銘柄名の楽天検索URLを &url= に渡すため、この型を使う。
RAKUTEN_AID = "5637367"
RAKUTEN_PID = "54"
RAKUTEN_PC_ID = "54"
RAKUTEN_PL_ID = "616"

# Amazonプロモ（⚠️旧 a_id=5609637 は媒体作り直しで無効。新ID受領後に差し替え）
AMAZON_AID = "5609637"
AMAZON_PID = "170"
AMAZON_PC_ID = "185"
AMAZON_PL_ID = "4062"

# Yahoo!ショッピング（saketto専用 / 2026-09-01 社長提供リンクで確認）
# pl_id=18502 は &url= でリンク先を指定できる型。
# Yahoo! は「インプレッション計測用の1x1画像」を併記する仕様なので、
# リンクを出したページには yahoo_impression_tag() を1回だけ入れること
# （カードごとに出すとインプレッションの水増しになる）。
YAHOO_AID = "5783006"
YAHOO_PID = "1225"
YAHOO_PC_ID = "1925"
YAHOO_PL_ID = "18502"


def rakuten_search(query):
    """楽天市場の検索結果ページにもしも経由で誘導"""
    target = f"https://search.rakuten.co.jp/search/mall/{urllib.parse.quote(query)}/"
    return (
        f"https://af.moshimo.com/af/c/click?"
        f"a_id={RAKUTEN_AID}&p_id={RAKUTEN_PID}&pc_id={RAKUTEN_PC_ID}&pl_id={RAKUTEN_PL_ID}"
        f"&url={urllib.parse.quote(target, safe='')}"
    )


def rakuten_url(target):
    """楽天の任意ページ（商品ページ等）にもしも経由で誘導。

    pl_id=616 は &url= で任意のリンク先を指定できる型なので、検索結果だけでなく
    商品ページにもそのまま使える。ふるさと納税の返礼品は商品URLが分かっているため、
    検索に落とさず直接その返礼品へ送る（GIN-DBは検索URLしか持っておらず
    検索結果着地になっているが、saketto は実URLを持っているのでその必要がない）。
    """
    return (
        f"https://af.moshimo.com/af/c/click?"
        f"a_id={RAKUTEN_AID}&p_id={RAKUTEN_PID}&pc_id={RAKUTEN_PC_ID}&pl_id={RAKUTEN_PL_ID}"
        f"&url={urllib.parse.quote(target, safe='')}"
    )


def yahoo_search(query):
    """Yahoo!ショッピングの検索結果ページにもしも経由で誘導"""
    target = ("https://shopping.yahoo.co.jp/search?p="
              + urllib.parse.quote(query))
    return _yahoo_wrap(target)


def yahoo_url(target):
    """Yahoo!ショッピングの任意ページ（商品ページ等）にもしも経由で誘導"""
    return _yahoo_wrap(target)


def _yahoo_wrap(target):
    return (
        f"https://af.moshimo.com/af/c/click?"
        f"a_id={YAHOO_AID}&p_id={YAHOO_PID}&pc_id={YAHOO_PC_ID}&pl_id={YAHOO_PL_ID}"
        f"&url={urllib.parse.quote(target, safe='')}"
    )


def yahoo_impression_tag():
    """Yahoo!ショッピングのインプレッション計測タグ。

    **1ページに1回だけ**出すこと。もしもの管理画面のコードはリンクとセットで
    配布されるが、商品カードごとに貼るとインプレッションを水増しすることになる。
    """
    return (
        f'<img src="https://i.moshimo.com/af/i/impression?'
        f'a_id={YAHOO_AID}&p_id={YAHOO_PID}&pc_id={YAHOO_PC_ID}&pl_id={YAHOO_PL_ID}"'
        f' width="1" height="1" style="border:none" alt="" loading="lazy">'
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


def resolve_yahoo(slug, idx, name):
    """Yahoo!ショッピングのリンクを返す。買えない判定・未調査ならNone（ボタン非表示）。

    楽天・Amazonと違い、**未登録は None**（検索へのフォールバックをしない）。
    記事に「収録銘柄すべてを実際に検索して確認している」と書いている以上、
    未調査の銘柄に自動でリンクを出すとその記述が嘘になるため。
    """
    ov = _load_overrides().get(f"{slug}:{idx}")
    if not ov:
        return None
    y = ov.get("yahoo") or {}
    if not y.get("show"):
        return None
    if y.get("product_url"):
        return yahoo_url(y["product_url"])
    return yahoo_search(y.get("query") or name)


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


# ── アフィリエイトの有効/無効 ─────────────────────────────
# ここが唯一の定義。gen_sample_v2 が再エクスポートし、site_common の
# 広告表記もここを見る（表記だけ実態とズレるのを防ぐため）。
RAKUTEN_ENABLED = True    # 2026/05/31 楽天 saketto提携済 → ON
AMAZON_ENABLED = False    # 2026/06/14 もしも媒体作り直しで旧Amazon ID無効 → 新ID受領まで一時OFF
YAHOO_ENABLED = True      # 2026/09/01 Yahoo!ショッピング saketto提携済（社長提供リンクで確認）
AFFILIATE_ENABLED = RAKUTEN_ENABLED or AMAZON_ENABLED or YAHOO_ENABLED

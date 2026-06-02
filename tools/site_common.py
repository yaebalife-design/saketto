# -*- coding: utf-8 -*-
"""saketto 全ページ共通の <head> パーツ（GA タグ・年齢ゲート）。
各 gen_*.py がここを import して head に差し込む。手書きの index.html は
このファイルの定義に合わせて手で揃える（GA_ID を変えたら両方直すこと）。
"""

# GA4 測定ID。社長から本番IDを受領したらここを差し替えて全ページ再生成する。
# 内部トラフィック（自分のアクセス）の除外は GIN-DB と同様に GA 管理画面側で行う：
#   管理 → データストリーム → タグ設定 → 内部トラフィックの定義（自宅IPを登録）
#   → 管理 → データフィルタ → 「Internal Traffic」を有効化
# コード側は標準 gtag のままでよい（IP除外はサーバー/管理画面側で完結）。
GA_ID = "G-REYY1OPEK2"


def analytics_head():
    """GA4 gtag.js ブロック。絶対URLなのでページ階層に依存しない。"""
    return (
        "<!-- Google tag (gtag.js) -->\n"
        f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>\n'
        "<script>\n"
        "  window.dataLayer = window.dataLayer || [];\n"
        "  function gtag(){dataLayer.push(arguments);}\n"
        "  gtag('js', new Date());\n"
        f"  gtag('config', '{GA_ID}');\n"
        "</script>"
    )


def age_gate_tag(prefix="../"):
    """年齢ゲート読み込み。prefix はリポジトリルートからの相対（サブディレクトリは "../"、ルートは ""）。"""
    return f'<script src="{prefix}assets/age-gate.js" defer></script>'


def favicon_head():
    """ファビコン群（絶対パス参照なのでページ階層に依存しない）。"""
    return (
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
        '<link rel="alternate icon" href="/favicon.ico" sizes="any">\n'
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">'
    )


def head_extra(prefix="../"):
    """head 末尾（</head> 直前）に入れる共通ブロック。"""
    return favicon_head() + "\n" + analytics_head() + "\n" + age_gate_tag(prefix)


# ────────────── OGP / canonical / 構造化データ(JSON-LD) ──────────────
import json as _json

SITE_URL = "https://saketto.com"
SITE_NAME = "saketto"
OG_IMAGE = SITE_URL + "/assets/images/og.png"


def _attr(s):
    """HTML属性値用エスケープ。"""
    return (str(s).replace("&", "&amp;").replace('"', "&quot;")
            .replace("<", "&lt;").replace(">", "&gt;"))


def breadcrumb(items):
    """items=[(name, path), ...]（path はサイト内絶対パス）→ BreadcrumbList dict。"""
    return {
        "@context": "https://schema.org/",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name,
             "item": SITE_URL + path}
            for i, (name, path) in enumerate(items)
        ],
    }


def website_node():
    return {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL + "/"}


def seo_head(path, og_title, description, og_type="website", image=None, jsonld=None):
    """canonical + OGP + Twitterカード + JSON-LD をまとめて返す。
    path: サイト内絶対パス（例 "/", "/brand/haccoba-0.html", "/genre/"）。
    jsonld: dict または dict のリスト（各々 <script type=ld+json> 1個に）。
    """
    url = SITE_URL + path
    img = image or OG_IMAGE
    t, dsc = _attr(og_title), _attr(description)
    lines = [
        f'<link rel="canonical" href="{url}">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        f'<meta property="og:title" content="{t}">',
        f'<meta property="og:description" content="{dsc}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{img}">',
        '<meta property="og:locale" content="ja_JP">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{t}">',
        f'<meta name="twitter:description" content="{dsc}">',
        f'<meta name="twitter:image" content="{img}">',
    ]
    if jsonld:
        nodes = jsonld if isinstance(jsonld, list) else [jsonld]
        for n in nodes:
            lines.append('<script type="application/ld+json">'
                         + _json.dumps(n, ensure_ascii=False) + '</script>')
    return "\n".join(lines)

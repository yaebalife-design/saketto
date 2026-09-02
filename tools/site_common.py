# -*- coding: utf-8 -*-
"""saketto 全ページ共通の <head> パーツ（GA タグ・年齢ゲート）。
各 gen_*.py がここを import して head に差し込む。手書きの index.html は
このファイルの定義に合わせて手で揃える（GA_ID を変えたら両方直すこと）。
"""

# GA4 測定ID（「10」は数字のイチ・ゼロ。2026/06/13 英字Oのタイプミスを修正。GA4管理画面のコードと要一致）。
# 内部トラフィック（自分のアクセス）の除外は GIN-DB と同様に GA 管理画面側で行う：
#   管理 → データストリーム → タグ設定 → 内部トラフィックの定義（自宅IPを登録）
#   → 管理 → データフィルタ → 「Internal Traffic」を有効化
# コード側は標準 gtag のままでよい（IP除外はサーバー/管理画面側で完結）。
GA_ID = "G-REYY10PEK2"


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
    return f'<script src="{prefix}assets/age-gate.v2.js" defer></script>'


def favicon_head():
    """ファビコン群（絶対パス参照なのでページ階層に依存しない）。"""
    return (
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
        '<link rel="alternate icon" href="/favicon.ico" sizes="any">\n'
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">'
    )


MOBILE_FIX_CSS = """<style>
/* ── スマホ共通調整（各テンプレのCSSより後に読ませて後勝ちさせる） ──
   左右32pxのままだと日本語が14〜17文字/行になり読みづらいため20pxへ詰める。
   4軸スケールSVGは viewBox 480 に対し表示幅が261pxしかなく、
   font-size=11/13 が実効6〜7pxまで潰れて漢字が判読できないので拡大する。 */
@media (max-width: 640px) {
  .section { padding-left: 1.25rem; padding-right: 1.25rem; }
  .divider { padding-left: 1.25rem; padding-right: 1.25rem; }
  .colophon { padding-left: 1.25rem; padding-right: 1.25rem; }
  .article { padding-left: 1.25rem; padding-right: 1.25rem; }
  .spec-board { padding-left: 1.25rem; padding-right: 1.25rem; }
  .official-foot { padding-left: 1.25rem; padding-right: 1.25rem; }
  .masthead { padding-left: 1.25rem; padding-right: 1.25rem; }
  .hero { padding-left: 1.25rem; padding-right: 1.25rem; }
  .story-block { padding: 1.5rem 1.25rem; }
  .purchase-card, .kura-card, .enjoy-cell, .tasting-row { padding: 1.25rem 1.15rem; }
  /* 見出しの装飾罫が2行目に取り残されるのを防ぐ（線の見え方を全ページで揃える） */
  .section-meta { flex-wrap: wrap; }
  .section-meta__rule { min-width: 2.5rem; }
}
@media (max-width: 860px) {
  .flavor-box svg[viewBox^="0 0 480"] text { font-size: 21px; }
}
/* アフィリエイト/主要導線のタップ領域を44px以上に（iOS HIG） */
.brand-card__shoplink, .spec-cell__gobuy, .kura-card__link,
.section-morelink a, .pick__detail { display: inline-flex; align-items: center; min-height: 44px; }
.masthead-nav a { min-height: 44px; display: inline-flex; align-items: center; }
/* PR表記は景品表示法の観点で小さすぎないこと */
.pick__pr, .purchase-card__note { font-size: .8rem; }
/* 買えない銘柄の唯一の出口。暗色カード上で既定リンク色だとコントラスト2.0:1で読めない */
.purchase-card__pending a { color: #F0C9BC; border-bottom: 1px solid #A8351F; text-decoration: none; }
.purchase-card__pending a:hover { color: #FAF6ED; }
</style>"""


SEARCH_CSS = """<style>
/* ── 現在地パンくず（JSON-LDと同じ階層を画面にも出す） ── */
.crumbs { max-width:1100px; margin:0 auto; padding:.9rem 2rem 0;
  font-family:'Zen Kaku Gothic Antique',sans-serif; font-size:.8rem;
  color:var(--ink-mute); letter-spacing:.04em; }
.crumbs a { color:var(--ink-mute); text-decoration:none; border-bottom:1px solid transparent; }
.crumbs a:hover { color:var(--accent); border-bottom-color:var(--accent); }
.crumbs__sep { margin:0 .5rem; color:var(--line); }
.crumbs [aria-current="page"] { color:var(--ink); }
@media (max-width:640px){ .crumbs { padding:.8rem 1.25rem 0; font-size:.75rem; } }

/* 現在いる軸をナビで示す */
.masthead-nav a[aria-current="page"] { color:var(--accent); border-bottom:1px solid var(--accent); }

/* ── 全ページ共通のマストヘッド検索 ── */
.sk-navsearch { position:relative; margin-left:auto; }
.sk-navsearch__label { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
.sk-navsearch input {
  font-family:'Zen Kaku Gothic Antique',sans-serif; font-size:16px; /* iOSの自動ズーム回避 */
  padding:.5rem .8rem; min-height:44px; width:min(260px,52vw);
  border:1px solid var(--line); background:var(--paper); color:var(--ink);
  letter-spacing:.03em; -webkit-appearance:none; border-radius:0;
}
.sk-navsearch input::placeholder { color:var(--ink-mute); }
.sk-navsearch input:focus { outline:2px solid var(--accent); outline-offset:2px; }
.sk-navsearch__results {
  position:absolute; top:calc(100% + .4rem); right:0; z-index:80;
  width:min(360px,86vw); max-height:60vh; overflow-y:auto;
  background:var(--paper); border:1px solid var(--line);
  box-shadow:0 14px 40px rgba(26,23,23,.14); text-align:left;
}
.sk-navsearch__results .search-hit { display:block; padding:.75rem .9rem; text-decoration:none;
  border-bottom:1px solid var(--line-soft); color:var(--ink); text-transform:none; letter-spacing:normal; }
.sk-navsearch__results .search-hit:last-child { border-bottom:none; }
.sk-navsearch__results .search-hit:hover,
.sk-navsearch__results .search-hit.is-active { background:var(--bg-alt); }
.sk-navsearch__results .search-hit__name { display:block; font-family:'Shippori Mincho',serif;
  font-weight:700; font-size:1rem; color:var(--ink); }
.sk-navsearch__results .search-hit__meta { display:block; font-size:.78rem; color:var(--ink-mute); margin-top:.15rem; }
.sk-navsearch__results .search-hit--none { padding:.85rem .9rem; font-size:.85rem;
  color:var(--ink-mute); text-transform:none; letter-spacing:normal; }
@media (max-width:640px) {
  .sk-navsearch { width:100%; margin-left:0; }
  .sk-navsearch input { width:100%; }
  .sk-navsearch__results { width:100%; }
}
</style>"""


def pr_notice():
    """フッターの広告表記。実際に貼っているリンクから文言を決める。

    全ページのフッターが「アフィリエイト広告（Amazonアソシエイト含む）を
    掲載しています」と書いていたが、Amazonリンクは1本も無かった
    （旧IDが無効になって AMAZON_ENABLED=False のまま）。
    表記を手で書くと実態と必ずズレるので、フラグから組み立てる。
    Amazonの提携が戻って AMAZON_ENABLED=True にすれば、
    Amazonアソシエイトの必須表記も自動で復活する。
    """
    from moshimo_link import RAKUTEN_ENABLED, AMAZON_ENABLED
    if AMAZON_ENABLED:
        return ("PR ／ 当サイトはアフィリエイト広告（Amazonアソシエイト含む）"
                "を掲載しています")
    if RAKUTEN_ENABLED:
        return "PR ／ 当サイトはアフィリエイト広告を掲載しています"
    return "PR ／ 当サイトは広告を掲載することがあります"


def search_tag():
    """サイト内検索（全ページ共通）。インデックスはルート絶対パスで引くため階層非依存。"""
    return '<script src="/assets/search.v3.js" defer></script>'


def head_extra(prefix="../"):
    """head 末尾（</head> 直前）に入れる共通ブロック。"""
    return (favicon_head() + "\n" + analytics_head() + "\n"
            + age_gate_tag(prefix) + "\n" + MOBILE_FIX_CSS + "\n"
            + SEARCH_CSS + "\n" + search_tag())


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


def canonical_path(path):
    """Cloudflare Pages は `/x.html` を `/x` へ308でリダイレクトする。
    canonical や sitemap に .html 付きを載せると、200を返すURLが
    「リダイレクトされる別URL」を正規と名乗ることになり、クロール予算を捨てる。
    そのため公開URLは常に拡張子なしへ正規化する（index.html はディレクトリに）。
    """
    if path.endswith("/index.html"):
        return path[: -len("index.html")]
    if path == "/index.html":
        return "/"
    if path.endswith(".html"):
        return path[: -len(".html")]
    return path


_HTML_URL_RE = None


def _normalize_jsonld_urls(node):
    """JSON-LD の中の自サイトURLから .html を落とす。

    canonical と OG は canonical_path() を通していたが、JSON-LD の dict は
    各 gen_*.py が seo_head を呼ぶ前に組み立てており、素のパス（.html付き）が
    そのまま url / @id / BreadcrumbList の item に入っていた。
    canonical は拡張子なし、構造化データは .html という食い違いが
    216ページ中207ページで起きていたため、ここで一括して揃える。
    呼び出し側の書き方に依存しないよう、値を再帰的に走査する。
    """
    import re as _re
    global _HTML_URL_RE
    if _HTML_URL_RE is None:
        _HTML_URL_RE = _re.compile(_re.escape(SITE_URL) + r"(/[^\"\s]*?\.html)")

    if isinstance(node, dict):
        return {k: _normalize_jsonld_urls(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_normalize_jsonld_urls(v) for v in node]
    if isinstance(node, str) and SITE_URL in node and ".html" in node:
        return _HTML_URL_RE.sub(lambda m: SITE_URL + canonical_path(m.group(1)), node)
    return node


def seo_head(path, og_title, description, og_type="website", image=None, jsonld=None):
    """canonical + OGP + Twitterカード + JSON-LD をまとめて返す。
    path: サイト内絶対パス（例 "/", "/brand/haccoba-0.html", "/genre/"）。
    jsonld: dict または dict のリスト（各々 <script type=ld+json> 1個に）。
    """
    path = canonical_path(path)
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
                         + _json.dumps(_normalize_jsonld_urls(n),
                                       ensure_ascii=False) + '</script>')
    return "\n".join(lines)

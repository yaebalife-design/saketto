# -*- coding: utf-8 -*-
"""蔵ページ・銘柄ページに置く「ふるさと納税の返礼品」ブロック。

## なぜ蔵単位で、返礼品名を必ず出すのか

返礼品と収録銘柄は**一致しない**。2026/09/02 に全件突き合わせたところ、
30件の返礼品のうち銘柄ページと確実に対応するのは3件だけだった。

    天郷醸造所   返礼品「在る宵 緒奏」   銘柄ページ「在る 緒奏」    ← 別表記か別商品か不明
    ハッピー太郎  返礼品「ハッピーどぶろく 480ml×2本」  ← 銘柄指定のない詰め合わせ
    平和どぶろく  返礼品「壱ノ濁・弐ノ濁・参ノ濁」  銘柄ページ「プレーン/小豆/黒豆/ホップ」
    LAGOON     返礼品「燕市産こしいぶき＋どぶろく」   ← どの銘柄のどぶろくか記載なし

そのため「この銘柄が返礼品です」とは書けない（嘘ゼロに反する）。
代わりに**実際の返礼品名と寄附額をそのまま列挙する**。こうすれば
どのページに置いても書いてあることは事実になり、読者も何がもらえるか分かる。

## リンクの原則

- 楽天=もしも経由、それ以外=A8経由。ASPを通せないポータルはリンクにしない
  （社長指示：未提携ポータルへ生URLを出さない）
- A8の商品リンクは <a>＋<img> で1組。切り離さない
"""
from furusato_data import (
    FURUSATO, PORTAL_NAMES, PORTAL_ORDER, items_of, is_accepting,
)
from moshimo_link import rakuten_url
from a8_link import portal_href as a8_portal_href, render_pixel as a8_pixel


def has_furusato(slug):
    return bool(FURUSATO.get(slug))


def _portal_links(slug, brand, item_urls):
    """ある返礼品（銘柄名で束ねたもの）のポータルリンク群。"""
    out = []
    for code in PORTAL_ORDER:
        u = item_urls.get(code)
        if not u:
            continue
        label = PORTAL_NAMES.get(code, code)
        if code == "r":
            out.append(f'<a class="fz-portal" href="{rakuten_url(u)}" target="_blank" '
                       f'rel="nofollow sponsored noopener">{label}</a>')
            continue
        href = a8_portal_href(code, u)
        if not href:
            # 未提携。扱いがある事実だけ非リンクで残す
            out.append(f'<span class="fz-portal is-plain">{label}</span>')
            continue
        out.append(f'<a class="fz-portal" href="{href}" target="_blank" '
                   f'rel="nofollow sponsored noopener">{label}</a>{a8_pixel(code)}')
    return "".join(out)


# 酒以外の食品と組み合わせた返礼品を見分ける語。ここに挙げたものだけを
# 「食品セット」として後ろへ回す。該当は天郷（干物・漬け魚・もつ鍋）と
# LAGOON（米）だけなので、増えたら足す。
_FOOD_WORDS = ("干物", "漬け魚", "もつ鍋", "こしいぶき", "お米", "チーズケーキ")


def _is_food_set(brand):
    return any(w in brand for w in _FOOD_WORDS)


def _rows(slug, limit=None):
    """返礼品を銘柄名で束ね、(銘柄, 寄附額, 申込可, ポータルHTML) を安い順に返す。"""
    grouped = {}
    for it in items_of(slug):
        g = grouped.setdefault(it["brand"], {"yen": it.get("yen"),
                                             "urls": {}, "accepting": False})
        g["urls"].setdefault(it["portal"], it["url"])
        if it.get("accepting", True):
            g["accepting"] = True
        if it.get("yen") and (not g["yen"] or it["yen"] < g["yen"]):
            g["yen"] = it["yen"]
    # 並びは「申込できる > 酒そのもの > 安い順」。
    # 品切れが先頭だと使えないページに見える。また天郷は食品セット（緒奏180ml入り）が
    # 最安なので、額だけで並べると酒のページの先頭が「漬け魚詰合せ」になってしまう。
    # 酒そのものを先に見せ、食品とのセットだけ後ろへ回す。
    # 「＋」の有無で判定すると酒同士のセットまで落ちるので、食品の語で判定する
    # （それで定期便82,000円が20,000円のセットより上に来ていた）。
    rows = sorted(grouped.items(),
                  key=lambda kv: (not kv[1]["accepting"],
                                  _is_food_set(kv[0]),
                                  kv[1]["yen"] or 10 ** 9))
    if limit:
        rows = rows[:limit]
    return [(b, g["yen"], g["accepting"], _portal_links(slug, b, g["urls"]))
            for b, g in rows]


def render(slug, brewery_name, rel="../", limit=None, section_num=None, compact=False):
    """返礼品ブロックのHTML。返礼品が無ければ空文字。

    limit … 表示する返礼品の上限（銘柄ページ用に絞るとき）
    compact … 見出しを小さくし、説明文を省く（銘柄ページ用）
    """
    if not has_furusato(slug):
        return ""
    data = FURUSATO[slug]
    rows = _rows(slug, limit=limit)
    if not rows:
        return ""
    total = len({i["brand"] for i in items_of(slug)})

    body = []
    for brand, yen, accepting, portals in rows:
        yen_txt = f'{yen:,}円' if yen else '寄附額はリンク先で確認'
        sold = '' if accepting else '<span class="fz-sold">品切れ中</span>'
        body.append(f'<li class="fz-item"><div class="fz-item__head">'
                    f'<span class="fz-brand">{brand}</span>'
                    f'<span class="fz-yen">{yen_txt}</span>{sold}</div>'
                    f'<div class="fz-portals">{portals}</div></li>')

    more = ''
    if limit and total > len(rows):
        more = (f'<a class="fz-more" href="{rel}furusato/">'
                f'ほか{total - len(rows)}品を見る</a>')

    head = f'<h3 class="fz-title">ふるさと納税でもらう</h3>'
    if not compact and section_num:
        head = (f'<div class="section-meta">'
                f'<span class="section-meta__num">No. {section_num:02d}</span>'
                f'<h2 class="section-meta__label">FURUSATO TAX</h2>'
                f'<span class="section-meta__count">/ {total} 品</span>'
                f'<span class="section-meta__rule"></span></div>')

    lead = ''
    if not compact:
        status = '' if is_accepting(slug) else '（現在はすべて品切れ）'
        lead = (f'<p class="fz-lead">{data["city"]}への寄附で、{brewery_name}の酒が'
                f'返礼品として届きます{status}。'
                f'寄附額と在庫は変わるので、申し込む前にリンク先で確かめてください。</p>')

    return (f'<section class="section fz-block">{head}{lead}'
            f'<ul class="fz-list">{"".join(body)}</ul>{more}'
            f'<p class="fz-note">※ ポータルへのリンクはアフィリエイト広告（PR）です。'
            f'寄附額に影響はありません。</p></section>')


CSS = """
.fz-block { background:var(--bg-alt); padding:1.6rem 1.8rem; }
.fz-title {
  font-family:'Shippori Mincho',serif; font-size:1rem; font-weight:500;
  color:var(--ink); letter-spacing:.05em; margin:0 0 .7rem;
}
.fz-lead, .fz-note {
  font-family:'Zen Kaku Gothic Antique',sans-serif; color:var(--ink-mute);
  font-size:.82rem; line-height:1.9;
}
.fz-lead { margin:0 0 1rem; }
.fz-note { margin:.9rem 0 0; }
.fz-list { list-style:none; display:flex; flex-direction:column; gap:.9rem; margin:0; }
.fz-item { border-top:1px solid var(--line-soft); padding-top:.75rem; }
.fz-item:first-child { border-top:none; padding-top:0; }
.fz-item__head { display:flex; align-items:baseline; flex-wrap:wrap; gap:.5rem .8rem; }
.fz-brand {
  font-family:'Zen Kaku Gothic Antique',sans-serif; font-size:.9rem;
  font-weight:500; color:var(--ink);
}
.fz-yen {
  font-family:'Cormorant Garamond',serif; font-style:italic;
  font-size:.9rem; color:var(--accent); white-space:nowrap;
}
.fz-sold {
  font-family:'Zen Kaku Gothic Antique',sans-serif; font-size:.72rem;
  color:var(--ink-mute); border:1px solid var(--line-soft); padding:.05rem .4rem;
}
/* A8の計測ピクセル(1x1)を包む器。imgタグ自体は無改変で、
   flexのgapで隙間が空かないようフローから外す。 */
.fz-portals { position:relative; display:flex; flex-wrap:wrap; gap:.4rem; margin-top:.45rem; }
.a8-px { position:absolute; width:1px; height:1px; overflow:hidden; }
.fz-portal {
  font-family:'Zen Kaku Gothic Antique',sans-serif; font-size:.76rem;
  padding:.28rem .7rem; border:1px solid var(--line); background:var(--paper);
  color:var(--ink-soft); text-decoration:none; transition:border-color .25s, color .25s;
}
a.fz-portal:hover { border-color:var(--accent); color:var(--accent); }
/* ASP未提携のポータルは押せそうに見せない */
.fz-portal.is-plain { border-style:dashed; border-color:var(--line-soft); color:var(--ink-mute); }
.fz-more {
  display:inline-block; margin-top:.9rem;
  font-family:'Zen Kaku Gothic Antique',sans-serif; font-size:.82rem;
  color:var(--accent); text-decoration:none; border-bottom:1px solid var(--line);
}
"""

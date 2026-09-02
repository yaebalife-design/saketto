# -*- coding: utf-8 -*-
"""saketto の robots.txt と sitemap.xml を生成する。
リポジトリ直下の .html を全走査し、内部リンクと同じ正規URLで列挙する：
  - ルート index.html         → /
  - {dir}/index.html         → /{dir}/        （末尾スラッシュ。ハブは "../{dir}/" でリンクされている）
  - {dir}/{name}.html        → /{dir}/{name}.html （蔵・銘柄・記事は .html でリンクされている）

使い方:  python gen_seo.py
※ 全ページは現在 noindex（公開準備中）。robots は GIN-DB と同様 Allow: / とし、
   インデックス可否は各ページの noindex メタで制御する。DNS紐付け後に noindex を一括解除する。
"""

import datetime
import hashlib
import json
from pathlib import Path

BASE_URL = "https://saketto.com"
REPO_ROOT = Path(__file__).resolve().parent.parent  # saketto_repo/

# lastmod の状態ファイル。以前は st_mtime を使っていたため、全ページ再生成のたびに
# 226件が同一日付になり、Googleがlastmodを無視する典型パターンだった。
# 内容ハッシュが変わったページだけ日付を更新する。
# ※本スクリプトは normalize_links / externalize_css より前に走るため、
#   ハッシュは「後処理前の内容」で毎回一貫して比較される（データが同じなら同じ値になる）
LASTMOD_STATE = Path(__file__).resolve().parent / "lastmod_state.json"

# 走査から除外するファイル名
EXCLUDE_NAMES = {"404.html", "google", "ads.txt"}

# 走査から除外するディレクトリ。公開対象はリポジトリ直下の各ハブだけで、
# ここは生成スクリプトとその作業用出力が入る場所なので sitemap に載せない。
# （gen_brand_pages_v2.py が書く tools/_preview/*.html が
#   https://saketto.com/tools/_preview/... として sitemap に載っていた）
EXCLUDE_DIRS = {".git", "tools", "node_modules"}


def url_and_priority(rel_parts, fname):
    """相対パス要素とファイル名から (パス, priority) を返す。"""
    if not rel_parts and fname == "index.html":
        return "/", "1.0"
    if fname == "index.html":
        # サブディレクトリのハブ → 末尾スラッシュ
        return "/" + "/".join(rel_parts) + "/", "0.9"
    # 通常ページ。Cloudflare Pages は /x.html を /x へ308でリダイレクトするため、
    # sitemap には最終URL（拡張子なし）を載せる。
    path = "/" + "/".join(list(rel_parts) + [fname[:-len(".html")] if fname.endswith(".html") else fname])
    top = rel_parts[0] if rel_parts else ""
    if top == "guide":
        prio = "0.85"
    elif top == "brewery":
        prio = "0.8"
    elif top == "brand":
        prio = "0.7"
    else:
        prio = "0.6"
    return path, prio


def collect():
    try:
        state = json.loads(LASTMOD_STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        state = {}
    today = datetime.date.today().isoformat()

    entries = []  # (path, priority, lastmod)
    new_state = {}
    for html in sorted(REPO_ROOT.rglob("*.html")):
        if EXCLUDE_DIRS.intersection(html.parts):
            continue
        if html.name in EXCLUDE_NAMES:
            continue
        rel = html.relative_to(REPO_ROOT)
        rel_parts = rel.parts[:-1]  # ディレクトリ部分
        path, prio = url_and_priority(rel_parts, html.name)
        digest = hashlib.md5(html.read_bytes()).hexdigest()
        prev = state.get(path)
        if prev and prev.get("hash") == digest:
            lastmod = prev["date"]      # 内容が同じなら日付を据え置く
        else:
            lastmod = today             # 内容が変わったページだけ今日にする
        new_state[path] = {"hash": digest, "date": lastmod}
        entries.append((path, prio, lastmod))
    LASTMOD_STATE.write_text(
        json.dumps(new_state, ensure_ascii=False, indent=1, sort_keys=True),
        encoding="utf-8")
    # priority 降順 → パス昇順で安定ソート
    entries.sort(key=lambda e: (-float(e[1]), e[0]))
    return entries


def build_sitemap(entries):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, prio, lastmod in entries:
        lines.append(
            f'  <url><loc>{BASE_URL}{path}</loc>'
            f'<priority>{prio}</priority><lastmod>{lastmod}</lastmod></url>'
        )
    lines.append('</urlset>')
    return "\n".join(lines) + "\n"


def build_robots():
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {BASE_URL}/sitemap.xml\n"
    )


def main():
    entries = collect()
    (REPO_ROOT / "sitemap.xml").write_text(build_sitemap(entries), encoding="utf-8")
    (REPO_ROOT / "robots.txt").write_text(build_robots(), encoding="utf-8")
    print(f"  sitemap.xml  ({len(entries)} URL)")
    print(f"  robots.txt   (Allow: / / Sitemap: {BASE_URL}/sitemap.xml)")
    # 内訳
    by_top = {}
    for path, _, _ in entries:
        top = path.split("/")[1] if path != "/" else "(root)"
        by_top[top] = by_top.get(top, 0) + 1
    for top, n in sorted(by_top.items()):
        print(f"    {top}: {n}")


if __name__ == "__main__":
    main()

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
from pathlib import Path

BASE_URL = "https://saketto.com"
REPO_ROOT = Path(__file__).resolve().parent.parent  # saketto_repo/

# 走査から除外するファイル名
EXCLUDE_NAMES = {"404.html", "google", "ads.txt"}


def url_and_priority(rel_parts, fname):
    """相対パス要素とファイル名から (パス, priority) を返す。"""
    if not rel_parts and fname == "index.html":
        return "/", "1.0"
    if fname == "index.html":
        # サブディレクトリのハブ → 末尾スラッシュ
        return "/" + "/".join(rel_parts) + "/", "0.9"
    # 通常ページ
    path = "/" + "/".join(list(rel_parts) + [fname])
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
    entries = []  # (path, priority, lastmod)
    for html in sorted(REPO_ROOT.rglob("*.html")):
        if ".git" in html.parts:
            continue
        if html.name in EXCLUDE_NAMES:
            continue
        rel = html.relative_to(REPO_ROOT)
        rel_parts = rel.parts[:-1]  # ディレクトリ部分
        path, prio = url_and_priority(rel_parts, html.name)
        lastmod = datetime.date.fromtimestamp(html.stat().st_mtime).isoformat()
        entries.append((path, prio, lastmod))
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

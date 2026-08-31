# -*- coding: utf-8 -*-
"""公開前の内部リンク検証（拡張子なしURL前提）。

Cloudflare Pages は `/x.html` を `/x` へ 308 で飛ばすので、公開URLは拡張子なしに
正規化してある（normalize_links.py）。したがってリンク先の実ファイルは
`x` / `x.html` / `x/index.html` のいずれかで解決する必要がある。
この違いを見落として「2,410本リンク切れ」と誤報したことがあるため、
解決規則をツール側に固定した。

    cd ツール/saketto_repo && python tools/verify_links.py
"""
import os
import re
import sys
from urllib.parse import unquote, urldefrag

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HREF_RE = re.compile(r'(?:href|src)="([^"]+)"')
SKIP_PREFIX = ("http://", "https://", "mailto:", "tel:", "javascript:", "data:", "#")


def resolve(target):
    """サイト内パスが実ファイルに解決できるか。拡張子なしURLの3形態を試す。"""
    p = os.path.join(ROOT, target.lstrip("/").replace("/", os.sep))
    if os.path.isfile(p):
        return True
    if os.path.isfile(p + ".html"):
        return True
    if os.path.isfile(os.path.join(p, "index.html")):
        return True
    return False


def main():
    html_files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "tools")]
        for fn in filenames:
            if fn.endswith(".html"):
                html_files.append(os.path.join(dirpath, fn))

    total = broken = 0
    dot_html = 0
    problems = []
    for path in html_files:
        html = open(path, encoding="utf-8").read()
        page_dir = os.path.dirname(path)
        for raw in HREF_RE.findall(html):
            if raw.startswith(SKIP_PREFIX) or not raw.strip():
                continue
            target, _ = urldefrag(unquote(raw))
            if not target:
                continue
            total += 1
            if target.endswith(".html"):
                dot_html += 1
            if target.startswith("/"):
                site_path = target
            else:
                abs_p = os.path.normpath(os.path.join(page_dir, target))
                site_path = "/" + os.path.relpath(abs_p, ROOT).replace(os.sep, "/")
            if not resolve(site_path):
                broken += 1
                problems.append((os.path.relpath(path, ROOT), raw))

    # index.html は手書きで生成対象外のため、共通文言の変更から取り残されやすい。
    # フッターの広告表記がページ間でバラつくと景表法の観点でも良くないので検知する。
    notices = set()
    unresolved = []
    for path in html_files:
        html = open(path, encoding="utf-8").read()
        for m in re.findall(r"PR ／ 当サイトは[^<]*", html):
            notices.add(m)
        if "{pr_notice()}" in html:
            unresolved.append(os.path.relpath(path, ROOT))

    print(f"HTMLファイル       : {len(html_files)}")
    print(f"内部リンク         : {total}")
    print(f"リンク切れ         : {broken}")
    print(f".html付きの内部リンク: {dot_html}  ← 308リダイレクトになるので0が正")
    print(f"広告表記の種類      : {len(notices)}  ← 全ページ同一なので1が正")
    if len(notices) > 1:
        for n in sorted(notices):
            print(f"   ・{n}")
    if unresolved:
        print(f"未評価の埋め込み    : {len(unresolved)} ← f-string化されていないテンプレートがある")
        for f in unresolved[:5]:
            print(f"   × {f}")
    for f, r in problems[:40]:
        print(f"   × {f} → {r}")
    if len(problems) > 40:
        print(f"   … ほか {len(problems)-40} 件")
    return 1 if (broken or dot_html or unresolved or len(notices) > 1) else 0


if __name__ == "__main__":
    sys.exit(main())

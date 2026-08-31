# -*- coding: utf-8 -*-
"""内部リンクの .html を落として本番URLに合わせる（生成後の後処理）

Cloudflare Pages は `/x.html` を `/x` へ308でリダイレクトする。
リンクを .html のままにすると全内部リンクが1ホップ余計に踏み、
クロール予算を捨てるうえ体感速度も落ちる。

生成スクリプトは184箇所で .html 付きのリンクを書いているため、
個別に直すより生成物を一括で正規化するほうが安全で漏れがない。
実行は gen_* の後、gen_seo.py の前後どちらでもよい。

    cd ツール/saketto_repo && python tools/normalize_links.py
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# href/src の内部パスのみ対象。外部URL・アンカー・mailto は触らない。
LINK_RE = re.compile(r'(href=")(?!https?:|mailto:|tel:|#|javascript:)([^"]+?)\.html((?:#[^"]*)?)(")')

def normalize(html: str) -> tuple[str, int]:
    n = 0
    def sub(m):
        nonlocal n
        head, path, frag, tail = m.groups()
        # index.html はディレクトリURLへ（/guide/index.html → /guide/）
        if path.endswith("/index") or path == "index":
            new = path[: -len("index")] if path.endswith("/index") else "./"
        else:
            new = path
        n += 1
        return f"{head}{new}{frag}{tail}"
    return LINK_RE.sub(sub, html), n


def main():
    total_files = total_links = 0
    for dirpath, _dirs, files in os.walk(ROOT):
        if os.sep + "tools" in dirpath or os.sep + ".git" in dirpath:
            continue
        for f in files:
            if not f.endswith(".html"):
                continue
            p = os.path.join(dirpath, f)
            src = open(p, encoding="utf-8").read()
            out, n = normalize(src)
            if n:
                open(p, "w", encoding="utf-8").write(out)
                total_files += 1
                total_links += n
    print(f"内部リンクを正規化: {total_links}本 / {total_files}ファイル")


if __name__ == "__main__":
    main()

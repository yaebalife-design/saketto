# -*- coding: utf-8 -*-
"""同一内容のインラインCSSを外部ファイルへ切り出す（生成後の最終処理）。

213ページの合計10.3MBのうち5.06MBがインラインCSSだったが、中身は11種類
しかなく、同じ20KBを166ページが個別に持っていた。回遊するたびに同じCSSを
再ダウンロードしていたことになる。

同じ位置に <link> を差し込むので**適用順は変わらない**
（メディアクエリを前に置いて効かなくなった事故があるため、ここは崩さない）。
ファイル名は内容のハッシュにしてあるので、CSSを変えれば別URLになり、
/assets/* の長期キャッシュに引っかからない。

1ページでしか使わないブロックは、外に出してもリクエストが増えるだけなので
インラインのまま残す。

    cd ツール/saketto_repo && python tools/externalize_css.py
"""
import hashlib
import os
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_DIR = os.path.join(ROOT, "assets", "css")
STYLE_RE = re.compile(r"<style>(.*?)</style>", re.S)

# 何ページ以上で使われていたら外部化するか
MIN_PAGES = 3


def html_files():
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "tools")]
        for fn in filenames:
            if fn.endswith(".html"):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def sweep():
    """どのページからも <link> されていないCSSを消す。

    「今回externalizeした分」を基準に消してはいけない。一部のページだけ
    再生成した場合、まだリンクを持っている他ページのCSSまで巻き添えで
    消えてしまう。**最終HTMLの参照だけ**を根拠にする。
    """
    if not os.path.isdir(CSS_DIR):
        return 0
    referenced = set()
    ref_re = re.compile(r'href="/assets/css/([0-9a-f]+)\.css"')
    for path in html_files():
        referenced.update(ref_re.findall(open(path, encoding="utf-8").read()))
    removed = 0
    for fn in os.listdir(CSS_DIR):
        if fn.endswith(".css") and fn[:-4] not in referenced:
            os.remove(os.path.join(CSS_DIR, fn))
            print(f"   未参照のため削除: {fn}")
            removed += 1
    return removed


def main():
    files = html_files()

    # 1周目：どのブロックが何ページで使われているか数える
    usage = defaultdict(int)
    body = {}
    for path in files:
        html = open(path, encoding="utf-8").read()
        for block in set(STYLE_RE.findall(html)):
            key = hashlib.sha1(block.encode()).hexdigest()[:12]
            usage[key] += 1
            body[key] = block

    targets = {k for k, n in usage.items() if n >= MIN_PAGES}
    if not targets:
        print("外部化の対象なし（すでに全て外部化済み）")
        sweep()
        return 0

    os.makedirs(CSS_DIR, exist_ok=True)
    for key in targets:
        with open(os.path.join(CSS_DIR, f"{key}.css"), "w", encoding="utf-8") as f:
            f.write(body[key].strip() + "\n")

    # 2周目：対象ブロックを同じ位置の <link> に置き換える
    saved = 0
    touched = 0
    for path in files:
        html = open(path, encoding="utf-8").read()
        before = len(html.encode())

        def repl(m):
            key = hashlib.sha1(m.group(1).encode()).hexdigest()[:12]
            if key not in targets:
                return m.group(0)  # 単発のブロックはそのまま
            return f'<link rel="stylesheet" href="/assets/css/{key}.css">'

        new = STYLE_RE.sub(repl, html)
        if new != html:
            open(path, "w", encoding="utf-8").write(new)
            saved += before - len(new.encode())
            touched += 1

    kept = sorted(usage.items(), key=lambda x: -x[1])
    print(f"CSSブロック {len(usage)}種 / うち外部化 {len(targets)}種"
          f"（{MIN_PAGES}ページ以上で使用）")
    for k, n in kept:
        mark = "→ /assets/css/%s.css" % k if k in targets else "インラインのまま（単発）"
        print(f"   {n:4}ページ  {len(body[k])/1024:6.1f}KB  {mark}")
    removed = sweep()
    print(f"\n{touched}ファイルを書き換え、HTML合計 {saved/1024/1024:.2f}MB 削減")
    print(f"外部CSS {len(targets)}本 計 "
          f"{sum(len(body[k].encode()) for k in targets)/1024:.0f}KB"
          + (f"／未参照の古いCSS {removed}本を削除" if removed else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

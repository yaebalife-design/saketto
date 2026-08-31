# -*- coding: utf-8 -*-
"""ふるさと納税の返礼品URLが生きているか確認する。

返礼品は時期で入れ替わるため、一度確認したURLは黙って死ぬ。
2026/08/31 の点検では、稲とアガベの3URLが全て死んでいた
（楽天404 / チョイス404 / ふるなびは200を返すが本文は「見つかりませんでした」）。
死んだURLを残すと、読者を404へ送りながら「返礼品あり」と嘘をつくことになる。

**200が返ってもページが空振りのことがある**ので、本文の文言も見る。

    cd ツール/saketto_repo && python tools/check_furusato_urls.py
"""
import os
import re
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from furusato_data import FURUSATO, PORTAL_NAMES  # noqa: E402

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# 200を返しながら中身が無いページを見抜くための語（ソフト404対策）
SOFT_404 = [
    "見つかりませんでした", "ページが見つかり", "お探しのページ",
    "受付を終了", "終了しました", "存在しません", "掲載を終了",
]


def check(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", "ignore")
            code = r.status
    except urllib.error.HTTPError as e:
        return e.code, [], ""
    except Exception as e:
        return f"ERR({type(e).__name__})", [], str(e)[:60]
    title = re.search(r"<title[^>]*>(.*?)</title>", body, re.S)
    title = re.sub(r"\s+", " ", title.group(1)).strip()[:56] if title else ""
    return code, [w for w in SOFT_404 if w in body[:30000]], title


def main():
    ng = 0
    total = 0
    for slug, data in FURUSATO.items():
        for portal, url in (data.get("urls") or {}).items():
            total += 1
            code, soft, title = check(url)
            bad = code != 200 or soft
            ng += bool(bad)
            mark = "×" if bad else "○"
            print(f"{mark} {slug:16} {PORTAL_NAMES.get(portal, portal):14} {str(code):>5}  {title}")
            if soft:
                print(f"     ソフト404の疑い（本文に {soft[:2]}）: {url}")
            elif code != 200:
                print(f"     {url}")
    print(f"\n確認 {total} 件 / 問題あり {ng} 件")
    if ng:
        print("→ 死んでいるURLは furusato_data.py から外すか、現行の返礼品URLに差し替えること。")
    return 1 if ng else 0


if __name__ == "__main__":
    sys.exit(main())

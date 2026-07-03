# -*- coding: utf-8 -*-
"""saketto / サイト内検索の静的インデックス生成

index.html の検索ボックスが fetch する assets/search-index.json を生成する。
収録: 蔵25 + 全銘柄（名前・かな・蔵名・県・副原料で部分一致検索できる）。

実行: cd ツール/saketto_repo/tools && python gen_search_index.py
※ データを変えたら（銘柄追加等）これも再実行して JSON を更新すること。
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from breweries_master import BREWERIES
from breweries_brands import BRANDS

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "assets" / "search-index.json"


def main():
    entries = []
    for b in BREWERIES:
        slug = b["slug"]
        entries.append({
            "u": f"brewery/{slug}.html",
            "n": b["name"],
            "m": f"蔵 ／ {b['prefecture']}・{b['city']}",
            "t": " ".join(filter(None, [b["name"], b.get("name_kana", ""), slug,
                                         b["prefecture"], b["city"]])).lower(),
        })
        for i, br in enumerate(BRANDS.get(slug, [])):
            subs = [s for s in (br.get("sub_ingredients") or []) if s]
            meta = f"銘柄 ／ {b['name']}（{b['prefecture']}）"
            if subs:
                meta += "　／ " + "・".join(subs[:2])
            entries.append({
                "u": f"brand/{slug}-{i}.html",
                "n": br["name"],
                "m": meta,
                "t": " ".join(filter(None, [br["name"], br.get("kana", ""), b["name"],
                                             slug, b["prefecture"]] + subs)).lower(),
            })
    OUT.write_text(json.dumps(entries, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    print(f"OK search-index.json: {len(entries)}件 ({OUT.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main()

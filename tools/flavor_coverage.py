# -*- coding: utf-8 -*-
"""味わいグラフの「根拠がどれだけあるか」を測る。

グラフは出ていても、中身の軸が初期値(0.5)のまま張り付いていることがある。
図としては描けてしまうので、**見た目では区別できない**。
「特徴が無い」のではなく「情報が無い」だけなのに、平坦な図はそう見えるため、
どの軸がどれだけ埋まっているかを定期的に測れるようにしておく。

    cd ツール/saketto_repo && python tools/flavor_coverage.py
    python tools/flavor_coverage.py --list   # 足りない銘柄を列挙
"""
import collections
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gen_brand_pages_v2 as G  # noqa: E402
from breweries_brands import BRANDS  # noqa: E402
from breweries_master import BREWERIES  # noqa: E402

AXES = [("body", "濃淡", 0.5), ("sweet", "甘辛", 0.5),
        ("acid", "酸", 0.45), ("clarity", "にごり", 0.5)]


def scan():
    name_of = {b["slug"]: b["name"] for b in BREWERIES}
    rows = []
    for slug, brands in BRANDS.items():
        details = G.DETAILS.get(slug, [])
        for i, brand in enumerate(brands):
            d = details[i] if i < len(details) else {}
            s4, r6, tags = G.derive_flavor(d, brand)
            missing = [jp for key, jp, base in AXES
                       if abs(s4[key] - base) < 0.02]
            has_tasting = bool(d.get("tasting_nose") or d.get("tasting_palate")
                               or d.get("tasting_finish"))
            rows.append({
                "slug": slug, "idx": i, "brewery": name_of.get(slug, slug),
                "brand": brand["name"], "missing": missing,
                "flat6": len(set(r6.values())) == 1,
                "tags": len(tags), "tasting": has_tasting,
                "source": d.get("tasting_source_name"),
                "source_type": d.get("tasting_source_type"),
            })
    return rows


def main():
    rows = scan()
    n = len(rows)
    print(f"収録銘柄 {n}\n")

    print("軸ごとの根拠")
    for key, jp, base in AXES:
        miss = sum(1 for r in rows if jp in r["missing"])
        print(f"   {jp:6} 根拠あり {n - miss:3} / {n}  ({(n - miss) * 100 // n}%)")
    flat = sum(1 for r in rows if r["flat6"])
    print(f"   6軸レーダーが平坦（＝導出できていない）: {flat}")
    print(f"   味の印象タグが付く銘柄: {sum(1 for r in rows if r['tags'])}")
    print(f"   テイスティング記述を持つ銘柄: {sum(1 for r in rows if r['tasting'])}")

    print("\n出典の種類")
    st = collections.Counter(r["source_type"] or "（未分類）" for r in rows if r["source"])
    for k, v in st.most_common():
        print(f"   {v:3}  {k}")
    print(f"   {sum(1 for r in rows if not r['source']):3}  出典なし")

    weak = [r for r in rows if r["missing"]]
    print(f"\n根拠が足りない銘柄: {len(weak)}")
    c = collections.Counter(r["brewery"] for r in weak)
    for k, v in c.most_common(8):
        print(f"   {k[:22]:24} {v}")

    if "--list" in sys.argv:
        print("\n── 内訳 ──")
        for r in weak:
            print(f"   {r['slug']}-{r['idx']:<3} {r['brand'][:34]:36} "
                  f"{'/'.join(r['missing'])}")
    else:
        print("\n（--list で足りない銘柄を列挙）")
    return 0


if __name__ == "__main__":
    sys.exit(main())

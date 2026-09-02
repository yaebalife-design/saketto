# -*- coding: utf-8 -*-
"""公開前の内部リンク検証（拡張子なしURL前提）。

Cloudflare Pages は `/x.html` を `/x` へ 308 で飛ばすので、公開URLは拡張子なしに
正規化してある（normalize_links.py）。したがってリンク先の実ファイルは
`x` / `x.html` / `x/index.html` のいずれかで解決する必要がある。
この違いを見落として「2,410本リンク切れ」と誤報したことがあるため、
解決規則をツール側に固定した。

    cd ツール/saketto_repo && python tools/verify_links.py
"""
import json
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
        # f-string化されていないテンプレートから {S['breweries']} 等の
        # プレースホルダがそのまま本番HTMLに出た事故があった（2026/09/02）
        for ph in re.findall(r"\{[SB]\[[^\]]*\]\}", html):
            unresolved.append(f"{os.path.relpath(path, ROOT)}  {ph}")

    # 銘柄を足したとき affiliate_overrides.json への登録を忘れると、
    # **実在を確認していない銘柄に自動で楽天の検索リンクが出る**。
    # 買えない酒にボタンを出さない方針が黙って破れるので、ここで検知する。
    unregistered = []
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        from breweries_brands import BRANDS
        ov = json.load(open(os.path.join(ROOT, "tools", "affiliate_overrides.json"),
                            encoding="utf-8"))
        for slug, brands in BRANDS.items():
            for i, b in enumerate(brands):
                if f"{slug}:{i}" not in ov:
                    unregistered.append(f"{slug}:{i}  {b['name']}")
    except Exception as e:      # 点検ツールなので、ここで落ちて全体を止めない
        unregistered = [f"（確認できず: {e}）"]

    # index.html は手書きのため、DBの実数と数字がズレても気づけない
    # （2026/09/02 に「28蔵」見出しの直下で「25蔵」と表示していた）。実数と突合する。
    index_mismatch = []
    try:
        from breweries_master import BREWERIES
        import furusato_data
        idx_html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
        n_kura = len(BREWERIES)
        if f'{n_kura}<span class="bignum__suffix">蔵</span>' not in idx_html:
            index_mismatch.append(f"大数字が {n_kura}蔵 になっていない")
        li_count = len(re.findall(r'<li><a href="brewery/', idx_html))
        if li_count != n_kura:
            index_mismatch.append(f"ALL BREWERIES 一覧が {li_count}件（DBは{n_kura}蔵）")
        assoc = sum(1 for b in BREWERIES if b.get("association"))
        if f"協会加盟{assoc}社＋協会非加盟{n_kura - assoc}社" not in idx_html:
            index_mismatch.append(
                f"協会加盟の内訳が 加盟{assoc}社＋非加盟{n_kura - assoc}社 と一致しない")
        n_fur = len(furusato_data.all_confirmed_slugs())
        if f"{n_fur}蔵の返礼品を一次ソース確認済" not in idx_html:
            index_mismatch.append(f"ふるさと納税の蔵数が {n_fur}蔵 と一致しない")
    except Exception as e:
        index_mismatch = [f"（確認できず: {e}）"]

    print(f"HTMLファイル       : {len(html_files)}")
    print(f"内部リンク         : {total}")
    print(f"リンク切れ         : {broken}")
    print(f".html付きの内部リンク: {dot_html}  ← 308リダイレクトになるので0が正")
    print(f"広告表記の種類      : {len(notices)}  ← 全ページ同一なので1が正")
    print(f"アフィリ未登録の銘柄  : {len(unregistered)}  ← 未登録だと未確認のまま楽天検索リンクが出る")
    for u in unregistered[:10]:
        print(f"   × {u}")
    if len(notices) > 1:
        for n in sorted(notices):
            print(f"   ・{n}")
    if unresolved:
        print(f"未評価の埋め込み    : {len(unresolved)} ← f-string化されていないテンプレートがある")
        for f in unresolved[:5]:
            print(f"   × {f}")
    print(f"トップの数字のズレ   : {len(index_mismatch)}  ← 手書きindexとDB実数の突合")
    for m in index_mismatch:
        print(f"   × {m}")
    for f, r in problems[:40]:
        print(f"   × {f} → {r}")
    if len(problems) > 40:
        print(f"   … ほか {len(problems)-40} 件")
    return 1 if (broken or dot_html or unresolved or unregistered
                 or len(notices) > 1 or index_mismatch) else 0


if __name__ == "__main__":
    sys.exit(main())

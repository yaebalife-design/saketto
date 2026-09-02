# -*- coding: utf-8 -*-
"""A8.net「商品リンク（リンク先URL指定型）」のリンク生成ヘルパー（saketto版）。

A8管理画面の「商品リンクを作成」で1本作ると、こういうHTMLが出る:

    <a href="https://px.a8.net/svt/ejp?a8mat=XXXX+YYYY+ZZZZ+WWWW&a8ejpredirect={二重エンコード済URL}"
       rel="nofollow">ラベル</a>
    <img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=XXXX+YYYY+ZZZZ+WWWW" alt="">

a8mat は **プログラム × 掲載サイト** で固定。可変なのは a8ejpredirect の値だけなので、
a8mat さえ取れれば残りはここで組み立てられる。

🔴 GIN-DB の a8mat は流用できない。掲載サイトが違うと別IDになる。
   （au PAY の例: GIN-DB は 4BAITR+8V4EKI+54OC+BW8O2 / www19、
     saketto は 4BAITR+8V4G42+54OC+BW8O2 / www15）

エンコードの注意:
  a8ejpredirect の値は「対象URL全体をパーセントエンコードしたもの」。
  対象URL側のクエリに日本語（=既に%エンコード済み）が入ると、その % がさらに %25 になる。
  → quote(target_url, safe="") 一発で正しい二重エンコードになる。

規約メモ:
  - リンク先は「広告主URL」内に限る。他ドメインへ飛ばすと提携解除リスク。
  - href / img src は改変しない。rel に sponsored noopener を追加し target="_blank" を付ける。
"""
import re
from urllib.parse import quote

# ---------------------------------------------------------------- プログラム定義
# a8mat: A8管理画面「商品リンク」で1本作って得た値をそのまま貼る。
#        未提携／未取得のポータルは None のままにしておくとリンクを出力しない（安全側）。
#
# gif: インプレッション計測ピクセルのホスト。**プログラムごとに違う**。
#      A8管理画面が出した <img src> のホストをそのまま写すこと。
#      共通の定数にすると片方のピクセルが別ホストのまま送られ、成果が計上されない。
A8_PROGRAMS = {
    # au PAY ふるさと納税（2026-09-02 社長取得・saketto用）
    #   検索パラメータは search_word。name / keyword でも200が返るが検索が効かず
    #   全カタログが出るので使わない。
    "a": {
        "a8mat": "4BAITR+8V4G42+54OC+BW8O2",
        "gif": "www15",
        "label": "au PAY ふるさと納税で見る",
        "css": "aupay",
        "search": "https://furusato.wowma.jp/products/list.php?search_word={q}",
        "domain": "furusato.wowma.jp",
    },
    # ふるさとチョイス（2026-09-02 社長取得・saketto用）
    "c": {
        "a8mat": "4B3Y3C+3H14WI+4560+BW8O2",
        "gif": "www18",
        "label": "ふるさとチョイスで見る",
        "css": "choice",
        "search": "https://www.furusato-tax.jp/search?header_search=1&q={q}",
        "domain": "www.furusato-tax.jp",
    },
    # ふるさと本舗（a8mat 取得待ち・saketto用）
    "h": {
        "a8mat": None,
        "gif": "www13",
        "label": "ふるさと本舗で見る",
        "css": "honpo",
        "search": "https://furusatohonpo.jp/donate/s/?keyword={q}",
        "domain": "furusatohonpo.jp",
    },
    # さとふる（a8mat 取得待ち。GIN-DBでも未取得）
    "s": {
        "a8mat": None,
        "gif": "www14",
        "label": "さとふるで見る",
        "css": "satofull",
        "search": "https://www.satofull.jp/products/list.php?word={q}",
        "domain": "www.satofull.jp",
    },
    # ふるなび（A8には無い。バリューコマース経由なので、ここでは常に未設定）
    "f": {
        "a8mat": None,
        "gif": "www14",
        "label": "ふるなびで見る",
        "css": "furunavi",
        "search": "https://furunavi.jp/Search.aspx?keyword={q}",
        "domain": "furunavi.jp",
    },
    # ANAのふるさと納税（A8にプログラムがあるか未確認）
    "ANA": {
        "a8mat": None,
        "gif": "www14",
        "label": "ANAのふるさと納税で見る",
        "css": "ana",
        "search": "https://furusato.ana.co.jp/search/?keyword={q}",
        "domain": "furusato.ana.co.jp",
    },
    # 楽天ふるさと納税はA8ではなく「もしも」経由。moshimo_link.py が担当する
}

IMPRESSION_BASE = "https://{gif}.a8.net/0.gif?a8mat={a8mat}"
CLICK_BASE = "https://px.a8.net/svt/ejp?a8mat={a8mat}&a8ejpredirect={target}"

_PAREN = re.compile(r"[（(][^）)]*[）)]")


def search_keyword(brand_name):
    """表示用銘柄名 → ポータル検索に投げるキーワード。

    表示名には「（セット）」「ほか」等の説明が混ざっており、そのまま投げると0件になる。
    """
    kw = _PAREN.sub("", brand_name)
    kw = re.split(r"[／/]", kw)[0]
    kw = re.sub(r"\s*ほか\s*$", "", kw)
    return re.sub(r"\s+", " ", kw).strip()


def portal_search_url(portal, brand_name):
    """ポータル内の検索結果URL（＝広告主ドメイン内）を組み立てる。"""
    return A8_PROGRAMS[portal]["search"].format(
        q=quote(search_keyword(brand_name), safe=""))


def a8_href(a8mat, target_url):
    """A8クリック計測URL。target_url は広告主ドメイン内であること。"""
    return CLICK_BASE.format(a8mat=a8mat, target=quote(target_url, safe=""))


def a8_impression_src(portal):
    """計測ピクセルのURL。ホストはプログラムごとに違うので定義から引く。"""
    prog = A8_PROGRAMS[portal]
    return IMPRESSION_BASE.format(gif=prog.get("gif", "www14"), a8mat=prog["a8mat"])


def is_available(portal):
    """a8mat が入っているポータルだけ True（未提携ポータルのリンクを出さないため）。"""
    return bool(A8_PROGRAMS.get(portal, {}).get("a8mat"))


def portal_href(portal, target_url):
    """返礼品ページへのA8リンク。**未提携なら None を返す（生URLは返さない）。**

    🔴 社長指示（2026/09/02）：未提携ポータルへの生URLを出さないこと。
    以前はここで target_url をそのまま返していたため、ANA・ふるなびへ
    1円にもならない発リンクが15本出ていた。呼び出し側が None を受けて
    「リンクにしない」を選べるように、生URLへのフォールバックは持たせない。

    リンク先が広告主ドメイン外のときも None。A8は広告主URL外への遷移を
    禁じており、出すと提携解除のリスクがある。
    """
    if not is_available(portal):
        return None
    if not target_url.startswith("https://" + A8_PROGRAMS[portal]["domain"]):
        return None
    return a8_href(A8_PROGRAMS[portal]["a8mat"], target_url)


def portal_search_href(portal, keyword):
    """ポータル内の検索結果へのA8リンク。未提携なら None。"""
    if not is_available(portal):
        return None
    return a8_href(A8_PROGRAMS[portal]["a8mat"], portal_search_url(portal, keyword))


def render_impression_pixels(portals_used):
    """ページ末尾に置くA8計測ピクセル（プログラムごとに1個だけ）。

    1ページに同じピクセルを何十個も置くとインプレッション水増しに見えるため、
    カードごとではなくページ末尾でまとめて1個ずつ出す。
    """
    out = []
    for p in dict.fromkeys(portals_used):
        if is_available(p):
            out.append(f'<img border="0" width="1" height="1" '
                       f'src="{a8_impression_src(p)}" alt="">')
    return "".join(out)


if __name__ == "__main__":
    # 社長がA8管理画面で作った実物と、ここで組み立てたものが一致するか自己検証する。
    # エンコードが1文字でもずれると成果が計上されないので、必ず実物と突き合わせる。
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    ok = True

    # au PAY ふるさと納税（2026-09-02 社長取得の実物）
    expected = ("https://px.a8.net/svt/ejp?a8mat=4BAITR+8V4G42+54OC+BW8O2&a8ejpredirect="
                "https%3A%2F%2Ffurusato.wowma.jp%2Fproducts%2Fdetail.php%3Fproduct_id%3D1432697")
    got = a8_href(A8_PROGRAMS["a"]["a8mat"],
                  "https://furusato.wowma.jp/products/detail.php?product_id=1432697")
    print(f"[a] クリックURL  : {'一致' if got == expected else '不一致'}")
    if got != expected:
        print("   期待:", expected)
        print("   生成:", got)
    ok &= got == expected

    pix_expected = "https://www15.a8.net/0.gif?a8mat=4BAITR+8V4G42+54OC+BW8O2"
    pix_got = a8_impression_src("a")
    print(f"[a] 計測ピクセル : {'一致' if pix_got == pix_expected else '不一致'}")
    ok &= pix_got == pix_expected

    # ふるさとチョイス（2026-09-02 社長取得の実物）
    c_expected = ("https://px.a8.net/svt/ejp?a8mat=4B3Y3C+3H14WI+4560+BW8O2&a8ejpredirect="
                  "https%3A%2F%2Fwww.furusato-tax.jp%2Fproduct%2Fdetail%2F01215%2F7014505")
    c_got = a8_href(A8_PROGRAMS["c"]["a8mat"],
                    "https://www.furusato-tax.jp/product/detail/01215/7014505")
    print(f"[c] クリックURL  : {'一致' if c_got == c_expected else '不一致'}")
    if c_got != c_expected:
        print("   期待:", c_expected)
        print("   生成:", c_got)
    ok &= c_got == c_expected

    c_pix_expected = "https://www18.a8.net/0.gif?a8mat=4B3Y3C+3H14WI+4560+BW8O2"
    c_pix_got = a8_impression_src("c")
    print(f"[c] 計測ピクセル : {'一致' if c_pix_got == c_pix_expected else '不一致'}")
    ok &= c_pix_got == c_pix_expected

    print("\n" + ("すべて実物と一致" if ok else "🔴 実物と食い違う。貼る前に直すこと"))
    print("\n提携済み:", [p for p in A8_PROGRAMS if is_available(p)] or "なし")
    print("取得待ち:", [p for p in A8_PROGRAMS if not is_available(p)])

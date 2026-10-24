# -*- coding: utf-8 -*-
"""銘柄のボトル画像（saketto）。

実物の商品写真（蔵の公式ショップ／正規取扱店）を見本にして、Codex で saketto の撮影セット
（米色の和紙・淡い檜の板・窓からの自然光）に撮り直したイメージ。見本の写真そのものは載せない。
作業の道具と手順は ツール/_bottle_work/bottle_make.py（このリポジトリの外）。

ここに載せてよいのは、次を全部満たした物だけ（GIN-DB・南部鉄瓶-DB と同じ基準）:
  1. 見本と並べて、銘柄名・ロゴ・瓶の形・栓・ラベルの図柄と色が一致（私＋別Agentの独立照合）
  2. 瓶以外の物が描かれていない。細字の崩れはぼかし済み（大きい字はぼかしで逃げない）
  3. 見本がその銘柄の商品そのもの

作り直したらファイル名を変える（-v2）。/assets/images は長くキャッシュされるため。
SHOW_BOTTLE_PHOTOS = False にすれば、全ページ従来の副原料イメージに戻る。
"""
from pathlib import Path

SHOW_BOTTLE_PHOTOS = True
_DIR = Path(__file__).resolve().parent.parent / "assets" / "images" / "bottles"

# "slug:idx" → {"file": bottles/ 下のファイル名, "ref": 見本の出典ページ, "checked": 照合の記録}
BOTTLE_IMAGES = {
    "haccoba:0": {"file": "haccoba-0.webp", "ref": "https://haccoba.com/products/hanauta-hops23",
               "checked": "2026-10-24 私＋別Agentの照合で合格。細字 craft sake brewery 2か所ぼかし"},
    "lagoon:3": {"file": "lagoon-3.webp", "ref": "https://lagoonbrew.official.ec/items/90429657",
               "checked": "2026-10-24 私＋別Agentの照合で合格。翔空横の読み仮名をぼかし"},
    "lagoon:4": {"file": "lagoon-4.webp", "ref": "https://lagoonbrew.official.ec/items/89152947",
               "checked": "2026-10-24 私＋別Agentの照合で合格。翔空横の読み仮名をぼかし"},
    "lagoon:5": {"file": "lagoon-5.webp", "ref": "https://lagoonbrew.official.ec/items/69755182",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "lagoon:6": {"file": "lagoon-6.webp", "ref": "https://lagoonbrew.official.ec/items/126203987",
               "checked": "2026-10-24 私＋別Agentの照合で合格。2回目で合格（1回目は翔の字が崩れた）"},
    "heiwa-namba:0": {"file": "heiwa-namba-0.webp", "ref": "https://www.sake-kagiya.com/view/item/000000002222",
               "checked": "2026-10-24 私＋別Agentの照合で合格。見本の店の透かしの名残を黒帯で塗り直し（瓶『壱ノ濁』）"},
    "heiwa-namba:3": {"file": "heiwa-namba-3.webp", "ref": "https://shopping.kimijimaya.co.jp/view/item/000000006586",
               "checked": "2026-10-24 私＋別Agentの照合で合格。キャップの印字をぼかし（瓶『参ノ濁』）"},
    "heiwa-namba:4": {"file": "heiwa-namba-4.webp", "ref": "https://shopping.kimijimaya.co.jp/view/item/000000006585",
               "checked": "2026-10-24 私＋別Agentの照合で合格。キャップの印字をぼかし（瓶『弐ノ濁』）"},
    "dejima-hosendo:0": {"file": "dejima-hosendo-0.webp", "ref": "https://filament-jp.net/sake/dejima-hosendo/hosen_kumo/hosen_kumo_1st.html",
               "checked": "2026-10-24 私＋別Agentの照合で合格。でじま芳扇堂の縦書き・読み仮名をぼかし"},
    "dejima-hosendo:2": {"file": "dejima-hosendo-2.webp", "ref": "https://shop.djm-hosendo.co.jp/products/detail/119",
               "checked": "2026-10-24 私＋別Agentの照合で合格。読み仮名をぼかし"},
    "dejima-hosendo:4": {"file": "dejima-hosendo-4.webp", "ref": "https://shop.djm-hosendo.co.jp/products/detail/138",
               "checked": "2026-10-24 私＋別Agentの照合で合格。首札の細字・縦書き・読み仮名をぼかし"},
    "dejima-hosendo:5": {"file": "dejima-hosendo-5.webp", "ref": "https://filament-jp.net/sake/dejima-hosendo/hosen_nami/hosen_nami_1st.html",
               "checked": "2026-10-24 私＋別Agentの照合で合格。縦書き・読み仮名をぼかし"},
    "dejima-hosendo:6": {"file": "dejima-hosendo-6.webp", "ref": "https://shop.djm-hosendo.co.jp/products/detail/23",
               "checked": "2026-10-24 私＋別Agentの照合で合格。縦書き・読み仮名をぼかし"},
    "dejima-hosendo:7": {"file": "dejima-hosendo-7.webp", "ref": "https://shop.djm-hosendo.co.jp/products/detail/146",
               "checked": "2026-10-24 私＋別Agentの照合で合格。縦書き・読み仮名をぼかし"},
    "linne:0": {"file": "linne-0.webp", "ref": "https://jp.sake-times.com/special/press/p_202512_linne-800oomugi-tenpai",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "nomu:0": {"file": "nomu-0.webp", "ref": "https://furusato.ana.co.jp/donation/g/g47211-BCES007/",
               "checked": "2026-10-24 私＋別Agentの照合で合格。見本のグラスは除去。シシカムの細字をぼかし"},
    "salmon-brewery:0": {"file": "salmon-brewery-0.webp", "ref": "https://sakeworld.jp/special/2506sakeshuzou/",
               "checked": "2026-10-24 私＋別Agentの照合で合格。見本は寝かせた瓶。細字の列・下の2行をぼかし"},
    "iyasaka:0": {"file": "iyasaka-0.webp", "ref": "https://note.com/ikko2535/n/n1c7b3b38e1e9",
               "checked": "2026-10-24 私＋別Agentの照合で合格。2回目で合格（1回目は十割麹酒が崩れた）。キャップ周り・側面の細字をぼかし。見本は弥栄醸造代表のnote（Vol.0）"},
    "dejima-hosendo:8": {"file": "dejima-hosendo-8.webp", "ref": "https://shop.djm-hosendo.co.jp/products/detail/147",
               "checked": "2026-10-24 私＋別Agentの照合で合格。首札の細字・縦書き・読み仮名をぼかし"},
    "dejima-hosendo:10": {"file": "dejima-hosendo-10.webp", "ref": "https://shop.djm-hosendo.co.jp/products/detail/162",
               "checked": "2026-10-24 私＋別Agentの照合で合格。縦書き・読み仮名をぼかし"},
    "dejima-hosendo:11": {"file": "dejima-hosendo-11.webp", "ref": "https://shop.djm-hosendo.co.jp/products/detail/148",
               "checked": "2026-10-24 私＋別Agentの照合で合格。首札の細字・縦書き・読み仮名をぼかし"},
    "dejima-hosendo:12": {"file": "dejima-hosendo-12.webp", "ref": "https://shop.djm-hosendo.co.jp/products/detail/168",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "cultiva:0": {"file": "cultiva-0.webp", "ref": "https://cultiva-sake.com/item/sankeinishiki-nagano-2025by/",
               "checked": "2026-10-24 私＋別Agentの照合で合格。見本のグラスは除去。細字の数字をぼかし（見本は sankeinishiki40 の画像）"},
    "cultiva:1": {"file": "cultiva-1.webp", "ref": "https://cultiva-sake.com/item/hinohikari-fukuoka-2025by/",
               "checked": "2026-10-24 私＋別Agentの照合で合格。手書き数字をぼかし"},
    "cultiva:2": {"file": "cultiva-2.webp", "ref": "https://cultiva-sake.com/item/yamadanishiki-fukuoka-2025by/",
               "checked": "2026-10-24 私＋別Agentの照合で合格。見本に無い清酒の印をぼかし"},
    "ine-to-agave:3": {"file": "ine-to-agave-3.webp", "ref": "https://jizake-mie.jp/SHOP/ineto-hachimitsu-500.html",
               "checked": "2026-10-24 私＋別Agentの照合で合格。副題・年度・蔵名の細字をぼかし"},
    "haccoba:1": {"file": "haccoba-1.webp", "ref": "https://note.com/haccoba/n/nd49720845bcb",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "haccoba:2": {"file": "haccoba-2.webp", "ref": "https://prtimes.jp/main/html/rd/p/000000055.000061904.html",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "haccoba:3": {"file": "haccoba-3.webp", "ref": "https://note.com/haccoba/n/na8cdb7d00ec6",
               "checked": "2026-10-24 私＋別Agentの照合で合格。丸の中の細字をぼかし"},
    "ine-to-agave:10": {"file": "ine-to-agave-10.webp", "ref": "https://note.com/inetoagave/n/nb39d090f75df",
               "checked": "2026-10-24 私＋別Agentの照合で合格。見本にない英字・蔵名の細字をぼかし"},
    "lagoon:7": {"file": "lagoon-7.webp", "ref": "https://lagoonbrew.official.ec/items/90929808",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "lagoon:9": {"file": "lagoon-9.webp", "ref": "https://lagoonbrew.official.ec/items/110049726",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "lagoon:11": {"file": "lagoon-11.webp", "ref": "https://lagoonbrew.official.ec/items/78443967",
               "checked": "2026-10-24 私＋別Agentの照合で合格。翔空横の読み仮名をぼかし"},
    "happy-taro:10": {"file": "happy-taro-10.webp", "ref": "https://happytaro.jp/doburoku/seasonal/ichigo/",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "happy-taro:11": {"file": "happy-taro-11.webp", "ref": "https://happytaro.jp/doburoku/seasonal/marou/",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "nondo:8": {"file": "nondo-8.webp", "ref": "https://reika-sake.com/products/03ndd13906331",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし（PETボトル）"},
    "dejima-hosendo:9": {"file": "dejima-hosendo-9.webp", "ref": "https://shop.djm-hosendo.co.jp/products/detail/111",
               "checked": "2026-10-24 私＋別Agentの照合で合格。2回目で合格（1回目は首の封が違った）。縦書き・読み仮名をぼかし"},
}


# ふるさと納税の返礼品名と DB の銘柄名が表記違いのもの（同じ商品であることを見本の出典で確認済み）
#   nomu:0 シシカム … 見本写真の出典が ANA のふるさと納税「SHISHIKAMU 720ml×6本」のページそのもの
FURUSATO_ALIASES = {"nomu:0": ["SHISHIKAMU"]}


def thumb_tag(slug, idx, rel="../", cls="entry__thumb"):
    """一覧の行に置く縦長サムネイル。画像の無い銘柄は同じ大きさの線画の枠（CSS側で描く）。"""
    f = bottle_file(slug, idx)
    if f and not (_DIR / "t" / f).exists():
        f = None  # サムネイルを作り忘れた銘柄で壊れた画像を出さない
    if f:
        return (f'<span class="{cls}"><img src="{rel}assets/images/bottles/t/{f}" alt="" '
                f'width="168" height="360" loading="lazy" decoding="async"></span>')
    return f'<span class="{cls} {cls}--none" aria-hidden="true"></span>'


def bottle_file(slug, idx):
    """掲載してよいボトル画像のファイル名（無ければ None）。"""
    if not SHOW_BOTTLE_PHOTOS:
        return None
    e = BOTTLE_IMAGES.get(f"{slug}:{idx}")
    if not e or not (_DIR / e["file"]).exists():
        return None
    return e["file"]

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
    "happy-taro:3": {"file": "happy-taro-3.webp", "ref": "https://happytaro.jp/doburoku/lineup/ukiuki/",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "happy-taro:4": {"file": "happy-taro-4.webp", "ref": "https://happytaro.jp/doburoku/seasonal/hassaku/",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "happy-taro:6": {"file": "happy-taro-6.webp", "ref": "https://happytaro.jp/doburoku/seasonal/kuromoji/",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "heiroku:0": {"file": "heiroku-0.webp", "ref": "https://www.fukuraiya.jp/SHOP/hiraro00008.html",
               "checked": "2026-10-24 私＋別Agentの照合で合格。見本は製品CG＋実物ラベル接写。蔵名の細字をぼかし"},
    "heiroku:1": {"file": "heiroku-1.webp", "ref": "https://eshop.wakamatsuyasaketen.com/view/item/000000001317",
               "checked": "2026-10-24 私＋別Agentの照合で合格。縦書きの詩の細字をぼかし"},
    "heiroku:4": {"file": "heiroku-4.webp", "ref": "https://eshop.wakamatsuyasaketen.com/view/item/000000001140",
               "checked": "2026-10-24 私＋別Agentの照合で合格。蔵名・詩の細字をぼかし"},
    "heiroku:5": {"file": "heiroku-5.webp", "ref": "https://eshop.wakamatsuyasaketen.com/view/item/000000001208",
               "checked": "2026-10-24 私＋別Agentの照合で合格。蔵名・詩の細字をぼかし"},
    "pukupuku:0": {"file": "pukupuku-0.webp", "ref": "https://sake-wadaya.com/18165/",
               "checked": "2026-10-24 私＋別Agentの照合で合格。首札のかなをぼかし（5本並びの写真から1本を切り出して見本に）"},
    "pukupuku:6": {"file": "pukupuku-6.webp", "ref": "https://shop.hamadaya-saketen.com/items/138064784",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "hakutsuru-sakecraft:0": {"file": "hakutsuru-sakecraft-0.webp", "ref": "https://www.hakutsuru.co.jp/corporate/news/detail/20240927120955.html",
               "checked": "2026-10-24 私＋別Agentの照合で合格。首札の細字をぼかし"},
    "hakutsuru-sakecraft:2": {"file": "hakutsuru-sakecraft-2.webp", "ref": "https://www.hakutsuru.co.jp/corporate/news/detail/20241217151344.html",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "hakutsuru-sakecraft:3": {"file": "hakutsuru-sakecraft-3.webp", "ref": "https://www.hakutsuru.co.jp/corporate/news/detail/20250114160850.html",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "hakutsuru-sakecraft:6": {"file": "hakutsuru-sakecraft-6.webp", "ref": "https://www.hakutsuru.co.jp/corporate/news/detail/20250408105856.html",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "hakutsuru-sakecraft:7": {"file": "hakutsuru-sakecraft-7.webp", "ref": "https://prtimes.jp/main/html/rd/p/000000411.000013868.html",
               "checked": "2026-10-24 私＋別Agentの照合で合格。首札の細字をぼかし"},
    "heiwa-kabutocho:0": {"file": "heiwa-kabutocho-0.webp", "ref": "https://www.sake-kagiya.com/view/item/000000002222",
               "checked": "2026-10-24 難波 heiwa-namba:0 と同じ瓶詰め商品（瓶『壱ノ濁』。DB定義で一致）の合格画像を使用。兜町の見本から作った版は透かしの名残と字の崩れで不合格"},
    "heiwa-kabutocho:3": {"file": "heiwa-kabutocho-3.webp", "ref": "https://shopping.kimijimaya.co.jp/view/item/000000006586",
               "checked": "2026-10-24 難波 heiwa-namba:3 と同じ瓶詰め商品（瓶『参ノ濁』。DB定義で一致）の合格画像を使用。兜町の見本から作った版は透かしの名残と字の崩れで不合格"},
    "lagoon:8": {"file": "lagoon-8.webp", "ref": "https://lagoonbrew.official.ec/items/74756117",
               "checked": "2026-10-24 私＋別Agentの照合で合格。2回目で合格（1回目は翔の字が崩れた）"},
    "librom:0": {"file": "librom-0.webp", "ref": "https://librom.jp/collections/all/products/librom-moscowmule",
               "checked": "2026-10-24 私＋別Agentの照合で合格。首札・サブロゴの細字をぼかし"},
    "librom:2": {"file": "librom-2.webp", "ref": "https://librom.jp/collections/all/products/tomax2026",
               "checked": "2026-10-24 私＋別Agentの照合で合格。首札の細字をぼかし"},
    "librom:3": {"file": "librom-3.webp", "ref": "https://librom.jp/collections/all/products/amaouno-osake",
               "checked": "2026-10-24 私＋別Agentの照合で合格。首札の細字をぼかし"},
    "librom:4": {"file": "librom-4.webp", "ref": "https://librom.jp/products/frerom",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "librom:5": {"file": "librom-5.webp", "ref": "https://librom.jp/products/sour-cola",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "sakenova:0": {"file": "sakenova-0.webp", "ref": "https://sakenovabrewery.jp/products/brewnote001",
               "checked": "2026-10-24 私＋別Agentの照合で合格。見本は公式の製品CG。修正なし"},
    "sakenova:1": {"file": "sakenova-1.webp", "ref": "https://sakenovabrewery.jp/products/bn002",
               "checked": "2026-10-24 私＋別Agentの照合で合格。見本は公式の製品CG。修正なし"},
    "sakenova:2": {"file": "sakenova-2.webp", "ref": "https://sakenovabrewery.jp/products/bn006",
               "checked": "2026-10-24 私＋別Agentの照合で合格。見本は公式の製品CG。修正なし"},
    "nomu:1": {"file": "nomu-1.webp", "ref": "https://nomu.okinawa/products/offzake-plain-set",
               "checked": "2026-10-24 私＋別Agentの照合で合格。パウチ。修正なし"},
    "nomu:3": {"file": "nomu-3.webp", "ref": "https://nomu.okinawa/products/タベル",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "ine-to-agave:1": {"file": "ine-to-agave-1.webp", "ref": "https://store.sakestreet.com/products/craft-inetohop-hanakaze-gururiko-2024by",
               "checked": "2026-10-24 私＋別Agentの照合で合格。蔵名・読み仮名の細字をぼかし"},
    "ine-to-agave:4": {"file": "ine-to-agave-4.webp", "ref": "https://shop.inetoagave.com/products/稲とリンゴ",
               "checked": "2026-10-24 私＋別Agentの照合で合格。年度表記（R05BY）の崩れと蔵ロゴ上段をぼかし。見本は2023年版"},
    "ine-to-agave:5": {"file": "ine-to-agave-5.webp", "ref": "https://shop.inetoagave.com/products/稲とブドウ",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし。見本は2022年版（DB名に年度なし）"},
    "happy-taro:2": {"file": "happy-taro-2.webp", "ref": "https://imadeya.co.jp/products/8211157581989",
               "checked": "2026-10-24 私＋別Agentの照合で合格。首札のかなをぼかし"},
    "heiroku:3": {"file": "heiroku-3.webp", "ref": "https://store.sakestreet.com/products/layer-pear",
               "checked": "2026-10-24 私＋別Agentの照合で合格。蔵名の細字をぼかし"},
    "pukupuku:1": {"file": "pukupuku-1.webp", "ref": "https://imadeya.co.jp/products/15034492092782",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "pukupuku:3": {"file": "pukupuku-3.webp", "ref": "https://imadeya.co.jp/products/14746740031854",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "fermenteria:3": {"file": "fermenteria-3.webp", "ref": "https://fermenteria.co/products/kabosette_chocolat",
               "checked": "2026-10-24 私＋別Agentの照合で合格。2回目で合格（1回目は副題の綴りが崩れた）。蔵名の細字をぼかし"},
    "fermenteria:5": {"file": "fermenteria-5.webp", "ref": "https://fermenteria.co/products/yeastology-01-novalager",
               "checked": "2026-10-24 私＋別Agentの照合で合格。細字のカナをぼかし"},
    "fermenteria:6": {"file": "fermenteria-6.webp", "ref": "https://fermenteria.co/products/yeastology-02-phillysour",
               "checked": "2026-10-24 私＋別Agentの照合で合格。細字のカナをぼかし"},
    "fermenteria:7": {"file": "fermenteria-7.webp", "ref": "https://fermenteria.co/products/citrene-japan-yuzu-sansho",
               "checked": "2026-10-24 私＋別Agentの照合で合格。細字のカナをぼかし"},
    "fermenteria:8": {"file": "fermenteria-8.webp", "ref": "https://fermenteria.co/products/citrene-taiwan-lime-maqaw",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "amanosato:4": {"file": "amanosato-4.webp", "ref": "https://shop.amanosato-sake.com/products/flagship-jyo",
               "checked": "2026-10-24 私＋別Agentの照合で合格。縦書き英字・キャップの注意書きをぼかし（見本は化粧箱を除いて切り出し）"},
    "amanosato:5": {"file": "amanosato-5.webp", "ref": "https://shop.amanosato-sake.com/products/flagship_2nd",
               "checked": "2026-10-24 私＋別Agentの照合で合格。縦書き英字・キャップの注意書きをぼかし"},
    "amanosato:6": {"file": "amanosato-6.webp", "ref": "https://shop.amanosato-sake.com/products/koharu_premium-500ml",
               "checked": "2026-10-24 私＋別Agentの照合で合格。縦書き英字・キャップの印字をぼかし（見本はバナーから瓶のみ切り出し）"},
    "pukupuku:5": {"file": "pukupuku-5.webp", "ref": "https://imadeya.co.jp/products/14791733444974",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし（見本は化粧箱を除いて切り出し）"},
    "nondo:1": {"file": "nondo-1.webp", "ref": "https://nondo-tono.life/products/権化シリーズ-rafters",
               "checked": "2026-10-24 私＋別Agentの照合で合格。修正なし"},
    "nondo:3": {"file": "nondo-3.webp", "ref": "https://nondo-tono.life/products/権化シリーズ-2",
               "checked": "2026-10-24 私＋別Agentの照合で合格。見本は斜め置き・グラス一部。修正なし"},
    "hakutsuru-sakecraft:8": {"file": "hakutsuru-sakecraft-8.webp", "ref": "https://www.e-hakutsuru.com/products/19445",
               "checked": "2026-10-24 私＋別Agentの照合で合格。首札の細字をぼかし（見本は木箱を除いて切り出し）"},
    "ine-to-agave:9": {"file": "ine-to-agave-9.webp", "ref": "https://shop.inetoagave.com/products/%E4%BA%A4%E9%85%92%E8%8A%B1%E9%A2%A8-6%E5%8F%B7%E9%85%B5%E6%AF%8D",
               "checked": "2026-10-24 私＋別Agentの照合で合格。首の曲線状の細字・社印をぼかし"},
    "ine-to-agave:12": {"file": "ine-to-agave-12.webp", "ref": "https://shop.inetoagave.com/products/doburoku-%E3%83%9B%E3%83%83%E3%83%97",
               "checked": "2026-10-24 私＋別Agentの照合で合格。年度表記（R05BY）の崩れをぼかし"},
    "ine-to-agave:7": {"file": "ine-to-agave-7.webp", "ref": "https://shop.inetoagave.com/products/%E7%A8%B2%E3%81%A8%E3%83%96%E3%83%89%E3%82%A6-special-edition-2024",
               "checked": "2026-10-24 私＋別Agentの照合で合格。年度表記・蔵名の細字をぼかし（見本は化粧箱を除いて切り出し）"},
    "nondo:2": {"file": "nondo-2.webp", "ref": "https://nondo-tono.life/products/権化シリーズ-4",
               "checked": "2026-10-24 私＋別Agentの照合で合格。2回目で合格（1回目は瓶とラベルが別物になった）。見本は斜め置き"},
    "ine-to-agave:11": {"file": "ine-to-agave-11.webp", "ref": "https://shop.inetoagave.com/products/%E5%BB%BB",
               "checked": "2026-10-24 私＋別Agentの照合で合格。2回目で合格（1回目はラベルが別物）。OGA City表記とキャップの細字をぼかし"},
    "fermenteria:4": {"file": "fermenteria-4.webp", "ref": "https://fermenteria.co/products/sparkling",
               "checked": "2026-10-24 私＋別Agentの照合で合格。2回目で合格（1回目は見出しの漢字が崩れた）。下部の細字をぼかし"},
    "dejima-hosendo:3": {"file": "dejima-hosendo-3.webp", "ref": "https://store.shopping.yahoo.co.jp/hirogaru-saketen/hosendo25.html",
               "checked": "2026-10-24 私＋別Agentの照合で合格（取扱店の写真が見本）。縦書き細字とふりがなをぼかし"},
    "heiroku:2": {"file": "heiroku-2.webp", "ref": "https://item.rakuten.co.jp/mizusato/40304202_hiraroku9/",
               "checked": "2026-10-24 私＋別Agentの照合で合格（取扱店の写真が見本）。rigin・下部ロゴと細字をぼかし"},
    "ine-to-agave:0": {"file": "ine-to-agave-0.webp", "ref": "https://store.shopping.yahoo.co.jp/izumise/018447.html",
               "checked": "2026-10-24 私＋別Agentの照合で合格（取扱店の写真が見本）。下部ロゴ・首とキャップの細字をぼかし"},
    "ine-to-agave:8": {"file": "ine-to-agave-8.webp", "ref": "https://item.rakuten.co.jp/auc-chitashige/36022309/",
               "checked": "2026-10-24 私＋別Agentの照合で合格（取扱店の写真が見本）。肩ラベル下の英字・小印をぼかし"},
    "ine-to-agave:15": {"file": "ine-to-agave-15.webp", "ref": "https://item.rakuten.co.jp/auc-horie/inetoagave66/",
               "checked": "2026-10-24 私＋別Agentの照合で合格（取扱店の写真が見本）。2回目で合格（1回目は谷泉が崩れた）。下部ロゴとR6BYをぼかし"},
    "konohanano:3": {"file": "konohanano-3.webp", "ref": "https://item.rakuten.co.jp/sekkodo/evan-garde_01/",
               "checked": "2026-10-24 私＋別Agentの照合で合格（取扱店の写真が見本）。ラベル右端の縦書き細字をぼかし"},
    "happy-taro:12": {"file": "happy-taro-12.webp", "ref": "https://store.shopping.yahoo.co.jp/jizake-mie/happy-akajiso-480.html",
               "checked": "2026-10-24 私＋別Agentの照合で合格（取扱店の写真が見本）。手書きsisoと小さな点列をぼかし"},
    "lagoon:0": {"file": "lagoon-0.webp", "ref": "https://item.rakuten.co.jp/kishimoto/syoukuu-029/",
               "checked": "2026-10-24 私＋別Agentの照合で合格（取扱店の写真＋公式写真のラベル部分が見本）。2回目で合格（1回目は翔空の空が崩れた）"},
    "ine-to-agave:14": {"file": "ine-to-agave-14.webp", "ref": "https://item.rakuten.co.jp/izumise/020412/",
               "checked": "2026-10-24 私＋別Agentの照合で合格（取扱店の写真が見本）。3回目で合格（ロゴINE to AGAVEが崩れた）。首とキャップの細字をぼかし"},
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

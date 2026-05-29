# -*- coding: utf-8 -*-
"""saketto / 銘柄データ (一次ソース確認版・2026-05-30)

- abv は度数(%), volume_ml は容量(ml)。公式非開示は None
- price は税込・参考価格(円)。"市場実勢" or 公式非開示は None で note に補記
- sub_ingredients は副原料リスト (米麹のみは ["米のみ"])
"""

BRANDS = {

    # ── 協会加盟9社（詳細データあり） ──
    "ine-to-agave": [
        {"name": "稲とアガベ CRAFT series", "abv": 14, "volume_ml": 500,
         "sub_ingredients": ["アガベシロップ"], "price": 2525,
         "note": "ブランドの代名詞。白ブドウや白桃を思わせる柔らかな香り"},
        {"name": "花風（ぐるりこ®）", "abv": 14, "volume_ml": 720,
         "sub_ingredients": ["ホップ"], "price": 2775,
         "note": "西洋唐花草（ホップ）を副原料に使用"},
        {"name": "稲とジャスミン", "abv": None, "volume_ml": 500,
         "sub_ingredients": ["ジャスミン茶葉"], "price": 3099,
         "note": "茶葉を副原料に。度数公式非開示"},
        {"name": "稲とハチミツ", "abv": None, "volume_ml": 500,
         "sub_ingredients": ["ハチミツ"], "price": 3319,
         "note": "ハチミツ副原料。度数公式非開示"},
        {"name": "稲とリンゴ SPECIAL EDITION", "abv": None, "volume_ml": 720,
         "sub_ingredients": ["リンゴ"], "price": 7175, "note": "特別版"},
        {"name": "稲とブドウ SPECIAL EDITION", "abv": None, "volume_ml": 720,
         "sub_ingredients": ["ブドウ"], "price": 7175, "note": "特別版"},
    ],

    "haccoba": [
        {"name": "はなうたホップス", "abv": 13, "volume_ml": 500,
         "sub_ingredients": ["ホップ"], "price": 2420,
         "note": "看板銘柄。「花酛」とクラフトビールのドライホッピングを融合"},
        {"name": "hanamoto bretta [kriek]", "abv": None, "volume_ml": 720,
         "sub_ingredients": ["花酛", "ベルギービール製法"], "price": 2640,
         "note": "「花酛」とベルギービール製法の融合"},
        {"name": "zairai [森 forest]", "abv": None, "volume_ml": 720,
         "sub_ingredients": ["地元在来植物"], "price": 2420,
         "note": "在来植物による地酒表現"},
        {"name": "kasu [sansho lemonade]", "abv": None, "volume_ml": 720,
         "sub_ingredients": ["山椒", "レモネード"], "price": 2420,
         "note": "未利用資源によるアップサイクル"},
        {"name": "水を編む", "abv": None, "volume_ml": None,
         "sub_ingredients": [], "price": None,
         "note": "ドブロク製法「花酛」の復刻版"},
    ],

    "lagoon": [
        {"name": "翔空 HOP SAKE ほっぺ", "abv": 15, "volume_ml": 720,
         "sub_ingredients": ["ホップ（シトラ）"], "price": 2420,
         "note": "看板銘柄。柑橘香と爽快さを兼備"},
        {"name": "翔空 ニゴリのHOP SAKE ほっぺ", "abv": 15.5, "volume_ml": 720,
         "sub_ingredients": ["ホップ（シトラ）"], "price": 2420,
         "note": "ニゴリ仕様、約100本限定"},
        {"name": "翔空 酔いどれ洋梨2025-2026 槽搾り生", "abv": 13, "volume_ml": 500,
         "sub_ingredients": ["ル・レクチェ（洋梨）"], "price": 2420,
         "note": "新潟ブランド洋梨×純米香"},
        {"name": "翔空 酔いどれメロン2025 ドブロク", "abv": 12, "volume_ml": 500,
         "sub_ingredients": ["マスクメロン"], "price": 2310,
         "note": "千葉産高級メロン使用"},
        {"name": "翔空 酔いどれイチゴ2025 槽絞り生", "abv": 14, "volume_ml": 500,
         "sub_ingredients": ["越後姫（イチゴ）"], "price": 2310,
         "note": "新潟産イチゴ約200kg使用"},
        {"name": "翔空 SAKEマルゲリータ Unpressed", "abv": 14, "volume_ml": 500,
         "sub_ingredients": ["トマト", "バジル"], "price": 1980,
         "note": "ピザマルゲリータをイメージしたドブロク"},
        {"name": "翔空 自然栽培亀の尾どぶろく", "abv": 17, "volume_ml": 500,
         "sub_ingredients": ["米のみ"], "price": 2100,
         "note": "幻の米「亀ノ尾」100%使用、192本限定"},
    ],

    "librom": [
        {"name": "LIBROMモスコミュール", "abv": None, "volume_ml": None,
         "sub_ingredients": [], "price": 2860, "note": "度数・容量・副原料公式非開示"},
        {"name": "博多美人", "abv": None, "volume_ml": None,
         "sub_ingredients": [], "price": 2860, "note": "度数・容量・副原料公式非開示"},
        {"name": "TOMATO", "abv": None, "volume_ml": None,
         "sub_ingredients": ["トマト"], "price": 2860,
         "note": "度数・容量公式非開示"},
        {"name": "あまおうのおさけ", "abv": None, "volume_ml": None,
         "sub_ingredients": ["あまおう（福岡県産いちご）"], "price": 2750,
         "note": "福岡県産素材×クラフトサケ"},
        {"name": "FREROM Hallertau Blanc", "abv": None, "volume_ml": None,
         "sub_ingredients": ["ホップ（Hallertau Blanc）"], "price": 2860,
         "note": "度数・容量公式非開示"},
        {"name": "サワーコーラ", "abv": None, "volume_ml": None,
         "sub_ingredients": [], "price": 3300, "note": "副原料公式非開示"},
    ],

    "konohanano": [
        {"name": "ハナグモリ", "abv": 13, "volume_ml": 500,
         "sub_ingredients": ["米のみ"], "price": 1980,
         "note": "看板銘柄。本格純米にごり酒、シュワッとガス感"},
        {"name": "ハナグモリ THE酸", "abv": None, "volume_ml": 500,
         "sub_ingredients": [], "price": None,
         "note": "酸味を強調した派生銘柄"},
        {"name": "ハナグモリ 焼酎用白麹仕様", "abv": None, "volume_ml": None,
         "sub_ingredients": ["焼酎用白麹"], "price": None,
         "note": "バリエーション銘柄"},
    ],

    "happy-taro": [
        {"name": "ハッピーどぶろく 穂の恵み", "abv": None, "volume_ml": 480,
         "sub_ingredients": ["米のみ（穂の恵み米）"], "price": 1870,
         "note": "定番どぶろく"},
        {"name": "ハッピーどぶろく 生もと 酵母無添加", "abv": None, "volume_ml": 480,
         "sub_ingredients": ["米のみ"], "price": 2310,
         "note": "生もと造り、酵母無添加"},
        {"name": "ハッピーどぶろく ホップ Huell Melon", "abv": None, "volume_ml": 480,
         "sub_ingredients": ["ホップ（Huell Melon）"], "price": 2310, "note": ""},
        {"name": "something happy うきうきホップ", "abv": None, "volume_ml": 480,
         "sub_ingredients": ["ホップ"], "price": 2530, "note": ""},
        {"name": "something happy 菅浦の八朔", "abv": None, "volume_ml": 480,
         "sub_ingredients": ["八朔"], "price": 2970, "note": ""},
        {"name": "something happy 政所と共に", "abv": None, "volume_ml": 480,
         "sub_ingredients": ["茶葉（政所茶）"], "price": 2530, "note": ""},
        {"name": "something happy 音羽の黒文字", "abv": None, "volume_ml": 480,
         "sub_ingredients": ["黒文字"], "price": 2970, "note": ""},
    ],

    "heiroku": [
        {"name": "Re:vive 久遠 misty おりがらみ", "abv": 14, "volume_ml": 720,
         "sub_ingredients": ["発芽玄米"], "price": None,
         "note": "発芽玄米ベースのRe:viveシリーズ標準"},
        {"name": "Re:vive 刹那", "abv": None, "volume_ml": 720,
         "sub_ingredients": ["発芽玄米"], "price": 2200,
         "note": "特約店扱い・参考価格"},
        {"name": "Re:vive Origin アカツキ", "abv": None, "volume_ml": 720,
         "sub_ingredients": ["発芽玄米"], "price": 11000,
         "note": "ハイエンド・特約店扱い参考価格"},
        {"name": "layer 洋ナシ", "abv": None, "volume_ml": 720,
         "sub_ingredients": ["洋ナシ果汁"], "price": 2200, "note": "特約店扱い"},
        {"name": "layer ぶどう", "abv": None, "volume_ml": 720,
         "sub_ingredients": ["ぶどう果汁"], "price": 2200, "note": "特約店扱い"},
        {"name": "layer りんご", "abv": None, "volume_ml": 720,
         "sub_ingredients": ["りんご果汁"], "price": 2200, "note": "特約店扱い"},
    ],

    "pukupuku": [
        {"name": "#plot 酵母無添加 ホップサケ", "abv": 7, "volume_ml": None,
         "sub_ingredients": ["ホップ"], "price": None,
         "note": "低アルコールのホップサケ"},
        {"name": "VaVaVa Spring 2026 DDH Doburoku", "abv": None, "volume_ml": 660,
         "sub_ingredients": ["ホップ"], "price": 2640, "note": ""},
        {"name": "KiKiKi Spring 2026 Hopped Sour", "abv": None, "volume_ml": 660,
         "sub_ingredients": ["ホップ"], "price": 2530, "note": ""},
        {"name": "#wildpath 水もとホップどぶろく", "abv": None, "volume_ml": 500,
         "sub_ingredients": ["ホップ"], "price": 2163, "note": ""},
        {"name": "木桶発酵 全麹酒 雫取り", "abv": None, "volume_ml": 500,
         "sub_ingredients": ["米のみ（全麹）"], "price": 11000,
         "note": "木桶仕込みの全麹酒、ハイエンド"},
        {"name": "アマーロどぶろく feat.伊勢屋酒造", "abv": None, "volume_ml": 460,
         "sub_ingredients": ["ハーブ", "ボタニカル"], "price": 2750,
         "note": "他蔵コラボ"},
    ],

    "adachi-noujo": [
        {"name": "KOYOI ～la première année～", "abv": 13, "volume_ml": 720,
         "sub_ingredients": ["米のみ（白麹仕込み・精米歩合80%）"], "price": None,
         "note": "第一弾。スッキリした綺麗さと心地よい酸"},
        {"name": "KOYOI La deuxième", "abv": 14, "volume_ml": 720,
         "sub_ingredients": ["米のみ"], "price": None, "note": "第二弾"},
    ],

    # ── 協会非加盟15社（情報が薄いものは概略のみ） ──
    "nondo": [
        {"name": "権化（ごんげ）", "abv": None, "volume_ml": None,
         "sub_ingredients": ["米のみ"], "price": None,
         "note": "自然栽培「遠野1号」米"},
        {"name": "とおの どぶろく速醸 生", "abv": None, "volume_ml": None,
         "sub_ingredients": ["米のみ"], "price": None, "note": ""},
    ],

    "fermenteria": [
        {"name": "サケベイビー", "abv": None, "volume_ml": None,
         "sub_ingredients": ["米のみ"], "price": None, "note": "駅ナカ醸造の生クラフトサケ"},
        {"name": "Rice Brew Milk", "abv": None, "volume_ml": None,
         "sub_ingredients": ["米のみ"], "price": None, "note": ""},
    ],

    "yamane": [
        {"name": "やまねのみのり", "abv": None, "volume_ml": None,
         "sub_ingredients": ["狭山茶", "発芽玄米"], "price": None,
         "note": "西川材の杉木桶仕込み"},
    ],

    "heiwa-kabutocho": [
        {"name": "平和どぶろく プレーン", "abv": None, "volume_ml": None,
         "sub_ingredients": ["米のみ"], "price": None, "note": ""},
        {"name": "平和どぶろく 小豆", "abv": None, "volume_ml": None,
         "sub_ingredients": ["小豆"], "price": None, "note": ""},
        {"name": "平和どぶろく 黒豆", "abv": None, "volume_ml": None,
         "sub_ingredients": ["黒豆"], "price": None, "note": ""},
        {"name": "平和どぶろく ホップ", "abv": None, "volume_ml": None,
         "sub_ingredients": ["ホップ"], "price": None, "note": ""},
        {"name": "平和どぶろく ブルーベリー", "abv": None, "volume_ml": None,
         "sub_ingredients": ["ブルーベリー"], "price": None, "note": ""},
        {"name": "平和どぶろく 抹茶", "abv": None, "volume_ml": None,
         "sub_ingredients": ["抹茶"], "price": None, "note": ""},
    ],

    "heiwa-namba": [
        {"name": "どぶろく プレーン", "abv": None, "volume_ml": None,
         "sub_ingredients": ["米のみ"], "price": None, "note": ""},
        {"name": "どぶろく 桜", "abv": None, "volume_ml": None,
         "sub_ingredients": ["桜"], "price": None, "note": "季節限定"},
        {"name": "どぶろく 抹茶", "abv": None, "volume_ml": None,
         "sub_ingredients": ["抹茶"], "price": None, "note": ""},
        {"name": "どぶろく 柚子", "abv": None, "volume_ml": None,
         "sub_ingredients": ["柚子"], "price": None, "note": ""},
    ],

    "tokyo-station": [
        {"name": "東京駅 どぶろく", "abv": None, "volume_ml": None,
         "sub_ingredients": ["米のみ"], "price": None, "note": ""},
        {"name": "フルーツどぶろく マンゴー", "abv": None, "volume_ml": None,
         "sub_ingredients": ["マンゴー"], "price": None, "note": ""},
        {"name": "フルーツどぶろく リンゴ", "abv": None, "volume_ml": None,
         "sub_ingredients": ["リンゴ"], "price": None, "note": ""},
        {"name": "フルーツどぶろく ぶどう", "abv": None, "volume_ml": None,
         "sub_ingredients": ["ぶどう"], "price": None, "note": ""},
        {"name": "フルーツどぶろく 桃", "abv": None, "volume_ml": None,
         "sub_ingredients": ["桃"], "price": None, "note": ""},
    ],

    "iyasaka": [
        {"name": "ITTEKI（一擲）十割麹酒 Vol.0-1", "abv": None, "volume_ml": None,
         "sub_ingredients": ["米のみ（米麹100%）"], "price": None,
         "note": "副原料なしだが米麹のみで造るため清酒規格外"},
    ],

    "sakenova": [
        {"name": "SAKENOVA", "abv": None, "volume_ml": None,
         "sub_ingredients": ["米のみ"], "price": None, "note": "佐渡産米使用"},
        {"name": "Crafted Series -Brew Note- ル レクチエ", "abv": None,
         "volume_ml": None, "sub_ingredients": ["ル レクチエ（洋梨）"],
         "price": None, "note": ""},
        {"name": "Crafted Series -Brew Note- 黒イチジク", "abv": None,
         "volume_ml": None, "sub_ingredients": ["黒イチジク"],
         "price": None, "note": ""},
    ],

    "linne": [
        {"name": "800 Barley（大麦）", "abv": None, "volume_ml": None,
         "sub_ingredients": ["大麦麹"], "price": None,
         "note": "haccoba/阿部酒造/LIBROMでの委託醸造"},
        {"name": "800 Buckwheat（蕎麦）", "abv": None, "volume_ml": None,
         "sub_ingredients": ["蕎麦麹"], "price": None, "note": ""},
        {"name": "800 Rice（米）", "abv": None, "volume_ml": None,
         "sub_ingredients": ["米麹"], "price": None, "note": ""},
        {"name": "800 Sweet Potato（薩摩芋）", "abv": None, "volume_ml": None,
         "sub_ingredients": ["芋麹"], "price": None, "note": ""},
    ],

    "amanosato": [
        {"name": "在る宵（あるよい）", "abv": None, "volume_ml": None,
         "sub_ingredients": ["福智町産無農薬果物", "ハーブ"], "price": None,
         "note": "福岡県産山田錦＋合鴨農法ヒノヒカリ使用"},
    ],

    "nomu": [
        {"name": "（初回醸造銘柄調整中）", "abv": None, "volume_ml": None,
         "sub_ingredients": ["アセロラ", "パイナップル", "シークワーサー"],
         "price": None, "note": "沖縄県産フルーツを副原料に。2025年11月醸造開始"},
    ],

    "salmon-brewery": [
        {"name": "鮭酒造シリーズ（生酛造り）", "abv": None, "volume_ml": None,
         "sub_ingredients": [], "price": None,
         "note": "多古米＋副原料で「限りなく日本酒に近いクラフトサケ」"},
    ],

    "tsuchiura": [],  # 2026年春開業予定・銘柄未発表

    "hakutsuru-sakecraft": [
        {"name": "HAKUTSURU SAKE CRAFT No.1〜No.7", "abv": None, "volume_ml": None,
         "sub_ingredients": ["米のみ（一部No.4はホップ）"], "price": None,
         "note": "No.4はホップ使用でロゼ色、各回非再現の一期一会型"},
    ],

    "dejima-hosendo": [
        {"name": "どぶろく各種（季節限定）", "abv": None, "volume_ml": None,
         "sub_ingredients": [], "price": None,
         "note": "九州初の都市型どぶろく醸造所。Brewery＋さけBar＋うつわGallery複合"},
    ],
}


def for_brewery(slug):
    return BRANDS.get(slug, [])

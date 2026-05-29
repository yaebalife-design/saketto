# -*- coding: utf-8 -*-
"""saketto / 受賞・メディア露出データ (2026-05-30確認)

各蔵について受賞・メディア掲載・海外進出を構造化。
type: "award" | "media" | "global"
"""

AWARDS = {
    "ine-to-agave": [
        {"type": "award", "year": 2023, "title": "ICC SAKE AWARD 初代優勝",
         "brand": "稲とアガベ OGAラベル",
         "source": "https://industry-co-creation.com/news/93891"},
        {"type": "award", "year": 2024, "title": "ICC SAKE AWARD 第3位",
         "brand": "花風",
         "source": "https://industry-co-creation.com/news/99025"},
        {"type": "media", "year": 2024, "title": "Forbes JAPAN「CULTURE-PRENEURS 30」選出",
         "brand": "岡住修兵代表",
         "source": "https://prtimes.jp/main/html/rd/p/000000032.000097044.html"},
        {"type": "media", "year": None, "title": "日経・朝日・毎日・週刊ダイヤモンド・Discover Japan他多数",
         "brand": None,
         "source": "https://note.com/inetoagave/n/n50e1f47f6856"},
    ],
    "haccoba": [
        {"type": "award", "year": 2025, "title": "日本パッケージデザイン大賞 銀賞（酒類カテゴリ）",
         "brand": "水を編む シリーズ",
         "source": "https://designcolon.com/haccoba-packageaward2025/"},
        {"type": "award", "year": 2025, "title": "東北アントレプレナー大賞（第32回東北ニュービジネス大賞）",
         "brand": None,
         "source": "https://prtimes.jp/main/html/rd/p/000000076.000061904.html"},
        {"type": "award", "year": 2023, "title": "ICC SAKE AWARD 準決勝進出",
         "brand": None, "source": "https://industry-co-creation.com/news/93891"},
        {"type": "global", "year": 2025, "title": "欧米進出開始（米/オランダ/ドイツ）",
         "brand": "Sunflower Sake(ポートランド)/Restaurant Flore(アムステルダム)/Enter Sake Berlin",
         "source": "https://prtimes.jp/main/html/rd/p/000000065.000061904.html"},
        {"type": "global", "year": None, "title": "アジア圏輸出（タイ/香港/シンガポール/台湾）",
         "brand": None,
         "source": "https://prtimes.jp/main/html/rd/p/000000065.000061904.html"},
    ],
    "pukupuku": [
        {"type": "award", "year": 2025, "title": "ICC SAKE AWARD 優勝",
         "brand": "#ODAKA – 蔵付酵母 木桶どぶろく –",
         "source": "https://industry-co-creation.com/news/115481"},
        {"type": "award", "year": 2024, "title": "ICC SAKE AWARD 決勝進出",
         "brand": None, "source": "https://industry-co-creation.com/news/99025"},
        {"type": "media", "year": 2024, "title": "京都芸術大学「クラフトサケ学」非常勤講師開設",
         "brand": "代表・立川哲之氏",
         "source": "https://prtimes.jp/main/html/rd/p/000000005.000107087.html"},
        {"type": "media", "year": 2024, "title": "経済産業省METI Journal・greenz.jp・BS朝日他",
         "brand": None,
         "source": "https://greenz.jp/2024/03/08/fukushima12_tachikawa-tetsuyuki/"},
    ],
    "linne": [
        {"type": "award", "year": 2025, "title": "ICC SAKE AWARD 準優勝",
         "brand": "800 大麦 樽熟成",
         "source": "https://industry-co-creation.com/news/115481"},
    ],
    "dejima-hosendo": [
        {"type": "award", "year": 2025, "title": "Tokyo酒チャレンジ 金賞",
         "brand": "芳扇 吟雲（九州初作付・初収穫の美山錦100%どぶろく）",
         "source": "https://www.atpress.ne.jp/news/433545"},
    ],
    "nondo": [
        {"type": "global", "year": 2024, "title": "Mugaritz（スペイン・旧3つ星）で提供",
         "brand": None,
         "source": "https://88bamboo.co/blogs/brand-spotlights/this-is-yotaro-sasakis-nondo-from-a-tiny-inn-in-iwate-prefectures-tono-city-comes-a-doburoku-sake-that-even-michelin-chefs-want-and-cant-have"},
        {"type": "global", "year": 2024, "title": "Disfrutar（バルセロナ・世界ベストレストラン2024年1位）で提供",
         "brand": None,
         "source": "https://88bamboo.co/blogs/brand-spotlights/this-is-yotaro-sasakis-nondo-from-a-tiny-inn-in-iwate-prefectures-tono-city-comes-a-doburoku-sake-that-even-michelin-chefs-want-and-cant-have"},
    ],
    "librom": [
        {"type": "global", "year": 2023, "title": "イタリア法人「LIBROM ITALY」設立",
         "brand": "バルバレスコ地区で現地米使用テスト醸造中",
         "source": "https://camp-fire.jp/projects/720095/view"},
    ],
    "happy-taro": [
        {"type": "media", "year": 2023, "title": "dancyu「クラフトSAKE醸造所訪問レポート ネオどぶろく」前後編大型特集",
         "brand": None, "source": "https://dancyu.jp/special/2023_00006966.html"},
    ],
    "heiroku": [
        {"type": "media", "year": None, "title": "Diamond『新日本酒紀行』掲載",
         "brand": None, "source": "https://diamond.jp/articles/-/346256"},
    ],
    "tokyo-station": [
        {"type": "media", "year": 2020, "title": "日経新聞「東京駅の店内で日本酒製造へ 国税庁、小売りに初認可」大型報道",
         "brand": None,
         "source": "https://www.nikkei.com/article/DGXMZO61253780X00C20A7EE8000/"},
    ],
    "sakenova": [
        {"type": "media", "year": 2025, "title": "日経新聞「サケアイ、佐渡に『クラフトサケ』の醸造所」",
         "brand": None,
         "source": "https://www.nikkei.com/article/DGXZQOCC2918J0Z20C26A1000000/"},
        {"type": "media", "year": 2025, "title": "日本アカデミー賞アフターパーティーで唯一の日本酒ブランドとして提供（約500名）",
         "brand": "SAKENOVA", "source": "https://sakeai.co.jp/service/sakenova"},
    ],
}


def for_brewery(slug):
    return AWARDS.get(slug, [])


def all_with_awards():
    """受賞・メディア・海外進出を持つ蔵を集計"""
    awarded_slugs = []
    for slug, items in AWARDS.items():
        if any(it["type"] == "award" for it in items):
            awarded_slugs.append(slug)
    return awarded_slugs

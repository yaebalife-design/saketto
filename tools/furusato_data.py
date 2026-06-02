# -*- coding: utf-8 -*-
"""saketto / ふるさと納税取扱データ (2026-05-30確認)

portals: ["c"=チョイス, "r"=楽天, "f"=ふるなび, "s"=さとふる, "ANA"=ANAのみ確認]
"""

FURUSATO = {

    "ine-to-agave": {
        "city": "秋田県男鹿市",
        "portals": ["c", "r", "f"],
        "donation_yen": 10500,
        "rep_brand": "CRAFT 稲とアガベ OGAラベル 500ml / 発酵マヨ6種セット",
        "urls": {
            "r": "https://item.rakuten.co.jp/f052060-oga/56050822/",
            "f": "https://furunavi.jp/product_detail.aspx?pid=1245441",
            "c": "https://www.furusato-tax.jp/product/detail/05206/5885075",
        },
        "note": "稲とアガベの代表銘柄が複数ポータルで出品中",
    },

    "haccoba": {
        "city": "福島県南相馬市",
        "portals": ["c", "r", "f", "s"],
        "donation_yen": 12000,
        "rep_brand": "はなうたホップス 720ml×2本",
        "urls": {
            "r": "https://item.rakuten.co.jp/f072125-minamisoma/41001/",
            "ANA": "https://furusato.ana.co.jp/donation/g/g07212-41001/",
        },
        "note": "4大ポータル+ANA展開。ANA経由は19,000円(2本)",
    },

    "heiroku": {
        "city": "岩手県紫波町",
        "portals": ["c"],
        "donation_yen": 40000,
        "rep_brand": "Re:vive Origin アカツキ 720ml",
        "urls": {
            "c": "https://www.furusato-tax.jp/product/detail/03321/6335322",
        },
        "note": "ふるさとチョイス限定。ハイエンドRe:viveを返礼品化",
    },

    "adachi-noujo": {
        "city": "大阪府高槻市",
        "portals": ["c", "r"],
        "donation_yen": 15000,
        "rep_brand": "KOYOI 720ml",
        "urls": {
            "r": "https://item.rakuten.co.jp/f272078-takatsuki/em001/",
        },
        "note": "楽天15,000円、JRE MALL 49,000円と価格差あり",
    },

    "amanosato": {
        "city": "福岡県福智町",
        "portals": ["c", "r", "f", "s"],
        "donation_yen": 13000,
        "rep_brand": "在る 緒奏（しょそう）720ml",
        "urls": {
            "r": "https://item.rakuten.co.jp/f406104-fukuchi/w37-02/",
        },
        "note": "4大ポータル全展開",
    },

    "nomu": {
        "city": "沖縄県沖縄市",
        "portals": ["ANA"],
        "donation_yen": 56000,
        "rep_brand": "SHISHIKAMU 720ml×6本",
        "urls": {
            "ANA": "https://furusato.ana.co.jp/donation/g/g47211-BCES007/",
        },
        "note": "ANAふるさと納税のみ確認。4大ポータル(c/r/f/s)での確認は未実施",
    },
}


PORTAL_NAMES = {
    "c": "ふるさとチョイス",
    "r": "楽天ふるさと納税",
    "f": "ふるなび",
    "s": "さとふる",
    "ANA": "ANAのふるさと納税",
}


def for_brewery(slug):
    return FURUSATO.get(slug)


def all_confirmed_slugs():
    return list(FURUSATO.keys())

# -*- coding: utf-8 -*-
"""saketto / ふるさと納税取扱データ

portals: ["c"=チョイス, "r"=楽天, "f"=ふるなび, "s"=さとふる, "ANA"=ANAのみ確認]

⚠️ **返礼品のURLは腐る。** 2026/08/31 の再確認で、稲とアガベの3URLが全て
死んでいた（楽天404・チョイス404・ふるなびは200だが本文が「見つかりませんでした」）。
返礼品は時期で入れ替わるので、**定期的にURLの生存確認をすること**。
死んだURLを残すと、読者を404へ送りつつ「返礼品あり」と嘘をつくことになる。
生存確認: python tools/check_furusato_urls.py
"""

FURUSATO = {

    # 2026/08/31 再確認：楽天404・チョイス404・ふるなびはソフト404。
    # 男鹿市のふるさとチョイスを検索しても、出てくるのは「発酵マヨ」と
    # 「SANABURI SPIRITS」(ジン)のみで、クラフトサケの返礼品は確認できず。
    # 出品が戻ったら復活させる。それまでは未確認扱いにする。
    # "ine-to-agave": {...},

    "haccoba": {
        "city": "福島県南相馬市",
        # ふるなび・さとふるにも出品ありと2026/05に記録していたが、いずれも
        # 検索結果がJSレンダリングで機械確認できず、URLも取れていない。
        # 確認できたポータルだけを載せる（URLの無いものは表示しない）。
        "portals": ["c", "r"],
        # 2026/08/31 訂正：12,000円としていたが、チョイス・ANAとも実際は19,000円だった
        "donation_yen": 19000,
        "rep_brand": "はなうたホップス 720ml×2本",
        "urls": {
            "c": "https://www.furusato-tax.jp/product/detail/07212/5278190",
            "r": "https://item.rakuten.co.jp/f072125-minamisoma/41001/",
            "ANA": "https://furusato.ana.co.jp/donation/g/g07212-41001/",
        },
        "note": "チョイス・楽天・ANAで確認。チョイス／ANAとも19,000円（720ml×2本）。ふるなび・さとふるは2026/05に出品ありと記録したが今回は確認できず",
    },

    "heiroku": {
        "city": "岩手県紫波町",
        "portals": ["c"],
        # 2026/08/31 訂正：チョイスの実額は41,000円だった
        "donation_yen": 41000,
        "rep_brand": "Re:vive Origin アカツキ 720ml",
        "urls": {
            "c": "https://www.furusato-tax.jp/product/detail/03321/6335322",
        },
        "note": "ふるさとチョイス限定。ハイエンドRe:viveを返礼品化",
    },

    "adachi-noujo": {
        "city": "大阪府高槻市",
        "portals": ["c", "r"],
        "donation_yen": 12000,
        # 2026/08/31 訂正：楽天の返礼品は「MIYOI Origin」で、KOYOI ではなかった。
        # 最低額はチョイスの MIYOI Craft KIWI が12,000円（2種飲み比べは24,000円）。
        # KOYOI と MIYOI は同じ蔵の別シリーズなので、返礼品名を実物に合わせる。
        "rep_brand": "MIYOI Origin 720ml",
        "urls": {
            "r": "https://item.rakuten.co.jp/f272078-takatsuki/em001/",
            # 表示している最低額と一致する返礼品へ送る（飲み比べセット
            # /6496132 は24,000円で、12,000円と表示しながらそこへ飛ばすと食い違う）
            "c": "https://www.furusato-tax.jp/product/detail/27207/6496131",
        },
        "note": "チョイスは MIYOI Craft KIWI（さぬきゴールド）12,000円、2種飲み比べ24,000円。楽天は MIYOI Origin 15,000円",
    },

    "amanosato": {
        "city": "福岡県福智町",
        # ふるなび・さとふるは確認できていないため載せない（上の haccoba と同じ理由）
        "portals": ["c", "r"],
        # 2026/08/31 訂正：チョイスの実額は12,500円だった（寒夜レモン500mlは13,000円）
        "donation_yen": 12500,
        "rep_brand": "在る宵 緒奏（しょそう）720ml",
        "urls": {
            "c": "https://www.furusato-tax.jp/product/detail/40610/6968022",
            "r": "https://item.rakuten.co.jp/f406104-fukuchi/w37-02/",
        },
        "note": "チョイス・楽天で確認。チョイスには「在る宵 寒夜（レモン）500ml」13,000円もあり（/40610/6968024）。ふるなび・さとふるは今回確認できず",
    },

    "mingura": {
        "city": "岩手県大船渡市",
        "portals": ["c", "r"],
        "donation_yen": 10000,
        "rep_brand": "どぶろく つぶつぶ／とろとろ 500ml",
        "urls": {
            "c": "https://www.furusato-tax.jp/product/detail/03203/7071273",
            "r": "https://item.rakuten.co.jp/f032034-ofunato/cen001/",
        },
        "note": "2026/08/31 確認。事業者名は運営元の株式会社セントラル伸光。原料米はぎんおとめ。ふるなび・さとふる・ANAでは確認できず",
    },

    "hajimari": {
        "city": "岩手県紫波郡紫波町",
        "portals": ["c", "r", "f", "ANA"],
        "donation_yen": 9000,
        "rep_brand": "はじまりのお酒 720ml",
        # 4ポータルとも同じ商品(DK002)で、2026/08/31時点はすべて在庫なし。
        # 出品自体は生きているので隠さず、品切れと明示して出す。
        "status": "現在4ポータルとも品切れ",
        "urls": {
            "c": "https://www.furusato-tax.jp/product/detail/03321/5893437",
            "r": "https://item.rakuten.co.jp/f033219-shiwa/dk001/",
            "f": "https://furunavi.jp/product_detail.aspx?pid=986919",
            "ANA": "https://furusato.ana.co.jp/donation/g/g03321-DK002/",
        },
        "note": "返礼品の中身は紫波町の月の輪酒造店が醸した樽酒で、はじまりの学校の自社醸造施設（2026年5月完成）で醸したものではないと商品説明にある",
    },

    "nomu": {
        "city": "沖縄県沖縄市",
        "portals": ["ANA"],
        "donation_yen": 56000,
        "rep_brand": "SHISHIKAMU 720ml×6本",
        "urls": {
            "ANA": "https://furusato.ana.co.jp/donation/g/g47211-BCES007/",
        },
        "note": "ANAのふるさと納税で確認。沖縄市にはノンアルの「OFFZAKE プレミアムパック」もあるが、酒ではないため掲載しない",
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

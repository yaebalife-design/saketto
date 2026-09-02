# -*- coding: utf-8 -*-
"""saketto / ふるさと納税取扱データ（2026-08-31 全面再調査）

## データの形

蔵ごとに `items`（返礼品1件＝1エントリ）を持つ。
以前は蔵に「ポータルのコード一覧」と「寄附額ひとつ」しか持てず、
同じ蔵でもポータルごと・セット内容ごとに額が違う実態を表せなかった
（12,000円と表示して実際は19,000円だった例がある）。

各 item:
  portal    … "c"=ふるさとチョイス / "r"=楽天 / "f"=ふるなび / "s"=さとふる
              / "a"=au PAY ふるさと納税 / "ANA"
  url       … 返礼品ページの正規URL（クエリパラメータは付けない）
              例外: au PAY は product_id がクエリなので ?product_id=... まで含める。
              product_div=bel は付けなくても同じページが開くので付けない
  yen       … 寄附額（確認できないときは None）
  brand     … 対応する銘柄
  accepting … 申込可能なら True。品切れ・受付終了は False
  city      … 蔵の所在自治体と違う自治体からの出品のときだけ書く

## 運用上の注意（実際に踏んだもの）

- **返礼品URLは黙って死ぬ。** 2026/08/31 の点検で稲とアガベの3URLが全滅していた。
  `python tools/check_furusato_urls.py` を定期実行すること。
- **ふるなびは200を返しながら中身が空のことがある**（ソフト404）。
  ステータスコードだけでは分からない。
- **ふるなび・さとふるは検索結果がJSレンダリング**で機械確認しにくい。
  さとふるはこの環境から接続自体ができず、全蔵で未検証。
- **au PAY は検索・商品ページともサーバ側描画**で最も機械確認しやすい
  （検索は `?search_word=`。name / keyword でも200が返るが検索が効かず全件出るので使わない）。
  ただし在庫判定に「品切」の文字列を使ってはいけない。サイドバーの絞り込み
  「品切れ中も含む」が全ページに出るため全件が品切れ扱いになる。
  在庫は「カートに入れる」の有無、寄附額は `id="gift-money-contents"` で見る
  （ページ内の他の「○○円」を拾うと額がずれる。実際に54,000と56,000でずれた）。
  検索結果に存在を示唆する記述はあっても、商品URLで裏が取れないものは載せない。
- 食品セットでも、クラフトサケが中身に含まれるものは掲載する
  （逆に、商品名にSEO目的で「クラフトサケ」と入っているだけで酒を含まないものは除外）。
- ノンアルコール（甘酒等）は対象外。
"""

FURUSATO = {

    # 2026/08/31 再調査：以前記録していた3URL（チョイス・楽天・ANA）がすべて404。
    # 男鹿市に残るのは発酵マヨと SANABURI SPIRITS（蒸留酒）だけで、
    # クラフトサケの返礼品は5ポータルのいずれにも無い。出品が戻ったら復活させる。
    # "ine-to-agave": {...},

    "haccoba": {
        "city": "福島県南相馬市",
        "items": [
            {"portal": "c", "url": "https://www.furusato-tax.jp/product/detail/07212/5278190",
             "yen": 19000, "brand": "はなうたホップス 720ml×2本", "accepting": True},
            {"portal": "r", "url": "https://item.rakuten.co.jp/f072125-minamisoma/41001/",
             "yen": 19000, "brand": "はなうたホップス 720ml×2本", "accepting": True},
            {"portal": "f", "url": "https://furunavi.jp/product_detail.aspx?pid=470819",
             "yen": 19000, "brand": "はなうたホップス 720ml×2本", "accepting": True},
            {"portal": "ANA", "url": "https://furusato.ana.co.jp/donation/g/g07212-41001/",
             "yen": 19000, "brand": "はなうたホップス 720ml×2本", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=553068",
             "yen": 19000, "brand": "はなうたホップス 720ml×2本", "accepting": True},
            # 蔵の地元とは別の自治体からの出品。現在は品切れ
            {"portal": "ANA", "url": "https://furusato.ana.co.jp/donation/g/g43505-024-0701/",
             "yen": 12000, "brand": "I'm home! -TARAGI- 500ml", "accepting": False,
             "city": "熊本県多良木町"},
            {"portal": "ANA", "url": "https://furusato.ana.co.jp/donation/g/g43505-024-0702/",
             "yen": 22000, "brand": "I'm home! -TARAGI- 500ml×2本", "accepting": False,
             "city": "熊本県多良木町"},
        ],
        "note": "多良木町との共同醸造「I'm home! -TARAGI-」はANA限定で、熊本県多良木町からの出品。現在は品切れ。さとふるは接続できず未確認",
    },

    "heiroku": {
        "city": "岩手県紫波町",
        "items": [
            {"portal": "c", "url": "https://www.furusato-tax.jp/product/detail/03321/6335322",
             "yen": 41000, "brand": "Re:vive Origin アカツキ 720ml", "accepting": True},
            {"portal": "r", "url": "https://item.rakuten.co.jp/f033219-shiwa/ea001/",
             "yen": 41000, "brand": "Re:vive Origin アカツキ 720ml", "accepting": True},
            {"portal": "ANA", "url": "https://furusato.ana.co.jp/donation/g/g03321-EA001/",
             "yen": 41000, "brand": "Re:vive Origin アカツキ 720ml", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=1496576",
             "yen": 41000, "brand": "Re:vive Origin アカツキ 720ml", "accepting": True},
        ],
        "note": "4ポータルとも同じ EA001 で41,000円",
    },

    "adachi-noujo": {
        "city": "大阪府高槻市",
        "items": [
            {"portal": "c", "url": "https://www.furusato-tax.jp/product/detail/27207/6496131",
             "yen": 12000, "brand": "MIYOI Craft KIWI-さぬきゴールド-", "accepting": True},
            {"portal": "c", "url": "https://www.furusato-tax.jp/product/detail/27207/6496132",
             "yen": 24000, "brand": "MIYOI Craft 2種飲み比べ", "accepting": True},
            {"portal": "r", "url": "https://item.rakuten.co.jp/f272078-takatsuki/aocu002/",
             "yen": 12000, "brand": "MIYOI Craft KIWI-さぬきゴールド-", "accepting": True},
            {"portal": "r", "url": "https://item.rakuten.co.jp/f272078-takatsuki/em001/",
             "yen": 14000, "brand": "MIYOI Origin 720ml", "accepting": True},
            {"portal": "r", "url": "https://item.rakuten.co.jp/f272078-takatsuki/aocu003/",
             "yen": 24000, "brand": "MIYOI Craft 2種飲み比べ", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2000971",
             "yen": 12000, "brand": "MIYOI Craft KIWI-さぬきゴールド-", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2000972",
             "yen": 24000, "brand": "MIYOI Craft 2種飲み比べ", "accepting": True},
        ],
        "note": "返礼品は KOYOI ではなく MIYOI シリーズ（同じ蔵の別シリーズ）。MIYOI Origin は楽天のみ",
    },

    "amanosato": {
        "city": "福岡県福智町",
        "items": [
            {"portal": "c", "url": "https://www.furusato-tax.jp/product/detail/40610/6968022",
             "yen": 12500, "brand": "在る宵 緒奏（しょそう）720ml", "accepting": True},
            {"portal": "c", "url": "https://www.furusato-tax.jp/product/detail/40610/6968024",
             "yen": 13000, "brand": "在る宵 寒夜（レモン）500ml", "accepting": True},
            {"portal": "r", "url": "https://item.rakuten.co.jp/f406104-fukuchi/w37-02/",
             "yen": 12500, "brand": "在る宵 緒奏（しょそう）720ml", "accepting": True},
            {"portal": "r", "url": "https://item.rakuten.co.jp/f406104-fukuchi/w37-06/",
             "yen": 13000, "brand": "在る宵 寒夜（レモン）500ml", "accepting": True},
            {"portal": "ANA", "url": "https://furusato.ana.co.jp/donation/g/g40610-W37-02/",
             "yen": 12500, "brand": "在る宵 緒奏（しょそう）720ml", "accepting": True},
            {"portal": "ANA", "url": "https://furusato.ana.co.jp/donation/g/g40610-W37-06/",
             "yen": 13000, "brand": "在る宵 寒夜（レモン）500ml", "accepting": True},
            # 食品セットだが、中身に緒奏180mlが含まれるもの
            {"portal": "r", "url": "https://item.rakuten.co.jp/f406104-fukuchi/w61-176/",
             "yen": 8500, "brand": "漬け魚詰合せ＋緒奏 180ml", "accepting": True},
            {"portal": "r", "url": "https://item.rakuten.co.jp/f406104-fukuchi/w61-178/",
             "yen": 8500, "brand": "干物詰合せ＋緒奏 180ml", "accepting": True},
            {"portal": "r", "url": "https://item.rakuten.co.jp/f406104-fukuchi/w61-14/",
             "yen": 10500, "brand": "牛もつ鍋＋緒奏 180ml", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2385617",
             "yen": 12500, "brand": "在る宵 緒奏（しょそう）720ml", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2385618",
             "yen": 13000, "brand": "在る宵 寒夜（レモン）500ml", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2424335",
             "yen": 8500, "brand": "干物詰合せ＋緒奏 180ml", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2395838",
             "yen": 8500, "brand": "漬け魚詰合せ＋緒奏 180ml", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2391200",
             "yen": 10500, "brand": "牛もつ鍋＋緒奏 180ml", "accepting": True},
            # 以下4件は au PAY でのみ確認できた増量版（楽天・チョイスには無い）
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2424336",
             "yen": 12000, "brand": "干物詰合せ（15切）＋緒奏 180ml", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2395839",
             "yen": 12000, "brand": "漬け魚詰合せ（15切）＋緒奏 180ml", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2391201",
             "yen": 15000, "brand": "牛もつ鍋（2人前×5）＋緒奏 180ml", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2391202",
             "yen": 24500, "brand": "牛もつ鍋（2人前×10）＋緒奏 180ml", "accepting": True},
        ],
        "note": "収録中で最も選択肢が多い。食品とのセット（緒奏180ml入り）は8,500円からで、最も少額から寄附できる。au PAY だけは同じセットの増量版（干物・漬け魚の15切、もつ鍋の5/10セット）も扱う",
    },

    "happy-taro": {
        "city": "滋賀県長浜市",
        "items": [
            {"portal": "c", "url": "https://www.furusato-tax.jp/product/detail/25203/6338700",
             "yen": 17000, "brand": "ハッピーどぶろく 480ml×2本", "accepting": True},
            {"portal": "r", "url": "https://item.rakuten.co.jp/f252034-nagahama/11551-30047299/",
             "yen": 17000, "brand": "ハッピーどぶろく 480ml×2本", "accepting": True},
            {"portal": "c", "url": "https://www.furusato-tax.jp/product/detail/25203/6593072",
             "yen": 20000, "brand": "ハッピーどぶろく＋something happy オリエンタルホエー", "accepting": True},
            {"portal": "r", "url": "https://item.rakuten.co.jp/f252034-nagahama/aqar004/",
             "yen": 20000, "brand": "ハッピーどぶろく＋something happy オリエンタルホエー", "accepting": True},
            {"portal": "f", "url": "https://furunavi.jp/product_detail.aspx?pid=1583248",
             "yen": 20000, "brand": "ハッピーどぶろく＋something happy オリエンタルホエー", "accepting": True},
            {"portal": "c", "url": "https://www.furusato-tax.jp/product/detail/25203/7136707",
             "yen": 20000, "brand": "ハッピーどぶろく＋お楽しみどぶろく 2本セット", "accepting": True},
            {"portal": "c", "url": "https://www.furusato-tax.jp/product/detail/25203/6593073",
             "yen": 82000, "brand": "お楽しみどぶろく 全4回定期便", "accepting": True},
            {"portal": "r", "url": "https://item.rakuten.co.jp/f252034-nagahama/aqar005/",
             "yen": 82000, "brand": "お楽しみどぶろく 全4回定期便", "accepting": True},
            {"portal": "f", "url": "https://furunavi.jp/product_detail.aspx?pid=1583249",
             "yen": 82000, "brand": "お楽しみどぶろく 全4回定期便", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=1500511",
             "yen": 17000, "brand": "ハッピーどぶろく 480ml×2本", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2121963",
             "yen": 20000, "brand": "ハッピーどぶろく＋something happy オリエンタルホエー", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2716898",
             "yen": 20000, "brand": "ハッピーどぶろく＋お楽しみどぶろく 2本セット", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2121964",
             "yen": 82000, "brand": "お楽しみどぶろく 全4回定期便", "accepting": True},
        ],
        "note": "提供事業者は醸造所が入る「湖のスコーレ株式会社」。同じ事業者の米糀チーズケーキは酒を含まないため掲載していない",
    },

    "librom": {
        "city": "福岡県福岡市",
        "items": [
            {"portal": "c", "url": "https://www.furusato-tax.jp/product/detail/40130/6968026",
             "yen": 20000, "brand": "熟成酒 まるごとジューシー博多あまおう 2本セット", "accepting": True},
            {"portal": "r", "url": "https://item.rakuten.co.jp/f401307-fukuoka/54110212/",
             "yen": 20000, "brand": "熟成酒 まるごとジューシー博多あまおう 2本セット", "accepting": True},
            {"portal": "f", "url": "https://furunavi.jp/product_detail.aspx?pid=1912006",
             "yen": 20000, "brand": "熟成酒 まるごとジューシー博多あまおう 2本セット", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2529022",
             "yen": 20000, "brand": "熟成酒 まるごとジューシー博多あまおう 2本セット", "accepting": True},
            # 太宰府市からの出品。梅は太宰府市産。現在は品切れ
            {"portal": "c", "url": "https://www.furusato-tax.jp/product/detail/40221/5918981",
             "yen": 13000, "brand": "LIBROM UME 500ml", "accepting": False,
             "city": "福岡県太宰府市"},
            {"portal": "r", "url": "https://item.rakuten.co.jp/f402214-dazaifu/166-1195/",
             "yen": 13000, "brand": "LIBROM UME 500ml", "accepting": False,
             "city": "福岡県太宰府市"},
        ],
        "note": "あまおうの熟成酒はLIBROM醸造だが提供事業者名は別（Babi920）。太宰府市産の梅を使う「UME」は太宰府市からの出品で、現在は品切れ",
    },

    "lagoon": {
        # 蔵は新潟市北区だが、返礼品は米の産地である燕市からの出品
        "city": "新潟県燕市",
        "items": [
            {"portal": "c", "url": "https://www.furusato-tax.jp/product/detail/15213/6875232",
             "yen": 17000, "brand": "燕市産こしいぶき＋どぶろく セット", "accepting": True},
            {"portal": "r", "url": "https://item.rakuten.co.jp/f152137-tsubame/10003039/",
             "yen": 17000, "brand": "燕市産こしいぶき＋どぶろく セット", "accepting": True},
            {"portal": "f", "url": "https://furunavi.jp/product_detail.aspx?pid=1815901",
             "yen": 17000, "brand": "燕市産こしいぶき＋どぶろく セット", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2427383",
             "yen": 17000, "brand": "燕市産こしいぶき＋どぶろく セット", "accepting": True},
        ],
        "note": "蔵の所在は新潟市北区だが、返礼品は米の産地である燕市から出ている。減農薬米こしいぶきをLAGOON BREWERYが醸したどぶろくと米2kgのセット。新潟市からの出品は確認できず",
    },

    "nondo": {
        "city": "岩手県遠野市",
        "items": [
            {"portal": "r", "url": "https://item.rakuten.co.jp/f032085-tono/1579727/",
             "yen": 21000, "brand": "とおの どぶろく 速醸 生 500ml×2本", "accepting": True},
        ],
        "note": "商品ページに「製造元:株式会社nondo」「とおの屋『要』が自家醸造」と明記。発送は地元の松田酒店。ふるさとチョイスにあった「権化 MARO」は掲載終了（404）",
    },

    # 平和どぶろくは兜町・難波とも、返礼品は親会社の平和酒造（和歌山県海南市）名義。
    # 商品ページに「どちらの醸造所で仕込んだか」の記載がないため、
    # 同じ商品を両方の蔵に紐づけたうえで、その旨を注記する。
    "heiwa-kabutocho": {
        "city": "和歌山県海南市",
        "items": [
            {"portal": "c", "url": "https://www.furusato-tax.jp/product/detail/30202/6984105",
             "yen": 23000, "brand": "平和どぶろく 壱ノ濁・弐ノ濁・参ノ濁 720ml×3本", "accepting": True},
            {"portal": "ANA", "url": "https://furusato.ana.co.jp/donation/g/g30202-W032/",
             "yen": 23000, "brand": "平和どぶろく 壱ノ濁・弐ノ濁・参ノ濁 720ml×3本", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2546230",
             "yen": 23000, "brand": "平和どぶろく 壱ノ濁・弐ノ濁・参ノ濁 720ml×3本", "accepting": True},
        ],
        "note": "返礼品は東京都中央区ではなく、親会社である平和酒造の地元・和歌山県海南市から出ている。壱ノ濁は米と米こうじ、弐ノ濁は白麹、参ノ濁はホップ入り。兜町・難波どちらの醸造所で仕込んだかは商品ページに記載がない",
    },

    "heiwa-namba": {
        "city": "和歌山県海南市",
        "items": [
            {"portal": "c", "url": "https://www.furusato-tax.jp/product/detail/30202/6984105",
             "yen": 23000, "brand": "平和どぶろく 壱ノ濁・弐ノ濁・参ノ濁 720ml×3本", "accepting": True},
            {"portal": "ANA", "url": "https://furusato.ana.co.jp/donation/g/g30202-W032/",
             "yen": 23000, "brand": "平和どぶろく 壱ノ濁・弐ノ濁・参ノ濁 720ml×3本", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2546230",
             "yen": 23000, "brand": "平和どぶろく 壱ノ濁・弐ノ濁・参ノ濁 720ml×3本", "accepting": True},
        ],
        "note": "返礼品は大阪市ではなく、親会社である平和酒造の地元・和歌山県海南市から出ている。兜町醸造所と同じ商品で、どちらの醸造所で仕込んだかは商品ページに記載がない",
    },

    "mingura": {
        "city": "岩手県大船渡市",
        "items": [
            {"portal": "c", "url": "https://www.furusato-tax.jp/product/detail/03203/7071273",
             "yen": 10000, "brand": "どぶろく つぶつぶ／とろとろ 500ml", "accepting": True},
            {"portal": "r", "url": "https://item.rakuten.co.jp/f032034-ofunato/cen001/",
             "yen": 10000, "brand": "どぶろく つぶつぶ／とろとろ 500ml", "accepting": True},
            # au PAY だけは「つぶつぶ」「とろとろ」を別商品として売っている
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2658506",
             "yen": 10000, "brand": "どぶろく つぶつぶ 500ml", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2658507",
             "yen": 10000, "brand": "どぶろく とろとろ 500ml", "accepting": True},
        ],
        "note": "事業者名は運営元の株式会社セントラル伸光。原料米はぎんおとめ。チョイス・楽天は「つぶつぶ／とろとろ」から選ぶ1商品だが、au PAY は2商品に分かれている",
    },

    "nomu": {
        "city": "沖縄県沖縄市",
        "items": [
            {"portal": "c", "url": "https://www.furusato-tax.jp/product/detail/47211/6999637",
             "yen": 56000, "brand": "SHISHIKAMU 720ml×6本", "accepting": True},
            {"portal": "r", "url": "https://item.rakuten.co.jp/f472115-okinawa/bces007/",
             "yen": 56000, "brand": "SHISHIKAMU 720ml×6本", "accepting": True},
            {"portal": "ANA", "url": "https://furusato.ana.co.jp/donation/g/g47211-BCES007/",
             "yen": 56000, "brand": "SHISHIKAMU 720ml×6本", "accepting": True},
            {"portal": "a", "url": "https://furusato.wowma.jp/products/detail.php?product_id=2570537",
             "yen": 56000, "brand": "SHISHIKAMU 720ml×6本", "accepting": True},
        ],
        "note": "沖縄市にはノンアルの「OFFZAKE」シリーズ7種もあるが、酒ではないため掲載していない",
    },

    "hajimari": {
        "city": "岩手県紫波郡紫波町",
        "items": [
            {"portal": "c", "url": "https://www.furusato-tax.jp/product/detail/03321/5893437",
             "yen": 9000, "brand": "はじまりのお酒 720ml", "accepting": False},
            {"portal": "r", "url": "https://item.rakuten.co.jp/f033219-shiwa/dk001/",
             "yen": 9000, "brand": "はじまりのお酒 720ml", "accepting": False},
            {"portal": "f", "url": "https://furunavi.jp/product_detail.aspx?pid=986919",
             "yen": 9000, "brand": "はじまりのお酒 720ml", "accepting": False},
            {"portal": "ANA", "url": "https://furusato.ana.co.jp/donation/g/g03321-DK002/",
             "yen": 9000, "brand": "はじまりのお酒 720ml", "accepting": False},
        ],
        "note": "4ポータルとも同じ商品(DK002)で、2026/08/31時点はすべて品切れ。中身は紫波町の月の輪酒造店が醸した樽酒で、はじまりの学校の自社醸造施設（2026年5月完成）で醸したものではないと商品説明にある",
    },
}


PORTAL_NAMES = {
    "c": "ふるさとチョイス",
    "r": "楽天ふるさと納税",
    "a": "au PAY ふるさと納税",
    "f": "ふるなび",
    "s": "さとふる",
    "ANA": "ANAのふるさと納税",
}

# 表示順。提携済み（＝成果が発生する）楽天・au PAY を先に置く。
# 楽天は moshimo_link.py、au PAY は a8_link.py が担当する。
PORTAL_ORDER = ["r", "a", "c", "f", "s", "ANA"]


def items_of(slug):
    return (FURUSATO.get(slug) or {}).get("items", [])


def portals_of(slug, accepting_only=True):
    """その蔵で寄附できるポータルのコード一覧（表示順）。"""
    codes = {i["portal"] for i in items_of(slug)
             if i.get("accepting", True) or not accepting_only}
    return [p for p in PORTAL_ORDER if p in codes]


def best_url(slug, portal):
    """そのポータルで最も少額の、申込可能な返礼品URL。無ければ品切れ品でも返す。"""
    live = [i for i in items_of(slug)
            if i["portal"] == portal and i.get("accepting", True)]
    pool = live or [i for i in items_of(slug) if i["portal"] == portal]
    if not pool:
        return None
    return sorted(pool, key=lambda i: i.get("yen") or 10 ** 9)[0]["url"]


def price_range(slug):
    """寄附額の下限・上限。申込可能なものを優先し、全て品切れなら品切れ品の額を返す
    （額が分からないと「戻ってきたら申し込むか」の判断ができないため）。"""
    live = sorted({i["yen"] for i in items_of(slug)
                   if i.get("accepting", True) and i.get("yen")})
    if live:
        return (live[0], live[-1])
    allv = sorted({i["yen"] for i in items_of(slug) if i.get("yen")})
    return (allv[0], allv[-1]) if allv else None


def is_accepting(slug):
    return any(i.get("accepting", True) for i in items_of(slug))


def item_count(slug, accepting_only=True):
    return len([i for i in items_of(slug)
                if i.get("accepting", True) or not accepting_only])


def for_brewery(slug):
    return FURUSATO.get(slug)


def all_confirmed_slugs():
    return list(FURUSATO.keys())

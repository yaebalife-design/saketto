# -*- coding: utf-8 -*-
"""醸造所を訪ねる人のための情報（飲める・買える・見学できる）。

蔵ページの「VISIT／訪ねる」と、読みもの「クラフトサケが飲める醸造所」がここを読む。
🔴 嘘ゼロ：各蔵の公式サイト・公式ショップ・公式リリースに書いてあることだけ。
   報道を使うときは媒体名を本文に書く。営業時間・料金・メニューは変わりやすいので載せない（公式で確認と書く）。
   確認できないものは None（ページには出さない）。「案内が無い」と「できない」を書き分ける。
   2026-10-28 に別Agent 2体で全文を出典と突き合わせ、指摘30点を反映済み。
キー: drink（飲める）/ buy（買える）/ tour（見学・体験）/ tour_kind（"event"＝イベントのときだけ）/
      address / access / caution / sources / official（公式サイトの代わりにリンクする先。None でリンクしない）
"""

CHECKED = "2026-10-28"

VISIT = {
    # ── 東北 ──
    "ine-to-agave": {
        "drink": "醸造所とは別の、直営のラーメン店「らーめん おがや」（男鹿市内）で、ラーメン専用の「稲とアガベ」とのペアリングを出している。",
        "buy": None,
        "tour": "男鹿で創業祭（2025年11月の4周年「OṃOn」）などのイベントを開いている。定期的な見学の案内はない。",
        "tour_kind": "event",
        "address": "秋田県男鹿市船川港船川新浜町1-21",
        "access": None,
        "caution": "醸造所は旧駅舎を改装した建物。併設の「土と風」は、公式サイト内でカフェ営業・完全予約制のレストランと書き方が分かれている。イベントの告知は公式のnote・SNS。",
        "sources": ["https://www.inetoagave.com/", "https://www.inetoagave.com/pages/restaurant/",
                    "https://www.inetoagave.com/pages/terroir/", "https://note.com/inetoagave/",
                    "https://san-tatsu.jp/pressrelease/474764/"],
    },
    "haccoba": {
        "drink": "醸造所とパブが一体の「haccoba 小高醸造所 &KITCHEN」のブリューパブで、酒蔵を眺めながら酒と料理を楽しめる。",
        "buy": "同じ建物のショップで酒とグッズを販売。小高駅舎内の「haccoba 小高駅舎醸造所&PUBLIC MARKET」も公式の販売先として案内されている。",
        "tour": None,
        "address": "福島県南相馬市小高区田町2-50-6",
        "access": "JR常磐線 小高駅から徒歩7分",
        "caution": "飲食のブリューパブは金・土・日の夜のみの営業で予約制（公式のフォームかメール）、8席。ショップはブリューパブとは別の時間帯で営業している。",
        "sources": ["https://haccoba.com/pages/brew-pub",
                    "https://haccoba.com/pages/%E7%89%B9%E5%AE%9A%E5%95%86%E5%8F%96%E5%BC%95%E6%B3%95%E3%81%AB%E5%9F%BA%E3%81%A5%E3%81%8F%E8%A1%A8%E8%A8%98",
                    "https://note.com/haccoba/n/n48a9ad45d07f"],
    },
    "pukupuku": {
        "drink": "酒蔵に併設した角打ちで飲める（公式noteの取扱店一覧）。",
        "buy": "酒蔵併設の角打ちでボトルを扱っている。自社のオンラインストアは置いていない。",
        "tour": None,
        "address": None,
        "access": None,
        "caution": "2024年秋に古民家を改装して開いた蔵。番地と営業の案内は公式に無いので、訪ねる前に公式SNSを見ておきたい。",
        "sources": ["https://note.com/pukupukubrewing/n/n052867015a09"],
    },
    "heiroku": {
        "drink": "醸造所のある古民家「日詰平井邸」のカフェ「喫茶喫酒」で、グラス単位の有料試飲（角打ち）ができる。",
        "buy": "日詰平井邸でボトルを買える。醸造所限定の酒もある。",
        "tour": "醸造家が案内する有料の酒蔵見学（約60分・試飲付き）。要予約。",
        "address": "岩手県紫波郡紫波町日詰字郡山駅246番地",
        "access": "JR紫波中央駅から徒歩15分",
        "caution": "日詰平井邸は国の重要文化財で、見学ツアー以外は醸造所付近に入れない。見学の前日から納豆・漬物・ヨーグルトなどの発酵食品を控えるよう案内がある。",
        "sources": ["https://www.hiraroku.com/access", "https://www.hiraroku.com/sakagurakengaku", "https://www.hiraroku.com/stay"],
    },
    "fermenteria": {
        "drink": "店頭で無料試飲ができ、造りたての生のクラフトサケ「サケベイビー」を店頭限定でカップ提供している（持ち帰り可）。",
        "buy": "火入れで日持ちするボトル商品や、ノンアルコールの麹ドリンクを販売。品ぞろえは時期で変わる。",
        "tour": "見学ツアーの案内はないが、店頭からガラス越しに、透明タンクで発酵する様子が見える。8Lから頼めるオリジナルの酒造りプランもある（事前相談）。",
        "address": "宮城県仙台市青葉区中央1-1-1 仙台駅1階 tekute dining",
        "access": "JR仙台駅の西口側1階「tekute dining」内",
        "caution": "店頭限定の新作は入れ替わりが早い。",
        "sources": ["https://fermenteria.co/pages/visit", "https://fermenteria.co/pages/original_sake_making"],
    },
    "mingura": {
        "drink": "醸造所の店内でクラフトどぶろくを飲める（公式note 2026年9月25日）。",
        "buy": "店頭でどぶろくを買える（同じ公式note）。オンラインショップもある。",
        "tour": "公式サイトでは、陶芸体験のように自分のお酒をつくる「素人醸造体験」を提供するとしている。日程・申し込み方法の案内はない。",
        "address": "岩手県大船渡市猪川町字久名畑4-6",
        "access": None,
        "caution": "公式サイトに営業日・営業時間の案内が見当たらない。訪ねる前に公式LINEか問い合わせフォームで聞いておきたい。",
        "sources": ["https://mingura-sake.com/", "https://note.com/minnano_sakagura/n/n49e7cb106df7"],
    },
    # ── 関東・新潟 ──
    "tsuchiura": {
        "drink": None,
        "buy": "醸造所（日下部ビル1階）で直売している。",
        "tour": "醸造工程の見学から試飲までの60〜90分のプログラム。要予約（公式の予約ページ）。",
        "address": "茨城県土浦市桜町1丁目6-16 日下部ビル1F",
        "access": "JR土浦駅西口から徒歩2分",
        "caution": "営業時間は予告なく変わる場合がある（公式）。",
        "sources": ["https://www.sake-ibaraki.com/access/", "https://prtimes.jp/main/html/rd/p/000000001.000182850.html"],
    },
    "yamane": {
        "drink": None,
        "buy": "赤沢醸造所に直売店がある。不定期営業で、営業日は公式サイトとXで告知。公式は、飯能市内の株式会社OHでの購入も案内している。",
        "tour": "「やまね酒造り学校」として、蔵見学・仕込み体験などを案内している（メールで予約）。",
        "address": "埼玉県飯能市赤沢223",
        "access": "飯能駅北口の国際興業バスで約30分「茶内」下車すぐ",
        "caution": "酒造りの状況によって、体験の予約を受けられないことがある。20歳未満は参加できず、中学生以下と妊娠中の人は入場できない。案内ページは2022年掲載のものなので、最新の受付状況は公式で見ておきたい。",
        "sources": ["https://yamaneshuzo.jp/",
                    "https://yamaneshuzo.jp/find/%e3%81%a9%e3%81%b6%e3%82%8d%e3%81%8f%e9%86%b8%e9%80%a0%e6%89%80/",
                    "https://yamaneshuzo.jp/2022/10/30/%e3%82%84%e3%81%be%e3%81%ad%e9%85%92%e9%80%a0%e3%82%8a%e5%ad%a6%e6%a0%a1/"],
    },
    "lagoon": {
        "drink": "酒蔵に併設した「LAGOON BREWERY Shop & Cafe」で、自社醸造のSAKEのテイスティングができる（しっかりした食事の提供はない）。",
        "buy": "併設のShopで、自社醸造のSAKEやオリジナルグッズを買える。",
        "tour": "Shop & Cafe の窓から発酵室を見るのは予約不要。蔵の中に入る見学（テイスティング付き・約1時間）は、メールで約1週間前までに相談する予約制。",
        "address": "新潟県新潟市北区前新田乙576-1",
        "access": "ビュー福島潟のとなり",
        "caution": "SAKE造りの都合で営業が急に変わることがある。内部見学の当日は、来る前に発酵食品や柑橘類をとらないよう案内がある（歯みがき・シャワー・着替えの後ならよい）。強い香りも控えたい。",
        "sources": ["https://www.lagoon-brewery.com/shop-cafe", "https://www.lagoon-brewery.com/brewery-tour",
                    "https://www.lagoon-brewery.com/company-access"],
    },
    "iyasaka": {
        "official": None,  # 公式サイトは公開前。蔵DBの official_url は紹介記事なので「公式」としてリンクしない
        "drink": None,
        "buy": None,
        "tour": "田植え・稲刈り（収穫祭）などのイベントを開いている。2026年9月12日の収穫祭では、希望者向けの蔵見学も予定に組まれていた（申し込み制・代表のnote）。",
        "tour_kind": "event",
        "address": "新潟県柏崎市石曽根1563-1",
        "access": None,
        "caution": "醸造所内の直売所・テイスティングスペースは、2026年8月時点で完成間近と報告されている（CAMPFIREの活動報告）。開店後はまずボトル販売のみで始め、テイスティングは準備が整い次第とのこと。開業したかは公式に確認できていないので、訪ねる前に問い合わせたい。",
        "sources": ["https://camp-fire.jp/projects/829438/activities", "https://note.com/ikko2535/n/n87beff1662c6",
                    "https://prtimes.jp/main/html/rd/p/000000002.000164820.html"],
    },
    # ── 東京 ──
    "konohanano": {
        "drink": "醸造所に併設した店「ALL (W)RIGHT -sake place-」で、自家醸造の酒のほか100種以上の日本酒を、和の肴と楽しめる。",
        "buy": "併設の店で醸造所のどぶろくを常時販売している（売り切れの場合あり）。",
        "tour": "営業時間内なら、ガラス越しに醸造の様子をいつでも見られる。説明を聞きたいときは事前に問い合わせ（醸造長が不在のこともある）。",
        "address": "東京都台東区浅草4丁目49-14 1F",
        "access": None,
        "caution": None,
        "sources": ["https://konohanano-brewery.com/allwrightsakeplace", "https://konohanano-brewery.com/"],
    },
    "heiwa-kabutocho": {
        "drink": "ブルワリーパブ形式の店で、造り手ができたてのどぶろくを出す。母体・平和酒造の「紀土」なども飲める。",
        "buy": "店内で物販がある（品目は公式に記載なし）。",
        "tour": None,
        "address": "東京都中央区日本橋兜町8番5号 1階 KITOKI",
        "access": None,
        "caution": "現金は使えず、キャッシュレス決済のみ（公式）。",
        "sources": ["https://www.heiwashuzou.co.jp/heiwa-doburoku-kabutocho", "https://www.heiwashuzou.co.jp/store-info"],
    },
    "tokyo-station": {
        "drink": "醸造所とテイスティングバーを併設した「はせがわ酒店 グランスタ東京店」で、完成から1週間ほどの時期に、生どぶろくを少量出している。",
        "buy": "併設のはせがわ酒店 グランスタ東京店で、瓶詰めの商品を買える。",
        "tour": "見学ツアーの案内はないが、コンコース側からガラス越しにタンクが見える（広場側の小窓からは甑も見える）。",
        "address": "東京都千代田区丸の内1-9-1 JR東日本東京駅構内B1",
        "access": "JR東京駅の改札内（地下1階）",
        "caution": "改札内の店なので、駅を利用しないときは入場券が要る。季節のフルーツどぶろくは季節限定。",
        "sources": ["https://www.tokyostation-sakebrewery.com/", "https://www.hasegawasaketen.com/shop.html"],
    },
    "ubu": {
        "drink": "醸造所に併設したカウンター7席の店で、その場で醸したできたてのどぶろく・クラフトサケを出す。",
        "buy": None,
        "tour": None,
        "address": "東京都港区新橋2-16-1 ニュー新橋ビル地下1階63号室",
        "access": "JR新橋駅SL広場から徒歩1分",
        "caution": "食事の時間帯は前日23時までの完全予約制。後半のバーの時間帯は予約なしで入れる（公式）。",
        "sources": ["https://shinbashi-sake-ubu.com/"],
    },
    # ── 関西 ──
    "happy-taro": {
        "drink": "醸造所のある「湖のスコーレ」内の店舗に、試飲スペース（HAKKO SALON）がある。",
        "buy": "湖のスコーレ内の店舗で、店でしか買えないクラフトどぶろくも扱っている（公式アクセスページ）。",
        "tour": "醸造所見学は完全予約制（2〜8名・約90分）。1人の場合は2名分の料金で受け付けている。申し込みは公式の問い合わせフォーム。",
        "address": "滋賀県長浜市元浜町13番29号 湖のスコーレ内",
        "access": "JR長浜駅から徒歩7分（専用駐車場なし）",
        "caution": "臨時の営業・休業はSNSで告知される。",
        "sources": ["https://happytaro.jp/access/", "https://happytaro.jp/tour/", "https://happytaro.jp/about/"],
    },
    "heiwa-namba": {
        "drink": "ブルワリーパブ形式の店で、できたてのどぶろくと、母体・平和酒造の「紀土」などを楽しめる。",
        "buy": "店内で物販がある（飲食とは別に物販の時間が設けられている）。",
        "tour": None,
        "address": "大阪府大阪市中央区難波5-1-5 大阪高島屋地下1階西ゾーン",
        "access": None,
        "caution": "大阪高島屋の中の店で、定休日は高島屋に準じる。",
        "sources": ["https://www.heiwashuzou.co.jp/heiwa-doburoku-namba", "https://www.heiwashuzou.co.jp/store-info"],
    },
    "adachi-noujo": {
        "drink": "富田団地1階の醸造所と立ち飲みバーが一体になった「酒蔵Bar」で飲める（@DIME 2025年6月14日の記事。公式サイトには飲食の案内がない）。",
        "buy": "公式ショップの特定商取引法の表記に、醸造所の販売場が載っている。",
        "tour": None,
        "address": "大阪府高槻市牧田町7番55-109号",
        "access": None,
        "caution": "公式サイトに飲食・来店の詳しい案内は無い（特定商取引法の表記に、営業時間と定休日の記載はある）。訪ねる前に問い合わせたい。",
        "sources": ["https://shop.adachi-noujo.com/law", "https://shop.adachi-noujo.com/about", "https://dime.jp/genre/1979641/"],
    },
    "hakutsuru-sakecraft": {
        "official": "https://www.hakutsuru.co.jp/community/shiryo/",
        "drink": None,
        "buy": "できた酒は白鶴酒造資料館でだけ販売している。各回本数限定で、同じ酒質は造らない一期一会の酒。",
        "tour": "資料館は入館無料の自由見学で、ガラス越しに醸造設備や発酵中の醪が見られる。10名以上の団体はオンライン予約が要る。",
        "address": "兵庫県神戸市東灘区住吉南町4丁目5-5（白鶴酒造資料館内）",
        "access": "阪神住吉駅から徒歩約5分、JR住吉駅から徒歩約15分",
        "caution": "限定本数なので売り切れることがある。資料館の駐車場は、工事のため一部使えない（公式）。",
        "sources": ["https://www.hakutsuru.co.jp/community/shiryo/",
                    "https://www.hakutsuru.co.jp/corporate/news/detail/20240904105912.html",
                    "https://www.hakutsuru.co.jp/corporate/news/detail/news_file/file/20261007N-hakutsuru-sake-craft-no22-wine-grape2.pdf"],
    },
    # ── 九州 ──
    "librom": {
        "drink": "醸造所に併設したパブで、搾りたての酒と、麹や酒粕を使った料理を出す。酒造りの様子を目の前に見ながら飲める。",
        "buy": "公式の「飲めて買えるお店」一覧に、醸造所そのものが載っている。",
        "tour": None,
        "address": "福岡県福岡市中央区高砂一丁目21番27号 ボンフル高砂103",
        "access": "渡辺通駅・薬院駅から徒歩5分",
        "caution": "予約は電話かInstagramのDMで受け付けている（公式）。",
        "sources": ["https://librom.jp/", "https://librom.jp/pages/brewery", "https://librom.jp/pages/store",
                    "https://librom.jp/pages/shop-list"],
    },
    "dejima-hosendo": {
        "drink": "醸造所に隣接したカウンター6席の「でじま芳扇堂 BAR」で、出島で醸したどぶろくを長崎の季節の肴と楽しめる。",
        "buy": "公式の販売店一覧（2023年11月）に、でじま芳扇堂（出島町）が載っている。",
        "tour": None,
        "address": "長崎県長崎市出島町5-24",
        "access": "路面電車「出島」電停から徒歩1分",
        "caution": "席が少ないので予約がすすめられている。時間帯によって紹介制の貸切営業があり、未成年連れ・食事のみの利用はできない。酒造期は短縮営業・臨時休業がある。となりで醸造しているため、強い香水は控えるよう案内がある（公式）。",
        "sources": ["https://djm-hosendo.co.jp/store", "https://djm-hosendo.co.jp/company",
                    "https://djm-hosendo.co.jp/details?wgd=blog-6&wgdo=date-DESC"],
    },
    "amanosato": {
        "drink": None,
        "buy": None,
        "tour": "2025年に初めての蔵開きを開き、第2回を2026年11月1日に開く（入場無料）。ふだんの見学受付の案内はない。",
        "tour_kind": "event",
        "address": "福岡県田川郡福智町上野3109-38",
        "access": None,
        "caution": "ふだんの来訪・試飲の案内は公式に無い。蔵開きなどの催しは、公式の催しページで告知される。",
        "sources": ["https://amanosato-sake.com/", "https://amanosato-community.netlify.app/",
                    "https://amanosato-community.netlify.app/event.html?slug=kurafes"],
    },
    # ── 訪ねられる拠点がまだ無い蔵（記事の最後で触れる） ──
    "linne": {
        "official": "https://linne-co.jp/",
        "drink": None, "buy": None,
        "tour": "京都の飲食店などで、要予約のペアリングイベントを開いている。",
        "tour_kind": "event",
        "address": None, "access": None,
        "caution": "ほかの蔵の設備を借りて醸すファントムブリュワリーで、訪ねられる自社の拠点はまだ無い。公式ニュース（2026年9月25日）で、2027年春に京都の清水・五条坂エリアへ自社醸造所とレストランを開く予定と発表している。",
        "sources": ["https://linne-co.jp/about", "https://linne-co.jp/news/4zaD1Si9"],
    },
    "salmon-brewery": {
        "drink": None, "buy": None, "tour": None, "address": None, "access": None,
        "caution": "自前の酒蔵はまだ無く、近くの酒蔵の協力で醸している（公式「鮭酒造とは」）。訪ねられる施設は今のところ無い。",
        "sources": ["https://salmonbre.official.ec/about"],
    },
}

# 来訪の案内が公式に見つからなかった蔵（2026-10-28 の調査。記事で名前だけ挙げる）
NO_INFO = ["nondo", "sakenova", "nomu", "cultiva", "hajimari"]

# 記事での地域のまとまり（並び順もこの順）
REGIONS_VISIT = [
    ("tokyo", "東京", "TOKYO", ["konohanano", "heiwa-kabutocho", "tokyo-station", "ubu"]),
    ("kansai", "関西", "KANSAI", ["heiwa-namba", "adachi-noujo", "hakutsuru-sakecraft", "happy-taro"]),
    ("tohoku", "東北", "TOHOKU", ["haccoba", "pukupuku", "heiroku", "mingura", "fermenteria", "ine-to-agave"]),
    ("kanto", "関東・新潟", "KANTO / NIIGATA", ["tsuchiura", "yamane", "lagoon", "iyasaka"]),
    ("kyushu", "九州", "KYUSHU", ["librom", "dejima-hosendo", "amanosato"]),
]


def get(slug):
    return VISIT.get(slug)


def can_drink(slug):
    v = VISIT.get(slug) or {}
    return bool(v.get("drink"))


def anchor(slug):
    """記事「クラフトサケが飲める醸造所」の中で、その蔵が載っている節へのアンカー。"""
    for k, _ja, _en, slugs in REGIONS_VISIT:
        if slug in slugs:
            return f"#v-{k}"
    return "#v-notyet" if slug in VISIT else ""

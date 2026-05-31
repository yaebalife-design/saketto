# -*- coding: utf-8 -*-
"""saketto / ガイド記事（読みもの）生成スクリプト

2本のガイド記事を生成する。
  guide/craftsake-towa.html … 「クラフトサケとは」
  guide/nomikata.html       … 「クラフトサケの飲み方・楽しみ方」

世界観CSSは gen_axes_pages.py から流用し、記事用タイポを追加。
嘘ゼロ: 事実は一次ソース（国税庁基本通達・クラフトサケブリュワリー協会公式・
各蔵プレスリリース・日本酒造組合中央会・厚労省 等）で確認したもののみ。

実行: cd ツール/saketto_repo/tools && python gen_guides.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from gen_axes_pages import CSS as BASE_CSS  # 世界観CSSを流用

REPO_ROOT = Path(__file__).resolve().parent.parent  # saketto_repo/
OUT_DIR = REPO_ROOT / "guide"


# ────────────── 記事用 追加CSS ──────────────

EXTRA_CSS = """
.article { max-width:1100px; margin:0 auto; padding:0 2rem 2rem; }
.prose { max-width:760px; }
.prose p { font-size:1.02rem; color:var(--ink-soft); line-height:1.95; margin-bottom:1.4rem; }
.prose strong { color:var(--ink); font-weight:600; }
.prose a { color:var(--accent); text-decoration:none; border-bottom:1px solid var(--line-soft); transition:border-color .25s; }
.prose a:hover { border-bottom-color:var(--accent); }
.lead {
  font-family:'Shippori Mincho', serif; font-size:1.22rem; line-height:1.95;
  color:var(--ink); margin-bottom:1.8rem; font-weight:500;
}
.lead .accent { color:var(--accent); }

/* 用語グリッド */
.term-grid { display:grid; grid-template-columns:1fr; border:1px solid var(--line); margin:1rem 0 2.5rem; max-width:860px; }
@media (min-width:680px){ .term-grid { grid-template-columns:1fr 1fr; } }
.term { padding:1.2rem 1.4rem; border-bottom:1px solid var(--line); background:var(--bg); }
@media (min-width:680px){ .term { border-right:1px solid var(--line); } .term:nth-child(2n){ border-right:none; } }
.term:last-child{ border-bottom:none; }
.term__name { font-family:'Shippori Mincho',serif; font-weight:700; font-size:1.12rem; color:var(--ink); margin-bottom:.4rem; }
.term__name .en { font-family:'Cormorant Garamond',serif; font-style:italic; font-size:.82rem; color:var(--accent); margin-left:.5rem; letter-spacing:.05em; }
.term__desc { font-size:.92rem; color:var(--ink-soft); line-height:1.8; }

/* 温度テーブル */
.temp-table { width:100%; max-width:760px; border-collapse:collapse; margin:1rem 0 1rem; font-size:.92rem; }
.temp-table th, .temp-table td { text-align:left; padding:.7rem 1rem; border-bottom:1px solid var(--line-soft); }
.temp-table thead th {
  font-family:'Zen Kaku Gothic Antique',sans-serif; font-weight:700; letter-spacing:.1em;
  font-size:.75rem; text-transform:uppercase; color:var(--ink); border-bottom:1px solid var(--line);
}
.temp-table td.t { font-family:'Cormorant Garamond',serif; font-style:italic; color:var(--accent); white-space:nowrap; }
.temp-table tr.grp td { background:var(--bg-alt); font-family:'Shippori Mincho',serif; font-weight:600; color:var(--ink); letter-spacing:.04em; }
.temp-note { font-size:.82rem; color:var(--ink-mute); margin:0 0 2.2rem; max-width:760px; }

/* 注意ボックス */
.callout { background:var(--bg-alt); border-left:3px solid var(--accent); padding:1.3rem 1.5rem; margin:1.6rem 0 2.2rem; max-width:760px; }
.callout__label {
  font-family:'Zen Kaku Gothic Antique',sans-serif; font-weight:700; letter-spacing:.12em;
  font-size:.74rem; color:var(--accent); text-transform:uppercase; margin-bottom:.5rem;
}
.callout p { font-size:.9rem; color:var(--ink-soft); line-height:1.85; margin:0; }
.callout a { color:var(--accent); text-decoration:none; border-bottom:1px solid var(--line-soft); }

/* ハブへのリンク行 */
.pill-links { display:flex; flex-wrap:wrap; gap:.6rem; margin:1rem 0 2.5rem; }
.pill-links a {
  font-family:'Zen Kaku Gothic Antique',sans-serif; font-weight:500; font-size:.9rem;
  letter-spacing:.03em; color:var(--ink); text-decoration:none;
  border:1px solid var(--line); padding:.55rem 1.1rem; transition:border-color .25s,color .25s;
}
.pill-links a:hover { border-color:var(--accent); color:var(--accent); }
.pill-links a .arr { color:var(--accent); margin-left:.45rem; }

/* 蔵リンクのインライン群 */
.kura-links { display:flex; flex-wrap:wrap; gap:.55rem 1rem; margin:.2rem 0 2rem; max-width:760px; }
.kura-links a { font-family:'Shippori Mincho',serif; font-size:.98rem; color:var(--ink); text-decoration:none; border-bottom:1px solid var(--line); padding-bottom:1px; transition:color .25s,border-color .25s; }
.kura-links a:hover { color:var(--accent); border-bottom-color:var(--accent); }

/* 次に読む */
.readmore { display:grid; grid-template-columns:1fr; gap:1rem; margin:1.5rem 0 0; max-width:860px; }
@media (min-width:680px){ .readmore { grid-template-columns:1fr 1fr; } }
.readmore a { display:block; border:1px solid var(--line); padding:1.4rem 1.5rem; text-decoration:none; background:var(--bg); transition:background .3s,padding-left .3s; }
.readmore a:hover { background:var(--paper); padding-left:1.75rem; }
.readmore__k { font-family:'Cormorant Garamond',serif; font-style:italic; font-size:.8rem; color:var(--accent); letter-spacing:.08em; }
.readmore__t { font-family:'Shippori Mincho',serif; font-weight:700; font-size:1.18rem; color:var(--ink); margin-top:.3rem; line-height:1.4; }

.sub-h { font-family:'Shippori Mincho',serif; font-weight:700; font-size:1.3rem; color:var(--ink); margin:0 0 .8rem; letter-spacing:.02em; }
.sub-h .accent { color:var(--accent); }
"""


# ────────────── ページ骨格 ──────────────

def page_head(title, description):
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — saketto.</title>
<meta name="description" content="{description}">
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@300;400;500&family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<style>{BASE_CSS}{EXTRA_CSS}</style>
</head>
<body>
<main>
"""


def masthead(label, right_text):
    return f"""
  <div class="masthead">
    <div class="left">
      <a href="../index.html"><span class="accent-dot"></span>SAKETTO</a>
      <span>{label}</span>
    </div>
    <div class="right">{right_text}</div>
  </div>
"""


def hero(eyebrow, title_html, lede):
    return f"""
  <section class="hero">
    <div class="hero__eyebrow">{eyebrow}</div>
    <h1 class="hero__title">{title_html}</h1>
    <p class="hero__lede">{lede}</p>
  </section>

  <div class="divider">
    <div class="rule"></div>
    <div class="ornament outer"></div>
    <div class="ornament"></div>
    <div class="ornament outer"></div>
    <div class="rule"></div>
  </div>
"""


def section_meta(num, label_en):
    return f"""    <div class="section-meta">
      <span class="section-meta__num">No. {num}</span>
      <span class="section-meta__label">{label_en}</span>
      <span class="section-meta__rule"></span>
    </div>"""


def divider():
    return """
  <div class="divider">
    <div class="rule"></div>
    <div class="ornament outer"></div>
    <div class="ornament"></div>
    <div class="ornament outer"></div>
    <div class="rule"></div>
  </div>
"""


def footer():
    return """
  <footer>
    <div class="colophon">
      <div class="colophon__brand">
        <a href="../index.html">saketto<span class="dot">.</span></a>
        <small>— クラフトサケの図鑑</small>
      </div>
      <div class="colophon__notes">
        <strong>準備中</strong><span class="colophon__sep">／</span>
        2026年夏、本サイト公開予定<span class="colophon__sep">／</span>
        20歳未満の飲酒は法律で禁じられています<span class="colophon__sep">／</span>
        PR ／ アフィリエイトリンクを含みます<span class="colophon__sep">／</span>
        © 2026 saketto.
      </div>
    </div>
  </footer>

</main>
</body>
</html>
"""


# 協会加盟蔵（saketto収録分・確認日2026-05-31）
KURA = {
    "konohanano": "木花之醸造所",
    "haccoba": "haccoba",
    "librom": "LIBROM",
    "ine-to-agave": "稲とアガベ",
    "lagoon": "LAGOON BREWERY",
    "happy-taro": "ハッピー太郎醸造所",
    "heiroku": "平六醸造",
    "pukupuku": "ぷくぷく醸造",
    "adachi-noujo": "足立農醸",
}


def kura_link(slug):
    return f'<a href="../brewery/{slug}.html">{KURA.get(slug, slug)}</a>'


# ────────────── 記事①：クラフトサケとは ──────────────

def build_towa():
    members6 = "WAKAZE・木花之醸造所・haccoba・LIBROM・稲とアガベ・LAGOON BREWERY"
    kura_row = '<div class="kura-links">' + \
        "".join(kura_link(s) for s in
                ["konohanano", "haccoba", "librom", "ine-to-agave", "lagoon",
                 "happy-taro", "heiroku", "pukupuku", "adachi-noujo"]) + "</div>"

    terms = [
        ("花酛", "HANAMOTO", "東北地方に伝わる、幻とされるどぶろくの製法。ホップの近縁種「カラハナソウ（唐花草）」の煎じ汁で雑菌の繁殖を抑えながら醸す。現代に再現する蔵もある。"),
        ("水もと・菩提酛", "MIZUMOTO", "室町時代に奈良・正暦寺で生まれた、現存最古級の酒母づくり。生米を水に漬けて乳酸発酵させた酸性水「そやし水」を仕込みに使い、雑菌を抑える。"),
        ("生酛", "KIMOTO", "自然界の乳酸菌を取り込んで乳酸を生成させる、伝統的な酒母の育て方。手間はかかるが、力強く安定した発酵を生む。"),
        ("速醸", "SOKUJO", "明治末期に確立した比較的新しい製法。醸造用の乳酸を加えることで、短期間で安全に酒母を仕込める。"),
        ("白麹", "SHIRO-KOJI", "もとは焼酎づくりに使う麹。クエン酸を多く生み、レモンを思わせる爽やかな酸味とキレを酒に与える。"),
        ("全麹", "ZEN-KOJI", "蒸米を使わず、原料をすべて米麹で仕込む方法。泡盛に通じる手法で、甘みと旨みが濃密に引き出される。"),
        ("木桶仕込み", "KIOKE", "木桶を発酵の容器に用いる、伝統的な仕込み。蔵や桶ごとの個性が酒に映るとされる。"),
        ("ドライホッピング", "DRY HOPPING", "ビールづくり由来の技法。発酵の後半などにホップを加え、華やかな香りを引き出す。"),
        ("どぶろく", "DOBUROKU", "もろみを「こさない」酒。固液分離をしないため清酒の定義を外れ、その他の醸造酒に分類される。"),
    ]
    term_html = '<div class="term-grid">' + "".join(
        f'<div class="term"><div class="term__name">{n}<span class="en">{en}</span></div>'
        f'<div class="term__desc">{d}</div></div>' for n, en, d in terms) + "</div>"

    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "DEFINITION / 定義")}
      <div class="prose">
        <p class="lead">「クラフトサケ」とは、米と米麹を軸にしながら、ホップ・果実・ハーブといった<span class="accent">副原料</span>を自由に取り入れて醸す、新しいジャンルの酒。</p>
        <p>日本の酒税法では、「清酒（いわゆる日本酒）」は<strong>米・米麹・水を原料として発酵させ、もろみをこした</strong>もの——と定義される。原料に副原料を加えたり、もろみをこさなかったりすると、この清酒の定義を外れ、その多くは<strong>「その他の醸造酒」</strong>という区分に入る。</p>
        <p>つまりクラフトサケは、日本酒づくりの技術を土台にしながら、あえて「日本酒」という枠の<strong>外</strong>に出ることで生まれた酒。米と麹だけを濾さずに仕込む<strong>どぶろく</strong>も、ホップを効かせたホップサケや、果実を絡めた果実サケも、この同じ土俵の上にある。</p>
        <div class="callout">
          <div class="callout__label">ひとことメモ</div>
          <p>「その他の醸造酒」になるか別の区分になるかは、使う副原料の種類や量、製法によって個別に判定されます。saketto では各銘柄を、公式情報で確認できた範囲で分類しています。</p>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("02", "WHY NOW / なぜ今")}
      <div class="prose">
        <h2 class="sub-h">「日本酒の枠の外」で、<span class="accent">自由</span>に醸す</h2>
        <p>背景には、日本酒（清酒）の<strong>製造免許</strong>が新規には事実上交付されない、という事情がある。需給調整のもとで既存の枠が守られており、ゼロから日本酒蔵を興すのは極めて難しい。</p>
        <p>そこで近年の若い造り手たちは、比較的取得しやすい<strong>「その他の醸造酒」の製造免許</strong>で参入し、清酒の定義に縛られない発想——副原料を加える、全部を麹で仕込む、もろみを濾さない——で酒を醸し始めた。これがクラフトサケというムーブメントの源流になっている。</p>
        <p>先駆けとされるのが、2021年に福島県南相馬市小高で立ち上がった {kura_link("haccoba")} や、秋田県男鹿の {kura_link("ine-to-agave")}。彼らが切り拓いた道を、いま全国の蔵が思い思いのかたちで歩んでいる。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("03", "THE ASSOCIATION / 協会")}
      <div class="prose">
        <h2 class="sub-h">合言葉は、<span class="accent">「自由を、醸そう。」</span></h2>
        <p>2022年6月27日、6つの醸造所が手を組み<strong>「クラフトサケブリュワリー協会」（JAPAN CRAFT SAKE BREWERIES ASSOCIATION）</strong>が発足した。掲げるコピーは<strong>「自由を、醸そう。」</strong>。</p>
        <p>設立の目的は、<strong>①クラフトサケの醸造所を増やす ②知名度を高める ③日本酒とクラフトサケが共存できる未来をつくる</strong>——の3つ。設立メンバーは {members6} の6蔵だった。</p>
        <p>その後、加盟は少しずつ広がっている。本記事の確認時点（2026年5月31日）で協会公式サイトに名を連ねる蔵のうち、saketto に収録しているのは次の蔵。それぞれの物語は、各蔵のページから。</p>
        {kura_row}
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("04", "VOCABULARY / 醸造のことば")}
      <div class="prose">
        <p>クラフトサケのラベルや解説には、聞き慣れない醸造用語が並ぶ。代表的なことばを知っておくと、味わいの背景がぐっと立体的に見えてくる。</p>
      </div>
      {term_html}
      <div class="prose">
        <p>こうした製法や副原料の個性は、saketto では<a href="../genre/">ジャンル</a>や<a href="../subingredients/">副原料</a>の軸からも辿れる。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("05", "HOW TO EXPLORE / 探し方")}
      <div class="prose">
        <h2 class="sub-h">5つの軸から、<span class="accent">次の一本</span>へ</h2>
        <p>クラフトサケの面白さは、その多様さ。saketto では、25の蔵と120を超える銘柄を、5つの軸から横断的に探せる。気になる入り口から、次に出会う一本を見つけてほしい。</p>
        <div class="pill-links">
          <a href="../subingredients/">副原料から<span class="arr">→</span></a>
          <a href="../region/">地域から<span class="arr">→</span></a>
          <a href="../genre/">ジャンルから<span class="arr">→</span></a>
          <a href="../availability/">入手性から<span class="arr">→</span></a>
          <a href="../furusato/">ふるさと納税から<span class="arr">→</span></a>
        </div>
        <div class="readmore">
          <a href="nomikata.html">
            <div class="readmore__k">NEXT READING — 02</div>
            <div class="readmore__t">クラフトサケの飲み方・楽しみ方</div>
          </a>
          <a href="../index.html">
            <div class="readmore__k">BACK TO</div>
            <div class="readmore__t">saketto トップへ</div>
          </a>
        </div>
      </div>
    </section>

  </div>
"""
    html = page_head("クラフトサケとは — 米から生まれた、自由な酒",
                     "クラフトサケとは何か。酒税法上の「その他の醸造酒」という位置づけ、クラフトサケブリュワリー協会、花酛・白麹・全麹などの醸造用語まで、その全体像をやさしく解説します。")
    html += masthead("READING 01 — WHAT IS CRAFT SAKE", "A Field Guide")
    html += hero(
        "READING 01 — WHAT IS CRAFT SAKE",
        'クラフトサケとは。<br>米から生まれた、<span class="accent">自由な酒</span>。',
        "日本酒づくりの技術を土台に、あえて「日本酒」の枠の外へ。米と副原料で醸す新ジャンル「クラフトサケ」の成り立ちを、法律・歴史・醸造のことばからひもときます。")
    html += body
    html += footer()
    return html


# ────────────── 記事②：飲み方・楽しみ方 ──────────────

def build_nomikata():
    temp_rows = [
        ("grp", "冷やして — COLD", ""),
        ("", "雪冷え", "約5℃前後", "香りは控えめ、きりりと締まった口当たり"),
        ("", "花冷え", "約10℃", "繊細な味わい、香りが少しずつ開く"),
        ("", "涼冷え", "約15℃", "はっきりした冷たさに、華やかな香り"),
        ("grp", "常温で — ROOM", ""),
        ("", "冷や（常温）", "約15〜20℃", "「冷や」は本来この常温のこと。酒の素の表情が出る"),
        ("grp", "温めて — WARM", ""),
        ("", "人肌燗", "約35℃", "米と麹の香り、さらりとやわらかく"),
        ("", "ぬる燗", "約40℃", "香りがもっとも豊かにふくらむ"),
        ("", "あつ燗", "約50℃", "シャープに引き締まり、キレのある辛口に"),
    ]
    trows = ""
    for r in temp_rows:
        if r[0] == "grp":
            trows += f'        <tr class="grp"><td colspan="3">{r[1]}</td></tr>\n'
        else:
            trows += f'        <tr><td>{r[1]}</td><td class="t">{r[2]}</td><td>{r[3]}</td></tr>\n'

    pairings = [
        ("果実サケ", "FRUIT", "前菜、生ハム、フレッシュチーズ、サラダ。果実の甘酸っぱさが軽やかな一皿に寄り添う。"),
        ("ホップサケ", "HOP", "揚げ物、スパイスの効いた料理、エスニック。ホップのほろ苦さと香りが油やスパイスを受け止める。"),
        ("古典どぶろく", "DOBUROKU", "味噌・漬物などの発酵食品、鍋もの。米の旨みと酸が、滋味深い和の食卓と好相性とされる。"),
        ("全麹・濃醇タイプ", "FULL KOJI", "熟成チーズ、ナッツ、食後の一杯に。とろりと濃い甘旨味は、デザート感覚でも楽しめる。"),
        ("白麹・酸の効いた酒", "ACIDIC", "脂ののった料理をさっぱりと。クエン酸由来の爽やかな酸が後味を切り替える。"),
    ]
    pair_html = '<div class="term-grid">' + "".join(
        f'<div class="term"><div class="term__name">{n}<span class="en">{en}</span></div>'
        f'<div class="term__desc">{d}</div></div>' for n, en, d in pairings) + "</div>"

    body = f"""
  <div class="article">

    <section class="section">
{section_meta("01", "TEMPERATURE / 温度")}
      <div class="prose">
        <p class="lead">クラフトサケは、低アルコールのものから濃厚な原酒まで、<span class="accent">味わいの幅</span>がとても広い。まずは「冷や」で、その個性を確かめるのがおすすめ。</p>
        <p>日本酒には、温度帯ごとに風流な呼び名がある。クラフトサケも基本は同じ。冷やすと香りは締まりシャープに、温めると米や麹の旨みがふくらむ。同じ一本でも温度で表情が変わるので、少しずつ試してみてほしい。</p>
      </div>
      <table class="temp-table">
        <thead><tr><th>呼び名</th><th>目安</th><th>表情</th></tr></thead>
        <tbody>
{trows}        </tbody>
      </table>
      <p class="temp-note">※ 温度帯の呼称は日本酒造組合中央会による。℃はおおよその目安です。最適な温度は銘柄ごとに異なるため、各蔵のおすすめがあればそれを優先してください。</p>
    </section>
{divider()}
    <section class="section">
{section_meta("02", "STORAGE / 保存")}
      <div class="prose">
        <h2 class="sub-h">生酒・にごりは、<span class="accent">冷蔵</span>が基本</h2>
        <p>クラフトサケには、加熱処理（火入れ）をしていない<strong>生酒</strong>や、澱（おり）を残した<strong>にごり・おりがらみ</strong>が多い。これらは繊細で変化しやすいため、<strong>冷蔵庫での保管</strong>が基本。火入れされたタイプも、品質を保つなら冷暗所が安心。</p>
        <p>開栓後は風味が変わりやすいので、なるべく早めに飲み切るのがおすすめ。発酵由来のガスを含むにごりやどぶろくは、<strong>開栓時に噴き出す</strong>ことがある。冷やしてから、ゆっくり少しずつ開けるのがコツ。</p>
        <div class="callout">
          <div class="callout__label">ボトルの表示を確認</div>
          <p>「要冷蔵」「開栓注意」などの表示は、その酒の個性そのもの。ラベルや蔵の案内に従うのが、いちばんおいしく楽しむ近道です。</p>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("03", "GLASS & STYLE / 器と飲み方")}
      <div class="prose">
        <h2 class="sub-h">ワイングラスでも、<span class="accent">ソーダ割り</span>でも</h2>
        <p>香りの華やかなクラフトサケは、<strong>ワイングラス</strong>に注ぐと立ちのぼる香りを楽しめる。フルーティーな果実サケやホップサケは、とくにグラス選びで印象が変わる。</p>
        <p>味のしっかりした銘柄なら、<strong>ロック</strong>や<strong>ソーダ割り</strong>も楽しい。クラフトサケは自由な酒。炭酸で割れば食前酒のように軽やかになり、低アルコールのタイプは飲み慣れていない人の入り口にもなる。にごりやどぶろくは、ぬる燗にすると米の甘みがふっくら開く。</p>
        <p>どんなスタイルが合うかは、銘柄ごとに蔵がおすすめを示していることも多い。迷ったら、<strong>蔵の推奨に従う</strong>のがいちばん。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("04", "PAIRING / 料理と合わせる")}
      <div class="prose">
        <p>副原料や製法の個性は、合わせる料理を選ぶ楽しみにもつながる。あくまで一例だが、ジャンル別の相性の目安を挙げてみる。</p>
      </div>
      {pair_html}
      <div class="prose">
        <p>こうしたジャンルは、saketto の<a href="../genre/">ジャンル</a>や<a href="../subingredients/">副原料</a>の軸から探せる。気分や食卓に合わせて、一本を選んでみてほしい。</p>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("05", "AVAILABILITY / 入手性で選ぶ")}
      <div class="prose">
        <h2 class="sub-h">「<span class="accent">限定流通</span>」も、味のうち</h2>
        <p>クラフトサケは少量仕込みが多く、通販で気軽に買えるものから、特約店だけ、現地だけ、抽選——と入手の難しさもさまざま。その希少さ自体が、この酒の魅力のひとつ。saketto では入手性の軸からも逆引きできる。</p>
        <div class="pill-links">
          <a href="../availability/">入手性から探す<span class="arr">→</span></a>
          <a href="../furusato/">ふるさと納税から探す<span class="arr">→</span></a>
        </div>
      </div>
    </section>
{divider()}
    <section class="section">
{section_meta("06", "PLEASE NOTE / お願い")}
      <div class="prose">
        <div class="callout">
          <div class="callout__label">楽しむ前に</div>
          <p><strong>20歳未満の飲酒は法律で禁じられています。</strong>　お酒を飲んだら運転はできません（飲酒運転は法律で禁止されています）。妊娠中・授乳期の飲酒は、おなかの赤ちゃんに影響することがあります。適量を守り、自分のペースで楽しんでください。</p>
        </div>
        <div class="readmore">
          <a href="craftsake-towa.html">
            <div class="readmore__k">READING — 01</div>
            <div class="readmore__t">そもそもクラフトサケとは？</div>
          </a>
          <a href="../index.html">
            <div class="readmore__k">BACK TO</div>
            <div class="readmore__t">saketto トップへ</div>
          </a>
        </div>
      </div>
    </section>

  </div>
"""
    html = page_head("クラフトサケの飲み方・楽しみ方",
                     "クラフトサケをもっとおいしく。温度帯の選び方、生酒・にごりの保存、ワイングラスやソーダ割りといったスタイル、料理とのペアリングまで、自由な酒の楽しみ方を解説します。")
    html += masthead("READING 02 — HOW TO ENJOY", "A Field Guide")
    html += hero(
        "READING 02 — HOW TO ENJOY",
        'クラフトサケの<span class="accent">飲み方</span>。<br>自由だから、おいしい。',
        "冷やでも燗でも、グラスでもソーダ割りでも。温度・保存・スタイル・ペアリングのちょっとしたコツで、クラフトサケはもっと豊かに楽しめます。")
    html += body
    html += footer()
    return html


# ────────────── 実行 ──────────────

def main():
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "craftsake-towa.html").write_text(build_towa(), encoding="utf-8")
    (OUT_DIR / "nomikata.html").write_text(build_nomikata(), encoding="utf-8")
    print("OK ガイド記事生成: guide/craftsake-towa.html, guide/nomikata.html")


if __name__ == "__main__":
    main()

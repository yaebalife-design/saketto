# -*- coding: utf-8 -*-
"""saketto 法的ページ生成：運営者情報 / プライバシーポリシー / 免責事項・広告表記。
gen_axes_pages の世界観CSSを流用し、ナビ・フッターは絶対パス（ルート設置のため）。

連絡先メールは非公開（社長方針）。お問い合わせはフォームで対応。
CONTACT_FORM_URL に Google フォーム等のURLを入れるとボタン化される（空なら「準備中」表示）。

実行: cd ツール/saketto_repo/tools && python gen_legal.py
"""
import sys, os
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from gen_axes_pages import CSS
from site_common import head_extra

REPO_ROOT = Path(__file__).resolve().parent.parent

# お問い合わせフォームURL（odanngochアカウントのGoogleフォーム等）。空なら「準備中」表示。
CONTACT_FORM_URL = ""

UPDATED = "2026年5月31日"

# 法的ページ用の追加CSS（読み物寄りの静的ページ）
STATIC_CSS = """
.static { max-width: 760px; margin: 0 auto; padding: 56px 28px 96px; position: relative; z-index: 1; }
.breadcrumb { font-size: 12px; letter-spacing: .08em; color: var(--ink-mute); margin-bottom: 28px; }
.breadcrumb a { color: var(--ink-mute); text-decoration: none; }
.breadcrumb a:hover { color: var(--accent); }
.breadcrumb span { margin: 0 .5em; color: var(--line); }
.static h1 { font-family: 'Shippori Mincho', serif; font-size: 30px; font-weight: 600; letter-spacing: .04em; color: var(--ink); margin-bottom: 10px; }
.static .updated { font-size: 12px; color: var(--ink-mute); letter-spacing: .06em; margin-bottom: 36px; padding-bottom: 24px; border-bottom: 1px solid var(--line-soft); }
.static h2 { font-family: 'Zen Kaku Gothic Antique', sans-serif; font-size: 18px; font-weight: 700; color: var(--ink); margin: 40px 0 14px; padding-left: 14px; border-left: 3px solid var(--accent); }
.static h3 { font-family: 'Zen Kaku Gothic Antique', sans-serif; font-size: 15px; font-weight: 700; color: var(--ink-soft); margin: 26px 0 10px; }
.static p { font-size: 15px; line-height: 1.95; color: var(--ink-soft); margin-bottom: 14px; }
.static ul { margin: 0 0 16px 1.2em; }
.static li { font-size: 15px; line-height: 1.9; color: var(--ink-soft); margin-bottom: 6px; }
.static a { color: var(--accent); text-decoration: none; border-bottom: 1px solid var(--line); }
.static a:hover { color: var(--accent-deep); border-bottom-color: var(--accent); }
.static table { width: 100%; border-collapse: collapse; margin: 8px 0 20px; font-size: 14px; }
.static th, .static td { text-align: left; padding: 12px 14px; border: 1px solid var(--line-soft); vertical-align: top; }
.static th { width: 30%; background: var(--bg-alt); font-weight: 700; color: var(--ink); white-space: nowrap; }
.static td { color: var(--ink-soft); }
.contact-btn { display: inline-block; margin-top: 8px; padding: 13px 26px; background: var(--accent); color: var(--paper); font-family: 'Zen Kaku Gothic Antique', sans-serif; font-weight: 500; letter-spacing: .06em; text-decoration: none; border: 1px solid var(--accent); }
.contact-btn:hover { background: var(--accent-deep); border-color: var(--accent-deep); color: var(--paper); }
.contact-pending { display: inline-block; margin-top: 8px; padding: 13px 26px; border: 1px dashed var(--line); color: var(--ink-mute); font-size: 14px; }
@media (max-width: 600px) { .static { padding: 40px 20px 72px; } .static h1 { font-size: 25px; } .static th { width: 38%; } }
"""

MASTHEAD = """
  <div class="masthead">
    <div class="left">
      <a class="brand-link" href="/index.html"><span class="accent-dot"></span>SAKETTO</a>
      <span>{label}</span>
    </div>
    <nav class="masthead-nav" aria-label="ナビ">
      <a href="/subingredients/">副原料</a>
      <a href="/index.html#breweries">蔵</a>
      <a href="/region/">地域</a>
      <a href="/genre/">ジャンル</a>
      <a href="/guide/">読みもの</a>
    </nav>
  </div>
"""

FOOTER = """
  <footer>
    <div class="colophon">
      <div class="colophon__brand">
        <a href="/index.html">saketto<span class="dot">.</span></a>
        <small>— クラフトサケの図鑑</small>
      </div>
      <div class="colophon__notes">
        <a href="/about.html">運営者情報</a><span class="colophon__sep">／</span>
        <a href="/privacy.html">プライバシーポリシー</a><span class="colophon__sep">／</span>
        <a href="/disclaimer.html">免責事項・広告表記</a><span class="colophon__sep">／</span>
        20歳未満の飲酒は法律で禁じられています<span class="colophon__sep">／</span>
        PR ／ アフィリエイトリンクを含みます<span class="colophon__sep">／</span>
        © 2026 saketto.
      </div>
    </div>
  </footer>
"""


def page(title, label, description, body):
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — saketto.</title>
<meta name="description" content="{description}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@300;400;500&family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<style>{CSS}{STATIC_CSS}</style>
{head_extra(prefix="")}
</head>
<body>
<main>
{MASTHEAD.format(label=label)}
  <article class="static">
    <div class="breadcrumb"><a href="/index.html">トップ</a><span>›</span>{title}</div>
{body}
  </article>
{FOOTER}
</main>
</body>
</html>
"""


def contact_block():
    if CONTACT_FORM_URL:
        return f'<p><a class="contact-btn" href="{CONTACT_FORM_URL}" target="_blank" rel="noopener">お問い合わせフォームへ →</a></p>'
    return '<p><span class="contact-pending">お問い合わせフォームは準備中です</span></p>'


# ────────────── プライバシーポリシー ──────────────
PRIVACY_BODY = f"""
  <h1>プライバシーポリシー</h1>
  <p class="updated">最終更新日: {UPDATED}</p>

  <p>saketto（さけっと／以下、「当サイト」）は、利用者の個人情報の保護を重要な責務と考え、以下の方針に基づき個人情報の適切な取り扱いに努めます。</p>

  <h2>1. 個人情報の取得について</h2>
  <p>当サイトは、原則として個人情報を直接取得することはありません。お問い合わせ等を通じて任意でご提供いただいた個人情報は、お問い合わせへの対応以外の目的では使用いたしません。</p>

  <h2>2. アクセス解析ツールについて</h2>
  <p>当サイトでは、サイトの利用状況を把握するために Google アナリティクス（Google Analytics）を使用しています。このツールはトラフィックデータの収集のために Cookie を使用しています。収集されるデータは匿名であり、個人を特定するものではありません。</p>
  <p>この機能は Cookie を無効にすることで収集を拒否できますので、お使いのブラウザの設定をご確認ください。詳細は以下をご参照ください。</p>
  <ul>
    <li><a href="https://marketingplatform.google.com/about/analytics/terms/jp/" target="_blank" rel="noopener">Google アナリティクス利用規約</a></li>
    <li><a href="https://policies.google.com/privacy?hl=ja" target="_blank" rel="noopener">Google プライバシーポリシー</a></li>
  </ul>

  <h2>3. 広告配信について</h2>
  <p>当サイトでは、第三者配信の広告サービス（Google AdSense、もしもアフィリエイト〔楽天市場 等〕、Amazonアソシエイト・プログラム、各ふるさと納税ポータルのアフィリエイト等）を利用しています。</p>
  <p>これらの広告配信事業者は、利用者の興味に応じた広告を表示するため、当サイトや他のサイトへのアクセスに関する情報（氏名・住所・メールアドレス・電話番号は含まれません）を Cookie を使用して収集する場合があります。</p>
  <p>Google AdSense における Cookie の利用、パーソナライズ広告の無効化（オプトアウト）については以下をご参照ください。</p>
  <ul>
    <li><a href="https://policies.google.com/technologies/ads?hl=ja" target="_blank" rel="noopener">広告 — ポリシーと規約（Google）</a></li>
  </ul>

  <h3>Amazonアソシエイト・プログラム</h3>
  <p>当サイトは、Amazon.co.jp を宣伝しリンクすることによって紹介料を獲得できる手段を提供することを目的に設定されたアフィリエイトプログラムである、Amazonアソシエイト・プログラムの参加者です。</p>

  <h2>4. 第三者への情報提供</h2>
  <p>当サイトは、利用者の個人情報を法令で定められた場合を除き、本人の同意なしに第三者へ開示・提供することはありません。</p>

  <h2>5. 免責事項</h2>
  <p>当サイトに掲載されている情報の正確性には万全を期しておりますが、利用者が当サイトの情報を用いて行う一切の行為について、当サイトは責任を負うものではありません。詳しくは<a href="/disclaimer.html">免責事項・広告表記</a>をご確認ください。</p>

  <h2>6. プライバシーポリシーの変更</h2>
  <p>当サイトは、必要に応じて本ポリシーの内容を変更することがあります。変更後のプライバシーポリシーは、当サイトに掲載した時点から効力を生じるものとします。</p>

  <h2>7. お問い合わせ</h2>
  <p>本ポリシーに関するお問い合わせは、<a href="/about.html">運営者情報</a>ページに記載の窓口までお願いいたします。</p>
"""

# ────────────── 免責事項・広告表記 ──────────────
DISCLAIMER_BODY = f"""
  <h1>免責事項・広告表記</h1>
  <p class="updated">最終更新日: {UPDATED}</p>

  <h2>1. アフィリエイト・広告表記</h2>
  <p>当サイト（saketto）は、以下のアフィリエイトプログラム・広告サービスに参加しており、リンク経由で商品・サービスが購入された場合、運営者が紹介料を受け取ることがあります。</p>
  <ul>
    <li>もしもアフィリエイト（楽天市場 等）</li>
    <li>Amazonアソシエイト・プログラム</li>
    <li>各ふるさと納税ポータルのアフィリエイト（楽天ふるさと納税 等）</li>
    <li>Google AdSense</li>
  </ul>
  <p>銘柄ページ等の「楽天市場で探す」などのボタン・リンクは、上記プログラムの広告リンクです。リンクをクリックして遷移した先で商品・サービスを購入・寄附した場合、運営者に一定の紹介料が支払われる仕組みです。</p>
  <p>※ 紹介料の有無は、利用者が支払う商品・サービスの価格・寄附額に影響を与えるものではありません。</p>

  <h2>2. 掲載画像について</h2>
  <p>当サイトのヒーロー画像・副原料や地域の雰囲気を表す画像の一部は、AI生成を含む<strong>イメージ画像</strong>です。特定の蔵（醸造所）の建物・敷地・施設の写真ではありません。各蔵の正確な外観・所在地等は、各蔵の公式サイト・公式SNS等でご確認ください。</p>

  <h2>3. 掲載情報の正確性について</h2>
  <p>当サイトは、各蔵の公式サイト・各コンテストの公式発表・各ふるさと納税ポータル等の公開情報をもとに、一次情報の確認を基本方針として、可能な限り正確な情報の掲載に努めています。ただし以下の点にご注意ください。</p>
  <ul>
    <li>情報は予告なく変更される場合があります（価格・度数・容量・副原料・在庫・受賞情報 等）</li>
    <li>クラフトサケはロット（仕込み）ごとに度数・容量・価格が変動することがあります</li>
    <li>各銘柄の最新の販売価格・在庫状況は、リンク先の販売ページでご確認ください</li>
    <li>蔵の見学・営業時間・予約方法等は、必ず各蔵の公式情報でご確認ください</li>
    <li>掲載の参考価格は記載時点のものです</li>
  </ul>

  <h2>4. 当サイトの利用について</h2>
  <p>当サイトに掲載されている情報を利用したことによって生じたいかなる損害についても、当サイトは責任を負いかねます。商品の購入・寄附・蔵への訪問・その他の判断は、利用者ご自身の責任において行ってください。</p>

  <h2>5. 飲酒に関するご注意</h2>
  <ul>
    <li><strong>20歳未満の飲酒は法律で禁止されています</strong></li>
    <li>未成年者・妊産婦の方への酒類の販売・提供は固くお断りしています</li>
    <li>飲酒運転は法律で禁止されています</li>
    <li>飲酒は適量を守り、節度を持ってお楽しみください</li>
    <li>体質的にお酒に弱い方、健康上の理由で飲酒を控えている方は無理に飲酒しないでください</li>
  </ul>

  <h2>6. 著作権について</h2>
  <p>当サイト掲載のテキスト・構成・デザインの著作権は、特に明記がない限り運営者に帰属します。各蔵名・銘柄名・ロゴ等の商標・著作物は、各権利者に帰属します。引用・参考にした情報については、可能な範囲で出典を明示しています。当サイト掲載情報の無断転載・複製は固くお断りいたします。</p>

  <h2>7. リンクについて</h2>
  <p>当サイトは原則リンクフリーです。リンクの際のご連絡は不要です。ただし、当サイトの内容を誤解させるような形でのリンクはご遠慮ください。</p>

  <h2>8. 外部リンクについて</h2>
  <p>当サイトから移動する外部リンク先の情報・商品・サービスについて、当サイトは一切の責任を負いません。各リンク先の利用規約・プライバシーポリシーに従ってご利用ください。</p>

  <h2>9. 免責事項の変更について</h2>
  <p>当サイトは、必要に応じて本免責事項の内容を変更することがあります。変更後の内容は、当サイトに掲載した時点から効力を生じるものとします。</p>
"""

# ────────────── 運営者情報 ──────────────
ABOUT_BODY = f"""
  <h1>運営者情報</h1>
  <p class="updated">最終更新日: {UPDATED}</p>

  <h2>サイト概要</h2>
  <table>
    <tr><th>サイト名</th><td>saketto（さけっと／クラフトサケDB）</td></tr>
    <tr><th>URL</th><td>https://saketto.com</td></tr>
    <tr><th>運営開始</th><td>2026年</td></tr>
    <tr><th>サイトの目的</th><td>米と副原料で醸す新ジャンルの酒「クラフトサケ」の蔵と銘柄を、副原料・蔵・地域・ジャンルの4軸から横断的に探せる無料データベースを提供する</td></tr>
    <tr><th>運営者</th><td>saketto 編集部</td></tr>
    <tr><th>連絡先</th><td>下記「お問い合わせ」をご覧ください</td></tr>
  </table>

  <h2>本サイトについて</h2>
  <p>saketto は、日本国内で造られているクラフトサケ（酒税法上の「その他の醸造酒」「清酒以外の発酵酒」に当たる、米＋副原料の自由な酒）の情報を集約し、副原料・蔵・地域・ジャンルなど複数の切り口から横断検索できる無料データベースです。</p>
  <p>各蔵の公開情報、各コンテストの公表情報、各ふるさと納税ポータルの公開情報をもとに編集し、情報の更新には自動化（プログラムによる生成・整形）を活用しています。最終的な公開の判断は運営者（人間）が行っています。</p>

  <h2>編集方針 — 一次ソース主義</h2>
  <ul>
    <li>蔵名・所在地・創業・銘柄名・度数・容量・副原料は、各蔵の公式情報で確認したうえで掲載しています</li>
    <li>受賞歴は、各コンテストの公式発表・各蔵の公式リリースに基づく事実情報を引用しています</li>
    <li>確認できない情報は掲載しない、または出典・確認日を明示する方針です</li>
    <li>蔵の建物等の写真は原則として無断掲載せず、雰囲気を表すイメージ画像で代替しています</li>
    <li>価格・在庫・度数等の最新情報は、各蔵・各販売サイトでご確認ください</li>
  </ul>

  <h2>収益について</h2>
  <p>当サイトはアフィリエイトプログラム・広告サービスを利用しており、リンク経由で商品が購入・寄附された場合に運営者が報酬を受け取ることがあります。詳しくは<a href="/disclaimer.html">免責事項・広告表記</a>をご確認ください。</p>

  <h2>お問い合わせ</h2>
  <p>掲載情報の修正依頼・新規の蔵／銘柄の掲載依頼・その他のお問い合わせは、お問い合わせフォームよりお願いいたします。</p>
  {contact_block()}

  <h2>関連ページ</h2>
  <ul>
    <li><a href="/privacy.html">プライバシーポリシー</a></li>
    <li><a href="/disclaimer.html">免責事項・広告表記</a></li>
  </ul>
"""


def main():
    pages = [
        ("privacy.html", "プライバシーポリシー", "PRIVACY",
         "saketto（クラフトサケDB）のプライバシーポリシー。アクセス解析・広告配信・Cookieの取り扱いについて。", PRIVACY_BODY),
        ("disclaimer.html", "免責事項・広告表記", "DISCLAIMER",
         "saketto（クラフトサケDB）の免責事項とアフィリエイト・広告表記、掲載情報の正確性・飲酒に関する注意。", DISCLAIMER_BODY),
        ("about.html", "運営者情報", "ABOUT",
         "saketto（クラフトサケDB）の運営者情報・編集方針（一次ソース主義）・お問い合わせ。", ABOUT_BODY),
    ]
    for fname, title, label, desc, body in pages:
        (REPO_ROOT / fname).write_text(page(title, label, desc, body), encoding="utf-8")
        print(f"  {fname}  ({title})")
    if not CONTACT_FORM_URL:
        print("  ※ お問い合わせフォームURL未設定（about.htmlは「準備中」表示）。URL取得後 CONTACT_FORM_URL に設定して再生成")


if __name__ == "__main__":
    main()

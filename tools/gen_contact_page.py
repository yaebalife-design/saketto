# -*- coding: utf-8 -*-
"""contact.html ＝ お問い合わせフォームを生成する（saketto版）。

■ 設計（Gin-DB で確立した方式をそのまま移植。社長指示「gin-dbと同じ感じで」）
  ブラウザが話す相手は **saketto.com/api/contact だけ**。
  送信内容は Cloudflare Pages Functions が受けて Googleスプレッドシートに1行追記する。
  送信先（シートID・サービスアカウント鍵）は Cloudflare の暗号化シークレットの中にしか
  存在せず、HTML にも JS にも リポジトリにも一切書かない。
  ページのソースを見ても、スクレイピングしても、宛先は分からない。
  mailto: リンクも置かない（メールアドレス収集ボットの主な標的なので）。

■ スパム対策（受け口 functions/api/contact.js 側と対）
  1. ハニーポット：人には見えない項目。入力があったら捨てる
  2. 表示から3秒未満の送信は機械とみなす
  3. Cloudflare Turnstile は環境変数を入れれば有効になる（未設定なら素通し）

■ 送信者のメールアドレスは「任意」
  返信が要らない指摘（誤字の報告など）で個人情報を出させないため。

■ 世界観は saketto（米色×墨×発酵朱・角丸なし・Shippori Mincho）。
  Gin-DB のCSSは流用せず、gen_legal.py の静的ページの骨格に合わせている。

実行: cd ツール/saketto_repo/tools && python gen_contact_page.py
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from gen_axes_pages import CSS
from gen_legal import MASTHEAD, FOOTER, STATIC_CSS
from site_common import head_extra, seo_head, breadcrumb, SITE_URL

REPO_ROOT = Path(__file__).resolve().parent.parent

# フォームの選択肢。**functions/api/contact.js の KINDS と完全一致させること**
# （食い違うと 422 bad_kind で弾かれ、問い合わせが届かない）
KINDS = [
    ("掲載情報の誤り", "度数・容量・価格・副原料・所在地などが実際と違う"),
    ("新規の蔵・銘柄の掲載依頼", "掲載されていない蔵・銘柄を載せてほしい"),
    ("画像・引用について", "画像や引用の取り下げ・差し替えのご依頼"),
    ("その他", "上記にあてはまらないもの"),
]

# フォーム用CSS。saketto の世界観に合わせ、角丸は使わず直線で構成する。
PAGE_CSS = """
.ct__lead { font-size: 15px; line-height: 1.95; color: var(--ink-soft); margin-bottom: 8px; }
.ct__note { font-size: 13px; line-height: 1.9; color: var(--ink-soft);
  background: var(--bg-alt); border-left: 3px solid var(--accent);
  padding: 1.1rem 1.3rem; margin: 22px 0 32px; }
.ct__note strong { color: var(--ink); }
.ct-field { margin-bottom: 24px; }
.ct-field > label { display: block; font-family: 'Zen Kaku Gothic Antique', sans-serif;
  font-weight: 700; font-size: 14px; letter-spacing: .04em; color: var(--ink); margin-bottom: 7px; }
.ct-req { font-size: 11px; font-weight: 700; color: var(--paper); background: var(--accent);
  padding: 2px 8px; margin-left: 8px; vertical-align: 1px; letter-spacing: .08em; }
.ct-opt { font-size: 11px; font-weight: 400; color: var(--ink-mute); margin-left: 8px; letter-spacing: .08em; }
.ct-help { font-size: 12.5px; color: var(--ink-mute); line-height: 1.75; margin-bottom: 8px; }
.ct-field input[type=text], .ct-field input[type=email], .ct-field input[type=url],
.ct-field textarea {
  width: 100%; font-family: inherit; font-size: 16px;  /* 16px未満はiOSで自動ズームする */
  padding: 12px 14px; border: 1px solid var(--line); background: var(--paper);
  color: var(--ink); -webkit-appearance: none; border-radius: 0; line-height: 1.8;
}
.ct-field textarea { min-height: 190px; resize: vertical; }
.ct-field input:focus, .ct-field textarea:focus {
  outline: 2px solid var(--accent); outline-offset: 1px; border-color: var(--accent); }
.ct-field [aria-invalid="true"] { border-color: var(--accent); }
.ct-err { display: none; font-size: 12.5px; color: var(--accent-deep); font-weight: 700; margin-top: 6px; }
.ct-err.is-shown { display: block; }
.ct-kinds { display: grid; gap: 9px; }
/* .ct-field > label より詳細度を上げないと display:block に負けて縦に割れる */
.ct-field .ct-kind { display: flex; gap: 11px; align-items: flex-start;
  border: 1px solid var(--line); padding: 13px 15px; cursor: pointer; background: var(--paper);
  margin-bottom: 0; font-weight: 400; font-size: inherit; transition: border-color .2s; }
.ct-kind:hover { border-color: var(--accent); }
.ct-kind input { margin-top: 3px; accent-color: var(--accent); width: 18px; height: 18px; flex-shrink: 0; }
.ct-kind:has(input:checked) { border-color: var(--accent); background: var(--bg-alt); }
.ct-kind:has(input:focus-visible) { outline: 2px solid var(--accent); outline-offset: 2px; }
.ct-kind > span { display: block; min-width: 0; }
.ct-kind b { display: block; font-family: 'Shippori Mincho', serif; font-size: 15px;
  margin-bottom: 3px; color: var(--ink); font-weight: 700; }
.ct-kind b + span { display: block; font-size: 12.5px; color: var(--ink-mute); line-height: 1.7; }
.ct-hp { position: absolute; left: -9999px; width: 1px; height: 1px; overflow: hidden; }
.ct-submit { appearance: none; border: 1px solid var(--accent); cursor: pointer;
  font-family: 'Zen Kaku Gothic Antique', sans-serif; font-weight: 700; font-size: 15px;
  letter-spacing: .1em; padding: 15px 44px; min-height: 52px;
  background: var(--accent); color: var(--paper); transition: background .2s; }
.ct-submit:hover:not(:disabled) { background: var(--accent-deep); border-color: var(--accent-deep); }
.ct-submit:disabled { opacity: .55; cursor: progress; }
.ct-submit:focus-visible { outline: 2px solid var(--ink); outline-offset: 3px; }
.ct-status { margin-top: 20px; font-size: 14px; line-height: 1.9; padding: 0; border: 1px solid transparent; }
.ct-status.is-shown { padding: 15px 17px; }
.ct-status.is-ok { background: var(--bg-alt); border-color: var(--accent); color: var(--ink); font-weight: 700; }
.ct-status.is-ng { background: var(--bg-alt); border-color: var(--accent); color: var(--accent-deep); font-weight: 700; }
.ct-done { display: none; }
.ct-done.is-shown { display: block; }
.is-sent .ct-form { display: none; }
.ct-foot { font-size: 12px; color: var(--ink-mute); line-height: 1.85; margin-top: 24px; }
@media (max-width: 640px) { .ct-submit { width: 100%; } }
"""

# JSは f-string の外で組み立てる（{ } が置換フィールドとして解釈されて壊れるため）
PAGE_JS = """
<script>
(function(){
  var form = document.getElementById('ct-form');
  if(!form) return;
  var btn    = document.getElementById('ct-submit');
  var status = document.getElementById('ct-status');
  var wrap   = document.getElementById('ct-wrap');
  var shownAt = Date.now();

  function setErr(id, msg){
    var el = document.getElementById(id);
    if(!el) return;
    el.textContent = msg || '';
    el.classList.toggle('is-shown', !!msg);
    var field = document.getElementById(id.replace('-err',''));
    if(field) field.setAttribute('aria-invalid', msg ? 'true' : 'false');
  }
  function say(kind, msg){
    status.className = 'ct-status is-shown ' + (kind === 'ok' ? 'is-ok' : 'is-ng');
    status.textContent = msg;
  }

  form.addEventListener('submit', function(e){
    e.preventDefault();
    setErr('ct-message-err',''); setErr('ct-email-err','');
    status.className = 'ct-status'; status.textContent = '';

    var kindEl = form.querySelector('input[name=kind]:checked');
    var message = form.message.value.trim();
    var email = form.email.value.trim();

    if(!kindEl){ say('ng','お問い合わせの種類をお選びください。'); return; }
    if(message.length < 10){
      setErr('ct-message-err','10文字以上でご記入ください。');
      form.message.focus(); return;
    }
    if(email && !/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)){
      setErr('ct-email-err','メールアドレスの形式をご確認ください。');
      form.email.focus(); return;
    }

    btn.disabled = true;
    var originalLabel = btn.textContent;
    btn.textContent = '送信中…';

    fetch('/api/contact', {
      method: 'POST',
      headers: {'content-type':'application/json'},
      body: JSON.stringify({
        kind: kindEl.value,
        name: form.name.value,
        email: email,
        url: form.url.value,
        message: message,
        // ハニーポット。欄名を website にすると、ブラウザやパスワード管理ソフトが
        // 「URLの入力欄」と判断して勝手に埋めることがある（autocomplete="off" は
        // 無視されることが多い）。埋まると正当な問い合わせが黙って捨てられるので、
        // 自動入力のヒューリスティクスが反応しない名前にしてある。
        hp: form.ct_ref2.value,
        elapsed: Date.now() - shownAt
      })
    }).then(function(r){
      return r.json().then(function(d){ return {ok: r.ok, d: d}; });
    }).then(function(res){
      if(res.ok && res.d && res.d.ok){
        wrap.classList.add('is-sent');
        document.getElementById('ct-done').classList.add('is-shown');
        document.getElementById('ct-done').focus();
      } else {
        say('ng', (res.d && res.d.message) || '送信に失敗しました。時間をおいてお試しください。');
        btn.disabled = false; btn.textContent = originalLabel;
      }
    }).catch(function(){
      say('ng','通信に失敗しました。電波状況をご確認のうえ、もう一度お試しください。');
      btn.disabled = false; btn.textContent = originalLabel;
    });
  });
})();
</script>
"""


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def build():
    title = "お問い合わせ"
    path = "/contact.html"
    desc = ("saketto の掲載内容の誤りのご指摘、新規の蔵・銘柄の掲載依頼、画像・引用に関する"
            "ご連絡はこちらのフォームからお送りいただけます。返信が不要な場合、"
            "メールアドレスの入力は任意です。")

    kinds_html = "\n".join(
        f'''          <label class="ct-kind">
            <input type="radio" name="kind" value="{esc(k)}"{' checked' if i == 0 else ''}>
            <span><b>{esc(k)}</b><span>{esc(d)}</span></span>
          </label>''' for i, (k, d) in enumerate(KINDS)
    )

    seo = seo_head(path, title, desc, og_type="website", jsonld=[
        {"@context": "https://schema.org/", "@type": "ContactPage",
         "name": "お問い合わせ", "description": desc, "url": SITE_URL + "/contact",
         "isPartOf": {"@type": "WebSite", "name": "saketto", "url": SITE_URL + "/"}},
        breadcrumb([("トップ", "/"), ("お問い合わせ", path)]),
    ])

    body = f"""
  <h1>お問い合わせ</h1>
  <p class="updated">掲載内容の修正・掲載依頼はこちらから</p>

  <p class="ct__lead">
    掲載内容の誤りのご指摘、新規の蔵・銘柄の掲載依頼などをお送りいただけます。<br>
    saketto は各蔵の公式発表を一次ソースとして掲載しており、事実と異なる記載が判明した場合は、
    確認のうえ速やかに訂正または取り下げます。
  </p>

  <div class="ct__note">
    <strong>蔵・販売店の方へ</strong><br>
    掲載の停止・修正のご依頼は、種類で「掲載情報の誤り」または「画像・引用について」を選び、
    該当ページのURLを添えてお送りください。内容を確認のうえ対応し、修正の場合はページに反映します。<br><br>
    <strong>いただいた情報の扱い</strong><br>
    お名前・メールアドレスの入力は任意です。<strong>返信が不要な場合は空欄のままお送りいただけます。</strong>
    ご記入いただいた場合も、お問い合わせへの回答以外の目的では使用しません。
    詳しくは<a href="/privacy.html">プライバシーポリシー</a>をご覧ください。
  </div>

  <div id="ct-wrap">

    <div class="ct-done" id="ct-done" tabindex="-1" role="status">
      <div class="ct-status is-shown is-ok" style="font-size:15px;">
        送信しました。ありがとうございます。<br>
        <span style="font-weight:400;font-size:14px;">
          内容を確認のうえ対応します。返信先をご記入いただいた場合でも、
          すべてのお問い合わせに個別の返信をお約束できるものではありません。あらかじめご了承ください。
        </span>
      </div>
      <p style="margin-top:22px;">
        <a href="/index.html">トップページへ戻る</a>
        ／ <a href="/brewery/">蔵から探す</a>
      </p>
    </div>

    <form class="ct-form" id="ct-form" novalidate>

      <div class="ct-field">
        <label id="ct-kind-label">お問い合わせの種類<span class="ct-req">必須</span></label>
        <div class="ct-kinds" role="radiogroup" aria-labelledby="ct-kind-label">
{kinds_html}
        </div>
      </div>

      <div class="ct-field">
        <label for="ct-url">対象ページのURL<span class="ct-opt">任意</span></label>
        <p class="ct-help">誤りのご指摘の場合、どのページかを教えていただけると確認が早くなります。</p>
        <input type="url" id="ct-url" name="url" autocomplete="off" placeholder="https://saketto.com/brand/...">
      </div>

      <div class="ct-field">
        <label for="ct-message">お問い合わせ内容<span class="ct-req">必須</span></label>
        <p class="ct-help">できるだけ具体的にご記入ください（例：「度数が13%と書かれていますが、公式サイトでは15%です」）。</p>
        <textarea id="ct-message" name="message" required minlength="10" maxlength="4000"
          aria-describedby="ct-message-err"></textarea>
        <p class="ct-err" id="ct-message-err" role="alert"></p>
      </div>

      <div class="ct-field">
        <label for="ct-name">お名前・団体名<span class="ct-opt">任意</span></label>
        <input type="text" id="ct-name" name="name" autocomplete="organization" maxlength="100">
      </div>

      <div class="ct-field">
        <label for="ct-email">返信先メールアドレス<span class="ct-opt">任意</span></label>
        <p class="ct-help">返信をご希望の場合のみご記入ください。空欄でも送信できます。</p>
        <input type="email" id="ct-email" name="email" autocomplete="email" maxlength="200"
          aria-describedby="ct-email-err">
        <p class="ct-err" id="ct-email-err" role="alert"></p>
      </div>

      <!-- スパム対策。人には見えない。入力があった送信は捨てる -->
      <div class="ct-hp" aria-hidden="true">
        <label for="ct-ref2">この欄は入力しないでください</label>
        <input type="text" id="ct-ref2" name="ct_ref2" tabindex="-1" autocomplete="off" inputmode="none">
      </div>

      <button type="submit" class="ct-submit" id="ct-submit">送信する</button>
      <p class="ct-status" id="ct-status" role="status" aria-live="polite"></p>

      <p class="ct-foot">
        20歳未満の方からの商品に関するお問い合わせにはお答えできません。<br>
        個別の銘柄の在庫・購入方法については、各蔵または販売店へ直接お問い合わせください。
      </p>
    </form>

  </div>
"""

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — saketto.</title>
<meta name="description" content="{desc}">
{seo}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@400;500&family=Cormorant+Garamond:ital,wght@0,400;1,400&display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@400;500&family=Cormorant+Garamond:ital,wght@0,400;1,400&display=swap" media="print" onload="this.media=&#39;all&#39;">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;700&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Noto+Sans+JP:wght@400;500&family=Cormorant+Garamond:ital,wght@0,400;1,400&display=swap"></noscript>
<style>{CSS}{STATIC_CSS}{PAGE_CSS}</style>
{head_extra(prefix="")}
</head>
<body>
<main>
{MASTHEAD.format(label="CONTACT — お問い合わせ")}
  <nav class="crumbs" aria-label="現在地">
    <a href="/index.html">トップ</a><span class="crumbs__sep">／</span>
    <span aria-current="page">お問い合わせ</span>
  </nav>
  <article class="static">
{body}
  </article>
{FOOTER}
</main>
{PAGE_JS}
</body>
</html>
"""


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    html = build()
    out = REPO_ROOT / "contact.html"
    out.write_text(html, encoding="utf-8")
    print(f"  contact.html  (お問い合わせフォーム / {len(html.encode('utf-8')) / 1024:.1f} KB)")
    print("  ※ 送信先は Cloudflare のシークレット（SHEETS_ID / SHEETS_TAB /")
    print("     GOOGLE_SA_EMAIL / GOOGLE_SA_KEY）とD1バインディング DB で設定する")


if __name__ == "__main__":
    main()

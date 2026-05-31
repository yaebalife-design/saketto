/* saketto 年齢確認ゲート — 自己完結（スタイル内包・絵文字なし・SVGアイコン）
   世界観：米色×墨×発酵朱、Shippori Mincho。localStorage で一度確認すれば再表示しない。 */
(function () {
  var KEY = 'saketto_age_verified';
  var verified = false;
  try { verified = localStorage.getItem(KEY) === '1'; } catch (e) {}
  if (verified) return;

  var STYLE = ''
    + '.sk-age{position:fixed;inset:0;z-index:99999;display:flex;align-items:center;'
    + 'justify-content:center;padding:24px;background:#F5F0E7;'
    + 'background-image:radial-gradient(ellipse 1.5px 2.2px at 18% 22%,rgba(184,73,58,.05) 60%,transparent 70%),'
    + 'radial-gradient(ellipse 1.2px 1.8px at 67% 38%,rgba(139,115,85,.05) 60%,transparent 70%),'
    + 'radial-gradient(ellipse 1.5px 2.3px at 42% 71%,rgba(26,23,23,.035) 60%,transparent 70%);'
    + 'background-size:64px 64px,96px 96px,80px 80px;'
    + 'font-family:"Noto Sans JP",sans-serif;color:#16100E;'
    + 'opacity:1;transition:opacity .4s ease;}'
    + '.sk-age.sk-age--hidden{opacity:0;pointer-events:none;}'
    + '.sk-age__box{max-width:460px;width:100%;background:#FAF6ED;'
    + 'border:1px solid #C0B69E;padding:48px 36px 36px;text-align:center;'
    + 'box-shadow:0 18px 50px rgba(26,23,23,.12);}'
    + '.sk-age__mark{display:block;margin:0 auto 22px;}'
    + '.sk-age__label{font-family:"Cormorant Garamond",serif;font-size:13px;'
    + 'letter-spacing:.42em;text-transform:uppercase;color:#7A6447;margin-bottom:6px;}'
    + '.sk-age__brand{font-family:"Shippori Mincho",serif;font-size:22px;font-weight:600;'
    + 'letter-spacing:.18em;color:#16100E;margin-bottom:28px;}'
    + '.sk-age__brand b{color:#A8351F;font-weight:600;}'
    + '.sk-age h2{font-family:"Shippori Mincho",serif;font-size:21px;font-weight:600;'
    + 'line-height:1.7;margin-bottom:16px;color:#16100E;}'
    + '.sk-age p{font-size:14px;line-height:1.9;color:#3D3633;margin-bottom:26px;}'
    + '.sk-age__btns{display:flex;flex-direction:column;gap:12px;margin-bottom:24px;}'
    + '.sk-age__btn{font-family:"Zen Kaku Gothic Antique",sans-serif;font-size:15px;'
    + 'font-weight:500;padding:15px 20px;border:1px solid #C0B69E;background:transparent;'
    + 'color:#16100E;cursor:pointer;letter-spacing:.06em;transition:background .2s,color .2s,border-color .2s;}'
    + '.sk-age__btn--yes{background:#A8351F;border-color:#A8351F;color:#FAF6ED;}'
    + '.sk-age__btn--yes:hover{background:#862719;border-color:#862719;}'
    + '.sk-age__btn--no:hover{background:#EDE5D2;border-color:#7A6447;}'
    + '.sk-age__notice{display:flex;gap:8px;align-items:flex-start;text-align:left;'
    + 'font-size:12px;line-height:1.8;color:#635C57;border-top:1px solid #D6CCB3;'
    + 'padding-top:18px;margin-bottom:0;}'
    + '.sk-age__notice svg{flex:0 0 auto;margin-top:2px;}'
    + '@media(max-width:480px){.sk-age__box{padding:38px 24px 28px;}.sk-age h2{font-size:19px;}}';

  // SVG：枡（木桶）を象った確認マーク。朱の線で世界観に合わせる。
  var MARK = '<svg class="sk-age__mark" width="46" height="46" viewBox="0 0 46 46" '
    + 'fill="none" stroke="#A8351F" stroke-width="1.4" aria-hidden="true">'
    + '<path d="M9 14 L37 14 L33 38 L13 38 Z"/>'
    + '<path d="M9 14 L13 38 M37 14 L33 38" opacity="0"/>'
    + '<path d="M6 14 L40 14" stroke-width="1.6"/>'
    + '<path d="M23 21 L23 31 M18 26 L28 26" stroke-width="1.2"/></svg>';

  var WARN = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" '
    + 'stroke="#A8351F" stroke-width="1.6" aria-hidden="true">'
    + '<path d="M12 3 L22 20 L2 20 Z"/><path d="M12 9 L12 14" stroke-width="1.8"/>'
    + '<circle cx="12" cy="17" r="0.6" fill="#A8351F" stroke="none"/></svg>';

  var html = ''
    + '<div class="sk-age" id="skAge" role="dialog" aria-modal="true" aria-labelledby="skAgeTitle">'
    + '  <div class="sk-age__box">'
    + MARK
    + '    <div class="sk-age__label">Craft Sake Database</div>'
    + '    <div class="sk-age__brand">saketto<b>.</b></div>'
    + '    <h2 id="skAgeTitle">あなたは20歳以上ですか</h2>'
    + '    <p>本サイトは米と副原料で醸すクラフトサケを紹介するデータベースです。<br>'
    + '       20歳未満の方の閲覧はご遠慮ください。</p>'
    + '    <div class="sk-age__btns">'
    + '      <button class="sk-age__btn sk-age__btn--yes" id="skAgeYes">はい、20歳以上です</button>'
    + '      <button class="sk-age__btn sk-age__btn--no" id="skAgeNo">いいえ</button>'
    + '    </div>'
    + '    <p class="sk-age__notice">' + WARN
    + '      <span>20歳未満の飲酒は法律で禁止されています。お酒は適量を守り、'
    + '      妊娠中・授乳期の飲酒はおやめください。</span></p>'
    + '  </div>'
    + '</div>';

  function init() {
    var style = document.createElement('style');
    style.textContent = STYLE;
    document.head.appendChild(style);

    var wrap = document.createElement('div');
    wrap.innerHTML = html;
    var gate = wrap.firstChild;
    document.body.appendChild(gate);
    document.documentElement.style.overflow = 'hidden';

    document.getElementById('skAgeYes').addEventListener('click', function () {
      try { localStorage.setItem(KEY, '1'); } catch (e) {}
      gate.classList.add('sk-age--hidden');
      document.documentElement.style.overflow = '';
      setTimeout(function () { if (gate && gate.parentNode) gate.parentNode.removeChild(gate); }, 450);
    });

    document.getElementById('skAgeNo').addEventListener('click', function () {
      window.location.replace('https://www.google.com/');
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

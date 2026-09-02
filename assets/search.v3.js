/* saketto サイト内検索（全ページ共通）
   - マストヘッドの検索ボタンから開くパネル。トップの検索窓があるページではそちらも動く。
   - インデックスは /assets/search-index.json（ルート絶対パスなので階層に依存しない）
   - カタカナ→ひらがな正規化つき。キーボード操作（↑↓/Enter/Esc）に対応。
   - v3: 検索結果の描画をエスケープするようにした（インデックスに & や < を含む
     銘柄名が入っても崩れない）。トップページはヒーローに大きな検索窓があるため、
     マストヘッドへの検索窓の注入をやめた（スタイル未定義の素のinputが出ていた）。 */
(function () {
  var INDEX_URL = '/assets/search-index.json';
  var data = null, requested = false;

  function norm(s) {
    // カタカナをひらがなへ寄せ、全角英数を半角へ
    return String(s || '').toLowerCase().replace(/[ァ-ヶ]/g, function (c) {
      return String.fromCharCode(c.charCodeAt(0) - 0x60);
    }).replace(/[Ａ-Ｚａ-ｚ０-９]/g, function (c) {
      return String.fromCharCode(c.charCodeAt(0) - 0xFEE0);
    });
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function load(cb) {
    if (data) { cb(); return; }
    if (requested) return;
    requested = true;
    fetch(INDEX_URL).then(function (r) { return r.json(); }).then(function (j) {
      data = j.map(function (x) { x._t = norm(x.t); x._n = norm(x.n); return x; });
      cb();
    }).catch(function () { requested = false; });
  }

  function search(q) {
    var nq = norm(q).trim();
    if (!nq) return [];
    var exact = [], partial = [];
    for (var i = 0; i < data.length; i++) {
      var d = data[i];
      if (d._n.indexOf(nq) !== -1) exact.push(d);
      else if (d._t.indexOf(nq) !== -1) partial.push(d);
    }
    return exact.concat(partial);
  }

  function wire(input, box) {
    if (!input || !box || input.dataset.skWired) return;
    input.dataset.skWired = '1';
    var cur = -1;

    function render() {
      var q = input.value.trim();
      if (!q) { box.hidden = true; box.innerHTML = ''; return; }
      if (!data) { load(render); return; }
      var hits = search(q);
      cur = -1;
      if (!hits.length) {
        box.innerHTML = '<div class="search-hit--none">該当が見つかりませんでした — 別の表記でお試しください</div>';
      } else {
        var shown = hits.slice(0, 8);
        box.innerHTML = shown.map(function (h) {
          return '<a class="search-hit" role="option" href="/' + esc(h.u) + '">' +
                 '<span class="search-hit__name">' + esc(h.n) + '</span>' +
                 '<span class="search-hit__meta">' + esc(h.m) + '</span></a>';
        }).join('') + (hits.length > shown.length
          ? '<div class="search-hit--none">ほか ' + (hits.length - shown.length) + ' 件</div>' : '');
      }
      box.hidden = false;
      input.setAttribute('aria-expanded', 'true');
    }

    function items() { return box.querySelectorAll('a.search-hit'); }

    input.addEventListener('focus', function () { load(render); });
    input.addEventListener('input', render);
    input.addEventListener('keydown', function (e) {
      var list = items();
      if (e.key === 'Escape') { box.hidden = true; input.setAttribute('aria-expanded', 'false'); return; }
      if (!list.length) return;
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        cur = e.key === 'ArrowDown' ? Math.min(cur + 1, list.length - 1) : Math.max(cur - 1, 0);
        for (var i = 0; i < list.length; i++) list[i].classList.toggle('is-active', i === cur);
        list[cur].scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'Enter') {
        if (cur >= 0) { e.preventDefault(); location.href = list[cur].getAttribute('href'); }
        else if (list.length) { e.preventDefault(); location.href = list[0].getAttribute('href'); }
      }
    });
    document.addEventListener('click', function (e) {
      if (!input.contains(e.target) && !box.contains(e.target)) {
        box.hidden = true; input.setAttribute('aria-expanded', 'false');
      }
    });
  }

  function markCurrentNav() {
    // 現在いる軸をナビ上で示す（aria-current はサイト全体で未使用だった）。
    // 例: /brand/... と /brewery/... は「蔵」、/guide/... は「読みもの」。
    var path = location.pathname;
    var map = [
      ['/subingredients', '../subingredients/'],
      ['/genre', '../genre/'],
      ['/region', '../region/'],
      ['/guide', '../guide/'],
      ['/brewery', '../brewery/'],
      ['/brand', '../brewery/'],
    ];
    var hit = null;
    for (var i = 0; i < map.length; i++) {
      if (path.indexOf(map[i][0]) === 0) { hit = map[i][1]; break; }
    }
    if (!hit) return;
    var links = document.querySelectorAll('.masthead-nav a');
    for (var j = 0; j < links.length; j++) {
      var href = links[j].getAttribute('href') || '';
      if (href === hit || href === hit.replace('../', '/')) {
        links[j].setAttribute('aria-current', 'page');
      }
    }
  }

  function init() {
    markCurrentNav();
    // トップページの大きい検索窓
    var hero = document.getElementById('skSearch');
    wire(hero, document.getElementById('skSearchResults'));

    // 全ページ共通：マストヘッドの検索（ヒーローに検索窓があるトップでは注入しない）
    var host = document.querySelector('.masthead');
    if (host && !hero && !document.getElementById('skNavSearch')) {
      var wrap = document.createElement('div');
      wrap.className = 'sk-navsearch';
      wrap.innerHTML =
        '<label class="sk-navsearch__label" for="skNavSearch">サイト内検索</label>' +
        '<input id="skNavSearch" type="search" autocomplete="off" role="combobox" ' +
        'aria-expanded="false" aria-controls="skNavSearchResults" ' +
        'placeholder="銘柄・蔵・副原料で探す" aria-label="サイト内検索">' +
        '<div class="sk-navsearch__results" id="skNavSearchResults" role="listbox" hidden></div>';
      host.appendChild(wrap);
      wire(document.getElementById('skNavSearch'), document.getElementById('skNavSearchResults'));
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();

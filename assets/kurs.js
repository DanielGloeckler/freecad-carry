/* =========================================================================
   Lernplattform-Logik: Kursleiste auf Kapitelseiten + Kursübersicht
   ========================================================================= */
(function () {
  'use strict';

  var KEYMAP = {
    'chassi.html':    { key: 'freecad-carry-chassi',    n: 6,  num: 1, title: 'Chassi' },
    'rad.html':       { key: 'freecad-carry-rad',       n: 6,  num: 2, title: 'Rad' },
    'lager.html':     { key: 'freecad-carry-lager',     n: 13,  num: 3, title: 'Radlager' },
    'achse.html':     { key: 'freecad-carry-achse',     n: 14,  num: 4, title: 'Achse & Schrauben' },
    'baugruppe.html': { key: 'freecad-carry-baugruppe', n: 10,  num: 5, title: 'Baugruppe' }
  };

  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function lsDel(k) { try { localStorage.removeItem(k); } catch (e) {} }
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function numOf(v) { var n = parseInt(v || '0', 10); return isNaN(n) ? 0 : n; }

  var file = (location.pathname.split('/').pop() || '').toLowerCase();
  var cfg = KEYMAP[file];

  /* ---------- Kapitelseite: Kursleiste + letzter Stand ---------- */
  if (cfg) {
    var fill = document.getElementById('kbarFill');
    var label = document.getElementById('kbarNum');
    var progressNum = document.getElementById('progressNum');

    function updateBar() {
      var m = /(\d+)\s*\/\s*(\d+)/.exec((progressNum && progressNum.textContent) || '');
      var cur = m ? parseInt(m[1], 10) : 1;
      var n = m ? parseInt(m[2], 10) : cfg.n;
      var done = document.querySelector('.final-badge') ? n : Math.min(cur - 1, n);
      if (done < 0) done = 0;
      if (fill) fill.style.width = Math.round(done / n * 100) + '%';
      if (label) label.textContent = done + ' von ' + n + ' erledigt';
      lsSet('freecad-carry-last', JSON.stringify({ file: file, step: cur, ts: Date.now() }));
    }

    if (progressNum && window.MutationObserver) {
      new MutationObserver(updateBar).observe(progressNum, {
        childList: true, characterData: true, subtree: true
      });
    }
    updateBar();
  }

  /* ---------- Kursübersicht ---------- */
  var cards = document.querySelectorAll('.kc');
  if (!cards.length) return;

  var total = 0, done = 0, firstOpen = null, allDone = true;

  for (var i = 0; i < cards.length; i++) {
    (function (card) {
      var f = card.getAttribute('data-file');
      var c = KEYMAP[f];
      if (!c) return;
      var n = c.n;
      var saved = clamp(numOf(lsGet(c.key)), 0, n);
      var pct = Math.round(saved / n * 100);

      var fbar = card.querySelector('.kc-fill');
      var count = card.querySelector('.kc-count');
      var badge = card.querySelector('.kc-badge');
      var open = card.querySelector('.kc-open');

      if (fbar) fbar.style.width = pct + '%';
      if (count) count.textContent = saved + ' von ' + n + ' erledigt';

      if (saved >= n) {
        if (badge) { badge.textContent = 'Abgeschlossen'; badge.className = 'kc-badge ok'; }
        if (open) { open.textContent = 'Wiederholen'; open.href = f; }
      } else if (saved > 0) {
        if (badge) { badge.textContent = 'In Arbeit'; badge.className = 'kc-badge prog'; }
        if (open) { open.textContent = 'Fortsetzen'; open.href = (f === 'chassi.html' || f === 'rad.html') ? f : (f + '?schritt=' + Math.min(saved + 1, n)); }
      } else {
        if (badge) { badge.textContent = 'Nicht begonnen'; badge.className = 'kc-badge new'; }
        if (open) { open.textContent = 'Starten'; open.href = f; }
      }

      total += n;
      done += saved;
      if (saved < n) {
        allDone = false;
        if (!firstOpen) firstOpen = { file: f, step: Math.min(saved + 1, n), title: c.title, num: c.num, saved: saved };
      }
    })(cards[i]);
  }

  var pctAll = total ? Math.round(done / total * 100) : 0;
  var ovFill = document.getElementById('ovFill');
  var ovPct = document.getElementById('ovPct');
  var ovText = document.getElementById('ovText');
  if (ovFill) ovFill.style.width = pctAll + '%';
  if (ovPct) ovPct.textContent = pctAll + ' %';
  if (ovText) ovText.textContent = done + ' von ' + total + ' Schritten erledigt';

  var continueBtn = document.getElementById('continueBtn');
  var lastText = document.getElementById('lastText');
  var last = null;
  try { last = JSON.parse(lsGet('freecad-carry-last') || 'null'); } catch (e) { last = null; }

  var target = null;
  if (last && KEYMAP[last.file]) {
    var lc = KEYMAP[last.file];
    var lsaved = clamp(numOf(lsGet(lc.key)), 0, lc.n);
    target = { file: last.file, step: clamp(last.step || 1, 1, lc.n) };
    var where = 'Kapitel ' + lc.num + ' · ' + lc.title + ' · Schritt ' + target.step;
    if (lsaved >= lc.n) where += ' (abgeschlossen)';
    if (lastText) lastText.textContent = 'Zuletzt geöffnet: ' + where;
  } else if (allDone) {
    if (lastText) lastText.textContent = 'Alle Kapitel abgeschlossen – super!';
  } else {
    if (lastText) lastText.textContent = 'Noch nicht begonnen – starte mit Kapitel 1.';
  }

  if (continueBtn) {
    if (allDone) {
      continueBtn.textContent = 'Kurs wiederholen';
      continueBtn.href = 'chassi.html';
    } else if (target) {
      continueBtn.textContent = 'Weiterlernen';
      continueBtn.href = (target.file === 'chassi.html' || target.file === 'rad.html') ? target.file : (target.file + (target.step > 1 ? '?schritt=' + target.step : ''));
    } else if (firstOpen) {
      continueBtn.textContent = firstOpen.saved > 0 ? 'Weiterlernen' : 'Kurs starten';
      continueBtn.href = (firstOpen.file === 'chassi.html' || firstOpen.file === 'rad.html') ? firstOpen.file : (firstOpen.file + (firstOpen.step > 1 ? '?schritt=' + firstOpen.step : ''));
    } else {
      continueBtn.textContent = 'Kurs starten';
      continueBtn.href = 'chassi.html';
    }
  }

  var reset = document.getElementById('resetBtn');
  if (reset) {
    reset.addEventListener('click', function () {
      if (!window.confirm('Fortschritt aller Kapitel wirklich zurücksetzen?')) return;
      for (var f in KEYMAP) if (KEYMAP.hasOwnProperty(f)) lsDel(KEYMAP[f].key);
      lsDel('freecad-carry-last');
      lsDel('freecad-grundkurs-v3');
      location.reload();
    });
  }
})();





/* Альянс Консалтинг — общие скрипты всех страниц: меню, кнопка «Связаться», появление блоков. */
(function () {
  var burger = document.getElementById('shBurger'), nav = document.getElementById('shNav');
  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { nav.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); });
    });
  }

  // «Связаться»: закрывать по клику мимо и по Esc
  var fab = document.querySelector('details.fab');
  if (fab) {
    document.addEventListener('click', function (e) { if (fab.open && !fab.contains(e.target)) fab.open = false; });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && fab.open) { fab.open = false; fab.querySelector('summary').focus(); }
    });
  }

  // Плавное появление блоков (если браузер умеет; иначе показываем сразу)
  var items = document.querySelectorAll('.reveal');
  if (items.length) {
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
      }, { threshold: 0.08 });
      items.forEach(function (el) { io.observe(el); });
    } else {
      items.forEach(function (el) { el.classList.add('in'); });
    }
  }
})();

/* плашка cookie: сайт использует Яндекс.Метрику */
(function () {
  var KEY = 'ak-cookie-ok';
  try { if (localStorage.getItem(KEY)) return; } catch (e) {}
  function show() {
    var d = document.createElement('div');
    d.className = 'ak-cookie'; d.setAttribute('role', 'region'); d.setAttribute('aria-label', 'Уведомление о cookie');
    d.innerHTML = '<p>Мы используем cookie и Яндекс.Метрику, чтобы сайт работал и становился удобнее. Продолжая пользоваться сайтом, вы соглашаетесь с <a href="/privacy.html">политикой обработки данных</a>.</p><button type="button" class="btn btn-sm">Понятно</button>';
    d.querySelector('button').onclick = function () { try { localStorage.setItem(KEY, '1'); } catch (e) {} d.remove(); document.body.classList.remove('cookie-open'); };
    document.body.appendChild(d); document.body.classList.add('cookie-open');
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', show); else show();
})();

/* 25.11.2026: телефон — «Показать ещё» у длинных списков, раскрытие карточек аудита */
(function () {
  function init() {
    document.querySelectorAll('.m-limit').forEach(function (g) {
      var n = g.children.length; if (n <= 3) return;
      var b = document.createElement('button'); b.type = 'button'; b.className = 'm-more';
      b.textContent = 'Показать ещё (' + (n - 3) + ')';
      b.onclick = function () { g.classList.add('open'); b.remove(); };
      g.parentNode.insertBefore(b, g.nextSibling);
    });
    document.querySelectorAll('.fold-cards > *').forEach(function (c) {
      c.addEventListener('click', function () { c.classList.toggle('open'); });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

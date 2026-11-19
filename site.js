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

(() => {
  'use strict';
  const labels = JSON.parse(document.getElementById('site-i18n').textContent);
  const interpolate = (text, values) => text.replace(/\{(\w+)\}/g, (_, key) => String(values[key] ?? ''));

  // Directory links work on project Pages; explicit index files also support file:.
  const languageLinks = [...document.querySelectorAll('.language-link')];
  languageLinks.forEach(link => { link.dataset.webHref = link.getAttribute('href'); });
  const updateLanguageLinks = () => languageLinks.forEach(link => {
    const target = location.protocol === 'file:' ? link.dataset.fileHref : link.dataset.webHref;
    const url = new URL(target, document.baseURI);
    url.hash = location.hash;
    link.href = url.href;
  });
  updateLanguageLinks();
  window.addEventListener('hashchange', updateLanguageLinks);
  languageLinks.forEach(link => link.addEventListener('click', updateLanguageLinks));

  const nav = document.getElementById('site-nav');
  const menu = document.querySelector('.menu-toggle');
  const menuLabel = menu.querySelector('.menu-label');
  const menuIcon = menu.querySelector('.menu-icon');
  const setMenu = open => {
    nav.classList.toggle('open', open);
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? labels.menu_close_label : labels.menu_open_label);
    menuLabel.textContent = open ? labels.menu_open : labels.menu_closed;
    menuIcon.textContent = open ? '×' : '☰';
  };
  const closeMenu = () => setMenu(false);
  menu.addEventListener('click', () => setMenu(menu.getAttribute('aria-expanded') !== 'true'));
  nav.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && nav.classList.contains('open')) {
      closeMenu();
      menu.focus();
    }
  });
  document.addEventListener('click', event => {
    if (!nav.contains(event.target) && !menu.contains(event.target)) closeMenu();
  });
  window.matchMedia('(min-width: 921px)').addEventListener('change', event => {
    if (event.matches) closeMenu();
  });

  const search = document.getElementById('publication-search');
  const year = document.getElementById('publication-year');
  const rows = [...document.querySelectorAll('.publication')];
  const count = document.querySelector('.result-count');
  const empty = document.querySelector('.empty-state');
  const showAll = document.getElementById('show-all');
  let expanded = false;
  const render = () => {
    const query = search.value.trim().toLocaleLowerCase();
    const matching = rows.filter(row =>
      (year.value === 'all' || row.dataset.year === year.value) &&
      row.dataset.search.includes(query));
    const isFiltered = Boolean(query) || year.value !== 'all';
    const visibleRows = isFiltered || expanded ? matching : matching.slice(0, 6);
    const visible = new Set(visibleRows);
    rows.forEach(row => { row.hidden = !visible.has(row); });
    const pattern = matching.length === 1 ? labels.count_singular : labels.count_plural;
    count.textContent = interpolate(pattern, {count: matching.length}) + (!isFiltered && !expanded && matching.length > visibleRows.length
      ? interpolate(labels.showing, {shown: visibleRows.length}) : '');
    empty.hidden = matching.length > 0;
    showAll.hidden = isFiltered || expanded || matching.length <= 6;
    if (!showAll.hidden) {
      showAll.replaceChildren(document.createTextNode(interpolate(labels.show_all, {count: matching.length}) + ' '));
      const arrow = document.createElement('span');
      arrow.setAttribute('aria-hidden', 'true');
      arrow.textContent = '↓';
      showAll.append(arrow);
    }
  };
  search.addEventListener('input', render);
  year.addEventListener('change', render);
  showAll.addEventListener('click', () => {
    expanded = true;
    render();
    rows[6]?.querySelector('a')?.focus({preventScroll: true});
  });
  render();

  if ('IntersectionObserver' in window) {
    const links = [...nav.querySelectorAll('a')];
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        links.forEach(link => {
          const active = link.hash === `#${entry.target.id}`;
          link.classList.toggle('active', active);
          if (active) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        });
      });
    }, {rootMargin: '-15% 0px -65% 0px'});
    document.querySelectorAll('main > section[id]').forEach(section => observer.observe(section));
  }
})();

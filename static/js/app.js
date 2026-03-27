/* ═══════════════════════════════════════
   SFAAM NEWS V2 — Shared JavaScript
   app.js
═══════════════════════════════════════ */

// ── Build Topbar ─────────────────────────────────────────────
function buildTopbar() {
  return `
    <div class="topbar">
      <div class="topbar-inner">
        <div style="display:flex;align-items:center;gap:10px;">
          <div class="brand-box">
            <a href="index.html">SFAAM NEWS</a>
          </div>
          <span class="brand-tagline">World News · Always Updated</span>
        </div>
        <div class="topbar-date">
          <span class="live-dot"></span>
          <span id="topDate"></span>
        </div>
      </div>
    </div>`;
}

// ── Build Nav ─────────────────────────────────────────────────
function buildNav(active) {
  const tabs = [
    { href: 'index.html',         label: '🏠 Home' },
    { href: 'world-news.html',    label: '🌐 World' },
    { href: 'usa-news.html',      label: '🇺🇸 USA' },
    { href: 'uk-news.html',       label: '🇬🇧 UK' },
    { href: 'pakistan-news.html', label: '🇵🇰 Pakistan' },
    { href: 'india-news.html',    label: '🇮🇳 India' },
    { href: 'about.html',         label: 'About' },
    { href: 'contact.html',       label: 'Contact' },
  ];
  const links = tabs.map(t =>
    `<a href="${t.href}" class="nav-tab ${t.href===active?'active':''}">${t.label}</a>`
  ).join('');
  return `
    <nav>
      <div class="nav-inner">
        ${links}
        <div class="nav-search">
          <form class="search-form" onsubmit="doSearch(event)">
            <input class="search-input" type="text" id="searchQ" placeholder="🔍 Search..."/>
            <button class="search-btn" type="submit">→</button>
          </form>
        </div>
      </div>
    </nav>`;
}

// ── Build Ticker ──────────────────────────────────────────────
function buildTicker(articles) {
  if (!articles || !articles.length) return '';
  const items = articles.slice(0, 8).map(a =>
    `<span class="tick-item" onclick="goArticle(${a.id})">${esc(a.title)}</span>
     <span class="tick-sep">●</span>`
  ).join('');
  return `
    <div class="ticker">
      <div class="ticker-inner">
        <div class="ticker-label">⚡ BREAKING</div>
        <div class="ticker-wrap">
          <div class="ticker-track">${items}${items}</div>
        </div>
      </div>
    </div>`;
}

// ── Build Footer ──────────────────────────────────────────────
function buildFooter() {
  return `
    <footer>
      <div class="footer-inner">
        <div>
          <div class="footer-brand-name">SFAAM NEWS</div>
          <div class="footer-txt">
            Your trusted source for world news.<br/>
            Updated every 5 minutes, 24/7.
          </div>
          <div class="social-icons" style="margin-top:14px;">
            <a href="#" class="social-icon" title="Facebook">f</a>
            <a href="#" class="social-icon" title="Instagram">📷</a>
            <a href="#" class="social-icon" title="Twitter/X">𝕏</a>
            <a href="https://wa.me/923431188853" class="social-icon" title="WhatsApp" target="_blank">💬</a>
            <a href="#" class="social-icon" title="YouTube">▶</a>
            <a href="#" class="social-icon" title="TikTok">🎵</a>
          </div>
        </div>
        <div class="footer-col">
          <h4>Pages</h4>
          <ul class="footer-links">
            <li><a href="index.html">🏠 Home</a></li>
            <li><a href="world-news.html">🌐 World News</a></li>
            <li><a href="usa-news.html">🇺🇸 USA News</a></li>
            <li><a href="uk-news.html">🇬🇧 UK News</a></li>
            <li><a href="pakistan-news.html">🇵🇰 Pakistan</a></li>
            <li><a href="india-news.html">🇮🇳 India</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>Contact</h4>
          <ul class="footer-links">
            <li><a href="about.html">About Us</a></li>
            <li><a href="contact.html">Contact</a></li>
            <li><a href="mailto:sfaamroy@gmail.com">📧 sfaamroy@gmail.com</a></li>
            <li><a href="https://wa.me/923431188853" target="_blank">💬 WhatsApp</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© ${new Date().getFullYear()} SFAAM NEWS. All rights reserved.</span>
        <span>Updated every 5 minutes</span>
      </div>
    </footer>`;
}

// ── Date Update ───────────────────────────────────────────────
function updateDate() {
  const el = document.getElementById('topDate');
  if (el) el.textContent = new Date().toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  });
}

// ── Go to Article Page ────────────────────────────────────────
function goArticle(id) {
  window.location.href = `article.html?id=${id}`;
}

// ── Search ────────────────────────────────────────────────────
function doSearch(e) {
  if (e) e.preventDefault();
  const q = document.getElementById('searchQ')?.value?.trim();
  if (q) window.location.href = `search.html?q=${encodeURIComponent(q)}`;
}

// ── Build Featured Section ────────────────────────────────────
function buildFeatured(articles, label) {
  if (!articles || articles.length < 3) return '';
  const [m, s1, s2] = articles;

  const mImg = m.image_url
    ? `<img class="feat-img" src="${esc(m.image_url)}" alt="${esc(m.title)}" loading="lazy" onerror="this.outerHTML='<div class=\\'feat-img-ph\\'>📰</div>'">`
    : `<div class="feat-img-ph">📰</div>`;

  const sideItem = (a) => {
    const sImg = a.image_url
      ? `<img class="feat-side-img" src="${esc(a.image_url)}" alt="${esc(a.title)}" loading="lazy" onerror="this.outerHTML='<div class=\\'feat-side-img-ph\\'>📰</div>'">`
      : `<div class="feat-side-img-ph">📰</div>`;
    return `
      <div class="feat-side-item" onclick="goArticle(${a.id})">
        ${sImg}
        <div class="cat-tag">SFAAM NEWS</div>
        <div class="h-sm">${esc(a.title)}</div>
        <span style="font-size:0.65rem;color:var(--muted)">${fmtDate(a.date)}</span>
      </div>`;
  };

  return `
    <div class="featured-box">
      <div class="section-label">⚡ ${label || 'Top Stories'}</div>
      <div class="featured-grid">
        <div class="feat-main" onclick="goArticle(${m.id})">
          ${mImg}
          <div class="feat-body">
            <div class="cat-tag">SFAAM NEWS · ${fmtDate(m.date)}</div>
            <div class="h-xl">${esc(m.title)}</div>
            <div class="summary">${esc(m.summary || '')}</div>
            <div class="read-more" style="margin-top:10px;">Read Full Story →</div>
          </div>
        </div>
        <div class="feat-side">
          ${sideItem(s1)}
          ${sideItem(s2)}
        </div>
      </div>
    </div>`;
}

// ── Build Card ────────────────────────────────────────────────
function buildCard(a) {
  const img = a.image_url
    ? `<img class="card-img" src="${esc(a.image_url)}" alt="${esc(a.title)}" loading="lazy" onerror="this.outerHTML='<div class=\\'card-img-ph\\'>📰</div>'">`
    : `<div class="card-img-ph">📰</div>`;
  return `
    <div class="card" onclick="goArticle(${a.id})">
      ${img}
      <div class="card-body">
        <div class="cat-tag">SFAAM NEWS</div>
        <div class="h-md">${esc(a.title)}</div>
        <div class="summary">${esc(a.summary || '')}</div>
        <div class="card-meta">
          <span>${fmtDate(a.date)}</span>
          <span class="read-more">Read →</span>
        </div>
      </div>
    </div>`;
}

// ── Build Sidebar ─────────────────────────────────────────────
function buildSidebar(articles) {
  const items = (articles || []).slice(0, 6).map((a, i) => `
    <div class="sidebar-item" onclick="goArticle(${a.id})">
      <span class="sidebar-num">${i + 1}</span>
      <span class="sidebar-title">${esc(a.title)}</span>
    </div>`).join('');
  return `
    <aside class="sidebar">
      <div class="sidebar-box">
        <div class="sidebar-hdr">🔥 Most Read</div>
        ${items || '<div style="padding:16px;font-size:0.8rem;color:#aaa;">Loading...</div>'}
      </div>
      <div class="sidebar-ad">
        <!-- AdSense / Monetag 300×250 -->
        Advertisement<br/>(300×250)
      </div>
    </aside>`;
}

// ── Build Pagination ──────────────────────────────────────────
function buildPagination(current, hasMore, fnName) {
  return `
    <div class="pagination">
      <button class="pg" onclick="${fnName}(${current-1})" ${current<=1?'disabled':''}>‹</button>
      ${[1,2,3,4,5].map(n=>`<button class="pg ${n===current?'active':''}" onclick="${fnName}(${n})">${n}</button>`).join('')}
      <button class="pg" onclick="${fnName}(${current+1})" ${!hasMore?'disabled':''}>›</button>
    </div>`;
}

// ── Toast ─────────────────────────────────────────────────────
function showToast(msg) {
  let t = document.getElementById('toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'toast'; t.className = 'toast';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 4500);
}

// ── Helpers ───────────────────────────────────────────────────
function fmtDate(d) {
  return new Date(d).toLocaleDateString('en-US', {
    day: 'numeric', month: 'short', year: 'numeric'
  });
}
function fmtDateLong(d) {
  return new Date(d).toLocaleDateString('en-US', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
  });
}
function esc(s) {
  if (!s) return '';
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;')
          .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

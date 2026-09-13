/* Problem Bank service worker — cache static assets; network-first for pages/API. */
const CACHE_VERSION = 'pb-v84';
const STATIC_CACHE = `static-${CACHE_VERSION}`;
const OFFLINE_URL = '/offline';

const PRECACHE_URLS = [
  OFFLINE_URL,
  '/static/manifest.webmanifest',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/js/theme.js',
  '/static/js/site.js',
  '/static/js/pwa.js',
  '/static/css/tokens.css',
  '/static/css/fonts.css',
  '/static/css/base.css',
  '/static/css/components.css',
  '/static/css/chrome.css',
  '/static/css/practice.css',
  '/static/css/pages.css',
  '/static/css/responsive.css',
  '/static/css/diagrams.css',
  '/static/css/lesson-pages.css',
  '/static/css/lesson-assist.css',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(PRECACHE_URLS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== STATIC_CACHE).map((key) => caches.delete(key)))
    ).then(() => self.clients.claim())
  );
});

function isApiRequest(url) {
  return url.pathname.startsWith('/api/');
}

function isStaticAsset(url) {
  return url.pathname.startsWith('/static/');
}

// JS and CSS carry ?v= cache-busts, so they must not be served cache-first.
function isVersionedAsset(url) {
  return isStaticAsset(url) && (url.pathname.endsWith('.js') || url.pathname.endsWith('.css'));
}

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  // API: network only (never cache authenticated JSON)
  if (isApiRequest(url)) {
    event.respondWith(
      fetch(request).catch(() =>
        new Response(JSON.stringify({ ok: false, error: 'You are offline', code: 'offline' }), {
          status: 503,
          headers: { 'Content-Type': 'application/json' },
        })
      )
    );
    return;
  }

  // JS/CSS: network-first so ?v= cache-busts are not stuck behind an old service worker entry
  if (isVersionedAsset(url)) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response && response.ok) {
            const clone = response.clone();
            caches.open(STATIC_CACHE).then((cache) => cache.put(request, clone));
          }
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // Other static assets: cache-first
  if (isStaticAsset(url)) {
    event.respondWith(
      caches.match(request).then((cached) => {
        const fetchPromise = fetch(request)
          .then((response) => {
            if (response && response.ok) {
              const clone = response.clone();
              caches.open(STATIC_CACHE).then((cache) => cache.put(request, clone));
            }
            return response;
          })
          .catch(() => cached);
        return cached || fetchPromise;
      })
    );
    return;
  }

  // Navigations / HTML: network-first, fall back to offline page
  if (request.mode === 'navigate' || (request.headers.get('accept') || '').includes('text/html')) {
    event.respondWith(
      fetch(request)
        .then((response) => response)
        .catch(() => caches.match(OFFLINE_URL))
    );
  }
});

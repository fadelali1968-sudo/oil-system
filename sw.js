// عمل بدون نت: يحفظ صفحة البرنامج ومكتباتها على الجهاز.
// الصفحة نفسها: من النت أولاً (لتصل التحديثات فوراً) وعند انقطاعه من النسخة المحفوظة.
// المكتبات (CDN والخطوط وFirebase): من النسخة المحفوظة أولاً وتُحدَّث بالخلفية.
// طلبات بيانات Firebase (firestore/auth) لا تمر من هنا — يتولاها Firebase بذاكرته الخاصة.
const CACHE = 'oil-offline-v1';
const PAGE = './index.html';
const LIBS = [
  'https://cdn.tailwindcss.com',
  'https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap',
  'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js',
  'https://cdn.jsdelivr.net/npm/xlsx-js-style@1.2.0/dist/xlsx.bundle.js',
  'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js',
  'https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js',
  'https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js',
  'https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js'
];
const LIB_HOSTS = ['cdn.tailwindcss.com', 'cdn.jsdelivr.net', 'cdnjs.cloudflare.com', 'fonts.googleapis.com', 'fonts.gstatic.com'];

// CORS أولاً (تحتاجه وحدات Firebase)، وإلا نسخة opaque تكفي لوسوم <script>
async function fetchLib(url) {
  try { const r = await fetch(url, { mode: 'cors' }); if (r.ok) return r; } catch (e) {}
  return fetch(url, { mode: 'no-cors' });
}

self.addEventListener('install', function (ev) {
  ev.waitUntil((async function () {
    const c = await caches.open(CACHE);
    try { await c.add(PAGE); } catch (e) {}
    await Promise.all(LIBS.map(async function (u) { try { await c.put(u, await fetchLib(u)); } catch (e) {} }));
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', function (ev) {
  ev.waitUntil((async function () {
    const keys = await caches.keys();
    await Promise.all(keys.filter(function (k) { return k.indexOf('oil-offline-') === 0 && k !== CACHE; }).map(function (k) { return caches.delete(k); }));
    await self.clients.claim();
  })());
});

function isLib(url) {
  return LIB_HOSTS.indexOf(url.hostname) >= 0 || (url.hostname === 'www.gstatic.com' && url.pathname.indexOf('/firebasejs/') === 0);
}

self.addEventListener('fetch', function (ev) {
  const req = ev.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  if (req.mode === 'navigate' && url.origin === self.location.origin) {
    ev.respondWith((async function () {
      const c = await caches.open(CACHE);
      try {
        const r = await fetch(req);
        if (r.ok) c.put(PAGE, r.clone());
        return r;
      } catch (e) {
        return (await c.match(PAGE)) || (await c.match(req)) || Response.error();
      }
    })());
    return;
  }

  if (url.origin === self.location.origin) {
    ev.respondWith((async function () {
      const c = await caches.open(CACHE);
      try { const r = await fetch(req); if (r.ok) c.put(req, r.clone()); return r; }
      catch (e) { return (await c.match(req)) || Response.error(); }
    })());
    return;
  }

  if (isLib(url)) {
    ev.respondWith((async function () {
      const c = await caches.open(CACHE);
      const hit = await c.match(req, { ignoreVary: true });
      const net = fetch(req).then(function (r) { if (r.ok || r.type === 'opaque') c.put(req, r.clone()); return r; });
      if (hit) { net.catch(function () {}); return hit; }
      return net;
    })());
  }
});

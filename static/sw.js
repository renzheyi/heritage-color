/* 考色 PWA Service Worker：静态资源缓存优先，页面网络优先（离线回退缓存）。
 * Streamlit 的 /_stcore/ 请求（含 WebSocket / 健康检查）一律交由浏览器原生处理。 */
const CACHE = 'kaose-pwa-v1';
const ASSETS = [
  '/app/static/icon-192.png',
  '/app/static/icon-512.png',
  '/app/static/manifest.webmanifest'
];

self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(CACHE)
      .then(function (cache) {
        // 单个资源失败不影响安装
        return Promise.allSettled(ASSETS.map(function (u) { return cache.add(u); }));
      })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys()
      .then(function (keys) {
        return Promise.all(keys.filter(function (k) { return k !== CACHE; })
          .map(function (k) { return caches.delete(k); }));
      })
      .then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (event) {
  var req = event.request;
  if (req.method !== 'GET') return;
  var url;
  try { url = new URL(req.url); } catch (e) { return; }
  if (url.origin !== self.location.origin) return;
  if (url.pathname.indexOf('/_stcore/') >= 0) return;
  if (url.pathname.indexOf('/_stapp/') >= 0) return;

  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req).catch(function () { return caches.match('/'); })
    );
    return;
  }

  event.respondWith(
    caches.match(req).then(function (cached) {
      return cached || fetch(req).then(function (resp) {
        var copy = resp.clone();
        caches.open(CACHE).then(function (c) { c.put(req, copy); });
        return resp;
      });
    })
  );
});

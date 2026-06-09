const CACHE_NAME = 'it-house-level-up-v3';
const STATIC_CACHE = 'it-house-static-v1';

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(STATIC_CACHE).then(cache => {
      return cache.addAll([
        '/static/manifest.json'
      ]).catch(() => {});
    })
  );
});

self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.open(STATIC_CACHE).then(cache => {
        return cache.match(request).then(cached => {
          const fetchPromise = fetch(request).then(networkRes => {
            if (networkRes && networkRes.status === 200) {
              cache.put(request, networkRes.clone());
            }
            return networkRes;
          }).catch(() => cached);
          return cached || fetchPromise;
        });
      })
    );
    return;
  }

  event.respondWith(
    fetch(request)
      .then(response => response)
      .catch(() => {
        if (request.mode === 'navigate') {
          return caches.match('/offline/');
        }
        return new Response('Offline', { status: 503 });
      })
  );
});

self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME, STATIC_CACHE];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (!cacheWhitelist.includes(cacheName)) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

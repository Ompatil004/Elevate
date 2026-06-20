const STATIC_CACHE = 'elevate-static-v1';
const RUNTIME_CACHE = 'elevate-runtime-v1';

const STATIC_ASSETS = ['/', '/index.html', '/vite.svg'];

const staleWhileRevalidate = async (request, cacheName) => {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);

  const networkPromise = fetch(request)
    .then((response) => {
      cache.put(request, response.clone());
      return response;
    })
    .catch(() => null);

  return cached || networkPromise;
};

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(STATIC_ASSETS)).catch(() => undefined)
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => ![STATIC_CACHE, RUNTIME_CACHE].includes(key))
          .map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  // SEC-20: do not cache third-party resources in service worker.
  // This avoids indefinite caching of remote assets without integrity validation.
  if (url.origin !== self.location.origin) return;

  if (url.origin === self.location.origin) {
    const isStaticAsset = ['script', 'style', 'image', 'font'].includes(request.destination);
    if (isStaticAsset) {
      event.respondWith(staleWhileRevalidate(request, RUNTIME_CACHE));
    }
  }
});

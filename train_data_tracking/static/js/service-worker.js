// service-worker.js

// Define the cache name to version the cache.
const CACHE_NAME = 'my-pwa-cache-v1';

// List of URLs to cache. Add all the URLs you want to cache here.
const cacheUrls = [
  '/',
  '/offline-page/', // You can create a custom offline page in Django
  // Add other URLs for your app's assets (CSS, JS, images, etc.)
];

// Install the service worker and cache assets.
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(cacheUrls);
      })
  );
});

// Activate the service worker and remove old caches.
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME) {
            return caches.delete(name);
          }
        })
      );
    })
  );
});

// Fetch event to intercept network requests and serve cached assets.
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // If the request is in the cache, return the cached response.
        if (response) {
          return response;
        }
        
        // If the request is not in the cache, fetch it from the network.
        return fetch(event.request)
          .then((networkResponse) => {
            // Clone the network response and cache it for future use.
            let responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              });
            return networkResponse;
          })
          .catch(() => {
            // If the network request fails, return an offline page or fallback.
            return caches.match('/offline-page/');
          });
      })
  );
});

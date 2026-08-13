const CACHE = "tbe-v2";
const ASSETS = [
  "./",
  "./index.html",
  "./routes.html",
  "./booking.html",
  "./css/app.min.css",
  "./js/app.min.js",
  "./icons/favicon.svg",
  "./images/coach-hero.svg"
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  e.respondWith(
    caches.match(e.request).then((cached) => {
      const networked = fetch(e.request)
        .then((res) => {
          const cacheCopy = res.clone();
          caches.open(CACHE).then((c) => c.put(e.request, cacheCopy));
          return res;
        })
        .catch(() => cached);
      return cached || networked;
    })
  );
});

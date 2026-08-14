const CACHE="tbe-v5";
const SHELL=["./","./index.html","./routes.html","./booking.html","./css/site.min.css","./js/app.min.js","./icons/favicon.svg","./images/trinity-express-logo.webp","./images/hero.webp"];
self.addEventListener("install",event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(SHELL)).then(()=>self.skipWaiting())));
self.addEventListener("activate",event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key!==CACHE).map(key=>caches.delete(key)))).then(()=>self.clients.claim())));
self.addEventListener("fetch",event=>{if(event.request.method!=="GET")return;const url=new URL(event.request.url);if(url.origin!==location.origin)return;event.respondWith(caches.match(event.request).then(cached=>{const fresh=fetch(event.request).then(response=>{if(response.ok){const copy=response.clone();caches.open(CACHE).then(cache=>cache.put(event.request,copy))}return response}).catch(()=>cached);return cached||fresh}))});

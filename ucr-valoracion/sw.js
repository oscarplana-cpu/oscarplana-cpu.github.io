// Portal de Valoración UCR · funcionamiento sin conexión.
// La página y sus iconos se guardan en el equipo; al publicar una versión nueva, cambia VERSION.
const VERSION = "ucr-20261028125257";
const ARCHIVOS = ["./", "./index.html", "./manifest.webmanifest", "./iconos/icono-192.png", "./iconos/icono-512.png", "./iconos/icono-512-maskable.png", "./iconos/apple-touch-icon.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(VERSION).then(c => c.addAll(ARCHIVOS)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  const req = e.request; if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin === location.origin){
    // la página: primero la red (para recibir versiones nuevas), y si no hay conexión, la copia guardada
    if (req.mode === "navigate"){ e.respondWith(fetch(req.url, {cache: "no-cache", credentials: "same-origin"}).then(r => { const c = r.clone(); caches.open(VERSION).then(x => x.put("./index.html", c)); return r; }).catch(() => caches.match("./index.html"))); return; }
    e.respondWith(caches.match(req).then(r => r || fetch(req)));
    return;
  }
  // tipografías de Google: se guardan la primera vez que hay conexión
  if (/fonts\.(googleapis|gstatic)\.com$/.test(url.hostname)){
    e.respondWith(caches.match(req).then(r => r || fetch(req).then(res => { const c = res.clone(); caches.open(VERSION).then(x => x.put(req, c)); return res; }).catch(() => new Response("", {status: 504}))));
  }
});

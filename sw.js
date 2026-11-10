// Duty Board service worker: app shell works offline; flight data is fetched fresh
// when online and falls back to the last saved copy when offline.
const SHELL = "duty-board-shell-v18";
const DATA = "duty-board-data";
const SHELL_FILES = ["./", "index.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(SHELL_FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(
    keys.filter(k => k !== SHELL && k !== DATA).map(k => caches.delete(k))
  )).then(() => self.clients.claim()));
});

self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;
  const dataFile = ["data.json", "roster.json", "crew.json", "crewkeys.json"].find(f => url.pathname.endsWith("/" + f));
  if (dataFile) {
    // network first, saved copy when offline
    e.respondWith(fetch(e.request, { cache: "no-store" }).then(res => {
      const copy = res.clone();
      caches.open(DATA).then(c => c.put(dataFile, copy));
      return res;
    }).catch(() => caches.open(DATA).then(c => c.match(dataFile)).then(r => r || Response.error())));
    return;
  }
  // app files: always ask the server first (skip the browser's 10-minute copy) so updates arrive at once
  e.respondWith(fetch(e.request, { cache: "no-cache" }).then(res => {
    const copy = res.clone();
    caches.open(SHELL).then(c => c.put(e.request, copy));
    return res;
  }).catch(() => caches.match(e.request).then(r => r || caches.match("index.html"))));
});

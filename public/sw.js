/* 서울 나들이: 한 번 열어 두면 인터넷이 끊겨도 보이게 해 주는 파일 */
const CACHE = 'nadeuri-1';
const SHELL = [
  './',
  'manifest.webmanifest',
  'fonts/bhs-ko.woff2',
  'icons/favicon.svg',
  'icons/icon-192.png',
  'icons/apple-touch-icon.png'
];
const HOME = new URL('./', self.registration.scope);

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

/* 새 내용을 받아서 저장해 둔다. 저장돼 있던 것과 다르면 true */
async function refresh() {
  try {
    const cache = await caches.open(CACHE);
    const old = await cache.match('./');
    const res = await fetch(HOME, { cache: 'no-store' });
    if (!res || !res.ok) return false;
    const next = await res.clone().text();
    const prev = old ? await old.text() : null;
    await cache.put('./', res);
    return prev !== null && prev !== next;
  } catch (err) {
    return false;
  }
}

/* 첫 화면은 저장해 둔 것을 바로 보여 주고, 뒤에서 새 내용을 받아 둔다 */
let changed = Promise.resolve(false);
async function page(e) {
  const cache = await caches.open(CACHE);
  const cached = await cache.match('./');
  if (cached) {
    changed = refresh();
    e.waitUntil(changed);
    return cached;
  }
  try {
    const res = await fetch(HOME, { cache: 'no-store' });
    if (res && res.ok) cache.put('./', res.clone());
    return res;
  } catch (err) {
    return new Response('인터넷에 연결한 뒤 다시 열어 주세요.', {
      status: 503,
      headers: { 'Content-Type': 'text/plain; charset=utf-8' }
    });
  }
}

/* 화면이 '바뀐 내용 있어요?' 하고 물으면 답한다 */
self.addEventListener('message', (e) => {
  if (!e.data || e.data.type !== 'check' || !e.source) return;
  e.waitUntil((async () => {
    let yes = await changed;
    changed = Promise.resolve(false);
    if (!yes && e.data.active) yes = await refresh();
    if (yes) e.source.postMessage({ type: 'updated' });
  })());
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  if (req.mode === 'navigate') {
    e.respondWith(page(e));
    return;
  }
  e.respondWith(
    caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      if (res && res.ok) {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy));
      }
      return res;
    }))
  );
});

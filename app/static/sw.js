const CACHE_NAME = 'daily-hub-cache-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/static/index.html',
    '/static/app.js',
    '/static/manifest.json',
    '/static/icon.png'
];

// Instala o Service Worker e salva os arquivos da interface no celular
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

// Intercepta as requisições (Modo Avião)
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request).then(response => {
            // Se tem no cache, devolve do cache. Se não, tenta pegar da internet.
            return response || fetch(event.request);
        })
    );
});
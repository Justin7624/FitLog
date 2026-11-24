const CACHE='fitlog-static-v4.0.0';
const FILES=['./','./index.html','./style.css','./app.js','./library.js','./pro.js','./v3-core.js','./v3-training.js','./v3-ui.js','./v3-sync.js','./v3.css','./manifest.webmanifest','./icon-192.png','./icon-512.png','./assets/body-mesh.js','./body-fit.js','./body-view.js','./body-studio.js','./body-studio.css'];
const ASSETS=new Set(FILES.map(f=>new URL(f,self.registration.scope).href));
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES.map(f=>new Request(f,{cache:'reload'})))).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('fitlog-static-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET'||new URL(e.request.url).origin!==self.location.origin)return;const u=new URL(e.request.url);u.search='';u.hash='';if(!ASSETS.has(u.href))return;e.respondWith(caches.open(CACHE).then(async c=>{const hit=await c.match(u.href);if(hit)return hit;return fetch(e.request);}));});

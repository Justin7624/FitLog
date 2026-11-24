"""Actual origin, native storage, PWA and offline mesh regression (CI/deployed test)."""
import os,functools,http.server,json,pathlib,threading
from playwright.sync_api import sync_playwright,expect
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}'
try:
 with sync_playwright() as pw:
  args={'headless':True,'args':['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']}
  if os.environ.get('CHROMIUM_PATH'):args['executable_path']=os.environ['CHROMIUM_PATH']
  browser=pw.chromium.launch(**args);context=browser.new_context(viewport={'width':430,'height':932},accept_downloads=True);page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('dialog',lambda d:d.accept())
  page.goto(url+'/tests/seed.html');fixture=json.loads((ROOT/'tests/v2-fixture.json').read_text());fixture['pro']['schema']=3;fixture['pro']['v3']={'nutrition':[{'id':'old-meal','name':'Legacy meal','date':'2026-11-23','protein':20}],'programs':[],'preferences':{'sound':True},'bodyGoals':[]};fixture['measurements']=[{'id':'legacy-height','date':'2026-11-01','kind':'Height','value':180,'unit':'cm'},{'id':'legacy-waist','date':'2026-11-01','kind':'Waist','value':35,'unit':'in'},{'id':'legacy-waist-new','date':'2026-11-23','kind':'Waist','value':33,'unit':'in'}]
  page.evaluate('''async x=>{localStorage.setItem('fitlog-v1',JSON.stringify(x));let c=document.createElement('canvas');c.width=c.height=10;let blob=await new Promise(r=>c.toBlob(r,'image/jpeg'));await new Promise((resolve,reject)=>{let q=indexedDB.open('fitlog-pro-v2',1);q.onupgradeneeded=()=>{q.result.createObjectStore('state');q.result.createObjectStore('photos',{keyPath:'id'})};q.onsuccess=()=>{let db=q.result,t=db.transaction(['state','photos'],'readwrite');t.objectStore('state').put(x,'latest');t.objectStore('photos').put({id:'legacy-photo',date:'2026-11-23',view:'Front',blob});t.oncomplete=()=>{db.close();resolve()};t.onerror=reject};q.onerror=reject});}''',fixture)
  page.goto(url+'/');page.wait_for_function('!migrationPending&&dbReady');assert page.evaluate('state.history[0].id')==fixture['history'][0]['id'];assert page.evaluate('state.pro.v3.nutrition[0].id')=='old-meal';assert page.evaluate('routineBy("arm").exercises.length')==18
  page.locator('nav [data-nav=body]').click();page.wait_for_function('photoCache.some(p=>p.id==="legacy-photo")');page.locator('[data-bs=open]').click();page.wait_for_function('FitLogBodyStudio.getFit()?.supplied===2');page.locator('#bsPhotos').check();expect(page.locator('#bsPhotoPanel img').first).to_be_visible();page.locator('[data-bs=simulate]').click();page.locator('[data-bs-input=waist]').fill('75');page.locator('[data-bs-input=waist]').press('Tab');page.locator('[data-bs=saveGoal]').click();assert page.evaluate('state.pro.v3.bodyStudio.goal.values.waist')==75
  print('PASS native migration, existing photos, goals and measurements')
  page.locator('#bsCSV').set_input_files({'name':'measurements.csv','mimeType':'text/csv','buffer':b'date,kind,value,unit\n2026-11-23,Chest,105,cm\n2026-11-23,Chest,105,cm\n2026-11-23,Hips,,cm\n'});page.wait_for_function('state.measurements.filter(x=>x.kind==="Chest").length===1');print('PASS CSV import and exact duplicate prevention')
  page.evaluate('navigator.serviceWorker.ready');page.wait_for_function('!!navigator.serviceWorker.controller');context.set_offline(True);page.reload();page.wait_for_function('!migrationPending');page.locator('nav [data-nav=body]').click();page.locator('[data-bs=open]').click();page.wait_for_function('FitLogBodyStudio.getFit()?.supplied===3');assert page.evaluate('state.pro.v3.bodyStudio.goal.values.waist')==75;assert page.evaluate('state.history[0].id')==fixture['history'][0]['id'];expect(page.locator('#bsCanvas')).to_be_visible();print('PASS offline 3D assets, history and goal persistence')
  assert not errors,errors;browser.close()
finally:server.shutdown()

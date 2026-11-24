"""Real browser acceptance tests. Run on localhost or GitHub Actions; no external account."""
import base64, functools, http.server, json, os, pathlib, tempfile, threading
from playwright.sync_api import sync_playwright, expect
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}'
try:
  with sync_playwright() as pw, tempfile.TemporaryDirectory() as tmp:
    args={'headless':True,'args':['--no-sandbox']}
    if os.environ.get('CHROMIUM_PATH'): args['executable_path']=os.environ['CHROMIUM_PATH']
    browser=pw.chromium.launch(**args)
    context=browser.new_context(viewport={'width':390,'height':844},accept_downloads=True)
    page=context.new_page(); errors=[]; dialogs=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    def dialog(d):
      dialogs.append(d.message)
      if 'already logged' in d.message: d.dismiss()
      elif d.type=='prompt': d.accept('test-long-passphrase')
      else: d.accept()
    page.on('dialog',dialog)
    page.goto(url+'/tests/seed.html')
    fixture=json.loads((ROOT/'tests/v2-fixture.json').read_text())
    page.evaluate('''async x=>{localStorage.setItem('fitlog-v1',JSON.stringify(x));const canvas=document.createElement('canvas');canvas.width=10;canvas.height=10;const blob=await new Promise(r=>canvas.toBlob(r,'image/jpeg'));await new Promise((resolve,reject)=>{const q=indexedDB.open('fitlog-pro-v2',1);q.onupgradeneeded=()=>{q.result.createObjectStore('state');q.result.createObjectStore('photos',{keyPath:'id'})};q.onsuccess=()=>{let d=q.result,t=d.transaction(['state','photos'],'readwrite');t.objectStore('state').put(x,'latest');t.objectStore('photos').put({id:'legacy-photo',date:'2026-11-23',view:'Front',blob});t.oncomplete=()=>{d.close();resolve()};t.onerror=reject};q.onerror=reject;});}''',fixture)
    page.goto(url+'/');page.wait_for_function('!migrationPending&&dbReady')
    assert page.evaluate('state.pro.schema')==3
    assert page.evaluate('state.history[0].id')==fixture['history'][0]['id']
    assert page.evaluate('state.history[0].notes')==fixture['history'][0]['notes']
    assert page.evaluate('routineBy("arm").exercises.length')==18
    assert page.evaluate('routineBy("arm").video').endswith('ruoCYrZCBeY')
    assert page.evaluate('state.settings.theme')==fixture['settings']['theme']
    assert page.evaluate('state.pro.goals.Biceps')==fixture['pro']['goals']['Biceps']
    page.locator('nav [data-nav=body]').click(); page.wait_for_function('photoCache.some(x=>x.id==="legacy-photo")');expect(page.locator('#timelineFrame img')).to_be_visible()
    print('PASS v2 migration and native IndexedDB photo preservation')
    page.locator('nav [data-nav=history]').click();page.locator('[data-action=deleteLog]').first.click();assert page.evaluate('state.history.length')==0;page.locator('[data-v3=undo]').first.click();assert page.evaluate('state.history.length')==1
    page.locator('nav [data-nav=routines]').click();page.locator('[data-action=start][data-id=arm]').click();page.locator('[data-field="w.date"]').fill(fixture['history'][0]['date']);page.locator('[data-action=markAll]').click();page.locator('[data-action=finish]').click();assert page.evaluate('state.history.length')==1;assert page.evaluate('!!state.active');assert any('already logged' in d for d in dialogs);page.locator('[data-action=discard]').click();print('PASS visible delete, undo and duplicate cancellation')
    page.locator('nav [data-nav=routines]').click();page.locator('[data-action=edit][data-id=ab]').click();page.locator('[data-pro=library]').click();page.locator('#libSearch').fill('forearm plank');page.locator('[data-pro=libAdd]').first.click();page.locator('[data-e="0"] [data-field="s.seconds"]').fill('1');page.locator('[data-e="0"] [data-field="e.rest"]').fill('1');page.locator('[data-action=backRoutines]').first.click();page.locator('[data-pro=startGuide][data-id=ab]').click();page.locator('[data-pro=guideStart]').click();page.wait_for_function('state.pro.guide.phase==="done"',timeout=10000);page.locator('[data-pro=review]').first.click();page.locator('[data-action=finish]').click();assert page.evaluate('state.history.length')==2;print('PASS library, routine edit, interval transitions and actual save')
    page.locator('nav [data-nav=wellness]').click();page.locator('#nutritionForm [name=name]').fill('Test meal');page.locator('#nutritionForm [name=protein]').fill('30');page.locator('#nutritionForm [name=water]').fill('250');page.locator('#nutritionForm button').click();assert page.evaluate('nutritionTotal(wellnessDate).protein')==30
    page.locator('nav [data-nav=routines]').click();page.locator('[data-v3=schedule]').first.click();page.locator('#programForm [name=weeks]').fill('2');page.locator('#programForm button').click();assert page.evaluate('v3().schedule.length')==14;print('PASS nutrition and program forms')
    page.locator('nav [data-nav=progress]').click();page.locator('[data-pro=report]').click();page.locator('#reportRange').select_option('365');pdf=page.pdf(format='A4');assert pdf.startswith(b'%PDF');print('PASS printable annual PDF')
    page.locator('header [data-nav=settings]').click();
    with page.expect_download() as dl: page.locator('[data-v3=encrypt]').click()
    backup=pathlib.Path(tmp)/'backup.json';dl.value.save_as(str(backup));assert json.loads(backup.read_text())['format']=='fitlog-encrypted-v1';page.locator('#encryptedFile').set_input_files(str(backup));page.wait_for_function('page==="home"');assert page.evaluate('state.history.length')==2;print('PASS encrypted export and import')
    page.reload();page.wait_for_function('!migrationPending');assert page.evaluate('state.history.length')==2;page.locator('nav [data-nav=body]').click();page.wait_for_function('photoCache.some(x=>x.id==="legacy-photo")');print('PASS persistence and photo retention')
    page.evaluate('navigator.serviceWorker.ready');page.wait_for_function('!!navigator.serviceWorker.controller');context.set_offline(True);page.reload();page.wait_for_function('!migrationPending');expect(page.locator('h1')).to_be_visible();assert page.evaluate('state.history.length')==2;context.set_offline(False);print('PASS offline shell and history')
    assert not errors,errors
    browser.close()
finally: server.shutdown()

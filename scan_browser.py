"""Hosted-origin acceptance: actual IndexedDB, encrypted backup, offline reload.
Run in CI or localhost; current sandbox blocks localhost navigation."""
import os,pathlib,json,functools,http.server,threading,base64
from playwright.sync_api import sync_playwright,expect
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}'
try:
 with sync_playwright() as p:
  args={'headless':True,'args':['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']}
  if os.environ.get('CHROMIUM_PATH'):args['executable_path']=os.environ['CHROMIUM_PATH']
  browser=p.chromium.launch(**args);context=browser.new_context(viewport={'width':430,'height':932},accept_downloads=True);page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('dialog',lambda d:d.accept('scan-test-passphrase') if d.type=='prompt' else d.accept())
  page.goto(url+'/tests/seed.html');fixture=json.loads((ROOT/'tests/v2-fixture.json').read_text());fixture['measurements']=[{'id':'h','kind':'Height','value':175,'unit':'cm','date':'2026-11-23'},{'id':'w','kind':'Waist','value':94,'unit':'cm','date':'2026-11-23'}];page.evaluate('(x)=>localStorage.setItem("fitlog-v1",JSON.stringify(x))',fixture);page.goto(url+'/');page.wait_for_function('!migrationPending&&dbReady');page.locator('nav [data-nav=body]').click();page.locator('[data-scan=open]').click()
  # Use actual file inputs, a known synthetic mannequin and no external photos.
  images=page.evaluate('''()=>{let m=BodyFit.fit({height:175,waist:94,chest:108},{torsoDepth:15});return Array.from({length:12},(_,i)=>{let rows=ScanCore.project(m.vertices,175,i*30),c=document.createElement('canvas');c.width=300;c.height=480;let x=c.getContext('2d');x.fillStyle='#eeeeee';x.fillRect(0,0,300,480);x.fillStyle='#353535';for(let y=30;y<450;y++){let r=Math.round((449-y)/419*(ScanCore.N-1));for(let [l,h] of rows[r])x.fillRect(150+l*420,y,Math.max(1,(h-l)*420),1);}return c.toDataURL('image/png').split(',')[1]})}''')
  page.locator('#scanBatch').set_input_files([{'name':f'{i:02}.png','mimeType':'image/png','buffer':base64.b64decode(im)} for i,im in enumerate(images)]);expect(page.locator('#scanCoverage')).to_contain_text('12/12 captured',timeout=20000)
  for i in range(12):page.locator(f'[data-scan-angle="{i}"]').click();page.locator('[data-scan=approve]').click()
  page.locator('[data-scan=build]').click();expect(page.locator('#scanMesh')).to_be_visible(timeout=20000);page.locator('[data-scan=save]').click();expect(page.locator('[data-scan-load]')).to_have_count(1,timeout=20000)
  with page.expect_download() as dl:page.locator('[data-scan=backup]').click()
  backup=pathlib.Path(dl.value.path()).read_bytes();assert json.loads(backup)['format']=='fitlog-encrypted-v1';assert b'Body scan' not in backup
  page.locator('[data-scan-delete]').click();expect(page.locator('[data-scan-load]')).to_have_count(0);page.locator('#scanRestore').set_input_files({'name':'backup.json','mimeType':'application/json','buffer':backup});expect(page.locator('[data-scan-load]')).to_have_count(1,timeout=30000);print('PASS native scan persistence, encrypted backup, deletion and restore')
  page.evaluate('navigator.serviceWorker.ready');page.wait_for_function('!!navigator.serviceWorker.controller');context.set_offline(True);page.reload();page.wait_for_function('!migrationPending');page.locator('nav [data-nav=body]').click();page.locator('[data-scan=open]').click();page.locator('[data-scan-load]').click();expect(page.locator('#scanMesh')).to_be_visible();assert page.evaluate('state.history[0].id')==fixture['history'][0]['id'];print('PASS offline scan reload and existing history retained');assert not errors,errors;browser.close()
finally:server.shutdown()

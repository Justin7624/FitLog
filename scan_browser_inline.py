import os,pathlib,json,re,base64
from playwright.sync_api import sync_playwright,expect
ROOT=pathlib.Path(__file__).resolve().parents[1]
fixture=json.loads((ROOT/'tests/v2-fixture.json').read_text());fixture['measurements']=[{'id':'h','kind':'Height','value':175,'unit':'cm','date':'2026-11-23'},{'id':'w','kind':'Waist','value':94,'unit':'cm','date':'2026-11-23'}]
html=(ROOT/'index.html').read_text();scripts=re.findall(r'<script src="([^"]+)" defer></script>',html);html=re.sub(r'<script src="[^"]+" defer></script>','',html);html=re.sub(r'<link rel="stylesheet" href="([^"]+)">',lambda m:'<style>'+(ROOT/m.group(1)).read_text()+'</style>',html);html=re.sub(r'<link[^>]+>','',html)
with sync_playwright() as p:
 args={'headless':True,'args':['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']}
 if os.environ.get('CHROMIUM_PATH'):args['executable_path']=os.environ['CHROMIUM_PATH']
 browser=p.chromium.launch(**args);page=browser.new_page(viewport={'width':430,'height':932},accept_downloads=True);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('dialog',lambda d:d.dismiss() if 'Discard original' in d.message else d.accept());page.set_content(html);page.evaluate('''fixture=>{let mem=new Map([['fitlog-v1',JSON.stringify(fixture)]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>mem.get(k)??null,setItem:(k,v)=>mem.set(k,v),removeItem:k=>mem.delete(k)}});const scans=new Map();Object.defineProperty(window,"indexedDB",{value:{open(name){const q={};if(name!=='fitlog-private-scans-v1'){queueMicrotask(()=>q.onerror?.());return q;}queueMicrotask(()=>{q.result={close(){},transaction(){let t={objectStore(){return {getAll(){return {result:structuredClone([...scans.values()])}},put(r){scans.set(r.id,structuredClone(r));return {result:r.id}},delete(k){scans.delete(k);return {}}}}};setTimeout(()=>t.oncomplete?.(),0);return t;}};q.onsuccess?.();});return q;}}});}''',fixture)
 for f in scripts:page.add_script_tag(content=(ROOT/f).read_text())
 page.locator('nav [data-nav=body]').click();expect(page.locator('[data-scan=open]')).to_be_visible();page.locator('[data-scan=open]').click();expect(page.locator('h1')).to_have_text('360° Body Scan');assert page.locator('[data-scan-val=height]').input_value()=='175'
 images=page.evaluate('''()=>{let m=BodyFit.fit({height:175,waist:94,chest:108},{torsoDepth:15});return Array.from({length:12},(_,i)=>{let rows=ScanCore.project(m.vertices,175,i*30),c=document.createElement('canvas');c.width=300;c.height=480;let x=c.getContext('2d');x.fillStyle='#eeeeee';x.fillRect(0,0,300,480);x.fillStyle='#353535';for(let y=30;y<450;y++){let r=Math.round((449-y)/419*(ScanCore.N-1));for(let [l,h] of rows[r])x.fillRect(150+l*420,y,Math.max(1,(h-l)*420),1);}return c.toDataURL('image/png').split(',')[1]})}''')
 page.locator('#scanBatch').set_input_files([{'name':f'{i:02}.png','mimeType':'image/png','buffer':base64.b64decode(im)} for i,im in enumerate(images)])
 expect(page.locator('#scanCoverage')).to_contain_text('12/12 captured',timeout=20000)
 for i in range(12):
  page.locator(f'[data-scan-angle="{i}"]').click();page.locator('[data-scan=approve]').click()
 expect(page.locator('#scanCoverage')).to_contain_text('12/12 approved');page.locator('[data-scan=build]').click();expect(page.locator('#scanMesh')).to_be_visible(timeout=20000);assert page.evaluate('FitLogScan.getModel().quality.count')==12;print('PASS actual PNG upload, mask approval, photo-assisted fit and canvas')
 page.locator('[data-scan=side]').click();page.locator('#scanMeasure').select_option('waist');page.wait_for_timeout(300);assert page.locator('#scanLines').evaluate('(c)=>c.width')>0
 with page.expect_download() as dl:page.locator('[data-scan=glb]').click()
 assert pathlib.Path(dl.value.path()).read_bytes()[:4]==b'glTF'
 with page.expect_download() as dl:page.locator('[data-scan=obj]').click()
 assert '\nf ' in pathlib.Path(dl.value.path()).read_text()
 with page.expect_download() as dl:page.locator('[data-scan=report]').click()
 assert 'Projected edge RMSE' in pathlib.Path(dl.value.path()).read_text()
 page.locator('[data-scan=correct]').click();page.locator('#scanGoalFields').locator('xpath=..').evaluate('(x)=>x.open=true');page.locator('[data-scan-goal=waist]').fill('85');page.locator('[data-scan=goal]').click();expect(page.locator('#scanDisplayNote')).to_contain_text('HYPOTHETICAL');page.locator('[data-scan=resetModel]').click();assert page.evaluate('state.measurements.length')==2;print('PASS measurement lines, GLB/OBJ/report, goal and journal isolation')
 page.locator('[data-scan=save]').click();expect(page.locator('[data-scan-load]')).to_have_count(1);page.locator('[data-scan-correction=abdomen]').fill('15');page.locator('[data-scan=correct]').click();# build a new scan to get a new record id
 page.locator('[data-scan=build]').click();expect(page.locator('#scanFitStatus')).to_contain_text('Reconstructed');page.locator('[data-scan=save]').click();expect(page.locator('[data-scan-load]')).to_have_count(2)
 opts=page.locator('#scanCompare option').evaluate_all('(a)=>a.map(x=>x.value).filter(Boolean)');page.locator('#scanCompare').select_option(opts[-1]);page.locator('#scanOverlay').check();page.locator('#scanMode').select_option('heat');expect(page.locator('#scanDisplayNote')).to_contain_text('Heatmap');page.locator('[data-scan=animate]').click();page.wait_for_timeout(500);assert int(page.locator('#scanBlend').input_value())>0;page.locator('[data-scan=animate]').click();print('PASS scan library, overlay, heatmap and animation using simulated scan database')
 page.locator('nav [data-nav=history]').click();assert page.evaluate('state.history[0].id')==fixture['history'][0]['id'];assert not errors,errors;print('PASS legacy workout data and no page errors');browser.close()

"""Offline isolated-browser rendering test, no navigation or network required.
This tests actual DOM, Canvas rendering and app controls, using mock storage because about:blank has no persistent origin.
Full PWA/IndexedDB origin tests are in browser_test.py and body_browser.py.
"""
import os,pathlib,json,base64,re,sys
from playwright.sync_api import sync_playwright,expect
ROOT=pathlib.Path(__file__).resolve().parents[1]
fixture=json.loads((ROOT/'tests/v2-fixture.json').read_text());fixture['measurements']=[dict(id=f'm{i}',kind=k,value=v,unit=u,date=d) for i,(k,v,u,d) in enumerate([('Height',180,'cm','2026-10-01'),('Waist',35,'in','2026-10-01'),('Body weight',185,'lb','2026-11-23'),('Waist',33,'in','2026-11-23'),('Chest',105,'cm','2026-11-23'),('Hips',100,'cm','2026-11-23'),('Left upper arm',36,'cm','2026-11-23'),('Right upper arm',34,'cm','2026-11-23'),('Shoulders',125,'cm','2026-11-23')])]
html=(ROOT/'index.html').read_text();scripts=re.findall(r'<script src="([^"]+)" defer></script>',html);html=re.sub(r'<script src="[^"]+" defer></script>','',html);html=re.sub(r'<link rel="stylesheet" href="([^"]+)">',lambda m:'<style>'+(ROOT/m.group(1)).read_text()+'</style>',html);html=re.sub(r'<link[^>]+>','',html)
with sync_playwright() as p:
 args={'headless':True,'args':['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']}
 if os.environ.get('CHROMIUM_PATH'):args['executable_path']=os.environ['CHROMIUM_PATH']
 browser=p.chromium.launch(**args);page=browser.new_page(viewport={'width':430,'height':932},accept_downloads=True);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(html);page.evaluate('''fixture=>{let mem=new Map([['fitlog-v1',JSON.stringify(fixture)]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>mem.get(k)??null,setItem:(k,v)=>mem.set(k,v),removeItem:k=>mem.delete(k)}});window.indexedDB={open(){const q={};queueMicrotask(()=>q.onerror?.());return q;}};}''',fixture)
 for file in scripts:page.add_script_tag(content=(ROOT/file).read_text())
 page.wait_for_function('typeof FitLogBodyStudio!=="undefined"');assert page.evaluate('state.history[0].id')==fixture['history'][0]['id'];assert page.evaluate('routineBy("arm").exercises.length')==18
 page.locator('nav [data-nav=body]').click();page.locator('[data-bs=open]').click();expect(page.locator('#bsCanvas')).to_be_visible();page.wait_for_function('FitLogBodyStudio.getFit()?.supplied===8');print('renderer:',page.locator('#bsRenderer').inner_text());print('stats:',page.locator('#bsStats').inner_text());assert 'unavailable' not in page.locator('#bsRenderer').inner_text().lower();assert page.evaluate('FitLogBodyStudio.getFit().rmse')<2
 page.wait_for_timeout(500)
 if os.environ.get('FITLOG_PREVIEW'):pathlib.Path('/mnt/data/fitlog4-preview-front.png').write_bytes(base64.b64decode(page.locator('#bsCanvas').evaluate('(c)=>c.toDataURL("image/png")').split(',')[1]))
 page.locator('[data-bs=side]').click();page.wait_for_timeout(500)
 if os.environ.get('FITLOG_PREVIEW'):pathlib.Path('/mnt/data/fitlog4-preview-side.png').write_bytes(base64.b64decode(page.locator('#bsCanvas').evaluate('(c)=>c.toDataURL("image/png")').split(',')[1]))
 page.locator('[data-bs=back]').click();page.wait_for_timeout(500);page.locator('[data-bs=front]').click();print('PASS actual canvas renderer and rotation controls')
 page.locator('#bsDisplay').select_option('muscles');page.locator('#bsRegion').select_option('5');expect(page.locator('#bsMuscleInfo')).to_contain_text('Biceps');print('PASS interactive region overlay')
 page.locator('#bsCompare').select_option('2026-10-01');page.locator('#bsOverlay').check();expect(page.locator('#bsComparisonControls')).to_be_visible();page.locator('#bsBlend').fill('50');expect(page.locator('#bsBlendLabel')).to_contain_text('50%');page.locator('[data-bs=animate]').click();page.wait_for_timeout(400);page.locator('[data-bs=animate]').click();print('PASS timeline and animation controls')
 page.locator('[data-bs=simulate]').click();page.locator('[data-bs-input=waist]').fill('75');page.locator('[data-bs-input=waist]').press('Tab');assert abs(page.evaluate('FitLogBodyStudio.getFit().metrics.find(m=>m.key==="waist").target')-75)<.01;assert page.evaluate('state.measurements.length')==len(fixture['measurements']);page.locator('[data-bs=saveGoal]').click();assert page.evaluate('state.pro.v3.bodyStudio.goal.values.waist')==75;print('PASS simulator and separate goal persistence')
 page.locator('[data-bs=actual]').click();page.locator('[data-bs-shape=abdomen]').fill('10');page.wait_for_timeout(350);page.locator('[data-bs=saveShape]').click();assert page.evaluate('state.pro.v3.bodyStudio.corrections["2026-11-23"].abdomen')==10
 with page.expect_download() as d:page.locator('[data-bs=obj]').click()
 assert d.value.suggested_filename.endswith('.obj');assert 'v ' in pathlib.Path(d.value.path()).read_text()[:300];print('PASS OBJ export')
 with page.expect_download() as d:page.locator('[data-bs=report]').click()
 report=pathlib.Path(d.value.path()).read_text();assert 'data:image/png;base64,' in report and 'Cross-section fit' in report;print('PASS downloadable comparison report')
 assert page.evaluate('FitLogBodyStudio.parseCSV("date,kind,value,unit\\n2026-11-23,Waist,33,in").length')==1
 page.locator('nav [data-nav=history]').click();assert page.evaluate('state.history[0].id')==fixture['history'][0]['id'];print('PASS original history retained');assert not errors,errors;browser.close()

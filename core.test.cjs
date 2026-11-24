const fs=require('fs'),vm=require('vm'),assert=require('assert/strict'),path=require('path').resolve(__dirname,'..');
const events={},nodeMap={},data=new Map();
function elem(sel){return nodeMap[sel]??= {innerHTML:'',textContent:'',style:{},dataset:{},hidden:true,classList:{toggle(){},add(){},remove(){}},addEventListener(n,f){events[sel+':'+n]=f},querySelector(){return null},click(){},scrollIntoView(){},value:'',};}
const document={querySelector:elem,querySelectorAll:()=>[],body:elem('body'),addEventListener(n,f){(events[n]??=[]).push(f)},hidden:false,getElementById:elem,createElement(){return elem('created');}};
let now=Date.now();class TestDate extends Date{constructor(...a){super(...(a.length?a:[now]));}static now(){return now;}}
const ctx=vm.createContext({console,Date:TestDate,JSON,Math,Set,Map,Number,String,Object,Array,URL,Blob,Uint8Array,atob,btoa,structuredClone,crypto:require('crypto').webcrypto,document,localStorage:{getItem:k=>data.get(k)??null,setItem:(k,v)=>data.set(k,v),removeItem:k=>data.delete(k)},navigator:{vibrate(){}},location:{protocol:'file:'},window:{scrollTo(){},print(){}},setTimeout:()=>1,clearTimeout(){},setInterval:()=>1,clearInterval(){},confirm:()=>true,prompt:()=>null,FormData,fetch:async()=>{throw Error('mock not configured')},indexedDB:{open(){const q={};queueMicrotask(()=>q.onerror?.());return q;}}});
const run=s=>vm.runInContext(s,ctx);const check=(label,s)=>{assert.ok(run(s),label);console.log('PASS',label)};
// Real v1 fixture generated from the original version's initialization.
const seed=JSON.parse(fs.readFileSync(require('path').join(__dirname,'v1-fixture.json'),'utf8'));seed.history[0].notes='Original user log preserved';seed.history[0].exercises[0].sets[0].reps=13;seed.history[0].exercises[0].sets[0].weight=12;data.set('fitlog-v1',JSON.stringify(seed));
for(const f of ['app.js','library.js','pro.js'])run(fs.readFileSync(path+'/'+f,'utf8'));
check('v1 migration preserves all 18 exercises and timestamped video',`state.routines[0].exercises.length===18&&state.routines[0].exercises[0].stamp==='0:26'&&state.routines[0].video.includes('ruoCYrZCBeY')`);
check('v1 exact historical notes/reps/weights/IDs retained',`state.history[0].notes==='Original user log preserved'&&state.history[0].exercises[0].sets[0].reps===13&&state.history[0].exercises[0].sets[0].weight===12&&state.history[0].id===${JSON.stringify(seed.history[0].id)}`);
check('legacy exercise key matches copied log',`state.history[0].exercises[0].exerciseKey===state.routines[0].exercises[0].exerciseKey`);
check('library count and filter',`LIBRARY.length===76&&(libSearch='plank',libRegion='Abs',libEquipment='My equipment',libResults().includes('Forearm plank')&&!libResults().includes('Side plank'))`);
run(`routineBy('ab').exercises.push(makeLibraryExercise(libBy('plank')));routineBy('ab').exercises[0].sets[0].seconds=1;routineBy('ab').exercises[0].rest=1;routineBy('ab').exercises[0].sets.push(clone(routineBy('ab').exercises[0].sets[0]));start('ab');nav('guide');guideStart();`);
check('guided set starts work',`state.pro.guide.phase==='work'&&state.pro.guide.running`);
now+=1100;run('guideTick()');check('automatic completion then rest',`state.active.exercises[0].sets[0].done&&state.pro.guide.phase==='rest'`);
now+=1100;run('guideTick()');check('automatic next working set',`state.pro.guide.phase==='work'&&state.pro.guide.setIndex===1&&state.pro.guide.running`);
now+=1100;run('guideTick()');now+=1100;run('guideTick()');check('guided sequence done',`completed(state.active).length===2&&state.pro.guide.phase==='done'`);
run('nav("session");finish()');check('finished session persisted',`state.history.length===2&&state.history.some(w=>w.routineId==='ab'&&completed(w).length===2)&&!state.active`);
check('anatomical region map and target set',`mapSvg('front').includes('data-muscle="Biceps"')&&regionSummary('Biceps',0).sets===4`);
run(`state.measurements.push(...[['Waist',30,'in'],['Hips',100,'cm'],['Shoulders',45,'in'],['Body weight',185,'lb'],['Body fat',15,'%']].map(([kind,value,unit])=>({id:uid(),date:dateLocal(),kind,value,unit})))`);
check('mixed-unit ratios and lean mass',`Math.abs(bodyRatios().waistHip[0].value-.762)<.001&&bodyRatios().shoulderWaist[0].value===1.5&&bodyRatios().lean[0].value===157.25`);
check('valid v1 and v2 backup',`validPro(state)&&validPro(initial())&&!validPro({...state,version:99})`);
check('valid photo backup parsed; invalid JPEG rejected',`parsePhotos({photoBackup:[{id:'test',date:'2026-11-23',view:'Front',data:'data:image/jpeg;base64,/9gA'}]})[0].blob.type==='image/jpeg'&&(()=>{try{parsePhotos({photoBackup:[{id:'x',date:'2026-11-23',view:'Front',data:'data:text/html;base64,YQ=='}]});return false}catch{return true}})()`);
check('substitution respects equipment and target muscle',`substituteList(state.routines[0].exercises[0]).every(l=>l[2]==='Biceps'&&profile().equipment.includes(l[4]))`);
run(`var sample=makeLibraryExercise(libBy('curl'));sample.sets[0].weight=10;sample.sets[0].reps=10;profile().weights=[10,11,12];for(let i=0;i<2;i++){let x=clone(sample);Object.assign(x.sets[0],{done:true,rpe:6});state.history.push({id:uid(),name:'Synthetic test',routineId:'arm',date:dateLocal(),duration:2,notes:'test',exercises:[x]});}`);
check('progressive overload after two successful logged sessions',`progression(sample).includes('11 lb')`);
check('secure cloud config blocks secret keys',`validCloudConfig('https://test.supabase.co','sb_publishable_test').url==='https://test.supabase.co'&&(()=>{try{validCloudConfig('https://test.supabase.co','sb_secret_test');return false}catch{return true}})()`);
check('video ID and timestamps',`youtubeId(state.routines[0].video)==='ruoCYrZCBeY'&&stampSeconds('17:24')===1044&&youtubeId('https://evil.com/watch?v=ruoCYrZCBeY')===''`);
for(const page of ['home','routines','history','progress','settings','equipment','goals','body','report','library']){run(`nav('${page}')`);assert.ok(elem('#app').innerHTML.includes('<h1>'),page);console.log('PASS render route',page)}
check('print report includes training & body tables',`reportPage().includes('Recorded personal bests')&&reportPage().includes('Waist / hip')`);
check('local save valid after edit',`validPro(JSON.parse(localStorage.getItem(KEY)))`);
console.log('ALL CORE TESTS PASSED (simulated DOM)');
(async()=>{
let row=null;
ctx.fetch=async(url,opts)=>{const u=new URL(url),body=opts.body?JSON.parse(opts.body):null;let result,status=200;if(u.pathname.endsWith('/token'))result={access_token:'mock-token',expires_in:3600,user:{id:'mock-user'}};else if(u.pathname.endsWith('/fitlog_snapshots')){assert.equal(opts.headers.Authorization,'Bearer mock-token');if(!opts.method||opts.method==='GET')result=row?[structuredClone(row)]:[];else if(opts.method==='POST'){assert.equal(body.user_id,'mock-user');row={...body};result=[row];}else if(opts.method==='PATCH'){const revision=Number(u.searchParams.get('revision').replace('eq.',''));if(revision===row.revision){row={...row,...body};result=[row];}else result=[];}else throw Error('unknown method');}else throw Error('unexpected URL');return {ok:status===200,status,text:async()=>JSON.stringify(result)};};
await run(`cloudLogin(new Map([['url','https://test.supabase.co'],['key','sb_publishable_test'],['email','test@example.com'],['password','not-real']]))`);
await run('cloudPush()');assert.equal(row.revision,1);assert.ok(row.payload.history.length>=2);assert.ok(!row.payload.photoBackup);console.log('PASS mocked cloud sign-in / initial push / photo exclusion');
row.revision=2;let blocked=false;try{await run('cloudPush()')}catch(e){blocked=e.message.includes('Cloud changed')};assert.ok(blocked);console.log('PASS stale cloud revision rejected');
await run('cloudPull()');assert.equal(run('cloudRevision'),2);await run('cloudPush()');assert.equal(row.revision,3);console.log('PASS mock cloud pull and revision-checked push');
const stores={state:new Map(),photos:new Map()};const fakeDB={transaction(names){const tx={objectStore(name){const map=stores[name];function req(fn){const q={};queueMicrotask(()=>{try{q.result=fn();q.onsuccess?.();}catch(e){q.error=e;tx.onerror?.();}});return q;}return {put(v,k){return req(()=>{map.set(k??v.id,v);return k??v.id;})},get(k){return req(()=>map.get(k))},getAll(){return req(()=>[...map.values()])},clear(){return req(()=>map.clear())},delete(k){return req(()=>map.delete(k))}};}};queueMicrotask(()=>queueMicrotask(()=>tx.oncomplete?.()));return tx;}};
ctx.fakeDB=fakeDB;run('dbPromise=Promise.resolve(fakeDB)');const before=run('state.history.length');await run(`restoreData({...clone(state),photoBackup:[{id:'photo-test',date:'2026-11-23',view:'Front',data:'data:image/jpeg;base64,/9gA'}]})`);assert.equal(stores.photos.size,1);assert.equal(run('photoCache.length'),1);assert.equal(run('state.history.length'),before);console.log('PASS mocked IndexedDB photo restore and state transaction');
console.log('ALL EXTENDED TESTS PASSED');
})().catch(e=>{console.error(e);process.exitCode=1;});

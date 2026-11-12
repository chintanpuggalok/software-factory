import { spawn } from 'node:child_process';
import { mkdtemp, readFile, mkdir, rm, writeFile, copyFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';

const browserDir = '/home/chint/.cache/ms-playwright/chromium-1243/chrome-linux64';
const html = path.resolve('artifacts/calculator-test/.factory-build/index.html');
const sandbox = await mkdtemp(path.join(tmpdir(), 'factory-browser-'));
await copyFile(html, path.join(sandbox, 'index.html'));
const screenshotDir = path.resolve('artifacts/calculator-test/screenshots');
await mkdir(screenshotDir, { recursive: true });
// Chrome's own sandbox is unavailable here. Bubblewrap isolates the browser instead.
// No network is available and the host home directory is hidden.
const child = spawn('bwrap', ['--ro-bind','/','/', '--tmpfs','/home', '--tmpfs','/tmp',
  '--dir','/tmp/browser', '--ro-bind',browserDir,'/tmp/browser', '--dir','/tmp/work', '--bind',sandbox,'/tmp/work',
  '--unshare-net', '--proc','/proc', '--dev','/dev',
  '--', '/tmp/browser/chrome', '--headless', '--no-sandbox', '--disable-gpu', '--no-first-run',
  '--disable-background-networking', '--remote-debugging-pipe', '--user-data-dir=/tmp/work/profile', 'about:blank'],
  {stdio:['ignore','ignore','pipe','pipe','pipe'], detached:true});
let stderr = ''; child.stderr.on('data', x => { stderr += x.toString(); });
let seq = 0, buf = Buffer.alloc(0); const waiting = new Map();
for (const stream of [child.stdio[3], child.stdio[4]]) stream.on('error', () => {});
child.stdio[4].on('data', chunk => {
  buf = Buffer.concat([buf, chunk]); let pos;
  while ((pos = buf.indexOf(0)) !== -1) {
    const message = buf.subarray(0,pos).toString(); buf = buf.subarray(pos+1);
    if (!message) continue;
    const msg = JSON.parse(message);
    if (msg.id && waiting.has(msg.id)) { const [resolve,reject]=waiting.get(msg.id); waiting.delete(msg.id); msg.error ? reject(Error(msg.error.message)) : resolve(msg.result); }
  }
});
child.on('exit', (code, signal) => { for (const [,reject] of waiting.values()) reject(Error(`Browser exited: ${code ?? signal}; ${stderr.slice(0,500)}`)); waiting.clear(); });
const send = (method, params = {}, sessionId) => new Promise((resolve,reject) => {
  const id=++seq; waiting.set(id,[resolve,reject]);
  child.stdio[3].write(JSON.stringify({id,method,params,...(sessionId ? {sessionId} : {})})+'\0');
});
try {
  const {targetId} = await send('Target.createTarget',{url:'file:///tmp/work/index.html'});
  const {sessionId} = await send('Target.attachToTarget',{targetId,flatten:true});
  const call = (method,params={}) => send(method,params,sessionId);
  const evaluate = async expression => { const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true}); if(r.exceptionDetails) throw Error(r.exceptionDetails.text); return r.result.value; };
  await call('Page.enable'); await call('Runtime.enable');
  let ready = false;
  for(let i=0;i<100;i++){ if(await evaluate('document.readyState === "complete" && typeof window.factoryCompute === "function"')){ready=true;break;} await new Promise(r=>setTimeout(r,100)); }
  assert(ready,'page did not load');
  assert.deepEqual(await evaluate(`(() => { const f=window.factoryCompute; return [f(2,'+',3),f(9,'-',4),f(3,'*',4),f(12,'/',3),f(0.1,'+',0.2)]; })()`),[5,5,12,4,0.3]);
  assert.equal(await evaluate(`(() => {try {window.factoryCompute(1,'/',0);return false;} catch(e) {return /zero/i.test(e.message);}})()`),true);
  await evaluate(`(() => { for (const key of ['2','+','3','Enter']) document.dispatchEvent(new KeyboardEvent('keydown',{key,bubbles:true})); })()`);
  assert.equal(await evaluate(`document.querySelector('#display').textContent`),'5');
  await evaluate(`document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))`);
  assert.equal(await evaluate(`document.querySelector('#display').textContent`),'0');
  await evaluate(`document.querySelector('[data-digit="7"]').click(); document.querySelector('[data-op="*"]').click(); document.querySelector('[data-digit="8"]').click(); document.querySelector('[data-action="equals"]').click()`);
  assert.equal(await evaluate(`document.querySelector('#display').textContent`),'56');
  await evaluate(`document.activeElement?.blur(); document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))`);
  for (const key of ['4','+','5','Enter']) {
    await call('Input.dispatchKeyEvent', {type:'keyDown', key});
    await call('Input.dispatchKeyEvent', {type:'keyUp', key});
  }
  assert.equal(await evaluate(`document.querySelector('#display').textContent`),'9','native browser keyboard');
  const scenarios = [
    [['2','+','3','*','4','Enter'], '20'],
    [['2','+','-','3','Enter'], '-1'],
    [['5','+','Enter'], '5'],
    [['2','+','3','Enter','Enter'], '5'],
    [['.','1','+','.','2','Enter'], '0.3'],
    [['1','/','0','Enter'], 'Cannot divide by zero'],
    [['1','/','0','Enter','7'], '7'],
  ];
  for (const [keys, expected] of scenarios) {
    await evaluate(`document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))`);
    await evaluate(`(() => {for (const key of ${JSON.stringify(keys)}) document.dispatchEvent(new KeyboardEvent('keydown',{key,bubbles:true}));})()`);
    assert.equal(await evaluate(`document.querySelector('#display').textContent`),expected, `keys: ${keys.join(' ')}`);
  }
  const contrastFailures = await evaluate(`(() => {
    function rgb(value){ const m=value.match(/rgba?\\(([^)]+)\\)/); return m ? m[1].split(',').map(Number) : null; }
    function lum(c){ const a=c.slice(0,3).map(x=>{x/=255;return x<=0.04045?x/12.92:((x+0.055)/1.055)**2.4}); return .2126*a[0]+.7152*a[1]+.0722*a[2]; }
    return [...document.querySelectorAll('body *')].filter(el=>[...el.childNodes].some(n=>n.nodeType===3 && n.textContent.trim()) && el.getBoundingClientRect().width>0).map(el=>{
      const s=getComputedStyle(el), fg=rgb(s.color); let p=el,bg;
      while(p){const c=rgb(getComputedStyle(p).backgroundColor); if(c && (c.length<4 || c[3]===1)){bg=c;break;} p=p.parentElement;}
      if(!fg || !bg)return null; const a=lum(fg),b=lum(bg),ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05); const large=parseFloat(s.fontSize)>=24 || (parseFloat(s.fontSize)>=18.66 && parseInt(s.fontWeight)>=700); return ratio<(large?3:4.5)?{text:el.textContent.trim().slice(0,45),ratio:Math.round(ratio*100)/100}:null;
    }).filter(Boolean);
  })()`);
  assert.deepEqual(contrastFailures, [], `Text contrast failures: ${JSON.stringify(contrastFailures)}`);
  const ax=await call('Accessibility.getFullAXTree');
  assert(ax.nodes.some(n=>n.role?.value==='button' && n.name?.value==='Add'),'Add button missing from accessibility tree');
  assert(ax.nodes.some(n=>n.role?.value==='status'),'Status region missing from accessibility tree');
  for(const [name,width,height] of [['mobile',375,812],['desktop',1365,900]]){
    await call('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});
    await evaluate('new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))');
    assert.equal(await evaluate('document.documentElement.scrollWidth <= window.innerWidth'),true,`${name} horizontal overflow`);
    const shot=await call('Page.captureScreenshot',{format:'png'});
    await writeFile(path.join(screenshotDir,`${name}.png`),Buffer.from(shot.data,'base64'));
  }
  console.log('PASS: isolated Chromium arithmetic, interaction scenarios, keyboard, clicks, accessibility roles, text contrast, mobile and desktop overflow');
  console.log('LIMIT: no screen-reader or human visual review');
} finally {
  try { process.kill(-child.pid, 'SIGKILL'); } catch {}
  for (const stream of [child.stderr, child.stdio[3], child.stdio[4]]) stream.destroy();
  await new Promise(resolve=>{if(child.exitCode!==null || child.signalCode!==null)resolve(); else {child.once('exit',resolve);setTimeout(resolve,3000);}});
  await rm(sandbox,{recursive:true,force:true});
}

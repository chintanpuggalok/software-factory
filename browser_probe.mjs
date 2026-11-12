import { spawn } from 'node:child_process';
import { mkdtemp, copyFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const [html, browser, acceptanceFlag] = process.argv.slice(2);
if (!html || !browser) throw Error('Usage: node browser_probe.mjs <html> <chromium>');
let acceptance=null;
if (acceptanceFlag === '--acceptance') {
  let input='';
  for await (const chunk of process.stdin) { input += chunk; if (input.length > 50000) throw Error('Acceptance contract too large'); }
  acceptance=JSON.parse(input);
  if (acceptance?.version!==1 || !Array.isArray(acceptance.actions) || acceptance.actions.length<1 || acceptance.actions.length>50) throw Error('Invalid acceptance contract');
}
const sandbox = await mkdtemp(path.join(tmpdir(), 'factory-browser-'));
await copyFile(path.resolve(html), path.join(sandbox, 'index.html'));
// Chromium runs without its internal sandbox only inside this isolated Bubblewrap process.
const args = ['--tmpfs','/', '--dir','/usr', '--ro-bind','/usr','/usr',
  '--symlink','usr/lib','/lib', '--symlink','usr/lib64','/lib64', '--dir','/etc',
  '--dir','/etc/fonts', '--ro-bind','/etc/fonts','/etc/fonts', '--dir','/tmp', '--tmpfs','/tmp',
  '--dir','/tmp/browser', '--ro-bind',path.dirname(browser),'/tmp/browser',
  '--dir','/tmp/work', '--bind',sandbox,'/tmp/work', '--unshare-net', '--unshare-pid',
  '--unshare-ipc', '--unshare-uts', '--die-with-parent', '--proc','/proc', '--dev','/dev',
  '--', `/tmp/browser/${path.basename(browser)}`, '--headless', '--no-sandbox', '--disable-gpu',
  '--no-first-run', '--disable-background-networking', '--remote-debugging-pipe',
  '--user-data-dir=/tmp/work/profile', 'about:blank'];
const child = spawn('bwrap', args, {stdio:['ignore','ignore','pipe','pipe','pipe'], detached:true,
  env:{PATH:'/usr/bin:/bin', HOME:'/tmp/work', LANG:'C.UTF-8'}});
let stderr=''; child.stderr.on('data',x=>{stderr+=x.toString();});
let seq=0, buf=Buffer.alloc(0); const waiting=new Map(); const errors=[];
for (const stream of [child.stdio[3],child.stdio[4]]) stream.on('error',()=>{});
child.stdio[4].on('data', chunk=>{
  buf=Buffer.concat([buf,chunk]); let pos;
  while((pos=buf.indexOf(0))!==-1){
    const raw=buf.subarray(0,pos).toString(); buf=buf.subarray(pos+1); if(!raw)continue;
    const msg=JSON.parse(raw);
    if(msg.method==='Runtime.exceptionThrown') errors.push(msg.params?.exceptionDetails?.text || 'JavaScript exception');
    if(msg.id && waiting.has(msg.id)){const [resolve,reject]=waiting.get(msg.id);waiting.delete(msg.id);msg.error?reject(Error(msg.error.message)):resolve(msg.result);}
  }
});
child.on('exit',(code,signal)=>{for(const [,reject] of waiting.values())reject(Error(`Browser exited: ${code ?? signal}; ${stderr.slice(0,500)}`));waiting.clear();});
const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{
  const id=++seq;waiting.set(id,[resolve,reject]);child.stdio[3].write(JSON.stringify({id,method,params,...(sessionId?{sessionId}:{})})+'\0');
});
try {
  const {targetId}=await send('Target.createTarget',{url:'about:blank'});
  const {sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
  const call=(method,params={})=>send(method,params,sessionId);
  const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value;};
  await call('Page.enable');await call('Runtime.enable');
  await call('Page.navigate',{url:'file:///tmp/work/index.html'});
  let ready=false;
  for(let i=0;i<100;i++){if(await evaluate('document.readyState === "complete" && location.pathname === "/tmp/work/index.html"')){ready=true;break;}await new Promise(r=>setTimeout(r,100));}
  if(!ready)throw Error('Page did not load');
  const acceptance_results=[];
  if(acceptance){
    for(const step of acceptance.actions){
      if(!step || typeof step.action !== 'string') throw Error('Invalid acceptance action');
      let passed=true, detail='';
      if(step.action==='reset'){
        await call('Page.reload');
        await new Promise(r=>setTimeout(r,100));
      } else if(step.action==='key' && typeof step.key==='string'){
        await call('Input.dispatchKeyEvent',{type:'keyDown',key:step.key});
        await call('Input.dispatchKeyEvent',{type:'keyUp',key:step.key});
      } else if(step.action==='click' && typeof step.selector==='string'){
        passed=await evaluate(`(() => {const el=document.querySelector(${JSON.stringify(step.selector)});if(!el)return false;el.click();return true;})()`);
        if(!passed)detail='Element not found';
      } else if(step.action==='expect_exists' && typeof step.selector==='string'){
        passed=await evaluate(`!!document.querySelector(${JSON.stringify(step.selector)})`);
        if(!passed)detail='Element not found';
      } else if(step.action==='expect_text' && typeof step.selector==='string' && typeof step.text==='string'){
        const actual=await evaluate(`document.querySelector(${JSON.stringify(step.selector)})?.textContent ?? null`);
        passed=actual===step.text;
        if(!passed)detail=`Expected ${JSON.stringify(step.text)}, got ${JSON.stringify(actual)}`;
      } else throw Error('Invalid acceptance action');
      acceptance_results.push({action:step.action,passed,detail});
      if(!passed)break;
    }
  }
  const checks=[];
  for(const [name,width,height] of [['mobile',375,812],['desktop',1365,900]]){
    await call('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});
    await evaluate('new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))');
    checks.push({name, width, height, no_horizontal_overflow:await evaluate('document.documentElement.scrollWidth <= window.innerWidth')});
  }
  const title=await evaluate('document.title');
  const body_visible=await evaluate('!!document.body && document.body.getBoundingClientRect().height > 0');
  const status=(body_visible && checks.every(x=>x.no_horizontal_overflow) && errors.length===0 && acceptance_results.every(x=>x.passed))?'passed':'failed';
  console.log(JSON.stringify({status,title,body_visible,viewports:checks,script_errors:errors,acceptance_results,
    scope:'page load, uncaught JavaScript errors, horizontal overflow, and supplied acceptance actions only; not complete accessibility or security verification'}));
} finally {
  try{process.kill(-child.pid,'SIGKILL');}catch{}
  for(const stream of [child.stderr,child.stdio[3],child.stdio[4]])stream.destroy();
  await new Promise(resolve=>{if(child.exitCode!==null || child.signalCode!==null)resolve();else{child.once('exit',resolve);setTimeout(resolve,3000);}});
  await rm(sandbox,{recursive:true,force:true});
}

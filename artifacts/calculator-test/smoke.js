'use strict';
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const html = fs.readFileSync(process.argv[2], 'utf8');
const match = html.match(/<script>([\s\S]*?)<\/script>/i);
assert(match, 'inline script missing');
const nodes = Object.fromEntries(['display', 'expression', 'announcement'].map(id => [id, {
  textContent: '', classList: { toggle() {} }
}]));
const listeners = {};
const document = {
  activeElement: null,
  getElementById(id) { return nodes[id]; },
  querySelectorAll() { return []; },
  querySelector() { return { addEventListener() {} }; },
  addEventListener(type, fn) { listeners[type] = fn; }
};
const context = { document, window: {}, HTMLButtonElement: function HTMLButtonElement() {} };
vm.runInNewContext(match[1], context, { timeout: 1000 });
const compute = context.window.factoryCompute;
assert.strictEqual(typeof compute, 'function');
for (const [a, op, b, expected] of [[2,'+',3,5], [9,'-',4,5], [3,'*',4,12], [12,'/',3,4], [0.1,'+',0.2,0.3]]) {
  assert.strictEqual(compute(a, op, b), expected);
}
assert.throws(() => compute(1, '/', 0));
function key(k) { listeners.keydown({ key:k, preventDefault() {}, ctrlKey:false, metaKey:false, altKey:false, isComposing:false }); }
for (const k of ['2', '+', '3', 'Enter']) key(k);
assert.strictEqual(nodes.display.textContent, '5');
key('Escape');
assert.strictEqual(nodes.display.textContent, '0');
for (const k of ['1', '/', '0', 'Enter']) key(k);
assert.match(nodes.display.textContent, /zero/i);
console.log('PASS: arithmetic, precision, keyboard sequence, clear, division-by-zero');
console.log('LIMIT: fake DOM only; no real browser, visual, or assistive technology check');

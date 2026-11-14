import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import factoryModule from '../extensions/factory.ts';
const factory = typeof factoryModule === 'function' ? factoryModule : factoryModule.default;

async function setup() {
  const commands = {};
  const sent = [];
  const notices = [];
  const pi = {
    registerCommand(name, command) { commands[name] = command; },
    registerShortcut() {},
    sendUserMessage(message, options) { sent.push({ message, options }); },
  };
  factory(pi);
  const ctx = { cwd: await mkdtemp(path.join(tmpdir(), 'factory-command-')), hasUI: true, isIdle: () => true,
    ui: { notify: (message) => notices.push(message), setWidget() {} } };
  return { commands, sent, notices, ctx };
}

test('factory starts an agent turn for a goal and resumes without a goal', async () => {
  const { commands, sent, ctx } = await setup();
  await commands.factory.handler('fix the login', ctx);
  await commands.factory.handler('', ctx);
  ctx.isIdle = () => false;
  await commands.factory.handler('resume', ctx);
  assert.equal(sent.length, 3);
  assert.match(sent[0].message, /factory-entry\/SKILL\.md/);
  assert.match(sent[0].message, /fix the login/);
  assert.match(sent[0].message, /implementation, and verification/);
  assert.match(sent[1].message, /current conversation or restore the saved goal/);
  assert.equal(sent[0].options, undefined);
  assert.equal(sent[2].options.deliverAs, 'followUp');
});

test('status does not start an agent and unsupported auto options fail visibly', async () => {
  const { commands, sent, notices, ctx } = await setup();
  await commands.factory.handler('status', ctx);
  await commands.factory.handler('fix login --runtime=opencode', ctx);
  assert.equal(sent.length, 0);
  assert.match(notices.at(-1), /not the agent-led run/);
});

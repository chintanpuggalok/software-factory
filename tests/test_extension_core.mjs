import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import {
  buildCoordinatorArgs,
  buildSimulationArgs,
  parsePlanArgs,
  readStatus,
  runCoordinator,
  summarizeStatus,
} from '../extensions/factory-core.mjs';

test('tokenizes quoted goals', () => {
  assert.deepEqual(parsePlanArgs('"a checklist app" --yes'), {
    goal: 'a checklist app',
    options: { yes: true, researchQuery: null, referenceUrls: [], acceptanceFile: null, build: false },
  });
});

test('parses value options and repeats reference URLs', () => {
  const result = parsePlanArgs('goal --research-query=market --reference-url=https://www.calculator.net/ --reference-url https://www.desmos.com/scientific');
  assert.equal(result.options.researchQuery, 'market');
  assert.equal(result.options.referenceUrls.length, 2);
});

test('rejects unknown options and missing values', () => {
  assert.match(parsePlanArgs('goal --bogus').error, /Unknown option/);
  assert.match(parsePlanArgs('goal --research-query').error, /needs a value/);
  assert.match(parsePlanArgs('goal --reference-url a --reference-url b --reference-url c --reference-url d').error, /three/);
  assert.match(parsePlanArgs('').error, /goal/);
  assert.match(parsePlanArgs('"unclosed').error, /Unclosed/);
  assert.match(parsePlanArgs('goal --yes=1').error, /does not take a value/);
});

test('builds exact coordinator arguments', () => {
  assert.deepEqual(buildSimulationArgs({ workspace: '/p', goal: 'demo' }), ['/p', '--goal', 'demo']);
  assert.deepEqual(buildCoordinatorArgs({
    workspace: '/p', goal: 'demo', build: true,
    options: { researchQuery: 'q', referenceUrls: ['https://a'], acceptanceFile: '/a.json' },
  }), ['/p', '--goal', 'demo', '--mode', 'pi-plan', '--subscription-confirmed', '--build-static',
    '--research-query', 'q', '--reference-url', 'https://a', '--acceptance-file', '/a.json']);
});

test('summarizes an empty project and a blocked plan', () => {
  assert.match(summarizeStatus({}), /No factory run/);
  const text = summarizeStatus({ plan: { goal: 'demo', stages: [{ name: 'idea', audit: 'PASS: ok' }], blocked: null } });
  assert.match(text, /Goal: demo/);
  assert.match(text, /idea \[PASS\]/);
  assert.match(text, /do not prove security/);
});

test('reads saved state and runs the simulator without model calls', async () => {
  const workspace = await mkdtemp(path.join(tmpdir(), 'factory-core-'));
  const result = await runCoordinator({
    script: path.resolve('factory.py'),
    workspace,
    args: buildSimulationArgs({ workspace, goal: 'demo' }),
  });
  assert.equal(result.code, 0, result.stderr);
  const status = await readStatus(workspace);
  assert.equal(status.simulated.goal, 'demo');
  assert.match(summarizeStatus(status), /Simulation: demo/);
  const raw = JSON.parse(await readFile(path.join(workspace, '.factory', 'state.json'), 'utf8'));
  assert.equal(raw.stages.length, 8);
});

test('reports a coordinator failure instead of throwing', async () => {
  const workspace = await mkdtemp(path.join(tmpdir(), 'factory-core-fail-'));
  const result = await runCoordinator({ script: path.resolve('factory.py'), workspace, args: ['/missing', '--goal', 'x'] });
  assert.equal(result.code, 2);
  assert.match(result.stderr, /BLOCKED/);
});

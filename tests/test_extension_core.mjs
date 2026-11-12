import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import {
  applyProgress,
  buildCoordinatorArgs,
  buildSimulationArgs,
  emptyModel,
  nextAction,
  parseFactoryArgs,
  parsePlanArgs,
  parseProgress,
  readStatus,
  renderRunLines,
  runCoordinator,
  summarizeStatus,
  verificationFromStatus,
} from '../extensions/factory-core.mjs';

test('tokenizes quoted goals', () => {
  assert.deepEqual(parsePlanArgs('"a checklist app" --yes'), {
    goal: 'a checklist app',
    options: { yes: true, researchQuery: null, referenceUrls: [], acceptanceFile: null, build: false, simulate: false },
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
  assert.deepEqual(buildSimulationArgs({ workspace: '/p', goal: 'demo' }), ['/p', '--goal', 'demo', '--progress']);
  assert.deepEqual(buildCoordinatorArgs({
    workspace: '/p', goal: 'demo', build: true,
    options: { researchQuery: 'q', referenceUrls: ['https://a'], acceptanceFile: '/a.json' },
  }), ['/p', '--goal', 'demo', '--progress', '--mode', 'pi-plan', '--subscription-confirmed', '--build-static',
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

test('renders a bounded run box with stage glyphs', () => {
  let model = emptyModel({ goal: 'demo' });
  model = applyProgress(model, { event: 'stage_start', stage: 'idea' });
  model = applyProgress(model, { event: 'stage_result', stage: 'idea', passed: true, verdict: 'PASS: ok' });
  model = applyProgress(model, { event: 'stage_start', stage: 'spec' });
  model.verification = { static: 'passed', browser: 'passed' };
  const lines = renderRunLines(model, 64);
  assert.equal(lines[0].startsWith('╭'), true);
  assert.equal(lines.at(-1).startsWith('╰'), true);
  assert(lines.some((line) => line.includes('✓ idea')));
  assert(lines.some((line) => line.includes('● spec')));
  assert(lines.some((line) => line.includes('static passed · browser passed')));
  assert(lines.every((line) => Array.from(line).length <= 64));
  const narrow = renderRunLines(model, 30);
  assert(narrow.every((line) => Array.from(line).length <= 30));
});

test('shows a blocker and ignores invalid progress', () => {
  let model = emptyModel({ goal: 'demo' });
  model = applyProgress(model, { event: 'stage_start', stage: 'design' });
  model = applyProgress(model, { event: 'stage_result', stage: 'design', passed: false, verdict: 'BLOCKED: no evidence' });
  assert.match(renderRunLines(model, 80).join('\n'), /blocked at design: BLOCKED: no evidence/);
  assert.equal(parseProgress('not a progress line'), null);
  assert.equal(parseProgress('PROGRESS {bad json'), null);
  assert.deepEqual(parseProgress('PROGRESS {"event":"stage_start","stage":"spec"}'),
    { event: 'stage_start', stage: 'spec' });
});

test('maps saved verification to the widget line', () => {
  assert.deepEqual(verificationFromStatus({ verification: { status: 'passed' }, browser: { browser: { status: 'unavailable' } } }),
    { static: 'passed', browser: 'unavailable' });
  assert.equal(verificationFromStatus({}), null);
});

test('resolves the next action from saved state', () => {
  const plan = (stages) => ({ plan: { goal: 'g', stages } });
  const pass = (name) => ({ name, audit: 'PASS: ok' });
  assert.equal(nextAction({}), 'plan');
  assert.equal(nextAction(plan([pass('idea')])), 'plan');
  assert.equal(nextAction({ plan: { goal: 'g', stages: [pass('idea')], blocked: { stage: 'idea' } } }), 'resume-plan');
  assert.equal(nextAction(plan(['idea', 'spec', 'design', 'architecture', 'plan'].map(pass))), 'build');
  assert.equal(nextAction({ ...plan(['idea', 'spec', 'design', 'architecture', 'plan'].map(pass)), verification: { status: 'passed' } }), 'done');
});

test('parses the single entry command without a goal', () => {
  assert.deepEqual(parseFactoryArgs(''), { goal: '', options: { yes: false, researchQuery: null, referenceUrls: [], acceptanceFile: null, build: false, simulate: false } });
  assert.equal(parseFactoryArgs('--simulate').options.simulate, true);
  assert.match(parsePlanArgs('goal --simulate').error, /Unknown option/);
});

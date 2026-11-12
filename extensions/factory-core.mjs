/**
 * Pure helpers for the factory Pi extension.
 *
 * This module has no Pi imports so it can be tested with plain Node.
 * It never runs a model. It only prepares arguments, reads local state, and
 * spawns the existing coordinator.
 */
import { spawn } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import path from 'node:path';

export function tokenize(text) {
  const tokens = [];
  let current = '';
  let quote = null;
  let started = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (quote) {
      if (ch === quote) quote = null;
      else current += ch;
      continue;
    }
    if (ch === '"' || ch === "'") { quote = ch; started = true; continue; }
    if (/\s/.test(ch)) {
      if (started || current) { tokens.push(current); current = ''; started = false; }
      continue;
    }
    current += ch;
  }
  if (quote) return { error: 'Unclosed quote' };
  if (started || current) tokens.push(current);
  return { tokens };
}

const VALUE_FLAGS = {
  '--research-query': 'researchQuery',
  '--reference-url': 'referenceUrl',
  '--acceptance-file': 'acceptanceFile',
};

export function parsePlanArgs(text) {
  const { tokens, error } = tokenize(text || '');
  if (error) return { error };
  const options = { yes: false, researchQuery: null, referenceUrls: [], acceptanceFile: null, build: false };
  const goal = [];
  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    if (!token.startsWith('--')) { goal.push(token); continue; }
    const split = token.indexOf('=');
    const name = split === -1 ? token : token.slice(0, split);
    let value = split === -1 ? null : token.slice(split + 1);
    if (name === '--yes' || name === '--build') {
      if (split !== -1) return { error: `${name} does not take a value` };
      if (name === '--yes') options.yes = true; else options.build = true;
      continue;
    }
    if (!(name in VALUE_FLAGS)) return { error: `Unknown option ${name}` };
    if (value === null) {
      value = tokens[++i];
      if (value === undefined || value.startsWith('--')) return { error: `${name} needs a value` };
    }
    if (name === '--reference-url') options.referenceUrls.push(value);
    else options[VALUE_FLAGS[name]] = value;
  }
  if (!goal.length) return { error: 'A goal is required' };
  if (options.referenceUrls.length > 3) return { error: 'At most three reference URLs' };
  if (options.researchQuery && options.researchQuery.length > 200) return { error: 'Research query is too long' };
  return { goal: goal.join(' '), options };
}

export function buildCoordinatorArgs({ workspace, goal, options = {}, build = false }) {
  if (!workspace || !goal) throw new Error('workspace and goal are required');
  const args = [workspace, '--goal', goal, '--progress'];
  if (build) {
    args.push('--mode', 'pi-plan', '--subscription-confirmed', '--build-static');
    if (options.researchQuery) args.push('--research-query', options.researchQuery);
    for (const url of options.referenceUrls || []) args.push('--reference-url', url);
    if (options.acceptanceFile) args.push('--acceptance-file', options.acceptanceFile);
  }
  return args;
}

export function buildSimulationArgs({ workspace, goal }) {
  if (!workspace || !goal) throw new Error('workspace and goal are required');
  return [workspace, '--goal', goal, '--progress'];
}

export function runCoordinator({ python = 'python3', script, workspace, args, onLine, timeoutMs = 900000 }) {
  return new Promise((resolve) => {
    const child = spawn(python, [script, ...args], { cwd: workspace, env: process.env });
    let stdout = '';
    let stderr = '';
    const emit = (chunk, stream) => {
      const text = chunk.toString();
      if (stream === 'stdout') stdout += text; else stderr += text;
      if (!onLine) return;
      for (const line of text.split('\n')) {
        if (line.trim()) onLine(line.trim(), stream);
      }
    };
    const timer = setTimeout(() => {
      child.kill('SIGTERM');
      resolve({ code: null, stdout, stderr, error: `Timed out after ${timeoutMs} ms` });
    }, timeoutMs);
    child.stdout.on('data', (chunk) => emit(chunk, 'stdout'));
    child.stderr.on('data', (chunk) => emit(chunk, 'stderr'));
    child.on('error', (error) => { clearTimeout(timer); resolve({ code: null, stdout, stderr, error: error.message }); });
    child.on('close', (code) => { clearTimeout(timer); resolve({ code, stdout, stderr }); });
  });
}

async function readJson(file) {
  try { return JSON.parse(await readFile(file, 'utf8')); } catch { return null; }
}

export async function readStatus(workspace) {
  const plan = await readJson(path.join(workspace, '.factory', 'pi-plan.json'));
  const simulated = await readJson(path.join(workspace, '.factory', 'state.json'));
  const verification = await readJson(path.join(workspace, '.factory-build', 'verification.json'));
  const browser = await readJson(path.join(workspace, '.factory-build', 'browser-evidence.json'));
  return { plan, simulated, verification, browser };
}

export function summarizeStatus(status) {
  const lines = [];
  const plan = status.plan;
  if (plan && Array.isArray(plan.stages)) {
    lines.push(`Goal: ${plan.goal}`);
    lines.push(`Runtime: ${plan.runtime || 'unknown'}`);
    lines.push(`Stages: ${plan.stages.length ? plan.stages.map((s) => `${s.name} [${String(s.audit).split(':')[0]}]`).join(', ') : 'none'}`);
    if (plan.blocked) lines.push(`Blocked at ${plan.blocked.stage}: ${String(plan.blocked.audit).slice(0, 200)}`);
  } else if (status.simulated && Array.isArray(status.simulated.stages)) {
    lines.push(`Simulation: ${status.simulated.goal}`);
    lines.push(`Stages: ${status.simulated.stages.map((s) => `${s.name} [${s.status}]`).join(', ')}`);
  } else {
    lines.push('No factory run found in this project.');
  }
  if (status.verification) {
    lines.push(`Prototype checks: ${status.verification.status || 'unknown'}`);
  }
  if (status.browser && status.browser.browser) {
    lines.push(`Browser: ${status.browser.browser.status} (repair attempted: ${status.browser.repair_attempted ? 'yes' : 'no'})`);
  }
  lines.push('Static and browser checks do not prove security, full accessibility, or production readiness.');
  return lines.join('\n');
}

export const PLANNING_STAGES = ['idea', 'spec', 'design', 'architecture', 'plan'];

export function emptyModel({ goal, runtime = 'pi', limit = 10 }) {
  return {
    goal,
    runtime,
    limit,
    stages: PLANNING_STAGES.map((name) => ({ name, state: 'pending', verdict: '' })),
    blocked: null,
    verification: null,
  };
}

export function parseProgress(line) {
  if (typeof line !== 'string' || !line.startsWith('PROGRESS ')) return null;
  try {
    const event = JSON.parse(line.slice('PROGRESS '.length));
    return event && typeof event.event === 'string' ? event : null;
  } catch {
    return null;
  }
}

export function applyProgress(model, event) {
  if (!event || !model) return model;
  const row = model.stages?.find((stage) => stage.name === event.stage);
  if (event.event === 'stage_start' && row) {
    row.state = 'running';
    row.verdict = '';
  }
  if (event.event === 'stage_result' && row) {
    row.state = event.passed ? 'passed' : 'blocked';
    row.verdict = typeof event.verdict === 'string' ? event.verdict : '';
    if (!event.passed) model.blocked = { stage: event.stage, verdict: row.verdict };
  }
  return model;
}

const GLYPH = { pending: '○', running: '●', passed: '✓', blocked: '✗', revise: '!' };

function clip(text, width) {
  const chars = Array.from(String(text));
  if (chars.length <= width) return String(text);
  return chars.slice(0, Math.max(0, width - 1)).join('') + '…';
}

function padRight(text, width) {
  const value = clip(text, width);
  return value + ' '.repeat(Math.max(0, width - Array.from(value).length));
}

export function renderRunLines(model, width = 64) {
  const inner = Math.max(24, Math.min(96, width)) - 2;
  const lines = [];
  const title = ' factory ';
  const side = Math.max(0, inner - title.length);
  lines.push('╭' + '─'.repeat(Math.floor(side / 2)) + title + '─'.repeat(side - Math.floor(side / 2)) + '╮');
  const put = (text) => lines.push('│ ' + padRight(text, inner - 1) + '│');
  put(clip(model.goal || 'untitled run', inner));
  const done = model.stages.filter((s) => s.state === 'passed').length;
  put(`${model.runtime} · ${done}/${model.stages.length} stages · up to ${model.limit} calls · no dollar limit`);
  put('');
  const visible = model.stages.slice(0, 6);
  for (const stage of visible) {
    const label = `${GLYPH[stage.state] || '·'} ${padRight(stage.name, 14)}${stage.state === 'running' ? 'auditing…' : stage.state}`;
    put(label);
  }
  if (model.stages.length > visible.length) put(`… +${model.stages.length - visible.length} more stages`);
  if (model.blocked) put(clip(`blocked at ${model.blocked.stage}: ${model.blocked.verdict}`, inner));
  if (model.verification) {
    put(clip(`static ${model.verification.static || 'unknown'} · browser ${model.verification.browser || 'unknown'}`, inner));
  }
  put('');
  put('/factory-status for detail · ctrl+c stops the run');
  lines.push('╰' + '─'.repeat(inner) + '╯');
  return lines;
}

export function verificationFromStatus(status) {
  if (!status) return null;
  const staticCheck = status.verification?.status;
  const browser = status.browser?.browser?.status;
  if (!staticCheck && !browser) return null;
  return { static: staticCheck || 'unknown', browser: browser || 'unknown' };
}

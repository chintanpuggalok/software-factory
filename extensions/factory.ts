import { fileURLToPath } from 'node:url';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import type { ExtensionAPI } from '@earendil-works/pi-coding-agent';
import {
  applyProgress,
  buildCoordinatorArgs,
  buildSimulationArgs,
  emptyModel,
  parsePlanArgs,
  parseProgress,
  readStatus,
  renderRunLines,
  runCoordinator,
  summarizeStatus,
  verificationFromStatus,
} from './factory-core.mjs';

const PACKAGE_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SCRIPT = path.join(PACKAGE_ROOT, 'factory.py');
const CACHE = '.factory/extension.json';

function output(ctx: any, text: string) {
  if (ctx.mode === 'print') process.stdout.write(text + '\n');
  else if (ctx.hasUI) ctx.ui.notify(text, 'info');
}

async function remember(workspace: string, record: unknown) {
  await mkdir(path.join(workspace, '.factory'), { recursive: true });
  await writeFile(path.join(workspace, '.factory', 'extension.json'), JSON.stringify(record, null, 2) + '\n');
}

async function recall(workspace: string) {
  try { return JSON.parse(await readFile(path.join(workspace, CACHE), 'utf8')); } catch { return null; }
}

async function confirmSpend(ctx: any, args: string, calls: number) {
  const { goal, options, error } = parsePlanArgs(args);
  if (error) return { error };
  if (ctx.hasUI) {
    const ok = await ctx.ui.confirm(
      'Run factory model calls?',
      `Up to ${calls} calls with no dollar limit enforced. Goal: ${goal}`,
    );
    if (!ok) return { cancelled: true };
    return { goal, options };
  }
  if (!options.yes) {
    return { error: 'Non-interactive use requires --yes to confirm model calls with no dollar limit.' };
  }
  return { goal, options };
}

function paint(ctx: any, model: any) {
  const width = Math.max(40, Math.min(96, process.stdout.columns || 64));
  ctx.ui.setWidget?.('factory-status', renderRunLines(model, width), { placement: 'aboveEditor' });
}

async function run(ctx: any, args: string[], workspace: string, model: any) {
  ctx.ui.setStatus?.('factory', 'running…');
  paint(ctx, model);
  const result = await runCoordinator({
    script: SCRIPT,
    workspace,
    args,
    onLine: (line: string, stream: string) => {
      if (stream === 'stderr' && line.startsWith('BLOCKED')) ctx.ui.notify?.(line, 'error');
      const event = parseProgress(line);
      if (event) {
        applyProgress(model, event);
        paint(ctx, model);
      }
    },
  });
  model.verification = verificationFromStatus(await readStatus(workspace));
  paint(ctx, model);
  ctx.ui.setStatus?.('factory', undefined);
  return result;
}

export default function (pi: ExtensionAPI) {
  pi.registerCommand('factory-status', {
    description: 'Show the factory run, plan stages, and verification state',
    handler: async (_args, ctx) => {
      output(ctx, summarizeStatus(await readStatus(ctx.cwd)));
    },
  });

  pi.registerCommand('factory-simulate', {
    description: 'Run the deterministic factory simulation. No model calls',
    handler: async (args, ctx) => {
      const { goal, error } = parsePlanArgs(args);
      if (error) return output(ctx, `Error: ${error}`);
      const model = emptyModel({ goal, runtime: 'simulate', limit: 0 });
      const result = await run(ctx, buildSimulationArgs({ workspace: ctx.cwd, goal }), ctx.cwd, model);
      if (result.error) return output(ctx, `Error: ${result.error}`);
      output(ctx, summarizeStatus(await readStatus(ctx.cwd)));
      if (result.code !== 0) output(ctx, `Simulation stopped with code ${result.code}.`);
    },
  });

  pi.registerCommand('factory-plan', {
    description: 'Run idea through plan with real model calls. Requires spend confirmation',
    handler: async (args, ctx) => {
      const parsed = await confirmSpend(ctx, args, 10);
      if (parsed.cancelled) return output(ctx, 'Cancelled.');
      if (parsed.error) return output(ctx, `Error: ${parsed.error}`);
      await remember(ctx.cwd, { action: 'plan', goal: parsed.goal, options: parsed.options });
      const model = emptyModel({ goal: parsed.goal, limit: 10 });
      const result = await run(ctx,
        buildCoordinatorArgs({ workspace: ctx.cwd, goal: parsed.goal, options: parsed.options }),
        ctx.cwd, model);
      if (result.error) return output(ctx, `Error: ${result.error}`);
      output(ctx, summarizeStatus(await readStatus(ctx.cwd)));
      if (result.code !== 0) {
        const blocked = result.stderr.split('\n').filter((l) => l.startsWith('BLOCKED')).join('\n');
        output(ctx, blocked || `Plan stopped with code ${result.code}.`);
      }
    },
  });

  pi.registerCommand('factory-build', {
    description: 'Generate and verify one static prototype from a completed plan. Requires spend confirmation',
    getArgumentCompletions: (prefix: string) => {
      const items = ['--yes', '--research-query=', '--reference-url=', '--acceptance-file='];
      const matches = items.filter((i) => i.startsWith(prefix));
      return matches.length ? matches.map((value) => ({ value, label: value })) : null;
    },
    handler: async (args, ctx) => {
      const parsed = await confirmSpend(ctx, args, 3);
      if (parsed.cancelled) return output(ctx, 'Cancelled.');
      if (parsed.error) return output(ctx, `Error: ${parsed.error}`);
      await remember(ctx.cwd, { action: 'build', goal: parsed.goal, options: parsed.options });
      const model = emptyModel({ goal: parsed.goal, limit: 13 });
      const result = await run(ctx,
        buildCoordinatorArgs({ workspace: ctx.cwd, goal: parsed.goal, options: parsed.options, build: true }),
        ctx.cwd, model);
      if (result.error) return output(ctx, `Error: ${result.error}`);
      output(ctx, summarizeStatus(await readStatus(ctx.cwd)));
      if (result.code !== 0) {
        const blocked = result.stderr.split('\n').filter((l) => l.startsWith('BLOCKED')).join('\n');
        output(ctx, blocked || `Build stopped with code ${result.code}.`);
      }
    },
  });

  pi.registerCommand('factory-resume', {
    description: 'Repeat the last plan or build command for this project',
    handler: async (_args, ctx) => {
      const last = await recall(ctx.cwd);
      if (!last || !last.goal) return output(ctx, 'No saved factory command in this project.');
      if (ctx.hasUI) {
        const ok = await ctx.ui.confirm('Resume factory run?',
          `Repeat the last ${last.action} run. Model calls have no dollar limit. Goal: ${last.goal}`);
        if (!ok) return output(ctx, 'Cancelled.');
      }
      const build = last.action === 'build';
      const model = emptyModel({ goal: last.goal, limit: build ? 13 : 10 });
      const result = await run(ctx,
        buildCoordinatorArgs({ workspace: ctx.cwd, goal: last.goal, options: last.options || {}, build }),
        ctx.cwd, model);
      if (result.error) return output(ctx, `Error: ${result.error}`);
      output(ctx, summarizeStatus(await readStatus(ctx.cwd)));
      if (result.code !== 0) output(ctx, `Resume stopped with code ${result.code}.`);
    },
  });
}

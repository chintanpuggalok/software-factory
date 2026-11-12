import { fileURLToPath } from 'node:url';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import type { ExtensionAPI } from '@earendil-works/pi-coding-agent';
import {
  applyProgress,
  buildCoordinatorArgs,
  buildSimulationArgs,
  emptyModel,
  modelFromStatus,
  renderIdleLines,
  nextAction,
  nextActionHint,
  parseFactoryCommand,
  parseFactoryArgs,
  parsePlanArgs,
  parseProgress,
  readEntry,
  readStatus,
  renderRunLines,
  runCoordinator,
  summarizeStatus,
  verificationFromStatus,
  writeEntry,
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

async function confirmGoal(ctx: any, goal: string, calls: number, assumeYes = false) {
  if (ctx.hasUI) {
    const ok = await ctx.ui.confirm(
      'Run factory model calls?',
      `Up to ${calls} calls with no dollar limit enforced. Goal: ${goal}`,
    );
    return ok ? { ok: true } : { cancelled: true };
  }
  if (!assumeYes) {
    return { error: 'Non-interactive use requires --yes to confirm model calls with no dollar limit.' };
  }
  return { ok: true };
}

async function confirmSpend(ctx: any, args: string, calls: number) {
  const { goal, options, error } = parsePlanArgs(args);
  if (error) return { error };
  const confirmed = await confirmGoal(ctx, goal, calls, options.yes);
  if (!confirmed.ok) return confirmed;
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
  async function showStatus(ctx: any, goalHint = '') {
    const status = await readStatus(ctx.cwd);
    const entry = await readEntry(ctx.cwd);
    const goal = goalHint || status.plan?.goal || entry?.goal || '';
    if (!goal && !status.plan && !status.simulated && !status.verification) {
      const width = Math.max(40, Math.min(96, process.stdout.columns || 64));
      ctx.ui.setWidget?.('factory-status', renderIdleLines(width), { placement: 'aboveEditor' });
      return output(ctx, 'No factory run in this project.\n/factory <goal>   plan, build, and verify\n/factory help     all commands');
    }
    const model = modelFromStatus(status, goal);
    model.next = nextActionHint(nextAction(status));
    paint(ctx, model);
    output(ctx, `${summarizeStatus(status)}\n${model.next}`);
    return { status, model };
  }

  pi.registerCommand('factory', {
    description: 'Factory entry: status, plan, build, simulate, resume, help',
    getArgumentCompletions: (prefix: string) => {
      const items = ['status', 'plan', 'build', 'simulate', 'resume', 'help',
        '--yes', '--simulate', '--research-query=', '--reference-url=', '--acceptance-file='];
      const matches = items.filter((i) => i.startsWith(prefix));
      return matches.length ? matches.map((value) => ({ value, label: value })) : null;
    },
    handler: async (args, ctx) => {
      const parsed = parseFactoryCommand(args);
      if (parsed.error) return output(ctx, `Error: ${parsed.error}`);

      if (parsed.command === 'help') {
        return output(ctx, [
          '/factory                  show status and the next step',
          '/factory status           show saved state',
          '/factory <goal>           plan, then build and verify',
          '/factory plan <goal>      plan only',
          '/factory build            build and verify from a passed plan',
          '/factory simulate <goal>  free eight-stage simulation',
          '/factory resume           repeat the last plan or build',
          'options: --yes --research-query= --reference-url= --acceptance-file=',
        ].join('\n'));
      }
      if (parsed.command === 'status') return void await showStatus(ctx, parsed.goal);

      const saved = await readEntry(ctx.cwd);
      const goal = parsed.goal || saved?.goal;
      if (parsed.command === 'resume') {
        if (!saved?.goal) return output(ctx, 'No saved factory command. Start with /factory <goal>.');
        return void await showStatus(ctx, saved.goal);
      }
      if (parsed.command === 'build') {
        if (!goal) return output(ctx, 'No saved goal. Start with /factory <goal>.');
        await writeEntry(ctx.cwd, { version: 1, goal, updatedAt: new Date().toISOString() });
        const status = await readStatus(ctx.cwd);
        if (nextAction(status) !== 'build' && nextAction(status) !== 'done') {
          return output(ctx, 'No passed plan yet. Run /factory plan <goal> first.');
        }
        if (nextAction(status) === 'done') return void await showStatus(ctx, goal);
        const confirmed = await confirmGoal(ctx, goal, 3, parsed.options.yes);
        if (confirmed.cancelled) return output(ctx, 'Cancelled.');
        if (confirmed.error) return output(ctx, `Error: ${confirmed.error}`);
        const model = emptyModel({ goal, limit: 3 });
        const result = await run(ctx,
          buildCoordinatorArgs({ workspace: ctx.cwd, goal, options: parsed.options, build: true }), ctx.cwd, model);
        model.next = nextActionHint('done');
        paint(ctx, model);
        if (result.code !== 0) {
          const blocked = result.stderr.split('\n').filter((l: string) => l.startsWith('BLOCKED')).join('\n');
          return output(ctx, blocked || `Build stopped with code ${result.code}.`);
        }
        return void await showStatus(ctx, goal);
      }

      if (!goal) return output(ctx, 'No goal yet. Use /factory <goal> or /factory help.');

      await writeEntry(ctx.cwd, { version: 1, goal, updatedAt: new Date().toISOString() });

      if (parsed.command === 'simulate') {
        const model = emptyModel({ goal, runtime: 'simulate', limit: 0 });
        model.next = 'simulated run only · no model calls';
        const result = await run(ctx, buildSimulationArgs({ workspace: ctx.cwd, goal }), ctx.cwd, model);
        paint(ctx, model);
        output(ctx, summarizeStatus(await readStatus(ctx.cwd)));
        if (result.code !== 0) output(ctx, `Simulation stopped with code ${result.code}.`);
        return;
      }

      const before = await readStatus(ctx.cwd);
      const action = parsed.command === 'plan' ? 'plan' : nextAction(before);
      if (action === 'done') return void await showStatus(ctx, goal);
      const calls = action === 'build' ? 3 : 13;
      const confirmed = await confirmGoal(ctx, goal, calls, parsed.options.yes);
      if (confirmed.cancelled) return output(ctx, 'Cancelled.');
      if (confirmed.error) return output(ctx, `Error: ${confirmed.error}`);

      let model = emptyModel({ goal, limit: calls });
      if (action === 'plan' || action === 'resume-plan') {
        const plan = await run(ctx,
          buildCoordinatorArgs({ workspace: ctx.cwd, goal, options: parsed.options }), ctx.cwd, model);
        if (plan.code !== 0) {
          paint(ctx, model);
          const blocked = plan.stderr.split('\n').filter((l: string) => l.startsWith('BLOCKED')).join('\n');
          return output(ctx, blocked || `Plan stopped with code ${plan.code}.`);
        }
      }
      const afterPlan = await readStatus(ctx.cwd);
      if (nextAction(afterPlan) === 'build') {
        model = emptyModel({ goal, limit: 3 });
        const build = await run(ctx,
          buildCoordinatorArgs({ workspace: ctx.cwd, goal, options: parsed.options, build: true }), ctx.cwd, model);
        if (build.code !== 0) {
          paint(ctx, model);
          const blocked = build.stderr.split('\n').filter((l: string) => l.startsWith('BLOCKED')).join('\n');
          return output(ctx, blocked || `Build stopped with code ${build.code}.`);
        }
      }
      await remember(ctx.cwd, { action: 'factory', goal, options: parsed.options });
      await showStatus(ctx, goal);
    },
  });

  pi.registerCommand('factory-status', {
    description: 'Show the factory run, plan stages, and verification state',
    handler: async (_args, ctx) => { await showStatus(ctx); },
  });


}

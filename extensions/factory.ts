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
  parseProgress,
  presentStageSummary,
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

async function recall(workspace: string): Promise<any> {
  try { return JSON.parse(await readFile(path.join(workspace, CACHE), 'utf8')); } catch { return null; }
}

async function remember(workspace: string, patch: Record<string, unknown>) {
  const prev = (await recall(workspace)) || {};
  const next = { ...prev, ...patch };
  await mkdir(path.join(workspace, '.factory'), { recursive: true });
  await writeFile(path.join(workspace, CACHE), JSON.stringify(next, null, 2) + '\n');
  return next;
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

export default function (pi: ExtensionAPI) {
  let collapsedState = false;
  let activeModel: any = null;

  function paint(ctx: any, model: any) {
    activeModel = model;
    const width = Math.max(1, Math.min(96, process.stdout.columns || 64));
    const lines = renderRunLines(model, width, { collapsed: collapsedState });
    ctx.ui.setWidget?.('factory-status', lines, { placement: 'aboveEditor' });
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

  async function showStatus(ctx: any, goalHint = '') {
    const cached = await recall(ctx.cwd);
    if (typeof cached?.collapsed === 'boolean') collapsedState = cached.collapsed;
    const status = await readStatus(ctx.cwd);
    const entry = await readEntry(ctx.cwd);
    const goal = goalHint || status.plan?.goal || entry?.goal || '';
    if (!goal && !status.plan && !status.simulated && !status.verification) {
      const width = Math.max(1, Math.min(96, process.stdout.columns || 64));
      ctx.ui.setWidget?.('factory-status', renderIdleLines(width, { collapsed: collapsedState }), { placement: 'aboveEditor' });
      return output(ctx, 'No factory run in this project.\n/factory <goal>   plan, build, and verify\n/factory help     all commands');
    }
    const model = modelFromStatus(status, goal);
    model.collapsed = collapsedState;
    model.next = nextActionHint(nextAction(status));
    paint(ctx, model);
    const current = presentStageSummary(model);
    const text = collapsedState
      ? `${current.glyph} ${current.stage}: ${current.detail}${goal ? ` · ${goal}` : ''}`
      : `${summarizeStatus(status)}\n${model.next}`;
    output(ctx, text);
    return { status, model };
  }

  async function setCollapsed(ctx: any, nextCollapsed: boolean) {
    collapsedState = nextCollapsed;
    await remember(ctx.cwd, { collapsed: collapsedState });
    if (activeModel) {
      activeModel.collapsed = collapsedState;
      paint(ctx, activeModel);
      const current = presentStageSummary(activeModel);
      return output(ctx, collapsedState
        ? `Widget collapsed — ${current.glyph} ${current.stage}: ${current.detail}`
        : 'Widget expanded.');
    }
    await showStatus(ctx);
  }

  pi.registerShortcut?.('ctrl+shift+f', {
    description: 'Toggle factory widget collapse/expand',
    handler: async (ctx: any) => {
      await setCollapsed(ctx, !collapsedState);
    },
  });

  pi.registerCommand('factory', {
    description: 'Factory entry: <goal>, status, collapse, expand, toggle, hide, plan, build, simulate, resume, help',
    getArgumentCompletions: (prefix: string) => {
      const items = ['status', 'collapse', 'expand', 'toggle', 'hide', 'plan', 'build', 'simulate', 'resume', 'help',
        '--yes', '--collapsed', '--expand', '--simulate', '--research-query=', '--reference-url=', '--acceptance-file=', '--runtime='];
      const matches = items.filter((i) => i.startsWith(prefix));
      return matches.length ? matches.map((value) => ({ value, label: value })) : null;
    },
    handler: async (args, ctx) => {
      const parsed = parseFactoryCommand(args);
      if (parsed.error) return output(ctx, `Error: ${parsed.error}`);

      if (typeof parsed.options?.collapsed === 'boolean') {
        collapsedState = parsed.options.collapsed;
        await remember(ctx.cwd, { collapsed: collapsedState });
      } else {
        const cached = await recall(ctx.cwd);
        if (typeof cached?.collapsed === 'boolean') collapsedState = cached.collapsed;
      }

      if (parsed.command === 'help') {
        return output(ctx, [
          '/factory                  resume work or ask for a goal',
          '/factory <goal>           start end-to-end work in this project',
          '/factory collapse         collapse widget to present stage and status',
          '/factory expand           expand widget to full stage list',
          '/factory toggle           toggle collapsed/expanded widget (or ctrl+shift+f)',
          '/factory hide             hide the factory widget',
          '/factory status           show saved state',
          '/factory plan <goal>      plan only',
          '/factory build            build and verify from a passed plan',
          '/factory simulate <goal>  free eight-stage simulation',
          '/factory resume           repeat the last plan or build',
          'options: --yes --collapsed --expand --research-query= --reference-url= --acceptance-file= --runtime=pi|opencode',
        ].join('\n'));
      }
      if (parsed.command === 'collapse') return void await setCollapsed(ctx, true);
      if (parsed.command === 'expand') return void await setCollapsed(ctx, false);
      if (parsed.command === 'toggle') return void await setCollapsed(ctx, !collapsedState);
      if (parsed.command === 'hide') {
        ctx.ui.setWidget?.('factory-status', undefined);
        return output(ctx, 'Factory widget hidden.');
      }
      if (parsed.command === 'status') return void await showStatus(ctx, parsed.goal);

      if (parsed.command === 'auto' || parsed.command === 'resume') {
        if (ctx.mode === 'print') {
          return output(ctx, 'Agent-led /factory requires interactive Pi. Print mode cannot wait for the agent turn.');
        }
        const options = parsed.options;
        if (options.runtime || options.researchQuery || options.referenceUrls.length || options.acceptanceFile) {
          return output(ctx, 'These options apply to /factory plan or /factory build, not the agent-led run.');
        }
        const prompt = [
          `Read ${path.join(PACKAGE_ROOT, '.agents/skills/factory-entry/SKILL.md')} and follow it for this project.`,
          'Lead the authorized work end to end. Execute the appropriate stages, audits, implementation, and verification.',
          'Do not stop at a status display or an intermediate milestone. Respect approval and safety boundaries.',
          parsed.goal ? `The requested goal is: ${JSON.stringify(parsed.goal)}` : 'Use the current conversation or restore the saved goal. Ask only if neither supplies a goal.',
        ].join('\n');
        ctx.ui.setWidget?.('factory-status', undefined);
        if (ctx.isIdle()) pi.sendUserMessage(prompt);
        else pi.sendUserMessage(prompt, { deliverAs: 'followUp' });
        return;
      }
      const saved = await readEntry(ctx.cwd);
      const goal = parsed.goal || saved?.goal;
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
        const model = emptyModel({ goal, limit: 3, runtime: parsed.options.runtime || 'pi', collapsed: collapsedState });
        const result = await run(ctx,
          buildCoordinatorArgs({ workspace: ctx.cwd, goal, options: parsed.options, mode: 'build' }), ctx.cwd, model);
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
        const model = emptyModel({ goal, runtime: 'simulate', limit: 0, collapsed: collapsedState });
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

      let model = emptyModel({ goal, limit: calls, runtime: parsed.options.runtime || 'pi', collapsed: collapsedState });
      if (action === 'plan' || action === 'resume-plan') {
        const plan = await run(ctx,
          buildCoordinatorArgs({ workspace: ctx.cwd, goal, options: parsed.options, mode: 'plan' }), ctx.cwd, model);
        if (plan.code !== 0) {
          paint(ctx, model);
          const blocked = plan.stderr.split('\n').filter((l: string) => l.startsWith('BLOCKED')).join('\n');
          return output(ctx, blocked || `Plan stopped with code ${plan.code}.`);
        }
      }
      if (parsed.command === 'plan') return void await showStatus(ctx, goal);
      const afterPlan = await readStatus(ctx.cwd);
      if (nextAction(afterPlan) === 'build') {
        model = emptyModel({ goal, limit: 3, runtime: parsed.options.runtime || 'pi', collapsed: collapsedState });
        const build = await run(ctx,
          buildCoordinatorArgs({ workspace: ctx.cwd, goal, options: parsed.options, mode: 'build' }), ctx.cwd, model);
        if (build.code !== 0) {
          paint(ctx, model);
          const blocked = build.stderr.split('\n').filter((l: string) => l.startsWith('BLOCKED')).join('\n');
          return output(ctx, blocked || `Build stopped with code ${build.code}.`);
        }
      }
      await remember(ctx.cwd, { action: 'factory', goal, options: parsed.options, collapsed: collapsedState });
      await showStatus(ctx, goal);
    },
  });

  pi.registerCommand('factory-status', {
    description: 'Show the factory run, plan stages, and verification state',
    handler: async (_args, ctx) => { await showStatus(ctx); },
  });
}

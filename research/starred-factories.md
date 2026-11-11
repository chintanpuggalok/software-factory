# Starred factory research

Accessed 2026-11-11. Star counts are GitHub API snapshots, not quality measures. We reviewed primary READMEs, not implementations or benchmarks. No external code was installed.

| Source | Stars | Fit and recommendation | Prerequisites, cost, license | Limits and validation |
|---|---:|---|---|---|
| https://github.com/obra/superpowers | 316155 | Trial small plans, test-first bug repair, and verification evidence. | Agent and model access; MIT. | Full workflow can add latency. Test on small and complex tasks. |
| https://github.com/github/spec-kit | 149324 | Trial separate entry points for features, bugs, and idea assessment. | Agent and model access; MIT. | Specs can drift. Compare acceptance criteria to results. |
| https://github.com/garrytan/gstack | 141214 | Trial browser QA and security review. | Agent, browser, and model access; MIT. | README describes claimed behavior, not independent proof. Test actual browser coverage. |
| https://github.com/bmad-code-org/BMAD-METHOD | 55264 | Trial matching planning depth to task size. | Agent access; README says MIT, API reports NOASSERTION. Verify license before reuse. | Process can become heavy. Measure the handoff cost. |
| https://github.com/the-open-engine/zeroshot | 2140 | Trial fresh-context independent review for consequential work. | Agents, model access, and delegation authorization; MIT. | More agents add cost. Verify isolation and compare against direct work. |
| https://github.com/dzhng/skills | 1497 | Trial small, composable skills. | Agent and model access; MIT. | More skills add routing and context overhead. Test selection. |
| https://github.com/strongdm/attractor | 1341 | Study explicit specifications for an agent runtime and pipeline. | Implementation work and model access; Apache-2.0. | It is a set of specifications, not an installed engine here. Review before choosing architecture. |
| https://github.com/disler/super-simple-software-factory | 1042 | Trial the principle that code enforces stage gates and records state; agents do bounded work. | Runtime and implementation work; MIT. | Its Python and SQLite design is not approved here. Verify recovery and gate behavior in our own engine. |
| https://github.com/bastani-inc/atomic | 883 | Study checkable execution graphs and durable evidence. | Runtime and model access; API reports NOASSERTION. Verify license. | README claims are untested. Defer adoption pending architecture review. |

Verdict: trial the ideas in skills and tests. Do not install these projects or promote their architecture without approval. Verify routing, evidence, recovery, and actual cost on an isolated sample.

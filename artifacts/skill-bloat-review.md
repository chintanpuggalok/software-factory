# Skill bloat review

Reviewed 2026-11-11. This is a manual review of instructions, not a token or runtime benchmark.

- `factory-audit` (219 words): longest. Its nine stage checks are useful, but each audit loads checks for all stages. Trial a short main skill with one small stage-specific reference per stage. File reads add overhead, so measure before adopting.
- `factory-design` (203 words): competitor research and design exploration are distinct jobs. Consider a separate on-demand research reference if tasks often need design without fresh competitor research. Do not weaken the confirmed market-leader requirement without user agreement.
- `factory-taste` (164 words): its duplicate warning about not generalizing from one choice can be merged with the hypothesis rule. Keep privacy and scope rules.
- Handoff instructions repeat across multiple skills and `AGENTS.md`. Project rules can carry the common contract, but removing local instructions can reduce portability. Test a standalone skill before removing them.
- Audit every stage may add latency, tokens, and repeated review, even with one skill. Test risk-based audit depth; do not remove the user-requested audit gate.
- Descriptions are advertised at startup. All ten have valid short descriptions, but startup and actual context costs have not been measured.

No skill was removed or rewritten in this review. Length alone is not evidence of bloat. Test routing, actual reads, costs, and output quality on a product task.

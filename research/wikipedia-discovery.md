# Wikipedia search discovery

- Source: https://en.wikipedia.org/w/api.php (accessed 2026-11-11 UTC; use the response timestamp as the exact access time).
- Recommendation: trial search snippets as leads for the design stage, not as proof of market share.
- Fit: gives the no-tools Pi planner a bounded public-source discovery input. The user supplies the query.
- Prerequisites and cost: internet access; no paid API key used. Wikipedia content is subject to its applicable CC BY-SA and other terms; links and attribution are retained.
- Limits: one search request, up to five snippets, 15-second timeout, 256 KB response limit, no redirects. Search relevance and market-share coverage are not guaranteed. The query is sent to Wikipedia. Do not put secrets in it. Snippets are untrusted and cannot establish rankings by themselves.
- Verdict: trial. Do not adopt as a sole source of market-share facts.
- Validation: compare retrieved leads and citations with authoritative, dated market reports. Check for false claims in model output. Add other sources only after their terms and access requirements are reviewed.

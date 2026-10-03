# 2. The Receipt

Filled after the run from real records, never estimated.

| Item | Value |
|---|---|
| Build date | 2026-09-26 to 2026-09-27 (UTC) |
| Plan | Claude Max 20x |
| Plan monthly price | USD 200.00 |
| Share of the plan's usage limit used | not recorded: the plan shows one weekly total for all work, not a figure per build |
| Wall-clock time | 68 min |
| Sessions | 2 |
| Limit hits | 0 |
| Retries | 0 |
| Tokens: Input | 1,184 |
| Tokens: Output | 445,768 |
| Tokens: Cache writes (5 minute and 1 hour, not split by the engine) | 1,755,746 |
| Tokens: Cache reads | 31,950,816 |
| API list price for these tokens (API list price, not billed) | USD 21.68 |
| Paid outside services | none billed; the review's independent judge (gpt-6-astra) made one call of 25,219 input and 855 output tokens, cost not recorded |
| Models and versions | claude-opus-5-5 (1M context), claude-sonnet-5, claude-haiku-4-5-20251001; review judge gpt-6-astra |

Notes:

- Run (internal run id): the build (fix-github-issue #4), 2026-09-26 23:35:34 to 2026-09-27 00:19:14 UTC, 43.7 min, 52 steps, USD 15.60 at API list prices.
- Run (internal run id): the v2 review of PR #10 with its fixes, 2026-09-27 06:45:21 to 07:09:46 UTC, 24.4 min, 75 steps, USD 6.08 at API list prices.
- Wall-clock time is 43.7 min for the build run plus 24.4 min for the review run. Every step started once and completed once; no step stopped on a rate limit.
- Token counts are for the Claude models only; the review judge's tokens are under Paid outside services.
- Plan tier from the build machine's Claude login (default_claude_max_20x); price from https://support.claude.com/en/articles/11049741-what-is-the-max-plan.

## API price table

USD per million tokens, from https://platform.claude.com/docs/en/about-claude/pricing, checked on 2026-09-27.

| Model | Input | Output | Cache writes (5 minute) | Cache writes (1 hour) | Cache reads |
|---|---|---|---|---|---|
| claude-opus-5-5 | 4 | 20 | 5 | 8 | 0.20 |
| claude-sonnet-5 | 2 | 10 | 2.50 | 4 | 0.20 |
| claude-haiku-4-5 | 1 | 5 | 1.25 | 2 | 0.10 |

The API list price is the engine's own figure at these list prices, shown as recorded; it is not recomputed from the table because the records do not split tokens by model. It was not billed: the build ran on the plan above.

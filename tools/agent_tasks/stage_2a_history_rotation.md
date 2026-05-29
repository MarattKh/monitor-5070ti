# Stage 2A: make price history safer to operate long-term

Goal: keep durable price history useful without allowing the JSONL file to grow without bounds.

Change scope:
- Improve price history writing and/or add a small maintenance helper.
- Prefer deterministic tests with temporary files.
- Keep validation offline and fixture-based.

Work:
1. Inspect `append_price_history` and existing price history summary helper.
2. Add a retention or rotation option that can keep only recent records or rotate by file size.
3. Default behavior must remain conservative and must not delete history unexpectedly.
4. Add clear tests for append behavior and any explicit retention/rotation helper.
5. Document the helper usage briefly if a new CLI is added.

Validation:
- Run `\.venv\Scripts\python.exe -m pytest`.

PR:
- Title: `Add price history maintenance helper`
- Body: explain how history maintenance avoids unbounded growth while preserving default behavior.

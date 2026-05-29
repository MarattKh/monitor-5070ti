# Stage 2A: add source stats summary helper

Goal: make source statistics easier to inspect during daily review.

Change scope:
- Add a small helper function or CLI that summarizes existing source stats data.
- Add deterministic tests.
- Keep validation offline and fixture-based.

Work:
1. Reuse the source stats structure already produced by `monitor_5070_ti_v_2.py`.
2. Classify each source as one of: ok, no_filtered_offers, unavailable, error.
3. Include raw count, filtered count, reason, and warnings in the output.
4. Add tests for all classifications.
5. If a CLI is added, keep it simple and documented.

Validation:
- Run `\.venv\Scripts\python.exe -m pytest`.

PR:
- Title: `Add source stats summary helper`
- Body: explain how source stats classification helps review the daily run.

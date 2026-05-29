# Stage 1P: skip terminal runtime states in agent cycle

Goal: prevent scheduled cycles from rerunning tasks that already need operator action or have failed.

Change scope:
- Update `tools/agent_cycle.py` only where task selection/state classification is handled.
- Add or update tests in `tests/test_agent_cycle.py`.
- Do not change notification credentials, scheduler setup, shopping monitor execution, or queue data format unless tests prove a narrow change is required.

Work:
1. Inspect `select_pending_tasks` and how runtime state statuses are used.
2. Introduce a clear terminal/non-runnable status set for runtime state, at least:
   - `completed`
   - `needs_review`
   - `failed`
   - `auto_merge_denied`
   - `pr_created_without_merge`
3. Make pending queue entries with one of those runtime statuses non-runnable.
4. Keep truly pending tasks runnable.
5. Add regression tests showing that pending queue entries with each terminal state are skipped and do not execute task work.

Validation:
- Run `\.venv\Scripts\python.exe -m pytest`.

PR:
- Title: `Skip terminal agent task states`
- Body: summarize the status-selection fix and tests.

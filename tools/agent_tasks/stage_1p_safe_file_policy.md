# Stage 1P: refine safe auto-merge file policy

Goal: reduce unnecessary manual review for low-risk documentation and test-only PRs while keeping agent and runtime infrastructure protected.

Change scope:
- Update the auto-merge safety policy in `tools/agent_cycle.py`.
- Add focused tests in `tests/test_agent_cycle.py`.
- Do not change scheduler setup or notification configuration.

Work:
1. Inspect current changed-file safety logic.
2. Treat docs-only and tests-only PRs as safe for auto-merge when all other safety checks pass.
3. Keep changes to these areas review-required:
   - `tools/agent_cycle.py`
   - `tools/agent_run.py`
   - `tools/agent_tasks/queue.json`
   - scheduler runner scripts
   - dependency/configuration files
4. Add tests for:
   - docs-only PR is safe;
   - tests-only PR is safe;
   - parser/test mixed PR remains safe if it matches existing safe patterns;
   - agent infrastructure and queue changes remain review-required.

Validation:
- Run `\.venv\Scripts\python.exe -m pytest`.

PR:
- Title: `Refine agent auto-merge file policy`
- Body: explain the docs/tests safe policy and protected paths.

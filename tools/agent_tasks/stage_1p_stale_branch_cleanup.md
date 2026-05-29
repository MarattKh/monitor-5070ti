# Stage 1P: add stale local branch cleanup guidance

Goal: prevent repeated failures when a local task branch already exists from an earlier interrupted run.

Change scope:
- Prefer a small helper or documented guard in agent tooling.
- Add tests if code is changed.
- Do not delete branches automatically unless the branch is confirmed merged or has no unique commits.

Work:
1. Inspect current behavior when `git checkout -b <branch>` fails because the branch already exists.
2. Improve logging and recovery instructions for this case.
3. If safe, make the tool reuse or reset a task branch only when it can prove there is no unmerged work at risk.
4. Add tests around the existing-branch path using the fake runner if possible.

Validation:
- Run `\.venv\Scripts\python.exe -m pytest`.

PR:
- Title: `Improve existing task branch recovery`
- Body: explain how existing local task branches are handled safely.

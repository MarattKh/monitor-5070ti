# Stage 1P: add queue completion helper

Goal: reduce manual queue edits after a PR is merged.

Change scope:
- Add a small helper under `tools/`, for example `tools/agent_mark_completed.py`.
- Add tests for the helper.
- Do not change scheduler setup or notification configuration.

Work:
1. Create a helper that marks a task id in `tools/agent_tasks/queue.json` as `completed`.
2. Support arguments:
   - task id;
   - optional queue path;
   - optional dry-run mode.
3. Preserve UTF-8 JSON without adding BOM.
4. Fail clearly if the task id is not found.
5. Add tests for successful update, dry-run, missing task id, and UTF-8 preservation.

Validation:
- Run `\.venv\Scripts\python.exe -m pytest`.

PR:
- Title: `Add agent queue completion helper`
- Body: explain that it reduces manual queue editing after PR merge.

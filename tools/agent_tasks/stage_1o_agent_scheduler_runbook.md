# Stage 1O: add autonomous agent-cycle runbook

Goal: add a short operator runbook for the autonomous Lenovo agent-cycle setup.

Change scope:
- Create or update `docs/agent_cycle_scheduler_runbook.md`.
- Do not change Python agent scripts, queue format, scheduler scripts, notification configuration, dependency files, or GitHub Actions.
- Keep the document concise and practical for Windows PowerShell operation.

The runbook should cover:
1. What `Monitor5070TiAgentCycle` does.
2. Expected normal empty-queue result: `Selected tasks: 0` and no Codex token usage.
3. Where logs and state are stored:
   - `C:\ProgramData\MonitorAgent\agent-cycle-last.log`
   - `C:\ProgramData\MonitorAgent\agent-cycle-state.json`
4. How to check the scheduled task status with `schtasks`.
5. What intervention Telegram events mean:
   - `needs_review`
   - `failed`
   - `auto_merge_denied`
   - `dirty_worktree`
   - `pr_created_without_merge`
   - `cycle_completed_with_errors`
6. A short troubleshooting section for dirty worktree, failed git pull, empty queue, and Codex/GitHub profile issues.

Validation:
- Run `\.venv\Scripts\python.exe -m pytest`.
- Do not run the monitor script that sends shopping notifications.

PR:
- Title: `Add agent cycle scheduler runbook`
- Body: explain that this documents the autonomous Windows scheduled agent cycle and expected empty-queue behavior.

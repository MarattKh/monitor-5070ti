# Agent Cycle Scheduler Runbook

`Monitor5070TiAgentCycle` is the Windows scheduled task that runs the autonomous agent queue for this repository. It starts one agent-cycle pass, selects pending tasks from the queue, runs them through the local Codex agent workflow, records state, and sends intervention notifications when operator action is needed.

## Normal Check

Check the scheduled task from PowerShell:

```powershell
schtasks /Query /TN "Monitor5070TiAgentCycle" /V /FO LIST
```

For a healthy run with no pending queue work, the latest log should contain:

```text
Selected tasks: 0
```

That empty-queue result is normal. It should not invoke Codex for task work and should not consume Codex tokens.

## Logs And State

The scheduler writes runtime artifacts under `C:\ProgramData\MonitorAgent`:

- `C:\ProgramData\MonitorAgent\agent-cycle-last.log` - latest cycle log, including queue path, state path, selected task count, failures, and notification attempts.
- `C:\ProgramData\MonitorAgent\agent-cycle-state.json` - task status history used to avoid rerunning completed or review-needed queue entries.

Useful PowerShell checks:

```powershell
Get-Content C:\ProgramData\MonitorAgent\agent-cycle-last.log -Tail 80
Get-Content C:\ProgramData\MonitorAgent\agent-cycle-state.json
```

## Telegram Intervention Events

These Telegram events mean the scheduler needs human follow-up:

- `needs_review` - a task produced a PR or state that must be reviewed manually before merge or closure.
- `failed` - `agent_run.py` or one of its checks failed for a selected task.
- `auto_merge_denied` - auto-merge was enabled, but policy blocked merge because the PR was not safe to merge automatically.
- `dirty_worktree` - the local repository had uncommitted changes, so the cycle stopped before running tasks.
- `pr_created_without_merge` - the task created a PR and left it open for manual review.
- `cycle_completed_with_errors` - one or more tasks failed, or the cycle stopped before completing cleanly.

## Troubleshooting

Dirty worktree:

```powershell
git status --short
```

Review the local changes. Commit, stash, or remove only changes you have confirmed are safe, then wait for the next scheduled run or rerun the scheduled task manually.

Failed `git pull`:

```powershell
git checkout main
git pull --ff-only
```

If fast-forward pull fails, inspect the branch state and resolve it manually before the next cycle.

Empty queue:

`Selected tasks: 0` means there is no pending work for this cycle. Check the queue and state if you expected a task to run:

```powershell
Get-Content tools\agent_tasks\queue.json
Get-Content C:\ProgramData\MonitorAgent\agent-cycle-state.json
```

Codex or GitHub profile issues:

Run these from the same Windows account used by the scheduled task:

```powershell
codex --version
codex exec --profile agent "Report ready."
gh auth status
gh repo view
```

If these fail, fix the local Codex profile or GitHub CLI authentication for that account before relying on the scheduled cycle.

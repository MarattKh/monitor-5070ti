# Task: Add a concurrency lock to the agent cycle
## Context
The scheduler can fire while a previous cycle still runs; overlapping cycles race the worktree and state.json and
cause spurious failures. No lock exists.
## Goal
Prevent two agent cycles running at once, at the code level.
## Steps
1. At the start of run_cycle/main in tools/agent_cycle.py, acquire an exclusive lock file under
C:\ProgramData\MonitorAgent\ (e.g. agent-cycle.lock) via atomic create (os.open O_CREAT|O_EXCL) writing PID + ISO
timestamp.
2. If the lock exists: treat as STALE if older than a safety timeout (90 min, longer than the executor timeout) or if
the PID is best-effort known dead, and take it over; otherwise log "another cycle running" and exit cleanly WITHOUT
marking any task failed.
3. Always release in a try/finally, including error paths.
4. Tests: acquire/release; second acquire while held is refused; stale lock (old timestamp) is taken over. Use the
timestamp staleness as the primary stale check (cross-platform safe).
## Constraints
Touch only tools/agent_cycle.py (+ small helper if cleaner) and tests/. Do not change queue/state formats. This is a
protected core path -> needs_review, not auto-merge; that is expected.

# AGENTS.md

## Project

This repository is `monitor-5070ti`: a Python monitor for RTX 5070 Ti offers in Russian/nearby retail sources.

Current stable baseline after Stage 1M:

- main commit: `2d1cce8` / PR #18 merged.
- expected local path on Marat's PC: `F:\Codex\monitor-5070ti`.
- Python environment: `.venv` with Python 3.12.
- known passing baseline: `37 passed`.
- DNS may be blocked; blocked access is an expected diagnostic state and must not be treated as a parser crash.

## Safety rules

- Do not commit secrets, tokens, cookies, browser profiles, Telegram tokens, `.env`, `.venv`, reports, logs, or `debug_html`.
- Keep `main` stable. Work in stage branches and open PRs.
- Make small incremental changes. Do not rewrite unrelated parsers.
- Preserve existing user thresholds unless explicitly asked to change them:
  - new good: 90000 RUB
  - new urgent: 75000 RUB
  - used good: 65000 RUB
  - used urgent: 50000 RUB
  - max price: 130000 RUB
- Telegram credentials are expected in Windows user environment variables:
  - `TG_BOT_TOKEN`
  - `TG_CHAT_ID`

## Standard commands

From repository root:

```powershell
$env:PYTHONPATH = (Get-Location).Path
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=.pytest-tmp
.\.venv\Scripts\python.exe tools\smoke_dns.py
.\.venv\Scripts\python.exe tools\smoke_dns.py --browser
.\.venv\Scripts\python.exe monitor_5070_ti_v_2.py --browser --daily-report
```

If absolute paths are required on Marat's PC:

```powershell
$env:PYTHONPATH = "F:\Codex\monitor-5070ti"
F:\Codex\monitor-5070ti\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=F:\Codex\monitor-5070ti\.pytest-tmp
```

## Definition of done

Every stage must finish with:

1. `git status --short` checked.
2. Unit tests passing.
3. Relevant smoke command executed.
4. `results.*`, `urgent_deals.md`, `latest_ai_prompt.md`, `monitor.log`, `debug_html/`, `.pytest-tmp/` not committed.
5. Summary written in Russian for Marat with exact commands and results.

## Stage workflow

For a requested stage:

1. Pull latest `main`.
2. Create a branch named `stage-<id>-<short-topic>`.
3. Inspect relevant files before editing.
4. Implement only the requested change.
5. Run tests and smoke checks.
6. Commit and push branch.
7. Open PR with concise Russian summary and test results.

## DNS parser note

Stage 1M added blocked-access diagnostics. If DNS returns `401 unauthorized`, `403 forbidden`, captcha, qrator, or an HTML block page, the monitor should report a blocked status with `block_reason`, warnings, and no false claim that DNS has zero real products.

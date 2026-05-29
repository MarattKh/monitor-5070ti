# Stage 2B: add blocked-source browser fallback

Goal: improve real daily RTX 5070 Ti monitoring when DNS or Ситилинк block plain HTTP requests.

Context:
- Daily monitor is stable and currently reports:
  - DNS: blocked / 401 unauthorized.
  - Ситилинк: blocked / 429 too many requests.
  - Регард: working.
- `parsers.dns.parse_offers_with_status(browser_mode=True)` and `parsers.citilink.parse_offers_with_status(browser_mode=True)` already exist.
- `requirements.txt` already includes Playwright.

Required behavior:
1. Keep the existing fast plain HTTP attempt first.
2. If a source with browser support returns `blocked=True` and the monitor was not already launched with `--browser`, retry that source once with `browser_mode=True`.
3. If browser fallback returns offers, use those offers and source status for that source.
4. If browser fallback returns no offers, keep the original blocked status and append a clear warning that browser fallback produced no offers, plus any browser fallback warnings.
5. Do not crash if Playwright or Chromium is unavailable; preserve a clear source warning/error instead.
6. Do not change raw counts semantics: raw_count must reflect the offers actually used for that source in the final source_stats row.
7. Keep final report deduplication from Stage 2A intact.

Preferred files:
- `monitor_5070_ti_v_2.py`
- tests only

Tests:
- Add offline tests with fake modules or monkeypatching.
- Cover fallback success after blocked HTTP.
- Cover fallback no-offers after blocked HTTP, preserving original block reason and warnings.
- Cover explicit `--browser`/browser_mode path so fallback is not attempted twice.

Validation:
- Run `./.venv/Scripts/python.exe -m pytest`.

PR:
- Title: `Add browser fallback for blocked RTX sources`
- Body: explain fallback trigger, count behavior, and non-crashing Playwright failure behavior.

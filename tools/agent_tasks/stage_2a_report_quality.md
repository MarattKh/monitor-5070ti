# Stage 2A: improve monitor report quality

Goal: make generated RTX 5070 Ti reports easier to read and harder to misinterpret.

Change scope:
- Improve report formatting in `monitor_5070_ti_v_2.py`.
- Add or update deterministic tests.
- Keep validation offline and fixture-based.

Work:
1. Review `render_results_markdown`, source summary formatting, and daily report text formatting.
2. Fix inconsistent indentation/formatting in the generated markdown summary.
3. Make source summary columns clear for both normal sources and unavailable or limited sources.
4. Ensure daily report text clearly distinguishes:
   - signals;
   - best overall price;
   - source health summary;
   - total filtered offers.
5. Add tests covering normal source rows and unavailable or limited source rows.

Validation:
- Run `\.venv\Scripts\python.exe -m pytest`.

PR:
- Title: `Improve RTX monitor report quality`
- Body: summarize report readability and regression coverage.

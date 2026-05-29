# Stage 2A: add offer deduplication

Goal: avoid duplicate RTX 5070 Ti offers from the same product URL or repeated parser output.

Change scope:
- Add a small deterministic deduplication step before report generation.
- Prefer changes in `monitor_5070_ti_v_2.py` and tests only.
- Keep validation offline and fixture-based.

Work:
1. Add a helper that deduplicates offers by stable key, preferably normalized URL first, then source/title/price fallback.
2. Preserve the cheapest offer when duplicates conflict.
3. Keep final offer ordering by price.
4. Ensure source raw counts still reflect parser output, while final total reflects deduplicated filtered offers.
5. Add tests for duplicate URLs, duplicate source/title/price rows, and distinct offers with same price.

Validation:
- Run `\.venv\Scripts\python.exe -m pytest`.

PR:
- Title: `Add RTX offer deduplication`
- Body: explain the deduplication key and count behavior.

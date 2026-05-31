# Task: Fix Yandex Market offers rejected by the filter
## Context
Yandex Market returns ~8 raw offers per run but ALL are dropped by the offer filter (0 filtered). Likely cause:
scraped URLs contain "/search" and hit the search/catalog-URL rejection in monitor_5070_ti_v_2.py.
## Goal
Let valid RTX 5070 Ti Yandex offers pass, WITHOUT weakening the search-URL filter for other sources.
## Steps
1. Inspect parsers/yandex_market.py output (URL+title) and the search-URL check in monitor_5070_ti_v_2.py.
2. Prefer making the parser emit real product URLs; if not feasible, add a narrow Yandex-specific exemption. Do not
broaden the filter so other sources' search/catalog URLs start passing.
3. Add a regression test: a valid Yandex RTX 5070 Ti offer passes; a genuine search/catalog URL is still rejected.
4. Full test suite must pass.
## Constraints
Touch only parsers/yandex_market.py, monitor_5070_ti_v_2.py, tests/. Do not touch agent tooling or queue/state files.

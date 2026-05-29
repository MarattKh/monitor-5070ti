# Stage 2B: enable existing retailer parsers

Goal: expand real RTX 5070 Ti daily monitoring beyond DNS, Ситилинк, and Регард by wiring already existing parser modules into the main monitor.

Context:
- Initial target source list included DNS, Ситилинк, Регард, Onliner, М.Видео, Эльдорадо, Wildberries, Мегамаркет, AliExpress, ComputerUniverse/CU, СДЭК/international shopping, and other reliable stores.
- `monitor_5070_ti_v_2.py` currently imports many parser modules but only enables DNS, Ситилинк, and Регард in the `sources` dict.
- Existing parser modules already present and should be evaluated/connected where safe:
  - `parsers.mvideo`
  - `parsers.eldorado`
  - `parsers.wildberries`
  - `parsers.megamarket`
  - `parsers.aliexpress`
  - `parsers.computeruniverse`
  - `parsers.cdek_shopping`
  - `parsers.ozon`
  - `parsers.yandex_market`
  - `parsers.avito`

Required behavior:
1. Add a source registry/list so the monitor attempts all enabled sources, not only DNS/Ситилинк/Регард.
2. Keep DNS and Ситилинк status-aware handling and browser fallback behavior from Stage 2B intact.
3. For simple `parse_offers()` modules, failures must remain isolated per source via `run_source`; one bad shop must not break the report.
4. Preserve source stats rows for every enabled source, including zero/raw/error rows.
5. Preserve Stage 2A deduplication and source raw-count semantics.
6. Add tests that prove multiple existing source modules are attempted and that a failing extra source does not stop working sources.
7. Avoid adding noisy Telegram alerts; daily report is allowed, buy-signal Telegram must still only fire for good/urgent deals.

Validation:
- Run `./.venv/Scripts/python.exe -m pytest`.
- Run the monitor once and inspect Source summary.

PR:
- Title: `Enable existing RTX retailer sources`
- Body: list newly enabled source modules and explain failure isolation/count behavior.

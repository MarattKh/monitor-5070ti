# RTX 5070 Ti Monitor v2

Скрипт мониторит реальные карточки товаров и сохраняет отчёты.

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install requests beautifulsoup4 lxml pytest
```

## Запуск

```bash
python monitor_5070_ti_v_2.py
```

Опции:
- `--query "RTX 5070 Ti"`
- `--dynamic-mode off|playwright|selenium`

## Telegram

Рекомендуется использовать внешний отправитель (bot token + chat id) и читать `report_*.json`.
В текущей версии telegram-отправка не встроена: добавьте модуль нотификаций, который читает новые отчёты и отправляет сообщения.

## Где смотреть отчёты

Папка `reports/`:
- `report_YYYYMMDD_HHMMSS.json`
- `report_YYYYMMDD_HHMMSS.txt`

## Что делать при антиботе

Источники `avito/ozon/wildberries/yandex_market/megamarket` помечены как `dynamic_required`.
Если сайт не отдаёт карточки в статическом HTML:
1. Запустите режим `--dynamic-mode playwright`.
2. Реализуйте Playwright/Selenium fallback внутри соответствующего parser-класса.
3. Проверяйте, что не добавляются пустые/мусорные результаты.

## Как добавить новый магазин

1. Создайте новый класс-парсер от `BaseSourceParser`.
2. Опишите `search_url` и `parse()` с извлечением:
   - `title`, `price`, `url`, `seller`, `availability`, `condition`, `source`, `checked_at`, `raw_text`.
3. Добавьте класс в список `parsers` внутри `run_monitor()`.
4. Убедитесь, что карточки проходят `is_valid_product()`.
5. Добавьте unit-тесты.

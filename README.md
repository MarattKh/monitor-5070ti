# monitor_5070ti

Мини-проект мониторинга источников по RTX 5070 Ti.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python monitor_5070_ti_v_2.py
```

Результаты создаются в `monitor_5070ti/outputs`:
- `results.md`
- `results.json`
- `results.csv`
- `latest_ai_prompt.md`

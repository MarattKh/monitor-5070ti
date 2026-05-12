@echo off
cd /d %~dp0
python -m pip install -r requirements.txt
python monitor_5070_ti_v_2.py
pause

@echo off 
:loop
python app.py 
timeout /t 600
goto loop
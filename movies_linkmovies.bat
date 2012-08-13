@rem Invoke a python script with the same name in the same directory as this batch script.
@setlocal enableextensions
@python "%~d0%~p0%0.py" %*

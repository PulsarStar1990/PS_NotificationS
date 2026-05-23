Set objShell = CreateObject("WScript.Shell")
objShell.Run "cmd /c .venv\Scripts\activate && python main.py", 0, True

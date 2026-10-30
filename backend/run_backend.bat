@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
  set "PYTHON=.venv\Scripts\python.exe"
  goto use_venv
)

where py >nul 2>nul
if not errorlevel 1 (
  py -3 -m venv .venv
  if errorlevel 1 goto venv_failed
  set "PYTHON=.venv\Scripts\python.exe"
  goto use_venv
)

if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
  set "PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
  set "PYTHONPATH=%~dp0.runtime-packages"
  set "USE_CODEX_RUNTIME=1"
  goto use_venv
)

python -m venv .venv
if errorlevel 1 goto venv_failed
set "PYTHON=.venv\Scripts\python.exe"

:use_venv
"%PYTHON%" -c "import fastapi, uvicorn, pandas, numpy" >nul 2>nul
if errorlevel 1 (
  echo Installing backend dependencies...
  if defined USE_CODEX_RUNTIME (
    "%PYTHON%" -m pip install --target ".runtime-packages" -r requirements.txt
  ) else (
    "%PYTHON%" -m pip install -r requirements.txt
  )
  if errorlevel 1 (
    echo Dependency installation failed.
    pause
    exit /b 1
  )
)

"%PYTHON%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
exit /b %errorlevel%

:venv_failed
echo Could not create the Python environment. Install Python 3.10+ and enable Python Launcher or Add Python to PATH.
pause
exit /b 1

@echo off
setlocal

pushd "%~dp0backend"

if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
)

call ".venv\Scripts\activate"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

uvicorn app:app --reload --port 8000

popd
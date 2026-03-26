@echo off
setlocal

pushd "%~dp0frontend"

call npm install
npm run dev

popd

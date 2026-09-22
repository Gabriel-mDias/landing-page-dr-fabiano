@echo off
setlocal
node "%~dp0cleanup-sample.mjs" --root "%CD%" %*
exit /b %ERRORLEVEL%

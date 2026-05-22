@echo off
setlocal

set FILE=%~dp0index_v42.html
set URL=file:///%FILE:\=/%

:: Try Edge first, then Chrome
set EDGE=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
set CHROME=C:\Program Files\Google\Chrome\Application\chrome.exe
set CHROME2=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe

if exist "%EDGE%"    ( start "" "%EDGE%"    --app="%URL%" --window-size=1400,900 & exit )
if exist "%CHROME%"  ( start "" "%CHROME%"  --app="%URL%" --window-size=1400,900 & exit )
if exist "%CHROME2%" ( start "" "%CHROME2%" --app="%URL%" --window-size=1400,900 & exit )

echo لم يتم العثور على Chrome أو Edge
pause

@echo off

set APP_NAME=dungeonbuilder
set ICON_PATH=res\icons\favicon.ico
set ENTRY_POINT=launcher.py

pyinstaller --onefile --windowed --icon=%ICON_PATH% %ENTRY_POINT%

rem Rename EXE
if exist dist\%ENTRY_POINT:.py=.exe% (
    ren dist\%ENTRY_POINT:.py=.exe% %APP_NAME%.exe
)

rem Create tar.gz archive (requires tar in PATH)
if exist %APP_NAME%.tar.gz del %APP_NAME%.tar.gz
tar -czvf %APP_NAME%.tar.gz -C dist %APP_NAME%.exe res

rem Remove spec files
if exist main.spec del main.spec
if exist launcher.spec del launcher.spec

echo Build complete: %APP_NAME%.tar.gz
pause

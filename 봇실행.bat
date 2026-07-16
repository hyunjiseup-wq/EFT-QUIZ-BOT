@echo off
cd /d "%~dp0"
title 타르코프 퀴즈봇

set "PYTHON_CMD="

where py >nul 2>nul
if not errorlevel 1 (
    py -3 -c "import sys" >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD (
    where python >nul 2>nul
    if not errorlevel 1 (
        python -c "import sys" >nul 2>nul
        if not errorlevel 1 set "PYTHON_CMD=python"
    )
)

if not defined PYTHON_CMD (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo https://www.python.org/downloads/ 에서 설치 후 다시 실행하세요.
    echo ^(설치 시 "Add Python to PATH" 체크 필수^)
    pause
    exit /b 1
)

if not exist ".env" (
    echo [오류] .env 파일이 없습니다. .env.example을 복사해 .env를 만들고 봇 토큰을 입력하세요.
    pause
    exit /b 1
)

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys" >nul 2>nul
    if errorlevel 1 (
        echo 기존 가상환경이 손상되어 다시 만듭니다...
        rmdir /s /q ".venv"
    )
)

if not exist ".venv\Scripts\python.exe" (
    echo 처음 실행입니다. 가상환경을 만들고 필요한 패키지를 설치합니다... ^(1~2분 소요^)
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo [오류] 가상환경 생성에 실패했습니다.
        pause
        exit /b 1
    )
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [오류] 패키지 설치에 실패했습니다. 인터넷 연결을 확인하세요.
        pause
        exit /b 1
    )
)

echo.
echo 봇을 시작합니다. 이 창을 닫으면 봇이 꺼집니다.
echo (봇 종료: 이 창을 닫거나 Ctrl+C)
echo.
".venv\Scripts\python.exe" bot.py

echo.
echo 봇이 종료되었습니다. 위에 오류 메시지가 있다면 확인하세요.
pause

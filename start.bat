@echo off
setlocal enabledelayedexpansion

echo Starting AdventureAI setup...

:: Only look for Python 3.10 if we need to create a venv
if not exist "venv" (
    echo Virtual environment not found. Looking for Python 3.10 to create it...
    
    :: Find Python 3.10 (checking system Python locations first)
    set PYTHON_PATH=
    for %%p in (
        "C:\Python310\python.exe"
        "C:\Program Files\Python310\python.exe"
        "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe"
    ) do (
        if exist %%p (
            echo Checking Python at: %%p
            %%p --version 2>nul | findstr /r "3\.10\." >nul
            if not errorlevel 1 (
                set PYTHON_PATH=%%p
                goto :found_python
            )
        )
    )

    :: Fallback to PATH if not found in common locations
    if "!PYTHON_PATH!"=="" (
        for /f "tokens=*" %%i in ('where python') do (
            echo Checking Python at: %%i
            %%i --version 2>nul | findstr /r "3\.10\." >nul
            if not errorlevel 1 (
                set PYTHON_PATH=%%i
                goto :found_python
            )
        )
    )

    :found_python
    if "!PYTHON_PATH!"=="" (
        echo Python 3.10.x is required but not found.
        echo Please install Python 3.10.x from https://www.python.org/downloads/
        pause
        exit /b 1
    )

    echo Found Python 3.10 at: !PYTHON_PATH!
    echo Creating virtual environment...
    "!PYTHON_PATH!" -m venv venv
)

:: From this point on, we use the venv Python
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Verify Python version in venv
python --version | findstr /r "3\.10\." >nul
if errorlevel 1 (
    echo Error: Virtual environment Python version is not 3.10
    echo This shouldn't happen if the venv was created correctly.
    pause
    exit /b 1
)

:: Install/upgrade packages
if not exist "venv\Scripts\pip.exe" (
    echo Installing pip tools...
    python -m pip install --upgrade pip
    
    echo Installing core requirements...
    pip install -r src\requirements\requirements-core.txt
    
    echo Installing extra requirements...
    pip install -r src\requirements\requirements-extras.txt
) else (
    :: Verify dependencies are installed correctly
    echo Checking installed dependencies...
    pip freeze > temp_requirements.txt
    findstr /V /C:"pkg-resources==0.0.0" temp_requirements.txt > cleaned_requirements.txt
    set MISSING_DEPS=0

    :: Check core requirements
    for /F "tokens=1,2 delims==" %%a in (src\requirements\requirements-core.txt) do (
        findstr /C:"%%a" cleaned_requirements.txt >nul
        if errorlevel 1 (
            set MISSING_DEPS=1
            echo Missing dependency: %%a
        )
    )

    :: Check extra requirements
    for /F "tokens=1,2 delims==" %%a in (src\requirements\requirements-extras.txt) do (
        findstr /C:"%%a" cleaned_requirements.txt >nul
        if errorlevel 1 (
            set MISSING_DEPS=1
            echo Missing dependency: %%a
        )
    )

    del temp_requirements.txt
    del cleaned_requirements.txt

    :: Install dependencies if missing
    if !MISSING_DEPS! EQU 1 (
        echo Some dependencies are missing. Installing requirements...
        pip install -r src\requirements\requirements-core.txt
        pip install -r src\requirements\requirements-extras.txt
    )
)

:: Run the main application
if exist "src\adventureai.py" (
    echo Starting AdventureAI...
    python src\adventureai.py
) else (
    echo Error: adventureai.py not found!
    echo Current directory: %CD%
    echo Looking for: %CD%\src\adventureai.py
    dir src
    pause
    exit /b 1
)

echo Script completed.
pause
deactivate

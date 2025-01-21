@echo off
setlocal EnableDelayedExpansion

:: Try fast start first
if exist "venv" (
    echo Attempting fast start...
    call venv\Scripts\activate
    
    :: Quick but thorough check for core dependencies and versions
    python -c "import torch; import openai; import numpy; assert numpy.__version__.startswith('1.')" 2>NUL
    if not errorlevel 1 (
        :: Check for .env and load it
        if exist ".env" (
            for /f "tokens=*" %%a in (.env) do (
                set %%a
            )
            echo Starting program...
            python src/adventureai.py
            if not errorlevel 1 (
                exit /b
            )
        )
    )
    echo Fast start failed, running full setup...
)

:: Full setup if fast start fails
echo Checking environment...

:: Find Python 3.10 installation
echo Checking for Python 3.10...
where python 2>NUL
if errorlevel 1 (
    echo Python not found in PATH
    pause
    exit /b 1
)

python -V 2>&1 | findstr /B "Python 3.10" >NUL
if errorlevel 1 (
    echo Python 3.10.x is required but a different version was found
    echo Current version:
    python -V
    echo Please install Python 3.10 and add it to your PATH
    pause
    exit /b 1
)

set PYTHON_PATH=python
echo Found Python 3.10 at %PYTHON_PATH%

:: Check for .env file and load it
if not exist ".env" (
    echo ERROR: .env file not found
    echo Please create a .env file with your OpenAI API key: OPENAI_API_KEY=your_key_here
    pause
    exit /b 1
)

:: Load environment variables from .env
for /f "tokens=*" %%a in (.env) do (
    set %%a
)

:: Check if OPENAI_API_KEY is set
if "%OPENAI_API_KEY%"=="" (
    echo ERROR: OPENAI_API_KEY not found in environment
    echo Please check your .env file
    pause
    exit /b 1
)

:: Check if venv exists and activate it
if exist "venv" (
    call venv\Scripts\activate
) else (
    echo Virtual environment not found, creating new one...
    %PYTHON_PATH% -m venv venv
    call venv\Scripts\activate
    python -m pip install --upgrade pip
)

:: Check if core packages are installed correctly
python -c "import torch; import torchvision; import xformers; import numpy; assert numpy.__version__.startswith('1.')" 2>NUL
if errorlevel 1 (
    echo Some core dependencies are missing or incompatible, updating packages...
    
    :: Check for Visual C++ Redistributable
    reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" /v Version >nul 2>&1
    if errorlevel 1 (
        echo Visual C++ Redistributable 2015-2022 is required but not found
        echo Downloading Visual C++ Redistributable...
        powershell -Command "& { Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile 'vc_redist.x64.exe' }"
        echo Installing Visual C++ Redistributable...
        vc_redist.x64.exe /quiet /norestart
        del vc_redist.x64.exe
        echo Visual C++ Redistributable installation complete
    )

    :: Remove existing venv to ensure clean install
    echo Removing existing virtual environment...
    deactivate 2>NUL
    if exist "venv" (
        rmdir /s /q "venv"
    )
    "%PYTHON_PATH%" -m venv venv
    call venv\Scripts\activate
    venv\Scripts\python.exe -m pip install --upgrade pip

    :: Install core requirements first (non-PyTorch)
    echo Installing core requirements...
    venv\Scripts\python.exe -m pip install numpy==1.24.3 Pillow>=10.0.0

    :: Install PyTorch ecosystem together with compatible versions
    echo Installing PyTorch ecosystem...
    venv\Scripts\python.exe -m pip install torch==2.2.1+cu118 torchvision==0.17.1+cu118 torchaudio==2.2.1 --index-url https://download.pytorch.org/whl/cu118
    venv\Scripts\python.exe -m pip install xformers==0.0.27.post2+cu118 --index-url https://download.pytorch.org/whl/cu118
) else (
    echo Core dependencies verified.
)

:: Check if other packages are installed
python -c "import openai; import diffusers; import transformers" 2>NUL
if errorlevel 1 (
    echo Installing/updating additional requirements...
    pip install -r requirements-extras.txt
) else (
    echo All dependencies verified.
)

:: Verify environment variables
python -c "import os; assert 'OPENAI_API_KEY' in os.environ, 'OpenAI API key not found in environment'" 2>NUL
if errorlevel 1 (
    echo ERROR: OPENAI_API_KEY not found in environment
    echo Please ensure your .env file contains: OPENAI_API_KEY=your_key_here
    pause
    exit /b 1
)

:: Run the main file
echo Starting the program...
python src/adventureai.py

pause 
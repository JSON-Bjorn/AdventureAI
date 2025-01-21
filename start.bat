@echo off
echo Checking environment...

:: Find Python 3.10 installation
for /f "tokens=*" %%i in ('where python') do (
    "%%i" -V 2>NUL | findstr /i "3.10." >NUL
    if not errorlevel 1 (
        set PYTHON_PATH=%%i
        goto :found_python
    )
)
echo Python 3.10.x is required but not found in PATH
echo Please install Python 3.10 and add it to your PATH
pause
exit /b 1

:found_python
echo Found Python 3.10 at %PYTHON_PATH%

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
python -c "import torch; import torchvision; import xformers" 2>NUL
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

    :: Install core requirements first (non-PyTorch)
    echo Installing core requirements...
    pip install numpy>=2.1.3 Pillow>=10.0.0

    :: Install PyTorch ecosystem together with compatible versions
    echo Installing PyTorch ecosystem...
    pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118
    pip install xformers==0.0.22.post4 --index-url https://download.pytorch.org/whl/cu118
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

:: Run the main file
echo Starting the program...
python adventureai.py

pause 
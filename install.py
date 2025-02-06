"""
Installs all dependencies in two steps. Because appearently that was needed once upon a time.
We will, soon, separate this entire repo and thus we will be able to run just pip install requirements.txt in the root directory.
Or just keep this file and only get one file to run.
"""

import subprocess
import sys
import os


def install_requirements(file_path):
    try:
        print(f"Installing dependencies from {file_path}...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", file_path]
        )
        print(f"Successfully installed dependencies from {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies from {file_path}: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Requirements file not found: {file_path}")
        sys.exit(1)


def main():
    # Get the absolute path to the requirements files
    base_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_core = os.path.join(
        base_dir, "src", "requirements", "requirements-core.txt"
    )
    requirements_extras = os.path.join(
        base_dir, "src", "requirements", "requirements-extras.txt"
    )

    # Install dependencies from both files
    install_requirements(requirements_core)
    install_requirements(requirements_extras)

    print("All dependencies installed successfully!")


if __name__ == "__main__":
    main()

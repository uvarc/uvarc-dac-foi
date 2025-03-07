import logging
import os
import subprocess
import sys
import venv

logger = logging.getLogger(__name__)

working_dir = os.path.abspath(os.path.dirname(__file__))

required_major = 3
required_minor = 12
current_version = sys.version_info

logger.info("Checking Python version...")
if current_version.major != required_major or current_version.minor != required_minor:
    raise RuntimeError(
        f"Required Python version is: {required_major}.{required_minor}.x"
    )

logger.info("Creating venv...")
venv_path = os.path.join(working_dir, "venv")
venv.create(venv_path, with_pip=True)

logger.info("Installing Python dependencies...")
pip_path = os.path.join(venv_path, "bin", "pip") if os.name != "nt" else os.path.join(venv_path, "Scripts", "pip")
requirements_path = os.path.join(working_dir, "backend", "requirements.txt")

try:
    subprocess.run([pip_path, "install", "-r", requirements_path])
except Exception as e:
    raise RuntimeError(e)
finally:
    logger.info("Deleting virtual environment...")
    logger.info("An error occurred during runtime, please rerun the setup script.")

logger.info("Applications setup complete. Run /backend/app.py to launch the development server.")
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.absolute()
APP_DIR = ROOT_DIR.joinpath("app")
sys.path.insert(0, str(APP_DIR))

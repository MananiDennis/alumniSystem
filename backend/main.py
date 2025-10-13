"""Launcher for the Alumni Tracking API.

This file is intentionally simple: it ensures the `backend/src` directory is
on sys.path so the package imports (e.g. `src.services`) work when running
from the repository root or from CI. It then imports the `app` instance from
the API package and runs it via uvicorn.

Usage:
  python backend/main.py
  # or
  uvicorn backend.main:app --host 0.0.0.0 --port 8000
"""

from pathlib import Path
import sys

# Ensure backend/src is on sys.path so `import src...` works
ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from src.api.main import app  # noqa: E402

if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI app from the imported module
    uvicorn.run(app, host="0.0.0.0", port=8000)

#!/usr/bin/env uv run

"""
Build script for preact-hello-world plugin.

Runs the Vite build and copies the output to the templates directory.

Usage:
    uv run python scripts/build.py
    # or
    ./scripts/build.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DIST_HTML = FRONTEND_DIR / "dist" / "index.html"
TEMPLATE_FILE = PROJECT_ROOT / "preact_hello_world" / "templates" / "counter.html"


def run_vite_build() -> bool:
    """Run the Vite build process."""
    print("Running Vite build...")
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Vite build failed:\n{result.stderr}", file=sys.stderr)
        return False

    print("Vite build completed successfully.")
    return True


def copy_built_html() -> bool:
    """Copy the built HTML file to the templates directory."""
    if not DIST_HTML.exists():
        print(f"Built HTML not found at {DIST_HTML}", file=sys.stderr)
        return False

    TEMPLATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(DIST_HTML, TEMPLATE_FILE)
    print(f"Copied {DIST_HTML} to {TEMPLATE_FILE}")
    return True


def main() -> int:
    """Main build process."""
    print(f"Project root: {PROJECT_ROOT}")
    print()

    if not run_vite_build():
        return 1

    if not copy_built_html():
        return 1

    print()
    print("Build complete!")
    print("Run tests to verify: uv run pytest")
    print("Deploy with: uv run canvas install preact_hello_world")
    return 0


if __name__ == "__main__":
    sys.exit(main())

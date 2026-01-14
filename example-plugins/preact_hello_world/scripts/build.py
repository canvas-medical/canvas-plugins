#!/usr/bin/env uv run

"""
Build script for preact-hello-world plugin.

Runs the Vite build and embeds the output into the Python handler.
This allows the frontend to be developed normally with hot reload,
then bundled into the plugin for deployment.

Usage:
    uv run python scripts/build.py
    # or
    ./scripts/build.py
"""

import re
import subprocess
import sys
from pathlib import Path

# Paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DIST_HTML = FRONTEND_DIR / "dist" / "index.html"
HANDLER_FILE = PROJECT_ROOT / "preact_hello_world" / "protocols" / "counter_button.py"


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


def read_built_html() -> str | None:
    """Read the built HTML file."""
    if not DIST_HTML.exists():
        print(f"Built HTML not found at {DIST_HTML}", file=sys.stderr)
        return None

    content = DIST_HTML.read_text()
    print(f"Read {len(content)} bytes from {DIST_HTML}")
    return content


def update_handler(html_content: str) -> bool:
    """Update the Python handler with the new HTML content."""
    if not HANDLER_FILE.exists():
        print(f"Handler file not found at {HANDLER_FILE}", file=sys.stderr)
        return False

    handler_code = HANDLER_FILE.read_text()

    # Pattern to match the COUNTER_HTML constant (triple-quoted string)
    pattern = r"COUNTER_HTML = '''.*?'''"

    # Escape any triple quotes in the HTML (unlikely but safe)
    escaped_html = html_content.replace("'''", "' ' '")

    # Build the new constant
    new_constant = f"COUNTER_HTML = '''{escaped_html}'''"

    # Replace the constant in the handler
    new_handler_code, count = re.subn(
        pattern,
        new_constant,
        handler_code,
        flags=re.DOTALL,
    )

    if count == 0:
        print("Could not find COUNTER_HTML constant in handler file", file=sys.stderr)
        return False

    HANDLER_FILE.write_text(new_handler_code)
    print(f"Updated {HANDLER_FILE}")
    return True


def main() -> int:
    """Main build process."""
    print(f"Project root: {PROJECT_ROOT}")
    print()

    # Step 1: Run Vite build
    if not run_vite_build():
        return 1

    # Step 2: Read the built HTML
    html_content = read_built_html()
    if html_content is None:
        return 1

    # Step 3: Update the Python handler
    if not update_handler(html_content):
        return 1

    print()
    print("Build complete! The handler now contains the latest frontend build.")
    print("Run tests to verify: uv run pytest")
    print("Deploy with: uv run canvas install preact_hello_world")
    return 0


if __name__ == "__main__":
    sys.exit(main())

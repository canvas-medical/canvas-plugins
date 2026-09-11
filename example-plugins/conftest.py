"""Global pytest configuration."""

import sys
from pathlib import Path

# Add the example-plugins directory to the Python path so that
# plugin-local tests can import from their plugin modules
sys.path.insert(0, str(Path(__file__).parent))

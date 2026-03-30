import sys
from pathlib import Path

# Add the plugin directory to sys.path so that
# `paytheory_payment_processor` is importable as a package
plugin_dir = Path(__file__).resolve().parent.parent.parent
if str(plugin_dir) not in sys.path:
    sys.path.insert(0, str(plugin_dir))

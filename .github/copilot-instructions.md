# Canvas Plugins SDK and CLI
Canvas Plugins is a Python CLI tool and SDK for developing and managing plugins that extend Canvas medical instances. The repository provides a comprehensive framework for creating event-driven healthcare applications.

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Bootstrap and Setup (Required First Steps)
**Install dependencies and set up the development environment:**
```bash
# Install uv package manager if not available
pip install uv==0.8.1

# Sync all dependencies - NEVER CANCEL: Takes ~22 seconds initially, <1 second when cached
# Set timeout to 60+ seconds for first run
uv sync

# Verify installation works
uv run canvas --version
```

### Build and Test
**Always run these validation steps after making changes:**
```bash
# Build the package - NEVER CANCEL: Takes ~1 second. Set timeout to 30+ seconds.
uv build

# Run unit tests - NEVER CANCEL: Takes ~6 seconds, runs 1341 tests. Set timeout to 30+ seconds.
uv run pytest -m "not integtest" --verbosity 2

# Run linting (very fast, ~0.1 seconds)
uv run ruff check --no-fix

# Run type checking - NEVER CANCEL: Takes ~23 seconds. Set timeout to 60+ seconds.
uv run mypy canvas_cli canvas_sdk plugin_runner logger pubsub --show-traceback

# Format code (very fast, ~0.1 seconds)
uv run ruff format

# Generate protobufs (very fast, ~0.1 seconds)
uv run ./bin/generate-protobufs

# Update allowed imports (~1 second)
uv run python -m plugin_runner.generate_allowed_imports
```

### Credentials Setup
**Set up Canvas instance credentials for plugin management:**
```bash
# Create credentials directory and file
mkdir -p ~/.canvas
cat > ~/.canvas/credentials.ini << EOF
[my-canvas-instance]
client_id=your_client_id
client_secret=your_client_secret

[my-dev-instance]
client_id=dev_client_id
client_secret=dev_client_secret
is_default=true
EOF
```

### Plugin Development Workflow
**Create and test plugins:**
```bash
# Create a new plugin (interactive command)
uv run canvas init
# Follow prompts to name your plugin

# Validate plugin manifest
uv run canvas validate-manifest [plugin-directory]

# Run plugin locally for development
uv run canvas run-plugin [plugin-directory]

# Test with event fixtures
uv run canvas emit canvas_cli/apps/emit/event_fixtures/PATIENT_CREATED.ndjson
```

## Validation
**Always manually validate changes using these scenarios:**

1. **Plugin Creation Test**: Run `uv run canvas init`, create a test plugin, verify it has proper structure (CANVAS_MANIFEST.json, protocols/, README.md)

2. **Build Validation**: Run `uv build` and verify dist/ contains both .tar.gz and .whl files

3. **CLI Functionality**: Test `uv run canvas --help`, `uv run canvas validate-manifest`, and other commands work

4. **Test Suite**: Run `uv run pytest -m "not integtest"` and verify all 1341+ tests pass

5. **Code Quality**: Run `uv run ruff check canvas_cli canvas_sdk plugin_runner logger pubsub` and verify core code is clean

**IMPORTANT**: Integration tests (marked with `integtest`) require real Canvas credentials and instances. Only run unit tests during development.

## Common Tasks

### Repository Structure
```
canvas-plugins/
├── canvas_cli/           # CLI application
├── canvas_sdk/           # SDK for plugin development
├── plugin_runner/        # Sandboxed plugin execution
├── example-plugins/      # 20+ example plugins
├── protobufs/           # Protocol buffer definitions
├── canvas_generated/    # Generated protobuf code
├── schemas/             # JSON schemas
├── logger/              # Logging utilities
├── pubsub/              # Pub/sub messaging
└── .github/             # CI/CD workflows
```

### Available Canvas CLI Commands
```bash
# Plugin management (requires credentials)
canvas list              # List plugins on instance
canvas install [path]    # Install plugin
canvas uninstall [name]  # Remove plugin
canvas enable [name]     # Enable plugin
canvas disable [name]    # Disable plugin

# Development tools
canvas init              # Create new plugin
canvas validate-manifest [path]  # Validate manifest
canvas run-plugin [dir]  # Run locally
canvas emit [fixture]    # Send test events
canvas logs              # Stream instance logs
```

### Event Fixtures for Testing
Available in `canvas_cli/apps/emit/event_fixtures/`:
- `PATIENT_CREATED.ndjson` - Patient creation events
- `APPOINTMENT_CREATED.ndjson` - Appointment events  
- `ASSESS_COMMAND__*.ndjson` - Assessment command events
- `SIMPLE_API_REQUEST.ndjson` - API request events
- And 50+ more event types

### Dependencies and Technology
- **Python**: 3.11+ (repo uses 3.12)
- **Package Manager**: uv (fast, modern Python package manager)
- **Build System**: Hatch 
- **Web Framework**: Django components
- **Communication**: gRPC and Protocol Buffers
- **Databases**: PostgreSQL, Redis
- **Testing**: pytest with extensive test suite
- **Linting**: ruff (replaces flake8, black, isort)
- **Type Checking**: mypy with Django stubs

### Critical Timing and Timeout Information
- **uv sync**: 22 seconds initially, <1 second cached - NEVER CANCEL, set 60+ second timeout
- **uv build**: 1 second - set 30+ second timeout  
- **pytest unit tests**: 6 seconds - set 30+ second timeout
- **mypy type checking**: 23 seconds - NEVER CANCEL, set 60+ second timeout
- **ruff linting/formatting**: 0.1 seconds - default timeout fine
- **protobuf generation**: 0.1 seconds - default timeout fine

### Pre-commit and CI Integration
The repository uses pre-commit hooks that run:
- ruff linting and formatting
- mypy type checking  
- Protocol buffer validation
- Import validation
- Standard file checks

**Always run `uv run ruff format` and `uv run ruff check --fix` before committing or the CI will fail.**

### Example Plugin Patterns
Explore `example-plugins/` for patterns:
- `my_first_plugin/` - Basic protocol example
- `simple_note_button_plugin/` - UI button integration
- `api_samples/` - REST API endpoints
- `example_chart_app/` - Chart applications
- `patient_portal_plugin/` - Patient portal customization
- `vitals_visualizer_plugin/` - Data visualization

### Environment Variables
For local development, create `.env` with:
```bash
CUSTOMER_IDENTIFIER=local
DATABASE_URL=postgresql://user:pass@localhost:5432/canvas
REDIS_ENDPOINT=redis://localhost:6379
PLUGIN_RUNNER_SIGNING_KEY=your_signing_key
```

## Troubleshooting
- **"uv not found"**: Install with `pip install uv==0.8.1`
- **Dependency conflicts**: Run `uv sync --refresh` to rebuild from scratch
- **Protobuf errors**: Run `uv run ./bin/generate-protobufs` to regenerate
- **Import errors**: Run `uv run python -m plugin_runner.generate_allowed_imports`
- **Permission errors**: Check Canvas credentials in `~/.canvas/credentials.ini`
- **CI failures**: Ensure `uv run ruff format` and `uv run ruff check --fix` have been run

## Key Files Reference
- `pyproject.toml` - Project configuration and dependencies
- `uv.lock` - Locked dependency versions
- `.python-version` - Python version (3.12)
- `.pre-commit-config.yaml` - Code quality automation
- `CANVAS_MANIFEST.json` - Plugin manifest structure
- `conftest.py` - pytest configuration and fixtures
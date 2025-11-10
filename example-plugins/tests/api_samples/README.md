# API Samples Tests

This directory contains tests and testing utilities for the `api_samples` plugin.

## Contents

### Test Files

- **[test_appointment_updater.py](test_appointment_updater.py)** - Tests for the AppointmentAPI endpoint
  - Uses real database objects via factories
  - Tests successful updates and error cases
  - 2 tests (both passing)

- **[test_hello_world.py](test_hello_world.py)** - Tests for the HelloWorldAPI endpoint
  - Tests authentication logic
  - Tests JSON response format
  - 2 tests (both passing)


## Quick Start

### Run Tests

```bash
# Run all api_samples tests
cd example-plugins
uv run pytest tests/api_samples/ -v

# Run specific test file
uv run pytest tests/api_samples/test_appointment_updater.py -v
```

## Related Files

- **Plugin code:** `example-plugins/api_samples/`
- **Factories:** `example-plugins/tests/factories.py` (includes AppointmentFactory)
- **Factory examples:** `example-plugins/tests/test_factory_examples.py`
- **Factory guide:** `example-plugins/tests/FACTORY_GUIDE.md`

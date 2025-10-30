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

### Seed Files

- **[seed_appointment_updater.py](seed_appointment_updater.py)** - Database seed file for local testing
  - Creates 5 test patients with appointments
  - Creates 2 providers and 2 locations
  - Various appointment statuses and scenarios
  - See [APPOINTMENT_UPDATER_GUIDE.md](APPOINTMENT_UPDATER_GUIDE.md) for usage

### Documentation

- **[APPOINTMENT_UPDATER_GUIDE.md](APPOINTMENT_UPDATER_GUIDE.md)** - Complete guide for testing the appointment_updater API locally
  - Quick start instructions
  - curl examples
  - Troubleshooting tips

## Quick Start

### Run Tests

```bash
# Run all api_samples tests
cd example-plugins
uv run pytest tests/api_samples/ -v

# Run specific test file
uv run pytest tests/api_samples/test_appointment_updater.py -v
```

### Run Plugin Locally with Seed Data

```bash
# From canvas-plugins directory
canvas run-plugin example-plugins/api_samples \
  --db-seed-file ./example-plugins/tests/api_samples/seed_appointment_updater.py
```

See [APPOINTMENT_UPDATER_GUIDE.md](APPOINTMENT_UPDATER_GUIDE.md) for complete instructions.

## Related Files

- **Plugin code:** `example-plugins/api_samples/`
- **Factories:** `example-plugins/tests/factories.py` (includes AppointmentFactory)
- **Factory examples:** `example-plugins/tests/test_factory_examples.py`
- **Factory guide:** `example-plugins/tests/FACTORY_GUIDE.md`

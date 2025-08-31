from collections.abc import Generator

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(
    early_config: pytest.Config,
    parser: pytest.Parser,
    args: list[str],
) -> None:
    """Ensure canvas_sdk is imported to register its models and settings."""
    import canvas_sdk  # noqa: F401


@pytest.fixture(autouse=True)
def transaction(db: None) -> Generator[None, None, None]:
    """Ensure each test runs within a transaction."""
    yield

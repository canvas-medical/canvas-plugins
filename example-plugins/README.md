To run tests:
```
uv run pytest

# with coverage
uv run pytest --cov=.  

# with missing coverage details
uv run pytest --cov=.  --cov-report=term-missing
```

To run the mypy type checker:
```
uv run mypy . --exclude tests --namespace-packages --explicit-package-bases
```

To load seeds:
```
uv run canvas run-plugin my_plugin --db-seed-file ./seed.py

plugin_runner INFO 2025-10-13 18:30:29,855 Starting server, listening on port 50051
```

To update the `coverage.md` coverage report:
```
uv run pytest \
  --cov=. \
  --cov-report=markdown \
  -q --disable-warnings >/dev/null
```
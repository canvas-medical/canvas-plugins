# pytest-canvas

**pytest-canvas** is a minimal pytest plugin that streamlines testing for projects using the Canvas SDK.

## What it does

- **Auto-loads the Canvas SDK** at the earliest point in the pytest lifecycle.
- **Wraps each test in a Django database transaction** to ensure isolation and consistency.
- **Removes boilerplate**—you no longer need to explicitly depend on `db` or `transactional_db`.

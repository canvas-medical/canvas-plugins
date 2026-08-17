# test_sandbox_lint_violations

Lint fixture for `canvas validate`. **Deliberately invalid — do not copy code out of it.**

`handlers/violations.py` contains one of every construct the RestrictedPython sandbox rejects. `handlers/clean.py` contains the correct form of each, so the fixture checks both directions: the rules fire where they should, and stay silent where they shouldn't.

It lives here rather than in `example-plugins/` because CI validates every example plugin, and this one is meant to fail.

## Running it

```sh
canvas validate plugin_runner/tests/fixtures/plugins/test_sandbox_lint_violations
```

Expected: an error finding for each code below, and none pointing at `clean.py`.

| Code | Construct in `violations.py` |
| --- | --- |
| `augmented-attribute` | `obj.total += 1` |
| `augmented-subscript` | `counts["a"] += 1`, `items[0] += 1`, `items[0:1] += [4]` |
| `type-blocked` | `type(obj)` and `type("Made", (object,), {})` |
| `setattr-blocked` | `setattr(obj, "flag", True)` |
| `delattr-blocked` | `delattr(obj, "total")` |
| `bytearray-blocked` | `bytearray(b"x")` |

`canvas validate` exits 1 on any error finding, so it will stop at the lint step and never reach handler loading. That is the point: every one of these fails once the plugin reaches an instance, and the lint is what catches them first.

Two of them fail differently, which is worth knowing:

- **`augmented-attribute` and `augmented-subscript`** are rejected when the sandbox *compiles* the module, so a plugin containing either cannot load at all.
- **`type(...)`** inside a method body compiles and loads fine, and only raises `NameError: name 'type' is not defined` when that line executes. A plugin using it can sit deployed and look healthy until the branch is hit.

The automated coverage is `canvas_cli/apps/plugin/test_plugin_lint.py::test_fixture_plugin_reports_every_construct_rule`, which lints this directory and asserts the full set. Add the fixture case there whenever a construct rule is added.

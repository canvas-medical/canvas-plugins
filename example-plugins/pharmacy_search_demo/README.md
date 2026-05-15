# pharmacy_search_demo

Demo plugin for [KOALA-4355](https://canvasmedical.atlassian.net/browse/KOALA-4355) — exercises all new pharmacy search filter parameters added in [canvas-plugins#1542](https://github.com/canvas-medical/canvas-plugins/pull/1542).

## Usage

```
GET /plugin-io/api/pharmacy_search_demo/run
```

Requires a logged-in staff session (`StaffSessionAuthMixin`). Returns a JSON report of all test cases with pass/fail status.

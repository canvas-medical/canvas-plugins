# custom_data_uat

UAT plugin for [canvas-plugins#1336](https://github.com/canvas-medical/canvas-plugins/commit/284cb015ffef4626e152a24a2d751424f18fd5b9) — custom attributes and custom models.

Uses `StaffSessionAuthMixin` so it's accessible from the browser when logged in as staff.

## What it tests

| # | Section | Features |
|---|---------|----------|
| 1 | CustomModel CRUD | create, read, update, delete a `Tag` |
| 2 | CustomModel relationships | FK traversal, reverse relations, UniqueConstraint, select_related, cascade delete |
| 3 | ModelExtension proxy | computed properties, isinstance checks |
| 4 | proxy_field | FK traversal returns proxy instances with added properties |
| 5 | AttributeHub CRUD | create hub, set/get/delete attributes |
| 6 | AttributeHub typed values | round-trip all value types (str, int, bool, Decimal, date, datetime, dict, list, None) |
| 7 | AttributeHub filtering | value-type rewriting (text, int gte, bool, cross-relation, NULL, isnull) |
| 8 | AttributeHub with_only | selective prefetch, fallback to DB for non-prefetched |
| 9 | AttributeHub bulk | set_attributes, bulk upsert, count verification |
| 10 | Transactions | atomic commit, rollback on error, nested savepoints |

## Usage

Navigate to:
```
https://<instance>.canvasmedical.com/plugin-io/api/custom_data_uat/run
```

Returns JSON with per-section pass/fail and an overall `all_passed` boolean.

## Manifest

- **Namespace**: `custom_data__uat`
- **Access**: `read_write` (needed for CustomModel and AttributeHub write tests)
- **Auth**: `StaffSessionAuthMixin` (browser session auth)

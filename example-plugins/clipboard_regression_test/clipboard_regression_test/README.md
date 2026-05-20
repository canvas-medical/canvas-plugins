clipboard_regression_test
=========================

## Description

Regression test plugin for clipboard iframe permissions. Declares
`CLIPBOARD_READ` and `CLIPBOARD_WRITE` under `url_permissions` and serves
a simple iframe with two buttons that call `navigator.clipboard.writeText()`
and `navigator.clipboard.readText()`.

## How to verify

1. Install on the target instance.
2. Open the **Clipboard Regression Test** application from the provider menu.
3. Click **Write** — expected: `write ok` appears in the log.
4. Click **Read** — expected: `read ok: hello from canvas`.

If either call fails with `NotAllowedError`, the iframe is missing the
corresponding `allow="clipboard-read"` / `allow="clipboard-write"` attribute.

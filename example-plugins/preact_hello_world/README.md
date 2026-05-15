# preact_hello_world

`preact_hello_world` is an example plugin that shows how to embed a Preact UI inside a Canvas plugin.

Preact was chosen to reduce the bundle size, but if you need regular React you can replace all references to `preact` with `react`.

To build the frontend code and update the Canvas plugin with it you must run `./scripts/build.py` and then upload the plugin with `canvas install`.

### Getting Started

Create a file `~/.canvas/credentials.ini` and add the client_id and client_secret credentials for each of your Canvas instances. You can define your default host with `is_default=true`. If no default is explicitly defined, the Canvas CLI will use the first instance in the file as the default for each of the CLI commands.

**Example:**

```
[my-canvas-instance]
client_id=myclientid
client_secret=myclientsecret

[my-dev-canvas-instance]
client_id=devclientid
client_secret=devclientsecret
is_default=true

[localhost]
client_id=localclientid
client_secret=localclientsecret
```

Next, you're ready to install canvas.

`pip install canvas`

**Usage**:

```console
$ canvas [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--version`
- `--help`: Show this message and exit.

**Commands**:

- `init`: Create a new plugin
- `install`: Install a plugin into a Canvas instance
- `uninstall`: Uninstall a plugin from a Canvas instance
- `disable`: Disable a plugin from a Canvas instance
- `enable`: Enable a plugin from a Canvas instance
- `list`: List all plugins from a Canvas instance
- `validate-manifest`: Validate the Canvas Manifest json file
- `logs`: Listen and print log streams from a Canvas instance

## `canvas init`

Create a new plugin.

**Usage**:

```console
$ canvas init [OPTIONS]
```

**Options**:

- `--help`: Show this message and exit.

## `canvas install`

Install a plugin into a Canvas instance.

**Usage**:

```console
$ canvas install [OPTIONS] PLUGIN_NAME
```

**Arguments**:

- `PLUGIN_NAME`: Path to plugin to install [required]

**Options**:

- `--host TEXT`: Canvas instance to connect to
- `--help`: Show this message and exit.

## `canvas uninstall`

Uninstall a plugin from a Canvas instance..

**Usage**:

```console
$ canvas uninstall [OPTIONS] NAME
```

**Arguments**:

- `NAME`: Plugin name to delete [required]

**Options**:

- `--host TEXT`: Canvas instance to connect to
- `--help`: Show this message and exit.

## `canvas enable`

Enable a plugin from a Canvas instance..

**Usage**:

```console
$ canvas enable [OPTIONS] NAME
```

**Arguments**:

- `NAME`: Plugin name to enable [required]

**Options**:

- `--host TEXT`: Canvas instance to connect to
- `--help`: Show this message and exit.

## `canvas disable`

Disable a plugin from a Canvas instance..

**Usage**:

```console
$ canvas disable [OPTIONS] NAME
```

**Arguments**:

- `NAME`: Plugin name to disable [required]

**Options**:

- `--host TEXT`: Canvas instance to connect to
- `--help`: Show this message and exit.

## `canvas list`

List all plugins from a Canvas instance.

**Usage**:

```console
$ canvas list [OPTIONS]
```

**Options**:

- `--host TEXT`: Canvas instance to connect to
- `--help`: Show this message and exit.

## `canvas validate-manifest`

Validate the Canvas Manifest json file.

**Usage**:

```console
$ canvas validate-manifest [OPTIONS] PACKAGE
```

**Arguments**:

- `PLUGIN_NAME`: Path to plugin to install [required]

**Options**:

- `--help`: Show this message and exit.

## `canvas logs`

Listens and prints log streams from the instance.

**Usage**:

```console
$ canvas logs [OPTIONS]
```

**Options**:

- `--host TEXT`: Canvas instance to connect to
- `--help`: Show this message and exit.

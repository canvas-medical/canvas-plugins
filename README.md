### Getting Started

`pip install canvas`

**Usage**:

```console
$ canvas [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--no-ansi`: Disable colorized output
- `--version`
- `--verbose`: Show extra output
- `--install-completion`: Install completion for the current shell.
- `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
- `--help`: Show this message and exit.

**Commands**:

- `auth`: Manage authenticating in Canvas instances
- `logs`: Listens and prints log streams from the instance
- `plugin`: Manage plugins in a Canvas instance
- `print-config`: Print the config and exit

## `canvas auth`

Manage authenticating in Canvas instances

**Usage**:

```console
$ canvas auth [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `add-api-key`: Add a host=api-key pair to the keychain, so it can be used in other requests
- `get-api-key`: Print the api_key for the given host
- `remove-api-key`: Removes a host from the keychain, and as the default if it's the one
- `set-default-host`: Set the host as the default host in the config file

### `canvas auth add-api-key`

Add a host=api-key pair to the keychain, so it can be used in other requests.
Optionally set a default so `--host` isn't required everywhere

**Usage**:

```console
$ canvas auth add-api-key [OPTIONS]
```

**Options**:

- `--host TEXT`: [required]
- `--api-key TEXT`: [required]
- `--is-default / --no-is-default`: [required]
- `--help`: Show this message and exit.

### `canvas auth get-api-key`

Print the api_key for the given host.

**Usage**:

```console
$ canvas auth get-api-key [OPTIONS] HOST
```

**Arguments**:

- `HOST`: [required]

**Options**:

- `--help`: Show this message and exit.

### `canvas auth remove-api-key`

Removes a host from the keychain, and as the default if it's the one.
This method always succeeds, regardless of username existence.

**Usage**:

```console
$ canvas auth remove-api-key [OPTIONS] HOST
```

**Arguments**:

- `HOST`: [required]

**Options**:

- `--help`: Show this message and exit.

### `canvas auth set-default-host`

Set the host as the default host in the config file. Validates it exists in the keychain.

**Usage**:

```console
$ canvas auth set-default-host [OPTIONS] HOST
```

**Arguments**:

- `HOST`: [required]

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
- `--api-key TEXT`: Canvas api-key for the provided host
- `--help`: Show this message and exit.

## `canvas plugin`

Manage plugins in a Canvas instance

**Usage**:

```console
$ canvas plugin [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `delete`: Delete a disabled plugin from an instance
- `init`: Create a plugin from a template using Cookiecutter
- `install`: Installs a given Python package into a running Canvas instance
- `list`: Lists all plugins from the instance
- `update`: Updates a plugin from an instance

### `canvas plugin delete`

Delete a disabled plugin from an instance.

**Usage**:

```console
$ canvas plugin delete [OPTIONS] NAME
```

**Arguments**:

- `NAME`: Plugin name to delete [required]

**Options**:

- `--host TEXT`: Canvas instance to connect to
- `--api-key TEXT`: Canvas api-key for the provided host
- `--help`: Show this message and exit.

### `canvas plugin init`

Create a plugin from a template using Cookiecutter.

**Usage**:

```console
$ canvas plugin init [OPTIONS] [TEMPLATE]
```

**Arguments**:

- `[TEMPLATE]`: [default: (dynamic)]

**Options**:

- `--no-input`: Don't prompt the user at command line
- `--help`: Show this message and exit.

### `canvas plugin install`

Installs a given Python package into a running Canvas instance.

**Usage**:

```console
$ canvas plugin install [OPTIONS] PACKAGE
```

**Arguments**:

- `PACKAGE`: Path to either a dir or wheel or sdist file containing the python package to install [required]

**Options**:

- `--host TEXT`: Canvas instance to connect to
- `--api-key TEXT`: Canvas api-key for the provided host
- `--help`: Show this message and exit.

### `canvas plugin list`

Lists all plugins from the instance.

**Usage**:

```console
$ canvas plugin list [OPTIONS]
```

**Options**:

- `--host TEXT`: Canvas instance to connect to
- `--api-key TEXT`: Canvas api-key for the provided host
- `--help`: Show this message and exit.

### `canvas plugin update`

Updates a plugin from an instance.

**Usage**:

```console
$ canvas plugin update [OPTIONS] NAME
```

**Arguments**:

- `NAME`: Plugin name to update [required]

**Options**:

- `--package PATH`: Path to a wheel or sdist file containing the python package to install
- `--enable / --disable`: Enable/disable the plugin
- `--host TEXT`: Canvas instance to connect to
- `--api-key TEXT`: Canvas api-key for the provided host
- `--help`: Show this message and exit.

## `canvas print-config`

Simple command to print the config and exit.

**Usage**:

```console
$ canvas print-config [OPTIONS]
```

**Options**:

- `--help`: Show this message and exit.

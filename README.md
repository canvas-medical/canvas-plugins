[![codecov](https://codecov.io/gh/canvas-medical/canvas-plugins/graph/badge.svg?token=P8JJUOJ8FH)](https://codecov.io/gh/canvas-medical/canvas-plugins)

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

### Canvas Platform

Canvas Platform hosts a plugin's git repository and deploys it to the instances it manages. Sign in once per machine with `canvas login`, which opens your browser; the session is stored per platform in `~/.canvas/platform-credentials.json`, readable only by you, and refreshes itself. `canvas login --platform <url>` or `CANVAS_PLATFORM_URL` points the CLI at a platform other than https://platform.canvasmedical.com, and later commands keep using the platform you last signed in to.

A plugin deployed through Canvas Platform has a publisher-prefixed name, `<org prefix>__<package>` (for example `acme__intake`), used for the manifest `name`, the package folder and its imports. `canvas login` lists the prefix of each organization you belong to, and the prefix decides which organization publishes the plugin. `canvas install` and `canvas validate` accept names with or without a prefix.

#### Which plugins go through Canvas Platform

`canvas config`, `canvas uninstall` and `canvas install` work for plugins Canvas Platform manages and for plugins installed straight onto an instance, and each decides per plugin:

- A name without a prefix, or a machine that is not signed in, goes straight to the instance, as `canvas install` always has.
- Otherwise the CLI asks platform for the plugin. If platform has it, the command goes through platform; if not, it goes to the instance.

`--host` names an instance for a plugin platform does not manage, and is refused for one it does. When an instance refuses `canvas install` because platform manages that plugin, the message names `canvas deploy`.

git signs in to platform's git server through `canvas git-credential`, a hidden command `canvas deploy`, `canvas init` and `canvas clone` register as the repository's credential helper. It mints a one-hour git token for the plugin named in the repository path, and the repository's configuration keeps any other credential helper, such as macOS's keychain, from answering for that server.

```console
$ canvas login
$ canvas init                                   # scaffolds acme__my_cool_plugin and registers it
$ canvas deploy my-cool-plugin/acme__my_cool_plugin --instance acme-staging
$ canvas config set acme__my_cool_plugin API_URL=https://api.example.com --instance acme-staging
```

**Usage**:

```console
$ canvas [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--version`
- `--help`: Show this message and exit.

**Commands**:

- `login`: Sign in to Canvas Platform through your browser
- `logout`: Sign out of Canvas Platform
- `init`: Create a new plugin
- `deploy`: Publish a plugin to Canvas Platform and deploy it
- `clone`: Clone a plugin's repository from Canvas Platform
- `install`: Install a plugin into a Canvas instance
- `uninstall`: Uninstall a plugin
- `config`: List, set and clear plugin variables
- `disable`: Disable a plugin from a Canvas instance
- `enable`: Enable a plugin from a Canvas instance
- `list`: List all plugins from a Canvas instance
- `validate-manifest`: Validate the Canvas Manifest json file
- `logs`: Listen and print log streams from a Canvas instance

## `canvas login`

Sign in to Canvas Platform through your browser (OAuth authorization code with PKCE). The sign-in URL is also printed, for a machine without a browser.

**Usage**:

```console
$ canvas login [OPTIONS]
```

**Options**:

- `--platform TEXT`: Canvas Platform URL
- `--help`: Show this message and exit.

## `canvas logout`

Revoke this machine's Canvas Platform session and delete its stored tokens.

**Usage**:

```console
$ canvas logout [OPTIONS]
```

**Options**:

- `--platform TEXT`: Canvas Platform URL
- `--help`: Show this message and exit.

## `canvas init`

Create a new plugin. Signed in to Canvas Platform, the package is named `<org prefix>__<package>`, registered with platform, and given a git repository whose `origin` is platform. Signed out, it is named from the project name alone.

**Usage**:

```console
$ canvas init [OPTIONS] [PLUGIN_TYPE]
```

**Arguments**:

- `PLUGIN_TYPE`: `handler` (default) or `application`

**Options**:

- `--org TEXT`: Organization that publishes the plugin, when you can publish in several
- `--help`: Show this message and exit.

## `canvas deploy`

Publish a plugin's code to Canvas Platform and deploy it. The manifest `name` must be publisher-prefixed. Deploy registers the plugin, points the repository's `origin` at platform with a credential helper, commits uncommitted changes after you confirm, pushes HEAD to `main`, deploys that commit and waits for each target's outcome. Consent requests for cross-plugin custom data access are answered inline. The repository is rooted at the directory containing the package. Without a terminal to confirm at, uncommitted changes are refused rather than committed.

**Usage**:

```console
$ canvas deploy [OPTIONS] PLUGIN_DIR
```

**Arguments**:

- `PLUGIN_DIR`: Path to the plugin package [required]

**Options**:

- `--instance TEXT`: Instance to deploy to, repeatable. Without it, deploy targets the only instance you can deploy to and otherwise lists the choices
- `--ref TEXT`: Deploy a pushed branch, tag or commit as-is, without pushing
- `--no-push`: Deploy the pushed `main` as-is, without pushing
- `-y, --yes`: Approve all consent requests
- `--help`: Show this message and exit.

## `canvas clone`

Clone a plugin's repository from Canvas Platform with `origin` and the credential helper set, ready for `canvas deploy`.

**Usage**:

```console
$ canvas clone [OPTIONS] NAME [DIRECTORY]
```

**Arguments**:

- `NAME`: Plugin name, e.g. `acme__intake` [required]
- `DIRECTORY`: Where to clone it, a directory named after the plugin by default

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

Uninstall a plugin. A plugin Canvas Platform manages is removed by an uninstall deployment from each `--instance`, which is required. Any other plugin is removed from the instance directly.

**Usage**:

```console
$ canvas uninstall [OPTIONS] NAME
```

**Arguments**:

- `NAME`: Plugin name to uninstall [required]

**Options**:

- `--instance TEXT`: Instance to uninstall from, repeatable
- `--host TEXT`: Canvas instance to connect to, for a plugin Canvas Platform does not manage
- `--force`: Uninstall an enabled plugin from an instance directly
- `--help`: Show this message and exit.

## `canvas config set` / `canvas config unset`

Set or clear a plugin's variable values. For a plugin Canvas Platform manages, values are stored in platform and a configure deployment brings them to the running plugin; without `--instance`, the only instance it is installed on that you can configure is targeted. A variable's sensitivity comes from the manifest's `variables`, and `--secret` / `--variable` state it for a key no revision declares. For any other plugin, values are written to the instance directly, and `unset` sets them empty.

**Usage**:

```console
$ canvas config set [OPTIONS] PLUGIN_NAME [KEY=VALUE]...
$ canvas config unset [OPTIONS] PLUGIN_NAME KEY...
```

**Options**:

- `--instance TEXT`: Instance to configure, repeatable
- `--host TEXT`: Canvas instance to connect to, for a plugin Canvas Platform does not manage
- `--secret KEY=VALUE`, `--variable KEY=VALUE`: (`set` only) a sensitive or non-sensitive value for an undeclared key
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

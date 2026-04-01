class PluginError(Exception):
    """An exception raised for plugin-related errors."""


class PluginValidationError(PluginError):
    """An exception raised when a plugin package is not valid."""


class InvalidPluginFormat(PluginValidationError):
    """An exception raised when the plugin file format is not supported."""


class PluginInstallationError(PluginError):
    """An exception raised when a plugin fails to install."""


class PluginUninstallationError(PluginError):
    """An exception raised when a plugin fails to uninstall."""


class NamespaceAccessError(PluginError):
    """An exception raised when a plugin cannot access its declared namespace.

    This typically occurs when:
    - The required access key secret is not configured
    - The access key is not found in the namespace's auth table
    - The plugin requests write access but only has read access
    """

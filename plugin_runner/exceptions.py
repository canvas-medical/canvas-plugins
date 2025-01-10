class PluginError(Exception):
    """An exception raised for plugin-related errors."""


class PluginValidationError(PluginError):
    """An exception raised when a plugin package is not valid."""


class InvalidPluginFormat(PluginValidationError):
    """An exception raised when the plugin file format is not supported."""


class PluginInstallationError(PluginError):
    """An exception raised when a plugin fails to install."""

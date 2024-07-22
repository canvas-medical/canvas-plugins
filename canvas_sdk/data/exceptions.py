"""Data Access Layer exceptions."""


class DataModuleError(RuntimeError):
    """
    General Data Access Layer error; base class and also used to represent errors of indeterminate
    cause.
    """

    pass


class DataModuleNotFoundError(DataModuleError):
    """Object not found error."""

    pass

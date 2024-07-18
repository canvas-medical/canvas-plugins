"""Data Access Layer exceptions."""


class DataAccessLayerError(RuntimeError):
    """
    General Data Access Layer error; base class and also used to represent errors of indeterminate
    cause.
    """

    pass


class DataAccessLayerNotFoundError(DataAccessLayerError):
    """Object not found error."""

    pass

from abc import ABC

from canvas_sdk.handlers.base import BaseHandler


class BaseProtocol(BaseHandler, ABC):
    """
    The class that protocols inherit from.
    """

    pass


__canvas_allowed_attributes__ = ("BaseProtocol",)

from abc import ABC

from canvas_sdk.handlers.base import BaseHandler


class BaseProtocol(BaseHandler, ABC):
    """
    The class that protocols inherit from.
    """

    pass


__exports__ = ("BaseProtocol",)

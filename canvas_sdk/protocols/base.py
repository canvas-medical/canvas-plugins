from abc import ABC

from canvas_sdk.handlers.base import BaseHandler


class BaseProtocol(BaseHandler, ABC):
    """Deprecated alias for BaseHandler. Use canvas_sdk.handlers.base.BaseHandler instead."""

    pass


__exports__ = ("BaseProtocol",)

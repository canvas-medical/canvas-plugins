from typing import Any


class CachingException(Exception):
    """A Generic Exception for the module."""


class CacheConfigurationError(CachingException):
    """An Exception raised when cache driver doesn't exist."""

    driver: str

    def __init__(self, driver: str, *args: Any):
        super().__init__(args)
        self.driver = driver

    def __str__(self) -> str:
        return f"The cache driver {self.driver} does not exist"


__exports__ = ("CachingException", "CacheConfigurationError")

from typing import Any, Generic, TypeVar

T = TypeVar("T")


class WriteOnceProperty(Generic[T]):
    """A descriptor for write-once values."""

    def __set_name__(self, owner: Any, name: str) -> None:
        """Set the name of the property so that the descriptor can access it."""
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, obj: Any, objtype: Any = None) -> T:
        """Retrieve the value of the property."""
        return getattr(obj, self.private_name)

    def __set__(self, obj: Any, value: T) -> None:
        """Set the value of the property.

        Throws an AttributeError if the property already has a value.
        """
        if hasattr(obj, self.private_name):
            raise AttributeError(f"{self.public_name} cannot be changed.")
        setattr(obj, self.private_name, value)


__exports__ = ()

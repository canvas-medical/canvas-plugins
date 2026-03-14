"""Tests for proxy_field descriptor.

Tests verify that:
1. Accessing a proxy_field returns an instance of the proxy class
2. Null FKs return None without error
3. Assignment delegates to the parent descriptor
4. Accessing on the class returns the descriptor itself
5. __set_name__ correctly finds the parent descriptor from MRO
"""

from unittest.mock import MagicMock

import pytest
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor

from canvas_sdk.v1.data.base import proxy_field


class FakeProxyClass:
    """Stub proxy class for testing __class__ swapping."""

    pass


class FakeParentModel:
    """Simulates a base model class with a FK descriptor."""

    pass


@pytest.fixture
def parent_descriptor() -> MagicMock:
    """Create a mock ForwardManyToOneDescriptor with descriptor protocol support."""
    desc = MagicMock(spec=ForwardManyToOneDescriptor)
    desc.__set__ = MagicMock()
    return desc


@pytest.fixture
def descriptor_with_parent(parent_descriptor: MagicMock) -> proxy_field:
    """Create a proxy_field and wire up its parent descriptor."""
    pf = proxy_field(FakeProxyClass)
    pf._parent_descriptor = parent_descriptor
    return pf


def test_get_returns_proxy_class(
    descriptor_with_parent: proxy_field, parent_descriptor: MagicMock
) -> None:
    """Accessing the field on an instance returns an object whose class is the proxy class."""
    related_obj = MagicMock()
    parent_descriptor.__get__ = MagicMock(return_value=related_obj)

    obj = MagicMock()
    result = descriptor_with_parent.__get__(obj, type(obj))

    parent_descriptor.__get__.assert_called_once_with(obj, type(obj))
    assert result.__class__ is FakeProxyClass


def test_get_returns_none_when_null(
    descriptor_with_parent: proxy_field, parent_descriptor: MagicMock
) -> None:
    """Null FKs return None without attempting to swap __class__."""
    parent_descriptor.__get__ = MagicMock(return_value=None)

    obj = MagicMock()
    result = descriptor_with_parent.__get__(obj, type(obj))

    assert result is None


def test_set_delegates_to_parent(
    descriptor_with_parent: proxy_field, parent_descriptor: MagicMock
) -> None:
    """Assignment delegates to the parent descriptor's __set__."""
    obj = MagicMock()
    value = MagicMock()

    descriptor_with_parent.__set__(obj, value)

    parent_descriptor.__set__.assert_called_once_with(obj, value)


def test_class_access_returns_descriptor(descriptor_with_parent: proxy_field) -> None:
    """Accessing on the class (obj is None) returns the descriptor itself."""
    result = descriptor_with_parent.__get__(None, FakeParentModel)
    assert result is descriptor_with_parent


def test_set_name_finds_parent_descriptor() -> None:
    """__set_name__ correctly walks MRO and finds the parent descriptor."""
    parent_desc = MagicMock(spec=ForwardManyToOneDescriptor)

    # Build a class hierarchy where the base has a descriptor named "patient"
    BaseModel = type("BaseModel", (), {"patient": parent_desc})
    ChildModel = type("ChildModel", (BaseModel,), {})

    pf = proxy_field(FakeProxyClass)
    pf.__set_name__(ChildModel, "patient")

    assert pf._parent_descriptor is parent_desc

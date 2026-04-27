"""Convenience authorization predicates for `@tool`, `@resource`, and `@prompt` decorators.

Each predicate is a callable that receives the bound `MCP` handler instance and returns bool.
The view rejects anonymous requests at the platform layer, so by the time these run the actor is
guaranteed non-null. Predicates can still inspect `handler.event_actor`, role/scope membership,
or any custom claim from `handler.event.context["headers"]`.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mcp import MCP

Predicate = Callable[["MCP"], bool]


def any_authenticated(handler: "MCP") -> bool:
    """Allow any authenticated actor."""
    return handler.event_actor is not None


def has_role(role: str) -> Predicate:
    """Allow any actor with the given role."""

    def predicate(handler: "MCP") -> bool:
        return handler.event_actor_has_role(role)

    return predicate


def has_scope(scope: str) -> Predicate:
    """Allow any actor whose OAuth token includes the given scope."""

    def predicate(handler: "MCP") -> bool:
        return handler.event_actor_has_scope(scope)

    return predicate


def all_of(*predicates: Predicate) -> Predicate:
    """Combine predicates with AND semantics."""

    def predicate(handler: "MCP") -> bool:
        return all(p(handler) for p in predicates)

    return predicate


def any_of(*predicates: Predicate) -> Predicate:
    """Combine predicates with OR semantics."""

    def predicate(handler: "MCP") -> bool:
        return any(p(handler) for p in predicates)

    return predicate


__exports__ = ("any_authenticated", "has_role", "has_scope", "all_of", "any_of", "Predicate")

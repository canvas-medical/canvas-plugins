from enum import StrEnum


class PortalAccessLevel(StrEnum):
    """
    How much a login may do in one area of the patient's chart.

    With NONE, hide the area; with VIEW, show it read-only; with ACT, allow its actions too. Levels
    compare by how much they allow, NONE < VIEW < ACT, and NONE is falsy.
    """

    NONE = "none"
    VIEW = "view"
    ACT = "act"

    def __lt__(self, other: object) -> bool:
        return _rank(self) < _rank(other)

    def __le__(self, other: object) -> bool:
        return _rank(self) <= _rank(other)

    def __gt__(self, other: object) -> bool:
        return _rank(self) > _rank(other)

    def __ge__(self, other: object) -> bool:
        return _rank(self) >= _rank(other)

    def __bool__(self) -> bool:
        return _rank(self) > 0


_PORTAL_ACCESS_RANKS = {
    PortalAccessLevel.NONE: 0,
    PortalAccessLevel.VIEW: 1,
    PortalAccessLevel.ACT: 2,
}


def _rank(level: object) -> int:
    if not isinstance(level, str):
        raise TypeError(f"Cannot compare a portal access level with {type(level).__name__}")
    return _PORTAL_ACCESS_RANKS[PortalAccessLevel(level)]


__exports__ = ()

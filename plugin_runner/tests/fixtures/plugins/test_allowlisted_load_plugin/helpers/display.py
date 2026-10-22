import decimal


def has_precision() -> str:
    """Read the shared decimal context, as a command display helper might."""
    return str(decimal.getcontext().prec > 0)

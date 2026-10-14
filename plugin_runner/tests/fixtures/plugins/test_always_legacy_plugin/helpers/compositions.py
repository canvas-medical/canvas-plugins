def count_items(items: list[str]) -> int:
    """Count with a closure that updates the enclosing total."""
    total = 0

    def add() -> None:
        nonlocal total
        total += 1

    for _item in items:
        add()

    return total

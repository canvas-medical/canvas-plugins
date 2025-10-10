"""
Priority Selector Utility.

Provides priority-based selection logic for extracting credentials and licenses.
"""

from typing import Callable, TypeVar

from logger import log

T = TypeVar("T")


class PrioritySelector:
    """Utility for priority-based selection from collections."""

    @staticmethod
    def select_by_priority(
        items: list[T],
        state_match: Callable[[T], bool],
        is_primary: Callable[[T], bool],
        patient_state: str | None = None,
        item_description: str = "item",
    ) -> T | None:
        """
        Select item using priority logic:
        1. State match + Primary
        2. State match only
        3. Primary (any state)
        4. First available

        Args:
            items: List of items to select from
            state_match: Function to check if item matches patient state
            is_primary: Function to check if item is marked as primary
            patient_state: Patient's address state code (e.g., 'CA', 'NY')
            item_description: Description of item type for logging

        Returns:
            Selected item or None if list is empty
        """
        if not items:
            log.info(f"PrioritySelector: No {item_description}s available")
            return None

        # Priority 1: State match + Primary
        if patient_state:
            for item in items:
                if state_match(item) and is_primary(item):
                    log.info(
                        f"PrioritySelector: Selected {item_description} (Priority 1: state+primary)"
                    )
                    return item

        # Priority 2: State match only
        if patient_state:
            for item in items:
                if state_match(item):
                    log.info(
                        f"PrioritySelector: Selected {item_description} (Priority 2: state match)"
                    )
                    return item

        # Priority 3: Primary (any state)
        for item in items:
            if is_primary(item):
                log.info(f"PrioritySelector: Selected {item_description} (Priority 3: primary)")
                return item

        # Priority 4: First available
        log.info(f"PrioritySelector: Selected {item_description} (Priority 4: first available)")
        return items[0]


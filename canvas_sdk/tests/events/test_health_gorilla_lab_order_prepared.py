from canvas_generated.messages.events_pb2 import EventType


def test_health_gorilla_lab_order_prepared_enum_value() -> None:
    """Pin the proto enum value so a re-numbering would fail the test rather
    than silently shift wire IDs and break in-flight plugin handlers.
    """
    assert EventType.HEALTH_GORILLA_LAB_ORDER_PREPARED == 25024


def test_health_gorilla_lab_order_prepared_name_resolves() -> None:
    """Plugin handlers use `EventType.Name(EventType.HEALTH_GORILLA_LAB_ORDER_PREPARED)`
    in their RESPONDS_TO; pin the round-trip so a typo or rename can't slip through.
    """
    assert (
        EventType.Name(EventType.HEALTH_GORILLA_LAB_ORDER_PREPARED)
        == "HEALTH_GORILLA_LAB_ORDER_PREPARED"
    )

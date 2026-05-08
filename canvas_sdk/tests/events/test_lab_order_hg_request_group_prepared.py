from canvas_generated.messages.events_pb2 import EventType


def test_lab_order_hg_request_group_prepared_enum_value() -> None:
    """Pin the proto enum value so a re-numbering would fail the test rather
    than silently shift wire IDs and break in-flight plugin handlers.
    """
    assert EventType.LAB_ORDER_HG_REQUEST_GROUP_PREPARED == 25024


def test_lab_order_hg_request_group_prepared_name_resolves() -> None:
    """Plugin handlers use `EventType.Name(EventType.LAB_ORDER_HG_REQUEST_GROUP_PREPARED)`
    in their RESPONDS_TO; pin the round-trip so a typo or rename can't slip through.
    """
    assert (
        EventType.Name(EventType.LAB_ORDER_HG_REQUEST_GROUP_PREPARED)
        == "LAB_ORDER_HG_REQUEST_GROUP_PREPARED"
    )

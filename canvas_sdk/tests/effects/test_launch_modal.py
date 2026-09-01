import json

import pytest

from canvas_sdk.effects.launch_modal import LaunchModalEffect


def _payload(effect: LaunchModalEffect) -> dict:
    """The data dict home-app reads off the wire."""
    return json.loads(effect.apply().payload)["data"]


def test_docked_pane_target_reaches_the_wire_as_a_string() -> None:
    """`docked_pane` is what routes an application into the persistent dock layer.

    The target travels as a plain string inside the effect's JSON payload — it is not a
    protobuf enum — which is why adding a target needs no protobuf regeneration. It does
    still have to match home-app's hand-written ``TargetTypeEnum`` exactly; a mismatch
    nulls the field there with no effect on this side.
    """
    effect = LaunchModalEffect(
        url="/plugin-io/api/my_plugin/pane",
        target=LaunchModalEffect.TargetType.DOCKED_PANE,
    )

    assert _payload(effect)["target"] == "docked_pane"


def test_docked_pane_carries_url_and_title_like_any_other_target() -> None:
    """A docked pane is an ordinary LaunchModalEffect; only its destination differs."""
    effect = LaunchModalEffect(
        url="/plugin-io/api/my_plugin/pane",
        target=LaunchModalEffect.TargetType.DOCKED_PANE,
        title="Patient list",
    )

    payload = _payload(effect)
    assert payload["url"] == "/plugin-io/api/my_plugin/pane"
    assert payload["title"] == "Patient list"
    assert payload["content"] is None


def test_a_docked_pane_can_be_served_from_inline_content() -> None:
    """`content` works for docks too, for panes that don't need a SimpleAPI route."""
    effect = LaunchModalEffect(
        content="<p>hello</p>",
        target=LaunchModalEffect.TargetType.DOCKED_PANE,
    )

    assert _payload(effect)["content"] == "<p>hello</p>"


def test_url_and_content_stay_mutually_exclusive_for_docked_panes() -> None:
    """The existing validator applies unchanged; the new target is not a special case."""
    with pytest.raises(ValueError, match="mutually exclusive"):
        LaunchModalEffect(
            url="/plugin-io/api/my_plugin/pane",
            content="<p>hello</p>",
            target=LaunchModalEffect.TargetType.DOCKED_PANE,
        )


def test_the_edge_is_not_part_of_the_effect() -> None:
    """Which edge a pane docks to comes from the manifest, never from the effect.

    One target rather than four (DOCK_LEFT, DOCK_RIGHT, …) keeps a single source of
    truth for the edge and lets the shell reserve the track before `on_open` resolves.
    A plugin therefore cannot move itself between edges at runtime, which is deliberate.
    """
    targets = {t.value for t in LaunchModalEffect.TargetType}

    assert "docked_pane" in targets
    assert not any(t.startswith("dock_") for t in targets)


@pytest.mark.parametrize(
    "target",
    [
        LaunchModalEffect.TargetType.DEFAULT_MODAL,
        LaunchModalEffect.TargetType.RIGHT_CHART_PANE,
        LaunchModalEffect.TargetType.RIGHT_CHART_PANE_LARGE,
        LaunchModalEffect.TargetType.NEW_WINDOW,
        LaunchModalEffect.TargetType.PAGE,
        LaunchModalEffect.TargetType.NOTE,
    ],
    ids=lambda t: t.value,
)
def test_existing_targets_are_unchanged(target: LaunchModalEffect.TargetType) -> None:
    """Adding the dock target must not disturb any surface already in use."""
    effect = LaunchModalEffect(url="/plugin-io/api/my_plugin/ui", target=target)

    assert _payload(effect)["target"] == target.value

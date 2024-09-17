import pytest
from pydantic import ValidationError

from canvas_sdk.effects.protocol_card import ProtocolCard, Recommendation


@pytest.mark.parametrize(
    "init_params,rec1_params,rec2_params",
    [
        (
            {
                "key": "link_rec",
                "patient_id": "patientuuid",
                "title": "This is a test!",
                "narrative": "we should only expect a link and a button",
            },
            {
                "title": "this is a link",
                "button": "click this",
                "href": "https://canvasmedical.com/",
            },
            {"title": "second link", "button": "don't click this", "href": "https://google.com/"},
        ),
        (
            {
                "key": "command_rec",
                "patient_id": "patientuuid",
                "title": "This is a test for command recommendations!",
                "narrative": "we should only expect buttons to insert commands",
            },
            {
                "title": "this is a command",
                "button": "click this",
                "command": {"type": "updategoal"},
                "context": {"progress": "none"},
            },
            {
                "title": "another command",
                "button": "hypertension",
                "command": {"type": "diagnose"},
                "context": {"background": "stuff"},
            },
        ),
        (
            {
                "patient_id": "patientuuid",
                "key": "command_rec_with_coding_filter",
                "title": "This is a test for command recommendations with coding filters!",
                "narrative": "we should only expect buttons to insert commands",
            },
            {
                "title": "hypertension",
                "button": "diagnose",
                "command": {
                    "type": "diagnose",
                    "filter": {"coding": [{"code": "I10", "system": "icd10cm"}]},
                },
                "context": {"background": "hey"},
            },
            {
                "title": "fake medication",
                "button": "prescribe",
                "command": {
                    "type": "prescribe",
                    "filter": {"coding": [{"code": "fake", "system": "fdb"}]},
                },
                "context": {"sig": "1pobid"},
            },
        ),
    ],
)
def test_add_recommendations(
    init_params: dict[str, str], rec1_params: dict[str, str], rec2_params: dict[str, str]
) -> None:
    p = ProtocolCard(**init_params)
    p.add_recommendation(**rec1_params)
    p.recommendations.append(Recommendation(**rec2_params))

    assert p.values == {
        "title": init_params["title"],
        "narrative": init_params["narrative"],
        "recommendations": [
            {
                "title": rec1_params.get("title", None),
                "button": rec1_params.get("button", None),
                "href": rec1_params.get("href", None),
                "command": rec1_params.get("command", None),
                "context": rec1_params.get("context", None),
            },
            {
                "title": rec2_params.get("title", None),
                "button": rec2_params.get("button", None),
                "href": rec2_params.get("href", None),
                "command": rec2_params.get("command", None),
                "context": rec2_params.get("context", None),
            },
        ],
        "status": "due",
    }


def test_add_recommendations_with_command_coding_filter_raises_error_when_invalid_coding_system() -> (
    None
):
    p = ProtocolCard()

    with pytest.raises(ValidationError) as e1:
        p.add_recommendation(
            title="hypertension",
            button="diagnose",
            command={
                "type": "diagnose",
                "filter": {"coding": [{"code": "I10", "system": "something-else"}]},
            },
            context={"background": "hey"},
        )
    err_msg1 = repr(e1.value)
    assert "1 validation error for Recommendation" in err_msg1
    assert "command.filter.coding.0.system" in err_msg1
    assert (
        "Input should be 'cpt', 'cvx', 'snomedct', 'rxnorm', 'loinc', 'icd10cm', 'fdb' or 'ndc'"
        in err_msg1
    )

    with pytest.raises(ValidationError) as e2:
        p.recommendations.append(
            Recommendation(
                title="fake medication",
                button="prescribe",
                command={"type": "prescribe", "filter": {"coding": [{"code": "fake"}]}},
                context={"sig": "1pobid"},
            )
        )
    err_msg2 = repr(e2.value)
    assert "1 validation error for Recommendation" in err_msg2
    assert "command.filter.coding.0.system" in err_msg2
    assert "Field required [type=missing, input_value={'code': 'fake'}" in err_msg2

    assert p.values["recommendations"] == []


def test_apply_method_succeeds_with_patient_id_and_key() -> None:
    p = ProtocolCard(patient_id="uuid", key="something-unique")
    applied = p.apply()
    assert (
        applied.payload
        == '{"patient": "uuid", "key": "something-unique", "data": {"title": "", "narrative": "", "recommendations": [], "status": "due"}}'
    )


def test_apply_method_raises_error_without_patient_id_and_key() -> None:
    p = ProtocolCard()

    with pytest.raises(ValidationError) as e:
        p.apply()
    err_msg = repr(e.value)

    assert "2 validation errors for ProtocolCard" in err_msg
    assert (
        "Field 'patient_id' is required to apply a ProtocolCard [type=missing, input_value=None, input_type=NoneType]"
        in err_msg
    )
    assert (
        "Field 'key' is required to apply a ProtocolCard [type=missing, input_value=None, input_type=NoneType]"
        in err_msg
    )

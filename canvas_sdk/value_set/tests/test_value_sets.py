from canvas_sdk.value_set.v2022.condition import (
    DisordersOfTheImmuneSystem,
    EncephalopathyDueToChildhoodVaccination,
    Rhabdomyolysis,
    StableAndUnstableAngina,
)
from canvas_sdk.value_set.value_set import CombinedValueSet


def test_value_set_class_values_property() -> None:
    value_set = DisordersOfTheImmuneSystem
    assert value_set.values["ICD10CM"] == DisordersOfTheImmuneSystem.ICD10CM
    assert value_set.values["SNOMEDCT"] == DisordersOfTheImmuneSystem.SNOMEDCT


def test_value_set_class_pipe_operator_with_two_value_sets() -> None:
    combined_value_set: CombinedValueSet = (
        DisordersOfTheImmuneSystem | EncephalopathyDueToChildhoodVaccination
    )

    both_classes_icd_10_codes = DisordersOfTheImmuneSystem.ICD10CM.union(
        EncephalopathyDueToChildhoodVaccination.ICD10CM
    )
    both_classes_snomed_codes = DisordersOfTheImmuneSystem.SNOMEDCT.union(
        EncephalopathyDueToChildhoodVaccination.SNOMEDCT
    )

    assert both_classes_icd_10_codes == combined_value_set.values["ICD10CM"]
    assert both_classes_snomed_codes == combined_value_set.values["SNOMEDCT"]


def test_value_set_class_pipe_operator_with_three_value_sets() -> None:
    combined_value_set: CombinedValueSet = (
        DisordersOfTheImmuneSystem | EncephalopathyDueToChildhoodVaccination | Rhabdomyolysis
    )

    all_classes_icd_10_codes = DisordersOfTheImmuneSystem.ICD10CM.union(
        EncephalopathyDueToChildhoodVaccination.ICD10CM
    ).union(Rhabdomyolysis.ICD10CM)
    all_classes_snomed_codes = DisordersOfTheImmuneSystem.SNOMEDCT.union(
        EncephalopathyDueToChildhoodVaccination.SNOMEDCT
    ).union(Rhabdomyolysis.SNOMEDCT)

    assert all_classes_icd_10_codes == combined_value_set.values["ICD10CM"]
    assert all_classes_snomed_codes == combined_value_set.values["SNOMEDCT"]


def test_value_set_class_pipe_operator_with_two_combined_value_sets() -> None:
    combined_value_set_1: CombinedValueSet = (
        DisordersOfTheImmuneSystem | EncephalopathyDueToChildhoodVaccination
    )
    combined_value_set_2: CombinedValueSet = Rhabdomyolysis | StableAndUnstableAngina

    combined_value_set = combined_value_set_1 | combined_value_set_2

    all_classes_icd_10_codes = (
        DisordersOfTheImmuneSystem.ICD10CM.union(EncephalopathyDueToChildhoodVaccination.ICD10CM)
        .union(Rhabdomyolysis.ICD10CM)
        .union(StableAndUnstableAngina.ICD10CM)
    )
    all_classes_snomed_codes = (
        DisordersOfTheImmuneSystem.SNOMEDCT.union(EncephalopathyDueToChildhoodVaccination.SNOMEDCT)
        .union(Rhabdomyolysis.SNOMEDCT)
        .union(StableAndUnstableAngina.SNOMEDCT)
    )

    assert combined_value_set.values["ICD10CM"] == all_classes_icd_10_codes
    assert combined_value_set.values["SNOMEDCT"] == all_classes_snomed_codes

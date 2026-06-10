from canvas_sdk.v1.data.chart_section_review import (
    ChartSectionReview,
    ChartSectionReviewSection,
)


def test_section_choices() -> None:
    """The section choices mirror the chart sections home-app exposes."""
    assert ChartSectionReviewSection.CONDITIONS == "conditions"
    assert ChartSectionReviewSection.MEDICATIONS == "medications"
    assert ChartSectionReviewSection.FAMILY_HISTORIES == "family_histories"


def test_review_fields() -> None:
    """A review exposes its section, content, entries, and patient/note FKs."""
    review = ChartSectionReview()
    review.patient_id = 11
    review.note_id = 22
    review.section = ChartSectionReviewSection.CONDITIONS
    review.entries = [1, 2, 3]
    review.content = "- Hypertension\n- Type 2 diabetes"

    assert review.patient_id == 11
    assert review.note_id == 22
    assert review.section == "conditions"
    assert review.entries == [1, 2, 3]
    assert review.content == "- Hypertension\n- Type 2 diabetes"

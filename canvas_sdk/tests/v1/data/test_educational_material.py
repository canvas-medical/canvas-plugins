import pytest

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    EducationalMaterialFactory,
)
from canvas_sdk.v1.data.educational_material import EducationalMaterial


@pytest.mark.django_db
def test_educational_material_fields_round_trip() -> None:
    """An EducationalMaterial's fields are readable through the data model."""
    material = EducationalMaterialFactory.create(
        article_id="98765",
        selected_language="es",
        title="Controlando la diabetes",
        languages=["en-us", "es"],
        abstract="Resumen del articulo.",
    )

    fetched = EducationalMaterial.objects.get(dbid=material.dbid)

    assert fetched.article_id == "98765"
    assert fetched.selected_language == "es"
    assert fetched.title == "Controlando la diabetes"
    assert fetched.languages == ["en-us", "es"]
    assert fetched.abstract == "Resumen del articulo."
    assert fetched.patient_id == material.patient_id
    assert fetched.note_id == material.note_id


@pytest.mark.django_db
def test_committed_excludes_uncommitted() -> None:
    """committed() returns only materials with a committer and no entered_in_error."""
    committer = CanvasUserFactory.create()
    committed = EducationalMaterialFactory.create(committer=committer)
    EducationalMaterialFactory.create(committer=None)

    result = list(EducationalMaterial.objects.committed())

    assert [m.dbid for m in result] == [committed.dbid]

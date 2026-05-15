import pytest

from canvas_sdk.clients.extend_ai.constants.processor_type import ProcessorType
from canvas_sdk.clients.extend_ai.constants.run_status import RunStatus
from canvas_sdk.clients.extend_ai.structures.processor_meta import ProcessorMeta
from canvas_sdk.clients.extend_ai.structures.processor_result import (
    Insight,
    ResultClassification,
    ResultExtraction,
    ResultSplitter,
    Split,
)
from canvas_sdk.clients.extend_ai.structures.processor_run import ProcessorRun
from canvas_sdk.clients.extend_ai.structures.stored_file import StoredFile
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test that ProcessorRun is a dataclass with the expected field types."""
    tested = ProcessorRun
    fields = {
        "id": str,
        "processor": ProcessorMeta,
        "output": ResultClassification | ResultExtraction | ResultSplitter | None,
        "status": RunStatus,
        "files": list[StoredFile],
        "usage": int,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "id": "run123",
                "processorId": "proc123",
                "processorName": "extractProcessor",
                "type": "EXTRACT",
                "output": {"value": {"key1": 33, "key2": "theKey2"}},
                "status": "PROCESSED",
                "files": [
                    {"id": "file1", "type": "PDF", "name": "doc1.pdf", "usage": {"credits": 10}},
                    {"id": "file2", "type": "PDF", "name": "doc2.pdf", "usage": {"credits": 15}},
                ],
                "usage": {"credits": 21},
            },
            ProcessorRun(
                id="run123",
                processor=ProcessorMeta(
                    id="proc123",
                    name="extractProcessor",
                    type=ProcessorType.EXTRACT,
                    created_at=None,
                    updated_at=None,
                ),
                output=ResultExtraction(value={"key1": 33, "key2": "theKey2"}),
                status=RunStatus.PROCESSED,
                files=[
                    StoredFile(id="file1", type="PDF", name="doc1.pdf"),
                    StoredFile(id="file2", type="PDF", name="doc2.pdf"),
                ],
                usage=46,
            ),
            id="extract_processed_with_two_files",
        ),
        pytest.param(
            {
                "id": "run456",
                "processorId": "proc456",
                "processorName": "classifyProcessor",
                "type": "CLASSIFY",
                "output": {
                    "type": "theClassification",
                    "confidence": 0.97,
                    "insights": [{"type": "theInsightType", "content": "theInsightContent"}],
                },
                "status": "PROCESSED",
                "files": [{"id": "file3", "type": "PDF", "name": "doc3.pdf"}],
                "usage": {"credits": 18},
            },
            ProcessorRun(
                id="run456",
                processor=ProcessorMeta(
                    id="proc456",
                    name="classifyProcessor",
                    type=ProcessorType.CLASSIFY,
                    created_at=None,
                    updated_at=None,
                ),
                output=ResultClassification(
                    type="theClassification",
                    confidence=0.97,
                    insights=[Insight(type="theInsightType", content="theInsightContent")],
                ),
                status=RunStatus.PROCESSED,
                files=[
                    StoredFile(id="file3", type="PDF", name="doc3.pdf"),
                ],
                usage=18,
            ),
            id="classify_processed_with_one_file",
        ),
        pytest.param(
            {
                "id": "run789",
                "processorId": "proc789",
                "processorName": "splitterProcessor",
                "type": "SPLITTER",
                "output": {
                    "splits": [
                        {
                            "type": "type1",
                            "observation": "observation1",
                            "identifier": "identifier1",
                            "startPage": 1,
                            "endPage": 1,
                            "classificationId": "subdocumentType1",
                            "id": "splitId1",
                            "fileId": "splitFile1",
                            "name": "name1",
                        },
                        {
                            "type": "type2",
                            "observation": "observation2",
                            "identifier": "identifier2",
                            "startPage": 2,
                            "endPage": 2,
                            "classificationId": "subdocumentType2",
                            "id": "splitId2",
                            "fileId": "splitFile2",
                            "name": "name2",
                        },
                        {
                            "type": "type3",
                            "observation": "observation3",
                            "identifier": "identifier3",
                            "startPage": 3,
                            "endPage": 5,
                            "classificationId": "subdocumentType3",
                            "id": "splitId3",
                            "fileId": "splitFile3",
                            "name": "name3",
                        },
                    ]
                },
                "status": "PROCESSED",
                "files": [
                    {"id": "file4", "type": "PDF", "name": "doc4.pdf", "usage": {"credits": 5}}
                ],
                "usage": {"credits": 29},
            },
            ProcessorRun(
                id="run789",
                processor=ProcessorMeta(
                    id="proc789",
                    name="splitterProcessor",
                    type=ProcessorType.SPLITTER,
                    created_at=None,
                    updated_at=None,
                ),
                output=ResultSplitter(
                    splits=[
                        Split(
                            type="type1",
                            observation="observation1",
                            identifier="identifier1",
                            startPage=1,
                            endPage=1,
                            classificationId="subdocumentType1",
                            id="splitId1",
                            fileId="splitFile1",
                            name="name1",
                        ),
                        Split(
                            type="type2",
                            observation="observation2",
                            identifier="identifier2",
                            startPage=2,
                            endPage=2,
                            classificationId="subdocumentType2",
                            id="splitId2",
                            fileId="splitFile2",
                            name="name2",
                        ),
                        Split(
                            type="type3",
                            observation="observation3",
                            identifier="identifier3",
                            startPage=3,
                            endPage=5,
                            classificationId="subdocumentType3",
                            id="splitId3",
                            fileId="splitFile3",
                            name="name3",
                        ),
                    ]
                ),
                status=RunStatus.PROCESSED,
                files=[StoredFile(id="file4", type="PDF", name="doc4.pdf")],
                usage=34,
            ),
            id="split_processed_with_one_file",
        ),
        pytest.param(
            {
                "id": "run147",
                "processorId": "proc147",
                "processorName": "splitterProcessor",
                "type": "SPLITTER",
                "output": None,
                "status": "FAILED",
                "files": [],
                "usage": {"credits": 37},
            },
            ProcessorRun(
                id="run147",
                processor=ProcessorMeta(
                    id="proc147",
                    name="splitterProcessor",
                    type=ProcessorType.SPLITTER,
                    created_at=None,
                    updated_at=None,
                ),
                output=None,
                status=RunStatus.FAILED,
                files=[],
                usage=37,
            ),
            id="split_failed_with_no_file",
        ),
    ],
)
def test_from_dict(data: dict, expected: ProcessorRun) -> None:
    """Test ProcessorRun.from_dict correctly deserializes processor run data and calculates usage credits."""
    tested = ProcessorRun
    result = tested.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("tested", "expected"),
    [
        pytest.param(
            ProcessorRun(
                id="run789",
                processor=ProcessorMeta(
                    id="proc789",
                    name="splitterProcessor",
                    type=ProcessorType.SPLITTER,
                    created_at=None,
                    updated_at=None,
                ),
                output=ResultSplitter(
                    splits=[
                        Split(
                            type="type1",
                            observation="observation1",
                            identifier="identifier1",
                            startPage=1,
                            endPage=1,
                            classificationId="subdocumentType1",
                            id="splitId1",
                            fileId="splitFile1",
                            name="name1",
                        ),
                        Split(
                            type="type2",
                            observation="observation2",
                            identifier="identifier2",
                            startPage=2,
                            endPage=2,
                            classificationId="subdocumentType2",
                            id="splitId2",
                            fileId="splitFile2",
                            name="name2",
                        ),
                        Split(
                            type="type3",
                            observation="observation3",
                            identifier="identifier3",
                            startPage=3,
                            endPage=5,
                            classificationId="subdocumentType3",
                            id="splitId3",
                            fileId="splitFile3",
                            name="name3",
                        ),
                    ]
                ),
                status=RunStatus.PROCESSED,
                files=[StoredFile(id="file4", type="PDF", name="doc4.pdf")],
                usage=34,
            ),
            {
                "id": "run789",
                "processor": {
                    "id": "proc789",
                    "name": "splitterProcessor",
                    "type": "SPLITTER",
                    "createdAt": None,
                    "updatedAt": None,
                },
                "output": {
                    "splits": [
                        {
                            "type": "type1",
                            "observation": "observation1",
                            "identifier": "identifier1",
                            "startPage": 1,
                            "endPage": 1,
                            "classificationId": "subdocumentType1",
                            "id": "splitId1",
                            "fileId": "splitFile1",
                            "name": "name1",
                        },
                        {
                            "type": "type2",
                            "observation": "observation2",
                            "identifier": "identifier2",
                            "startPage": 2,
                            "endPage": 2,
                            "classificationId": "subdocumentType2",
                            "id": "splitId2",
                            "fileId": "splitFile2",
                            "name": "name2",
                        },
                        {
                            "type": "type3",
                            "observation": "observation3",
                            "identifier": "identifier3",
                            "startPage": 3,
                            "endPage": 5,
                            "classificationId": "subdocumentType3",
                            "id": "splitId3",
                            "fileId": "splitFile3",
                            "name": "name3",
                        },
                    ]
                },
                "status": "PROCESSED",
                "files": [{"id": "file4", "type": "PDF", "name": "doc4.pdf"}],
                "usage": 34,
            },
            id="split_processed_with_one_file",
        ),
        pytest.param(
            ProcessorRun(
                id="run147",
                processor=ProcessorMeta(
                    id="proc147",
                    name="splitterProcessor",
                    type=ProcessorType.SPLITTER,
                    created_at=None,
                    updated_at=None,
                ),
                output=None,
                status=RunStatus.FAILED,
                files=[],
                usage=37,
            ),
            {
                "id": "run147",
                "processor": {
                    "id": "proc147",
                    "name": "splitterProcessor",
                    "type": "SPLITTER",
                    "createdAt": None,
                    "updatedAt": None,
                },
                "output": None,
                "status": "FAILED",
                "files": [],
                "usage": 37,
            },
            id="split_failed_with_no_file",
        ),
    ],
)
def test_to_dict(tested: ProcessorRun, expected: dict) -> None:
    """Test ProcessorRun.to_dict correctly serializes processor run data for API requests."""
    result = tested.to_dict()
    assert result == expected

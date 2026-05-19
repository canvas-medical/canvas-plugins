from canvas_sdk.effects.data_integration.types import AnnotationItem

CBC_WITH_DIFFERENTIAL_TEMPLATE = {
    "template_id": 5009,
    "template_name": "Complete Blood Count (Cbc) With Differential",
    "fields": {
        "6690-2": {
            "value": "17.2",
            "unit": "10*3/uL",
            "abnormal": True,
            "reference_range": "4.5 - 11.0 10*3/uL",
            "annotations": [AnnotationItem(text="AI 94%", color="#4CAF50")],
        },
        "WBC": {
            "value": "7.2",
            "unit": "10*3/uL",
            "reference_range": "4.5 - 11.0 10*3/uL",
            "annotations": [AnnotationItem(text="AI 94%", color="#4CAF50")],
        },
        "789-8": {
            "value": "4.85",
            "unit": "10*6/uL",
            "reference_range": "4.50 - 5.90 10*6/uL",
            "annotations": [AnnotationItem(text="AI 91%", color="#4CAF50")],
        },
        "RBC": {
            "value": "4.85",
            "unit": "10*6/uL",
            "reference_range": "4.50 - 5.90 10*6/uL",
            "annotations": [AnnotationItem(text="AI 91%", color="#4CAF50")],
        },
        "718-7": {
            "value": "14.2",
            "unit": "g/dL",
            "reference_range": "13.5 - 17.5 g/dL",
            "annotations": [AnnotationItem(text="AI 93%", color="#4CAF50")],
        },
        "Hemoglobin": {
            "value": "14.2",
            "unit": "g/dL",
            "reference_range": "13.5 - 17.5 g/dL",
            "annotations": [AnnotationItem(text="AI 93%", color="#4CAF50")],
        },
        "4544-3": {
            "value": "42.1",
            "unit": "%",
            "reference_range": "38.3 - 48.6 %",
            "annotations": [AnnotationItem(text="AI 90%", color="#4CAF50")],
        },
        "Hematocrit": {
            "value": "42.1",
            "unit": "%",
            "reference_range": "38.3 - 48.6 %",
            "annotations": [AnnotationItem(text="AI 90%", color="#4CAF50")],
        },
        "777-3": {
            "value": "250",
            "unit": "10*3/uL",
            "reference_range": "150 - 400 10*3/uL",
            "annotations": [
                AnnotationItem(text="AI 88%", color="#4CAF50"),
                AnnotationItem(text="Verify", color="#FF9800"),
            ],
        },
        "Platelet Count": {
            "value": "250",
            "unit": "10*3/uL",
            "reference_range": "150 - 400 10*3/uL",
            "annotations": [
                AnnotationItem(text="AI 88%", color="#4CAF50"),
                AnnotationItem(text="Verify", color="#FF9800"),
            ],
        },
    },
}

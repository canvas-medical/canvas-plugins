from canvas_sdk.effects.data_integration.types import AnnotationItem

LIPID_PANEL_TEMPLATE = {
    "template_id": 303756,
    "template_name": "Lipid Panel",
    "fields": {
        "2093-3": {
            "value": "245",
            "unit": "mg/dL",
            "reference_range": "< 200 mg/dL",
            "abnormal": True,
            "annotations": [
                AnnotationItem(text="AI 95%", color="#4CAF50"),
                AnnotationItem(text="High", color="#F44336"),
            ],
        },
        "Total Cholesterol": {
            "value": "245",
            "unit": "mg/dL",
            "reference_range": "< 200 mg/dL",
            "abnormal": True,
            "annotations": [
                AnnotationItem(text="AI 95%", color="#4CAF50"),
                AnnotationItem(text="High", color="#F44336"),
            ],
        },
        "2085-9": {
            "value": "55",
            "unit": "mg/dL",
            "reference_range": "> 40 mg/dL",
            "annotations": [AnnotationItem(text="AI 92%", color="#4CAF50")],
        },
        "HDL Cholesterol": {
            "value": "55",
            "unit": "mg/dL",
            "reference_range": "> 40 mg/dL",
            "annotations": [AnnotationItem(text="AI 92%", color="#4CAF50")],
        },
        "13457-7": {
            "value": "160",
            "unit": "mg/dL",
            "reference_range": "< 100 mg/dL",
            "abnormal": True,
            "annotations": [
                AnnotationItem(text="AI 90%", color="#4CAF50"),
                AnnotationItem(text="High", color="#F44336"),
            ],
        },
        "LDL Cholesterol": {
            "value": "160",
            "unit": "mg/dL",
            "reference_range": "< 100 mg/dL",
            "abnormal": True,
            "annotations": [
                AnnotationItem(text="AI 90%", color="#4CAF50"),
                AnnotationItem(text="High", color="#F44336"),
            ],
        },
        "2571-8": {
            "value": "150",
            "unit": "mg/dL",
            "reference_range": "< 150 mg/dL",
            "annotations": [
                AnnotationItem(text="AI 85%", color="#FFC107"),
                AnnotationItem(text="Borderline", color="#FF9800"),
            ],
        },
        "Triglycerides": {
            "value": "150",
            "unit": "mg/dL",
            "reference_range": "< 150 mg/dL",
            "annotations": [
                AnnotationItem(text="AI 85%", color="#FFC107"),
                AnnotationItem(text="Borderline", color="#FF9800"),
            ],
        },
    },
}

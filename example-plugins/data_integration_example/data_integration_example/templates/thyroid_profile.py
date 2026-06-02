from canvas_sdk.effects.data_integration.types import AnnotationItem

THYROID_PROFILE_TEMPLATE = {
    "template_id": 620,
    "template_name": "Thyroid Profile With Tsh",
    "fields": {
        "11580-8": {
            "value": "9.35",
            "unit": "uIU/mL",
            "reference_range": "0.45 - 4.50 uIU/mL",
            "abnormal": True,
            "annotations": [AnnotationItem(text="AI 92%", color="#4CAF50")],
        },
        "Thyroid Stimulating Hormone": {
            "value": "2.35",
            "unit": "uIU/mL",
            "reference_range": "0.45 - 4.50 uIU/mL",
            "annotations": [AnnotationItem(text="AI 92%", color="#4CAF50")],
        },
        "3026-2": {
            "value": "13.5",
            "unit": "ug/dL",
            "reference_range": "4.5 - 12.0 ug/dL",
            "abnormal": True,
            "annotations": [
                AnnotationItem(text="AI 89%", color="#4CAF50"),
                AnnotationItem(text="High", color="#F44336"),
            ],
        },
        "Thyroxine (T4)": {
            "value": "13.5",
            "unit": "ug/dL",
            "reference_range": "4.5 - 12.0 ug/dL",
            "abnormal": True,
            "annotations": [
                AnnotationItem(text="AI 89%", color="#4CAF50"),
                AnnotationItem(text="High", color="#F44336"),
            ],
        },
        "3050-2": {
            "value": "32",
            "unit": "%",
            "reference_range": "24 - 39 %",
            "annotations": [
                AnnotationItem(text="AI 87%", color="#4CAF50"),
                AnnotationItem(text="Verify", color="#FF9800"),
            ],
        },
        "T3 Uptake": {
            "value": "32",
            "unit": "%",
            "reference_range": "24 - 39 %",
            "annotations": [
                AnnotationItem(text="AI 87%", color="#4CAF50"),
                AnnotationItem(text="Verify", color="#FF9800"),
            ],
        },
        "32215-6": {
            "value": "2.5",
            "reference_range": "1.2 - 4.9",
            "annotations": [
                AnnotationItem(text="AI 78%", color="#FFC107"),
                AnnotationItem(text="Low confidence", color="#F44336"),
            ],
        },
        "Free Thyroxine Index": {
            "value": "2.5",
            "reference_range": "1.2 - 4.9",
            "annotations": [
                AnnotationItem(text="AI 78%", color="#FFC107"),
                AnnotationItem(text="Low confidence", color="#F44336"),
            ],
        },
    },
}

# lab_results_modal

Adds a "Lab Results" button to the patient chart header. Clicking it opens a modal that lists the patient's lab reports and the values within
each report.

The modal demonstrates how to walk the `LabReport` → `LabTest` → `LabValue`
relationship using `LabReport.result_tests` (filtered to exclude the
"ordered test" rows that exist purely as fulfillment markers and carry no
values).

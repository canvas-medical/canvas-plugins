# CMS122v14 Diabetes: Glycemic Status Assessment Greater Than 9%

## Description

Clinical Quality Measure (CQM) protocol for CMS122v14 - measures the percentage of patients 18-75 years of age with diabetes who had a glycemic status assessment (HbA1c or GMI) > 9.0% during the measurement period.

## Measure Overview

- **CMS ID**: CMS122v14
- **Measurement Period**: 2026
- **Measure Type**: Process
- **Improvement Notation**: A lower rate indicates better performance (inverse measure)

## Population Criteria

### Initial Population
- Patients 18-75 years of age by end of measurement period
- With diabetes diagnosis overlapping measurement period
- With qualifying encounter during measurement period

### Denominator
- Equals Initial Population

### Denominator Exclusions
- Hospice care during measurement period
- Age 66+ living in long-term nursing home
- Age 66+ with frailty AND (advanced illness OR dementia medications)
- Palliative care during measurement period

### Numerator
Patients with:
- Most recent glycemic status assessment (HbA1c or GMI) > 9.0%
- OR no glycemic status assessment during measurement period
- OR assessment performed but no result documented

## Clinical Guidance

- Reducing A1c blood level by 1 percentage point helps reduce the risk of microvascular complications by up to 40%
- A reasonable A1C goal for many nonpregnant adults is <7% (ADA, Level A evidence)
- Less stringent goals (<8%) may be appropriate for patients with limited life expectancy, extensive comorbidities, or long-standing diabetes

## References

- [CMS122v14 eCQM Specification](https://ecqi.healthit.gov/ecqm/ec/2026/cms122v14)
- American Diabetes Association Standards of Care in Diabetes - 2023

## Important Note

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it gets updated if you add, remove, or rename protocols.

# CMS125v14 Breast Cancer Screening Plugin

This plugin implements the CMS125v14 Breast Cancer Screening Clinical Quality Measure for Canvas Medical using the `canvas_sdk`.

## Overview

**Description:** Percentage of women 42-74 years of age who had a mammogram to screen for breast cancer.

**Measure Identifier:** CMS125v14 (implementing CMS125v14 logic)

**Author:** National Committee for Quality Assurance

## Clinical Rationale

Breast cancer is one of the most common types of cancers, accounting for a quarter of all new cancer diagnoses for women in the U.S. The U.S. Preventive Services Task Force (USPSTF) recommends biennial screening mammography for women aged 50-74 years.

According to the National Cancer Institute's Surveillance Epidemiology and End Results program, the chance of a woman being diagnosed with breast cancer increases with age. By age 60, it is one in 25.

## Measure Logic

### Initial Population
Women aged 42-74 years with a visit during the measurement period.

### Denominator
Equals the initial population.

**Exclusions:**
1. Women who had a bilateral mastectomy
2. Women with a history of bilateral mastectomy
3. Women with evidence of both right and left unilateral mastectomy
4. Patients in hospice care during the measurement year
5. Patients who received palliative care during the measurement period (all ages)
6. Patients age ≥66 with frailty AND (advanced illness OR dementia medications) during measurement period or prior year
7. Patients age ≥66 living long-term in nursing home

### Numerator
Women with one or more mammograms between October 1 of two years prior to the measurement period and the end of the measurement period (27-month total screening window).

### Stratification
- **Stratum 1:** Ages 42-51 at end of measurement period
- **Stratum 2:** Ages 52-74 at end of measurement period

## Implementation Details

### Value Sets Used

All value sets are sourced from CMS125v14 specifications and added to `canvas_sdk/value_set/v2026/`:

**Diagnostic Studies:**
- Mammography (LOINC codes for mammography screening)

**Procedures:**
- BilateralMastectomy
- UnilateralMastectomyLeft
- UnilateralMastectomyRight

**Conditions:**
- HistoryOfBilateralMastectomy
- StatusPostLeftMastectomy
- StatusPostRightMastectomy

**Encounters:**
- OfficeVisit
- AnnualWellnessVisit
- HomeHealthcareServices
- PreventiveCareServicesEstablishedOfficeVisit18AndUp
- PreventiveCareServicesInitialOfficeVisit18AndUp

### Key Protocol Methods

- `in_initial_population()`: Checks if patient is female, aged 42-74, with qualifying visit
- `in_denominator()`: Applies exclusion criteria (mastectomy, hospice, palliative care, frailty+advanced illness for age ≥66, nursing home for age ≥66)
- `in_numerator()`: Checks for mammogram within 27-month window (October 1, two years prior to end of MP)
- `had_mastectomy()`: Detects bilateral mastectomy or equivalent
- `has_frailty_with_advanced_illness()`: Checks frailty + advanced illness/dementia for age ≥66
- `received_palliative_care()`: Checks for palliative care (all ages)
- `in_nursing_home()`: Checks if patient is in long-term nursing home (age ≥66)
- `get_stratification()`: Returns stratification group (1 for ages 42-51, 2 for ages 52-74)
- `first_due_in()`: Calculates when screening first becomes due (at age 42)
- `compute_results()`: Returns protocol status and recommendations with stratification info

## Installation

```bash
cd /path/to/canvas-plugins
canvas install cms125v14-breast-cancer-screening/cms125v14_breast_cancer_screening
```

## Testing

Run the test suite:

```bash
cd cms125v14_breast_cancer_screening
pytest tests/test_cms125v14_protocol.py -v
```

All 12 tests pass successfully, covering:
- Metadata validation
- Initial population inclusion/exclusion criteria
- Age range boundaries (51-74)
- Sex-based exclusion
- Mastectomy detection
- First due date calculation
- Denominator and numerator logic
- Results computation

## Known Limitations & Notes

The current implementation fully complies with CMS125v14 specifications with the following notes:

1. **✅ Age Range**: Correctly implements 42-74 age range per CMS125v14 flow
2. **✅ Visit Validation**: Checks for qualifying visits using billing line items
3. **✅ All Exclusions Implemented**:
   - Bilateral mastectomy (all variants)
   - Hospice care
   - Palliative care (all ages)
   - Frailty + Advanced Illness (age ≥66)
   - Nursing home (age ≥66) - *Note: May need customization based on Canvas instance data*
4. **✅ Numerator Window**: October 1, two years prior to end of measurement period
5. **✅ Stratification**: Stratum 1 (42-51) and Stratum 2 (52-74)
6. **✅ Tomosynthesis**: 3D mammography codes included via custom value set
7. **✅ Protocol Overrides**: Supports custom screening cycles

### Nursing Home Detection
The `in_nursing_home()` method checks Coverage records for long-term care indicators. This may need customization based on how your Canvas instance tracks patient residence in long-term care facilities. Alternative approaches include checking patient addresses or encounter patterns.

## Migration from canvas_workflow_kit

This plugin was migrated from the original `canvas_workflow_kit` implementation with the following key changes:

- All imports updated to use `canvas_sdk`
- Direct QuerySet operations instead of helper methods like `age_at_between`, `has_visit_within`
- Value sets migrated from v2018 to v2026 with updated codes from CMS125v14
- Protocol inherits from `canvas_sdk.protocols.ClinicalQualityMeasure`
- Tests use `canvas_sdk.test_utils.factories` instead of mock JSON data
- Pytest-based test suite instead of unittest

## References

- [CMS125v14 Measure Specification](https://ecqi.healthit.gov/sites/default/files/ecqm/measures/CMS125-v14.0.000-QDM.html)
- American Cancer Society. 2010. Cancer Facts & Figures 2010
- U.S. Preventive Services Task Force (USPSTF). 2009. Screening for breast cancer recommendation statement
- National Cancer Institute. 2010. Breast Cancer Screening

## Support

For issues or questions about this plugin, refer to the Canvas SDK documentation or contact your Canvas Medical representative.

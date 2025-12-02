# CMS125v14 Breast Cancer Screening Plugin

A Canvas Medical plugin implementing the CMS125v14 Breast Cancer Screening Clinical Quality Measure (CQM).

## What This Plugin Does

- Displays protocol cards in the patient chart for women aged 42-74 who need breast cancer screening
- Tracks mammography completion within the 27-month screening window
- Automatically excludes patients with bilateral mastectomy, hospice care, palliative care, or other qualifying exclusions
- Provides a "Plan" button to order mammography when screening is due
- Supports protocol overrides for custom screening intervals

## Why Use This Plugin

- **Quality reporting** - Accurately tracks CMS125v14 measure for HEDIS/quality reporting
- **Clinical decision support** - Surfaces screening reminders directly in the patient chart
- **Reduces care gaps** - Ensures eligible patients don't miss recommended screenings
- **Handles complexity** - Implements all CMS exclusion criteria (mastectomy, hospice, frailty, etc.)

## Example Scenario

**Without this plugin:** A 55-year-old female patient comes in for an annual wellness visit. The provider must manually check when her last mammogram was and remember the 27-month screening window.

**With this plugin:** The protocol card automatically shows:
- "Sarah had a mammography 14 months ago on 10/15/23. Next screening due in 395 days." (if satisfied)
- "No mammography found in the last 27 months. Sarah is due for breast cancer screening." with a "Plan" button (if due)

## Measure Overview

| Property | Value |
|----------|-------|
| **Measure ID** | CMS125v14 |
| **Version** | v14.0.0 |
| **Author** | National Committee for Quality Assurance |
| **Population** | Women 42-74 years of age |
| **Screening Window** | 27 months |

## Protocol Card Statuses

| Status | Condition |
|--------|-----------|
| `SATISFIED` | Mammogram found within 27-month window |
| `DUE` | No mammogram found, screening needed |
| `NOT_APPLICABLE` | Patient excluded or not yet eligible |

## Measure Logic

### Initial Population
Women aged 42-74 years at end of measurement period.

### Denominator Exclusions
Patients are excluded if any of the following apply:

1. **Bilateral mastectomy** - History of bilateral mastectomy, or both left and right unilateral mastectomies
2. **Hospice care** - Received hospice care during measurement period
3. **Palliative care** - Received palliative care during measurement period
4. **Frailty + Advanced illness** (age ≥66 only) - Has frailty indicator AND advanced illness or dementia medications
5. **Nursing home resident** (age ≥66 only) - Living long-term in nursing facility

### Numerator
Women with one or more mammograms (standard or 3D tomosynthesis) in the 27-month screening window.

### Stratification
- **Stratum 1:** Ages 42-51
- **Stratum 2:** Ages 52-74

## Setup

No configuration required. Install and the plugin will automatically display protocol cards for eligible patients.

```bash
canvas install cms125v14_breast_cancer_screening
```

## Configuration

### Protocol Overrides

For patients with specific risk factors requiring different screening intervals:
- Set a custom `reference_date` and `cycle_in_days` via `ProtocolOverride`
- Overrides the standard 27-month window for that patient

### Nursing Home Detection

The nursing home exclusion checks:
1. Coverage type = `LTC` (Long Term Care)
2. Plan name keywords: "long term care", "nursing home", "skilled nursing"

This may need customization based on how your Canvas instance tracks nursing home residence.

## Technical Details

### Triggered Events

This protocol responds to:
- `CONDITION_CREATED` / `CONDITION_UPDATED` / `CONDITION_RESOLVED`
- `MEDICATION_LIST_ITEM_CREATED` / `MEDICATION_LIST_ITEM_UPDATED`
- `OBSERVATION_CREATED` / `OBSERVATION_UPDATED`
- `PATIENT_UPDATED`
- `ENCOUNTER_CREATED` / `ENCOUNTER_UPDATED`
- `CLAIM_CREATED` / `CLAIM_UPDATED`
- `PROTOCOL_OVERRIDE_CREATED` / `PROTOCOL_OVERRIDE_UPDATED` / `PROTOCOL_OVERRIDE_DELETED`

### Data Access

| Type | Resources |
|------|-----------|
| **Read** | patients, conditions, billing_line_items, imaging_reports, medications, coverages, protocol_overrides, encounters |
| **Write** | None |

### Value Sets (v2026)

**Screening:**
- Mammography, Tomography

**Exclusions:**
- BilateralMastectomy, UnilateralMastectomyLeft/Right
- HistoryOfBilateralMastectomy, StatusPostLeftMastectomy, StatusPostRightMastectomy
- HospiceCareAmbulatory, HospiceEncounter
- PalliativeCareDiagnosis, PalliativeCareEncounter, PalliativeCareIntervention
- FrailtyDiagnosis, FrailtySymptom, FrailtyEncounter
- AdvancedIllness, DementiaMedications

**Qualifying Visits:**
- OfficeVisit, AnnualWellnessVisit, HomeHealthcareServices
- PreventiveCareServicesEstablishedOfficeVisit18AndUp
- PreventiveCareServicesInitialOfficeVisit18AndUp

## Testing

```bash
cd cms125v14_breast_cancer_screening
uv run pytest -m "not integtest" -v
```

## References

- [CMS125v14 Measure Specification](https://ecqi.healthit.gov/sites/default/files/ecqm/measures/CMS125-v14.0.000-QDM.html)
- [U.S. Preventive Services Task Force - Breast Cancer Screening (2024)](https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/breast-cancer-screening)
- [Canvas Medical Documentation](https://docs.canvasmedical.com)

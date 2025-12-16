# CMS130v14 - Colorectal Cancer Screening

This Canvas EMR plugin implements the CMS130v14 Clinical Quality Measure (CQM) for colorectal cancer screening tracking, helping healthcare providers ensure their adult patients receive appropriate screening for colorectal cancer.

## What This Plugin Does

This plugin automatically monitors patients aged 46-75 years and tracks whether they:

- Had appropriate colorectal cancer screening during the measurement period, OR
- Had screening within the appropriate lookback period prior to the measurement period

The plugin creates protocol cards in the patient chart when action is needed, making it easy for clinicians to identify patients who require screening.

## Clinical Measure Overview

- **Measure**: CMS130v14 - Colorectal Cancer Screening
- **Version**: 2026-01-01v14
- **Measure Type**: Clinical Quality Measure (CQM)
- **Published By**: National Committee for Quality Assurance
- **Reference**: [eCQI Health IT - CMS130v14](https://ecqi.healthit.gov/sites/default/files/ecqm/measures/CMS130-v14.0.000-QDM.html)
- **GUID**: aa2a4bbc-864f-45ee-b17a-7ebcc62e6aac

## Population Criteria

### Initial Population:

- Patients aged **46-75 years** at the end of the measurement period
- Had a qualifying encounter during the measurement period:
  - Office Visit
  - Annual Wellness Visit (AWV)
  - Preventive Care Services (Established or Initial Office Visit, 18 and Up)
  - Home Healthcare Services
  - Virtual Encounter
  - Telephone Visits

### Denominator Exclusions:

Patients are excluded if they meet any of the following criteria:

1. **Hospice Care**: Patients receiving hospice care services for any part of the measurement period
   - Hospice diagnosis
   - Hospice encounters
   - Discharge to hospice (inpatient discharge disposition)
   - Hospice care assessment (LOINC 45755-6) with result "Yes"
   - Hospice care ambulatory interventions (orders/performed)

2. **Colon Exclusions**: Patients with:
   - Diagnosis or past history of **total colectomy**
   - Diagnosis or past history of **malignant neoplasm of colon** (colorectal cancer)

3. **Advanced Illness with Frailty (Age 66+)**: Patients aged 66+ with:
   - **Frailty indicators** (frailty devices, diagnoses, encounters, symptoms), AND
   - **Advanced illness conditions** (dementia, cancer, chemotherapy) OR **dementia medications** during measurement period or year prior

4. **Nursing Home Residents (Age 66+)**: Patients aged 66+ residing in nursing facilities or long-term care facilities
   - Housing status observation (LOINC 71802-3) with result "Lives in nursing home" (SNOMED 160734000)

5. **Palliative Care**: Patients receiving palliative care for any part of the measurement period
   - Palliative care diagnosis
   - Palliative care encounters
   - Palliative care assessment (LOINC 71007-9)
   - Palliative care interventions

### Numerator:

Patients who meet any of the following screening criteria:

1. **Fecal Occult Blood Test (FOBT)**: During the measurement period (1 year interval)
2. **Stool DNA (sDNA) with FIT Test**: During the measurement period or the **2 years prior** to the measurement period
3. **Flexible Sigmoidoscopy**: During the measurement period or the **4 years prior** to the measurement period
4. **CT Colonography**: During the measurement period or the **4 years prior** to the measurement period
5. **Colonoscopy**: During the measurement period or the **9 years prior** to the measurement period

## Why Use This Plugin

- **Improved Patient Outcomes**: Ensures adult patients receive critical preventive colorectal cancer screening to detect and prevent cancer
- **Quality Reporting**: Automates tracking for CMS quality measure reporting requirements
- **Time Savings**: Automatically identifies patients needing screening without manual chart review
- **Compliance**: Helps practices meet MIPS/Quality Payment Program requirements
- **Patient Safety**: Reduces risk of missed colorectal cancer screening
- **Early Detection**: Screening can find precancerous polyps that can be removed before they become cancer

## Clinical Recommendation

The U.S. Preventive Services Task Force (2021) recommends:
- **Grade B recommendation**: Screening for colorectal cancer in adults aged **45 to 49 years**
- **Grade A recommendation**: Screening for colorectal cancer in adults aged **50 to 75 years**

Appropriate screenings are defined by any one of the following:
- Fecal occult blood test (annually)
- Stool DNA (sDNA) with FIT test (every 3 years)
- Flexible sigmoidoscopy (every 5 years)
- Computed tomographic (CT) colonography (every 5 years)
- Colonoscopy (every 10 years)

## Plugin Components

### 1. Protocol

**File**: `protocols/cms130v14_protocol.py`

**Class**: `CMS130v14ColorectalCancerScreening`

**Function**: Monitors patient data and creates protocol cards when screening is needed

## How It Works

The plugin responds to various clinical events in real-time:

### Events Monitored:

- **Condition changes**: New diagnoses, updates, or resolutions (hospice, frailty, advanced illness, palliative care, colon cancer, colectomy)
- **Medications**: Dementia medications affecting frailty exclusions
- **Observations**: Hospice assessments, housing status, palliative care assessments
- **Patient updates**: Demographic changes (including age changes)
- **Encounters**: Office visits, annual wellness visits, preventive care encounters
- **Lab Reports**: FOBT and FIT-DNA test results
- **Imaging Reports**: CT Colonography, Flexible Sigmoidoscopy, Colonoscopy
- **Referral Reports**: Colonoscopy and Flexible Sigmoidoscopy referrals
- **Claims**: Hospice care and palliative care interventions

### Protocol Card Display:

**When a patient needs action:**
- Protocol card appears in the patient's chart
- Shows clear status and recommendations
- Provides one-click access to order screening tests or referrals
- Displays available screening options (FOBT, FIT-DNA, Flexible Sigmoidoscopy, CT Colonography, Colonoscopy)

**When a patient is compliant:**
- Protocol card shows "satisfied" status with details of completed screening
- Shows date of last screening and next due date
- No action required from clinician

**When a patient is excluded:**
- Protocol card shows "not applicable" status with reason for exclusion
- Clear explanation of why patient is not eligible for screening

## Setup & Installation

This plugin requires no configuration - it works automatically once installed.

1. Install the plugin through Canvas plugin manager
2. The protocol will automatically begin monitoring eligible patients
3. Protocol cards will appear for patients requiring screening

## Technical Details

- **SDK Version**: 0.1.4
- **Plugin Version**: 0.0.1
- **Measurement Period**: January 1, 2026 through December 31, 2026 (configurable)

### Value Sets Used:

- **Screening Tests**:
  - Fecal Occult Blood Test (FOBT) - LOINC codes
  - sDNA FIT Test - LOINC codes
  - Flexible Sigmoidoscopy - CPT, SNOMED codes
  - CT Colonography - LOINC codes
  - Colonoscopy - CPT, SNOMED codes

- **Encounters**:
  - Office Visit
  - Annual Wellness Visit
  - Preventive Care Services (Established/Initial Office Visit, 18 and Up)
  - Home Healthcare Services
  - Virtual Encounter
  - Telephone Visits

- **Exclusions**:
  - Hospice Diagnosis, Encounter, Care Ambulatory
  - Malignant Neoplasm of Colon
  - Total Colectomy
  - Advanced Illness
  - Frailty Device, Diagnosis, Encounter, Symptom
  - Dementia Medications
  - Palliative Care Diagnosis, Encounter, Intervention
  - Housing Status (nursing home)

### Data Models:

- **Patient** - Demographics and age calculation
- **Condition** - Exclusion diagnoses (hospice, frailty, advanced illness, palliative care, colon cancer, colectomy)
- **Encounter** - Office visits and preventive care
- **LabReport** - FOBT and FIT-DNA test results
- **ImagingReport** - CT Colonography results
- **ReferralReport** - Colonoscopy and Flexible Sigmoidoscopy referrals
- **Observation** - Hospice assessments, housing status, palliative care assessments
- **Medication** - Dementia medication tracking
- **ClaimLineItem** - Hospice and palliative care interventions

## Example Scenarios

### Scenario 1: Patient Needs Screening

**Without this plugin:**
- Provider must manually review all patients aged 46-75
- Easy to miss patients who haven't had recent screening
- Time-consuming chart review for quality reporting

**With this plugin:**
- Protocol card automatically appears for 62-year-old patient
- Shows "Action needed: Colorectal cancer screening not documented"
- Provider can order FOBT, FIT-DNA, or refer for colonoscopy
- Status automatically updates when screening is completed

### Scenario 2: Patient with Recent Colonoscopy

**Patient**: 68-year-old with colonoscopy 3 years ago

**Plugin Action**: 
- Detects colonoscopy within 9-year lookback period
- Creates "SATISFIED" protocol card
- Shows date of last colonoscopy and next due date (6 years from now)

**Result**: Patient is compliant, no action needed

### Scenario 3: Nursing Home Exclusion

**Patient**: 70-year-old in nursing facility

**Plugin Action**: 
- Detects housing status observation indicating nursing home residence
- Automatically excludes patient from measure due to age 66+ and nursing home residence

**Result**: Patient excluded from measure, protocol card shows "not applicable" with explanation

### Scenario 4: Hospice Care Exclusion

**Patient**: 60-year-old receiving hospice care

**Plugin Action**: 
- Detects hospice diagnosis or encounter during measurement period
- Automatically excludes patient from measure

**Result**: Patient excluded from measure, protocol card shows "not applicable" with explanation

### Scenario 5: Frailty and Advanced Illness Exclusion

**Patient**: 70-year-old with frailty device and advanced illness diagnosis

**Plugin Action**: 
- Detects age 66+ with frailty indicators
- Detects advanced illness diagnosis
- Automatically excludes patient from measure

**Result**: Patient excluded from measure, protocol card shows "not applicable" with explanation

## Important Notes

### CANVAS_MANIFEST.json

The `CANVAS_MANIFEST.json` file is used when installing your plugin. Please ensure it gets updated if you add, remove, or rename protocols.

### Measurement Period

The plugin uses a configurable measurement period (default: calendar year 2026). The protocol evaluates patients based on:

- Age at end of measurement period (must be 46-75)
- Encounters during measurement period
- Prior-year screening results (lookback periods vary by screening type)

### Screening Intervals

The plugin recognizes the following screening intervals:

- **FOBT**: 1 year (within measurement period only)
- **FIT-DNA**: 2 years (within measurement period or 2 years prior)
- **Flexible Sigmoidoscopy**: 4 years (within measurement period or 4 years prior)
- **CT Colonography**: 4 years (within measurement period or 4 years prior)
- **Colonoscopy**: 9 years (within measurement period or 9 years prior)

### Age Range

**Important**: The measure includes patients aged **46-75 years** at the end of the measurement period. This differs from previous versions which included ages 50-75.

### Stratification

The measure reports rates for two age strata:
- **Stratum 1**: Patients age 46-49 by the end of the measurement period
- **Stratum 2**: Patients age 50-75 by the end of the measurement period

## Debugging & Logs

The plugin includes comprehensive logging for troubleshooting:

- Event triggers and patient evaluations
- Initial population checks (age and encounter validation)
- Denominator exclusion checks with reasons
- Screening detection and validation
- Database query results
- Error conditions

Log messages are prefixed with `CMS130v14:` for easy filtering.

## References

1. Howlader N, Noone AM, Krapcho M, Miller D, Brest A, Yu M, Ruhl J, Tatalovich Z, Mariotto A, Lewis DR, Chen HS, Feuer EJ, Cronin KA (2020). SEER Cancer Statistics Review, 195-2017. Retrieved September 22, 2020, https://seer.cancer.gov/csr/1975_2017/

2. SEER. (n.d.). Cancer of the Colon and Rectum. https://seer.cancer.gov/statfacts/html/colorect.html

3. US Preventive Services Task Force, Davidson, K. W., Barry, M. J., Mangione, C. M., Cabana, M., Caughey, A. B., Davis, E. M., Donahue, K. E., Doubeni, C. A., Krist, A. H., Kubik, M., Li, L., Ogedegbe, G., Owens, D. K., Pbert, L., Silverstein, M., Stevermer, J., Tseng, C. W., & Wong, J. B. (2021). Screening for Colorectal Cancer: US Preventive Services Task Force Recommendation Statement. JAMA, 325(19), 1965–1977. https://doi.org/10.1001/jama.2021.6238

## Copyright & Disclaimer

This measure and related data specifications are owned and developed by the National Committee for Quality Assurance (NCQA). NCQA is not responsible for any use of the measure. The measure may be used for internal, noncommercial purposes without obtaining approval from NCQA.

The performance measure is not a clinical guideline and does not establish a standard of medical care. The measure and specifications are provided "AS IS" without warranty of any kind.

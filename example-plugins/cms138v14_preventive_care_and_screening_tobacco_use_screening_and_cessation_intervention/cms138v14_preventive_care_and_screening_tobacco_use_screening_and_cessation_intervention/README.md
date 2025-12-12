# CMS138v14 - Preventive Care and Screening: Tobacco Use Screening and Cessation Intervention

This Canvas EMR plugin implements the CMS138v14 Clinical Quality Measure (CQM) for tobacco use screening and cessation intervention tracking, helping healthcare providers ensure their patients receive appropriate tobacco screening and cessation support.

## What This Plugin Does

This plugin automatically monitors patients aged 12 years and older and tracks whether they:

1. **Were screened for tobacco use** during the measurement period, AND
2. **Received cessation intervention** (counseling or pharmacotherapy) if identified as a tobacco user

The plugin creates protocol cards in the patient chart when action is needed, making it easy for clinicians to identify patients who require tobacco screening or cessation interventions.

## Clinical Measure Overview

**Measure:** CMS138v14 - Preventive Care and Screening: Tobacco Use Screening and Cessation Intervention
**Version:** v14.0.0
**Measure Type:** Clinical Quality Measure (CQM)
**Published By:** National Committee for Quality Assurance
**Reference:** [eCQI Health IT - CMS138v14](https://ecqi.healthit.gov/ecqm/ec/2026/cms0138v14)

### Population Criteria

**Initial Population:**
- Patients aged 12 years and older at the start of the measurement period
- Had qualifying encounters during the measurement period:
  - 2 or more qualifying visits (office visits, telehealth, therapy evaluations, etc.), OR
  - 1 or more preventive care visits (annual wellness, preventive care services)

**Denominator Exclusions:**

Patients are excluded if they meet any of the following criteria:

1. **Hospice Care:** Patients receiving hospice care services during the measurement period, including:
   - Hospice encounter or diagnosis
   - Hospice care assessment with "Yes" result
   - Discharge to hospice from inpatient encounter
   - Hospice care ambulatory order or intervention

**Three Population Rates:**

This measure tracks three separate rates per CMS specification:

| Population | Description | Numerator Criteria |
|------------|-------------|-------------------|
| Population 1 | Screening Rate | Patient was screened for tobacco use |
| Population 2 | Intervention Rate | Tobacco users who received cessation intervention |
| Population 3 | Overall Rate (MIPS) | Screened AND received intervention if user |

**Numerator:**

Patients who meet any of the following:
- Screened as tobacco non-user during the measurement period, OR
- Screened as tobacco user AND received cessation intervention (counseling or pharmacotherapy) within 6 months prior to or during the measurement period

### Cessation Interventions

For tobacco users, one of the following must be documented within the 6-month lookback period:

**Counseling:**
- Tobacco use cessation counseling instruction (SNOMED codes)
- Cessation counseling CPT codes (99406, 99407)
- Z71.6 ICD-10 diagnosis (Tobacco abuse counseling)

**Pharmacotherapy:**
- Tobacco cessation medications (e.g., varenicline, bupropion, nicotine replacement)

## Why Use This Plugin

- **Improved Patient Outcomes:** Ensures patients receive tobacco screening and cessation support to reduce tobacco-related health risks
- **Quality Reporting:** Automates tracking for CMS quality measure reporting requirements
- **Time Savings:** Automatically identifies patients needing screening or intervention without manual chart review
- **Compliance:** Helps practices meet MIPS/Quality Payment Program requirements
- **Preventive Care:** Supports population health by systematically addressing tobacco use

## Plugin Components

### 1. Protocol
- **File:** `protocols/cms138v14_protocol.py`
- **Class:** `CMS138v14TobaccoScreening`
- **Function:** Monitors patient data and creates protocol cards when tobacco screening or intervention is needed

### 2. Questionnaires

The plugin works with tobacco use screening questionnaires that capture:
- Current tobacco use status
- Type of tobacco products used
- Frequency of use
- Previous quit attempts

## How It Works

The plugin responds to various clinical events in real-time:

### Events Monitored:
- **Patient changes:** New patients, demographic updates
- **Condition changes:** New diagnoses, condition updates
- **Interviews/Questionnaires:** Tobacco screening questionnaire completions
- **Encounters:** Office visits, preventive care encounters
- **Medications:** Cessation medication orders and active prescriptions
- **Instructions:** Cessation counseling documentation

### Protocol Card Display:

**When a patient needs screening:**
- Protocol card appears showing "Due" status
- Displays recommendation to complete tobacco use questionnaire
- One-click access to start the questionnaire

**When a tobacco user needs intervention:**
- Protocol card shows intervention is needed
- Provides options to document counseling or prescribe cessation medication
- Shows screening date and tobacco use status

**When a patient is compliant:**
- Protocol card shows "Satisfied" status
- Displays screening date and result
- Shows intervention date if applicable (for tobacco users)

**When a patient is excluded:**
- Protocol card shows "Not Applicable" status
- Displays reason for exclusion (e.g., hospice care, age, insufficient visits)

## Setup & Installation

This plugin requires no configuration - it works automatically once installed.

1. Install the plugin through Canvas plugin manager
2. The protocol will automatically begin monitoring eligible patients
3. Protocol cards will appear for patients requiring tobacco screening
4. Questionnaire recommendations will guide clinical workflow

## Technical Details

**SDK Version:** 0.1.4
**Plugin Version:** 1.0.0

**Value Sets Used:**
- Tobacco Use Screening assessment codes
- Tobacco User status codes (SNOMED)
- Tobacco Non-User status codes (SNOMED)
- Tobacco Use Cessation Counseling codes (CPT, SNOMED)
- Tobacco Use Cessation Pharmacotherapy medications
- Office Visit encounter codes
- Preventive Care Services codes
- Annual Wellness Visit codes
- Hospice care codes (various types)
- Telehealth and virtual encounter codes

**Data Models:**
- `Patient` - Demographics and age calculation
- `Condition` - Z71.6 tobacco counseling diagnosis, hospice diagnoses
- `Encounter` - Office visits and preventive care
- `ClaimLineItem` - Claims-based encounters and procedures
- `Medication` - Cessation medication tracking
- `Instruction` - Cessation counseling documentation
- `Observation` - Tobacco screening observations
- `Interview/InterviewQuestionResponse` - Questionnaire responses

## Example Scenarios

### Scenario 1: Patient Needs Tobacco Screening
**Patient:** 35-year-old with two office visits this year, no tobacco screening documented
**Plugin Action:** Protocol card appears showing "Due" status with questionnaire recommendation
**Result:** Provider completes tobacco use questionnaire; patient identified as non-user; card shows "Satisfied"

### Scenario 2: Tobacco User Needs Intervention
**Patient:** 52-year-old screened as tobacco user, no cessation intervention documented
**Plugin Action:** Protocol card shows "Due" with options for counseling or medication
**Result:** Provider documents cessation counseling; card updates to "Satisfied"

### Scenario 3: Tobacco User with Pharmacotherapy
**Patient:** 45-year-old tobacco user with active varenicline prescription
**Plugin Action:** Protocol automatically detects cessation medication
**Result:** Protocol card shows "Satisfied" with screening and intervention dates

### Scenario 4: Hospice Care Exclusion
**Patient:** 68-year-old with hospice encounter documented
**Plugin Action:** Automatically excludes patient from measure
**Result:** Protocol card shows "Not Applicable" with hospice exclusion reason

### Scenario 5: Insufficient Visits
**Patient:** 25-year-old with only one office visit (needs 2+ qualifying OR 1+ preventive)
**Plugin Action:** Patient doesn't meet encounter requirements
**Result:** Protocol card shows "Not Applicable" - insufficient qualifying visits

## Important Notes

### CANVAS_MANIFEST.json
The CANVAS_MANIFEST.json file is used when installing your plugin. Please ensure it gets updated if you add, remove, or rename protocols or questionnaires.

### Measurement Period
The plugin uses a configurable measurement period (default: calendar year). The protocol evaluates patients based on:
- Age at START of measurement period (must be 12+)
- Encounters during measurement period
- Screening during measurement period
- Interventions within 6 months prior to OR during measurement period

### Debugging & Logs
The plugin includes comprehensive logging for troubleshooting:
- Event triggers and patient evaluations
- Population membership (initial, denominator, numerator)
- Exclusion criteria checks with reasons
- Screening and intervention detection
- Database query results
- Error conditions

---

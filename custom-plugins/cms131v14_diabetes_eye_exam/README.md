# CMS131v14 - Diabetes: Eye Exam

This Canvas EMR plugin implements the CMS131v14 Clinical Quality Measure (CQM) for diabetes eye exam tracking, helping healthcare providers ensure their diabetic patients receive appropriate retinal or dilated eye exams.

## What This Plugin Does

This plugin automatically monitors patients with diabetes (ages 18-75) and tracks whether they:

1. **Had a retinal or dilated eye exam** during the measurement period, OR
2. **Had a negative retinal exam** (no evidence of retinopathy) in the 12 months prior to the measurement period

The plugin creates protocol cards in the patient chart when action is needed, making it easy for clinicians to identify patients who require eye exams.

## Clinical Measure Overview

**Measure:** CMS131v14 - Diabetes: Eye Exam  
**Version:** 2025-05-08v14  
**Measure Type:** Clinical Quality Measure (CQM)  
**Published By:** National Committee for Quality Assurance  
**Reference:** [eCQI Health IT - CMS131v14](https://ecqi.healthit.gov/ecqm/ec/2026/cms0131v14)

### Population Criteria

**Initial Population:**
- Patients aged 18-75 years at the end of the measurement period
- Active diagnosis of diabetes during the measurement period
- Had a qualifying office visit, annual wellness visit (AWV), or preventive care encounter during the measurement period

**Denominator Exclusions:**

Patients are excluded if they meet any of the following criteria:

1. **Hospice Care:** Patients receiving hospice care services during the measurement period
2. **Palliative Care:** Patients receiving palliative care during the measurement period
3. **Advanced Illness with Frailty (Age 66+):** Patients aged 66+ with:
   - Frailty indicators (e.g., frailty device), AND
   - Advanced illness conditions (dementia, cancer, chemotherapy) OR dementia medications during measurement period or year prior
4. **Nursing Home Residents (Age 66+):** Patients aged 66+ residing in nursing facilities or long-term care facilities
5. **Bilateral Eye Absence:** Patients with documented bilateral absence of eyes (SNOMED code: 15665641000119103)

**Numerator:**

Patients who meet any of the following:
- Retinal or dilated eye exam by an eye care professional during the measurement period
- Negative retinal exam (no diabetic retinopathy) in the 12 months prior to the measurement period
- Diabetic retinopathy severity level documented during the measurement period
- Automated AI screening for diabetic retinopathy during the measurement period (coming soon)

## Why Use This Plugin

- **Improved Patient Outcomes:** Ensures diabetic patients receive critical preventive eye care to detect and prevent vision loss
- **Quality Reporting:** Automates tracking for CMS quality measure reporting requirements
- **Time Savings:** Automatically identifies patients needing eye exams without manual chart review
- **Compliance:** Helps practices meet MIPS/Quality Payment Program requirements
- **Patient Safety:** Reduces risk of missed diabetic retinopathy screening

## Plugin Components

### 1. Protocol
- **File:** `protocols/cms131v14_protocol.py`
- **Class:** `CMS131v14DiabetesEyeExam`
- **Function:** Monitors patient data and creates protocol cards when eye exams are needed

### 2. Questionnaires

The plugin includes two structured questionnaires for comprehensive tracking:

#### Hospice & Frailty Questionnaire (`hospice_and_frailty.yml`)
- **Purpose:** Captures hospice care enrollment and frailty indicators
- **Sections:**
  - Hospice care status with SNOMED codes (e.g., 385763009: Hospice care)
  - Frailty indicators (e.g., 105501005: Frailty device)
- **Usage:** Complete when assessing patient for denominator exclusions

#### Hospice & Palliative Care Questionnaire (`hospice_and_palliative.yml`)
- **Purpose:** Documents palliative care services
- **Usage:** Track palliative care encounters and assessments

These questionnaires are automatically included when the plugin is installed and appear in the clinical workflow for data capture.

## How It Works

The plugin responds to various clinical events in real-time:

### Events Monitored:
- **Condition changes:** New diabetes diagnoses, updates, or resolutions
- **Medications:** Dementia medications affecting frailty exclusions
- **Interviews/Questionnaires:** Hospice and frailty questionnaire completions
- **Patient updates:** Demographic changes (including age changes)
- **Encounters:** Office visits, annual wellness visits
- **Claims:** Nursing home visits, palliative care services

### Protocol Card Display:

**When a patient needs action:**
- Protocol card appears in the patient's chart
- Shows clear status and recommendations
- Provides one-click access to document the eye exam or exclusion criteria

**When a patient is compliant:**
- Protocol card shows "satisfied" status with details of completed exam
- No action required from clinician

## Setup & Installation

This plugin requires no configuration - it works automatically once installed.

1. Install the plugin through Canvas plugin manager
2. The protocol will automatically begin monitoring eligible patients
3. Questionnaires will be available in the clinical workflow
4. Protocol cards will appear for patients requiring eye exams

## Technical Details

**SDK Version:** 0.1.4  
**Plugin Version:** 1.0.0  

**Value Sets Used:**
- Diabetes value sets (ICD-10 codes)
- Office Visit encounters (CPT codes)
- Annual Wellness Visits (AWV)
- Eye care exam codes (CPT, HCPCS)
- Hospice care codes (SNOMED)
- Palliative care encounter codes
- Frailty indicators
- Advanced illness conditions
- Dementia medications
- Nursing facility visit codes

**Data Models:**
- `Patient` - Demographics and age calculation
- `Condition` - Diabetes and exclusion diagnoses
- `Encounter` - Office visits and preventive care
- `ClaimLineItem` - Claims-based encounters
- `Medication` - Dementia medication tracking
- `Interview` - Questionnaire responses
- `ReferralReport` - Eye care specialist referrals

## Example Scenarios

### Scenario 1: Patient Needs Eye Exam
**Without this plugin:**
- Provider must manually review all diabetic patients
- Easy to miss patients who haven't had recent eye exams
- Time-consuming chart review for quality reporting

**With this plugin:**
- Protocol card automatically appears for 62-year-old diabetic patient
- Shows "Action needed: Eye exam not documented in past year"
- Provider can document exam or refer to ophthalmology
- Status automatically updates when exam is completed

### Scenario 2: Nursing Home Exclusion
**Patient:** 70-year-old diabetic in nursing facility  
**Plugin Action:** Automatically excludes patient from measure due to age 66+ and nursing home residence  
**Result:** No protocol card shown, appropriate exclusion applied

### Scenario 3: Palliative Care Exclusion
**Patient:** 55-year-old diabetic receiving palliative care  
**Plugin Action:** Questionnaire completed documenting palliative care services  
**Result:** Patient excluded from measure, protocol card removed

## Important Notes

### CANVAS_MANIFEST.json
The CANVAS_MANIFEST.json file is used when installing your plugin. Please ensure it gets updated if you add, remove, or rename protocols or questionnaires.

### Measurement Period
The plugin uses a configurable measurement period (default: calendar year). The protocol evaluates patients based on:
- Age at end of measurement period
- Encounters during measurement period
- Prior-year exam results (12 months before measurement period start)

### Debugging & Logs
The plugin includes comprehensive logging for troubleshooting:
- Event triggers and patient evaluations
- Exclusion criteria checks with reasons
- Database query results
- Error conditions

---

# PDMP Bamboo Plugin

## Description

A comprehensive Canvas plugin that combines data extraction from Canvas EMR with PDMP requests to BambooHealth PMP Gateway. This unified plugin provides a single "PDMP Request" button in note headers that automatically extracts patient, practitioner, and organization data from Canvas and sends it to the PDMP Gateway for prescription monitoring reports.

## Features

- **Three Button Workflow Options**:
  - **PDMP Request (Prod)**: Production environment with Canvas data extraction and certificate authentication
  - **PDMP Request (Test)**: Test environment with Canvas data extraction and standard authentication
  - **PDMP Request (Mock)**: Mock testing with static template data for plugin functionality verification
- **Canvas Data Integration**: Automatically extracts patient, practitioner, and organization data from Canvas EMR
- **PDMP XML Mapping**: Maps Canvas data to BambooHealth PDMP XML template format
- **Mock Data Testing**: Uses static XML template for testing plugin functionality without real patient data
- **Environment-Aware Authentication**: Supports both production (with certificates) and test environments
- **Comprehensive Error Handling**: Simple HTML error display for missing data and API errors
- **Rich Response Display**: Parses and displays NarxCare scores, clinical alerts, and full PDMP reports
- **Configurable Authentication**: Custom authentication headers for BambooHealth PMP Gateway
- **Automatic Documentation**: Creates structured assessment in patient note documenting PDMP check with date and practitioner

## Installation

1. Ensure the plugin is properly configured in your Canvas environment
2. Set up the required secrets (see Configuration section)
3. For production environment, place client certificates in the `certs/` directory
4. The plugin will automatically add the "PDMP Request" button to note headers

## Configuration

### Required Secrets

Configure the following secrets in your Canvas plugin configuration:

**Individual Secrets (Recommended):**
- **PDMP_API_URL**: The BambooHealth PMP Gateway base URL (Required)
- **PDMP_API_USERNAME**: Username for PMP Gateway authentication (Required)  
- **PDMP_API_PASSWORD**: Password for PMP Gateway authentication (Required)
- **TEST_PDMP_API_URL**: Test environment PMP Gateway base URL (Required for test/mock requests)
- **TEST_PDMP_API_USERNAME**: Test environment username (Required for test/mock requests)
- **TEST_PDMP_API_PASSWORD**: Test environment password (Required for test/mock requests)

**Consolidated Secrets (Alternative):**
- **all_secrets**: JSON object containing all secrets as key-value pairs (Fallback option)

**Direct JSON Secrets (Also Supported):**
- All secrets provided as a single JSON object with individual secret keys (e.g., `{"PDMP_API_URL": "...", "PDMP_API_USERNAME": "...", ...}`)

### Example Configuration

**Individual Secrets:**
```
PDMP_API_URL: https://prep.pmpgateway.net
PDMP_API_USERNAME: your_username
PDMP_API_PASSWORD: your_password
TEST_PDMP_API_URL: https://test.pmpgateway.net
TEST_PDMP_API_USERNAME: test_username
TEST_PDMP_API_PASSWORD: test_password
```

**Consolidated Secrets (for easier testing):**
```
all_secrets: {
  "PDMP_API_URL": "https://prep.pmpgateway.net",
  "PDMP_API_USERNAME": "your_username",
  "PDMP_API_PASSWORD": "your_password",
  "TEST_PDMP_API_URL": "https://test.pmpgateway.net",
  "TEST_PDMP_API_USERNAME": "test_username",
  "TEST_PDMP_API_PASSWORD": "test_password"
}
```

**Direct JSON Secrets (your current structure):**
```
{
  "PDMP_API_URL": "https://prep.pmpgateway.net",
  "PDMP_API_USERNAME": "your_username",
  "PDMP_API_PASSWORD": "your_password",
  "TEST_PDMP_API_URL": "https://test.pmpgateway.net",
  "TEST_PDMP_API_USERNAME": "test_username",
  "TEST_PDMP_API_PASSWORD": "test_password"
}
```

**Note**: The plugin automatically appends `/v5_1/patient` to the base URL.

### Certificate Setup (Production Only)

For production environment (`PDMP_ENVIRONMENT = "production"`):

1. **Place certificates** in the `certs/` directory:
   - `client.crt` - Your client certificate
   - `client.key` - Your private key

2. **Certificate requirements**:
   - Must be signed by BambooHealth's trusted CA
   - Private key should be password-less for Canvas compatibility
   - Certificates must be valid and not expired

## Usage

1. **Open a Note**: Navigate to any patient note in Canvas
2. **Choose Button Type**: Look for one of three PDMP Request buttons in the note header:
   - **PDMP Request (Prod)**: For production PDMP requests with real patient data
   - **PDMP Request (Test)**: For test environment requests with real patient data
   - **PDMP Request (Mock)**: For testing plugin functionality using mock template data
3. **Automatic Processing** (for Prod/Test buttons): The plugin will:
   - Extract patient, practitioner, and organization data from Canvas
   - Validate required fields and show warnings for missing data
   - Create PDMP XML request with Canvas data
   - Send request to BambooHealth PMP Gateway
   - Create structured assessment documenting the PDMP check (if successful)
   - Parse and display the response in a modal
4. **Mock Testing** (for Mock button): The plugin will:
   - Use static XML template with mock patient data (Bob Dylan Testpatient)
   - Send request to test environment without extracting real Canvas data
   - Display mock data information in the response
   - Still create structured assessment for documentation
5. **View Results**: Review NarxCare scores, clinical alerts, and full PDMP report
6. **Note Documentation**: A structured assessment is automatically added to the note with "PDMP checked by" and "Date checked" fields

## Data Requirements

The plugin extracts and validates the following Canvas data:

### Patient Data (Required)
- First Name, Last Name, Date of Birth, Sex
- Address (street, city, state, zip code)
- Phone number, SSN, Medical Record Number

### Practitioner Data (Required)
- First Name, Last Name
- NPI Number and/or DEA Number (at least one required)
- Role/Title

### Organization Data (Required)
- Organization name
- Group NPI Number and/or Practice Location NPI
- Practice location information

## Error Handling

The plugin provides comprehensive error handling with simple HTML displays:

- **Missing Data Errors**: Lists specific Canvas fields that are missing or incomplete
- **Configuration Errors**: Indicates missing secrets or invalid URLs
- **Authentication Errors**: Shows authentication failures with BambooHealth
- **API Request Errors**: Displays PDMP Gateway response errors with troubleshooting tips
- **Validation Warnings**: Shows data extraction warnings but still attempts PDMP request

All errors are displayed in consistent, user-friendly HTML modals with specific guidance for resolution.

## File Structure

```
pdmp_bamboo/
├── CANVAS_MANIFEST.json          # Plugin configuration
├── protocols/
│   └── my_protocol.py            # Main PDMP request protocol
├── utils/
│   ├── data_extractor.py         # Canvas data extraction utilities
│   ├── xml_mapper.py             # PDMP XML template mapping
│   ├── xml_request.py            # HTTP request and authentication
│   ├── pdmp_parser.py            # PDMP response parsing
│   ├── error_html.py             # Simple HTML error display
│   └── template_reader.py        # XML template reader for mock requests
├── templates/
│   ├── pdmp_check_questionnaire.yml  # Structured assessment questionnaire
│   └── patient-request.xml       # Mock PDMP XML template for testing
├── certs/
│   └── README.md                 # Certificate setup instructions
└── README.md                     # This file
```

## Development and Customization

The plugin is designed with modular utilities:

- **DataExtractor**: Handles Canvas SDK data extraction and validation
- **PDMPXMLMapper**: Maps Canvas data to PDMP XML template format
- **XMLRequest**: Manages HTTP requests and BambooHealth authentication
- **PDMPParser**: Parses PDMP XML responses for display
- **ErrorHTML**: Creates simple, consistent error displays
- **TemplateReader**: Reads XML templates for mock testing requests

### Adding New Data Sources

To extract additional Canvas data:
1. Update `DataExtractor` methods with new field extraction
2. Modify `PDMPXMLMapper` to include new fields in XML template
3. Update validation logic to check for new required fields

### Customizing XML Template

To modify the PDMP XML template:
1. Update `PDMPXMLMapper.create_pdmp_xml()` method
2. Adjust hardcoded values in `PDMPXMLMapper.HARDCODED_VALUES`
3. See "Questions for Product Review" section below for configuration options

## Questions for Product Review

### Template Customization
The following values are currently hardcoded but could be made configurable:

**Software Information:**
- `<Developer>Canvas Medical</Developer>`
- `<Product>Canvas EMR</Product>`
- `<Version>1.0.0</Version>`

**Should these be:**
- Hardcoded defaults as they are now?
- Configurable via plugin secrets?
- Dynamic based on Canvas instance information?

**Default Values:**
- `<Pmp>KS</Pmp>` (PMP destination - currently Kansas)
- Date range: 2022-01-01 to 2024-12-31 (currently 2-year span)
- NCPDP Number: 1234567 (default pharmacy identifier)

**Questions:**
- What PMP destinations should be supported? How should this be determined?
- What date range should be used for prescription history requests?
- How should NCPDP numbers be handled for different practice locations?
- Should address information be extracted from Canvas practice locations or use defaults?

**Professional License Handling:**
- Currently using NPI as professional license number
- Should we extract actual license numbers from Canvas if available?
- How should multiple license types be prioritized?

**Request Customization:**
- Should diagnosis codes be extracted from Canvas encounters/assessments?
- Should current/pending prescriptions be included from Canvas medication lists?
- How should veterinary prescriptions be handled?

### Date Range Configuration
**FOLLOW-UP QUESTION**: The working sample uses a 2-year date range, but this should be dynamic:
- **Current implementation**: Now calculates date range dynamically from current date back 2 years (730 days)
- **Questions for review**:
  - Is 2 years the optimal time period for PDMP prescription history?
  - Should this be configurable via plugin secrets (e.g., `PDMP_HISTORY_YEARS`)?
  - Are there regulatory requirements that specify the lookback period?
  - Should different states/PMPs have different date ranges?

### Essential vs Optional Fields
**FOLLOW-UP CLARIFICATION**: Based on the working sample, we're focusing on essential fields only:
- **Required fields**: Patient demographics, practitioner identifiers, location data, date range
- **Optional fields being skipped**: RxCodes, DiagnosisCodes, VeterinaryPrescription, PharmacyBenefitsMemberID
- **Questions**:
  - Should any of the "optional" fields be made configurable for specific use cases?
  - Are there scenarios where diagnosis codes or current prescriptions should be included?

### Data Validation Strategy
- Should the plugin fail if critical data is missing, or proceed with warnings?
- What constitutes "critical" vs "optional" data for PDMP requests?
- Should users be able to manually input missing data before sending requests?
- **NEW**: Enhanced validation now provides specific guidance (❌ CRITICAL, ⚠️ WARNING, ℹ️ INFO)

### Environment Configuration
- Are the current production vs test environment settings sufficient?
- Should there be additional environment-specific configurations?
- How should certificate management be handled in different deployment scenarios?

## Requirements Added by AI

- **requests**: HTTP library for making API requests to BambooHealth PMP Gateway
- **uuid**: For generating unique request identifiers (Python standard library)
- **hashlib**: For creating authentication password digests (Python standard library)
- **time**: For timestamp generation in authentication (Python standard library)
- **re**: For regex parsing of PDMP XML responses (Python standard library)

## Features & Change Log

- **v0.0.13**: Added all_secrets JSON field support for consolidated secret management
- Added secrets helper utility with fallback from individual secrets to all_secrets JSON
- Enhanced configuration flexibility for easier testing and deployment
- Updated all secret access points to use new helper functions
- **v0.0.12**: Added third "PDMP Request (Mock)" button for testing plugin functionality with static template data
- Added `patient-request.xml` template file for mock testing
- Created `TemplateReader` utility for reading XML templates
- Added mock workflow function with static test data display
- Enhanced documentation with three-button workflow options
- **v0.0.11**: Enhanced PDMP request validation and XML template improvements
- **Dynamic Date Range**: Date range now calculated dynamically (current date back 2 years) instead of hardcoded
- **Enhanced Validation**: Improved error messages with specific guidance (❌ CRITICAL, ⚠️ WARNING, ℹ️ INFO)
- **Essential Fields Focus**: Streamlined XML to include only essential fields, skipping optional RxCodes/DiagnosisCodes
- **Better User Guidance**: Clear instructions for fixing missing Canvas data
- **v0.0.11**: Combined extract_relevant_data, bamboo_pdmp, and structured_assessment functionality
- Unified single-button PDMP workflow with Canvas data extraction
- Automatic structured assessment creation for PDMP check documentation
- Function-based architecture (no classes) for Canvas sandbox compliance
- Fixed Canvas sandbox violations (getattr, hasattr, __file__)
- Environment-aware certificate authentication
- Comprehensive error handling and validation
- PDMP response parsing and display
- Configurable authentication for BambooHealth PMP Gateway

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it
gets updated if you add, remove, or rename protocols.

pdmp_bamboo
===========

## Description

A comprehensive **Prescription Drug Monitoring Program (PDMP)** integration plugin for Canvas EMR that provides seamless connectivity to the BambooHealth PMP Gateway. This plugin enables healthcare providers to query prescription drug monitoring databases directly from patient notes, retrieve comprehensive prescription histories, and automatically document PDMP checks through structured assessments.

### Key Features

- **Real-time PDMP Queries**: Query prescription drug monitoring databases for patient prescription histories
- **Clinical Risk Assessment**: Display NarxCare risk scores and clinical alerts for informed decision-making
- **Automated Documentation**: Generate structured assessments to document PDMP checks in patient records
- **Direct Report Access**: One-click access to full HTML reports from the PMP Gateway
- **Multi-Environment Support**: Test and production environment configurations
- **Secure Authentication**: Robust authentication with certificate-based security for production
- **Responsive UI**: Clean, intuitive interface with comprehensive error handling

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it gets updated if you add, remove, or rename protocols.

## Architecture

This plugin implements a **clean, modular architecture** with clear separation of concerns.


## Components

### Protocols

#### PDMPRequestProtocol
- **Class**: `pdmp_bamboo.protocols.my_protocol:PDMPRequestProtocol`
- **Type**: Action Button Protocol
- **Location**: Note Header
- **Description**: Main protocol for initiating PDMP requests from patient notes

**Data Access:**
- **Read**: Patient, Staff, Organization, PracticeLocation, Questionnaire data
- **Write**: StructuredAssessmentCommand for documentation

#### ReportEndpoint
- **Class**: `pdmp_bamboo.api.endpoint.report_endpoint:ReportEndpoint`
- **Type**: Simple API Route
- **Path**: `/plugin-io/api/pdmp_bamboo/report`
- **Description**: RESTful endpoint for retrieving full PDMP reports

### Services

#### PDMPIntegrationService
The main orchestrator that coordinates the entire PDMP workflow:
- Data extraction from Canvas models
- XML generation for PMP Gateway
- API request handling
- Response processing and UI creation

#### DataExtractionService
Handles extraction and validation of Canvas data:
- Patient information extraction
- Practitioner and organization data
- Practice location details
- Comprehensive data validation

#### XMLGenerationService
Manages XML request generation:
- Patient data XML
- Practitioner/provider XML
- Location XML
- Complete PMP Gateway request XML

#### UIService
Creates user interface components:
- Success and error modals
- Assessment effects
- Report buttons
- Clinical data display

#### ResponseParserService
Processes PDMP API responses:
- Clinical risk scores (NarxCare)
- Alert messages
- Report URL extraction
- Data visualization

### Data Models

#### DTOs (Data Transfer Objects)
- **PatientDTO**: Patient demographic and contact information
- **PractitionerDTO**: Provider details including NPI, DEA, and credentials
- **OrganizationDTO**: Healthcare organization information
- **PracticeLocationDTO**: Practice location details with addresses
- **AddressDTO**: Standardized address information

#### Mappers
Specialized mappers for data transformation:
- **PatientMapper**: Canvas Patient → PatientDTO
- **PractitionerMapper**: Canvas Staff → PractitionerDTO
- **OrganizationMapper**: Canvas Organization → OrganizationDTO
- **PracticeLocationMapper**: Canvas PracticeLocation → PracticeLocationDTO

### Validators
Comprehensive validation for data integrity:
- **PatientValidator**: Patient data validation
- **PractitionerValidator**: Provider credential validation
- **OrganizationValidator**: Organization data validation
- **PracticeLocationValidator**: Location data validation

## Configuration

### Required Secrets

The plugin requires the following secrets to be configured:

#### Test Environment
- `TEST_PDMP_API_URL`: BambooHealth test environment URL
- `TEST_PDMP_API_USERNAME`: Test environment username
- `TEST_PDMP_API_PASSWORD`: Test environment password

#### Production Environment (Optional)
- `PDMP_API_URL`: BambooHealth production environment URL
- `PDMP_API_USERNAME`: Production username
- `PDMP_API_PASSWORD`: Production password
- `PDMP_CLIENT_CERT`: Client certificate for authentication
- `PDMP_CLIENT_KEY`: Client private key

### Environment Setup

1. **Test Environment**: No certificates required, uses basic authentication
2. **Production Environment**: Requires client certificates for secure communication

## Usage

### Basic PDMP Request

1. **Navigate** to a patient note
2. **Click** the "PDMP Request" button in the note header
3. **Wait** for the system to extract patient and provider data
4. **Review** the PDMP response with risk scores and alerts
5. **Access** the full report via the report button

### Workflow

1. **Data Extraction**: System extracts patient, practitioner, and organization data
2. **Validation**: All data is validated for completeness and accuracy
3. **XML Generation**: Creates PMP Gateway-compliant XML request
4. **API Request**: Sends authenticated request to BambooHealth
5. **Response Processing**: Parses clinical data and risk scores
6. **Documentation**: Creates structured assessment in patient record
7. **UI Display**: Shows results with interactive report access

### Report Access

- **Direct Report Button**: Opens full HTML report in new tab
- **Clinical Data**: Displays risk scores and alerts in modal
- **Assessment Documentation**: Automatically creates structured assessment

## API Reference

### Report Endpoint

**GET** `/plugin-io/api/pdmp_bamboo/report`

**Parameters:**
- `report_id` (required): Report ID from PDMP response
- `env` (optional): Environment (test/prod)
- `patient_id` (optional): Canvas patient ID
- `practitioner_id` (optional): Canvas practitioner ID
- `organization_id` (optional): Canvas organization ID

**Response:**
- **200**: HTML report content
- **400**: Bad request (missing parameters)
- **500**: Server error

## Error Handling

The plugin includes comprehensive error handling:

### Data Validation Errors
- Missing required patient information
- Invalid practitioner credentials
- Incomplete organization data
- Location validation failures

### API Errors
- Authentication failures
- Network connectivity issues
- Invalid XML format
- Gateway timeout errors

### User Interface
- Clear error messages with actionable guidance
- Validation error modals with specific field issues
- Network error handling with retry options

## Security

### Authentication
- **Test Environment**: Basic HTTP authentication
- **Production Environment**: Certificate-based mutual TLS authentication



## Development

### Prerequisites
- Canvas SDK 0.1.4+
- Python 3.8+
- Access to BambooHealth PMP Gateway

### Installation
1. Install plugin `pdmp_bamboo`
2. Configure required secrets
3. Install client certificates (production only)
4. Restart Canvas services

### Testing
- Use test environment for development
- Verify data extraction accuracy
- Test error handling scenarios
- Validate XML generation

## Troubleshooting

### Common Issues


#### Data Validation Errors
- **Cause**: Missing or invalid patient/provider data
- **Solution**: Ensure all required fields are populated in Canvas

#### Authentication Failures
- **Cause**: Invalid credentials or certificate issues
- **Solution**: Verify secrets configuration and certificate validity

#### XML Generation Errors
- **Cause**: Invalid data format or missing required fields
- **Solution**: Check data extraction logs and validate input data

### Logging

The plugin provides comprehensive logging:
- Data extraction details
- XML generation process
- API request/response logging
- Error tracking and debugging

### Support

For technical support or feature requests:
1. Check the logs for detailed error information
2. Verify configuration and secrets
3. Test with known good data
4. Contact the development team with specific error details

## Version History

### v0.0.1
- Initial release
- Basic PDMP request functionality
- Test environment support
- Structured assessment documentation
- Report access via API endpoint

## License

This plugin is proprietary software. All rights reserved.

## Contributing

This is an internal Canvas plugin. For modifications or enhancements, please contact the development team.
PDMP3 Plugin
============

## Description

A Canvas Medical plugin for integrating with PMP Gateway v5.1 to retrieve prescription drug monitoring program (PDMP) data for patients. This plugin generates XML requests that only include actual patient data (no default values) and integrates with both PMP Gateway and FHIR endpoints.

## Architecture

### Core Components

1. **PMP Gateway Integration** (`utils/simple_request.py`) - Direct API calls to PMP Gateway
2. **FHIR Client** (`utils/fhir_client.py`) - Canvas Medical FHIR API integration 
3. **XML Generation** (`utils/xml.py`) - Dynamic XML payload generation
4. **Authentication** (`utils/auth.py`) - WSSE authentication for PMP Gateway

### Data Flow

1. Extract patient/provider data from Canvas
2. Generate XML payload with **only present data** (no defaults)
3. Authenticate with PMP Gateway using WSSE headers
4. Receive and parse prescription monitoring data
5. Display results in Canvas UI

## Configuration

### Required Canvas Plugin Secrets

**IMPORTANT**: All credentials and location data must be configured in Canvas plugin settings. The plugin will not work without these secrets configured:

#### PMP Gateway Credentials:
- `pmp_gateway_username` - Your PMP Gateway username
- `pmp_gateway_password` - Your PMP Gateway password  
- `pmp_gateway_api_url` - Your PMP Gateway API endpoint (e.g., `https://prep.pmpgateway.net/v5_1/patient`)

#### Facility Information:
- `pmp_location_name` - Your clinic/facility name
- `pmp_location_dea` - Your facility DEA number
- `pmp_location_npi` - Your facility NPI number
- `pmp_default_state` - Your facility state code (e.g., `KS`)
- `pmp_location_street` - Your facility street address
- `pmp_location_city` - Your facility city
- `pmp_location_zip` - Your facility ZIP code

### Testing with Working Values

For initial testing, you can use these working test credentials:

```
pmp_gateway_username: canvas-prep-1
pmp_gateway_password: j;%KAIGPI!o0Az>iSu{6
pmp_gateway_api_url: https://prep.pmpgateway.net/v5_1/patient

```

### FHIR Configuration (Future Use)

The plugin includes a FHIR client for Canvas Medical API integration:

- `canvas_fhir_base_url` - Canvas FHIR API base URL
- `canvas_api_key` - Canvas API bearer token

## Key Features

### ✅ Data Integrity

- **No Default Values**: XML only includes actual patient data
- **Error Handling**: Missing data triggers API errors (as intended)
- **Data Validation**: Comprehensive validation before API calls

### ✅ Flexible XML Generation

```python
# Production method - only actual data
generate_patient_request_xml(patient_data, staff_data, location_config)

# Testing method - includes defaults (TODO: remove in production)  
generate_patient_request_xml_for_testing()
```

### ✅ Dual Integration Support

- **PMP Gateway**: Direct PDMP data retrieval
- **FHIR Client**: Canvas Medical API integration (preserved for future use)

### ✅ Robust Authentication

- WSSE authentication with SHA256 digest (lowercase)
- Matches proven bamboo_request.py implementation
- UUID nonce generation for security

## Usage

1. **Install Plugin**: Deploy to Canvas Medical instance
2. **Configure Secrets**: Set production values in Canvas settings
3. **Access PDMP Data**: Click "Show Info (PDMP3)" button in note headers
4. **View Results**: Modal displays prescription history and risk scores

## API Response Format

Successful responses include:

- **Patient Prescription History**
- **NARX Risk Scores**: Narcotics, Stimulants, Sedatives, Overdose  
- **Clinical Alerts**: High/Medium/Low severity messages
- **Report URLs**: Links to detailed viewable reports
- **State Coverage**: Multi-state PDMP data aggregation

## Development Notes

### XML Generation Strategy

❌ **Old Approach** (Fixed):
```xml
<!-- Always included defaults even if data missing -->
<FirstName>Test</FirstName>  
<LastName>Provider</LastName>
```

✅ **New Approach**:
```xml
<!-- Only includes if staff_data.first_name exists -->
<FirstName>John</FirstName>
<!-- LastName omitted if not present -->
```

### Error Handling Philosophy

**Fail Fast**: Missing required data should trigger API errors, not be hidden by defaults. This ensures:

1. **Data Quality**: Forces proper data collection
2. **Debugging**: Clear error messages about missing fields
3. **Compliance**: Ensures all required PDMP data is present

### Testing vs Production

```python
# For testing - has defaults
xml = generate_patient_request_xml_for_testing()

# For production - only real data  
xml = generate_patient_request_xml(patient_data, staff_data, location_config)
```

**TODO**: Remove testing method in production deployment.

## Troubleshooting

### Common Issues

1. **Missing Data Errors**: Expected behavior - ensure all required fields are collected
2. **Authentication Failures**: Verify credentials match bamboo_request.py values
3. **Empty XML Elements**: Correct behavior - only present data is included
4. **State Coverage Errors**: Some states may not allow cross-state queries

### Debug Logging

All operations log with `PDMP3:` prefix:

```
PDMP3: Authentication headers generated successfully
PDMP3: API request completed - Status: success
PDMP3: Received response - Status: 200
```

## Security Considerations

- ⚠️ **Test Credentials**: Current defaults are for test environment only
- ⚠️ **Production Deployment**: Replace with encrypted production credentials
- ⚠️ **Certificate Requirements**: Production may require client certificates
- ⚠️ **State Compliance**: Ensure compliance with state PDMP regulations

## Future Enhancements

1. **FHIR Integration**: Leverage included FHIR client for Canvas API
2. **Certificate Support**: Add production certificate handling  
3. **Multi-State Optimization**: Enhanced cross-state query support
4. **Real-Time Alerts**: Integration with Canvas alerting system

---

### Important Notes

- **Test Environment**: Current configuration targets PMP Gateway test environment
- **Data Quality**: Plugin deliberately excludes default values to ensure data integrity
- **Production Ready**: Remove TODO items and configure proper credentials for production use
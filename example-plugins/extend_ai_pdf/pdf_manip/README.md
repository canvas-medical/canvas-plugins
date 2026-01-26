# Extend AI PDF Extraction Plugin

A Canvas plugin that uses Extend AI to extract structured information from PDF documents using configurable processors.

## Features

- **List Processors**: Browse all available Extend AI document processors
- **View Processor Configuration**: Retrieve detailed configuration for a specific processor
- **Process Documents**: Submit PDF documents (via public URL) for processing
- **Check Run Status**: Monitor the status of document processing runs
- **Retrieve Results**: Get extracted data from completed processing runs
- **File Management**: List and delete files stored in Extend AI

## Components

### Protocol: `PdfManip`

A SimpleAPI handler that exposes REST endpoints for Extend AI operations.

**API Endpoints:**

| Method | Endpoint | Description | SDK Method |
|--------|----------|-------------|------------|
| GET | `/processors` | List all available processors | `list_processors` |
| GET | `/processors/<processor_id>` | Get processor configuration | `processor` |
| POST | `/execute` | Start processing a document | `run_processor` |
| GET | `/status/<run_id>` | Check run status and cleanup files | `run_status` / `delete_file` |
| GET | `/result/<run_id>` | Get extraction results | `run_status` |
| GET | `/stored_files` | List all stored files | `list_files` |
| POST | `/delete_files` | Delete files from storage | `delete_file` |

### Application: `PdfFormApp`

A patient-specific application that launches a right side panel interface for:

- Selecting a processor from available options
- Submitting documents for processing via public S3 URL
- Monitoring processing status
- Viewing extracted results
- Managing stored files

## Configuration

### Required Secrets

Configure this secret in your Canvas plugin settings:

| Secret Name | Description |
|-------------|-------------|
| `ExtendAiKey` | Extend AI API Key |

## Installation

1. Install the plugin via the command line: `canvas install pdf_manip`
2. Configure the required secret with your Extend AI API key (`https://xxxx.canvasmedical.com/admin/plugin_io/plugin/`)
3. Access the application from a patient's chart in the drawer menu

## Usage

1. Open a patient chart
2. Launch the "PDF Upload" application
3. Select a processor from the dropdown list
4. Provide a publicly accessible URL to your PDF document
5. Submit for processing and monitor the status
6. View extracted results when processing completes

### Document Processing Workflow

1. **Select Processor**: Choose an Extend AI processor configured for your document type
2. **Submit Document**: Provide a public S3 URL to the PDF document
3. **Monitor Status**: The plugin polls for processing status (PENDING → PROCESSING → PROCESSED)
4. **Retrieve Results**: Once processed, view the structured extraction results
5. **Cleanup**: Files are automatically deleted from Extend AI after successful processing

## Extend AI Processor Types

Extend AI supports various processor types for different document extraction needs:

- **Extraction**: Extract structured data from documents using custom schemas
- **Classification**: Classify documents into predefined categories
- **Splitting**: Split multi-page documents into logical sections

## Important Note

The `CANVAS_MANIFEST.json` is used when installing your plugin. Please ensure it gets updated if you add, remove, or rename protocols.

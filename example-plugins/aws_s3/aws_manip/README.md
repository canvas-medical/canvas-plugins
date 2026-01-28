# AWS S3 Document Management Plugin

A Canvas plugin that enables storing, retrieving, and deleting documents in AWS S3 directly from the patient chart.

## Features

- **List Objects**: Browse all objects stored in your S3 bucket
- **Get Object Content**: Retrieve and view the content of text-based objects
- **Upload Text**: Save text content to S3 with a custom key
- **Upload Binary**: Upload image files (PNG, JPEG, GIF, WebP, BMP) to S3
- **Delete Objects**: Remove objects from the S3 bucket
- **Presigned URLs**: Generate temporary URLs for secure sharing (valid for 1 hour)

## Components

### Protocol: `AwsManip`

A SimpleAPI handler that exposes REST endpoints for S3 operations.

**API Endpoints:**

| Method | Endpoint | Description | SDK Method |
|--------|----------|-------------|------------|
| GET | `/list_items` | List all objects in the bucket | `list_s3_objects` |
| GET | `/get_item/<item_key>` | Retrieve object content by key | `access_s3_object` |
| GET | `/presigned_url/<item_key>` | Generate a presigned URL for an object | `generate_presigned_url` |
| POST | `/upload_item/<item_key>` | Upload content (text or binary) to S3 | `upload_text_to_s3` / `upload_binary_to_s3` |
| DELETE | `/delete_item/<item_key>` | Delete an object from S3 | `delete_object` |

### Application: `AwsFormApp`

A patient-specific application that launches a right side panel interface with three tabs:

1. **List/Get** - Browse objects, view content, copy presigned URLs, delete items
2. **Save Text** - Upload text content with a custom S3 key
3. **Save Binary** - Upload image files to S3

## Configuration

### Required Secrets

Configure these secrets in your Canvas plugin settings:

| Secret Name | Description |
|-------------|-------------|
| `S3Key` | AWS Access Key ID |
| `S3Secret` | AWS Secret Access Key |
| `S3Region` | AWS Region (e.g., `us-east-1`) |
| `S3Bucket` | S3 Bucket name |

## Installation

1. Install the plugin via the command line: `canvas install aws_manip`
2. Configure the four required secrets with your AWS credentials (`https://xxxx.canvasmedical.com/admin/plugin_io/plugin/`)
3. Access the application from a patient's chart in the drawer menu

## Usage

1. Open a patient chart
2. Launch the "AWS S3 Document Management" application
3. Use the tabs to list, upload, or manage S3 objects

## AWS IAM Permissions

Ensure your AWS credentials have the following S3 permissions on the target bucket:

- `s3:ListBucket`
- `s3:GetObject`
- `s3:PutObject`
- `s3:DeleteObject`

## Important Note

The `CANVAS_MANIFEST.json` is used when installing your plugin. Please ensure it gets updated if you add, remove, or rename protocols.

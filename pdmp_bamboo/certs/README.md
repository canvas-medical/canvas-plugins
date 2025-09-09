# PDMP Certificate Directory

This directory contains client certificates for BambooHealth PMP Gateway authentication.

## Required Files

- `client.crt` - Client certificate file (for production environment)
- `client.key` - Private key file (for production environment)

## Environment Configuration

The plugin automatically detects the environment via the `PDMP_ENVIRONMENT` secret:

- **Production** (`PDMP_ENVIRONMENT = "production"`): Uses client certificates for mutual TLS
- **Test/Development** (any other value): Uses standard authentication without certificates

## Setup Instructions

### For Production Environment

1. **Obtain certificates** from BambooHealth for production PDMP Gateway access
2. **Place certificate files** in this directory:
   - `client.crt` - Your client certificate
   - `client.key` - Your private key (password-less for Canvas compatibility)
3. **Set environment** in Canvas plugin secrets:
   - `PDMP_ENVIRONMENT` = "production"

### For Test/Development Environment

1. **Set environment** in Canvas plugin secrets:
   - `PDMP_ENVIRONMENT` = "test" (or any value other than "production")
2. **No certificate files required** - plugin uses standard authentication

## Security Notes

- Keep your private key secure and never commit it to version control
- Ensure proper file permissions (600 for key file, 644 for cert file)
- Rotate certificates according to your organization's security policy
- Certificates must be signed by BambooHealth's trusted CA

## Testing

To test the plugin without certificates:
- Set `PDMP_ENVIRONMENT` to "test"
- Use test credentials in `PDMP_API_USERNAME` and `PDMP_API_PASSWORD`
- Point `PDMP_API_URL` to test environment endpoint
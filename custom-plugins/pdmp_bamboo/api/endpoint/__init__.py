"""
PDMP API Package

This package provides clean, modular API handling for PDMP requests.
It separates concerns into client, response handling, and configuration.
"""

"""
API Package

Contains API endpoints and clients for the PDMP plugin.
"""

from pdmp_bamboo.api.endpoint.report_endpoint import ReportEndpoint

__all__ = ['ReportEndpoint']
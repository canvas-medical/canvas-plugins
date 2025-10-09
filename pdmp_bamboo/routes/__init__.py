"""
PDMP Bamboo Routes.

SimpleAPI endpoints for PDMP report requests.
"""

from pdmp_bamboo.routes.report_api import ReportAPI
from pdmp_bamboo.routes.report_iframe_api import ReportIframeAPI

__all__ = [
    "ReportAPI",
    "ReportIframeAPI",
]

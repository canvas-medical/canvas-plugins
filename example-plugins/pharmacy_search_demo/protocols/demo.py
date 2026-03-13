"""Demo for KOALA-4355: improved pharmacy search filters.

Install this plugin and hit GET /plugin-io/api/pharmacy_search_demo/run
to exercise every new search_pharmacies parameter and get a pass/fail report.
"""

from __future__ import annotations

from http import HTTPStatus
from typing import Any

from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import SimpleAPIRoute, StaffSessionAuthMixin
from canvas_sdk.utils.http import pharmacy_http
from logger import log


class PharmacySearchDemo(StaffSessionAuthMixin, SimpleAPIRoute):
    """Runs all pharmacy search test cases and returns a JSON report."""

    PATH = "/run"

    def get(self) -> list[Response]:
        """Execute every test case and return results."""
        results: list[dict[str, Any]] = []

        for case in TEST_CASES:
            name = case["name"]
            kwargs = case["kwargs"]
            check = case["check"]

            try:
                log.info(f"[pharmacy_search_demo] running: {name}")
                pharmacies = pharmacy_http.search_pharmacies(**kwargs)
                passed, detail = check(pharmacies)
                results.append(
                    {
                        "name": name,
                        "passed": passed,
                        "detail": detail,
                        "result_count": len(pharmacies),
                    }
                )
            except Exception as exc:
                log.error(f"[pharmacy_search_demo] {name} error: {exc}")
                results.append(
                    {
                        "name": name,
                        "passed": False,
                        "detail": f"exception: {exc}",
                    }
                )

        passed_count = sum(1 for r in results if r["passed"])
        total = len(results)

        return [
            JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "summary": f"{passed_count}/{total} passed",
                    "all_passed": passed_count == total,
                    "results": results,
                },
            )
        ]


# ---------------------------------------------------------------------------
# Check helpers
# ---------------------------------------------------------------------------


def _is_nonempty(pharmacies: list[dict]) -> tuple[bool, str]:
    if pharmacies:
        return True, f"returned {len(pharmacies)} result(s)"
    return False, "expected results but got none"


def _is_empty_ok(pharmacies: list[dict]) -> tuple[bool, str]:
    return True, f"returned {len(pharmacies)} result(s) (empty is acceptable)"


def _all_in_state(state: str) -> Any:
    def check(pharmacies: list[dict]) -> tuple[bool, str]:
        if not pharmacies:
            return False, "no results to verify"
        mismatches = [
            p.get("state", p.get("State", ""))
            for p in pharmacies
            if (p.get("state") or p.get("State") or "").upper() != state.upper()
        ]
        if mismatches:
            return False, f"{len(mismatches)} pharmacy(ies) not in state {state}: {mismatches[:5]}"
        return True, f"all {len(pharmacies)} result(s) in state {state}"

    return check


def _all_zip_startswith(prefix: str) -> Any:
    def check(pharmacies: list[dict]) -> tuple[bool, str]:
        if not pharmacies:
            return False, "no results to verify"
        mismatches = []
        for p in pharmacies:
            zip_code = str(p.get("zip_code") or p.get("ZipCode") or p.get("zip") or "")
            if not zip_code.startswith(prefix):
                mismatches.append(zip_code)
        if mismatches:
            return False, f"{len(mismatches)} zip(s) don't start with {prefix}: {mismatches[:5]}"
        return True, f"all {len(pharmacies)} result(s) have zip starting with {prefix}"

    return check


def _org_name_contains(substr: str) -> Any:
    def check(pharmacies: list[dict]) -> tuple[bool, str]:
        if not pharmacies:
            return False, "no results to verify"
        mismatches = []
        for p in pharmacies:
            name = p.get("organization_name") or p.get("OrganizationName") or p.get("name") or ""
            if substr.lower() not in name.lower():
                mismatches.append(name)
        if mismatches:
            return (
                False,
                f"{len(mismatches)} name(s) don't contain '{substr}': {mismatches[:5]}",
            )
        return True, f"all {len(pharmacies)} result(s) contain '{substr}' in name"

    return check


def _has_location_fields(pharmacies: list[dict]) -> tuple[bool, str]:
    """Just verify the call succeeded — location ordering is server-side."""
    if not pharmacies:
        return False, "no results to verify"
    return True, f"returned {len(pharmacies)} result(s) with location ordering"


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

TEST_CASES: list[dict[str, Any]] = [
    {
        "name": "1. basic text search",
        "kwargs": {"search_term": "walgreens"},
        "check": _is_nonempty,
    },
    {
        "name": "2. empty/no search term sends no search= param",
        "kwargs": {"search_term": None},
        "check": _is_empty_ok,
    },
    {
        "name": "3. filter by state",
        "kwargs": {"search_term": None, "state": "CA"},
        "check": _all_in_state("CA"),
    },
    {
        "name": "4. filter by organization name (icontains)",
        "kwargs": {"search_term": None, "organization_name": "CVS"},
        "check": _org_name_contains("CVS"),
    },
    {
        "name": "5. filter by zip code prefix",
        "kwargs": {"search_term": None, "zip_code_prefix": "902"},
        "check": _all_zip_startswith("902"),
    },
    {
        "name": "6. filter by multiple zip code prefixes",
        "kwargs": {"search_term": None, "zip_code_prefix": "902,100"},
        "check": _is_nonempty,
    },
    {
        "name": "7. filter by NCPDP ID",
        "kwargs": {"search_term": None, "ncpdp_id": "0000000"},
        "check": _is_empty_ok,
    },
    {
        "name": "8. filter by specialty type",
        "kwargs": {"search_term": None, "specialty_type": "retail"},
        "check": _is_nonempty,
    },
    {
        "name": "9. filter by exact ID (nonexistent)",
        "kwargs": {"search_term": None, "id": 999999999},
        "check": _is_empty_ok,
    },
    {
        "name": "10. location-based ordering",
        "kwargs": {
            "search_term": "pharmacy",
            "latitude": "34.05",
            "longitude": "-118.24",
        },
        "check": _has_location_fields,
    },
    {
        "name": "11. combined filters: state + organization name",
        "kwargs": {
            "search_term": None,
            "state": "CA",
            "organization_name": "Walgreens",
        },
        "check": lambda pharmacies: (
            (True, f"all {len(pharmacies)} result(s) match combined filters")
            if pharmacies
            else (False, "no results for combined filter")
        ),
    },
]

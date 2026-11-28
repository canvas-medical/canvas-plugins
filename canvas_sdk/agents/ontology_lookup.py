"""GETs on the ontology services the agent tools look codes and medications up in."""

from typing import Any

from logger import log


class CodeSearchUnavailable(RuntimeError):
    """An ontology service did not answer; the model is told to try again."""


class CodeNotFound(CodeSearchUnavailable):
    """The service has no record at the path asked for, such as an unknown FDB code.

    A kind of ``CodeSearchUnavailable``, so a caller that only handles an outage still
    stops there; one that can tell the model what to fix catches this first.
    """


def get_json(client: Any, path: str) -> Any:
    """The JSON body of a GET on an ontology service, raising when it did not answer.

    Raises:
        CodeNotFound: The service answered 404.
        CodeSearchUnavailable: It did not answer, or answered another error.
    """
    try:
        response = client.get_json(path)
    except Exception as exc:
        log.warning(f"Ontology lookup failed: {type(exc).__name__}")
        raise CodeSearchUnavailable("The code search did not answer; try again.") from exc
    if response.status_code == 404:
        raise CodeNotFound("The code search found no such record.")
    if response.status_code != 200:
        log.warning(f"Ontology lookup answered {response.status_code}")
        raise CodeSearchUnavailable(f"The code search answered {response.status_code}; try again.")
    return response.json()


def items(body: Any) -> list[dict[str, Any]]:
    """The rows of a paginated (``{"results": [...]}``) or bare-list response."""
    rows = body.get("results") if isinstance(body, dict) else body
    return [row for row in rows or [] if isinstance(row, dict)]


__exports__ = ()

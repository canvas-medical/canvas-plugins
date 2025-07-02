import json
from datetime import datetime
from pathlib import Path
from typing import Any

TOKENS_PATH = Path.home() / ".canvas" / "tokens.json"
TOKENS_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load_tokens() -> dict:
    if not TOKENS_PATH.exists():
        return {}
    with TOKENS_PATH.open("r") as f:
        return json.load(f)


def _save_tokens(tokens: dict) -> None:
    with TOKENS_PATH.open("w") as f:
        json.dump(tokens, f, indent=2)


def _set_value(key: str, value: Any) -> None:
    """Set a value in the token storage."""
    tokens = _load_tokens()
    tokens[key] = value
    _save_tokens(tokens)


def _get_value(key: str) -> Any | None:
    """Get value from the token storage."""
    tokens = _load_tokens()
    return tokens.get(key)


def _delete_value(key: str) -> None:
    """Delete a value from the token storage."""
    tokens = _load_tokens()
    tokens.pop(key, None)
    _save_tokens(tokens)


def set_token(host_token_key: str, token: str, exp: datetime) -> None:
    """Set a token with an expiry date in the token storage."""
    _set_value(host_token_key, {"token": token, "exp_date": exp.isoformat()})


def get_token(host_token_key: str) -> str | None:
    """Get a token from the token storage."""
    value = _get_value(host_token_key)

    if not value:
        return None
    try:
        exp = value["exp_date"]
        if datetime.fromisoformat(exp) <= datetime.now():
            return None
    except ValueError:
        return None

    return value["token"]


def delete_token(host_token_key: str) -> None:
    """Delete a token from the token storage."""
    _delete_value(host_token_key)

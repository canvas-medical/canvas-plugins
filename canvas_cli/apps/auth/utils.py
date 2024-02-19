import keyring

# Keyring namespace we'll use
KEYRING_SERVICE = __name__


def get_password(username: str) -> str | None:
    """Return the stored password for username, or None."""
    return keyring.get_password(KEYRING_SERVICE, username)


def set_password(username: str, password: str) -> None:
    """Set the password for the given username."""
    keyring.set_password(KEYRING_SERVICE, username=username, password=password)


def delete_password(username: str) -> None:
    """Delete the password for the given username."""
    keyring.delete_password(KEYRING_SERVICE, username=username)

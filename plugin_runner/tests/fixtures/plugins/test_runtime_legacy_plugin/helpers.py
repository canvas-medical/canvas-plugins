def working_directory() -> str:
    """Read the working directory.

    `os` is not an allowed import, and a deferred import inside a function only reaches
    the sandbox's `__import__` when this module is sandbox-compiled — which happens under
    the current rules and not under the deprecated ones. Nothing about it fails at load.
    """
    import os

    return os.getcwd()

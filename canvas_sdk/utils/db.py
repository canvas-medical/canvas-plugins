from django.db import close_old_connections, reset_queries


def thread_cleanup() -> None:
    """
    Call this method to do cleanup work at thread exit. For users doing
    advanced work with threads there is a need to do cleanup after each thread
    runs so that e.g. the database pool does not become exhausted.
    """
    reset_queries()
    close_old_connections()


__exports__ = ("thread_cleanup",)

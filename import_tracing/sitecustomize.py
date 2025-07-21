import os

if os.getenv("PROFILE_IMPORTS"):
    import site

    site.addsitedir("/app/import_tracing")

    import __init__

    __init__.enable()

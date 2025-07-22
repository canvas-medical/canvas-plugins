import os

if os.getenv("PROFILE_IMPORTS"):
    import __init__

    __init__.enable()

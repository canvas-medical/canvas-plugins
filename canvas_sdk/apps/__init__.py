class BaseApp:
    """
    Base class for an App, which is currently the way plugin authors define
    static additions to the Canvas UI.
    """

    SCOPE_PATIENT = "patient"
    SCOPE_GLOBAL = "global"

    TARGET_MODAL = "modal"
    TARGET_NEW_WINDOW = "new-window"
    TARGET_RIGHT_PANE = "right-pane"

    application_identifier = ""
    # TODO_APPS is this just a path to a file included in the plugin?
    icon = ""
    scope = SCOPE_PATIENT
    target = TARGET_MODAL
    # TODO_APPS what template tags can be used here? patient ID, what else?
    url_template = ""

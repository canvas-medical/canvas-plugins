from canvas_sdk.v1.data import ModelExtension, Patient


class PatientProxy(Patient, ModelExtension):
    """Patient proxy used as the ForeignKey target for plugin-owned CustomModels.

    Plugins can't FK directly to canvas_sdk.v1.data.Patient — Custom Data lives
    in the plugin's namespace and the FK column needs to target a model the
    plugin's schema knows about. Proxies bridge that gap.
    """

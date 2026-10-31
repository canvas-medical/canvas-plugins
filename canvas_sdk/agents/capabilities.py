from enum import StrEnum


class Capability(StrEnum):
    """What an agent run may do beyond what its manifest grants, decided by the platform.

    The platform grants a capability from the permissions of the staff member who
    started the run and sets the run's grants on the agent as ``self.capabilities``.
    A run nobody on staff started has none. A tool declares the capabilities it needs
    with ``required_capabilities``, and the platform hides it from a run without them.
    """

    # Read and change claims across patients: the requester holds the Revenue access
    # permission, which the revenue pages require, and can see every patient.
    REVENUE = "revenue"


__exports__ = ("Capability",)

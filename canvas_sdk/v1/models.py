# Normally we would register Django models in the models module, but they are in "data" for legacy
# reasons. For this reason, we import * from data to avoid duplication.

from .data import *  # noqa: F403

__exports__ = ()

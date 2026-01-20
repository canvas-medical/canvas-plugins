from canvas_sdk.effects.custom_model.mutation import Mutation
from canvas_sdk.v1.data.base import RestrictedQuerySet


class Update(Mutation):
    def __init__(self, qs: RestrictedQuerySet, **kwargs):
        super().__init__(qs)
        self._kwargs = kwargs

    def apply(self):
        self.qs.update(**self._kwargs)


__exports__ = ("Update")

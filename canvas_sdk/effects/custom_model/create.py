from canvas_sdk.effects.custom_model.mutation import Mutation
from canvas_sdk.v1.data.base import RestrictedQuerySet


class BulkCreate(Mutation):
    def __init__(self, qs: RestrictedQuerySet, **kwargs):
        super().__init__(qs)
        self._kwargs = kwargs

    def apply(self):
        self.qs.bulk_create(**self._kwargs)


class Create(Mutation):
    def __init__(self, qs: RestrictedQuerySet, **kwargs):
        super().__init__(qs)
        self._kwargs = kwargs

    def apply(self):
        return self.qs.create(**self._kwargs)


class GetOrCreate(Mutation):
    def __init__(self, qs: RestrictedQuerySet, **kwargs):
        super().__init__(qs)
        self._kwargs = kwargs

    def apply(self):
        return self.qs.get_or_create(**self._kwargs)


__exports__ = ("BulkCreate", "Create", "GetOrCreate")

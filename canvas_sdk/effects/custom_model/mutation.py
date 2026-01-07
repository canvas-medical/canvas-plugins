from canvas_sdk.v1.data.base import RestrictedQuerySet


class Mutation:
    class Meta:
        abstract = True

    def __init__(self, qs: RestrictedQuerySet):
        self.qs = qs

    def apply(self):
        raise NotImplementedError()

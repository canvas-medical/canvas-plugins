import factory

from canvas_sdk.v1.data import (
    Claim,
    ClaimComment,
    ClaimCoverage,
    ClaimLabel,
    ClaimProvider,
    ClaimQueue,
    ClaimSubmission,
)


class ClaimCoverageFactory(factory.django.DjangoModelFactory[ClaimCoverage]):
    """Factory for creating ClaimCoverage."""

    class Meta:
        model = ClaimCoverage

    claim = factory.SubFactory("canvas_sdk.test_utils.factories.claim.ClaimFactory")
    coverage = factory.SubFactory("canvas_sdk.test_utils.factories.CoverageFactory")


class ClaimQueueFactory(factory.django.DjangoModelFactory[ClaimQueue]):
    """Factory for creating ClaimQueue."""

    class Meta:
        model = ClaimQueue
        django_get_or_create = ("queue_sort_ordering",)

    queue_sort_ordering = 5
    name = "Claim: Filed"


class ClaimFactory(factory.django.DjangoModelFactory[Claim]):
    """Factory for creating Claim."""

    class Meta:
        model = Claim

    note = factory.SubFactory("canvas_sdk.test_utils.factories.NoteFactory")
    current_queue = factory.SubFactory(ClaimQueueFactory)


class ClaimCommentFactory(factory.django.DjangoModelFactory[ClaimComment]):
    """Factory for creating ClaimComment."""

    class Meta:
        model = ClaimComment

    claim = factory.SubFactory(ClaimFactory)
    comment = "Need to message Dr. House"


class ClaimProviderFactory(factory.django.DjangoModelFactory[ClaimProvider]):
    """Factory for creating ClaimProvider."""

    class Meta:
        model = ClaimProvider

    claim = factory.SubFactory(ClaimFactory)


class ClaimLabelFactory(factory.django.DjangoModelFactory[ClaimLabel]):
    """Factory for creating ClaimLabel."""

    class Meta:
        model = ClaimLabel

    claim = factory.SubFactory(ClaimFactory)
    label = factory.SubFactory("canvas_sdk.test_utils.factories.TaskLabelFactory")


class ClaimSubmissionFactory(factory.django.DjangoModelFactory[ClaimSubmission]):
    """Factory for creating ClaimSubmission."""

    class Meta:
        model = ClaimSubmission

    claim = factory.SubFactory(ClaimFactory)
    clearinghouse_claim_id = "123456"

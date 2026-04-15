from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect


class ScheduleCallback(_BaseEffect):
    """Schedule a callback event to be fired after a delay.

    After ``delay_seconds``, the platform will emit a ``SCHEDULED_CALLBACK``
    event that the plugin can handle. The ``key`` and ``context`` are passed
    through to the event so the handler can identify what triggered the
    callback and act accordingly.

    This is useful for patterns that need a grace period before taking action,
    such as checking whether a resource is still in a particular state after
    a delay.

    Example usage::

        class OnClaimQueueMoved(BaseProtocol):
            RESPONDS_TO = EventType.Name(EventType.CLAIM_QUEUE_MOVED)

            def compute(self):
                if self.event.context["queue_entered"]["name"] != "QueuedForSubmission":
                    return []
                return [ScheduleCallback(
                    key=f"candid-submit-{self.target}",
                    context={"claim_id": str(self.target)},
                    delay_seconds=60,
                ).apply()]

        class OnSubmissionCheck(BaseProtocol):
            RESPONDS_TO = EventType.Name(EventType.SCHEDULED_CALLBACK)

            def compute(self):
                claim = Claim.objects.get(id=self.event.context["claim_id"])
                if claim.current_queue.name != "QueuedForSubmission":
                    return []
                return [HttpRequest(...).apply()]
    """

    class Meta:
        effect_type = EffectType.SCHEDULE_CALLBACK

    key: str
    context: dict[str, Any] | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Serialize the callback key and context into the payload."""
        return {
            "key": self.key,
            "context": self.context or {},
        }


__exports__ = ("ScheduleCallback",)

from abc import abstractmethod

import arrow
from cron_converter import Cron

from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler


class CronTask(BaseHandler):
    """
    A type of handler that executes periodically according to a provided schedule.
    """

    RESPONDS_TO = EventType.Name(EventType.CRON)

    SCHEDULE: str = ""  # e.g. "* * * * *" for every minute.

    @abstractmethod
    def execute(self) -> list[Effect]:
        """
        Perform some work and return a list of effects.
        """

    def compute(self) -> list[Effect]:
        """
        See if the task should execute given the timestamp.
        """
        if not self.SCHEDULE:
            raise ValueError("You must set a SCHEDULE.")
        datetime = arrow.get(self.event.target.id).datetime
        if datetime in Cron(self.SCHEDULE):
            return self.execute()
        return []


__exports__ = ("CronTask",)

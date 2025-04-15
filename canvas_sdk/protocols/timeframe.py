import arrow


class Timeframe:
    """A class representing a timeframe with a start and and end."""

    def __init__(self, start: arrow.Arrow, end: arrow.Arrow):
        self.start = start
        self.end = end

    def __str__(self) -> str:
        return f"<Timeframe start={self.start}, end={self.end}>"

    @property
    def duration(self) -> int:
        """Returns the number of days in the timeframe."""
        return (self.end - self.start).days

    def increased_by(self, years: int = 0, months: int = 0, days: int = 0) -> "Timeframe":
        """Returns a new Timeframe object increased by the years, months, days in the arguments."""
        start = self.start
        end = self.end

        if years > 0:
            end = end.shift(years=years)
        elif years < 0:
            start = start.shift(years=years)

        if months > 0:
            end = end.shift(months=months)
        elif months < 0:
            start = start.shift(months=months)

        if days > 0:
            end = end.shift(days=days)
        elif days < 0:
            start = start.shift(days=days)

        return Timeframe(start=start, end=end)


__exports__ = ("Timeframe",)

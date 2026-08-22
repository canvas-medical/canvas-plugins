from abc import abstractmethod

from canvas_sdk.effects import Effect
from canvas_sdk.handlers.base import BaseHandler


class PluginSurfaceEntry(BaseHandler):
    """Base class for an entry a plugin contributes to a Canvas surface.

    Canvas asks every plugin what it offers for a surface, then tells the plugin
    when the user picks one of its entries. An action button in a note header and
    an automation in the note body command list are both that shape, so both
    subclass this.

    A subclass says which events those two are, what the entry looks like, and
    what happens when the user picks it.
    """

    PRIORITY: int = 0

    def visible(self) -> bool:
        """Return True to offer this entry for the context of the event."""
        return True

    @abstractmethod
    def handle(self) -> list[Effect]:
        """Return the effects to apply when the user picks this entry."""
        raise NotImplementedError("Implement to handle the entry being picked")

    @property
    @abstractmethod
    def entry_key(self) -> str:
        """The key Canvas sends back when the user picks this entry."""
        raise NotImplementedError("Implement to identify the entry")

    @abstractmethod
    def is_list_event(self) -> bool:
        """Whether the event asks plugins what they offer, rather than picking one."""
        raise NotImplementedError("Implement to recognise the list event")

    @abstractmethod
    def shows_this_entry(self) -> bool:
        """Whether the list event asks for the surface this entry belongs to.

        A surface with more than one location answers False for the locations
        that are not its own.
        """
        raise NotImplementedError("Implement to match the entry to the surface")

    @abstractmethod
    def entry_effect(self) -> Effect:
        """The effect that puts this entry in the list."""
        raise NotImplementedError("Implement to describe the entry")

    def is_configured(self) -> bool:
        """Whether the subclass carries what it needs to answer at all."""
        return True

    def compute(self) -> list[Effect]:
        """Offer this entry, or handle the user picking it."""
        if not self.is_configured():
            return []

        if self.is_list_event():
            if self.shows_this_entry() and self.visible():
                return [self.entry_effect()]
            return []

        if self.event.context.get("key") == self.entry_key:
            return self.handle()

        return []


__exports__ = ("PluginSurfaceEntry",)

"""SettingsPageHandler — the new handler type the Notion gap analysis calls
out as priority #4 for instance-configuration plugins.

Plugins subclass this to register a section under home-app's `/set-up/` UI
with the same visual treatment as built-in sections. The handler responds to
``EventType.INSTANCE_CONFIG__GET_SETTINGS_PAGE`` and returns a
:class:`SettingsPageForm` effect describing the form's fields and category.

Example::

    class FastingProgramSettings(SettingsPageHandler):
        SECTION_KEY = "fasting_program"
        SECTION_TITLE = "Fasting Program"
        SECTION_CATEGORY = "Clinical"
        SECTION_DESCRIPTION = "Customer-configurable parameters for the fasting protocol."

        def render(self) -> SettingsPageForm:
            return SettingsPageForm(
                section_key=self.SECTION_KEY,
                title=self.SECTION_TITLE,
                category=self.SECTION_CATEGORY,
                description=self.SECTION_DESCRIPTION,
                form_fields=[
                    FormField(key="hours", label="Fasting Window (hours)", type=InputType.NUMBER, value=16),
                    FormField(key="practitioner_signoff", label="Signoff", type=InputType.CHECKLIST_PICKER,
                              options=["MD", "NP", "RN"]),
                ],
            )
"""

from abc import abstractmethod
from typing import Any

from django.core.exceptions import ImproperlyConfigured

from canvas_sdk.effects import Effect
from canvas_sdk.effects.settings_page_form import SettingsPageForm
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler


class SettingsPageHandler(BaseHandler):
    """Register a native section under home-app's /set-up/ UI."""

    SECTION_KEY: str
    SECTION_TITLE: str = ""
    SECTION_CATEGORY: str = "General"
    SECTION_DESCRIPTION: str = ""

    RESPONDS_TO = [
        EventType.Name(EventType.INSTANCE_CONFIG__GET_SETTINGS_PAGE),
    ]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if not getattr(cls, "SECTION_KEY", None):
            raise ImproperlyConfigured(f"{cls.__name__!r} must define SECTION_KEY.")

    def accept_event(self) -> bool:
        """Only handle events whose section_key matches this handler."""
        return self.event.context.get("section_key") == self.SECTION_KEY

    def compute(self) -> list[Effect]:
        """Build the SettingsPageForm by delegating to subclass `render`."""
        form = self.render()
        if not form.section_key:
            form.section_key = self.SECTION_KEY
        if not form.title:
            form.title = self.SECTION_TITLE or self.SECTION_KEY
        if form.category == "General" and self.SECTION_CATEGORY != "General":
            form.category = self.SECTION_CATEGORY
        if not form.description and self.SECTION_DESCRIPTION:
            form.description = self.SECTION_DESCRIPTION
        return [form.apply()]

    @abstractmethod
    def render(self) -> SettingsPageForm:
        """Subclasses return the SettingsPageForm that describes their section."""
        raise NotImplementedError


__exports__ = ("SettingsPageHandler",)

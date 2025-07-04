from canvas_sdk.v1.data import Command


class ToggleQuestionsMixin:
    """Mixin that adds toggle functionality to questionnaire-based commands.

    This mixin should be used with classes that inherit from QuestionnaireCommand
    and provides the ability to skip/enable individual questions.

    Note: In the data model, skip=true means the question is ENABLED (not skipped).
    This is counterintuitive but matches the existing behavior.
    """

    # All toggle states (persisted + runtime changes)
    _question_toggles: dict[str, bool] | None = None

    def _ensure_toggles_loaded(self) -> None:
        """Load toggle states from the database if not already loaded."""
        if self._question_toggles is not None:
            return

        self._question_toggles = {}

        if hasattr(self, "command_uuid") and self.command_uuid:
            try:
                command_data = Command.objects.values_list("data", flat=True).get(
                    id=self.command_uuid
                )
                for key, value in command_data.items():
                    if key.startswith("skip-"):
                        question_id = key.replace("skip-", "")
                        self._question_toggles[question_id] = bool(value)
            except Command.DoesNotExist:
                pass

    @property
    def question_toggles(self) -> dict[str, bool]:
        """Get the current toggle states for questions (question_id -> enabled)."""
        self._ensure_toggles_loaded()
        return self._question_toggles.copy()  # type: ignore[union-attr]

    def is_question_enabled(self, question_id: str | int) -> bool | None:
        """Check if a question is enabled."""
        self._ensure_toggles_loaded()
        question_id = str(question_id)
        return self._question_toggles.get(question_id, None)  # type: ignore[union-attr]

    def set_question_enabled(self, question_id: str | int, enabled: bool) -> None:
        """Enable or disable a question."""
        self._ensure_toggles_loaded()
        self._question_toggles[str(question_id)] = enabled  # type: ignore[index]

    @property
    def values(self) -> dict:
        """Include skip states in command values."""
        values = super().values  # type: ignore[misc]

        # Get all current toggle states
        all_toggles = self.question_toggles

        # Add skip- prefix for the values dict
        for question_id, enabled in all_toggles.items():
            values[f"skip-{question_id}"] = enabled

        return values


__exports__ = ()

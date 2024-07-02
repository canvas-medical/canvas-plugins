from pydantic_core import ValidationError

from canvas_sdk.base import Model


class DataModel(Model):
    class Meta:
        update_required_fields = ("id",)

    def model_dump_json_nested(self, *args, **kwargs) -> str:
        """
        Returns the model's json representation nested in a {"data": {..}} key.
        """
        return f'{{"data": {self.model_dump_json(*args, **kwargs)}}}'

    def _validate_before_effect(self, method: str) -> None:
        if method == "create" and getattr(self, "id", None):
            error = self._create_error_detail(
                "value", "create cannot be called on a model with an id", "id"
            )
            raise ValidationError.from_exception_data(self.__class__.__name__, [error])
        super()._validate_before_effect(method)

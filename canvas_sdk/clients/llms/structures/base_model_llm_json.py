from typing import get_args, get_origin, get_type_hints

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseModelLlmJson(BaseModel):
    """Subclass of BaseModel to ensure valid JSON Schema.

    When using the method `model_json_schema`:
    - the key `additionalProperties` will be present, set to False
    - the fields name will be camelCased
    """

    model_config = ConfigDict(extra="forbid", alias_generator=to_camel)

    @classmethod
    def validate_nested_models(cls) -> bool:
        """Validate that all nested BaseModel fields are BaseModelLlmJson subclasses."""
        # Resolve forward references (strings/ForwardRef from `from __future__ import
        # annotations` or synthetic modules) into actual types via get_type_hints().
        try:
            hints = get_type_hints(cls)
        except Exception:
            hints = {}

        for field_name, field_info in cls.model_fields.items():
            field_type = hints.get(field_name, field_info.annotation)

            types_to_check: list = []
            if get_origin(field_type) is not None:
                types_to_check.extend(get_args(field_type))
            else:
                types_to_check.append(field_type)

            for a_type in types_to_check:
                if not isinstance(a_type, type):
                    continue
                if not issubclass(a_type, BaseModel):
                    continue
                if not (issubclass(a_type, BaseModelLlmJson) and a_type.validate_nested_models()):
                    return False
        return True


__exports__ = ()

from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import DateTimeField, JSONField, Model
from django.forms.fields import URLField as URLFormField
from django.utils import timezone


class URLArray(JSONField):
    default_error_messages = JSONField.default_error_messages | {
        "invalid_list": "Value must be a list",
        "invalid_strings": "Value must be a list of URLs as strings",
        "invalid_urls": "Value must be a list of valid URLs",
    }

    def validate(self, value: Any, model_instance: Model | None) -> None:
        super().validate(value, model_instance)
        if not isinstance(value, list):
            raise ValidationError(
                self.error_messages["invalid_list"],
                code="invalid_list",
                params={"value": value},
            )
        if not all(isinstance(v, str) for v in value):
            raise ValidationError(
                self.error_messages["invalid_strings"],
                code="invalid_urls",
                params={"value": value},
            )
        try:
            uv = URLValidator()
            for v in value:
                uv(v)
        except ValidationError:
            raise ValidationError(
                self.error_messages["invalid_urls"],
                code="invalid_urls",
                params={"value": value},
            )

    def from_db_value(self, value: Any, *args: Any, **kwargs: Any) -> Any:
        value = super().from_db_value(value, *args, **kwargs)
        if isinstance(value, list) and not value:
            return None
        return value

    def to_python(self, value: Any) -> Any:
        value = super().to_python(value)
        if isinstance(value, list):
            if not value:
                return None
            uf = URLFormField()
            value = [uf.to_python(v) for v in value if isinstance(v, str)]
        return value


class AppliedDateField(DateTimeField):
    def __init__(self, *args: Any, **kwargs: Any):
        kwargs.setdefault("blank", True)
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance: Model, add: bool) -> Any:
        if not getattr(model_instance, self.attname, None):
            value = timezone.now()
            setattr(model_instance, self.attname, value)
            return value
        return super().pre_save(model_instance, add)

from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError as JsonschemaValidationError
from saviialib.general_types.error_types.api.saviia_api_error_types import (
    ValidationError,
)


class JsonschemaClient:
    def __init__(self, schema):
        self.schema = schema
        self.validator = Draft7Validator(schema)

    def validate(self, data):
        errors = list(self.validator.iter_errors(data))
        if not errors:
            return True
        error = errors[0]
        raise ValidationError(reason=self._format_error(error))

    def _format_error(self, error: JsonschemaValidationError) -> str:
        path = ".".join(str(p) for p in error.absolute_path)
        if error.validator in ("maxItems",):
            return f"'{path}' has too many items (max {error.validator_value})."
        if error.validator in ("maxLength",):
            return f"'{path}' is too long (max length {error.validator_value})."
        if isinstance(error.instance, (str, list, dict)):
            return f"Invalid value at '{path}'."
        return f"Invalid input at '{path}': {error.message}"

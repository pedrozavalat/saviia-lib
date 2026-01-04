from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError
from saviialib.general_types.error_types.api.saviia_api_error_types import ValidationError

class JsonschemaClient:
    def __init__(self, schema):
        self.validator = Draft7Validator(schema)

    def validate(self, data):
        if not self.validator.is_valid(data):
            errors = list(self.validator.iter_errors(data))
            formatted_errors = {
                "code": " ".join(e.validator for e in errors),
                "message": " ".join(str(list(e.instance.keys())) for e in errors),
                "details": " ".join(e.message for e in errors),
            }
            raise ValidationError(formatted_errors) # type: ignore
        return True

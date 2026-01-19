# Internal modules
from saviialib.libs.schema_validator_client.schema_validator_contract import (
    SchemaValidatorContract,
)
from saviialib.libs.schema_validator_client.clients.jsonschema.jsonschema_client import (
    JsonschemaClient,
)


class SchemaValidatorClient(SchemaValidatorContract):
    def __init__(self, schema, client_name: str = "jsonschema"):
        """
        Initialize a SchemaValidatorClient instance.
        :param client_name: The name of the calendar client to use. If not
        provided, 'jsonschema' is used as the default client.
        """
        if client_name == "jsonschema":
            self.client_name = client_name
            self.client_obj = JsonschemaClient(schema)

    def validate(self, data):
        return self.client_obj.validate(data)

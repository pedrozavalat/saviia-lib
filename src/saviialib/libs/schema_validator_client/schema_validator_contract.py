from abc import ABC, abstractmethod

class SchemaValidatorContract(ABC):
    @abstractmethod
    def validate(self, data):
        pass
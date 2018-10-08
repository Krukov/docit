
from abc import ABCMeta, abstractmethod


class SchemaAdapter(metaclass=ABCMeta):

    def __init__(self, schema):
        self.schema = schema

    def get_data(self):
        data = {name: self.get_field_data(name) for name in self.get_fields()}
        if self.many:
            return [data]
        return data

    def get_field_data(self, field_name: str) -> dict:
        return {
            'description': self.get_field_description(field_name),
            'type': self.get_field_type(field_name),
            'required': self.get_field_required(field_name),
            'nullable': self.get_field_nullable(field_name),
        }

    @property
    @abstractmethod
    def many(self):
        pass

    @abstractmethod
    def get_fields(self) -> list:
        """Return list of schema fields name"""
        pass

    @abstractmethod
    def get_field_description(self, field_name: str) -> str:
        """Return description for given field name"""
        pass

    @abstractmethod
    def get_field_type(self, field_name: str) -> type:
        """Return field type for given field name"""
        pass

    @abstractmethod
    def get_field_required(self, field_name: str) -> bool:
        """Return 'required' requirements for given field name"""
        pass

    @abstractmethod
    def get_field_nullable(self, field_name: str) -> bool:
        """Return 'nullable' requirements for given field name"""
        pass


class SchemaLink:

    def __init__(self, link, data, max_count=3):
        self._link = link
        self._data = data
        self.__max_count = max_count
        self.counter = 1

    def get(self, condition=True):
        if condition and self.counter > self.__max_count:
            if isinstance(self._data, list):
                return [self._link]
            return self._link
        return self._data

    def __hash__(self):
        return hash(str(self._data))

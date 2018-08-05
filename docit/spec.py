
from collections import OrderedDict, defaultdict


class Schema:
    pass


class Request:
    PATH, QUERY, HEADER = 'PATH', 'QUERY', 'HEADER'


class Application:

    @staticmethod
    def get_handler_name(handler):
        return handler.__module__ + '.' + handler.__name__

    @staticmethod
    def get_schema_name(schema):
        return schema.__module__ + '.' + schema.__name__

    def __init__(self, name, version, schema=Schema, **extra):
        self._extra = extra
        self.name = name
        self.version = version
        self._handlers = defaultdict(dict)
        self._paths = OrderedDict()
        self._schema_type = schema
        self._schemas = {}

    def register_schema(self, schema):
        name = self.get_schema_name(schema)
        self._schemas[name] = self._schema_type(schema)
        return name

    def request(self, schema, in_=Request.PATH):
        def _(func):
            _schema = self.register_schema(schema)
            self._handlers[self.get_handler_name(func)]['request'] = {'in': in_, 'schema': _schema}
            return func
        return _

    def response(self, status_or_response, schema=None):
        def _(func):
            func_name = self.get_handler_name(func)
            if 'responses' not in self._handlers[func_name]:
                self._handlers[func_name]['responses'] = []
            if isinstance(status_or_response, int):
                status = status_or_response
                _schema = schema
            else:
                _schema = status_or_response.schema
                status = status_or_response.status
            _schema = self.register_schema(_schema)
            self._handlers[func_name]['responses'].append({'schema': _schema, 'status': status})
            return func

        return _

    def add_path(self, path, handler, method='GET'):
        self._paths[self.get_handler_name(handler)] = (path, method)


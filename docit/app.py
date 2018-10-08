import json
from collections import OrderedDict, defaultdict

from .mapping import SwaggerMapping
from .schema import SchemaLink, SchemaAdapter


class Request:
    PATH, QUERY, HEADER = 'PATH', 'QUERY', 'HEADER'


class Application:

    REQUEST = Request

    @staticmethod
    def get_handler_name(handler):
        return handler.__module__ + '.' + handler.__name__

    @staticmethod
    def get_schema_name(schema):
        if isinstance(schema, dict):
            return hash(json.dumps(schema))
        if not isinstance(schema, type):
            schema = schema.__class__
        # return '{}{}'.format(''.join(map(str.capitalize, schema.__module__.split('.'))), schema.__name__)
        return schema.__name__

    def __init__(self, name, version, link_max_count=3, **extra):
        self.extra = extra
        self.project_name = name
        self.version = version
        self.license = {
            "name": "Apache 2.0",
            "url": "http://www.apache.org/licenses/LICENSE-2.0.html"
        }
        self._handlers = defaultdict(dict)
        self.paths = OrderedDict()
        self._schemas = {}
        self._schema_types = {}
        self._link_max_count = link_max_count

    def register_schema_adapter(self, base_class, schema_adapter):
        assert issubclass(schema_adapter, SchemaAdapter)
        self._schema_types[base_class] = schema_adapter

    def get_schema_data(self, schema):
        if schema is None:
            return
        for base_class, schema_facade in self._schema_types.items():
            if (isinstance(schema, type) and issubclass(schema, base_class)) or isinstance(schema, base_class):
                return schema_facade(schema).get_data()

    def register_schema(self, schema, force_link=False):
        if not schema:
            return
        name = self.get_schema_name(schema)
        data = self.get_schema_data(schema)

        schema_link = SchemaLink(
            name, data,
            max_count=0 if force_link else self._link_max_count
        )
        if hash(schema_link) not in self._schemas:
            self._schemas[hash(schema_link)] = schema_link
        else:
            self._schemas[hash(schema_link)].counter += 1

        return self._schemas[hash(schema_link)]

    def request(self, schemas):
        def _(func):
            parameters = []
            for _in, schema in schemas.items():
                _schema = self.register_schema(schema)
                parameters.append({'in': _in, 'schema': _schema})
            self._handlers[self.get_handler_name(func)]['request'] = parameters
            return func

        return _

    def response(self, status_or_response, schema=None, force_link=False, **kwargs):
        def _(func):
            handler_name = self.get_handler_name(func)
            if 'responses' not in self._handlers[handler_name]:
                self._handlers[handler_name]['responses'] = []
            if isinstance(status_or_response, int):
                status = status_or_response
                _schema = schema
            else:
                _schema = status_or_response.schema
                status = status_or_response.status
            _schema = self.register_schema(_schema, force_link=force_link)
            data = dict(kwargs)
            data.update({'schema': _schema, 'status': status})
            self._handlers[handler_name]['responses'].append(data)
            return func

        return _

    def add_path(self, path, handler, method='GET', content_type='application/json', description=''):
        handler_name = self.get_handler_name(handler)
        handler_meta = self._handlers[handler_name]
        self.paths[handler_name] = {
            'path': path,
            'method': method,
            'content_type': content_type,
            'description': description,
        }
        self.paths[handler_name].update(handler_meta)

    def get_swagger(self):
        return SwaggerMapping.transform(self)



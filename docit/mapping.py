from copy import deepcopy
from collections import OrderedDict

from reformer import Reformer, Field, MethodField


def _to_swagger(value):
    return SwaggerMapping.from_python(value)


class SwaggerMethodMapper(Reformer):
    description = Field()
    produces = Field('self').as_([Field('content_type')])
    responses = Field().iter({
        Field('status', to=str): {
            'description': Field('description', required=False),
            'schema': Field('schema', required=False).get().call(_to_swagger),
        }
    })
    parameters = MethodField()

    def get_parameters(self, obj):
        request = obj['request']
        params = []
        for request in request:
            schema = request['schema'].get()
            if isinstance(schema, dict):
                for name, data in schema.items():
                    params.append({
                        'name': name,
                        'in': request['in'].lower(),
                        'description': data['description'],
                        'required': data['required'],
                        'schema': SwaggerMapping.from_python(data['type'])
                    })
        return params


class SwaggerMapping(Reformer):
    info = Field('self', schema={
        'title': Field('project_name'),
        'description': Field('extra.description'),
        'version': Field('version'),
        'license': Field('license'),
    })
    paths = Field('paths').iter({
        Field('value.path'): {
            Field('value.method').lower(): Field('value', schema=SwaggerMethodMapper())
        },
    })

    TYPE_MAPPING = OrderedDict((
        (int, {'type': 'integer'}),
        (float, {'type': 'number', 'format': 'float'}),
        (str, {'type': 'string'}),
        (bool, {'type': 'boolean'}),
    ))

    CONTAINER_MAPPING = OrderedDict((
        (dict, {'type': 'object', 'properties': {}}),
    ))

    @classmethod
    def add_type(cls, type, handler, container=False):
        storage = cls.TYPE_MAPPING
        if container:
            storage = cls.CONTAINER_MAPPING
        storage[type] = handler

    @classmethod
    def from_python(cls, value):
        for _type, meta in cls.CONTAINER_MAPPING.items():
            if isinstance(value, _type):
                if callable(meta):
                    return meta(value)
                return meta
        for _type, meta in cls.TYPE_MAPPING.items():
            if value is _type or value == _type:
                if callable(meta):
                    return meta(value)
                return deepcopy(meta)

    @classmethod
    def _container_handler(cls, value):
        meta = {'type': 'array'}
        if isinstance(value, tuple):
            meta['items'] = cls.from_python(type(value[0]))
            meta['items']['enum'] = list(value)
            return meta
        if len(value) > 0:
            meta.update(cls.from_python(value[0]))
        return meta


SwaggerMapping.add_type(str, lambda v: {'items': {'$ref': '#/definitions/' + v}}, container=True)
SwaggerMapping.add_type((list, set, tuple), SwaggerMapping._container_handler, container=True)

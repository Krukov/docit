
import collections


class _Attr:

    def __init__(self, name, getter=dict.get):
        self._getter = lambda obj: getter(obj, name)

    @staticmethod
    def schema_getter(schema, obj, item=None):
        if isinstance(schema, dict):
            new = {}
            for key, value in schema.items():
                if isinstance(key, _Attr):
                    key = key._get(obj)
                elif key == Ellipsis and item:
                    key = item
                elif callable(key):
                    key = key(obj)

                if isinstance(value, _Attr):
                    value = value._get(obj)
                elif value == Ellipsis and item:
                    value = item
                elif callable(value):
                    value = value(obj)
                new[key] = value
        else:
            new = []
            for value in schema:
                if isinstance(value, _Attr):
                    value = value._get(obj)
                elif value == Ellipsis and item:
                    value = item
                elif callable(value):
                    value = value(obj)
                new.append(value)
        return new

    @classmethod
    def as_(cls, schema):
        return cls('', getter=lambda obj, name: cls.schema_getter(schema, obj))

    def iter_(self, schema):
        getter = self._getter

        def _getter(obj):
            result = []
            for item in getter(obj):
                result.append(self.schema_getter(schema, obj, item))
            return result
        self._getter = _getter
        return self

    @property
    def item_(self):
        return ...

    def __getattr__(self, item):
        getter = self._getter

        def _getter(obj):
            value = getter(obj)
            if isinstance(value, dict):
                return value[item]
            return getattr(value, item)
        self._getter = _getter
        return self

    def __call__(self, *args, **kwargs):
        getter = self._getter

        def _getter(obj):
            return getter(obj)(*args, **kwargs)
        self._getter = _getter
        return self

    def __getitem__(self, item):
        getter = self._getter

        def _getter(obj):
            return getter(obj)[item]

        self._getter = _getter
        return self

    def __add__(self, other):
        getter = self._getter
        if isinstance(other, _Attr):
            self._getter = lambda obj: (getter(obj) + other._getter(obj))
        else:
            self._getter = lambda obj: (getter(obj) + other)
        return self

    def __radd__(self, other):
        getter = self._getter
        if isinstance(other, _Attr):
            self._getter = lambda obj: (other._getter(obj) + getter(obj))
        else:
            self._getter = lambda obj: (other + getter(obj))
        return self

    def _get(self, obj):
        return self._getter(obj)


class AttrMeta(type):
    @classmethod
    def __prepare__(cls, name, bases):
        return collections.OrderedDict()

    def __new__(mcs, name, bases, attrs):
        attrs.setdefault('__attr__', [])
        for base in bases:
            for _name in getattr(base, '__attr__', []):
                if _name not in attrs:
                    attrs.append(_name)

        attrs['__attr__'] = [key for key, value in attrs.items() if isinstance(value, _Attr)]
        return type.__new__(mcs, name, bases, attrs)


class Map(metaclass=AttrMeta):

    def serialize(self, obj):
        result = {}
        for attr in self.__attr__:
            result[attr] = getattr(self, attr)._get(obj)
        return result


class Key:
    def __getattr__(self, item):
        return _Attr(item)

    def as_(self, obj):
        return _Attr.as_(obj)


key = Key()


# class Swagger(Map):
#     name = key.name
#     paths = key.paths.iter(
#         name=key.name + key.method,
#         responces=key.responces.iter(**{
#             'in_' + key.in_.lower: key.schema
#         }),
#     )
#
#     def get_link(self, link):
#         return '//rel..'
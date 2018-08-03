
from collections import OrderedDict, defaultdict


def get_function_name(func):
    return func.__module__ + '.' + func.__name__


class Schema:
    pass


class Request:
    in_path = Schema
    in_query = Schema
    in_header = Schema


class Responce:
    schema = Schema
    status = 200


class Link:
    target = (Schema, Responce, Request)


class Method:
    requests = [Request]
    responces = [Responce]


class Path:
    methods = [Method]


class Document:
    paths = [Path]
    links = [Link]

    def __init__(self, name):
        self.name = name


class Application:

    def __init__(self, name, version, **extra):
        self._extra = extra
        self.name = name
        self.version = version
        self._handlers = defaultdict(dict)
        self._paths = OrderedDict()

    def request(self, in_path=None, in_query=None, in_header=None):
        def _(func):
            self._handlers[get_function_name(func)]['request'] = Request()
            return func
        return _

    def response(self, status_or_response, schema=None):
        def _(func):
            func_name = get_function_name(func)
            if 'response' not in self._handlers[func_name]:
                self._handlers[func_name]['response'] = []
            self._handlers[func_name]['response'].append(Responce)
            return func

        return _

    def add_path(self, path, handler):
        self._paths[get_function_name(handler)] = path


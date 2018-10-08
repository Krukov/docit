from collections import OrderedDict
from docit.app import Application
from marshmallow import Schema, fields, validate

from docit.schema import SchemaAdapter


expect = {
    "swagger": "3.0",
    "info": {
        "description": "Des",
        "version": "0.1.0",
        "title": "Project",
        "license": {
            "name": "Apache 2.0",
            "url": "http://www.apache.org/licenses/LICENSE-2.0.html"
        }
    },
    # "basePath": "/v2",
    "paths": {
        "/v2/user/{username}": {
            "get": {
                "description": "get user info",
                "produces": [
                    "application/json"
                ],
                "parameters": [
                    {
                        "name": "status",
                        "in": "query",
                        "description": "Status",
                        "required": True,
                        "schema":  {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "available",
                                    "pending",
                                    "sold"
                                ],
                                # "default": "available"
                            },
                        },
                    },
                    {
                        "name": "username",
                        "in": "path",
                        "description": "User",
                        "required": True,
                        "schema": {
                            "type": "string",
                        },
                    }
                ],
                "responses": {
                    "200": {
                        "description": "successful operation",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/User"
                            }
                        }
                    },
                    "404": {
                        "description": "not found",
                        "schema": None,
                    }
                },
            }
        },
    },
}
definitions = {
    "User": {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "format": "int64"
            },
            "username": {
                "type": "string"
            },
            "userStatus": {
                "type": "integer",
                "format": "int32",
                "description": "User Status"
            }
        },
    },
}


def test_app_swagger():
    api = Application(version='0.1.0', name='Project', description='Des')

    class RequestSchema(Schema):
        status = fields.List(
            fields.String(
                validate=validate.OneOf([
                    "available",
                    "pending",
                    "sold",
                ])
            ),
            required=True,
            description='Status',
        )

    class RequestSchema2(Schema):
        username = fields.String(
            required=True,
            description='User',
        )

    class User(Schema):
        id = fields.Integer()
        username = fields.String()
        userStatus = fields.Integer(description="User Status")

    class MyShemaAdapter(SchemaAdapter):
        @property
        def many(self):
            return self.schema.many

        def get_fields(self) -> list:
            return list(self.schema._declared_fields.keys())

        def get_field_description(self, field_name: str) -> str:
            return self.schema._declared_fields[field_name].metadata.get('description')

        def _get_field_type(self, field):
            if isinstance(field, fields.List):
                return [self._get_field_type(field.container), ]
            if isinstance(field.validate, validate.OneOf):
                return tuple(field.validate.choices)
            if isinstance(field, fields.String):
                return str
            return field

        def get_field_type(self, field_name: str):
            field = self.schema._declared_fields[field_name]
            return self._get_field_type(field)

        def get_field_required(self, field_name: str) -> bool:
            return self.schema._declared_fields[field_name].required

        def get_field_nullable(self, field_name: str) -> bool:
            return self.schema._declared_fields[field_name].allow_none

    api.register_schema_adapter(Schema, MyShemaAdapter)

    @api.request(OrderedDict((
            (api.REQUEST.QUERY, RequestSchema()),
            (api.REQUEST.PATH, RequestSchema2()),
    )))
    @api.response(200, User(many=True), description='successful operation', force_link=True)
    @api.response(404, description='not found')
    def handler():
        return {'data': 100}

    api.add_path('/v2/user/{username}', handler, description='get user info')

    result = api.get_swagger()
    assert 'info' in result
    assert 'paths' in result
    assert expect['info'] == result['info']
    assert '/v2/user/{username}' in result['paths']
    assert 'get' in result['paths']['/v2/user/{username}']
    get = result['paths']['/v2/user/{username}']['get']
    expect_get = expect['paths']['/v2/user/{username}']['get']

    assert 'description' in get
    assert 'produces' in get
    assert 'responses' in get
    assert 'parameters' in get

    assert get['description'] == expect_get['description']
    assert get['produces'] == expect_get['produces']
    assert len(get['parameters']) == len(expect_get['parameters'])
    assert get['parameters'][1] == expect_get['parameters'][1]
    assert get['parameters'][0] == expect_get['parameters'][0]
    assert '200' in get['responses']
    assert '404' in get['responses']

    assert dict(get['responses']['404']) == expect_get['responses']['404']
    assert dict(get['responses']['200']) == expect_get['responses']['200']


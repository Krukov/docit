from docit.spec import Application


def test_app_swagger():
    api = Application(version='0.1', name='test')

    class RequestSchema:
        pass

    class RespSchema:
        pass

    class NotFoudndResp:
        status = 404
        schema = {}


    @api.request(RequestSchema)
    @api.response(200, RespSchema)
    @api.response(NotFoudndResp)
    def handler():
        return

    api.add_path('/path', handler)

    assert '/path' in api._paths.values()
    assert 'tests.test.handler' in api._paths.keys()
    assert 'tests.test.handler' in api._handlers

    # assert hash(RequestSchema) in data['schemas']
    # assert hash(RespSchema) in data['schemas']
    # assert hash(NotFoudndResp) in data['schemas']


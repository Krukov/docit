from docit.spec import Application


# def test_app_swagger():
#     api = Application(version='0.1', name='test')
#
#     class RequestSchema:
#         pass
#
#     class RespSchema:
#         pass
#
#     class NotFoudndResp:
#         status = 404
#         schema = {}
#
#
#     @api.request(RequestSchema)
#     @api.response(200, RespSchema)
#     @api.response(NotFoudndResp)
#     def handler():
#         return
#
#     api.add_path('/path', handler)
#
#     assert '/path' in api._paths.values()
#     assert 'tests.test.handler' in api._paths.keys()
#     assert 'tests.test.handler' in api._handlers

    # assert hash(RequestSchema) in data['schemas']
    # assert hash(RespSchema) in data['schemas']
    # assert hash(NotFoudndResp) in data['schemas']


from docit.export import Map, key


def test_key():
    target = {
        'title': 'test',
        'suname': 'sutest',
        'set': True,
        'value': 1,
        'dict': {
            'test1': 'test_1',
        },
        'array': ['hello', 'my', 'name']
    }

    class Test(Map):
        name = key.title
        value = key.value
        set = key.set
        array = key.array[1]
        dict_1 = key.dict.test1
        dict_full = key.dict

        name_func = key.title.replace('test', 'new')
        set_num = key.set.numerator
        full_name = key.title + ' ' + key.suname

        dict_as = key.as_({
            'key': key.value,
            key.set: 't',
            key.title: key.suname,
        })
        list_as = key.as_([
            key.title, 'weee'
        ])
        iter = key.array.iter_({
            key.array.item_: key.value
        })
        iter2 = key.array.iter_(key.array.item_ + )

    expect = {
        'name': 'test',
        'value': 1,
        'name_func': 'new',
        'full_name': 'test sutest',
        'set': True,
        'set_num': 1,
        'array': 'my',
        'dict_1': 'test_1',
        'dict_full': {
            'test1': 'test_1',
        },

        'dict_as': {'key': 1, True: 't', 'test': 'sutest'},
        'list_as': ['test', 'weee'],
        'iter': [{'hello': 1}, {'my': 1}, {'name': 1}],
        'iter2': ['hello1', 'my2', 'name3'] ,
    }
    assert Test().serialize(target) == expect

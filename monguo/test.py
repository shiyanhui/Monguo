# -*- coding: utf-8 -*-

import motor
import sys

from tornado import gen
from tornado.ioloop import IOLoop

from document import Document
from connection import Connection
from field import *

class UserDocument(Document):
    name = StringField()
    sex = StringField()

    meta = {
        'collection': 'test'
    }

    @staticmethod
    @gen.coroutine
    def get_user():
        user = {
            'name': 'shiyanhui',
            'sex': 'male'
        }
        raise gen.Return(user)

    def test_method():
        user = {
            'name': 'shiyanhui',
            'sex': 'male'
        }
        user2 = {
            'name': 'lime'
        }
        result = yield UserDocument.insert(user)
        raise gen.Return(result)


a = '33'
@gen.coroutine
def test():
    print a
    Connection.connect('test')
    yield UserDocument.remove()
    yield UserDocument.test_method()
    result = yield UserDocument.find_one()
    raise gen.Return(result)

class Test(object):
    hello = '2'
    def __init__(self, value):
        self.value = value

    def __call__(self):        
        return self.value

    name = StringField()
    sex = StringField()

    @gen.coroutine
    def test(self):
        Connection.connect('test')
        yield UserDocument.remove()
        yield UserDocument.test_method()
        result = yield UserDocument.find_one()
        print result

if __name__ == '__main__':
    value = IOLoop.current().run_sync(Test(3).test)
    # for name, attr in Test.__dict__.items():
    #     if isinstance(attr, Field):
    #         attr.validate()


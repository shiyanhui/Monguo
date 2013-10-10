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

@gen.coroutine
def test():
    Connection.connect('test')
    yield UserDocument.remove()
    yield UserDocument.test_method()
    result = yield UserDocument.find_one()
    print result

class Test(object):
    def __init__(self, value):
        self.value = value

    def __call__(self):        
        return self.value

    name = StringField()
    sex = StringField()



if __name__ == '__main__':
    IOLoop.current().run_sync(test)
    # for name, attr in Test.__dict__.items():
    #     if isinstance(attr, Field):
    #         attr.validate()


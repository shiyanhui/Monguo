# -*- coding: utf-8 -*-

import motor
import sys

from tornado import gen
from tornado.concurrent import Future, TracebackFuture
from tornado.ioloop import IOLoop, TimeoutError

from document import Document
from connection import Connection
from field import *
from manipulator import MonguoSONManipulator
from pymongo.son_manipulator import SONManipulator

class UserDocument(Document):
    name = StringField(required=True)
    sex = StringField(required=True, default='male', 
                          unique=False, candidate=['male', 'female'])

    meta = {
        'collection': 'test'
    }

    def insert_user():
        user = {
            'name': 'shiyanhui',
            'sex': 'male'
        }
        result = yield UserDocument.insert(user)
        raise gen.Return(result)

@gen.coroutine
def test():
    Connection.connect('test')
    yield UserDocument.remove()
    yield UserDocument.insert({'name': 'lime'})
    result = yield UserDocument.find_one()
    print result
    result 
    result['sex'] = 'female'
    yield UserDocument.save(result)
    result = yield UserDocument.find_one()
    raise gen.Return(result)

if __name__ == '__main__':
    print IOLoop.instance().run_sync(test)

   
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

    @classmethod
    @gen.coroutine
    def get_user(cls):
        user = {
            'name': 'shiyanhui',
            'sex': 'male'
        }
        raise gen.Return(user)

@gen.coroutine
def test():
    Connection.connect('test')
    count = yield UserDocument.get_user()
    print count

IOLoop.current().run_sync(test)
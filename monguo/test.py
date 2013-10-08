# -*- coding: utf-8 -*-

from tornado import gen
from monguo.document import Document

class UserDocument(Document):
    name = StringField()
    sex = StringField()

    meta = {
        'collection': 'hello'
    }

    @classmethod
    @gen.coroutine
    def get_user(cls):
        user = {
            'name': 'shiyanhui',
            'sex': 'male'
        }
        raise gen.Return(user)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: lime
# @Date:   2014-03-26 14:00:01
# @Last Modified by:   lime
# @Last Modified time: 2014-03-26 14:37:29

from datetime import datetime
from bson.objectid import ObjectId
from bson.dbref import DBRef
from tornado import gen
from tornado.ioloop import IOLoop

from monguo.document import Document, EmbeddedDocument
from monguo.connection import Connection
from monguo.field import *


class UserDocument(Document):
    name  = StringField(required=True, unique=True, max_length=20)
    email = EmailField(required=True)
    age   = IntegerField()
    sex   = StringField(required=True, default='male', 
                                       candidate=['male', 'female'])

    meta = {
        'collection': 'user'
    }

    @gen.coroutine
    def get_user_list_1():
        result = yield UserDocument.to_list(UserDocument.find())
        raise gen.Return(result)


    @staticmethod
    @gen.coroutine
    def get_user_list_2():
        result = yield UserDocument.to_list(UserDocument.find())
        raise gen.Return(result)


    @classmethod
    @gen.coroutine
    def get_user_list_3(cls):
        result = yield UserDocument.to_list(UserDocument.find())
        raise gen.Return(result)


    def get_user_list_4():
        result = [item for item in UserDocument.get_collection(True).find()]
        return result

    @staticmethod
    def get_user_list_5():
        result = [item for item in UserDocument.get_collection(True).find()]
        return result

    @classmethod
    def get_user_list_6(cls):
        result = [item for item in UserDocument.get_collection(True).find()]
        return result


class CommentDocument(EmbeddedDocument):
    commentor = ReferenceField(UserDocument, required=True)
    contents  = StringField(required=True, max_length=200)


class PostDocument(Document):
    author       = ReferenceField(UserDocument, required=True)
    publish_time = DateTimeField(required=True)
    title        = StringField(required=True, max_length=100)
    contents     = StringField(max_length=5000)
    comments     = ListField(EmbeddedDocumentField(CommentDocument))

    meta = {
        'collection': 'post'
    }

@gen.coroutine
def test():
    Connection.connect('test')

    yield UserDocument.remove()
    
    bob_id = yield UserDocument.insert({
        'name': 'Bob',
        'email': 'bob@gmail.com',
        'age': 19
    })

    alice_id = yield UserDocument.insert({
        'name': 'Alice',
        'email': 'alice@gmail.com',
        'sex': 'female',
        'age': 18
    })

    post_id = yield PostDocument.insert({
        'author': DBRef(UserDocument.meta['collection'], bob_id),
        'publish_time': datetime.now(),
        'title': 'title',
    })

    comment = {
        'commentor': DBRef(UserDocument.meta['collection'], alice_id),
        'contents': 'I am comments.'
    }

    yield PostDocument.update({'_id': post_id}, 
                              {'$push': {'comments': comment}})

    user = yield UserDocument.find_one({'name': 'Bob'})
    posts = yield PostDocument.find().to_list(5)
    user_list = yield UserDocument.get_user_list_1()
    print user_list
    user_list = yield UserDocument.get_user_list_2()
    print user_list
    user_list = yield UserDocument.get_user_list_3()
    print user_list
    user_list = UserDocument.get_user_list_4()
    print user_list
    user_list = UserDocument.get_user_list_5()
    print user_list
    user_list = UserDocument.get_user_list_6()
    print user_list

if __name__ == '__main__':
    IOLoop.instance().run_sync(test)

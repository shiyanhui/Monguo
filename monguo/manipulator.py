# -*- coding: utf-8 -*-

from tornado import gen
from tornado.concurrent import Future, TracebackFuture
from tornado.ioloop import IOLoop

from field import Field
from error import *
from pymongo.son_manipulator import SONManipulator

__all__ = ['MonguoSONManipulator']

class MonguoSONManipulator(SONManipulator):
    def __init__(self, document_cls, method_name, son=None):
        self.document_cls = document_cls
        self.method_name  = method_name
        self.son          = son

    def insert(self):
        _son       = {}
        field_list = []

        for name, attr in self.document_cls.__dict__.items():
            if isinstance(attr, Field):
                field_list.append(name)

                if (attr.required and not self.son.has_key(name) 
                                            and attr.default is None):
                    raise RequiredError(field=name)

                value = None
                if (attr.required and not self.son.has_key(name) 
                                        and attr.default is not None):
                    value = attr.default
                elif self.son.has_key(name):
                    value = self.son[name]

                if value is not None:
                    if attr.unique:
                        count = collection.find({name: value}).count()
                        if count:
                            raise UniqueError(field=name)

                    if attr.candidate:
                        if value not in attr.candidate:
                            raise CandidateError(field=name)
                    attr.validate(value)
                    _son[name] = value

        for name, attr in self.son.items():
            if name not in field_list:
                raise UndefinedFieldError(field=name)
        return _son

    def save(self):
        if self.son.has_key('_id'):
            _id = self.son['_id']
            del self.son['_id']
            _son = self.insert()
            _son['_id'] = _id
        else:
            _son = self.insert()
        return _son

    def update(self):
        if self.son.has_key('$set'):
            pass
        else:
            _son = self.insert()
        return _son

    def transform_incoming(self, son, collection):
        if self.son is None:
            self.son = son
        try:
            self.son = getattr(self, self.method_name)()
        except AttributeError, e:
            pass

        return self.son

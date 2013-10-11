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

    @gen.coroutine
    def is_unique(self):
        raise gen.Return(True)

    def transform_incoming(self, son, collection):
        if self.son is None:
            self.son = son

        self._collection = collection

        if self.method_name == 'insert':
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
                            self._condition= {name: value}
                            IOLoop.current().run_sync(self.is_unique)
                        if attr.candidate:
                            if value not in attr.candidate:
                                raise CandidateError(field=name)
                        attr.validate(value)
                        _son[name] = value

            for name, attr in self.son.items():
                if name not in field_list:
                    raise UndefinedFieldError(field=name)

        try:
            self.son = _son
        except Exception, e:
            pass

        return self.son

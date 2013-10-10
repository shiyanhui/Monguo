# -*- coding: utf-8 -*-

from tornado import gen
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
    def check_unique(self):
        result = yield self.collection.find_one(self.condition)
        if result:
            raise UniqueError(file=self._field_name)

    def transform_incoming(self, son, collection):
        if self.son is None:
            self.son = son
        
        self._collection = collection

        _son = {}
        if self.method_name == 'insert':
            for name, attr in self.document_cls.__dict__.items():
                if isinstance(attr, Field):
                    self._field_name = name
                    
                    if attr.required:
                        if not self.son.has_key(name):
                            if attr.default is not None:
                                if attr.unique:
                                    self._condition = {name: attr.default}
                                    IOLoop.current().run_sync(
                                                self.check_unique)
                                if attr.candidate:
                                    if attr.default not in attr.candidate:
                                        raise 
                                _son[name] = attr.default
                            else:
                                raise RequiredError(field=name)
                        else:
                            if attr.unique:
                                self._condition= {name: self.son[name]}
                                IOLoop.current().run_sync(self.check_unique)

                            attr.validate(self.son[name])
                            _son[name] = self.son[name]

                    elif self.son.has_key(name):
                        if attr.unique:
                            self._condition= {name: self.son[name]}
                            IOLoop.current().run_sync(self.check_unique)
                        attr.validate(self.son[name])
                        _son[name] = self.son[name]


        return self.son        

# -*- coding: utf-8 -*-

from field import Field
from error import *
from pymongo.son_manipulator import SONManipulator


__all__ = ['MonguoSONManipulator']

class MonguoSONManipulator(SONManipulator):

    def __init__(self, document_cls, method_name, son=None):
        self.document_cls = document_cls
        self.method_name  = method_name
        self.son          = son

    def transform_incoming(self, son, collection):
        if self.son is None:
            self.son = son

        _son = {}
        if self.method_name == 'insert':
            for name, attr in self.document_cls.__dict__.items():
                if isinstance(attr, Field):
                    if attr.required:
                        if not self.son.has_key(name):
                            if attr.default is not None:
                                # default的值也得检查
                                _son[name] = attr.default
                            else:
                                raise RequiredError(field=name)
                        else:
                            _son[name] = attr.validate(self.son[name])
                    elif self.son.has_key(name):
                        _son[name] = attr.validate(self.son[name])
                        
        return self.son        

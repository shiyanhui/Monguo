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

    def __check_value(self, field, collection, name, value):
        field.validate(value)

        if field.unique:
            count = collection.find({name: value}).count()
            if count:
                raise UniqueError(field=name)

        if field.candidate: 
            if value not in field.candidate:
                raise CandidateError(field=name)

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
                    self.__check_value(attr, collection, name, value)
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
        field_dict = {}
        for name, attr in self.document_cls.__dict__.items():
            if isinstance(attr, Field):
                field_dict[name] = attr

        operators = ['$inc', '$name', '$setOnInsert', '$set', '$unset', '$', 
                    '$addToSet', '$pop', '$pullAll', '$pull', '$pushAll',
                    '$push', '$each', '$slice', '$sort', '$bit', '$isolated']


        contain_operator = False
        for name in self.son:
            if name in operators:
                contain_operator = True
                break

        if not contain_operator:
            self.insert()
        else:
            if self.son.has_key('$rename'):
                for name in self.son['$rename']:
                    raise FieldRenameError(field=name)

            if self.son.has_key('$set'):
                for name, value in self.son['$set'].items():
                    if not field_dict.has_key(name):
                        raise UndefinedFieldError(field=name)

                    self.__check_value(field_dict[name], collection, 
                                                            name, value)

            if self.son.has_key('$unset'):
                for name in self.son['$unset']:
                    if name not in field_dict:
                        raise UndefinedFieldError(field=name)

                    if field_dict[name].required:
                        raise FieldDeleteError(field=name)

        return self.original_son

    def transform_incoming(self, son, collection):
        self.original_son = son

        if self.son is None:
            self.son = son

        try:
            self.son = getattr(self, self.method_name)()
        except AttributeError, e:
            pass

        return self.son

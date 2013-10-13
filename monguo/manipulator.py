# -*- coding: utf-8 -*-

import re

from tornado import gen
from tornado.concurrent import Future, TracebackFuture
from tornado.ioloop import IOLoop

from field import Field
from error import *
from pymongo.son_manipulator import SONManipulator

__all__ = ['MonguoSONManipulator']

class MonguoSONManipulator(SONManipulator):
    def __init__(self, document_cls, method_name, **options):
        self.document_cls = document_cls
        self.method_name  = method_name
        self.options = options

    def __check_value(self, field, name, value):
        field.validate(value)

        if field.unique:
            count = self.collection.find({name: value}).count()
            if count:
                raise UniqueError(field=name)

        if field.candidate: 
            if value not in field.candidate:
                raise CandidateError(field=name)

    @property
    def document_fields(self):
        field_list = {}

        for name, attr in self.document_cls.__dict__.items():
            if isinstance(attr, Field):
                field_list[name] = attr

        return field_list

    @document_fields.setter
    def document_fields(self, value):
        raise AssignmentError(field='document_fields')
    
    def insert(self):
        _son = {}

        for name, attr in self.document_cls.__dict__.items():
            if isinstance(attr, Field):
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
                    self.__check_value(attr, name, value)
                    _son[name] = value

        for name, attr in self.son.items():
            if name not in self.document_fields:
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

        def __check_name_in_set_fields(name):
            regex = re.compile(r'^[_a-zA-Z][.$_a-zA-Z0-9]+[_$a-zA-Z0-9]$')
            if not regex.match(name):
                raise NameError('NameError in $set field %s' % name)
            
            for index, char in enumerate(name):
                if char == '$':
                    if name[index-1] != '.':
                        raise NameError("before '$' should be '.' \
                                                        in field of '$set'!")
                    if index != len(name) - 1 and name[index+1] != '.':
                        raise NameError("after '$' should be '.' \
                                                        in field of '$set'!")

        operators = ['$inc', '$name', '$setOnInsert', '$set', '$unset', '$', 
                    '$addToSet', '$pop', '$pullAll', '$pull', '$pushAll',
                    '$push', '$each', '$slice', '$sort', '$bit', '$isolated']

        try:
            spec = self.options['args'][0]
        except IndexError, e:
            try:
                spec = self.options['kwargs']['spec']
            except KeyError, e:
                raise SyntaxError('lack of spec argument!')

        if not isinstance(spec, dict) and not isinstance(spec, SON):
            raise TypeError('spec argument should be a dict \
                                        type or SON instance.')

        try:
            upsert = self.options['args'][2]
        except IndexError, e:
            upsert = self.options['kwargs'].get('upsert', False)

        if not isinstance(upsert, bool):
            raise TypeError('upsert should be bool type.')

        if not upsert:
            contain_operator = False
            for name in self.son:
                if name in operators:
                    contain_operator = True
                    break

            if not contain_operator:
                _son = self.insert()
                return _son

            if self.son.has_key('$rename'):
                for name in self.son['$rename']:
                    raise FieldRenameError(field=name)

            if self.son.has_key('$unset'):
                for name in self.son['$unset']:
                    if name not in self.document_fields:
                        raise UndefinedFieldError(field=name)

                    if self.document_fields[name].required:
                        raise FieldDeleteError(field=name)
                        
            if self.son.has_key('$set'):
                for name, value in self.son['$set'].items():

                    __check_name_in_set_fields(name)

                    name_list = name.split('.')
                    
                    if not self.document_fields.has_key(name):
                        raise UndefinedFieldError(field=name)

                    self.__check_value(self.document_fields[name], name, value)
        return self.son

    def transform_incoming(self, son, collection):
        self.collection = collection
        self.son = son

        try:
            _son = getattr(self, self.method_name)()
        except AttributeError, e:
            pass

        return _son

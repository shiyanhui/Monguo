# -*- coding: utf-8 -*-

import re

from tornado import gen
from tornado.concurrent import Future, TracebackFuture
from tornado.ioloop import IOLoop

from field import *
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
            if name not in self.document_cls.fields_dict():
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
            '''Check whether the field name in '$set' is validated.'''

            regex = re.compile(r'^[_a-zA-Z][.$_a-zA-Z0-9]+[_$a-zA-Z0-9]$')
            if not regex.match(name):
                raise NameError('NameError in $set field %s' % name)
            
            for index, char in enumerate(name):
                if char == '$':
                    if name[index-1] != '.':
                        raise NameError("before '$' should be '.' \
                                                        in field of '$set'!")
                    if index != len(name) - 1 and name[index + 1] != '.':
                        raise NameError("after '$' should be '.' \
                                                        in field of '$set'!")
            name_list = name.split('.')
            
            pre_name = '$'
            for name in name_list:
                if name == pre_name == '$': 
                    raise NameError('NameError in %s' % name)
                pre_name = name

        def __check_document(document):
            for name, value in document:
                if not isinstance(value, dict):                   
                    pass
                else:
                    __check_document(value)

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
                    if name not in self.document_cls.fields_dict():
                        raise UndefinedFieldError(field=name)

                    if self.document_cls.fields_dict()[name].required:
                        raise FieldDeleteError(field=name)
                        
            if self.son.has_key('$set'):
                for name, value in self.son['$set'].items():

                    # Is the field name in self.son['$set'] is right? 
                    __check_name_in_set_fields(name)

                    current_document_cls = self.document_cls
                    name_list = name.split('.')
                    for index, name in enumerate(name_list):

                        fields_dict = current_document_cls.fields_dict()
                        if name not in fields_dict:
                            raise UndefinedFieldError(field=name)
                        
                        attr = fields_dict[name]

                        if name != '$':
                            if index != len(name_list) - 1:
                                if name_list[index + 1] != '$':
                                    if not isinstance(
                                                attr, EmbeddedDocumentField):
                                        raise TypeError("'%s' should be EmbeddedDocumentField type." % name)
                                    current_document_cls = attr.__class__
                                else:
                                    if not isinstance(attr, ListField):
                                        raise TypeError('%s should be\
                                                ListField type.' % name)
                                    attr.validate(value)

                    if not self.document_cls.fields_dict().has_key(name):
                        raise UndefinedFieldError(field=name)

                    self.__check_value(self.document_cls.fields_dict()[name], 
                                                                   name, value)
        return self.son

    def transform_incoming(self, son, collection):
        self.collection = collection
        self.son = son

        try:
            _son = getattr(self, self.method_name)()
        except AttributeError, e:
            pass

        return _son

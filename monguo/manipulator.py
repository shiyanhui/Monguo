# -*- coding: utf-8 -*-

import re
import util

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

    def check_value(self, field, name, value):
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
                    self.check_value(attr, name, value)
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
        def check_key_in_set_fields(key):
            '''Check whether the field name in '$set' is validated.'''

            name_list = key.split('.')
            name_error = NameError('%s is an illegal key!', key)
            for name in name_list:
                if not (util.legal_variable_name(name) or name.isdigit() or 
                        name == '$'):
                    raise name_error

            if name_list.count('$') > 1:
                raise name_error

            if not util.legal_variable_name(name_list[0]):
                raise name_error

            if (name_list.count('$') == 1 and 
                    name_list[name_list.index('$') - 1].isdigit()):
                raise name_error

            return name_list

        def check_document(document):
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
                    name_list = check_key_in_set_fields(name)
                    name_without_dollar = '.'.join([name for name in name_list if name != '$'])

                    fields_dict = self.document_cls.fields_dict()

                    if name_list[0] not in fields_dict:
                        raise UndefinedFieldError(field=name)
                    
                    current_attr = fields_dict[name_list[0]]
                    for index, name in enumerate(name_list):
                        if name == '$' or name.isdigit():
                            if index != len(name_list) - 1:
                                next_name = name_list[index + 1]

                                if next_name.isdigit():
                                    if isinstance(current_attr.field, ListField):
                                        current_attr = current_attr.field
                                    elif isinstance(current_attr, GenericListField):
                                        break
                                    else:
                                        raise TypeError('item in %s should be GenericListField or ListField type.' % name)
                                else:
                                    if isinstance(current_attr.field, DictField):
                                        current_attr = current_attr.field
                                    elif isinstance(current_attr.field, GenericDictField):
                                        break
                                    else:
                                        raise TypeError('item in %s should be GenericDictField or DictField type.' % name)
                            else:
                                self.check_value(current_attr, name_without_dollar, value)
                        else:
                            if index != len(name_list) - 1:
                                if util.legal_variable_name(name_list[index + 1]):
                                    if isinstance(current_attr, EmbeddedDocumentField):
                                        current_attr = current_attr.document
                                    elif isinstance(current_attr, GenericDictField):
                                        break
                                    else:
                                        raise TypeError("'%s' isn't EmbeddedDocumentField or GenericDictField type." % name)
                                else:
                                    if isinstance(current_attr, ListField):
                                        current_attr = current_attr.field
                                    elif isinstance(current_attr, GenericListField):
                                        break
                                    else:
                                        raise TypeError("%s isn't ListField or GenericListField type." % name)
                            else:
                                self.check_value(current_attr, name_without_dollar, value)

            if self.son.has_key('$inc'):
                for name, value in self.son['$inc'].items():
                    if not util.isnum(value):
                        raise ValueError('value in $inc must be number.')

                    # Is the field name in self.son['$set'] is right? 
                    name_list = check_key_in_set_fields(name)
                    name_without_dollar = '.'.join([name for name in name_list if name != '$'])

                    fields_dict = self.document_cls.fields_dict()

                    if name_list[0] not in fields_dict:
                        raise UndefinedFieldError(field=name)
                    
                    current_attr = fields_dict[name_list[0]]
                    for index, name in enumerate(name_list):
                        if name == '$' or name.isdigit():
                            if index != len(name_list) - 1:
                                next_name = name_list[index + 1]

                                if next_name.isdigit():
                                    if isinstance(current_attr.field, ListField):
                                        current_attr = current_attr.field
                                    elif isinstance(current_attr, GenericListField):
                                        break
                                    else:
                                        raise TypeError('item in %s should be GenericListField or ListField type.' % name)
                                else:
                                    if isinstance(current_attr.field, DictField):
                                        current_attr = current_attr.field
                                    elif isinstance(current_attr.field, GenericDictField):
                                        break
                                    else:
                                        raise TypeError('item in %s should be GenericDictField or DictField type.' % name)
                            else:
                                if not isinstance(current_attr, NumberField):
                                    raise ValueError('The field assigned to is not an instance of NumberField.')
                                    
                                self.check_value(current_attr, name_without_dollar, value)
                        else:
                            if index != len(name_list) - 1:
                                if util.legal_variable_name(name_list[index + 1]):
                                    if isinstance(current_attr, EmbeddedDocumentField):
                                        current_attr = current_attr.document
                                    elif isinstance(current_attr, GenericDictField):
                                        break
                                    else:
                                        raise TypeError("'%s' isn't EmbeddedDocumentField or GenericDictField type." % name)
                                else:
                                    if isinstance(current_attr, ListField):
                                        current_attr = current_attr.field
                                    elif isinstance(current_attr, GenericListField):
                                        break
                                    else:
                                        raise TypeError("%s isn't ListField or GenericListField type." % name)
                            else:
                                if not isinstance(current_attr, NumberField):
                                    raise ValueError('The field assigned to is not an instance of NumberField.')

                                self.check_value(current_attr, name_without_dollar, value)

            if self.son.has_key('$addToSet'):
                pass

            if self.son.has_key('$pop'):
                pass

            if self.son.has_key('$pullAll'):
                pass

            if self.son.has_key('$pull'):
                pass

            if self.son.has_key('$pushAll'):
                pass

            if self.son.has_key('$push'):
                pass

        return self.son

    def transform_incoming(self, son, collection):
        self.collection = collection
        self.son = son

        try:
            _son = getattr(self, self.method_name)()
        except AttributeError, e:
            pass

        return _son

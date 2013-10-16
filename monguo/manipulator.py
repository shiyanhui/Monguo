# -*- coding: utf-8 -*-

import re
import util

from bson.son import SON
from tornado import gen
from tornado.concurrent import Future, TracebackFuture
from tornado.ioloop import IOLoop
from pymongo.son_manipulator import SONManipulator

from field import *
from error import *

__all__ = ['MonguoSONManipulator']


class MonguoSONManipulator(SONManipulator):
    def __init__(self, document_cls, method_name, **options):
        self.document_cls = document_cls
        self.method_name  = method_name
        self.options = options

    def __check_value(self, field, name, value):
        value = field.validate(value)
        if (field.unique and not field.in_list 
                         and util.legal_variable_name(name)):
            count = self.collection.find({name: value}).count()
            if count:
                raise UniqueError(field=name)

        return value

    def insert(self):
        from document import BaseDocument
        son = BaseDocument.validate_document(self.document_cls, self.son)

        for name, attr in self.document_cls.fields_dict().items():
            if attr.unique and not attr.in_list:
                count = self.collection.find({name: son[name]}).count()
                if count:
                    raise UniqueError(field=name)
        return son

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
        def check_key_in_operator_fields(key):
            '''Check whether the field name in '$set' is validated.'''

            name_list = key.split('.')
            name_error = NameError("%s is an illegal key!", key)
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

        def pre_deal(operator, value):
            if operator == '$set': 
                value = [value]

            elif operator == '$addToSet':
                if isinstance(value, dict) and '$each' in value:
                    if len(value.items()) > 1:
                        raise SyntaxError("There cant't be other keys except "
                                          "'$each'.")

                    value = value['$each']
                    if not isinstance(value, (list, tuple)):
                        raise TypeError("Value of '$each' should be list or "
                                        "tuple type.")
                else:
                    value = [value]

            elif operator == '$inc':
                if not util.isnum(value):
                    raise ValueError("Value in '$inc' must be number.")
                value = [value]

            elif operator == '$pushAll':
                if not isinstance(value, (list, tuple)):
                    raise TypeError("Value in '$pushAll' should be list or "
                                    "tuple.")
            elif operator == '$push':
                if isinstance(value, dict) and '$each' in value:
                    if len(value.items()) > 1:
                        raise SyntaxError("There cant't be other keys except "
                                          "'$each'.")

                    value = value['$each']
                    if not isinstance(value, (list, tuple)):
                        raise TypeError("Value of '$each' should be list or "
                                        "tuple type.")
                else:
                    value = [value]

            elif operator == '$bit':
                if not isinstance(value, dict):
                    raise TypeError("The field value of '$bit' shoud be dict "
                                    "type.")

                if len(value.items()) != 1:
                    raise ValueError("Can't have other key except 'and' and "
                                     "'or' in '$bit'")

                key = value.keys()[0]
                if key != 'and' and key != 'or':
                    raise ValueError("Key in '$bit' should be 'and' or 'or'.")

                if not isinstance(value[key], (int, long)):
                    raise TypeError("Value in '$bit' should be int or long "
                                    "type.")

                value = [value[key]]
            return value

        def post_deal(operator, attr, name, value):
            if operator == '$addToSet':
                if not isinstance(attr, (ListField, GenericListField)):
                    raise TypeError("The field added to is not an instance of "
                                    "ListField or GenericListField.")

            elif operator == '$inc':
                if not isinstance(attr, (IntegerField, FloatField)):
                    raise TypeError("The field assigned to is not an instance "
                                    "of IntegerField or FloatField.")

            elif operator == '$pushAll':
                if not isinstance(attr, (ListField, GenericListField)):
                    raise TypeError("The field added to is not an instance of "
                                    "ListField or GenericListField.")

            elif operator == '$push':
                if not isinstance(attr, (ListField, GenericListField)):
                    raise TypeError("The field added to is not an instance of "
                                    " ListField or GenericListField.")

            elif operator == '$bit':
                if not isinstance(attr, IntegerField):
                    raise TypeError("The field bitwith to is not an instance "
                                    "of IntegerField.")

            elif operator == '$unset':
                if not isinstance(attr, (GenericDictField, DictField)):
                    raise TypeError("%s should be in GenericDictField or"
                                    "DictField." % name)

                if isinstance(attr, DictField):
                    fields_dict = attr.document.fields_dict()
                    if name in fields_dict and fields_dict[name].required:
                        raise FieldDeleteError(field=name)

        def deal_with_operator(operator):
            for name, value in self.son[operator].items():
                value = pre_deal(operator, value)

                original_name = name
                # Is the field name in self.son[operator] is right? 
                name_list = check_key_in_operator_fields(name)
                name_without_dollar = '.'.join([name for name in name_list 
                                               if name != '$'])

                fields_dict = self.document_cls.fields_dict()

                if name_list[0] not in fields_dict:
                    raise UndefinedFieldError(field=name_list[0])
                
                current_attr = fields_dict[name_list[0]]
                if operator == '$unset':
                    last_name = name_list.pop()
                    if not name_list:
                        fields_dict = self.document_cls.fields_dict()
                        if name in fields_dict and fields_dict[name].required:
                            raise FieldDeleteError(field=name)

                for index, name in enumerate(name_list):
                    if name == '$' or name.isdigit():
                        if index != len(name_list) - 1:
                            next_name = name_list[index + 1]

                            if next_name.isdigit():
                                if isinstance(current_attr, ListField):
                                    current_attr = current_attr.field
                                elif isinstance(current_attr, 
                                                GenericListField):
                                    break
                                else:
                                    raise TypeError("item in %s should be "
                                                    "GenericListField or "
                                                    "ListField type." %
                                                    name)
                            else:
                                if isinstance(current_attr.field, DictField):
                                    current_attr = current_attr.field
                                elif isinstance(current_attr.field, 
                                                GenericDictField):
                                    break
                                else:
                                    raise TypeError("item in %s should be "
                                                    "GenericDictField or "
                                                    "DictField type." % name)
                        else:
                            if operator == '$unset':
                                post_deal(operator, current_attr, last_name,
                                          value)
                            else:
                                post_deal(operator, current_attr, 
                                          name_without_dollar, value)

                                for item in value:
                                    result = self.__check_value(current_attr,
                                                        name_without_dollar,
                                                        item)
                                    self.son[operator][original_name] = result
                            
                    else:
                        if index != len(name_list) - 1:
                            next_name = name_list[index + 1]

                            if util.legal_variable_name(next_name):
                                if isinstance(current_attr, 
                                              DictField):
                                    current_attr = (current_attr.document.
                                                    fields_dict()[next_name])

                                elif isinstance(current_attr, 
                                                GenericDictField):
                                    break
                                else:
                                    raise TypeError("'%s' isn't DictField or "
                                                    "GenericDictField type." %
                                                    name)
                            else:
                                if isinstance(current_attr, ListField):
                                    current_attr = current_attr.field
                                elif isinstance(current_attr, 
                                                GenericListField):
                                    break
                                else:
                                    raise TypeError("%s isn't ListField or "
                                                    "GenericListField type." %
                                                    name)
                        else:
                            if operator == '$unset':
                                post_deal(operator, current_attr, last_name,
                                          value)
                            else:
                                post_deal(operator, current_attr, 
                                          name_without_dollar, value)

                                for item in value:
                                    result = self.__check_value(current_attr,
                                                        name_without_dollar,
                                                        item)
                                    self.son[operator][original_name] = result

        update_operators = ['$inc', '$name', '$setOnInsert', '$set', '$unset', 
                            '$addToSet', '$pop', '$pullAll', '$pull', '$sort',
                            '$pushAll', '$push', '$each', '$slice', '$bit' ,
                            '$isolated']

        try:
            spec = self.options['args'][0]
        except IndexError, e:
            try:
                spec = self.options['kwargs']['spec']
            except KeyError, e:
                raise SyntaxError("Lack of spec argument.")

        if not isinstance(spec, (dict, SON)):
            raise TypeError("spec argument should be a dict "
                            "type or SON instance.")

        try:
            upsert = self.options['args'][2]
        except IndexError, e:
            upsert = self.options['kwargs'].get('upsert', False)

        if not isinstance(upsert, bool):
            raise TypeError('Upsert should be bool type.')

        if not upsert or self.collection.find_one(spec):
            contain_operator = False
            for name in self.son:
                if name in update_operators:
                    contain_operator = True
                    break

            if not contain_operator:
                _son = self.insert()
                return _son

            if self.son.has_key('$rename'):
                for name in self.son['$rename']:
                    raise NotSupportError(field=name)

            new_operators = ['$set', '$inc', '$addToSet', '$pushAll', '$push', 
                             '$bit', '$unset']

            for operator in new_operators:
                if self.son.has_key(operator):
                    deal_with_operator(operator)
        else:
            if self.son.has_key('$setOnInsert'):
                mongodb_version = (self.collection.database.
                                   command('buildInfo')['version'])
                if mongodb_version < '2.4':
                    raise KeyError("Your Mongdb's version is %s, only version "
                                   "2.4+ support '$setOnInsert'." %
                                   mongodb_version)

                self.son = self.son['$setOnInsert']
                self.son = self.insert()

        return self.son

    def transform_incoming(self, son, collection):
        self.collection = collection
        self.son = son

        try:
            _son = getattr(self, self.method_name)()
        except AttributeError, e:
            pass

        return _son
